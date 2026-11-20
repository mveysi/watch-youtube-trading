"""watch-youtube CLI entry point."""

import json
import logging
import shutil
import tempfile
import time
from datetime import date
from pathlib import Path

import click

from .extractor import check_ffmpeg, get_video_duration

_DEFAULT_GLOSSARY = Path(__file__).parent.parent / "data" / "glossary_trading_tr.json"


@click.command()
@click.argument("url")
@click.option(
    "--output-dir", "-o",
    type=click.Path(file_okay=False, writable=True, path_type=Path),
    default=Path("."),
    show_default=True,
    help="Directory to save storyboard images.",
)
@click.option(
    "--groq-api-key", "-k",
    envvar="GROQ_API_KEY",
    default=None,
    help="Groq API key for Whisper transcription (or set GROQ_API_KEY env var).",
)
@click.option(
    "--whisper", "prefer_whisper",
    is_flag=True,
    default=False,
    help="Transcribe with Groq Whisper even if YouTube subtitles exist (much better for "
         "English jargon inside non-English speech). Needs a Groq API key.",
)
@click.option(
    "--language", "-l",
    default=None,
    help="Spoken language hint for Whisper, ISO code (e.g. tr, en).",
)
@click.option(
    "--glossary",
    type=click.Path(dir_okay=False, path_type=Path),
    default=_DEFAULT_GLOSSARY,
    show_default=True,
    help="Glossary JSON; its 'whisper_prompt' is sent to Whisper as a vocabulary hint.",
)
@click.option(
    "--frames", "frame_mode",
    type=click.Choice(["visual", "transcript"]),
    default="visual",
    show_default=True,
    help="visual = scene-change detection + gap filling (language independent, best for "
         "slides/charts); transcript = legacy keyword/silence rules only.",
)
@click.option(
    "--max-frames", "-n",
    type=int,
    default=None,
    help="Maximum frames to extract. Default: scales with video length (12–60).",
)
@click.option(
    "--scene-threshold",
    type=float,
    default=0.03,
    show_default=True,
    help="ffmpeg scene score threshold for --frames visual (lower = more sensitive).",
)
@click.option(
    "--jpeg-quality", "-q",
    type=click.IntRange(1, 95),
    default=85,
    show_default=True,
    help="JPEG compression quality for storyboard output (1–95).",
)
@click.option(
    "--silence-gap", "-g",
    type=float,
    default=5.0,
    show_default=True,
    help="Minimum silence gap in seconds to trigger frame extraction (Rule B).",
)
@click.option(
    "--frame-format",
    type=click.Choice(["jpg", "png"]),
    default="jpg",
    show_default=True,
    help="Intermediate frame format (jpg=faster, png=lossless).",
)
@click.option(
    "--keep-temp",
    is_flag=True,
    default=False,
    help="Keep temporary video/frame files after processing.",
)
@click.option(
    "--learn/--no-learn",
    default=False,
    show_default=True,
    help="Update the self-learning keyword store from transcript-keyword frames.",
)
@click.option(
    "--cookies", "cookies_file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    help="Netscape cookies.txt for YouTube (use when YouTube asks to confirm you're not a bot). "
         "If omitted, ./cookies.txt is used automatically when present.",
)
@click.option(
    "--cookies-from-browser",
    default=None,
    metavar="BROWSER",
    help="Read YouTube cookies from a browser profile (firefox, chrome, edge, ...). The browser should be closed.",
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    default=False,
    help="Enable verbose (DEBUG) logging.",
)
def cli(
    url: str,
    output_dir: Path,
    groq_api_key: str | None,
    prefer_whisper: bool,
    language: str | None,
    glossary: Path,
    frame_mode: str,
    max_frames: int | None,
    scene_threshold: float,
    jpeg_quality: int,
    silence_gap: float,
    frame_format: str,
    keep_temp: bool,
    learn: bool,
    cookies_file: Path | None,
    cookies_from_browser: str | None,
    verbose: bool,
) -> None:
    """watch-youtube: YouTube video storyboard generator for Vision LLMs.

    Downloads a YouTube video, picks visually meaningful frames (scene changes,
    transcript cues, gap filling), compiles them into annotated storyboard grids
    and saves the full transcript + metadata next to them.

    \b
    Example:
      watch-youtube "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -o ./output -v
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        format="[%(asctime)s] %(levelname)s  %(message)s",
        datefmt="%H:%M:%S",
        level=log_level,
    )
    log = logging.getLogger("watch_youtube")
    # Third-party HTTP clients flood -v output (and would print request headers).
    for noisy in ("httpx", "httpcore", "groq", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    temp_dir = Path(tempfile.mkdtemp(prefix="watch_youtube_"))
    t_start = time.time()

    try:
        check_ffmpeg()

        log.info("Step 1/5 ▸ Downloading transcript + video...")
        from .downloader import download_video, set_auth
        if cookies_file is None and not cookies_from_browser and Path("cookies.txt").is_file():
            cookies_file = Path("cookies.txt")
        if cookies_file or cookies_from_browser:
            log.info(f"          YouTube auth: {'cookies file' if cookies_file else cookies_from_browser}")
        set_auth(cookies_file, cookies_from_browser)
        result = download_video(
            url, temp_dir, groq_api_key,
            prefer_whisper=prefer_whisper,
            whisper_prompt=_load_whisper_prompt(glossary),
            whisper_language=language,
        )
        log.info(
            f"          Transcript: {result.transcript_source} "
            f"({len(result.transcript_entries)} entries)"
        )
        if result.title:
            log.info(f"          Title: {result.title}  |  Channel: {result.channel}")

        # Each video gets its own subdirectory so storyboards never overwrite each other
        video_output_dir = output_dir / result.video_id
        video_output_dir.mkdir(parents=True, exist_ok=True)
        log.info(f"          Output dir: {video_output_dir}")

        log.info("Step 2/5 ▸ Saving transcript...")
        saved_transcript = _save_transcript(result, video_output_dir)
        for p in saved_transcript:
            log.info(f"          → {video_output_dir.name}/{p.name}")

        duration = get_video_duration(result.video_path) or result.duration
        if max_frames is None:
            from .scenes import auto_max_frames
            max_frames = auto_max_frames(duration)

        log.info(f"Step 3/5 ▸ Selecting frames ({frame_mode} mode, max {max_frames})...")
        from .analyzer import extract_smart_timestamps
        keyword_ts = extract_smart_timestamps(
            result.transcript_entries,
            silence_threshold=silence_gap,
            max_timestamps=max_frames if frame_mode == "transcript" else 500,
        )
        if frame_mode == "visual":
            from .scenes import detect_scene_changes, select_visual_timestamps
            scene_times = detect_scene_changes(result.video_path, scene_threshold)
            kw_only = [t for t in keyword_ts if not t.reason.startswith("fallback")]
            timestamps = select_visual_timestamps(
                scene_times, kw_only, result.transcript_entries, duration, max_frames,
            )
            log.info(
                f"          {len(scene_times)} scene changes, {len(kw_only)} transcript cues "
                f"→ {len(timestamps)} frames selected"
            )
        else:
            timestamps = keyword_ts
            log.info(f"          Found {len(timestamps)} transcript-based timestamps")
        if verbose:
            for ts in timestamps:
                log.debug(f"    {ts.time_sec:7.1f}s  [{ts.reason}]  {ts.transcript_text[:60]}")

        log.info("Step 4/5 ▸ Extracting frames with ffmpeg...")
        from .extractor import extract_frames
        frames = extract_frames(
            result.video_path,
            timestamps,
            temp_dir,
            fmt=frame_format,
        )
        log.info(f"          Extracted {len(frames)} frames successfully")
        if timestamps and not frames:
            # Never report success with no images — the Vision analysis would silently
            # fall back to transcript-only.
            raise EnvironmentError(
                f"No frames could be extracted from the video ({len(timestamps)} attempted). "
                f"The downloaded video file is probably broken; rerun with --keep-temp to inspect it."
            )

        log.info("Step 5/5 ▸ Compiling storyboard grids...")
        for old in video_output_dir.glob("storyboard_*.jpg"):
            old.unlink()
        from .compiler import compile_storyboards
        boards = compile_storyboards(frames, video_output_dir, jpeg_quality=jpeg_quality)

        _save_metadata(url, result, duration, frame_mode, timestamps, frames, boards, video_output_dir)

        if learn and result.transcript_entries and timestamps:
            from .analyzer import update_keyword_store
            new_kw = update_keyword_store(result.transcript_entries, keyword_ts)
            if new_kw:
                log.info(f"          Keyword store: learned {new_kw} new term(s) from this video")

        elapsed = time.time() - t_start
        log.info("=" * 62)
        log.info(f"  Done in {elapsed:.1f}s")
        log.info(f"  {len(frames)} frames → {len(boards)} storyboard grid(s)")
        for b in boards:
            size_kb = b.stat().st_size // 1024
            log.info(f"  → {video_output_dir.name}/{b.name}  ({size_kb} KB)")
        log.info(f"  → {video_output_dir.name}/transcript.txt, metadata.json")
        log.info("=" * 62)

    except ValueError as exc:
        logging.getLogger("watch_youtube").error(f"Video error: {exc}")
        raise click.Abort() from exc
    except EnvironmentError as exc:
        logging.getLogger("watch_youtube").error(str(exc))
        raise click.Abort() from exc
    finally:
        if not keep_temp:
            shutil.rmtree(temp_dir, ignore_errors=True)


def _load_whisper_prompt(glossary: Path | None) -> str | None:
    if not glossary or not glossary.exists():
        return None
    try:
        return json.loads(glossary.read_text(encoding="utf-8")).get("whisper_prompt")
    except Exception:
        return None


def _save_transcript(result, out_dir: Path) -> list[Path]:
    """Persist the raw subtitle file and a readable, timestamped transcript.txt."""
    saved: list[Path] = []
    for old in out_dir.glob("transcript_raw*"):   # no stale file from an earlier run
        old.unlink()
    # Whisper output → transcript_raw.srt ; YouTube subtitle → always transcript_raw.vtt/.srt
    raws: list[tuple[Path, str]] = []
    if result.transcript_path and Path(result.transcript_path).exists():
        raws.append((Path(result.transcript_path), "transcript_raw"))
    yt = result.youtube_transcript_path
    if yt and Path(yt).exists() and yt != result.transcript_path:
        raws.append((Path(yt), "transcript_raw_youtube"))
    for src, stem in raws:
        dst = out_dir / f"{stem}{src.suffix}"
        shutil.copyfile(src, dst)
        saved.append(dst)

    if result.transcript_entries:
        lines = [
            f"# {result.title or result.video_id}",
            f"# Kaynak: {result.transcript_source}  |  Kanal: {result.channel}",
        ]
        if result.whisper_repaired:
            lines.append(
                f"# Not: Whisper'ın döngüye girdiği/boş bıraktığı {result.whisper_repaired} bölüm "
                f"YouTube altyazısıyla dolduruldu; bu paragraflar [yt] ile işaretli (terimler daha az güvenilir)."
            )
        lines.append("")
        buf: list[str] = []
        t0 = 0.0
        has_yt = False

        def flush() -> None:
            tag = " [yt]" if has_yt else ""
            lines.append(f"[{_mmss(t0)}]{tag} " + " ".join(buf))

        for e in result.transcript_entries:
            if not buf:
                t0 = e.start_sec
                has_yt = False
            buf.append(e.text)
            has_yt = has_yt or e.source == "yt"
            if e.end_sec - t0 >= 30:
                flush()
                buf = []
        if buf:
            flush()
        txt = out_dir / "transcript.txt"
        txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
        saved.append(txt)
    return saved


def _save_metadata(url, result, duration, frame_mode, timestamps, frames, boards, out_dir: Path) -> None:
    per_board = 9
    data = {
        "url": url,
        "video_id": result.video_id,
        "title": result.title,
        "channel": result.channel,
        "duration_sec": duration,
        "transcript_source": result.transcript_source,
        "whisper_repaired_segments": result.whisper_repaired,
        "analyzed_at": date.today().isoformat(),
        "frame_mode": frame_mode,
        "frames": [
            {
                "time": _mmss(f.time_sec),
                "time_sec": f.time_sec,
                "reason": next((t.reason for t in timestamps if abs(t.time_sec - f.time_sec) < 0.01), ""),
                "storyboard": boards[i // per_board].name if boards and i // per_board < len(boards) else None,
            }
            for i, f in enumerate(frames)
        ],
        "storyboards": [b.name for b in boards],
    }
    (out_dir / "metadata.json").write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _mmss(sec: float) -> str:
    sec = int(sec)
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


if __name__ == "__main__":
    cli()
