"""Visual frame selection: ffmpeg scene-change detection + gap filling.

Why: transcript-keyword selection fails on non-English videos and on long
chart/slide lessons where the speaker never says "look at this". Scene changes
are language-independent — every new slide, drawing step or chart scroll
produces a visual change, which is exactly what a Vision LLM needs to see.
"""

import logging
import re
import subprocess

from pathlib import Path

from . import SmartTimestamp, TranscriptEntry
from .extractor import check_ffmpeg

logger = logging.getLogger(__name__)

# metadata=print emits "...pts_time:X" then, on the next log line, "...lavfi.scene_score=Y"
_SCORE_RE = re.compile(r"pts_time:([0-9.]+)[^\n]*\n[^\n]*?lavfi\.scene_score=([0-9.]+)")

SCENE_THRESHOLD_DEFAULT = 0.03   # low: slide decks change subtly (drawing steps)
SKIP_START_SEC = 6.0             # intros / black opening frames
STABLE_MIN_SEC = 4.0             # a segment must hold this long to count as a "shot"
SCENE_TIMEOUT_SEC = 900


def auto_max_frames(duration_sec: float | None) -> int:
    """Roughly one frame per ~35s of video, clamped to [12, 60].

    35s keeps short on-screen captions in talking-head videos from slipping
    between picks while a 13-min video still fits in 3 storyboard pages.
    """
    if not duration_sec:
        return 30
    return int(max(12, min(60, duration_sec / 35)))


def detect_scene_changes(
    video_path: Path, threshold: float = SCENE_THRESHOLD_DEFAULT,
) -> list[tuple[float, float]]:
    """Return (timestamp_sec, scene_score) pairs where the score exceeds threshold.

    The score (0–1) measures how much the picture changed; a new slide scores far
    higher than a gesture or a colour-cycling lamp, so it is used to rank
    candidates. Analyses a downscaled stream for speed. Returns [] on failure.
    """
    ffmpeg_bin = check_ffmpeg()
    cmd = [
        ffmpeg_bin, "-hide_banner", "-nostats",
        "-i", str(video_path),
        "-an",
        "-vf", f"scale=320:-2,select='gt(scene,{threshold})',metadata=print",
        "-f", "null", "-",
    ]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=SCENE_TIMEOUT_SEC,
        )
    except subprocess.TimeoutExpired:
        logger.warning("Scene detection timed out — falling back to transcript-based selection")
        return []
    scenes = [(float(m.group(1)), float(m.group(2))) for m in _SCORE_RE.finditer(result.stderr)]
    logger.debug(f"Scene detection: {len(scenes)} changes at threshold {threshold}")
    return scenes


def select_visual_timestamps(
    scene_times: list[tuple[float, float]] | list[float],
    keyword_ts: list[SmartTimestamp],
    entries: list[TranscriptEntry],
    duration: float | None,
    max_frames: int,
    min_gap: float | None = None,
    max_gap: float | None = None,
) -> list[SmartTimestamp]:
    """Combine stable visual segments, transcript keyword hits and gap filling.

    1. Scene changes split the video into segments. For every segment that stays
       visually stable for >= STABLE_MIN_SEC, take the frame ~1s *before* it ends:
       that is the segment's final state (slide fully drawn, annotations done).
       Longer-lasting segments get higher priority (a summary slide shown for
       80s matters more than a 5s cutaway).
    2. Candidates closer than min_gap: keep the higher-priority one.
    3. Any stretch longer than max_gap with no pick is filled — preferring a
       keyword hit inside that stretch, otherwise evenly spaced.
    4. If over budget, repeatedly drop the point with the lowest
       (neighbour span × priority), keeping coverage even and important frames.
    """
    if not duration:
        duration = max((e.end_sec for e in entries), default=0.0)
    if duration <= 0:
        return []

    # Gaps scale with video length so short videos still get several frames.
    if min_gap is None:
        min_gap = max(8.0, min(25.0, duration / (max_frames * 1.5)))
    if max_gap is None:
        max_gap = max(min_gap * 2, min(60.0, duration / max(4, max_frames * 0.6)))

    start = min(SKIP_START_SEC, duration * 0.05)
    end = max(start, duration - 1.0)

    change_times = sorted(s[0] if isinstance(s, tuple) else float(s) for s in scene_times)

    # 1. Stable segments → take each one's end state
    cands: list[tuple[float, str, float]] = []   # (time, reason, priority)
    bounds = [0.0] + change_times + [duration]
    for a, b in zip(bounds, bounds[1:]):
        seg = b - a
        if seg < STABLE_MIN_SEC:
            continue
        t = min(b - 1.0, end)
        if t < start:
            continue
        prio = 1.0 + min(seg, 120.0) / 60.0
        cands.append((t, f"segment_end:{seg:.0f}s", prio))

    # 2. Thin: candidates closer than min_gap keep the higher priority
    picks: list[tuple[float, str, float]] = []
    for c in cands:
        if picks and c[0] - picks[-1][0] < min_gap:
            if c[2] > picks[-1][2]:
                picks[-1] = c
        else:
            picks.append(c)

    # 3. Gap filling
    kw_times = sorted((k.time_sec, k.reason) for k in keyword_ts)
    filled: list[tuple[float, str, float]] = []
    prev = start
    for c in picks + [(end, "end", 0.0)]:
        t = c[0]
        while t - prev > max_gap:
            window = [(kt, kr) for kt, kr in kw_times if prev + min_gap <= kt <= min(prev + max_gap, t - min_gap)]
            if window:
                kt, kr = window[0]
                filled.append((kt, kr, 0.6))
                prev = kt
            else:
                prev = prev + max_gap * 0.8
                filled.append((prev, "gap_fill", 0.4))
        if c[1] != "end":
            filled.append(c)
            prev = t
    if not filled:
        filled = [(start, "gap_fill", 0.4)]

    # 4. Trim to budget
    filled.sort()
    while len(filled) > max(2, max_frames):
        best_i, best_val = 1, float("inf")
        for i in range(1, len(filled) - 1):
            val = (filled[i + 1][0] - filled[i - 1][0]) * filled[i][2]
            if val < best_val:
                best_i, best_val = i, val
        filled.pop(best_i)
    filled = filled[:max_frames]

    return [
        SmartTimestamp(time_sec=round(t, 2), reason=r, transcript_text=transcript_window(entries, t))
        for t, r, _ in filled
    ]


def transcript_window(entries: list[TranscriptEntry], t: float, before: float = 4.0, after: float = 6.0) -> str:
    """Transcript text spoken around time t (used as the frame caption)."""
    parts = [e.text for e in entries if e.end_sec >= t - before and e.start_sec <= t + after]
    text = " ".join(parts)
    return text[:240]
