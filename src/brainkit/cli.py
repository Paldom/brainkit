"""brainkit CLI: build a brain from researchkit projects and query it.

    brainkit ingest <researchkit-project-dir> [--brain DIR]
    brainkit search "query" [--brain DIR] [-n N]
    brainkit index [--brain DIR]
    brainkit list [--brain DIR]

The brain directory defaults to ``$BRAINKIT_DIR`` or ``./brain``.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from brainkit.brain import _iter_notes as iter_notes
from brainkit.brain import build_index, ingest_research_project, search


def _default_brain() -> str:
    return os.environ.get("BRAINKIT_DIR", "brain")


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
    sub = parser.add_subparsers(dest="command")

    ingest = sub.add_parser(
        "ingest", help="Ingest a researchkit project (result.json + materials/)"
    )
    ingest.add_argument("project", help="Path to the researchkit project folder")

    query = sub.add_parser("search", help="Search the brain; hits cite their sources")
    query.add_argument("query", help="Search terms")
    query.add_argument(
        "-n", "--limit", type=int, default=5, help="Max hits (default 5)"
    )

    sub.add_parser("index", help="Regenerate index.md")
    sub.add_parser("list", help="List notes in the brain")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    brain_dir = Path(args.brain)

    if args.command == "ingest":
        project_dir = Path(args.project)
        try:
            report = ingest_research_project(project_dir, brain_dir)
        except (FileNotFoundError, ValueError) as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        print(
            f"Ingested {report.topic!r}: topic note + {len(report.source_notes)} "
            f"source notes ({report.skipped_sources} skipped) -> {brain_dir}"
        )
        return 0

    if args.command == "search":
        hits = search(brain_dir, args.query, limit=args.limit)
        if not hits:
            print("No matches.")
            return 1
        for hit in hits:
            citation = f" <{hit.url}>" if hit.url else f" (research run: {hit.project})"
            print(f"[{hit.score}] {hit.title}{citation}")
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
