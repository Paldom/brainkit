"""Build and query a Git-native brain from researchkit projects.

A *brain* is a directory of frontmattered markdown notes — portable,
human-readable, diffable — arranged as a pyramid an agent can descend:

    brain/
    ├── index.md            # the map: domains and topics, nothing bulkier
    ├── log.md              # date-grouped ingest journal (OKF §9)
    └── notes/
        ├── index.md at every level below (OKF §8 progressive disclosure)
        ├── domains/<slug>.md    # L1: one boosted run, over its topics
        ├── topics/<slug>.md     # L2: one research run's own synthesis
        ├── reports/<slug>.md    # L3: one `##` section of a run's analysis
        ├── sources/<hash>-<slug>.md  # L4: one archived URL, deduplicated
        └── imported/<slug>.md   # frontmattered md via ingest_notes

The levels are not decoration: a boosted researchkit run already contains a
parent-over-children hierarchy, and ingest used to flatten it into sibling
notes. Notes link DOWN by ``[[slug]]`` and UP by a ``parent`` field, so an
answer can be traced from a map to a synthesis to a primary source.

Writes are *gated by provenance*: notes are created by ingesting a
researchkit project (``result.json`` + ``materials/``; a boosted run's
``subprojects/`` recurse) or, via :func:`ingest_notes`, arbitrary markdown
that carries provenance frontmatter (``url``/``project``/``title``) — never
anonymous free text. Every claim traces back to a research run or a source
URL. Re-ingesting identical input is inert down to the byte.

Retrieval is lexical: BM25 with per-level length normalization and a bounded
preference for higher levels, and every hit carries its citation.
Frontmatter values are JSON-encoded, which is valid YAML 1.2 and keeps the
bundle conformant with the Open Knowledge Format v0.2.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import os
import pathlib
import re
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from brainkit import Note, __version__, parse_note, raw_frontmatter, slugify

NOTES_DIRNAME = "notes"
DOMAINS_DIRNAME = "domains"
TOPICS_DIRNAME = "topics"
SOURCES_DIRNAME = "sources"
REPORTS_DIRNAME = "reports"
IMPORTED_DIRNAME = "imported"
SUBPROJECTS_DIRNAME = "subprojects"
INDEX_FILENAME = "index.md"
LOG_FILENAME = "log.md"
OKF_VERSION = "0.2"

# OKF §3.1: reserved at every level of the tree, never concept documents.
RESERVED_FILENAMES = frozenset({INDEX_FILENAME, LOG_FILENAME})

# The pyramid, high to low. An agent descends it; search ranks by it; the
# index groups by it. `note` (free-form import) sits with report: it is
# somebody's synthesis, just not one brainkit produced.
LEVELS: dict[str, int] = {
    "domain": 0,
    "topic": 1,
    "report": 2,
    "note": 2,
    "source": 3,
}
# Note kinds whose BODY brainkit or a human wrote, as opposed to archived
# third-party content. Only these carry wiki-link edges.
_AUTHORED_KINDS = frozenset({"domain", "topic", "note"})
_LEVEL_DIRNAME = {
    "domain": DOMAINS_DIRNAME,
    "topic": TOPICS_DIRNAME,
    "report": REPORTS_DIRNAME,
    "note": IMPORTED_DIRNAME,
    "source": SOURCES_DIRNAME,
}

# Report headings that begin the raw-archive half of a researchkit report.
# Chunking stops at the first one: everything below is per-provider output
# already captured as source notes, and it outnumbers the analysis ~4:1.
_REPORT_STOP = frozenset(
    {
        "keyword-based-site-research",
        "provider-summaries",
        "raw-provider-outputs",
        "analytics",
    }
)

_TOKEN = re.compile(r"[a-z0-9]+")
# [[slug]], [[slug|label]] and [[slug#heading]] all target `slug`.
_WIKILINK = re.compile(r"\[\[([^\]|#]+)")
_TITLE_WEIGHT = 3
_SNIPPET_CHARS = 240
_DESC_CHARS = 160
_TITLE_CHARS = 90
# BM25's standard defaults: k1 saturates term frequency, b controls how hard
# length normalization bites. Untuned on purpose — there is no eval set yet,
# and inventing constants without one is how ranking becomes taste.
_BM25_K1 = 1.2
_BM25_B = 0.75
# The single hierarchy knob: how much a domain note may outrank a source note
# on identical relevance. Spread geometrically over the levels by
# :func:`_level_prior`.
_LEVEL_PRIOR_CEILING = 2.0
# Characters YAML 1.2 §5.1 excludes from its printable set that `json.dumps`
# leaves literal: DEL, the C1 block minus U+0085 (NEL, which IS printable), the
# two non-characters, and lone surrogates — which additionally cannot be
# encoded as UTF-8 at all, so writing one would abort the run.
_YAML_FORBIDDEN = re.compile(r"[\x7f-\x84\x86-\x9f\ud800-\udfff\ufffe\uffff]")
# The generation stamp in an index header, ignored when deciding whether the
# index actually changed.
_STAMP = re.compile(r" · generated \S+")
# A frontmatter key safe to write unquoted.
_PLAIN_KEY = re.compile(r"[A-Za-z_][A-Za-z0-9_-]*")


@dataclass(frozen=True)
class IngestReport:
    """What one ingest run wrote into the brain."""

    topic: str
    topic_note: Path
    source_notes: list[Path]
    skipped_sources: int
    pruned_sources: int = 0
    # Per-file skip reasons ("materials/003-x.md: no 'url' in frontmatter") —
    # len(skip_reasons) == skipped_sources.
    skip_reasons: list[str] = field(default_factory=list)
    # Materials that were not valid UTF-8 and were read with replacement
    # characters. Reported, never silent — a repaired body is still evidence,
    # but a reader deserves to know it was repaired.
    repaired_sources: list[str] = field(default_factory=list)
    # Report-body notes written when include_reports=True.
    report_notes: list[Path] = field(default_factory=list)
    # One report per ingested subprojects/* child (boosted researchkit runs).
    sub_reports: list[IngestReport] = field(default_factory=list)


@dataclass(frozen=True)
class SearchHit:
    """One retrieval result with its provenance.

    Source notes carry a ``url``; topic notes carry the ``project`` (the
    research run) instead — every hit is citable one way or the other.
    """

    path: Path
    title: str
    score: float
    url: str
    snippet: str
    project: str = ""
    # The content's `published` date from the source material, "" when
    # unknown — deliberately NOT the ingest time, so a displayed date always
    # means the same thing the ranking used.
    published: str = ""
    # Trust tier from the source material ("social" vs "web"), "" when unknown
    # — user-generated content is the classic poisoning vector, so surface it.
    source_type: str = ""
    # Where this hit sits in the pyramid, and the note one level up. Lets a
    # caller show the descent path instead of a bare score.
    kind: str = ""
    parent: str = ""


MetaValue = "str | int | list[str] | dict[str, str]"
Meta = Mapping[str, "str | int | list[str] | dict[str, str]"]


def _yaml_value(value: str | int | list[str] | dict[str, str]) -> str:
    """One frontmatter value, encoded as JSON.

    JSON is a subset of YAML 1.2, so a JSON-encoded value is *always* a valid,
    unambiguous YAML value — no indicator-character list to get right, no
    escaping to hand-roll, and (the reason it beats quoting only when
    necessary) no implicit-type surprises. Left plain, a title of ``007``
    loads as the integer 7, ``12:00:00`` as 43200, ``2026-01-01`` as a date,
    and ``.inf`` as a float; which of those fire also differs between YAML 1.1
    and 1.2 consumers, so "quote only when needed" is a compatibility matrix
    rather than a rule. Strings are quoted unconditionally instead.

    Structure is preserved rather than stringified: ``tags`` stays a list and
    ``generated`` stays a mapping, which is what OKF §4.1/§5.2 consumers read.
    Strings have their whitespace collapsed first — a frontmatter field is a
    single-line value, and a newline in a scraped title is noise.
    """
    if isinstance(value, str):
        value = " ".join(value.split())
    elif isinstance(value, list):
        value = [" ".join(item.split()) for item in value]
    elif isinstance(value, dict):
        value = {k: " ".join(v.split()) for k, v in value.items()}
    encoded = json.dumps(value, ensure_ascii=False, allow_nan=False)
    # json escapes C0 controls but emits DEL and the C1 block (U+0080-U+009F)
    # literally, and YAML's printable set (1.2 §5.1) excludes both — mojibake
    # from a mis-decoded scraped page is enough to make a note unparseable.
    # Escaping rather than stripping keeps the round trip lossless.
    return _YAML_FORBIDDEN.sub(lambda m: f"\\u{ord(m.group()):04x}", encoded)


def _frontmatter(pairs: Meta) -> str:
    """Render a frontmatter block as one JSON-encoded value per line.

    Line-oriented so the reader stays a partition on the first colon, and so
    every field is greppable.
    """
    lines = ["---"]
    for key, value in pairs.items():
        # Keys are encoded too. brainkit's own are plain identifiers, but
        # `rebuild` copies keys straight off an existing note, and a
        # hand-written `weird: key` would otherwise emit a second colon and
        # make the block unparseable.
        name = key if _PLAIN_KEY.fullmatch(key) else _yaml_value(key)
        lines.append(f"{name}: {_yaml_value(value)}")
    lines.append("---")
    return "\n".join(lines)


def _write_note(path: Path, meta: Meta, body: str) -> None:
    """Write a note, leaving it untouched when nothing about it changed.

    ``generated.at`` moves on every ingest, so a naive write makes
    re-ingesting identical input produce a diff on every note — the brain's
    git history fills with commits that say only "ingested again", and
    "idempotent ingestion" stops meaning anything a reviewer can see.

    So: re-stamp the candidate with the note's EXISTING timestamp and compare.
    Identical means the content did not change, and the file is left exactly
    as it was — timestamp included, since it still records when this content
    was actually produced.
    """
    body = body.rstrip("\n")
    if path.is_file():
        previous = path.read_text(encoding="utf-8")
        stamped = dict(meta)
        raw = parse_note(previous).meta.get("generated", "")
        try:
            decoded = json.loads(raw)
        except ValueError:
            decoded = None
        if isinstance(decoded, dict):
            stamped["generated"] = decoded
            if f"{_frontmatter(stamped)}\n\n{body}\n" == previous:
                return
    path.write_text(f"{_frontmatter(meta)}\n\n{body}\n", encoding="utf-8")


def _generated() -> dict[str, str]:
    """OKF §5.2 ``generated``: who wrote this note, and when.

    Supersedes a bare ``ingested_at`` timestamp (§13.1) and finally records
    the actor — ``<producer>/<version>`` per the §7 convention.
    """
    return {"by": f"brainkit/{__version__}", "at": _now()}


def _tags(result: Mapping[str, object]) -> list[str]:
    """Research keywords as OKF §4.1 ``tags`` — cross-cutting, free, no LLM.

    researchkit already synthesizes these per run; brainkit was discarding
    them. Deduplicated case-insensitively, order preserved.
    """
    seen: dict[str, str] = {}
    for key in ("synthesized_keywords", "keywords"):
        value = result.get(key)
        if not isinstance(value, list):
            continue
        for item in value:
            text = " ".join(str(item).split())
            if text:
                seen.setdefault(text.lower(), text)
    return list(seen.values())


def _now() -> str:
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds")


_LOG_TITLE = "# Brain log"
_LOG_DATE_RE = re.compile(r"^## (\d{4}-\d{2}-\d{2})$", re.MULTILINE)


def _append_log(brain_dir: Path, kind: str, event: str) -> None:
    """Record one entry in the brain's ``log.md`` (OKF §9, reserved filename).

    Date-grouped, newest first: ``## YYYY-MM-DD`` headings with
    ``* **Kind**: text`` entries under them. A git-diffable ingest journal
    where a day's work reads as one block — the previous flat
    one-line-per-timestamp form buried the shape of a session in noise.

    Newest-first means this is a read-modify-write rather than an append; a
    log is small and rewriting it whole keeps the ordering invariant honest.
    """
    log_path = brain_dir / "log.md"
    today = _now()[:10]
    entry = f"* **{kind}**: {event}"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    text = log_path.read_text(encoding="utf-8") if log_path.is_file() else ""
    if not text.startswith(_LOG_TITLE):
        text = f"{_LOG_TITLE}\n"
    match = _LOG_DATE_RE.search(text)
    if match and match.group(1) == today:
        # today's section already open — newest entry goes at its top
        cut = match.end() + 1
        body = f"{text[:cut]}\n{entry}\n{text[cut:].lstrip(chr(10))}"
    else:
        head, _, rest = text.partition("\n")
        body = f"{head}\n\n## {today}\n\n{entry}\n\n{rest.strip(chr(10))}\n"
    log_path.write_text(body.rstrip("\n") + "\n", encoding="utf-8")


def _read_json(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} does not contain a JSON object")
    return data


def _source_slug(url: str, stem: str) -> str:
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:8]
    # Strip researchkit's positional prefix (001-...) so the same URL cited
    # by two different runs lands on the same note.
    bare = re.sub(r"^\d{3}-", "", stem)
    return f"{digest}-{slugify(bare)[:60] or 'source'}"


def _source_note_path(sources_dir: Path, url: str, stem: str) -> Path:
    """Stable per-URL note path.

    The readable stem comes from the citation title, which can drift between
    runs — the URL is the identity. An existing note with this URL's digest
    prefix is reused (verified against its frontmatter ``url``; a true 8-hex
    digest collision falls back to the full digest as the filename).
    """
    slug = _source_slug(url, stem)
    digest = slug.split("-", 1)[0]
    for candidate in sorted(sources_dir.glob(f"{digest}-*.md")):
        existing = parse_note(candidate.read_text(encoding="utf-8"))
        if existing.meta.get("url", "") == url:
            return candidate
        # digest prefix collision with a different URL
        full = hashlib.sha1(url.encode("utf-8")).hexdigest()
        return sources_dir / f"{full}.md"
    return sources_dir / f"{slug}.md"


def _read_list(raw: str) -> list[str]:
    """Read a multi-valued frontmatter field.

    Stored as a JSON list. It used to be a comma-joined string, which silently
    corrupted every research topic containing a comma — and a researchkit
    topic is a sentence, so most of them do: the value could not be split back
    into the items that went in, so re-ingesting appended the whole topic
    again, and ``topics`` grew without bound on every run. Legacy
    comma-joined values are still read, best-effort, so old brains keep
    working.
    """
    try:
        decoded = json.loads(raw)
    except ValueError:
        decoded = None
    if isinstance(decoded, list):
        return [str(item) for item in decoded]
    return [item.strip() for item in raw.split(",") if item.strip()]


def _corroboration(projects: list[str]) -> int:
    """Citing-run count derived from the ``projects`` list — ONE derivation
    shared by the write and prune paths so the stored field can't drift."""
    return len(projects)


def _merge_all(existing: str, incoming: str) -> list[str]:
    """Union two multi-valued fields, preserving first-seen order."""
    merged = _read_list(existing)
    for item in _read_list(incoming):
        if item not in merged:
            merged.append(item)
    return merged


def _merge_topics(existing: str, topic: str) -> list[str]:
    """Add ``topic`` to a stored list, preserving order, without duplicating."""
    topics = _read_list(existing)
    if topic and topic not in topics:
        topics.append(topic)
    return topics


def _material_files(materials_dir: Path) -> list[Path]:
    """Material files to ingest, manifest-first.

    When researchkit's ``index.json`` manifest is present, only files it
    currently lists as ``fetched`` are ingested — stale files left behind by
    earlier runs (changed citation sets, renamed titles) are ignored. A
    directory without a manifest falls back to every ``*.md``.
    """
    if not materials_dir.is_dir():
        return []
    manifest_path = materials_dir / "index.json"
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            entries = manifest["entries"]
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            # Fail closed: a researchkit-managed dir with a corrupt manifest
            # must not silently ingest whatever files happen to lie around.
            raise ValueError(
                f"{manifest_path} is not a valid materials manifest: {e}"
            ) from e
        if not isinstance(entries, list):
            raise ValueError(f"{manifest_path}: 'entries' is not a list")
        files: list[Path] = []
        for i, entry in enumerate(entries):
            if not isinstance(entry, dict):
                raise ValueError(f"{manifest_path}: entry {i} is not an object")
            if entry.get("status") != "fetched":
                continue
            file_value = entry.get("file")
            if not isinstance(file_value, str) or not file_value:
                raise ValueError(
                    f"{manifest_path}: fetched entry {i} has no valid 'file'"
                )
            # basename only (both separator styles) — manifest entries must
            # not escape materials/
            name = pathlib.PurePosixPath(file_value.replace("\\", "/")).name
            candidate = materials_dir / name
            if not candidate.is_file():
                # Fail closed BEFORE any brain writes: a listed-but-missing
                # material means the project dir is corrupt, and ingesting
                # a partial set would prune sources that are still cited.
                raise ValueError(
                    f"{manifest_path}: fetched file {name!r} is missing from "
                    "materials/ — re-run `researchkit materials` first"
                )
            files.append(candidate)
        return files
    return sorted(materials_dir.glob("*.md"))


def _read_material(path: Path) -> tuple[str, bool]:
    """Read one material file; report whether it needed repairing.

    A scraped page saved with a broken encoding is not a reason to lose a
    whole research run — and a strict read of one bad byte used to abort the
    entire ingest with an error that did not even name the file. Undecodable
    bytes are replaced rather than dropped, because a replacement character in
    a body still leaves the source citable, whereas skipping the file loses
    the citation entirely. The repair is reported, never silent.
    """
    raw = path.read_bytes()
    try:
        return raw.decode("utf-8"), False
    except UnicodeDecodeError:
        return raw.decode("utf-8", errors="replace"), True


def ingest_research_project(
    project_dir: Path,
    brain_dir: Path,
    *,
    include_reports: bool = True,
    _project_name: str | None = None,
    _parent: str = "",
) -> IngestReport:
    """Ingest one researchkit project into the brain.

    Requires the project to have been run (``result.json``); downloaded
    ``materials/`` become source notes, and the run's meta-summary becomes
    the topic note. A boosted run's ``subprojects/*`` are ingested
    recursively (each is a normal project). With ``include_reports=True``
    the report body's ``##`` sections also become notes, so a run with thin
    materials is still queryable. Re-ingesting is idempotent: notes are
    overwritten, and a source cited by several research runs accumulates
    every topic in its frontmatter instead of being duplicated.
    """
    result_path = (project_dir / "result.json").absolute()
    if not result_path.is_file():
        raise FileNotFoundError(
            f"result.json not found (looked for: {result_path}) — "
            "has this researchkit project been run? If it lives elsewhere, "
            "pass the project path as an absolute path."
        )
    result = _read_json(result_path)
    # A boosted parent's result.json carries "overarching_topic" and
    # "super_summary" instead of the flat-run keys.
    topic = (
        str(result.get("topic", ""))
        or str(result.get("overarching_topic", ""))
        or project_dir.name
    )
    # Sub-projects of different boosted runs share basenames (sub_01_<slug>),
    # so recursion qualifies them with the parent's (timestamped) name —
    # otherwise re-running a boosted topic would prune the previous run's
    # sub sources and overwrite its topic notes.
    project_name = _project_name or project_dir.name
    # Topic-note identity is per research RUN: two different projects on the
    # same topic string must not overwrite each other's provenance. The hash
    # suffix keeps identity exact even when slugs truncate or collide
    # ("foo bar" vs "foo-bar").
    run_digest = hashlib.sha1(f"{topic}\x00{project_name}".encode()).hexdigest()[:8]
    node_slug = (
        f"{slugify(topic)[:40] or 'topic'}--"
        f"{slugify(project_name)[:32] or 'run'}-{run_digest}"
    )

    topics_dir = brain_dir / NOTES_DIRNAME / TOPICS_DIRNAME
    sources_dir = brain_dir / NOTES_DIRNAME / SOURCES_DIRNAME
    topics_dir.mkdir(parents=True, exist_ok=True)
    sources_dir.mkdir(parents=True, exist_ok=True)

    source_notes: list[Path] = []
    # (note path, the title THIS run cited it under) — see _cite_list
    citations: list[tuple[Path, str]] = []
    repaired: list[str] = []
    skip_reasons: list[str] = []  # material skips first; sub-project skips appended
    materials_dir = project_dir / "materials"
    for material in _material_files(materials_dir):
        text, was_repaired = _read_material(material)
        if was_repaired:
            repaired.append(f"materials/{material.name}: not valid UTF-8")
        note = parse_note(text)
        url = note.meta.get("url", "")
        if not url or not note.body.strip():
            reason = "no 'url' in frontmatter" if not url else "empty body"
            skip_reasons.append(f"materials/{material.name}: {reason}")
            continue
        note_path = _source_note_path(sources_dir, url, material.stem)
        slug = note_path.stem
        topics_value = [topic]
        projects_value = [project_name]
        existing_meta: dict[str, str] = {}
        body = note.body.strip()
        # The same URL archived by two research runs is ONE note, but the two
        # archives are rarely identical — different scrape, different title,
        # sometimes a truncated fetch. Last-write-wins made the note's content
        # oscillate between them on every ingest. Keep the fuller archive
        # instead: deterministic, independent of ingest order, and it prefers
        # the more complete capture rather than the most recent accident.
        keep_incoming = True
        if note_path.is_file():
            existing = parse_note(note_path.read_text(encoding="utf-8"))
            existing_meta = dict(existing.meta)
            keep_incoming = len(body) > len(existing.body.strip())
            if not keep_incoming:
                body = existing.body.strip()
            topics_value = _merge_topics(existing.meta.get("topics", ""), topic)
            projects_value = _merge_topics(
                existing.meta.get("projects", ""), project_name
            )
        # Content fields follow the archive that won; provenance always merges.
        primary = note.meta if keep_incoming else existing_meta
        secondary = existing_meta if keep_incoming else note.meta
        meta: dict[str, str | int | list[str] | dict[str, str]] = {
            "title": primary.get("title") or secondary.get("title") or url,
            "slug": slug,
            "type": "source",
            "url": url,
            # OKF §4.1: `resource` is the spec's name for the canonical URI of
            # the asset a concept describes. `url` stays as brainkit's own
            # field so existing readers and every printed citation still work.
            "resource": url,
            "topics": topics_value,
            "projects": projects_value,
            # Union, not last-write-wins: the same URL archived by two
            # sub-projects usually carries a different provider set, and
            # overwriting made the field flip-flop on every ingest.
            "providers": _merge_all(
                existing_meta.get("providers", ""), note.meta.get("providers", "")
            ),
        }
        # OKF-queryable description (front-loaded index blurb) and a
        # DETERMINISTIC corroboration count — the number of research runs
        # citing this URL (OpenWiki ships confidence labels as prompt policy;
        # brainkit computes the tier from provenance it already tracks).
        desc = _description(body)
        if desc:
            meta["description"] = desc
        meta["corroboration"] = _corroboration(projects_value)
        # WHICH run supplied the body that won. Without it, a note merges the
        # citations of every run that fetched the URL onto ONE run's capture,
        # so pruning the run that contributed the content leaves the content
        # behind wearing the others' provenance. Recorded so the claim stays
        # honest and `lint` can notice when it stops being true.
        meta["content_from"] = (
            project_name if keep_incoming else existing_meta.get("content_from", "")
        ) or project_name
        # Research metadata passes through: where the content came from and
        # when it was published matters as much as the content itself. A field
        # the winning archive lacks falls back to the other one — never lose
        # provenance just because the fuller capture recorded less about it.
        for extra in (
            "source_type",
            "content_kind",
            "published",
            "final_url",
            "content_digest",
        ):
            value = primary.get(extra) or secondary.get(extra)
            if value:
                meta[extra] = value
        meta["generated"] = _generated()
        _write_note(note_path, meta, body)
        source_notes.append(note_path)
        # THIS material's title, not the merged note's: the note keeps the
        # fuller archive's title, which a sibling sub-project may have set.
        citations.append((note_path, note.meta.get("title") or url))

    summary = (
        str(result.get("meta_summary", "")).strip()
        or str(result.get("super_summary") or "").strip()
    )
    tags = _tags(result)
    pruned = _prune_project_sources(sources_dir, project_name, set(source_notes))

    report_notes: list[Path] = []
    if include_reports:
        report_notes = _ingest_report_sections(
            project_dir,
            brain_dir,
            topic=topic,
            project_name=project_name,
            tags=tags,
        )

    skipped_materials = len(skip_reasons)

    # Boosted runs: each subprojects/* child is a normal project — recurse so
    # the deepest research lands in the brain too. Un-run children are
    # reported, not fatal (one failed sub must not lose the others).
    sub_reports: list[IngestReport] = []
    subprojects_dir = project_dir / SUBPROJECTS_DIRNAME
    if subprojects_dir.is_dir():
        for child in sorted(p for p in subprojects_dir.iterdir() if p.is_dir()):
            if not (child / "result.json").is_file():
                skip_reasons.append(
                    f"{SUBPROJECTS_DIRNAME}/{child.name}: no result.json (not run)"
                )
                continue
            sub_reports.append(
                ingest_research_project(
                    child,
                    brain_dir,
                    include_reports=include_reports,
                    _project_name=f"{project_name}/{child.name}",
                    _parent=node_slug,
                )
            )

    # The node note is written LAST because its kind depends on what came
    # back: a run with ingested children is a DOMAIN (the level above topic),
    # and it can only list them once they exist. This is the hierarchy that
    # was already in the research data and used to be flattened away — a
    # boosted parent and its sub-projects were stored as unrelated siblings.
    topic_note = _write_node_note(
        brain_dir,
        topic=topic,
        slug=node_slug,
        project_name=project_name,
        summary=summary,
        tags=tags,
        source_notes=source_notes,
        citations=citations,
        children=[r.topic_note for r in sub_reports],
        reports=report_notes,
        parent=_parent,
    )

    build_index(brain_dir)
    _append_log(
        brain_dir,
        "Ingest",
        f"`{project_name}` — {len(source_notes)} sources, "
        f"{len(report_notes)} reports, {pruned} pruned, "
        f"{skipped_materials} skipped",
    )
    return IngestReport(
        topic=topic,
        topic_note=topic_note,
        source_notes=source_notes,
        skipped_sources=skipped_materials,
        pruned_sources=pruned,
        skip_reasons=skip_reasons,
        repaired_sources=repaired,
        report_notes=report_notes,
        sub_reports=sub_reports,
    )


def _link_list(paths: list[Path]) -> str:
    """A wiki-linked, described bullet list — the descent path one level down.

    Reads each target's own note, so it must only be used for targets already
    written and settled (a parent's children, never a run's shared sources).
    """
    lines = []
    for path in paths:
        note = parse_note(path.read_text(encoding="utf-8"))
        desc = note.meta.get("description", "")
        lines.append(
            f"- [[{path.stem}]] — {note.title}" + (f" — {desc}" if desc else "")
        )
    return "\n".join(lines)


def _cite_list(citations: list[tuple[Path, str]]) -> str:
    """This run's source list, titled as THIS run cited them.

    Deliberately not read back from the shared source notes. One URL archived
    by two sub-projects yields one note whose title is the fuller archive's,
    so a list built from the note would change under a sibling's feet and the
    topic note would never be byte-stable. A citation belongs to the run that
    made it.
    """
    return "\n".join(f"- [[{path.stem}]] — {title}" for path, title in citations)


def _write_node_note(
    brain_dir: Path,
    *,
    topic: str,
    slug: str,
    project_name: str,
    summary: str,
    tags: list[str],
    source_notes: list[Path],
    citations: list[tuple[Path, str]],
    children: list[Path],
    reports: list[Path],
    parent: str,
) -> Path:
    """Write one research run's note at the level its shape earns.

    A run with ingested sub-projects is a **domain** (L1) — the cross-run
    layer brainkit never had; a leaf run is a **topic** (L2). Both carry the
    run's own synthesis plus an explicit list of links one level down, so an
    agent can descend rather than search blind.

    The ``## Topics`` list is emitted even when the summary is junk. A boosted
    parent's ``super_summary`` is not always trustworthy — one real run has an
    unrelated tool message where its summary should be — so the note's value
    must not depend on it.
    """
    kind = "domain" if children else "topic"
    directory = brain_dir / NOTES_DIRNAME / _LEVEL_DIRNAME[kind]
    directory.mkdir(parents=True, exist_ok=True)

    meta: dict[str, str | int | list[str] | dict[str, str]] = {
        "title": topic,
        "slug": slug,
        "type": kind,
        "project": project_name,
    }
    if parent:
        meta["parent"] = parent
    if children:
        meta["topic_count"] = len(children)
    meta["source_count"] = len(source_notes)
    desc = _description(summary)
    if desc:
        meta["description"] = desc
    if tags:
        meta["tags"] = tags
    meta["generated"] = _generated()

    body_parts = [summary] if summary else []
    if children:
        body_parts += ["## Topics", _link_list(children)]
    if reports:
        # Without this the report sections are unreachable: nothing links to
        # them, so the pyramid has a rung an agent can only find by search.
        body_parts += ["## Report sections", _link_list(reports)]
    if source_notes or not children:
        body_parts += ["## Sources", _cite_list(citations) or "*(none downloaded)*"]

    path = directory / f"{slug}.md"
    _write_note(path, meta, "\n\n".join(body_parts))
    # A run that gains sub-projects between ingests changes level. Drop the
    # note it used to be, or the brain would hold the same run twice.
    other = (
        brain_dir / NOTES_DIRNAME / _LEVEL_DIRNAME["topic" if children else "domain"]
    )
    stale = other / f"{slug}.md"
    if stale.is_file():
        stale.unlink()
    return path


def _prune_project_sources(
    sources_dir: Path, project_name: str, current: set[Path]
) -> int:
    """Drop this project's attribution from notes it no longer cites.

    Re-ingesting a re-run project must reflect its CURRENT citation set: a
    source note this project previously contributed but no longer cites
    loses the project from ``projects:``; a note left with no projects at
    all is deleted (the brain mirrors research runs).
    """
    pruned = 0
    # project -> topic map from the brain's topic notes, for recomputing a
    # pruned note's display topics from its remaining project memberships.
    topics_dir = sources_dir.parent / TOPICS_DIRNAME
    topic_by_project: dict[str, str] = {}
    if topics_dir.is_dir():
        for topic_path in sorted(topics_dir.glob("*.md")):
            tnote = parse_note(topic_path.read_text(encoding="utf-8"))
            proj = tnote.meta.get("project", "")
            if proj:
                topic_by_project[proj] = tnote.title
    for note_path in sorted(sources_dir.glob("*.md")):
        if note_path in current:
            continue
        note = parse_note(note_path.read_text(encoding="utf-8"))
        projects = _read_list(note.meta.get("projects", ""))
        if project_name not in projects:
            continue
        projects.remove(project_name)
        if projects:
            meta: dict[str, str | int | list[str] | dict[str, str]] = dict(note.meta)
            meta["projects"] = projects
            meta["corroboration"] = _corroboration(projects)
            remaining_topics = [
                topic_by_project[proj] for proj in projects if proj in topic_by_project
            ]
            if remaining_topics:
                meta["topics"] = list(dict.fromkeys(remaining_topics))
            _write_note(note_path, meta, note.body.strip())
        else:
            note_path.unlink()
            pruned += 1
    return pruned


def _ingest_report_sections(
    project_dir: Path,
    brain_dir: Path,
    *,
    topic: str,
    project_name: str,
    tags: list[str] | None = None,
) -> list[Path]:
    """Chunk the project's ``report.md`` analysis into one note per ``##``.

    This is the layer where a research run's actual synthesis lives — the
    executive summary, the consensus and divergent findings, the takeaways —
    so it is ingested by default rather than hidden behind a flag.

    Chunking stops at the first raw-data heading (:data:`_REPORT_STOP`).
    A researchkit report is analysis first and archive second: past that
    boundary come per-provider dumps, keyword site-research spew and
    analytics tables, which are already captured as source notes and would
    otherwise outnumber the analysis notes four to one.
    """
    report_path = project_dir / "report.md"
    if not report_path.is_file():
        return []
    reports_dir = brain_dir / NOTES_DIRNAME / REPORTS_DIRNAME
    reports_dir.mkdir(parents=True, exist_ok=True)
    # Digest-suffixed prefix: slug truncation alone collides for boosted
    # sub-projects under a long parent name ("<parent>/sub_01_…" all truncate
    # to the same 48 chars), and a collision makes each sub's stale-prune
    # DELETE its siblings' report notes. Same identity trick as topic notes.
    name_digest = hashlib.sha1(project_name.encode("utf-8")).hexdigest()[:8]
    prefix = f"{slugify(project_name)[:40] or 'run'}-{name_digest}"

    text = report_path.read_text(encoding="utf-8")
    # "## heading" lines split sections — but only OUTSIDE ``` fences (reports
    # embed markdown examples); anything before the first heading is the
    # overview.
    sections: list[list[str]] = [[]]
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        if not in_fence and line.startswith("## "):
            if slugify(line.removeprefix("## ")) in _REPORT_STOP:
                break  # analysis ends here; the rest is raw archive
            sections.append([line])
        else:
            sections[-1].append(line)
    written: list[Path] = []
    used_slugs: set[str] = set()
    for lines in sections:
        if lines and lines[0].startswith("## "):
            heading = lines[0].removeprefix("## ").strip()
            body = "\n".join(lines[1:])
        else:
            heading, body = "Overview", "\n".join(lines)
        if len(body.strip()) < 40:  # ponytail: skip stub sections, no smarter filter
            continue
        # Repeated headings ("## Key findings" per provider block) get -2, -3…
        slug = base = f"{prefix}--{slugify(heading)[:48] or 'section'}"
        n = 2
        while slug in used_slugs:
            slug = f"{base}-{n}"
            n += 1
        used_slugs.add(slug)
        report_meta: dict[str, str | int | list[str] | dict[str, str]] = {
            "title": f"{heading} ({topic})",
            "slug": slug,
            "type": "report",
            "project": project_name,
            "topics": topic,
        }
        section_desc = _description(body)
        if section_desc:
            report_meta["description"] = section_desc
        if tags:
            report_meta["tags"] = tags
        report_meta["generated"] = _generated()
        path = reports_dir / f"{slug}.md"
        _write_note(path, report_meta, body.strip())
        written.append(path)
    # Stale sections are removed AFTER the write, not cleared before it: an
    # up-front wipe deletes the very files _write_note compares against, so
    # every re-ingest would rewrite every section with a fresh timestamp.
    current = {path.name for path in written}
    for stale in reports_dir.glob(f"{prefix}--*.md"):
        if stale.name not in current:
            stale.unlink()
    return written


def ingest_notes(source: Path, brain_dir: Path) -> tuple[list[Path], list[str]]:
    """Ingest arbitrary frontmattered markdown (a file or a directory).

    Grows a brain from non-researchkit producers: any ``*.md`` whose
    frontmatter carries a ``url`` becomes a normal source note (same
    URL-keyed identity and topic merging as project ingest); anything else
    with frontmatter and a body is filed under ``notes/imported/``. Files
    without provenance are skipped with a reason.

    Returns ``(written_notes, skip_reasons)``.
    """
    source = source.absolute()
    if source.is_dir():
        files = sorted(source.rglob("*.md"))
    elif source.is_file():
        files = [source]
    else:
        raise FileNotFoundError(f"{source} not found (looked for this exact path).")

    sources_dir = brain_dir / NOTES_DIRNAME / SOURCES_DIRNAME
    imported_dir = brain_dir / NOTES_DIRNAME / "imported"
    written: list[Path] = []
    skipped: list[str] = []
    for path in files:
        note = parse_note(path.read_text(encoding="utf-8"))
        if not note.body.strip():
            skipped.append(f"{path.name}: empty body")
            continue
        url = note.meta.get("url", "")
        topic = note.meta.get("topics", "") or note.meta.get("topic", "") or "imported"
        project = note.meta.get("project", "") or note.meta.get("source", "")
        title = note.meta.get("title", "")
        if not (url or project or title):
            skipped.append(
                f"{path.name}: no provenance frontmatter (need url/project/title)"
            )
            continue
        if url:
            sources_dir.mkdir(parents=True, exist_ok=True)
            note_path = _source_note_path(sources_dir, url, path.stem)
            topics_value, projects_value = [topic], [project] if project else []
            providers_value = _read_list(note.meta.get("providers", ""))
            if note_path.is_file():
                existing = parse_note(note_path.read_text(encoding="utf-8"))
                topics_value = _merge_topics(existing.meta.get("topics", ""), topic)
                if project:
                    projects_value = _merge_topics(
                        existing.meta.get("projects", ""), project
                    )
                else:
                    projects_value = _read_list(existing.meta.get("projects", ""))
                providers_value = _merge_all(
                    existing.meta.get("providers", ""),
                    note.meta.get("providers", ""),
                )
            imported_meta: dict[str, str | int | list[str] | dict[str, str]] = {
                "title": title or url,
                "slug": note_path.stem,
                "type": "source",
                "url": url,
                "topics": topics_value,
                "projects": projects_value,
                "providers": providers_value,
            }
        else:
            imported_dir.mkdir(parents=True, exist_ok=True)
            slug = slugify(title or path.stem)[:60] or "note"
            note_path = imported_dir / f"{slug}.md"
            imported_meta = {
                "title": title or path.stem,
                "slug": slug,
                "type": "note",
                "topics": topic,
                "project": project,
            }
        # Author-supplied OKF lifecycle/trust fields pass straight through:
        # brainkit never invents a `status`, a `stale_after` or a `verified`
        # (§5.2-5.5) — those are claims only a human or a process can make.
        # `derived_from` is how a distilled note keeps its chain to sources.
        # Summarization is a documented memory-poisoning channel (OWASP ASI06),
        # so an insight that loses its provenance is the failure mode, not a
        # tidy-up detail — but the field is only ever passed through, never
        # invented.
        for okf_field in (
            "status",
            "stale_after",
            "verified",
            "description",
            "derived_from",
            "related",
            "resource",
            "tags",
        ):
            if note.meta.get(okf_field):
                imported_meta[okf_field] = note.meta[okf_field]
        imported_meta["generated"] = _generated()
        _write_note(note_path, imported_meta, note.body.strip())
        written.append(note_path)
    build_index(brain_dir)
    return written, skipped


def _iter_notes(brain_dir: Path) -> list[tuple[Path, Note]]:
    """Every concept document in the brain.

    ``index.md`` and ``log.md`` are OKF §3.1 reserved filenames — directory
    listings and history, not knowledge — so they are excluded at the one
    place every read path funnels through. Otherwise a per-directory index
    would be indexed as a note and could out-rank the notes it lists.
    """
    notes_dir = brain_dir / NOTES_DIRNAME
    if not notes_dir.is_dir():
        return []
    return [
        (path, parse_note(path.read_text(encoding="utf-8")))
        for path in sorted(notes_dir.rglob("*.md"))
        if path.name not in RESERVED_FILENAMES
    ]


def _ellipsize(text: str, limit: int) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def _is_prose(line: str) -> bool:
    """Is this line something worth showing as a description?

    Not: blank lines, ATX headings, horizontal rules, images, table pipes.
    A researchkit summary opens ``## Executive Summary`` with its first
    sentence on the very next line, so this has to be judged per LINE — a
    paragraph-level check discards the heading and the sentence together, and
    then happily settles on the ``---`` rule further down as the description.
    """
    text = line.strip()
    if not text or text.startswith(("#", "![", "|")):
        return False
    return set(text) - set("-*_ ") != set()  # a rule is only rule characters


def _description(body: str) -> str:
    """One-line description of a note: its first prose paragraph, truncated.

    Lets an agent pick a note out of an ``index.md`` without opening it.
    """
    # ponytail: no markdown stripping — link/emphasis syntax passes through;
    # add a stripper only if index descriptions prove too noisy in practice.
    lines = body.splitlines()
    for i, line in enumerate(lines):
        if not _is_prose(line):
            continue
        paragraph = [line]
        for following in lines[i + 1 :]:
            if not following.strip() or not _is_prose(following):
                break
            paragraph.append(following)
        return _ellipsize(" ".join(paragraph), _DESC_CHARS)
    return ""


def _entry(path: Path, note: Note, base: Path, suffix: str = "") -> str:
    """One OKF §8 index line: link, description, optional annotation.

    The link text is truncated. A researchkit ``topic`` is a whole paragraph
    of scoping prose, so untruncated titles turn the index — the one artifact
    that has to stay small enough to load every run — back into the thing it
    was rewritten to stop being. The note itself keeps the full title.
    """
    # Relative to the index doing the linking (OKF §6.2). Bundle-absolute
    # "/notes/..." is the spec's recommended form, but it resolves against the
    # host in a rendered markdown view, which breaks the links on GitHub.
    link = os.path.relpath(path, base).replace(os.sep, "/")
    desc = note.meta.get("description") or _description(note.body)
    line = f"* [{_ellipsize(note.title or path.stem, _TITLE_CHARS)}]({link})"
    if desc:
        line += f" — {_ellipsize(desc, _DESC_CHARS)}"
    return line + suffix


def _write_dir_index(directory: Path, heading: str, lines: list[str]) -> None:
    """An ``index.md`` for one level (OKF §8, no frontmatter)."""
    if not directory.is_dir():
        return
    body = [f"# {heading}", "", f"{len(lines)} notes.", ""] + (lines or ["*(empty)*"])
    (directory / INDEX_FILENAME).write_text("\n".join(body) + "\n", encoding="utf-8")


def _render_index(brain_dir: Path, *, write_levels: bool = True) -> str:
    """Regenerate the brain's index files — the map an agent reads first.

    The root ``index.md`` is the TOP of the pyramid and nothing else:
    domains, then topics, then a pointer to each level's own index. It
    deliberately does not list sources or report sections. The flat
    every-topic-times-every-source listing it replaces measured 17.9 KB at 4
    topics and 83 sources, which extrapolates to ~450 KB at a hundred topics
    — an artifact no agent can afford to load, describing a brain it is
    supposed to make navigable.

    Each ``notes/<level>/index.md`` then lists that level in full, so the
    detail is one hop away rather than absent: OKF §8 progressive disclosure,
    which is what the spec prescribes and what brainkit has been claiming.
    """
    notes = _iter_notes(brain_dir)
    by_kind: dict[str, list[tuple[Path, Note]]] = {}
    for path, note in notes:
        by_kind.setdefault(note.meta.get("type", ""), []).append((path, note))

    domains = by_kind.get("domain", [])
    topics = by_kind.get("topic", [])
    titles = {n.meta.get("slug", p.stem): n.title for p, n in notes}

    counts = " · ".join(
        f"{len(by_kind.get(kind, []))} {kind}s" for kind in LEVELS if kind != "note"
    )
    lines = [
        "# Brain index",
        "",
        f"{counts} · generated {_now()}",
        "",
        "Descend: a domain note summarizes its topics, a topic note lists its",
        "sources. Every level's full listing lives in its own `index.md`.",
    ]

    if domains:
        lines += ["", "## Domains", ""]
        for path, note in domains:
            count = note.meta.get("topic_count", "")
            lines.append(
                _entry(path, note, brain_dir, f" ({count} topics)" if count else "")
            )

    if topics:
        lines += ["", "## Topics", ""]
        for path, note in topics:
            parent = note.meta.get("parent", "")
            label = _ellipsize(titles.get(parent, parent), _TITLE_CHARS)
            lines.append(
                _entry(path, note, brain_dir, f" · in *{label}*" if parent else "")
            )

    lines += ["", "## Levels", ""]
    for kind, dirname in _LEVEL_DIRNAME.items():
        directory = brain_dir / NOTES_DIRNAME / dirname
        entries = sorted(by_kind.get(kind, []), key=lambda pair: pair[0].name)
        if write_levels:
            _write_dir_index(
                directory,
                f"{dirname.capitalize()} index",
                [_entry(p, n, directory) for p, n in entries],
            )
        if entries:
            lines.append(
                f"* [{dirname}]({NOTES_DIRNAME}/{dirname}/{INDEX_FILENAME}) "
                f"— {len(entries)} notes"
            )

    # OKF §12: the bundle-root index is the one place frontmatter is allowed
    # in an index file, and the one place the targeted spec version is stated.
    front = _frontmatter({"okf_version": OKF_VERSION})
    return f"{front}\n\n" + "\n".join(lines) + "\n"


def build_index(brain_dir: Path) -> Path:
    """Write the root index and every level index; return the root's path.

    An index whose CONTENT is unchanged keeps its old generation stamp, so
    regenerating never dirties the tree on its own — same contract as
    :func:`_write_note`.
    """
    text = _render_index(brain_dir)
    index = brain_dir / INDEX_FILENAME
    index.parent.mkdir(parents=True, exist_ok=True)
    if index.is_file():
        previous = index.read_text(encoding="utf-8")
        if _STAMP.sub("", previous) == _STAMP.sub("", text):
            return index
    index.write_text(text, encoding="utf-8")
    return index


def link_graph(brain_dir: Path) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    """Resolve the ``[[wikilinks]]`` the brain has always written but never read.

    Every topic note has listed its sources as ``[[slug]]`` since v0.1, and
    nothing ever parsed them back: no traversal, no backlinks, no way to tell
    a dead link from a link to a note that has not been written yet. The
    graph is already in the files; this reads it.

    Returns ``(outgoing, incoming)`` keyed by note slug. A target that does
    not resolve still appears in ``outgoing`` — OKF §6.1 says a broken link
    is not malformed, it may simply be knowledge not yet written — so callers
    decide whether to care (:func:`lint` does).
    """
    notes = _by_slug(brain_dir)
    slugs = set(notes)
    outgoing: dict[str, set[str]] = {}
    incoming: dict[str, set[str]] = {slug: set() for slug in slugs}
    for slug, (_path, note) in notes.items():
        # Only AUTHORED bodies carry edges. A source note is an archived web
        # page, and pages about wikis quote `[[note-name]]` as an example —
        # reading those as references invented 94 dead links on a real brain
        # and would have manufactured backlinks from any that happened to
        # match a real slug.
        # `related` is an explicit, unambiguous edge list any note may carry —
        # including the kinds whose bodies are not read for links. It is how a
        # report section or a hand-annotated source says "see also" without
        # reopening the false-positive problem below.
        targets = set(_read_list(note.meta.get("related", "")))
        if note.meta.get("type", "") in _AUTHORED_KINDS:
            targets |= {
                match.group(1).strip() for match in _WIKILINK.finditer(note.body)
            }
        outgoing[slug] = targets
        for target in targets & slugs:
            incoming[target].add(slug)
    return outgoing, incoming


def _by_slug(brain_dir: Path) -> dict[str, tuple[Path, Note]]:
    """Notes keyed by slug — the identity every wiki-link resolves against."""
    return {
        note.meta.get("slug") or path.stem: (path, note)
        for path, note in _iter_notes(brain_dir)
    }


def _recency_rank(date_text: object) -> float:
    """Sort key: newer dates rank first, unparseable/absent dates last.

    Deterministic recency (not LLM judgment, not decay windows): day
    granularity via the date ORDINAL — no timestamps, so the rank is
    identical on every machine (naive ``timestamp()`` would interpret the
    date in host-local time) and pre-1970 dates need no special case.
    ``inf`` puts unparseable/absent dates after every real date.
    """
    text = str(date_text or "").strip()
    try:
        return -float(dt.date.fromisoformat(text[:10]).toordinal())
    except ValueError:
        return float("inf")


def _own_body(note: Note) -> str:
    """A note's own prose, minus the link appendix brainkit generates.

    ``## Topics`` and ``## Sources`` are descent lists written by
    :func:`_write_node_note`, not content — they repeat every child's title
    and description. Scoring them lets a domain note inherit the vocabulary
    of everything beneath it and win every query about any of its sources,
    which is precisely the wrong end of the pyramid to land on.
    """
    cut = len(note.body)
    for heading in ("\n## Topics\n", "\n## Sources\n", "\n## Report sections\n"):
        found = note.body.find(heading)
        if found != -1:
            cut = min(cut, found)
    return note.body[:cut]


def _level_prior(kind: str) -> float:
    """Rank multiplier for a note's level in the pyramid.

    One tunable (:data:`_LEVEL_PRIOR_CEILING`) spread geometrically across the
    levels, so a domain note gets the ceiling, a source note gets 1.0, and the
    rungs between are evenly spaced. Length normalization alone will not do
    this job: it knows a document is short, not that it is *synthesized*.

    The ceiling deliberately matches the flat 2x kind boost this replaces —
    the shape changed, the strength did not, because nothing has measured it
    yet. Tune it against an eval set, not by taste.
    """
    depth = LEVELS.get(kind, max(LEVELS.values()))
    deepest = max(LEVELS.values())
    return float(_LEVEL_PRIOR_CEILING ** ((deepest - depth) / deepest))


def _bm25(tf: int, length: int, avg_length: float) -> float:
    """Saturating, length-normalized term weight (Robertson/Sparck Jones)."""
    if tf <= 0:
        return 0.0
    norm = 1 - _BM25_B + _BM25_B * (length / avg_length if avg_length else 1.0)
    return tf * (_BM25_K1 + 1) / (tf + _BM25_K1 * norm)


def _snippet(body: str, terms: list[str]) -> str:
    for paragraph in body.split("\n"):
        lowered = paragraph.lower()
        if any(term in lowered for term in terms):
            return paragraph.strip()[:_SNIPPET_CHARS]
    return body.strip()[:_SNIPPET_CHARS]


def search(
    brain_dir: Path, query: str, limit: int = 5, kind: str | None = None
) -> list[SearchHit]:
    """Lexical retrieval over the brain; every hit carries its citation URL.

    ``kind`` filters to one note type (``topic``/``source``/``report``/
    ``note``). Topic and report notes get a 2x score boost: they are
    synthesized, on-domain knowledge, and raw term frequency otherwise lets
    long chatty source archives outrank them. Equal scores break by
    recency (``published``, else ``ingested_at``): vector-free but not
    time-blind — a superseded fact never outranks its fresher sibling at
    the same relevance.
    """
    terms = list(dict.fromkeys(_TOKEN.findall(query.lower())))
    if not terms:
        return []

    notes = _iter_notes(brain_dir)
    if not notes:
        return []

    # Tokenize once. Body scoring uses the note's OWN prose (see _own_body);
    # frontmatter never scores at all, since it is metadata, not content.
    tokens: dict[Path, list[str]] = {}
    titles: dict[Path, set[str]] = {}
    kinds: dict[Path, str] = {}
    for path, note in notes:
        tokens[path] = _TOKEN.findall(_own_body(note).lower())
        titles[path] = set(_TOKEN.findall(note.title.lower()))
        kinds[path] = note.meta.get("type", "")

    # IDF is global — computed over the whole brain, not the filtered subset —
    # so a --kind filter narrows *what comes back*, never what a term is worth.
    total = len(notes)
    doc_freq = {
        term: sum(1 for path in tokens if term in tokens[path] or term in titles[path])
        for term in terms
    }
    idf = {
        term: math.log(1 + (total - df + 0.5) / (df + 0.5))
        for term, df in doc_freq.items()
    }

    # Average length PER LEVEL: a source archive and a topic synthesis have
    # wildly different natural lengths, and normalizing against one global
    # mean would hand short notes a second, accidental hierarchy boost on top
    # of the explicit one.
    lengths: dict[str, list[int]] = {}
    for path in tokens:
        lengths.setdefault(kinds[path], []).append(len(tokens[path]))
    avg_length = {k: sum(v) / len(v) for k, v in lengths.items() if v}

    hits: list[SearchHit] = []
    rank_key: dict[Path, tuple[int, int, float]] = {}
    for path, note in notes:
        note_kind = kinds[path]
        if kind and note_kind != kind:
            continue
        counts = Counter(tokens[path])
        score = 0.0
        covered = 0
        for term in terms:
            in_title = term in titles[path]
            tf = counts.get(term, 0)
            if not tf and not in_title:
                continue
            covered += 1
            weight = _bm25(tf, len(tokens[path]), avg_length.get(note_kind, 0.0))
            score += idf[term] * (weight + _TITLE_WEIGHT * in_title)
        if score <= 0:
            continue
        score *= _level_prior(note_kind)
        # Ties break on how much of the query was matched, then on level, then
        # on the CONTENT date (never ingest time — an undated note must not
        # borrow freshness from when it happened to be imported), then path.
        rank_key[path] = (
            -covered,
            LEVELS.get(note_kind, max(LEVELS.values())),
            _recency_rank(note.meta.get("published", "")),
        )
        hits.append(
            SearchHit(
                path=path,
                title=note.title or path.stem,
                score=score,
                url=note.meta.get("url", ""),
                snippet=_snippet(note.body, terms),
                project=note.meta.get("project", ""),
                published=note.meta.get("published", ""),
                source_type=note.meta.get("source_type", ""),
                kind=note_kind,
                parent=note.meta.get("parent", ""),
            )
        )
    hits.sort(key=lambda h: (-h.score, *rank_key[h.path], h.path.name))
    return hits[:limit]


@dataclass(frozen=True)
class Finding:
    """One thing wrong with the brain, named so it can be grepped for."""

    check: str
    path: Path
    detail: str
    # Errors are structural breaks the brain can fix. Warnings are judgements
    # about the world (a fact went stale, an index is getting big) — they must
    # not fail a CI gate, or the gate turns red one morning with no change to
    # the repository and everyone learns to ignore it.
    severity: str = "error"

    def __str__(self) -> str:
        return f"{self.severity} {self.check}: {self.path}: {self.detail}"


# A root index past this is a signal to group topics under domains, not a
# hard failure — the point is to notice before it stops being loadable.
_INDEX_SOFT_MAX_BYTES = 8 * 1024


def _valid_date(text: str) -> bool:
    try:
        dt.date.fromisoformat(text[:10])
    except ValueError:
        return False
    return True


def _reachable(brain_dir: Path) -> set[str]:
    """Slugs reachable by descending the pyramid from its roots.

    Roots are the notes nothing is expected to link to: domains, top-level
    topics, and free-form imports. Everything else has to be reachable by
    following wiki-links down, because that descent is exactly what the
    bundled skill tells an agent to do — a note it cannot reach is a note
    that only search can find.

    Deliberately NOT seeded from the level indexes: those list every note by
    construction, so seeding from them would make the check vacuous.
    """
    notes = _by_slug(brain_dir)
    outgoing, _incoming = link_graph(brain_dir)
    roots = [
        slug
        for slug, (_path, note) in notes.items()
        if note.meta.get("type") == "domain"
        or note.meta.get("type") == "note"
        or (note.meta.get("type") == "topic" and not note.meta.get("parent"))
    ]
    seen: set[str] = set()
    stack = list(roots)
    while stack:
        slug = stack.pop()
        if slug in seen:
            continue
        seen.add(slug)
        stack.extend(target for target in outgoing.get(slug, ()) if target in notes)
    return seen


def lint(brain_dir: Path, *, as_of: str | None = None) -> list[Finding]:
    """Check the brain for the damage a markdown corpus actually accumulates.

    Read-only, deterministic, no LLM — Karpathy's wiki pattern is three
    operations (ingest, query, **lint**) and brainkit shipped the first two.
    Every check is either an invariant brainkit itself claims (one note per
    URL, a ``corroboration`` count matching its ``projects`` list, an index
    that matches its notes) or a structural break a reader would otherwise
    meet as a silent absence (a dead link, an unreachable note).

    ``as_of`` fixes "now" for the staleness check so a run is reproducible.

    Deliberately NOT here: contradiction detection. Its deterministic
    proxy — note pairs with high term overlap and distant dates — measures
    topic continuity, not disagreement: it flags every revision of a subject
    and misses any contradiction phrased in different words. A check nobody
    can act on teaches people to ignore the whole command.
    """
    findings: list[Finding] = []
    notes = _iter_notes(brain_dir)
    by_slug = _by_slug(brain_dir)
    outgoing, _incoming = link_graph(brain_dir)
    today = (as_of or _now())[:10]

    seen_urls: dict[str, Path] = {}
    seen_paths: dict[str, Path] = {}
    for path, note in notes:
        rel = path.relative_to(brain_dir)
        kind = note.meta.get("type", "")

        # macOS and Windows fold case: two notes differing only by case are
        # one file there and two here, which corrupts a brain on clone.
        folded = str(rel).casefold()
        if folded in seen_paths:
            findings.append(
                Finding("path-collision", rel, f"case-folds onto {seen_paths[folded]}")
            )
        else:
            seen_paths[folded] = rel

        if not note.meta:
            findings.append(Finding("no-frontmatter", rel, "OKF §11.1: none found"))
            continue
        if not kind:
            findings.append(Finding("no-type", rel, "OKF §11.2 requires `type`"))
        elif kind not in LEVELS:
            findings.append(Finding("unknown-type", rel, f"{kind!r} is not a level"))

        for key in ("published", "stale_after"):
            value = note.meta.get(key, "")
            if value and not _valid_date(value):
                findings.append(Finding("bad-date", rel, f"{key}={value!r}"))

        stale = note.meta.get("stale_after", "")
        if stale and _valid_date(stale) and stale[:10] <= today:
            findings.append(
                Finding("stale", rel, f"stale_after {stale[:10]}", severity="warning")
            )

        if kind == "source":
            url = note.meta.get("url", "")
            if not url:
                findings.append(Finding("no-url", rel, "a source note must cite one"))
            elif url in seen_urls:
                findings.append(
                    Finding("duplicate-url", rel, f"also claimed by {seen_urls[url]}")
                )
            else:
                seen_urls[url] = rel
            projects = _read_list(note.meta.get("projects", ""))
            supplier = note.meta.get("content_from", "")
            if supplier and supplier not in projects:
                findings.append(
                    Finding(
                        "orphaned-content",
                        rel,
                        f"body came from {supplier!r}, which no longer cites it; "
                        "re-ingest a citing run to re-select the content",
                    )
                )
            stored = note.meta.get("corroboration", "")
            if stored and stored != str(_corroboration(projects)):
                findings.append(
                    Finding(
                        "corroboration-drift",
                        rel,
                        f"stored {stored}, {len(projects)} citing runs",
                    )
                )

    for slug, targets in outgoing.items():
        source_path = by_slug[slug][0].relative_to(brain_dir)
        for target in sorted(targets - set(by_slug)):
            findings.append(Finding("dead-link", source_path, f"[[{target}]]"))

    reachable = _reachable(brain_dir)
    for slug, (path, _note) in sorted(by_slug.items()):
        if slug not in reachable:
            findings.append(
                Finding(
                    "unreachable",
                    path.relative_to(brain_dir),
                    "no descent path from any root reaches this note",
                )
            )

    index = brain_dir / INDEX_FILENAME
    if index.is_file():
        current = index.read_text(encoding="utf-8")
        # Regenerate and compare: an index that no longer matches its notes is
        # a map of a place that has changed, which is worse than no map.
        if _STAMP.sub("", current) != _STAMP.sub(
            "", _render_index(brain_dir, write_levels=False)
        ):
            findings.append(
                Finding(
                    "index-stale",
                    Path(INDEX_FILENAME),
                    "does not match the notes; run `brainkit index`",
                )
            )
        size = len(current.encode("utf-8"))
        if size > _INDEX_SOFT_MAX_BYTES:
            findings.append(
                Finding(
                    "index-too-big",
                    Path(INDEX_FILENAME),
                    f"{size} bytes > {_INDEX_SOFT_MAX_BYTES}; group topics "
                    "under domains so the map stays loadable",
                    severity="warning",
                )
            )
    return findings


def rebuild(brain_dir: Path) -> list[Path]:
    """Re-derive everything brainkit owns; return the notes that changed.

    Separate from :func:`lint` on purpose. Lint is read-only, and a read-only
    contract is worth keeping — a check that might edit your knowledge base is
    a check you hesitate to run. This rewrites only what brainkit derives:
    frontmatter encoding, the ``corroboration`` count, and the indexes. It is
    also the migration path for brains written before frontmatter was
    JSON-encoded, whose notes would otherwise only be repaired if their
    research run happened to be re-ingested.

    Dead links, unreachable notes and staleness are never touched: each is a
    statement about knowledge, and the fix is to write the missing note or
    re-run the research, not to delete the evidence that it is missing.
    """
    changed: list[Path] = []
    for path, note in _iter_notes(brain_dir):
        text = path.read_text(encoding="utf-8")
        meta: dict[str, str | int | list[str] | dict[str, str]] = {}
        for key, raw in raw_frontmatter(text):
            # Work from the RAW value. A value already written as JSON is
            # already canonical and is kept verbatim; anything else is a legacy
            # plain scalar and becomes a JSON string. Never re-decode
            # Note.meta: it cannot tell the string "null" from the literal
            # null, and rewriting would turn a title into an actual null.
            try:
                meta[key] = json.loads(raw)
            except ValueError:
                meta[key] = raw
        if note.meta.get("type") == "source":
            # The one derived field: recomputed, never trusted from the file.
            meta["corroboration"] = _corroboration(
                _read_list(note.meta.get("projects", ""))
            )
        _write_note(path, meta, note.body.strip())
        if path.read_text(encoding="utf-8") != text:
            changed.append(path)
    build_index(brain_dir)
    if changed:
        _append_log(brain_dir, "Rebuild", f"rewrote {len(changed)} notes")
    return changed


@dataclass(frozen=True)
class Coverage:
    """Mechanical facts about a result set.

    These are **retrieval gaps**, not knowledge gaps. BM25 cannot tell a
    subject the brain has never researched from one it filed under different
    words, so nothing here claims to know what the brain does not know — every
    field is a countable property of what came back.
    """

    unmatched_terms: list[str]
    newest: str
    runs: list[str]
    social: int
    total: int
    levels: list[str]

    def signals(self) -> list[str]:
        """One line per signal worth acting on; empty when nothing stands out."""
        out: list[str] = []
        if self.unmatched_terms:
            terms = ", ".join(sorted(self.unmatched_terms))
            out.append(f"no note in this brain contains: {terms}")
        out.append(
            f"newest matching content: {self.newest}"
            if self.newest
            else "no matching note carries a publication date"
        )
        if len(self.runs) == 1:
            out.append(f"every hit comes from one research run ({self.runs[0]})")
        else:
            out.append(f"{len(self.runs)} research runs are represented")
        if self.social:
            out.append(
                f"{self.social} of {self.total} hits are social-tier sources "
                "(user-generated; the classic poisoning vector)"
            )
        if "source" not in self.levels:
            out.append("only synthesized notes matched; no primary source did")
        elif len(set(self.levels)) == 1:
            out.append("only primary sources matched; no synthesis covers this")
        return out


def ancestors(brain_dir: Path, slug: str) -> list[str]:
    """Titles from the top of the pyramid down to ``slug``, exclusive.

    A hit's breadcrumb. Topic and domain notes name their parent outright;
    a source or report is placed by whichever authored note cites it, which
    is what the link graph already knows.
    """
    notes = _by_slug(brain_dir)
    _outgoing, incoming = link_graph(brain_dir)
    chain: list[str] = []
    seen = {slug}
    current = slug
    while True:
        if current not in notes:
            break
        note = notes[current][1]
        parent = note.meta.get("parent", "") or next(
            (link for link in sorted(incoming.get(current, ())) if link not in seen),
            "",
        )
        if not parent or parent in seen or parent not in notes:
            break
        seen.add(parent)
        chain.append(notes[parent][1].title or parent)
        current = parent
    return list(reversed(chain))


def context(
    brain_dir: Path, query: str, limit: int = 5, kind: str | None = None
) -> tuple[list[SearchHit], Coverage]:
    """Search, plus mechanical coverage signals about what came back.

    The verb every comparable system pairs with plain retrieval — gbrain's
    ``think``, Hindsight's ``reflect`` — and both report the differentiator is
    honest gap analysis rather than the prose. brainkit has no model, so it
    does not pretend to synthesize: it returns the same hits with the counts
    an agent would otherwise have to derive by opening every note.
    """
    hits = search(brain_dir, query, limit=limit, kind=kind)
    terms = list(dict.fromkeys(_TOKEN.findall(query.lower())))
    corpus: set[str] = set()
    for _path, note in _iter_notes(brain_dir):
        corpus.update(_TOKEN.findall(note.title.lower()))
        corpus.update(_TOKEN.findall(_own_body(note).lower()))
    dates = sorted((hit.published[:10] for hit in hits if hit.published), reverse=True)
    runs = sorted({hit.project for hit in hits if hit.project})
    return hits, Coverage(
        unmatched_terms=[term for term in terms if term not in corpus],
        newest=dates[0] if dates else "",
        runs=runs,
        social=sum(1 for hit in hits if hit.source_type == "social"),
        total=len(hits),
        levels=[hit.kind for hit in hits],
    )
