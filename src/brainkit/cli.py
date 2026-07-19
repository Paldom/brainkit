"""brainkit CLI: build a brain from researchkit projects and query it.

    brainkit ingest <researchkit-project-dir> [--brain DIR] [--include-reports]
    brainkit ingest-notes <dir-or-file.md> [--brain DIR]
    brainkit search "query" [--brain DIR] [-n N] [--kind topic|source|report|note]
    brainkit index [--brain DIR]
    brainkit list [--brain DIR]

The brain directory defaults to ``$BRAINKIT_DIR`` or ``./brain``.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from brainkit.brain import (
    NOTES_DIRNAME,
    IngestReport,
    build_index,
    ingest_notes,
    ingest_research_project,
    search,
)
from brainkit.brain import _iter_notes as iter_notes


def _default_brain() -> str:
    return os.environ.get("BRAINKIT_DIR", "brain")


def _require_brain(brain_dir: Path) -> str | None:
    """Return an error message if ``brain_dir`` is not an existing brain.

    A read command against a missing directory (e.g. a *relative* ``--brain``
    resolved against the wrong cwd) would otherwise return an empty result set,
    which is indistinguishable from a brain that genuinely has no matches. Fail
    loudly instead so callers see the path mistake rather than a false negative.
    """
    if not brain_dir.is_dir():
        return (
            f"brain directory not found: {brain_dir} (cwd: {Path.cwd()}) — "
            "pass an absolute --brain path or set BRAINKIT_DIR"
        )
    if not (brain_dir / NOTES_DIRNAME).is_dir():
        return (
            f"{brain_dir} exists but has no {NOTES_DIRNAME}/ — not a brain yet; "
            "ingest a researchkit project first"
        )
    return None


def _resolve_input_path(raw: str) -> Path:
    """Resolve a user-supplied path to an absolute one.

    A relative path that doesn't exist under the current cwd is retried
    against the shell's ``$PWD`` — ``uv run --directory`` changes cwd but
    inherits PWD, which is exactly the footgun this covers.
    """
    path = Path(raw).expanduser()
    if not path.is_absolute() and not path.exists():
        pwd = os.environ.get("PWD", "")
        if pwd and (Path(pwd) / raw).exists():
            return (Path(pwd) / raw).resolve()
    # resolve() (not absolute()) so symlinks/".." can't fork a project's
    # brain identity between the cwd and $PWD branches
    return path.resolve()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="brainkit",
        description="Portable, human-readable agent brain built from research runs.",
    )
    parser.add_argument(
        "--brain",
        default=_default_brain(),
        help="Brain directory (default: $BRAINKIT_DIR or ./brain)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show per-file detail (e.g. why a material was skipped)",
    )
    sub = parser.add_subparsers(dest="command")

    ingest = sub.add_parser(
        "ingest",
        help=(
            "Ingest a researchkit project (result.json + materials/); "
            "a boosted run's subprojects/ are ingested recursively"
        ),
    )
    ingest.add_argument("project", help="Path to the researchkit project folder")
    ingest.add_argument(
        "--include-reports",
        action="store_true",
        help="Also chunk report.md '##' sections into notes (for materials-thin runs)",
    )

    notes = sub.add_parser(
        "ingest-notes",
        help="Ingest arbitrary frontmattered markdown (a file or directory)",
    )
    notes.add_argument("path", help="Markdown file or directory of *.md files")

    query = sub.add_parser("search", help="Search the brain; hits cite their sources")
    query.add_argument("query", help="Search terms")
    query.add_argument(
        "-n", "--limit", type=int, default=5, help="Max hits (default 5)"
    )
    query.add_argument(
        "--kind",
        choices=["topic", "source", "report", "note"],
        default=None,
        help="Only return notes of this type",
    )

    sub.add_parser("index", help="Regenerate index.md")
    sub.add_parser("list", help="List notes in the brain")
    return parser


def _print_ingest_report(
    report: IngestReport, brain_dir: Path, verbose: bool, indent: str = ""
) -> None:
    extras = ""
    if report.report_notes:
        extras += f" + {len(report.report_notes)} report notes"
    print(
        f"{indent}Ingested {report.topic!r}: topic note + "
        f"{len(report.source_notes)} source notes{extras} "
        f"({report.skipped_sources} skipped) -> {brain_dir}"
    )
    if verbose:
        for reason in report.skip_reasons:
            print(f"{indent}  skipped {reason}")
    for sub_report in report.sub_reports:
        _print_ingest_report(sub_report, brain_dir, verbose, indent + "  ")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    brain_dir = Path(args.brain)

    if args.command == "ingest":
        project_dir = _resolve_input_path(args.project)
        try:
            report = ingest_research_project(
                project_dir, brain_dir, include_reports=args.include_reports
            )
        except (FileNotFoundError, ValueError) as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        _print_ingest_report(report, brain_dir, args.verbose)
        return 0

    if args.command == "ingest-notes":
        try:
            written, skipped = ingest_notes(_resolve_input_path(args.path), brain_dir)
        except (FileNotFoundError, ValueError) as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        print(f"Ingested {len(written)} notes ({len(skipped)} skipped) -> {brain_dir}")
        if args.verbose:
            for reason in skipped:
                print(f"  skipped {reason}")
        return 0

    if args.command in ("search", "index", "list"):
        err = _require_brain(brain_dir)
        if err is not None:
            print(f"Error: {err}", file=sys.stderr)
            return 2

    if args.command == "search":
        hits = search(brain_dir, args.query, limit=args.limit, kind=args.kind)
        if not hits:
            print("No matches.")
            return 1
        for hit in hits:
            if hit.url:
                citation = f" <{hit.url}>"
            elif hit.project:
                citation = f" (research run: {hit.project})"
            else:
                citation = f" (note: {hit.path.name})"
            date = f" [{hit.published[:10]}]" if hit.published else ""
            tier = f" ({hit.source_type})" if hit.source_type == "social" else ""
            print(f"[{hit.score}] {hit.title}{date}{tier}{citation}")
            print(f"    {hit.snippet}")
            print(f"    note: {hit.path}")
        return 0

    if args.command == "index":
        print(build_index(brain_dir))
        return 0

    if args.command == "list":
        notes = iter_notes(brain_dir)
        for path, note in notes:
            kind = note.meta.get("type", "?")
            print(f"{kind:7} {path.stem:40} {note.title[:60]}")
        print(f"{len(notes)} notes in {brain_dir}")
        return 0

    build_parser().print_help()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
