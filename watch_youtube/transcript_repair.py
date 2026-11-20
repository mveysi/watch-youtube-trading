"""Detect and repair broken stretches in a Whisper transcript.

Whisper (esp. on long audio) sometimes
  * loops:  "BASE BASE BASE BASE …", "Arz Bölgesi Arz Bölgesi …",
            "Bu sefer manipülasyonları. Bu sefer manipülasyonları. …"
  * goes quiet: one tiny segment ("Bİk") spanning 30s of real speech, or a
    gap with no segments at all.

Those time ranges are replaced with the YouTube subtitle lines for the same
range. Whisper's text is kept everywhere else (it spells jargon far better).
Replaced entries carry source="yt" so downstream readers know those words are
less reliable.
"""

from __future__ import annotations

import logging
import re

from . import TranscriptEntry

logger = logging.getLogger(__name__)

_WORD_RE = re.compile(r"\w+", re.UNICODE)

# Thresholds tuned on a real Turkish lecture: Whisper loops are long ("BASE" ×50,
# "Arz Bölgesi" ×14, "Bu sefer manipülasyonları" ×8) while a speaker's genuine
# emphasis is short ("alıcı, satıcı, alıcı, satıcı", "alıyorlar ×5").
MAX_NGRAM = 6          # look for repeated phrases up to this many words
MIN_REPEATS_UNIGRAM = 8
MIN_REPEATS_PHRASE = 3
MIN_LOOP_WORDS = 14    # a phrase loop must cover at least this many words in total
SPARSE_MIN_SEC = 8.0   # a segment this long …
SPARSE_WPS = 0.4       # … with fewer words/second than this is "near-silent"
GAP_MIN_SEC = 15.0     # no Whisper segment at all for this long


def has_repetition_loop(text: str) -> bool:
    """True if some 1–6 word phrase repeats back-to-back too many times."""
    words = [w.lower() for w in _WORD_RE.findall(text)]
    n_words = len(words)
    for n in range(1, MAX_NGRAM + 1):
        need = MIN_REPEATS_UNIGRAM if n == 1 else MIN_REPEATS_PHRASE
        if n * need > n_words:
            break
        for start in range(n_words - n * need + 1):
            gram = words[start:start + n]
            reps = 1
            pos = start + n
            while pos + n <= n_words and words[pos:pos + n] == gram:
                reps += 1
                pos += n
            if reps >= need and (n == 1 or n * reps >= MIN_LOOP_WORDS):
                return True
    return False


_TR_LETTERS = re.compile(r"[ıİşŞğĞüÜöÖçÇ]")
TR_MIN_WORDS = 12


def is_garbled_turkish(entry: TranscriptEntry) -> bool:
    """Whisper sometimes drops every Turkish-specific letter *and the rest of the
    word* ("Burası" → "Buras", "gerçekleşti" → "ger"), or silently translates a
    stretch into English. Either way a 12+ word Turkish segment ends up with no
    ı/ş/ğ/ü/ö/ç at all — which virtually never happens in real Turkish speech.
    Measured on 3 lectures: 6–14 segments per video (15–20% of speech time).
    """
    words = _WORD_RE.findall(entry.text)
    return len(words) >= TR_MIN_WORDS and not _TR_LETTERS.search(entry.text)


def looks_turkish(entries: list[TranscriptEntry]) -> bool:
    text = " ".join(e.text for e in entries)
    letters = sum(c.isalpha() for c in text) or 1
    return len(_TR_LETTERS.findall(text)) / letters > 0.01


def is_sparse(entry: TranscriptEntry) -> bool:
    dur = entry.end_sec - entry.start_sec
    if dur < SPARSE_MIN_SEC:
        return False
    return len(_WORD_RE.findall(entry.text)) / dur < SPARSE_WPS


def find_bad_ranges(
    entries: list[TranscriptEntry],
    duration: float | None = None,
    language: str | None = None,
) -> list[tuple[float, float]]:
    """Time ranges where the Whisper transcript can't be trusted."""
    turkish = language == "tr" or (language is None and looks_turkish(entries))
    bad: list[tuple[float, float]] = []
    prev_end = 0.0
    for e in entries:
        if e.start_sec - prev_end >= GAP_MIN_SEC:
            bad.append((prev_end, e.start_sec))
        if has_repetition_loop(e.text) or is_sparse(e) or (turkish and is_garbled_turkish(e)):
            bad.append((e.start_sec, e.end_sec))
        prev_end = max(prev_end, e.end_sec)
    if duration and duration - prev_end >= GAP_MIN_SEC:
        bad.append((prev_end, duration))
    return _merge_ranges(bad)


def _merge_ranges(ranges: list[tuple[float, float]], slack: float = 1.0) -> list[tuple[float, float]]:
    merged: list[tuple[float, float]] = []
    for a, b in sorted(ranges):
        if merged and a <= merged[-1][1] + slack:
            merged[-1] = (merged[-1][0], max(merged[-1][1], b))
        else:
            merged.append((a, b))
    return merged


def repair_with_fallback(
    whisper: list[TranscriptEntry],
    fallback: list[TranscriptEntry],
    duration: float | None = None,
    language: str | None = None,
) -> tuple[list[TranscriptEntry], int]:
    """Replace bad Whisper ranges with fallback (YouTube) lines.

    Returns (entries, number_of_ranges_repaired). Without a fallback the bad
    looping segments are dropped (an empty stretch is better than garbage).
    """
    turkish = language == "tr" or (language is None and looks_turkish(whisper))
    if fallback and turkish and not looks_turkish(fallback):
        # e.g. the only subtitle available is YouTube's English translation/dub
        logger.warning("Whisper repair: YouTube subtitle is not in the spoken language — not used for filling")
        fallback = []
    # Without a same-language fallback, keep garbled-but-readable Turkish text
    # (dropping it would lose more than it saves); still drop loops.
    bad = find_bad_ranges(whisper, duration, language if fallback else "xx")
    if not bad:
        return whisper, 0

    def in_bad(e: TranscriptEntry) -> bool:
        mid = (e.start_sec + e.end_sec) / 2
        return any(a <= mid <= b for a, b in bad)

    kept = [e for e in whisper if not in_bad(e)]
    filled = [
        TranscriptEntry(e.start_sec, e.end_sec, e.text, source="yt")
        for e in fallback if in_bad(e)
    ]
    repaired = sum(1 for a, b in bad if any(a <= (f.start_sec + f.end_sec) / 2 <= b for f in filled))
    if not fallback:
        logger.warning(f"Whisper: {len(bad)} broken range(s) dropped (no YouTube subtitle to fill from)")
    else:
        logger.info(f"Whisper: {len(bad)} broken range(s) detected, {repaired} filled from YouTube subtitles")
    out = sorted(kept + filled, key=lambda e: e.start_sec)
    return out, len(bad)
