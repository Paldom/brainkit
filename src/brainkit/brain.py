"""Build and query a Git-native brain from researchkit projects.

A *brain* is a directory of frontmattered markdown notes — portable,
human-readable, diffable:

    brain/
    ├── index.md            # generated wiki index (topics → sources)
    └── notes/
        ├── topics/<topic-slug>.md      # one note per ingested research run
        ├── sources/<hash>-<slug>.md    # one note per downloaded source
        ├── reports/<run>--<slug>.md    # report sections (ingest --include-reports)
        └── imported/<slug>.md          # frontmattered md via ingest-notes

Writes are *gated by provenance*: notes are created by ingesting a
researchkit project (``result.json`` + ``materials/``; a boosted run's
``subprojects/`` recurse) or, via :func:`ingest_notes`, arbitrary markdown
that carries provenance frontmatter (``url``/``project``/``title``) — never
anonymous free text. Every claim in the brain traces back to a research run
or a source URL. Retrieval is lexical (term-frequency scoring,
title-weighted) and returns citations alongside every hit.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
import re
from dataclasses import dataclass, field
from pathlib import Path

from brainkit import Note, parse_note, slugify

NOTES_DIRNAME = "notes"
TOPICS_DIRNAME = "topics"
SOURCES_DIRNAME = "sources"
REPORTS_DIRNAME = "reports"
SUBPROJECTS_DIRNAME = "subprojects"
INDEX_FILENAME = "index.md"

_TOKEN = re.compile(r"[a-z0-9]+")
_TITLE_WEIGHT = 3
_SNIPPET_CHARS = 240
_DESC_CHARS = 160


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
    score: int
    url: str
    snippet: str
    project: str = ""


def _frontmatter(pairs: dict[str, str]) -> str:
    lines = ["---"]
    for key, value in pairs.items():
        lines.append(f"{key}: {' '.join(str(value).split())}")
    lines.append("---")
    return "\n".join(lines)


def _now() -> str:
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds")


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


def _merge_topics(existing: str, topic: str) -> str:
    topics = [t.strip() for t in existing.split(",") if t.strip()]
    if topic not in topics:
        topics.append(topic)
    return ", ".join(topics)


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


def ingest_research_project(
    project_dir: Path,
    brain_dir: Path,
    *,
    include_reports: bool = False,
    _project_name: str | None = None,
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
    topic_slug = (
        f"{slugify(topic)[:40] or 'topic'}--"
        f"{slugify(project_name)[:32] or 'run'}-{run_digest}"
    )

    topics_dir = brain_dir / NOTES_DIRNAME / TOPICS_DIRNAME
    sources_dir = brain_dir / NOTES_DIRNAME / SOURCES_DIRNAME
    topics_dir.mkdir(parents=True, exist_ok=True)
    sources_dir.mkdir(parents=True, exist_ok=True)

    source_notes: list[Path] = []
    skip_reasons: list[str] = []  # material skips first; sub-project skips appended
    materials_dir = project_dir / "materials"
    for material in _material_files(materials_dir):
        note = parse_note(material.read_text(encoding="utf-8"))
        url = note.meta.get("url", "")
        if not url or not note.body.strip():
            reason = "no 'url' in frontmatter" if not url else "empty body"
            skip_reasons.append(f"materials/{material.name}: {reason}")
            continue
        note_path = _source_note_path(sources_dir, url, material.stem)
        slug = note_path.stem
        topics_value = topic
        projects_value = project_name
        existing_meta: dict[str, str] = {}
        if note_path.is_file():
            existing = parse_note(note_path.read_text(encoding="utf-8"))
            existing_meta = dict(existing.meta)
            topics_value = _merge_topics(existing.meta.get("topics", ""), topic)
            projects_value = _merge_topics(
                existing.meta.get("projects", ""), project_name
            )
        meta = {
            "title": note.meta.get("title", url),
            "slug": slug,
            "type": "source",
            "url": url,
            "topics": topics_value,
            "projects": projects_value,
            "providers": note.meta.get("providers", ""),
        }
        # Research metadata passes through: where the content came from and
        # when it was published matters as much as the content itself. On a
        # shared-URL merge, a field the newer material lacks keeps the
        # existing note's value (union semantics — never lose provenance).
        for extra in ("source_type", "content_kind", "published", "final_url"):
            value = note.meta.get(extra) or existing_meta.get(extra)
            if value:
                meta[extra] = value
        meta["ingested_at"] = _now()
        front = _frontmatter(meta)
        note_path.write_text(f"{front}\n\n{note.body.strip()}\n", encoding="utf-8")
        source_notes.append(note_path)

    summary = (
        str(result.get("meta_summary", "")).strip()
        or str(result.get("super_summary") or "").strip()
    )
    links = "\n".join(
        f"- [[{p.stem}]] — {parse_note(p.read_text(encoding='utf-8')).title}"
        for p in source_notes
    )
    body_parts = [
        part for part in (summary, "## Sources", links or "*(none downloaded)*") if part
    ]
    front = _frontmatter(
        {
            "title": topic,
            "slug": topic_slug,
            "type": "topic",
            "project": project_name,
            "source_count": str(len(source_notes)),
            "ingested_at": _now(),
        }
    )
    topic_note = topics_dir / f"{topic_slug}.md"
    topic_note.write_text(
        f"{front}\n\n" + "\n\n".join(body_parts) + "\n", encoding="utf-8"
    )

    pruned = _prune_project_sources(sources_dir, project_name, set(source_notes))

    report_notes: list[Path] = []
    if include_reports:
        report_notes = _ingest_report_sections(
            project_dir, brain_dir, topic=topic, project_name=project_name
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
                )
            )

    build_index(brain_dir)
    return IngestReport(
        topic=topic,
        topic_note=topic_note,
        source_notes=source_notes,
        skipped_sources=skipped_materials,
        pruned_sources=pruned,
        skip_reasons=skip_reasons,
        report_notes=report_notes,
        sub_reports=sub_reports,
    )


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
        projects = [
            s.strip() for s in note.meta.get("projects", "").split(",") if s.strip()
        ]
        if project_name not in projects:
            continue
        projects.remove(project_name)
        if projects:
            meta = dict(note.meta)
            meta["projects"] = ", ".join(projects)
            remaining_topics = [
                topic_by_project[proj] for proj in projects if proj in topic_by_project
            ]
            if remaining_topics:
                deduped = list(dict.fromkeys(remaining_topics))
                meta["topics"] = ", ".join(deduped)
            note_path.write_text(
                f"{_frontmatter(meta)}\n\n{note.body.strip()}\n", encoding="utf-8"
            )
        else:
            note_path.unlink()
            pruned += 1
    return pruned


def _ingest_report_sections(
    project_dir: Path, brain_dir: Path, *, topic: str, project_name: str
) -> list[Path]:
    """Chunk the project's ``report.md`` into one note per ``##`` section.

    Makes a run with thin/absent materials queryable: the report body itself
    (real, cited knowledge) becomes ``type: report`` notes carrying the
    project as provenance. Idempotent per project: prior report notes for
    this project are rewritten as a set.
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
    for stale in reports_dir.glob(f"{prefix}--*.md"):
        stale.unlink()

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
        front = _frontmatter(
            {
                "title": f"{heading} ({topic})",
                "slug": slug,
                "type": "report",
                "project": project_name,
                "topics": topic,
                "ingested_at": _now(),
            }
        )
        path = reports_dir / f"{slug}.md"
        path.write_text(f"{front}\n\n{body.strip()}\n", encoding="utf-8")
        written.append(path)
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
            topics_value, projects_value = topic, project
            providers_value = note.meta.get("providers", "")
            if note_path.is_file():
                existing = parse_note(note_path.read_text(encoding="utf-8"))
                topics_value = _merge_topics(existing.meta.get("topics", ""), topic)
                if project:
                    projects_value = _merge_topics(
                        existing.meta.get("projects", ""), project
                    )
                else:
                    projects_value = existing.meta.get("projects", "")
                providers_value = existing.meta.get("providers", "") or providers_value
            front = _frontmatter(
                {
                    "title": title or url,
                    "slug": note_path.stem,
                    "type": "source",
                    "url": url,
                    "topics": topics_value,
                    "projects": projects_value,
                    "providers": providers_value,
                    "ingested_at": _now(),
                }
            )
        else:
            imported_dir.mkdir(parents=True, exist_ok=True)
            slug = slugify(title or path.stem)[:60] or "note"
            note_path = imported_dir / f"{slug}.md"
            front = _frontmatter(
                {
                    "title": title or path.stem,
                    "slug": slug,
                    "type": "note",
                    "topics": topic,
                    "project": project,
                    "ingested_at": _now(),
                }
            )
        note_path.write_text(f"{front}\n\n{note.body.strip()}\n", encoding="utf-8")
        written.append(note_path)
    build_index(brain_dir)
    return written, skipped


def _iter_notes(brain_dir: Path) -> list[tuple[Path, Note]]:
    notes_dir = brain_dir / NOTES_DIRNAME
    if not notes_dir.is_dir():
        return []
    return [
        (path, parse_note(path.read_text(encoding="utf-8")))
        for path in sorted(notes_dir.rglob("*.md"))
    ]


def _description(body: str) -> str:
    """One-line description of a note: its first prose paragraph, truncated.

    Lets an agent pick sources from ``index.md`` without opening every note.
    Headings and images are skipped; anything else counts as prose.
    """
    # ponytail: no markdown stripping — link/emphasis syntax passes through;
    # add a stripper only if index descriptions prove too noisy in practice.
    for paragraph in body.split("\n\n"):
        text = " ".join(paragraph.split())
        if not text or text.startswith(("#", "![")):
            continue
        if len(text) > _DESC_CHARS:
            text = text[: _DESC_CHARS - 1].rstrip() + "…"
        return text
    return ""


def build_index(brain_dir: Path) -> Path:
    """Regenerate ``index.md``: every topic with its cited, described sources."""
    notes = _iter_notes(brain_dir)
    topics = [(p, n) for p, n in notes if n.meta.get("type") == "topic"]
    sources = [(p, n) for p, n in notes if n.meta.get("type") == "source"]

    lines = [
        "# Brain index",
        "",
        f"{len(topics)} topics · {len(sources)} sources · generated {_now()}",
    ]
    for _path, topic_note in topics:
        project = topic_note.meta.get("project", "")
        lines += ["", f"## {topic_note.title} ({project})", ""]
        for source_path, source_note in sources:
            note_projects = source_note.meta.get("projects", "")
            members = [s.strip() for s in note_projects.split(",") if s.strip()]
            if project in members:
                line = (
                    f"- [{source_note.title}]({source_note.meta.get('url', '')}) "
                    f"(`{source_path.stem}`)"
                )
                desc = _description(source_note.body)
                if desc:
                    line += f" — {desc}"
                lines.append(line)
    index = brain_dir / INDEX_FILENAME
    index.parent.mkdir(parents=True, exist_ok=True)
    index.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return index


def _score(note: Note, terms: list[str]) -> int:
    body_tokens = _TOKEN.findall(note.body.lower())
    title_tokens = _TOKEN.findall(note.title.lower())
    score = 0
    for term in terms:
        score += body_tokens.count(term)
        score += title_tokens.count(term) * _TITLE_WEIGHT
    return score


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
    long chatty source archives outrank them.
    """
    terms = _TOKEN.findall(query.lower())
    if not terms:
        return []
    hits: list[SearchHit] = []
    for path, note in _iter_notes(brain_dir):
        note_kind = note.meta.get("type", "")
        if kind and note_kind != kind:
            continue
        score = _score(note, terms)
        if score <= 0:
            continue
        # ponytail: fixed 2x kind boost — upgrade to length-normalized
        # (BM25-style) scoring if boosts keep needing tuning.
        if note_kind in ("topic", "report"):
            score *= 2
        hits.append(
            SearchHit(
                path=path,
                title=note.title or path.stem,
                score=score,
                url=note.meta.get("url", ""),
                snippet=_snippet(note.body, terms),
                project=note.meta.get("project", ""),
            )
        )
    hits.sort(key=lambda h: (-h.score, h.path.name))
    return hits[:limit]
