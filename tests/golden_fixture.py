"""A small boosted research run exercising the source-merge paths.

Shared by the golden test and the script that produced its expected bytes
from v0.2.0, so the two can never build different inputs.
"""

from __future__ import annotations

import json
from pathlib import Path


def _material(title: str, url: str, body: str, **extra: str) -> str:
    lines = [f"title: {title}", f"url: {url}", "source_type: web", "providers: exa"]
    lines += [f"{key}: {value}" for key, value in extra.items()]
    return "---\n" + "\n".join(lines) + f"\n---\n\n{body}\n"


def build(root: Path) -> Path:
    parent = root / "20260901_golden"
    (parent / "subprojects").mkdir(parents=True)
    (parent / "result.json").write_text(
        json.dumps(
            {
                "overarching_topic": "golden domain",
                "super_summary": "The domain summary sentence for the golden run.",
                "keywords": ["alpha", "beta"],
            }
        ),
        encoding="utf-8",
    )
    shared_long = "A long shared archive body. " * 20
    subs = {
        "sub_01_first": {
            "001-shared.md": _material(
                "Shared: first capture",
                "https://shared.test/a",
                shared_long,
                published="2026-01-02",
                content_digest="aaa111",
                final_url="https://shared.test/a?x=1",
            ),
            "002-only.md": _material(
                "Only first", "https://first.test/b", "First only body text."
            ),
        },
        "sub_02_second": {
            "001-shared.md": _material(
                "Shared: second, shorter capture",
                "https://shared.test/a",
                "Short capture.",
                content_digest="bbb222",
                content_kind="article",
            ),
            "002-social.md": _material(
                "A post", "https://social.test/p", "Social words here."
            ).replace("source_type: web", "source_type: social"),
        },
    }
    for name, materials in subs.items():
        sub = parent / "subprojects" / name
        (sub / "materials").mkdir(parents=True)
        (sub / "result.json").write_text(
            json.dumps(
                {"topic": f"topic of {name}", "meta_summary": f"Summary of {name}."}
            ),
            encoding="utf-8",
        )
        (sub / "report.md").write_text(
            "# Report\n\n## Executive Summary\n\nThe executive summary of "
            f"{name} says useful things.\n\n## Raw Provider Outputs\n\nignored\n",
            encoding="utf-8",
        )
        for filename, text in materials.items():
            (sub / "materials" / filename).write_text(text, encoding="utf-8")
    return parent


def normalized(brain: Path) -> dict[str, str]:
    """Source and report notes, minus the generation stamp."""
    out: dict[str, str] = {}
    for level in ("sources", "reports"):
        for path in sorted((brain / "notes" / level).glob("*.md")):
            if path.name == "index.md":
                continue
            lines = path.read_text(encoding="utf-8").splitlines()
            out[f"{level}/{path.name}"] = "\n".join(
                line for line in lines if not line.startswith("generated:")
            )
    return out
