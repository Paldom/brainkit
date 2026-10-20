"""read, sections, context packs, query variants, the token cache."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from brainkit.brain import (
    _CACHE_FILE,
    Corpus,
    best_section,
    context_pack,
    ingest_research_project,
    read_note,
    search,
    search_fused,
    sections,
)
from brainkit.cli import main

BODY = """Intro paragraph about zebras.

## Findings

Zebra stripes deter biting flies.

### Cost

Stripes cost nothing extra.

```
## not a heading inside a fence
```

## Open questions

Why do zebras stand in lines?
"""


@pytest.fixture
def brain(tmp_path: Path) -> Path:
    project = tmp_path / "run"
    (project / "materials").mkdir(parents=True)
    (project / "result.json").write_text(
        json.dumps({"topic": "zebra research", "meta_summary": "Zebras, summarised."})
    )
    (project / "materials" / "001.md").write_text(
        '---\ntitle: "Stripes"\nurl: https://z.test\n---\n\n' + BODY
    )
    (project / "materials" / "002.md").write_text(
        '---\ntitle: "Lions"\nurl: https://l.test\n---\n\n'
        + "Lions hunt zebras at dawn. " * 40
    )
    brain = tmp_path / "brain"
    ingest_research_project(project, brain)
    return brain


def _source(brain: Path, title: str) -> str:
    return next(h.slug for h in search(brain, title, limit=10) if h.title == title)


def test_sections_ignore_fenced_headings() -> None:
    paths = [s.path for s in sections(BODY)]
    assert paths == [(), ("Findings",), ("Findings", "Cost"), ("Open questions",)]


def test_best_section_is_the_enclosing_one() -> None:
    path, text = best_section(BODY, ["flies"])
    assert path == ("Findings",) and "biting flies" in text


def test_hits_carry_their_section(brain: Path) -> None:
    hit = next(h for h in search(brain, "stripes cost") if h.title == "Stripes")
    assert hit.section == ("Findings", "Cost")
    assert "cost nothing" in hit.excerpt


class TestRead:
    def test_levels(self, brain: Path) -> None:
        slug = _source(brain, "Stripes")
        assert read_note(brain, slug, level="abstract")["content"]
        outline = str(read_note(brain, slug, level="outline")["content"])
        assert "- Findings\n  - Cost" in outline
        full = read_note(brain, slug)
        assert "Why do zebras" in str(full["content"])
        assert full["tokens_estimate"] == (int(str(full["chars"])) + 3) // 4

    def test_section(self, brain: Path) -> None:
        slug = _source(brain, "Stripes")
        record = read_note(brain, slug, section="findings > cost")
        assert str(record["content"]).startswith("Stripes cost nothing extra.")
        assert record["section"] == ["Findings", "Cost"]

    def test_missing_section_lists_the_outline(self, brain: Path) -> None:
        with pytest.raises(KeyError, match="Open questions"):
            read_note(brain, _source(brain, "Stripes"), section="Nope")

    def test_cli(self, brain: Path, capsys: pytest.CaptureFixture[str]) -> None:
        slug = _source(brain, "Stripes")
        assert main(["--brain", str(brain), "read", slug, "--level", "outline"]) == 0
        assert "Findings" in capsys.readouterr().out
        assert main(["--brain", str(brain), "read", slug, "--json"]) == 0
        assert json.loads(capsys.readouterr().out)["id"] == slug
        assert main(["--brain", str(brain), "read", "missing", "--json"]) == 1
        assert "error" in json.loads(capsys.readouterr().out)


class TestPack:
    def test_budget_is_a_hard_bound(self, brain: Path) -> None:
        for budget in (50, 300, 5000):
            packed = context_pack(brain, "zebras", budget)
            assert int(str(packed["used_chars"])) <= budget

    def test_whole_units_and_omissions(self, brain: Path) -> None:
        packed = context_pack(brain, "zebras stripes lions", 400)
        items = packed["pack"]
        assert isinstance(items, list) and items
        assert all(i["unit"] in ("note", "section") for i in items)
        assert not any(i["truncated"] for i in items[1:])  # only #1 may be cut
        assert packed["omitted"] or int(str(packed["used_chars"])) <= 400

    def test_paging(self, brain: Path) -> None:
        first = context_pack(brain, "zebras", 200, limit=3)
        seen = first["next_exclude"]
        assert isinstance(seen, list)
        second = context_pack(brain, "zebras", 200, limit=3, exclude=seen)
        items = second["pack"]
        assert isinstance(items, list)
        ids = {i["id"] for i in items}
        assert not ids & set(seen)

    def test_cli(self, brain: Path, capsys: pytest.CaptureFixture[str]) -> None:
        assert (
            main(["--brain", str(brain), "context", "zebras", "--budget", "300"]) == 0
        )
        out = capsys.readouterr().out
        assert "chars (≈" in out and "## [" in out
        argv = ["--brain", str(brain), "context", "zebras", "--budget", "50", "--json"]
        assert main(argv) == 0
        assert json.loads(capsys.readouterr().out)["budget_chars"] == 50


class TestVariants:
    def test_original_query_dominates(self, brain: Path) -> None:
        plain = search(brain, "biting flies", limit=1)
        fused = search_fused(brain, "biting flies", ["lion hunting dawn"], limit=3)
        assert fused[0].slug == plain[0].slug

    def test_variant_adds_recall(self, brain: Path) -> None:
        fused = search_fused(brain, "predators morning", ["lions hunt dawn"], limit=5)
        assert any(h.title == "Lions" for h in fused)
        assert all(h.channel == "fused" for h in fused)

    def test_cli(self, brain: Path, capsys: pytest.CaptureFixture[str]) -> None:
        argv = ["--brain", str(brain), "search", "predators", "--also", "lions"]
        main(argv)
        assert "Lions" in capsys.readouterr().out


class TestTokenCache:
    def test_cache_written_by_writers_only(self, brain: Path, tmp_path: Path) -> None:
        cache = brain / _CACHE_FILE
        assert cache.is_file()
        before = cache.read_bytes()
        search(brain, "zebras")
        assert cache.read_bytes() == before

    def test_cached_equals_uncached(self, brain: Path) -> None:
        cached = [h.slug for h in search(brain, "zebra stripes", limit=10)]
        (brain / _CACHE_FILE).unlink()
        assert [h.slug for h in search(brain, "zebra stripes", limit=10)] == cached

    def test_stale_or_corrupt_cache_is_ignored(self, brain: Path) -> None:
        expected = [h.slug for h in search(brain, "zebra", limit=10)]
        (brain / _CACHE_FILE).write_text("{not json")
        assert [h.slug for h in search(brain, "zebra", limit=10)] == expected
        (brain / _CACHE_FILE).write_text(json.dumps({"key": "old", "entries": {}}))
        assert [h.slug for h in search(brain, "zebra", limit=10)] == expected

    def test_edited_note_is_retokenized(self, brain: Path) -> None:
        slug = _source(brain, "Lions")
        path = Corpus(brain).by_slug[slug][0]
        path.write_text(path.read_text() + "\nKangaroo addendum.\n")
        assert any(h.slug == slug for h in search(brain, "kangaroo"))
