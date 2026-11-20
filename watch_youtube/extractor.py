"""Extract video frames at smart timestamps via ffmpeg subprocess calls."""

import logging
import os
import shutil
import subprocess
from pathlib import Path

from . import ExtractedFrame, SmartTimestamp

logger = logging.getLogger(__name__)

_FFMPEG_TIMEOUT = 30  # seconds per frame extraction
_MIN_FRAME_BYTES = 100  # skip black/corrupt frames smaller than this


_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _find_bundled_ffmpeg() -> Path | None:
    """Look for an ffmpeg unpacked anywhere under <project>/tools/ (any version folder)."""
    tools = _PROJECT_ROOT / "tools"
    if not tools.is_dir():
        return None
    for name in ("ffmpeg.exe", "ffmpeg"):
        hits = sorted(tools.rglob(name), reverse=True)  # newest version folder first
        for hit in hits:
            if hit.is_file():
                return hit
    return None


def _add_to_path(bin_dir: Path) -> None:
    """Prepend bin_dir to PATH so yt-dlp and ffprobe lookups find the same ffmpeg."""
    current = os.environ.get("PATH", "")
    if str(bin_dir) not in current.split(os.pathsep):
        os.environ["PATH"] = str(bin_dir) + os.pathsep + current


def check_ffmpeg() -> str:
    """Return path to ffmpeg binary or raise EnvironmentError with install tip.

    Search order: PATH → <project>/tools/**/ffmpeg(.exe) → macOS Homebrew.
    A bundled or Homebrew ffmpeg is also added to PATH for this process.
    """
    binary = shutil.which("ffmpeg")
    if binary:
        return binary

    for candidate in (_find_bundled_ffmpeg(), Path("/opt/homebrew/bin/ffmpeg")):
        if candidate and candidate.exists():
            _add_to_path(candidate.parent)
            logger.debug(f"Using ffmpeg at {candidate}")
            return str(candidate)

    raise EnvironmentError(
        "ffmpeg not found. Install it with:\n"
        "  Windows: winget install Gyan.FFmpeg  (or unzip the ffmpeg 'essentials' build into ./tools/)\n"
        "  macOS:   brew install ffmpeg\n"
        "  Ubuntu:  sudo apt install ffmpeg"
    )


def get_video_duration(video_path: Path) -> float | None:
    """Use ffprobe to get video duration in seconds. Returns None on failure."""
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        try:
            ffprobe = str(Path(check_ffmpeg()).with_name(
                "ffprobe.exe" if os.name == "nt" else "ffprobe"))
        except EnvironmentError:
            return None
        if not Path(ffprobe).exists():
            return None
    try:
        result = subprocess.run(
            [
                ffprobe, "-v", "quiet",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(video_path),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return float(result.stdout.strip())
    except Exception:
        return None


def extract_frames(
    video_path: Path,
    timestamps: list[SmartTimestamp],
    output_dir: Path,
    quality: int = 2,
    fmt: str = "jpg",
) -> list[ExtractedFrame]:
    """Extract one frame per smart timestamp. Skips failures gracefully."""
    ffmpeg_bin = check_ffmpeg()
    frames: list[ExtractedFrame] = []

    for idx, ts in enumerate(timestamps):
        out_path = output_dir / f"frame_{idx:04d}_{int(ts.time_sec):05d}s.{fmt}"
        success = _extract_single_frame(ffmpeg_bin, video_path, ts.time_sec, out_path, quality)
        if success:
            frames.append(ExtractedFrame(
                time_sec=ts.time_sec,
                path=out_path,
                transcript_text=ts.transcript_text,
            ))
        else:
            logger.debug(f"Skipping frame at {ts.time_sec:.1f}s (extraction failed or empty)")

    return frames


def _extract_single_frame(
    ffmpeg_bin: str,
    video_path: Path,
    time_sec: float,
    output_path: Path,
    quality: int,
) -> bool:
    """
    Extract a single frame using input-seeking (-ss before -i) for speed.
    Returns True if a valid non-empty frame was written.
    """
    cmd = [
        ffmpeg_bin,
        "-ss", f"{time_sec:.3f}",   # fast input seek
        "-i", str(video_path),
        "-frames:v", "1",
        "-q:v", str(quality),        # JPEG quality: 1=best, 31=worst
        "-y",                        # overwrite without prompting
        str(output_path),
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=_FFMPEG_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        logger.warning(f"ffmpeg timed out at {time_sec:.1f}s")
        return False

    if result.returncode != 0:
        logger.debug(f"ffmpeg error at {time_sec:.1f}s: {result.stderr[-200:]}")
        return False

    # Reject suspiciously small files (black frame / seek past end of video)
    if not output_path.exists() or output_path.stat().st_size < _MIN_FRAME_BYTES:
        return False

    if _is_mostly_black(output_path):
        logger.debug(f"Dropping black/blank frame at {time_sec:.1f}s")
        output_path.unlink(missing_ok=True)
        return False

    return True


def _is_mostly_black(path: Path, threshold: float = 12.0) -> bool:
    """True when the frame's mean brightness (0-255) is below threshold."""
    try:
        from PIL import Image, ImageStat
        with Image.open(path) as img:
            gray = img.convert("L").resize((64, 36))
            return ImageStat.Stat(gray).mean[0] < threshold
    except Exception:
        return False
