"""Rebuild the pinned eval corpus from two real researchkit runs.

Run once, by hand, from the repo root; the output under tests/eval/corpus/ is
committed so the eval never depends on the (gitignored) original runs:

    uv run python tests/eval/build_corpus.py .local/research/<august-run> \\
        .local/research-202610/<october-run>

Each sub-project keeps its first PER_SUB fetched materials (manifest order),
bodies trimmed to BODY_CHARS; report.md keeps only the analysis band (what
ingest reads). The October run is the one whose synthesis failed upstream —
kept on purpose, it is part of what the eval must handle.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

PER_SUB = 25
BODY_CHARS = 6000
STOP = ("## Keyword-based Site Research", "## Provider Summaries", "## Raw Provider")
KEEP_KEYS = (
    "topic",
    "overarching_topic",
    "meta_summary",
    "super_summary",
    "keywords",
    "synthesized_keywords",
)
OUT = Path(__file__).parent / "corpus"


def trim_report(text: str) -> str:
    cut = min((text.find(stop) for stop in STOP if stop in text), default=len(text))
    return text[:cut].rstrip() + "\n"


def copy_run(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True)
    result = json.loads((src / "result.json").read_text(encoding="utf-8"))
    kept = {k: result[k] for k in KEEP_KEYS if k in result}
    (dst / "result.json").write_text(
        json.dumps(kept, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if (src / "report.md").is_file():
        report = trim_report((src / "report.md").read_text(encoding="utf-8"))
        (dst / "report.md").write_text(report, encoding="utf-8")
    materials = src / "materials"
    if materials.is_dir():
        manifest = json.loads((materials / "index.json").read_text(encoding="utf-8"))
        entries = [e for e in manifest["entries"] if e.get("status") == "fetched"]
        entries = entries[:PER_SUB]
        (dst / "materials").mkdir()
        for entry in entries:
            text = (materials / entry["file"]).read_text(
                encoding="utf-8", errors="replace"
            )
            head, sep, body = text.partition("\n---\n")
            (dst / "materials" / entry["file"]).write_text(
                head + sep + body[:BODY_CHARS], encoding="utf-8"
            )
        manifest["entries"] = entries
        (dst / "materials" / "index.json").write_text(
            json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    subs = src / "subprojects"
    if subs.is_dir():
        for child in sorted(p for p in subs.iterdir() if (p / "result.json").is_file()):
            copy_run(child, dst / "subprojects" / child.name)


def main(runs: list[str]) -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    for run in runs:
        src = Path(run)
        copy_run(src, OUT / src.name)


if __name__ == "__main__":
    main(sys.argv[1:])
