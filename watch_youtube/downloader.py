"""Download YouTube transcripts, audio, and video via yt-dlp."""

import re
import time
import logging
from pathlib import Path

import yt_dlp
import webvtt

from . import DownloadResult, TranscriptEntry

logger = logging.getLogger(__name__)

_TIMECODE_RE = re.compile(r"(\d+):(\d{2}):(\d{2})[.,](\d+)")
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")


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
    transcript_path, fmt = _download_transcript(url, output_dir)

    entries: list[TranscriptEntry] = []
    source = "none"

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
            w_entries = _transcribe_with_whisper(audio_path, groq_api_key, whisper_prompt, whisper_language)
            if w_entries:
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
        title=info.get("title") or "",
        channel=info.get("channel") or info.get("uploader") or "",
        duration=info.get("duration"),
    )


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


def _download_transcript(url: str, output_dir: Path) -> tuple[Path | None, str]:
    """Try manual then auto-generated subtitles; return (path, format) or (None, 'none')."""
    opts = {
        "outtmpl": str(output_dir / "%(id)s.%(ext)s"),
        "quiet": True,
        "noplaylist": True,  # playlist URLs (&list=...) must only fetch this one video
        "no_warnings": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": [".*-orig", "en", "en-US", "en-GB"],
        "subtitlesformat": "vtt",
        "skip_download": True,
        "extractor_args": {"youtube": {"player_client": ["android"]}},
    }
    subtitle_error: Exception | None = None
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
    except yt_dlp.utils.DownloadError as e:
        subtitle_error = e

    for ext in ("vtt", "srt"):
        matches = list(output_dir.glob(f"*.{ext}"))
        if matches:
            matches.sort(key=lambda p: 0 if ".en." in p.name else 1)
            return matches[0], ext

    if subtitle_error is not None:
        raise ValueError(f"Cannot access video: {subtitle_error}") from subtitle_error

    return None, "none"


def _download_audio(url: str, output_dir: Path) -> Path:
    """Download audio-only as .mp3 for Whisper transcription."""
    opts = {
        "outtmpl": str(output_dir / "%(id)s_audio.%(ext)s"),
        "quiet": True,
        "noplaylist": True,  # playlist URLs (&list=...) must only fetch this one video
        "no_warnings": True,
        "format": "bestaudio/best",
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}],
        # Mono 16 kHz 32 kbps ≈ 14 MB/hour — stays under Groq's 25 MB upload limit
        # for videos up to ~1.5h, with no loss for speech recognition.
        "postprocessor_args": {"extractaudio": ["-ac", "1", "-ar", "16000", "-b:a", "32k"]},
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

    matches = list(output_dir.glob("*_audio.mp3"))
    if not matches:
        raise RuntimeError("Audio download produced no file")
    return matches[0]


def _download_video_file(url: str, output_dir: Path) -> tuple[Path, dict]:
    """Download best quality MP4 video for frame extraction; return (path, info)."""
    opts = {
        "outtmpl": str(output_dir / "%(id)s_video.%(ext)s"),
        "quiet": True,
        "noplaylist": True,  # playlist URLs (&list=...) must only fetch this one video
        "no_warnings": True,
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best[ext=mp4]/best",
        "merge_output_format": "mp4",
        "extractor_args": {"youtube": {"player_client": ["android"]}},
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True) or {}

    matches = list(output_dir.glob("*_video.mp4"))
    if not matches:
        # Some videos download without the _video suffix when merge happens
        matches = list(output_dir.glob("*.mp4"))
    if not matches:
        raise RuntimeError("Video download produced no .mp4 file")
    return matches[0], info


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
        extra["prompt"] = prompt[:800]
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

    seen: set[str] = set()
    for cap in captions:
        clean = _HTML_TAG_RE.sub("", cap.text)
        clean = _WHITESPACE_RE.sub(" ", clean).strip()
        if not clean or clean in seen:
            continue
        seen.add(clean)
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
