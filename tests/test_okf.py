"""Interop and honesty: OKF links and timestamps, non-English text, docs."""

from __future__ import annotations

import json
import re
import shlex
from pathlib import Path

import pytest
from conftest import notes_in

from brainkit import parse_note, raw_frontmatter
from brainkit.brain import (
    _tokens,
    context,
    ingest_notes,
    ingest_research_project,
    link_graph,
    lint,
    rebuild,
    search,
)
from brainkit.cli import build_parser

REPO = Path(__file__).resolve().parent.parent


def _material(title: str, url: str, body: str) -> str:
    return f"---\ntitle: {json.dumps(title)}\nurl: {url}\n---\n\n{body}\n"


def _project(root: Path, name: str, summary: str, materials: dict[str, str]) -> Path:
    project = root / name
    (project / "materials").mkdir(parents=True)
    (project / "result.json").write_text(
        json.dumps({"topic": f"topic {name}", "meta_summary": summary}),
        encoding="utf-8",
    )
    for filename, content in materials.items():
        (project / "materials" / filename).write_text(content, encoding="utf-8")
    return project


class TestUnicodeTokenizer:
    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("résumé", ["resume"]),
            ("szövegösszefoglaló", ["szovegosszefoglalo"]),
            ("Straße", ["strasse"]),
            ("知识库", ["知", "识", "库", "知识", "识库"]),
            ("東京", ["東", "京", "東京"]),
            ("中", ["中"]),
            ("한국어", ["한", "국", "어", "한국", "국어"]),
            ("किताब", ["किताब"]),
            ("مُحَمَّد", ["محمد"]),
        ],
    )
    def test_folds_and_segments(self, text: str, expected: list[str]) -> None:
        assert _tokens(text) == expected

    def test_identifiers_are_indexed_whole_and_in_parts(self) -> None:
        tokens = _tokens("use snake_case and kebab-case")
        assert {"snake", "case", "kebab", "snake_case", "kebab-case"} <= set(tokens)

    def test_mixed_cjk_and_latin(self) -> None:
        assert _tokens("API设计") == ["api", "设", "计", "设计"]

    @pytest.mark.parametrize(
        ("query", "needle"),
        [
            ("szövegösszefoglaló", "hungarian"),
            ("szovegosszefoglalo", "hungarian"),  # typed without accents
            ("Gedächtnis", "german"),
            ("知识库", "chinese"),
            ("ナレッジ", "japanese"),
        ],
    )
    def test_non_english_known_item_retrieval(
        self, tmp_path: Path, query: str, needle: str
    ) -> None:
        materials = {
            "001-hu.md": _material(
                "hungarian", "https://hu.test", "A szövegösszefoglaló modell."
            ),
            "002-de.md": _material(
                "german", "https://de.test", "Das Gedächtnis eines Agenten."
            ),
            "003-zh.md": _material("chinese", "https://zh.test", "个人知识库的设计。"),
            "004-ja.md": _material(
                "japanese", "https://ja.test", "ナレッジベースの設計について。"
            ),
            "005-en.md": _material("english", "https://en.test", "Plain English."),
        }
        brain = tmp_path / "brain"
        ingest_research_project(_project(tmp_path, "run", "s", materials), brain)
        hits = search(brain, query)
        assert hits and hits[0].title == needle


class TestMarkdownLinks:
    def _brain(self, tmp_path: Path) -> tuple[Path, Path]:
        brain = tmp_path / "brain"
        report = ingest_research_project(
            _project(
                tmp_path,
                "run",
                "A summary.",
                {"001-a.md": _material("A [bracketed] title", "https://a.test", "b")},
            ),
            brain,
        )
        return brain, report.topic_note

    def test_node_notes_use_okf_markdown_links(self, tmp_path: Path) -> None:
        brain, topic = self._brain(tmp_path)
        body = parse_note(topic.read_text(encoding="utf-8")).body
        assert "[[" not in body
        assert re.search(r"- \[A \\\[bracketed\\\] title\]\(\.\./sources/", body)
        outgoing, incoming = link_graph(brain)
        (source,) = notes_in(brain / "notes" / "sources")
        assert source.stem in outgoing[topic.stem]
        assert topic.stem in incoming[source.stem]
        assert lint(brain) == []

    def test_dead_markdown_link_is_reported(self, tmp_path: Path) -> None:
        brain, topic = self._brain(tmp_path)
        topic.write_text(
            topic.read_text(encoding="utf-8") + "\n- [gone](../sources/gone.md)\n",
            encoding="utf-8",
        )
        dead = [f.detail for f in lint(brain) if f.check == "dead-link"]
        assert dead == ["(notes/sources/gone.md)"]

    def test_external_links_are_citations_not_edges(self, tmp_path: Path) -> None:
        brain, topic = self._brain(tmp_path)
        topic.write_text(
            topic.read_text(encoding="utf-8")
            + "\nSee [the spec](https://example.com/spec.md).\n",
            encoding="utf-8",
        )
        assert [f for f in lint(brain) if f.check == "dead-link"] == []

    def test_rebuild_migrates_legacy_wikilink_lists(self, tmp_path: Path) -> None:
        brain, topic = self._brain(tmp_path)
        (source,) = notes_in(brain / "notes" / "sources")
        text = topic.read_text(encoding="utf-8")
        legacy = re.sub(
            r"^- \[.*?\]\(\.\./sources/(.+?)\.md\)(.*)$",
            r"- [[\1]] — A legacy title\2",
            text,
            flags=re.MULTILINE,
        )
        legacy += "\n- [[never-existed]] — Dead\n"
        topic.write_text(legacy, encoding="utf-8")
        rebuild(brain)
        body = topic.read_text(encoding="utf-8")
        assert f"- [A legacy title](../sources/{source.name})" in body
        # an unresolvable legacy link is left as written, so lint still sees it
        assert "- [[never-existed]] — Dead" in body
        assert [f.detail for f in lint(brain) if f.check == "dead-link"] == [
            "[[never-existed]]"
        ]


class TestTimestamps:
    def test_date_only_passthrough_is_normalized(self, tmp_path: Path) -> None:
        src = tmp_path / "n.md"
        src.write_text(
            '---\ntitle: "T"\nauthor: "a"\nstale_after: "2027-01-01"\n'
            'verified: [{"by": "human:x", "at": "2026-10-01"}]\n---\nbody\n',
            encoding="utf-8",
        )
        brain = tmp_path / "brain"
        ingest_notes(src, brain)
        (note,) = notes_in(brain / "notes" / "imported")
        raw = dict(raw_frontmatter(note.read_text(encoding="utf-8")))
        assert json.loads(raw["stale_after"]) == "2027-01-01T00:00:00Z"
        assert json.loads(raw["verified"])[0]["at"] == "2026-10-01T00:00:00Z"
        assert not [f for f in lint(brain) if f.check == "date-only-timestamp"]

    def test_legacy_date_only_value_warns(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        imported = brain / "notes" / "imported"
        imported.mkdir(parents=True)
        (imported / "x.md").write_text(
            '---\ntitle: "X"\nslug: "x"\ntype: "note"\nstale_after: "2099-01-01"\n'
            'verified: [{"by": "human:y", "at": "2026-01-01"}]\n---\n\nbody\n',
            encoding="utf-8",
        )
        found = [f for f in lint(brain) if f.check == "date-only-timestamp"]
        assert [f.severity for f in found] == ["warning", "warning"]

    def test_generated_at_carries_an_offset(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        ingest_research_project(
            _project(tmp_path, "r", "s", {"001.md": _material("A", "https://a", "b")}),
            brain,
        )
        for path in (brain / "notes").rglob("*.md"):
            if path.name in ("index.md", "log.md"):
                continue
            generated = json.loads(dict(raw_frontmatter(path.read_text()))["generated"])
            assert re.search(r"T\d\d:\d\d:\d\d(\+00:00|Z)$", generated["at"]), path


class TestCoverage:
    def test_source_only_hits_report_their_runs(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        shared = {"001-a.md": _material("Zygote", "https://z.test", "zygote facts")}
        ingest_research_project(_project(tmp_path, "run1", "s", shared), brain)
        ingest_research_project(_project(tmp_path, "run2", "s", shared), brain)
        hits, coverage = context(brain, "zygote", kind="source")
        assert hits and coverage.runs == ["run1", "run2"]
        assert any("only source archives matched" in s for s in coverage.signals())


def _documented_commands() -> list[str]:
    """Every ``brainkit …`` invocation shown in a fenced block of the docs."""
    commands: list[str] = []
    for doc in (REPO / "README.md", REPO / ".claude/skills/brainkit/SKILL.md"):
        in_fence = False
        for line in doc.read_text(encoding="utf-8").splitlines():
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            text = line.strip()
            if in_fence and re.match(r"(uv run )?brainkit\b", text):
                commands.append(text)
    return commands


@pytest.mark.parametrize("command", _documented_commands())
def test_documented_command_parses(command: str) -> None:
    """Docs cannot drift from the CLI: each example must parse for real."""
    text = command.split("  #", 1)[0].split(" # ", 1)[0]
    text = re.sub(r"<[^>]+>", "x", text)
    argv = shlex.split(text)
    if argv[:2] == ["uv", "run"]:
        argv = argv[2:]
    assert argv[0] == "brainkit"
    try:
        build_parser().parse_args(argv[1:])
    except SystemExit as e:  # argparse reports errors by exiting
        pytest.fail(f"documented command does not parse: {command!r} ({e})")


def test_docs_have_commands() -> None:
    assert len(_documented_commands()) >= 10
