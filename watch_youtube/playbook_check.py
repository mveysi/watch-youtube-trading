"""Playbook denetleyici ve bilgi durumu panosu.

Kullanım (proje kökünden):
    playbook-check                 # denetle + bilgi durumunu yazdır
    playbook-check --write         # ayrıca Playbook.md içindeki "Bilgi Durumu" panosunu güncelle
    playbook-check --last-log      # sadece LearningLog.md'nin son kaydını yazdır

Hata varsa çıkış kodu 1'dir. Uyarılar çıkış kodunu etkilemez.
"""

from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import click

CATEGORIES = ["PA", "RISK", "MS", "SMC", "SD", "IMB", "LIQ", "OB", "ENT"]
RULE_ID = r"(?:%s)-\d{3}" % "|".join(CATEGORIES)
RULE_ID_RE = re.compile(r"\b(%s)\b" % RULE_ID)
Q_ID_RE = re.compile(r"\bQ-\d{3}\b")
RULE_HEAD_RE = re.compile(r"^### (%s):\s*(.+?)\s*$" % RULE_ID)
FIELD_RE = re.compile(r"^- \*\*(.+?):\*\*\s*(.*)$")
WIKILINK_RE = re.compile(r"\[\[([^\]|#]*)(?:#([^\]|]*))?(?:\|[^\]]*)?\]\]")
ANCHOR_RE = re.compile(r"\{#([A-Za-z0-9_-]+)\}")
LOG_ENTRY_RE = re.compile(r"^## .*\(([A-Za-z0-9_-]{11})\)\s*$", re.M)

REQUIRED_FIELDS = ["Kural", "Parametreler", "Kaynak", "Güven", "Durum"]
GUVEN_VALUES = ("açık kural", "türetilmiş", "çelişkili")
DURUM_VALUES = ("aktif", "iptal")
Q_STATUSES = ("açık", "beklenen", "kısmen cevaplandı", "cevaplandı", "iptal")

DASH_BEGIN = "<!-- BILGI-DURUMU:BASLA -->"
DASH_END = "<!-- BILGI-DURUMU:BITIR -->"


@dataclass
class Rule:
    id: str
    title: str
    line: int
    fields: dict[str, str] = field(default_factory=dict)

    @property
    def category(self) -> str:
        return self.id.split("-")[0]

    @property
    def guven(self) -> str:
        return self.fields.get("Güven", "").strip().lower()

    @property
    def active(self) -> bool:
        return self.fields.get("Durum", "").strip().lower().startswith("aktif")

    @property
    def open_params(self) -> bool:
        return "?" in self.fields.get("Parametreler", "")

    @property
    def ready(self) -> bool:
        return self.active and not self.open_params and not self.guven.startswith("çelişkili")


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def err(self, msg: str) -> None:
        if msg not in self.errors:
            self.errors.append(msg)

    def warn(self, msg: str) -> None:
        if msg not in self.warnings:
            self.warnings.append(msg)


def _strip_code(text: str) -> str:
    """Remove fenced and inline code so format examples are not checked."""
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return re.sub(r"`[^`\n]*`", "", text)


def _section(text: str, heading: str) -> str:
    """Return the body of a level-2 section (until the next level-2 heading)."""
    m = re.search(r"^## %s\s*$" % re.escape(heading), text, re.M)
    if not m:
        return ""
    rest = text[m.end():]
    nxt = re.search(r"^## (?!(%s):)" % "|".join(CATEGORIES), rest, re.M)
    return rest[: nxt.start()] if nxt else rest


def parse_rules(playbook: str, rep: Report) -> list[Rule]:
    rules: list[Rule] = []
    start = playbook.find("\n## Kurallar")
    end = playbook.find("\n## Açık Sorular")
    if start < 0:
        rep.err("Playbook.md: '## Kurallar' bölümü bulunamadı")
        return rules
    offset = playbook[:start].count("\n") + 1
    body = playbook[start: end if end > 0 else None]
    current: Rule | None = None
    last_field: str | None = None
    for i, line in enumerate(body.splitlines()):
        head = RULE_HEAD_RE.match(line)
        if head:
            current = Rule(head.group(1), head.group(2), offset + i)
            rules.append(current)
            last_field = None
            continue
        if line.startswith("## ") or (line.startswith("### ") and not head):
            if line.startswith("### "):
                rep.err(f"Playbook.md:{offset + i}: kural başlığı biçimi hatalı → '{line.strip()}' "
                        f"(beklenen: '### MS-001: başlık')")
            current = None
            continue
        if current is None:
            continue
        f = FIELD_RE.match(line)
        if f:
            last_field = f.group(1).strip()
            current.fields[last_field] = f.group(2)
        elif last_field and line.startswith("  "):  # wrapped / nested line of the last field
            current.fields[last_field] += " " + line.strip()
    return rules


def parse_questions(playbook: str, rep: Report) -> dict[str, str]:
    """Return {Q-ID: status}."""
    questions: dict[str, str] = {}
    for line in _section(playbook, "Açık Sorular").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3 or not re.fullmatch(r"Q-\d{3}", cells[0]):
            continue
        qid, status = cells[0], cells[2].lower()
        if qid in questions:
            rep.err(f"Playbook.md: soru {qid} iki kez tanımlı")
        if not status.startswith(Q_STATUSES):
            rep.err(f"Playbook.md: {qid} durumu geçersiz '{cells[2]}' (geçerli: {', '.join(Q_STATUSES)})")
        questions[qid] = status
    return questions


def parse_contradictions(playbook: str) -> list[str]:
    """Return the 'Karar' cell of each contradiction row."""
    decisions = []
    for line in _section(playbook, "Çelişkiler").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 4 and cells[0] not in ("Konu", "") and not set(cells[0]) <= {"-"}:
            decisions.append(cells[-1])
    return decisions


def _q_status_key(status: str) -> str:
    for s in ("kısmen cevaplandı", "cevaplandı", "beklenen", "iptal", "açık"):
        if status.startswith(s):
            return s
    return "?"


def check_wiki(wiki: Path) -> tuple[Report, dict]:
    rep = Report()
    pb_path = wiki / "Playbook.md"
    if not pb_path.exists():
        rep.err(f"{pb_path} yok (docs/wiki_template/ içinden kopyala)")
        return rep, {}
    playbook = pb_path.read_text(encoding="utf-8")
    pages = {p.stem: p.read_text(encoding="utf-8") for p in sorted(wiki.glob("*.md"))}
    videos_text = pages.get("Videos", "")
    video_ids = set(ANCHOR_RE.findall(videos_text))
    if not videos_text:
        rep.err("Videos.md bulunamadı")

    rules = parse_rules(playbook, rep)
    questions = parse_questions(playbook, rep)
    decisions = parse_contradictions(playbook)
    rule_ids = {r.id for r in rules}

    # --- rule checks ---
    for rid, n in Counter(r.id for r in rules).items():
        if n > 1:
            rep.err(f"Playbook.md: kural {rid} {n} kez tanımlı")
    for r in rules:
        where = f"Playbook.md:{r.line} {r.id}"
        for fname in REQUIRED_FIELDS:
            if not r.fields.get(fname, "").strip():
                rep.err(f"{where}: '{fname}' alanı eksik/boş")
        if r.guven and not r.guven.startswith(GUVEN_VALUES):
            rep.err(f"{where}: Güven geçersiz '{r.fields['Güven']}' (geçerli: {', '.join(GUVEN_VALUES)})")
        durum = r.fields.get("Durum", "").strip().lower()
        if durum and not durum.startswith(DURUM_VALUES):
            rep.err(f"{where}: Durum geçersiz '{r.fields['Durum']}' (geçerli: aktif | iptal (neden))")
        kaynak = r.fields.get("Kaynak", "")
        cited = re.findall(r"\[\[Videos#([A-Za-z0-9_-]+)\]\]", kaynak)
        if kaynak and not cited:
            rep.err(f"{where}: Kaynak'ta [[Videos#VIDEO_ID]] yok")
        if kaynak and cited and not re.search(r"\d{1,2}:\d{2}", kaynak):
            rep.warn(f"{where}: Kaynak'ta dakika (dk:sn) yok")
        if r.open_params and not Q_ID_RE.search(r.fields.get("Parametreler", "")):
            rep.warn(f"{where}: '?' parametre var ama bağlı soru (Q-NNN) yok")

    # --- references across the Playbook and all pages ---
    for name, text in pages.items():
        body = _strip_code(text)
        for rid in sorted(set(RULE_ID_RE.findall(body)) - rule_ids):
            (rep.err if name == "Playbook" else rep.warn)(
                f"{name}.md: tanımsız kural kimliğine atıf {rid}")
        for qid in sorted(set(Q_ID_RE.findall(body)) - set(questions)):
            (rep.err if name == "Playbook" else rep.warn)(
                f"{name}.md: Açık Sorular tablosunda olmayan soru {qid}")
        for target, anchor in WIKILINK_RE.findall(body):
            target = target.strip()
            if target == "Videos" and anchor and anchor not in video_ids:
                rep.err(f"{name}.md: kırık video linki [[Videos#{anchor}]]")
            elif target and target not in pages:
                rep.warn(f"{name}.md: [[{target}]] sayfası henüz yok (planlanmış olabilir)")

    # --- contradictions ---
    pending = [d for d in decisions if not d.startswith("✅")]
    conflicted = [r.id for r in rules if r.guven.startswith("çelişkili")]
    if conflicted and not pending:
        rep.warn(f"Güveni 'çelişkili' olan kural var ({', '.join(conflicted)}) ama Çelişkiler'de bekleyen satır yok")
    if pending and not conflicted:
        rep.warn("Çelişkiler'de karar bekleyen satır var ama hiçbir kural 'çelişkili' işaretli değil")

    # --- learning log coverage ---
    log = pages.get("LearningLog")
    if log is None:
        rep.warn("LearningLog.md yok (docs/wiki_template/ içinden kopyala)")
    else:
        logged = set(LOG_ENTRY_RE.findall(_strip_code(log)))
        for vid in sorted(video_ids - logged):
            rep.warn(f"LearningLog.md: {vid} için öğrenme kaydı yok")

    stats = _stats(rules, questions, pending, len(video_ids))
    return rep, stats


def _stats(rules: list[Rule], questions: dict[str, str], pending: list[str], n_videos: int) -> dict:
    per_cat: dict[str, Counter] = defaultdict(Counter)
    for r in rules:
        c = per_cat[r.category]
        if not r.active:
            c["iptal"] += 1
            continue
        c["aktif"] += 1
        c["hazır"] += r.ready
        for g in GUVEN_VALUES:
            if r.guven.startswith(g):
                c[g] += 1
    q_counts = Counter(_q_status_key(s) for s in questions.values())
    not_ready = [
        (r.id, sorted(set(Q_ID_RE.findall(r.fields.get("Parametreler", "")))))
        for r in rules if r.active and not r.ready
    ]
    return {"per_cat": per_cat, "questions": q_counts, "pending": len(pending),
            "not_ready": not_ready, "videos": n_videos}


def render_dashboard(stats: dict) -> str:
    pc, q = stats["per_cat"], stats["questions"]
    rows = ["| Kategori | Aktif | Koda hazır | Açık kural | Türetilmiş | Çelişkili | İptal |",
            "|---|---|---|---|---|---|---|"]
    total: Counter = Counter()
    for cat in CATEGORIES:
        c = pc.get(cat)
        if not c:
            continue
        total.update(c)
        rows.append(f"| {cat} | {c['aktif']} | {c['hazır']} | {c['açık kural']} | {c['türetilmiş']} "
                    f"| {c['çelişkili']} | {c['iptal']} |")
    rows.append(f"| **Toplam** | **{total['aktif']}** | **{total['hazır']}** | {total['açık kural']} "
                f"| {total['türetilmiş']} | {total['çelişkili']} | {total['iptal']} |")
    nr = ", ".join(f"{rid} ({'/'.join(qs)})" if qs else rid for rid, qs in stats["not_ready"]) or "—"
    return "\n".join([
        "## Bilgi Durumu",
        "",
        f"_Otomatik üretilir (`playbook-check --write`), elle düzenlenmez · {date.today().isoformat()} · "
        f"işlenen video: {stats['videos']}_",
        "",
        *rows,
        "",
        f"**Sorular:** {q['açık']} açık · {q['beklenen']} beklenen (eğitmen ileride anlatacak) · "
        f"{q['kısmen cevaplandı']} kısmen · {q['cevaplandı']} cevaplandı · "
        f"**Bekleyen çelişki:** {stats['pending']}",
        "",
        f"**Koda hazır olmayan kurallar** (açık parametre / çelişki): {nr}",
    ])


def write_dashboard(pb_path: Path, dashboard: str) -> None:
    text = pb_path.read_text(encoding="utf-8")
    block = f"{DASH_BEGIN}\n{dashboard}\n{DASH_END}"
    if DASH_BEGIN in text and DASH_END in text:
        text = re.sub(re.escape(DASH_BEGIN) + r".*?" + re.escape(DASH_END),
                      lambda _: block, text, flags=re.S)
    else:  # insert before the first '---' separator after the header
        idx = text.find("\n---\n")
        text = (text[:idx] + "\n\n" + block + "\n" + text[idx:]) if idx >= 0 else block + "\n\n" + text
    pb_path.write_text(text, encoding="utf-8", newline="")


def last_log_entry(wiki: Path) -> str:
    log = wiki / "LearningLog.md"
    if not log.exists():
        return "(LearningLog.md yok)"
    text = log.read_text(encoding="utf-8")
    # blank out fenced code (keeping offsets) so the format example is not taken as an entry
    masked = re.sub(r"```.*?```", lambda m: " " * len(m.group()), text, flags=re.S)
    heads = [m.start() for m in re.finditer(r"^## ", masked, re.M)]
    return text[heads[-1]:].strip() if heads else "(henüz kayıt yok)"


@click.command()
@click.argument("wiki_dir", default="docs/wiki", type=click.Path(path_type=Path))
@click.option("--write", "do_write", is_flag=True, help="Playbook.md içindeki Bilgi Durumu panosunu güncelle.")
@click.option("--last-log", is_flag=True, help="Sadece LearningLog.md'nin son kaydını yazdır.")
def cli(wiki_dir: Path, do_write: bool, last_log: bool) -> None:
    """docs/wiki Playbook'unu denetler ve bilgi durumunu gösterir."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if last_log:
        click.echo(last_log_entry(wiki_dir))
        return
    rep, stats = check_wiki(wiki_dir)
    if stats:
        dashboard = render_dashboard(stats)
        click.echo(dashboard)
        if do_write:
            write_dashboard(wiki_dir / "Playbook.md", dashboard)
            click.echo("\n✔ Playbook.md → Bilgi Durumu güncellendi")
    click.echo(f"\nHatalar: {len(rep.errors)} · Uyarılar: {len(rep.warnings)}")
    for e in rep.errors:
        click.echo(f"  ✖ {e}")
    for w in rep.warnings:
        click.echo(f"  ⚠ {w}")
    sys.exit(1 if rep.errors else 0)


if __name__ == "__main__":
    cli()
