---
name: watch-youtube
description: Analyze a YouTube video by downloading its transcript, extracting visually meaningful frames (scene-change segments + transcript cues + gap filling), and compiling them into annotated storyboard grids optimized for Vision LLM token efficiency. After analysis, writes extracted knowledge to docs/wiki/ following wiki-schema rules. Use this skill whenever the user provides a YouTube URL and wants to analyze, summarize, or understand a video's visual content. Trigger on: "analyze this YouTube video", "understand what's shown in this video", "extract key frames", "summarize this tutorial", "what does this video show", "create a storyboard", "compress this video for LLM", "vision LLM video input".
---

# watch-youtube: YouTube Video Storyboard for Vision LLMs

Turns a YouTube video into annotated JPEG storyboard grids + a saved transcript, analyzes both, and writes the extracted knowledge to `docs/wiki/` using wiki-schema rules.

## When the user invokes this skill

The goal is not to summarise each lesson but to **grow one consistent body of knowledge**: every new lesson adds to, refines or corrects what the wiki already knows (course series build on themselves).

0. If `docs/wiki/` does not exist yet (fresh clone), create it by copying everything in `docs/wiki_template/` (`Index.md`, `Videos.md`, `Playbook.md`, `LearningLog.md`) into it. If it exists but a template file is missing (e.g. `LearningLog.md` after an update), copy just that file.
1. Extract the video ID and check `docs/wiki/Videos.md` — if already analyzed, answer from the wiki instead.
2. Run the pipeline (see **Running the pipeline**). Playlist URLs (`&list=...`) are fine — only the single video is fetched. **If `GROQ_API_KEY` is set, always use `--whisper -l <lang>`** (Turkish videos: `-l tr`).
3. **Prepare before reading the lesson (active learning)** — see **Before the lesson**: run `playbook-check`, read the open/expected questions and the rules/pages related to this lesson's topic, and write down which questions this lesson might answer.
4. Read **both** sources from `output/<video_id>/`:
   - `storyboard_page_*.jpg` — what was on screen (slides, charts, labels)
   - `transcript.txt` — what was said (timestamped, 30s paragraphs). For talk-heavy videos this is the primary source; read all of it. Paragraphs tagged `[yt]` were filled from YouTube subtitles because Whisper failed there — jargon in them is less reliable.
   - `metadata.json` — title, channel, duration, which frame came from where, `whisper_repaired_segments`
5. Correct transcript recognition errors (see **Transcript quality**).
6. Show the user a structured analysis.
7. Update concept pages in `docs/wiki/` (see **Writing to docs/wiki**): current knowledge in the main text, one line per change in *Tanımın Gelişimi*.
8. **Update `docs/wiki/Playbook.md`** (see **Playbook**): add/refine rules (acceptance filter!), close answered questions, open new ones, record contradictions.
9. **Propagate changes** (see **Change propagation**): every rule you changed → check its *İlgili* rules and every page that mentions it.
10. Add the video record to `docs/wiki/Videos.md`, update `docs/wiki/Index.md`, and update any series tracker page.
11. Run `playbook-check --write`; fix every ✖ error before continuing (warnings: fix if they are real mistakes).
12. **Append the lesson entry to `docs/wiki/LearningLog.md`** (format in that file) — append only, never rewrite older entries, never read the whole file. Its "Bilgi durumu" line comes from step 11.
13. Report anything the pipeline likely missed (see **Coverage check**).
14. **End with the Quality Report** (see **Quality Report**) — always, as the last thing in your reply.

---

## Setup (run once per environment)

**Windows (this machine)** — run from the project root in Git Bash:

```bash
export PYTHONIOENCODING=utf-8   # Turkish output in the console
# ffmpeg: found automatically on PATH or anywhere under ./tools/ (any version folder)
.venv/Scripts/pip install -r requirements.txt
.venv/Scripts/pip install -e .
.venv/Scripts/python -m spacy download en_core_web_sm
```

**macOS / Linux:**

```bash
source .venv/bin/activate
pip install -r requirements.txt && pip install -e .
python -m spacy download en_core_web_sm
brew install ffmpeg   # or: sudo apt install ffmpeg
```

---

## Running the pipeline

Windows (Git Bash, project root):

```bash
export PYTHONIOENCODING=utf-8
.venv/Scripts/watch-youtube.exe "<YOUTUBE_URL>" -o ./output -v
.venv/Scripts/playbook-check.exe            # knowledge state + format check (add --write after updating the Playbook)
```

macOS / Linux: `watch-youtube "<YOUTUBE_URL>" -o ./output -v`

With a Groq key (recommended for non-English videos full of English jargon):

```bash
GROQ_API_KEY="gsk_..." .venv/Scripts/watch-youtube.exe "<URL>" -o ./output --whisper -l tr
```

### Key options

| Flag | Default | Purpose |
|------|---------|---------|
| `--output-dir / -o` | `.` | Where to save outputs (a `<video_id>/` subfolder is created) |
| `--frames` | `visual` | `visual` = scene-change segments + transcript cues + gap fill (language independent). `transcript` = legacy keyword/silence rules only |
| `--max-frames / -n` | auto | Frame budget. Auto ≈ one frame per 35s, clamped 12–60 |
| `--scene-threshold` | `0.03` | ffmpeg scene score threshold (lower = more sensitive) |
| `--whisper` | off | Use Groq Whisper even when YouTube subtitles exist |
| `--language / -l` | auto | Whisper language hint (`tr`, `en`, …) |
| `--glossary` | `data/glossary_trading_tr.json` | Its `whisper_prompt` is sent to Whisper as a vocabulary hint |
| `--groq-api-key / -k` | env `GROQ_API_KEY` | Groq key for Whisper |
| `--learn/--no-learn` | `--no-learn` | Self-learning keyword store (off by default — see below) |
| `--jpeg-quality / -q` | `85` | Storyboard JPEG quality |
| `--keep-temp` | off | Keep the downloaded video and raw frames |
| `--verbose / -v` | off | Per-frame debug output |

### Outputs (`output/<video_id>/`)

| File | Content |
|------|---------|
| `storyboard_page_NNN.jpg` | 3×3 grids, timestamp badge + spoken caption under each frame |
| `transcript.txt` | Full readable transcript, `[mm:ss]` every ~30s |
| `transcript_raw.vtt` | YouTube subtitle in the video's original spoken language (AI-dub captions are skipped) |
| `transcript_raw.srt` + `transcript_raw_youtube.vtt` | With `--whisper`: Whisper output + the YouTube fallback |
| `metadata.json` | URL, title, channel, duration, transcript source, every frame's time + selection reason |

---

## Pipeline architecture

```
YouTube URL ──(playlist params stripped)
    │
    ▼
downloader.py   Subtitles (YouTube VTT) → optional Groq Whisper (--whisper, glossary prompt)
    │           Video MP4 + title/channel/duration metadata
    ▼
main.py         Save transcript.txt + raw subtitle
    ▼
analyzer.py     Transcript cues: EN + TR "showing" phrases, domain clusters (incl. trading)
    ▼
scenes.py       ffmpeg scene detection → stable segments → take each segment's END state
    │           (slide fully drawn); longer segments = higher priority;
    │           fill gaps > ~60s (prefer transcript cues); trim to budget evenly
    ▼
extractor.py    ffmpeg frame grab; drops black/blank frames
    ▼
compiler.py     Pillow grids (Turkish-capable fonts: Segoe UI / Arial)
    ▼
output/<video_id>/  storyboards + transcript.txt + metadata.json
    ▼
Vision LLM analysis → docs/wiki/
```

**Self-learning keyword store** (`data/keyword_store.json`) is off by default. When enabled with `--learn`, it learns only from transcript-keyword frames (never from scene/gap-fill picks) and skips Turkish function words. Builtin keywords are always merged in from code.

---

## Transcript quality

YouTube auto-captions of non-English speech badly mangle English jargon (e.g. Turkish trading videos: "Hayır hayır" = Higher High, "Boz" = BOS, "Play Station" = Price Action).

- Use `data/glossary_trading_tr.json` → `asr_corrections` as a **lookup guide** while reading. Do NOT blindly replace — always confirm against context and on-screen labels in the storyboards.
- When you find a new recurring error, **add it to `asr_corrections`** so future videos benefit.
- Add a short **"Transkript Notu"** section at the end of each wiki page listing the corrections you applied and anything still uncertain (mark uncertain terms "(muhtemel)").
- If a Groq key is available, prefer `--whisper` for such videos.

---

## Coverage check

Before writing the wiki, sanity-check that nothing important was missed:

- Does the transcript mention a slide/chart/summary ("ekranda", "neler öğrendik", "özet", "şimdi grafiğe bakalım") at a time with no nearby frame?
- Talking-head videos: short on-screen captions (lower-thirds, keyword cards) can fall between picks.
- If in doubt, rerun with `--keep-temp` and a larger `-n`, or build a quick contact sheet:
  `ffmpeg -i video.mp4 -vf "fps=1/10,scale=240:-2,tile=8x10" -frames:v 1 contact.jpg`
- State in the Videos.md record what was missed and how it was recovered.

---

## Writing to docs/wiki (wiki-schema integration)

Follow `.claude/skills/wiki-schema/SKILL.md`. Every page starts with:

```markdown
**Özet:** [Max 3 sentences]
**Kütüphaneler/Teknolojiler:** [Key technologies/concepts]
**Bağlantılar:** [[Related_Topic]], [[Another_Topic]]
**Kaynak Video:** [[Videos#VIDEO_ID]] — Short title (VIDEO_ID)
```

- PascalCase English file names (`MarketStructure.md`, `SmartMoneyConcepts.md`).
- Pages are **concept pages, not lesson summaries**. If a concept page already exists, update it (and append the new video to its `Kaynak Video` line) instead of creating a duplicate. The main text always states the *current* knowledge — rewrite it when a lesson refines or corrects it, and add one line to `## Tanımın Gelişimi` at the bottom (format: wiki-schema §6). Lesson-only material (end-of-lesson slide, homework) goes into the Videos.md record / LearningLog, not into the concept page.
- Describe diagrams/charts in text (labels, arrows, annotations, what the example shows).
- Tag sponsor segments: `> [!sponsor] Name`.

### Extra sections for trading / strategy videos

Because this wiki feeds a later analysis/trading system, trading pages also include:

- **"Bot / Uygulama İçin Çıkarılabilir Kurallar"** — short pseudo-code view of the topic's rules, each line pointing to its Playbook ID (→ SD-003). The Playbook is the authoritative wording.
- **"Açık sorular"** — list the Playbook question IDs relevant to this topic (Q-002, Q-011) with one line each; the full table lives in the Playbook.
- New terms go into `[[TradingTerminology]]`.
- Series videos: update the series tracker page (e.g. `[[PriceActionCourseRoadmap]]`) — mark the lesson done, add announced upcoming topics.

---

## Playbook

`docs/wiki/Playbook.md` is the single, authoritative list of **codeable trading rules** learned so far. Topic pages explain; the Playbook decides. A later analysis/backtest system will read only this file. Format and ID scheme are documented at the top of the Playbook itself; a worked example is in `docs/playbook_ornek.md`.

For every video:
0. **Acceptance filter:** a statement gets a rule ID only if a program needs it to **compute something or make a decision**: definitions (how to detect a swing, trend, zone, imbalance…), filters (news window, timeframe alignment), entry/stop/target and risk rules. Anecdotes, psychology, general market commentary and personal tips stay as notes on the concept page. Before opening a new ID, check whether it is really a refinement of an existing rule — if so, update that rule.
1. **Rules:** add each rule the video teaches as `### <PREFIX>-<NNN>: <title>` with Kural / Parametreler / Kaynak (video + mm:ss range) / Güven / Durum / İlgili. Update existing rules instead of duplicating them (append the new source).
2. **Measurable or nothing:** a rule must be codeable without guessing ("gövde kapanışı önceki swing high üzerinde", not "güçlü kırılım"). If the instructor gives no number/threshold, **do not invent one** — leave the parameter as `?` and open a question.
3. **Güven:** `açık kural` only if the instructor explicitly states/shows it (cite the minute). Your own formalisation of a looser explanation is `türetilmiş`.
4. **Open questions:** close those this video answers (status `cevaplandı` or `kısmen cevaplandı`, video ID, the answer with minute). Add new ones with the next free `Q-NNN`. If the instructor says a topic will be covered later ("ilerideki derslerde anlatacağım"), add it with status `beklenen` and write the promised topic in *Cevap*.
5. **Contradictions:** if this video conflicts with an existing rule, do **not** silently overwrite — add a row to *Çelişkiler*, mark the rule `çelişkili`, and ask the user which applies. Course series build on themselves (early lessons simplify, later ones refine), so your recommendation should normally be the **later, topic-specific lesson by the same instructor**, but the user still decides. While waiting, the *Karar* cell starts with `⏳`; once decided it starts with `✅` (playbook-check counts a row as open when the cell is empty, starts with `⏳` or says "bekleniyor"). Once the user decides, fill the *Karar* cell, set the rule back to its new definition (Güven no longer `çelişkili`), and fix every older topic page, terminology entry and pseudo-code block that still uses the overruled definition (`grep` the wiki for the term).
6. In topic pages, the "Bot / Uygulama İçin Çıkarılabilir Kurallar" section should reference Playbook IDs (e.g. "→ MS-004") rather than restating rules differently.
7. Never edit the *Bilgi Durumu* block by hand — `playbook-check --write` regenerates it.

---

## Before the lesson

Learning is active: know what you are looking for before you read the transcript.

1. `playbook-check` (or `.venv/Scripts/playbook-check.exe` on Windows) — current knowledge state and any format errors left from earlier lessons (fix those first).
2. In Playbook → *Açık Sorular*, list the questions with status `açık`, `beklenen` or `kısmen cevaplandı` whose topic matches this lesson's title/announced topic. `beklenen` rows naming this lesson's topic are the most likely to be answered.
3. Read the Playbook rules and concept pages for that topic, so new statements can be classified as **new / refinement / contradiction** instead of being added as duplicates.
4. Optional context: `playbook-check --last-log` prints only the previous lesson's LearningLog entry (what was left open). Never read the whole LearningLog.
5. Note the list of target questions — it goes into the LearningLog entry as *Ders öncesi aranan*, and the Quality Report says which of them were answered.

## Change propagation

When a rule's meaning changes (refined, narrowed, overruled, cancelled):

1. Search the wiki for the rule ID and for the term itself (e.g. `grep -rn "MS-004\|MSB" docs/wiki`).
2. Check each rule listed in its *İlgili* field — does it still hold with the new definition? Update it (or open a question / contradiction).
3. Fix every concept page text, terminology entry and pseudo-code block that still uses the old meaning; add one line to that page's *Tanımın Gelişimi*.
4. List the touched rules and pages in the LearningLog entry (*İnceltilen / düzeltilen*).

---

## Quality Report

Finish every processed video with this block (Turkish, concise). It is what the user reviews instead of reading every page:

```
📋 Kalite Raporu: <video başlığı>
- Transcript: whisper | vtt · YouTube'dan doldurulan bölüm: N · kaçmış olabilecek görsel: yok / <dk + açıklama>
- Ders öncesi aranan sorular: Q-020, Q-021 → cevaplanan: Q-020 · cevapsız kalan: Q-021
- Yeni kurallar: SD-004 (açık kural), IMB-002 (türetilmiş) …
- Güncellenen kurallar: MS-003 (kırılım tipi netleşti) …
- Kapanan sorular: Q-002 → "gövde kapanışı gerekir" (12:40) …
- Yeni açık sorular: Q-011 (base en az kaç mum?) …
- Çelişkiler: yok / <kısa açıklama — kullanıcı kararı bekleniyor>
- Hâlâ belirsiz ifadeler: "hacimli mum" (ölçü yok) …
- Sözlüğe eklenen altyazı hataları: N
- Bilgi durumu: aktif kural X (koda hazır Y) · açık soru Z · beklenen W · bekleyen çelişki V  (playbook-check: hata 0)
```

The same content (in the LearningLog format) is appended to `docs/wiki/LearningLog.md`, so the report survives the chat.

---

## Recording the video in docs/wiki/Videos.md

**Always** append:

```markdown
### [Video Başlığı](https://www.youtube.com/watch?v=VIDEO_ID) {#VIDEO_ID}
- **ID:** `VIDEO_ID`
- **Kanal / Seri:** Channel — Series (playlist ID, video N)   ← if applicable
- **Analiz tarihi:** YYYY-MM-DD
- **Süre:** ~X dakika (Ns)
- **Transcript:** vtt / srt / whisper / synthetic (+ quality notes)
- **Kare sayısı:** N kare, M storyboard sayfası (+ anything missed / recovered)
- **Oluşturulan wiki sayfaları:** [[Sayfa1]] (yeni), [[Sayfa2]] (güncellendi)
- **Özet:** One-sentence summary
```

This is the single source of truth for "which videos have been analyzed." Always check it before re-analyzing.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ffmpeg not found` | Windows: `winget install Gyan.FFmpeg`, or unzip the ffmpeg "essentials" build anywhere under `./tools/` (found automatically); macOS: `brew install ffmpeg` |
| `playbook-check` not found | `pip install -e .` again (the command was added in a later version) |
| `UnicodeEncodeError` in console | `export PYTHONIOENCODING=utf-8` |
| `HTTP Error 429` for `en` subtitles | Harmless if the original-language (`*-orig`) subtitle still downloaded |
| yt-dlp "No supported JavaScript runtime" warning | Harmless for now; if downloads start failing, install `deno` |
| `No module named spacy` | `pip install spacy && python -m spacy download en_core_web_sm` |
| `Sign in to confirm you're not a bot` | YouTube temporarily blocked this IP (many downloads). Wait a few hours, or put a Netscape `cookies.txt` (exported with the "Get cookies.txt LOCALLY" browser extension while logged in to youtube.com) in the project root — it is picked up automatically (`--cookies FILE` / `--cookies-from-browser firefox` also work). Never commit or share the cookie file (`cookies*.txt` is gitignored). |
| `Cannot access video` | Private, age-restricted or region-blocked |
| No transcript found | Pass `--groq-api-key` or set `GROQ_API_KEY` |
| Whisper: audio over 25 MB | Should not happen (audio is sent in 10-min chunks of ~2.4 MB). If it does, run without `--whisper` and report it |
| Module import error | `pip install -e .` from project root with venv active |
