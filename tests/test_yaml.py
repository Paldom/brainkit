"""Frontmatter must be parseable YAML (OKF v0.2 §11.1).

Before the emitter encoded values, 46% of a real brain's notes failed
``yaml.safe_load`` — every one of them a title containing ``": "``. brainkit's
own reader partitions on the first colon and so never noticed; every external
consumer (Obsidian, an OKF validator, another agent's parser) did.

Values are written as JSON, which is a subset of YAML 1.2. Quoting "only when
necessary" was tried and rejected: it produces valid YAML but silently
*retypes* values, and which values it retypes differs between YAML 1.1 and 1.2
consumers. :data:`RETYPED_WHEN_PLAIN` is the evidence.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from brainkit import _unquote, parse_note
from brainkit.brain import (
    _frontmatter,
    _yaml_value,
    ingest_notes,
    ingest_research_project,
)

# Titles that broke the real brain, plus the scalar shapes YAML treats as
# syntax rather than text.
NASTY = [
    "Docker Security: A Practical Guide",
    "GLM-5.2: Built for Long-Horizon Tasks",
    "Me at 3AM vibecoding with Claude Code : vibecoding",
    "- leading dash",
    "? leading question mark",
    ": leading colon",
    "[bracketed]",
    "{braced}",
    "#hashtag first",
    "&anchor",
    "*alias",
    "!tag",
    "|literal",
    ">folded",
    "'single quoted'",
    '"double quoted"',
    "%directive",
    "@reserved",
    "`backtick",
    "trailing colon:",
    "hash # comment",
    "true",
    "FALSE",
    "Null",
    "~",
    "yes",
    "off",
    "",
    "   ",
    'back\\slash and "quote"',
    "control\x00char",
    "Crème Brûlée — em dash, ünicode",
]

# Values a "quote only when needed" emitter would leave plain, and that YAML
# then loads as something other than a string. This is why the emitter quotes
# unconditionally instead of maintaining a list of dangerous shapes.
RETYPED_WHEN_PLAIN = [
    "007",
    "1:30",
    "0x1F",
    ".inf",
    ".nan",
    "2026-01-01",
    "1_000",
    "+.INF",
    "12:00:00",
]


class TestValueEncoding:
    @pytest.mark.parametrize("value", NASTY + RETYPED_WHEN_PLAIN)
    def test_round_trips_exactly(self, value: str) -> None:
        # whitespace is collapsed on write; nothing else is touched
        expected = " ".join(value.split())
        assert _unquote(_yaml_value(value)) == expected

    @pytest.mark.parametrize("value", RETYPED_WHEN_PLAIN)
    def test_dangerous_shapes_stay_strings(self, value: str) -> None:
        yaml = pytest.importorskip("yaml")
        loaded = yaml.safe_load(f"title: {_yaml_value(value)}")["title"]
        assert isinstance(loaded, str), f"{value!r} was retyped to {type(loaded)}"
        assert loaded == value

    def test_structure_survives_as_structure(self) -> None:
        """OKF consumers read ``tags`` as a list — it must not be stringified."""
        yaml = pytest.importorskip("yaml")
        block = _frontmatter(
            {
                "title": "Security: hard",
                "tags": ["ai", "agent memory"],
                "generated": {"by": "brainkit/0.1.0", "at": "2026-08-29T00:00:00Z"},
                "source_count": 25,
            }
        )
        meta = yaml.safe_load(block.removeprefix("---\n").removesuffix("\n---"))
        assert meta["tags"] == ["ai", "agent memory"]
        assert meta["generated"]["by"] == "brainkit/0.1.0"
        assert meta["source_count"] == 25  # a count is a number, not "25"
        assert meta["title"] == "Security: hard"

    @given(st.text())
    def test_any_text_round_trips_after_collapse(self, value: str) -> None:
        collapsed = " ".join(value.split())
        assert _unquote(_yaml_value(collapsed)) == collapsed

    @given(st.text())
    def test_encoding_is_always_one_line(self, value: str) -> None:
        assert "\n" not in _yaml_value(value)


class TestUnquote:
    def test_legacy_plain_scalars_pass_through(self) -> None:
        """Frontmatter brainkit did not write still reads, unchanged."""
        assert _unquote("plain title") == "plain title"
        assert _unquote("https://example.com/a:b") == "https://example.com/a:b"
        assert _unquote('"unbalanced') == '"unbalanced'
        assert _unquote("") == ""

    def test_non_string_json_keeps_its_raw_text(self) -> None:
        # Note.meta is a flat string mapping; a list is handed back verbatim
        # so a caller can json.loads it, rather than stringified into a lie.
        assert _unquote('["a", "b"]') == '["a", "b"]'
        assert _unquote("25") == "25"
        assert _unquote("true") == "true"

    def test_decodes_what_the_emitter_writes(self) -> None:
        for value in ("a\nb", 'q"uote', "back\\slash", "Crème"):
            assert _unquote(json.dumps(value, ensure_ascii=False)) == value


class TestBrainOutputParsesAsYaml:
    """End-to-end: every note a real ingest writes must survive a YAML parse."""

    def _brain_with_nasty_titles(self, tmp_path: Path) -> Path:
        project = tmp_path / "20260705_run"
        (project / "materials").mkdir(parents=True)
        (project / "result.json").write_text(
            json.dumps({"topic": "Security: hard mode", "meta_summary": "sum"}),
            encoding="utf-8",
        )
        (project / "report.md").write_text(
            "intro that is long enough to survive the stub filter\n\n"
            "## Findings: the good ones\n\n" + "body text " * 20,
            encoding="utf-8",
        )
        for i, title in enumerate(NASTY + RETYPED_WHEN_PLAIN):
            (project / "materials" / f"{i:03d}-m.md").write_text(
                f"---\ntitle: {json.dumps(title)}\n"
                f"url: https://example.test/{i}\n---\n\nbody {i}\n",
                encoding="utf-8",
            )
        brain = tmp_path / "brain"
        ingest_research_project(project, brain)
        loose = tmp_path / "loose.md"
        loose.write_text(
            "---\ntitle: Imported: a note\nproject: manual\n---\n\nfree text\n",
            encoding="utf-8",
        )
        ingest_notes(loose, brain)
        return brain

    def test_every_note_is_valid_yaml_with_a_type(self, tmp_path: Path) -> None:
        yaml = pytest.importorskip("yaml")
        brain = self._brain_with_nasty_titles(tmp_path)
        notes = sorted(brain.rglob("*.md"))
        assert len(notes) > len(NASTY)
        checked = 0
        for path in notes:
            text = path.read_text(encoding="utf-8")
            if path.name in ("index.md", "log.md"):
                # OKF §3.1 reserved: directory listings and history, not
                # concepts, so no `type`. §12 allows frontmatter in exactly
                # one of them — the bundle-root index — for the spec version.
                if path == brain / "index.md":
                    block = text[4 : text.find("\n---\n", 3)]
                    assert yaml.safe_load(block) == {"okf_version": "0.2"}
                else:
                    assert not text.startswith("---\n")
                continue
            meta = yaml.safe_load(text[4 : text.find("\n---\n", 3)])
            assert isinstance(meta, dict), path
            assert meta.get("type"), f"{path}: OKF §11.2 requires a non-empty type"
            checked += 1
        assert checked == len(
            [p for p in notes if p.name not in ("index.md", "log.md")]
        )

    def test_titles_survive_the_round_trip(self, tmp_path: Path) -> None:
        brain = self._brain_with_nasty_titles(tmp_path)
        titles = {
            parse_note(p.read_text(encoding="utf-8")).title
            for p in (brain / "notes" / "sources").glob("*.md")
            if p.name != "index.md"
        }
        for value in ("Docker Security: A Practical Guide", "007", "12:00:00", "~"):
            assert value in titles, f"{value!r} did not survive ingest"


class TestHostileInput:
    """Edge cases that would otherwise corrupt a note or abort a whole run."""

    @pytest.mark.parametrize(
        "value",
        [
            "a\u2028b",  # LINE SEPARATOR
            "a\u2029b",  # PARAGRAPH SEPARATOR
            "a\x00b",  # NUL
            "\ufeffheading",  # BOM
            "caf\x9ce",  # C1 mojibake from a mis-decoded page
            "a\x7fb",  # DEL
            "null",
            "true",
            "brain \U0001f9e0 note",
            'he said "no" \\ then left',
            "Re: #1 — a title",
        ],
    )
    def test_hostile_scalars_survive_and_parse(self, value: str) -> None:
        yaml = pytest.importorskip("yaml")
        encoded = _yaml_value(value)
        expected = " ".join(value.split())
        assert _unquote(encoded) == expected
        assert yaml.safe_load(f"k: {encoded}")["k"] == expected

    def test_a_key_needing_quotes_is_quoted(self) -> None:
        """`rebuild` copies keys off existing notes; one bad key must not
        make the whole block unparseable."""
        yaml = pytest.importorskip("yaml")
        block = _frontmatter({"weird: key": "v", "type": "note"})
        meta = yaml.safe_load(block.removeprefix("---\n").removesuffix("\n---"))
        assert meta == {"weird: key": "v", "type": "note"}

    def test_a_mis_encoded_material_does_not_abort_the_run(
        self, tmp_path: Path
    ) -> None:
        """One bad byte used to lose every source in the run."""
        project = tmp_path / "run"
        (project / "materials").mkdir(parents=True)
        (project / "result.json").write_text(
            json.dumps({"topic": "t", "meta_summary": "s"}), encoding="utf-8"
        )
        (project / "materials" / "001-ok.md").write_bytes(
            b"---\ntitle: Fine\nurl: https://a.test/1\n---\n\nbody\n"
        )
        (project / "materials" / "002-bad.md").write_bytes(
            b"---\ntitle: Caf\xe9 bad\nurl: https://b.test/2\n---\n\nbody\n"
        )
        brain = tmp_path / "brain"
        report = ingest_research_project(project, brain)

        assert len(report.source_notes) == 2  # the good one is NOT collateral
        assert report.skipped_sources == 0
        assert report.repaired_sources == ["materials/002-bad.md: not valid UTF-8"]
        # and the repaired note is still valid YAML
        yaml = pytest.importorskip("yaml")
        bad = next(p for p in report.source_notes if "bad" in p.stem)
        text = bad.read_text(encoding="utf-8")
        assert yaml.safe_load(text[4 : text.find("\n---\n", 3)])["url"]
