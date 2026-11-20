"""Download YouTube transcripts, audio, and video via yt-dlp."""

import re
import time
import logging
from collections import deque
from pathlib import Path

import yt_dlp
import webvtt

from . import DownloadResult, TranscriptEntry

logger = logging.getLogger(__name__)

_TIMECODE_RE = re.compile(r"(\d+):(\d{2}):(\d{2})[.,](\d+)")
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")

# YouTube authentication (only needed when YouTube answers "Sign in to confirm you're not a bot").
# Set once via set_auth(); merged into every yt-dlp call. Cookies are only read, never written.
_AUTH_OPTS: dict = {}


def set_auth(cookies_file: Path | None = None, cookies_from_browser: str | None = None) -> None:
    """Configure yt-dlp authentication from a Netscape cookies.txt file or a browser profile."""
    _AUTH_OPTS.clear()
    if cookies_file:
        _AUTH_OPTS["cookiefile"] = str(cookies_file)
    elif cookies_from_browser:
        _AUTH_OPTS["cookiesfrombrowser"] = (cookies_from_browser,)


def _ydl(opts: dict) -> "yt_dlp.YoutubeDL":
    return yt_dlp.YoutubeDL({**opts, **_AUTH_OPTS})


def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from URL. Falls back to 'unknown'."""
    patterns = [
        r"(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})",
    ]
    for pattern in patterns:
        m = re.search(pattern, url)
        if m:
            return m.group(1)
    return "unknown"


def download_video(
    url: str,
    output_dir: Path,
    groq_api_key: str | None = None,
    prefer_whisper: bool = False,
    whisper_prompt: str | None = None,
    whisper_language: str | None = None,
) -> DownloadResult:
    """Orchestrate transcript + video download with Whisper fallback.

    prefer_whisper: transcribe with Groq Whisper even when YouTube subtitles
    exist (auto-captions badly mangle English jargon inside non-English speech).
    The YouTube subtitle is still kept as a fallback if Whisper fails.
    """
    video_id = extract_video_id(url)
    if video_id != "unknown":
        # Strip playlist/index params so only this single video is ever fetched.
        url = f"https://www.youtube.com/watch?v={video_id}"
    transcript_path, fmt, orig_lang = _download_transcript(url, output_dir, whisper_language)
    if orig_lang:
        logger.debug(f"Original spoken language: {orig_lang}")
    whisper_language = whisper_language or orig_lang

    entries: list[TranscriptEntry] = []
    source = "none"
    youtube_path = transcript_path
    repaired = 0

    if transcript_path is not None:
        entries = _parse_transcript_file(transcript_path, fmt)
        source = fmt
        logger.debug(f"Parsed {len(entries)} entries from {fmt} transcript")

    want_whisper = groq_api_key and (prefer_whisper or transcript_path is None)
    if prefer_whisper and not groq_api_key:
        logger.warning("--whisper requested but no GROQ_API_KEY — using YouTube subtitles")
    if want_whisper:
        logger.info("Downloading audio for Groq Whisper transcription...")
        try:
            audio_path = _download_audio(url, output_dir)
            w_entries = _transcribe_chunked(audio_path, groq_api_key, whisper_prompt, whisper_language)
            if w_entries:
                from .transcript_repair import repair_with_fallback
                from .extractor import get_video_duration
                w_entries, repaired = repair_with_fallback(
                    w_entries, entries, get_video_duration(audio_path), whisper_language
                )
                entries = w_entries
                source = "whisper"
                transcript_path = _write_srt(w_entries, output_dir / f"{video_id}.whisper.srt")
                logger.debug(f"Whisper returned {len(entries)} entries")
        except Exception as e:
            if not entries:
                raise
            logger.warning(f"Whisper failed ({e}) — keeping YouTube subtitles")

    if not entries:
        logger.warning("No transcript and no GROQ_API_KEY — frames will be chosen visually only")
        source = "synthetic"

    video_path, info = _download_video_file(url, output_dir)
    return DownloadResult(
        video_path=video_path,
        transcript_entries=entries,
        transcript_source=source,
        temp_dir=output_dir,
        video_id=video_id,
        transcript_path=transcript_path,
        youtube_transcript_path=youtube_path,
        whisper_repaired=repaired,
        title=info.get("title") or "",
        channel=info.get("channel") or info.get("uploader") or "",
        duration=info.get("duration"),
    )


CHUNK_SEC = 600      # Whisper loops/skips far less on ~10-min pieces than on a whole lecture
OVERLAP_SEC = 5
PROMPT_MAX_CHARS = 250


def _transcribe_chunked(
    audio_path: Path,
    api_key: str,
    prompt: str | None,
    language: str | None,
) -> list[TranscriptEntry]:
    """Split audio into ~10-min chunks (5s overlap), transcribe each, stitch back."""
    import subprocess
    from .extractor import check_ffmpeg, get_video_duration

    duration = get_video_duration(audio_path)
    if not duration or duration <= CHUNK_SEC + OVERLAP_SEC:
        return _transcribe_with_whisper(audio_path, api_key, prompt, language)

    ffmpeg_bin = check_ffmpeg()
    entries: list[TranscriptEntry] = []
    starts = list(range(0, int(duration), CHUNK_SEC))
    for i, start in enumerate(starts):
        chunk = audio_path.with_name(f"{audio_path.stem}_part{i:02d}.mp3")
        subprocess.run(
            [ffmpeg_bin, "-hide_banner", "-loglevel", "error", "-y",
             "-ss", str(start), "-t", str(CHUNK_SEC + OVERLAP_SEC),
             "-i", str(audio_path), "-c", "copy", str(chunk)],
            check=True, capture_output=True,
        )
        logger.info(f"  Whisper chunk {i + 1}/{len(starts)} ({start // 60}–{min(start + CHUNK_SEC, int(duration)) // 60} dk)")
        part = _transcribe_with_whisper(chunk, api_key, prompt, language)
        # Keep each segment in exactly one chunk: split the overlap down the middle.
        lo = start + (OVERLAP_SEC / 2 if i > 0 else 0)
        hi = start + CHUNK_SEC + OVERLAP_SEC / 2 if i < len(starts) - 1 else float("inf")
        for e in part:
            abs_start = e.start_sec + start
            if lo <= abs_start < hi:
                entries.append(TranscriptEntry(abs_start, e.end_sec + start, e.text))
    return entries


def _write_srt(entries: list[TranscriptEntry], path: Path) -> Path:
    def tc(s: float) -> str:
        ms = int(round(s * 1000))
        h, ms = divmod(ms, 3_600_000)
        m, ms = divmod(ms, 60_000)
        sec, ms = divmod(ms, 1000)
        return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"
    blocks = [f"{i}\n{tc(e.start_sec)} --> {tc(e.end_sec)}\n{e.text}\n" for i, e in enumerate(entries, 1)]
    path.write_text("\n".join(blocks), encoding="utf-8")
    return path


def _download_transcript(
    url: str, output_dir: Path, language: str | None = None,
) -> tuple[Path | None, str, str | None]:
    """Download subtitles in the video's *original spoken* language.

    Returns (path, format, original_language). YouTube now adds AI-dubbed audio
    tracks (e.g. English) to many videos, which come with their own "-orig"
    captions ("en-US-orig" next to the real "tr-orig") — so "-orig" alone is not
    enough; the language must match the original audio.
    """
    langs = [".*-orig", "en", "en-US", "en-GB"]
    if language:
        langs = [f"{language}-orig", language] + langs
    opts = {
        "outtmpl": str(output_dir / "%(id)s.%(ext)s"),
        "quiet": True,
        "noplaylist": True,  # playlist URLs (&list=...) must only fetch this one video
        "no_warnings": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": langs,
        "subtitlesformat": "vtt",
        "skip_download": True,
        "extractor_args": {"youtube": {"player_client": ["android"]}},
    }
    subtitle_error: Exception | None = None
    info: dict = {}
    try:
        with _ydl(opts) as ydl:
            info = ydl.extract_info(url, download=True) or {}
    except yt_dlp.utils.DownloadError as e:
        subtitle_error = e

    orig = (language or info.get("language") or "").split("-")[0].lower() or None

    def rank(p: Path) -> int:
        name = p.name
        if orig and f".{orig}-orig." in name:
            return 0
        if orig and (f".{orig}." in name or f".{orig}-" in name):
            return 1
        if "-orig." in name and not orig:
            return 2
        if ".en" in name:
            return 4
        return 3

    for ext in ("vtt", "srt"):
        matches = list(output_dir.glob(f"*.{ext}"))
        if matches:
            matches.sort(key=lambda p: (rank(p), p.name))
            logger.debug(f"Subtitles available: {[m.name for m in matches]} → using {matches[0].name}")
            return matches[0], ext, orig

    if subtitle_error is not None:
        raise ValueError(f"Cannot access video: {subtitle_error}") from subtitle_error

    return None, "none", orig


def _download_audio(url: str, output_dir: Path) -> Path:
    """Download audio-only as .mp3 for Whisper transcription."""
    opts = {
        "outtmpl": str(output_dir / "%(id)s_audio.%(ext)s"),
        "quiet": True,
        "noplaylist": True,  # playlist URLs (&list=...) must only fetch this one video
        "no_warnings": True,
        # Prefer the original audio track over YouTube's AI-dubbed ones.
        "format": "bestaudio[format_note*=original]/bestaudio/best",
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}],
        # Mono 16 kHz 32 kbps ≈ 14 MB/hour — stays under Groq's 25 MB upload limit
        # for videos up to ~1.5h, with no loss for speech recognition.
        "postprocessor_args": {"extractaudio": ["-ac", "1", "-ar", "16000", "-b:a", "32k"]},
    }
    with _ydl(opts) as ydl:
        ydl.download([url])

    matches = list(output_dir.glob("*_audio.mp3"))
    if not matches:
        raise RuntimeError("Audio download produced no file")
    return matches[0]


# Player clients tried in order. The default client returned complete 720p files
# in testing; the "android" client sometimes returns a truncated 360p file that
# yt-dlp still reports as 100% downloaded (seen on a 23-min lecture: 583 KB).
_VIDEO_CLIENTS: list[list[str] | None] = [None, ["android"]]


def _download_video_file(url: str, output_dir: Path) -> tuple[Path, dict]:
    """Download an MP4 for frame extraction and verify it is complete; return (path, info)."""
    last_problem = ""
    for client in _VIDEO_CLIENTS:
        for stale in output_dir.glob("*_video*"):
            stale.unlink(missing_ok=True)
        opts = {
            "outtmpl": str(output_dir / "%(id)s_video.%(ext)s"),
            "quiet": True,
            "noplaylist": True,  # playlist URLs (&list=...) must only fetch this one video
            "no_warnings": True,
            "format": (  # prefer H.264: AV1 decodes several times slower during scene detection
                "bestvideo[ext=mp4][vcodec^=avc1][height<=1080]+bestaudio[ext=m4a]/"
                "bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/"
                "bestvideo[height<=1080]+bestaudio/best[ext=mp4]/best"
            ),
            "merge_output_format": "mp4",
        }
        if client:
            opts["extractor_args"] = {"youtube": {"player_client": client}}
        label = client[0] if client else "default"
        try:
            with _ydl(opts) as ydl:
                info = ydl.extract_info(url, download=True) or {}
        except yt_dlp.utils.DownloadError as e:
            last_problem = f"{label}: {e}"
            logger.warning(f"Video download failed with client '{label}' — trying next")
            continue

        matches = list(output_dir.glob("*_video.mp4")) or list(output_dir.glob("*.mp4"))
        if not matches:
            last_problem = f"{label}: no .mp4 produced"
            continue
        ok, why = _video_is_complete(matches[0], info.get("duration"))
        if ok:
            if client:
                logger.info(f"Video downloaded with fallback client '{label}'")
            return matches[0], info
        last_problem = f"{label}: {why}"
        logger.warning(f"Downloaded video looks incomplete ({why}) with client '{label}' — retrying")

    raise RuntimeError(f"Could not download a complete video file ({last_problem})")


def _video_is_complete(path: Path, expected_duration: float | None) -> tuple[bool, str]:
    """Decode one frame near the end; a truncated download fails here."""
    import subprocess
    from .extractor import check_ffmpeg

    if not expected_duration:
        return True, ""
    probe_at = max(0.0, expected_duration * 0.9)
    result = subprocess.run(
        [check_ffmpeg(), "-v", "error", "-ss", f"{probe_at:.1f}", "-i", str(path),
         "-frames:v", "1", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60,
    )
    err = result.stderr.lower()
    if result.returncode != 0 or "partial file" in err or "invalid data" in err:
        size_kb = path.stat().st_size // 1024
        return False, f"cannot decode at {probe_at:.0f}s, file {size_kb} KB"
    return True, ""


def _transcribe_with_whisper(
    audio_path: Path,
    api_key: str,
    prompt: str | None = None,
    language: str | None = None,
) -> list[TranscriptEntry]:
    """Transcribe audio via Groq Whisper API with segment-level timestamps.

    prompt: vocabulary hint (e.g. trading jargon) — Whisper spells these terms
    correctly far more often when they appear in the prompt.
    """
    from groq import Groq, RateLimitError

    size_mb = audio_path.stat().st_size / 1_048_576
    if size_mb > 25:
        raise RuntimeError(f"Audio is {size_mb:.0f} MB — over Groq's 25 MB limit")

    client = Groq(api_key=api_key)
    extra: dict = {}
    if prompt:
        # Whisper treats the prompt as "previous transcript". A long keyword list
        # makes it output garbage (measured: 728-char list → 277 nonsense words
        # for 10 min of speech). Keep it to a short natural sentence.
        if len(prompt) > PROMPT_MAX_CHARS or prompt.count(",") > 12:
            logger.warning(
                f"Whisper prompt is long/list-like ({len(prompt)} chars) — truncating to "
                f"{PROMPT_MAX_CHARS}. Use a short natural sentence (see glossary whisper_prompt_note)."
            )
            prompt = prompt[:PROMPT_MAX_CHARS].rsplit(" ", 1)[0]
        extra["prompt"] = prompt
    if language:
        extra["language"] = language

    for attempt in range(2):
        try:
            with audio_path.open("rb") as f:
                response = client.audio.transcriptions.create(
                    file=(audio_path.name, f),
                    model="whisper-large-v3-turbo",
                    response_format="verbose_json",
                    timestamp_granularities=["segment"],
                    **extra,
                )
            break
        except RateLimitError:
            if attempt == 0:
                logger.warning("Groq rate limit hit — retrying in 60s...")
                time.sleep(60)
            else:
                raise

    # Depending on the groq SDK version, segments arrive as objects or plain dicts.
    def field(seg, name):
        return seg.get(name) if isinstance(seg, dict) else getattr(seg, name, None)

    entries = []
    for seg in getattr(response, "segments", None) or []:
        text = _WHITESPACE_RE.sub(" ", (field(seg, "text") or "").strip())
        if text:
            entries.append(TranscriptEntry(
                start_sec=float(field(seg, "start")),
                end_sec=float(field(seg, "end")),
                text=text,
            ))
    return entries


def _parse_transcript_file(path: Path, fmt: str) -> list[TranscriptEntry]:
    if fmt == "vtt":
        return _parse_vtt(path)
    return _parse_srt(path)


def _parse_vtt(path: Path) -> list[TranscriptEntry]:
    """Parse WebVTT using webvtt-py; strips HTML tags and deduplicates rolling-window lines."""
    entries = []
    try:
        captions = webvtt.read(str(path))
    except Exception:
        # Some auto-captions have malformed headers; fall back to raw read
        captions = webvtt.read_buffer(path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True))

    # Auto-captions repeat each line across a few consecutive cues (rolling window).
    # Only dedupe against the last few kept lines — a global set would also delete
    # phrases the speaker genuinely repeats later ("burada kırılım var").
    recent: deque[str] = deque(maxlen=3)
    for cap in captions:
        clean = _HTML_TAG_RE.sub("", cap.text)
        clean = _WHITESPACE_RE.sub(" ", clean).strip()
        if not clean or clean in recent:
            continue
        recent.append(clean)
        entries.append(TranscriptEntry(
            start_sec=_timecode_to_seconds(cap.start),
            end_sec=_timecode_to_seconds(cap.end),
            text=clean,
        ))
    return entries


_SRT_BLOCK_RE = re.compile(
    r"\d+\r?\n"
    r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})\r?\n"
    r"([\s\S]*?)(?=\n\s*\n|\Z)",
    re.MULTILINE,
)


def _parse_srt(path: Path) -> list[TranscriptEntry]:
    """Parse SRT subtitle file with pure regex."""
    text = path.read_text(encoding="utf-8", errors="replace")
    entries = []
    for m in _SRT_BLOCK_RE.finditer(text):
        start_raw, end_raw, body = m.groups()
        clean = _HTML_TAG_RE.sub("", body).strip()
        clean = _WHITESPACE_RE.sub(" ", clean)
        if clean:
            entries.append(TranscriptEntry(
                start_sec=_timecode_to_seconds(start_raw),
                end_sec=_timecode_to_seconds(end_raw),
                text=clean,
            ))
    return entries


def _timecode_to_seconds(tc: str) -> float:
    """Convert HH:MM:SS.mmm or HH:MM:SS,mmm to float seconds."""
    tc = tc.strip().replace(",", ".")
    parts = tc.split(":")
    h, m, s = float(parts[0]), float(parts[1]), float(parts[2])
    return h * 3600 + m * 60 + s
