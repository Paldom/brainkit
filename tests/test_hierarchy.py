"""The brain is a pyramid, and re-ingesting it changes nothing.

Two properties this file pins:

* **Levels.** A boosted research run already contains a hierarchy — a parent
  with an ``overarching_topic`` over sub-projects with their own topics — and
  ingest used to flatten it into sibling topic notes. Now the parent is a
  ``domain`` and the children are its ``topic``s, so an agent can descend
  from a map to a synthesis to a source instead of searching blind.
* **Inertness.** Re-ingesting identical input must produce zero diffs. Notes
  carry a ``generated`` timestamp, so this is not automatic; and several
  fields used to oscillate between two archives of the same URL, which meant
  no multi-cited source note was ever byte-stable.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from conftest import notes_in

from brainkit import parse_note
from brainkit.brain import (
    LEVELS,
    _frontmatter,
    _iter_notes,
    _level_prior,
    ancestors,
    build_index,
    context,
    ingest_research_project,
    link_graph,
    lint,
    rebuild,
    search,
)
from brainkit.cli import main


def _material(title: str, url: str, body: str, providers: str = "openai") -> str:
    return (
        f"---\ntitle: {title}\nurl: {url}\nsource_type: web\n"
        f"providers: {providers}\n---\n\n{body}\n"
    )


def _leaf(
    parent: Path,
    name: str,
    topic: str,
    summary: str,
    materials: dict[str, str],
) -> Path:
    project = parent / name
    (project / "materials").mkdir(parents=True)
    (project / "result.json").write_text(
        json.dumps({"topic": topic, "meta_summary": summary}), encoding="utf-8"
    )
    for filename, text in materials.items():
        (project / "materials" / filename).write_text(text, encoding="utf-8")
    return project


def boosted(tmp_path: Path, name: str = "20260828_run") -> Path:
    """A boosted run: a parent over two sub-projects, one source shared."""
    parent = tmp_path / name
    (parent / "subprojects").mkdir(parents=True)
    (parent / "result.json").write_text(
        json.dumps(
            {
                "overarching_topic": "Agent brains, surveyed",
                "super_summary": "Everyone is converging on markdown in git.",
                "keywords": ["agent memory", "okf"],
            }
        ),
        encoding="utf-8",
    )
    shared_a = _material("Shared", "https://s.test/1", "Short capture.", "brave")
    shared_b = _material(
        "Shared (fuller)",
        "https://s.test/1",
        "A much longer capture of the very same page, with more detail.",
        "gemini, kimi",
    )
    _leaf(
        parent / "subprojects",
        "sub_01_inventory",
        "Inventory of systems",
        "## Executive Summary\nMem0, Letta and Zep dominate the inventory.",
        {
            "001-a.md": _material("Doc A", "https://a.test/1", "Body A."),
            "002-s.md": shared_a,
        },
    )
    _leaf(
        parent / "subprojects",
        "sub_02_formats",
        "Portable formats",
        "## Executive Summary\nOKF formalizes the markdown wiki pattern.",
        {
            "001-b.md": _material("Doc B", "https://b.test/2", "Body B."),
            "002-s.md": shared_b,
        },
    )
    return parent


class TestLevels:
    def test_parent_becomes_a_domain_over_its_topics(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        report = ingest_research_project(boosted(tmp_path), brain)

        domain = parse_note(report.topic_note.read_text(encoding="utf-8"))
        assert domain.meta["type"] == "domain"
        assert report.topic_note.parent.name == "domains"
        assert domain.meta["topic_count"] == "2"
        assert domain.meta["description"]  # the run's own super_summary

        # and it links DOWN to each child with an OKF §6.1 markdown link
        assert "## Topics" in domain.body
        for child in report.sub_reports:
            assert f"(../topics/{child.topic_note.name})" in domain.body

    def test_children_point_back_up(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        report = ingest_research_project(boosted(tmp_path), brain)
        for child in report.sub_reports:
            meta = parse_note(child.topic_note.read_text(encoding="utf-8")).meta
            assert meta["type"] == "topic"
            assert meta["parent"] == report.topic_note.stem
            assert child.topic_note.parent.name == "topics"

    def test_a_flat_run_is_still_a_topic(self, tmp_path: Path) -> None:
        """No sub-projects, no domain — the level follows the run's shape."""
        brain = tmp_path / "brain"
        project = _leaf(
            tmp_path,
            "flat",
            "just a topic",
            "summary",
            {"001-a.md": _material("Doc", "https://f.test/1", "Body.")},
        )
        report = ingest_research_project(project, brain)
        assert parse_note(report.topic_note.read_text()).meta["type"] == "topic"
        assert not (brain / "notes" / "domains").exists()

    def test_a_run_that_gains_children_changes_level_once(self, tmp_path: Path) -> None:
        """Re-ingest after boosting must not leave the old topic note behind."""
        brain = tmp_path / "brain"
        parent = boosted(tmp_path)
        # first ingest it as a leaf by hiding its sub-projects
        subs = parent / "subprojects"
        subs.rename(parent / "_subprojects")
        first = ingest_research_project(parent, brain)
        assert first.topic_note.parent.name == "topics"

        (parent / "_subprojects").rename(subs)
        second = ingest_research_project(parent, brain)
        assert second.topic_note.parent.name == "domains"
        assert not first.topic_note.exists()  # no duplicate of the same run
        assert len(notes_in(brain / "notes" / "domains")) == 1

    def test_every_level_gets_its_own_index(self, tmp_path: Path) -> None:
        """OKF §8 progressive disclosure: a listing at each level."""
        brain = tmp_path / "brain"
        ingest_research_project(boosted(tmp_path), brain)
        for level in ("domains", "topics", "sources"):
            index = brain / "notes" / level / "index.md"
            assert index.is_file(), level
            assert not index.read_text().startswith("---")  # §8: no frontmatter

    def test_root_index_is_a_map_not_a_listing(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        ingest_research_project(boosted(tmp_path), brain)
        index = (brain / "index.md").read_text(encoding="utf-8")
        assert 'okf_version: "0.2"' in index  # OKF §12
        assert "## Domains" in index and "## Topics" in index
        # the bulk levels are linked, never inlined
        assert "https://a.test/1" not in index
        assert "notes/sources/index.md" in index

    def test_index_links_resolve_from_the_file_that_holds_them(
        self, tmp_path: Path
    ) -> None:
        brain = tmp_path / "brain"
        ingest_research_project(boosted(tmp_path), brain)
        for index in brain.rglob("index.md"):
            for line in index.read_text(encoding="utf-8").splitlines():
                if not line.startswith("* ["):
                    continue
                target = line.split("](", 1)[1].split(")", 1)[0]
                assert (index.parent / target).exists(), f"{index}: {target}"


class TestInertness:
    def _ingest_twice(self, tmp_path: Path) -> tuple[dict[Path, str], dict[Path, str]]:
        brain = tmp_path / "brain"
        project = boosted(tmp_path)
        ingest_research_project(project, brain)
        before = {
            p.relative_to(brain): p.read_text(encoding="utf-8")
            for p in sorted((brain / "notes").rglob("*.md"))
        }
        ingest_research_project(project, brain)
        after = {
            p.relative_to(brain): p.read_text(encoding="utf-8")
            for p in sorted((brain / "notes").rglob("*.md"))
        }
        return before, after

    def test_reingest_changes_no_note_byte(self, tmp_path: Path) -> None:
        before, after = self._ingest_twice(tmp_path)
        assert before.keys() == after.keys()
        changed = [str(k) for k in before if before[k] != after[k]]
        assert changed == []

    def test_shared_source_does_not_oscillate(self, tmp_path: Path) -> None:
        """Two archives of one URL: the fuller one wins, deterministically."""
        brain = tmp_path / "brain"
        ingest_research_project(boosted(tmp_path), brain)
        shared = [
            p
            for p in notes_in(brain / "notes" / "sources")
            if parse_note(p.read_text()).meta["url"] == "https://s.test/1"
        ]
        assert len(shared) == 1
        note = parse_note(shared[0].read_text(encoding="utf-8"))
        assert "much longer capture" in note.body  # the richer archive
        assert note.meta["title"] == "Shared (fuller)"
        # provenance from BOTH archives is kept, not overwritten
        assert json.loads(note.meta["providers"]) == ["brave", "gemini", "kimi"]
        assert len(json.loads(note.meta["projects"])) == 2
        assert note.meta["corroboration"] == "2"

    def test_topics_with_commas_survive_a_reingest(self, tmp_path: Path) -> None:
        """A researchkit topic is a sentence; it must not be comma-split."""
        brain = tmp_path / "brain"
        topic = "Formats: OKF, AGENTS.md, and llms.txt — what actually works"
        project = _leaf(
            tmp_path,
            "run",
            topic,
            "s",
            {"001-a.md": _material("Doc", "https://c.test/1", "Body.")},
        )
        ingest_research_project(project, brain)
        ingest_research_project(project, brain)
        note = parse_note(notes_in(brain / "notes" / "sources")[0].read_text())
        assert json.loads(note.meta["topics"]) == [topic]

    def test_rebuilding_the_index_does_not_dirty_the_tree(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        ingest_research_project(boosted(tmp_path), brain)
        index = brain / "index.md"
        before = index.read_text(encoding="utf-8")
        build_index(brain)
        assert index.read_text(encoding="utf-8") == before


class TestRanking:
    def test_level_prior_is_ordered_and_bounded(self) -> None:
        priors = {kind: _level_prior(kind) for kind in LEVELS}
        assert priors["source"] == pytest.approx(1.0)
        assert priors["domain"] == pytest.approx(2.0)  # the single knob
        assert priors["source"] < priors["report"] < priors["topic"]
        assert priors["topic"] < priors["domain"]
        assert _level_prior("something-unknown") == pytest.approx(1.0)

    def test_synthesis_outranks_the_source_it_summarizes(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        ingest_research_project(boosted(tmp_path), brain)
        hits = search(brain, "markdown git converging")
        assert hits and hits[0].kind == "domain"

    def test_generated_link_lists_do_not_score(self, tmp_path: Path) -> None:
        """A domain note must not inherit its children's whole vocabulary."""
        brain = tmp_path / "brain"
        ingest_research_project(boosted(tmp_path), brain)
        # "Doc A" appears ONLY in a source title and in generated link lists
        hits = search(brain, "Doc A")
        assert hits
        assert hits[0].kind == "source"
        assert hits[0].url == "https://a.test/1"

    def test_long_source_does_not_beat_short_synthesis(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        project = _leaf(
            tmp_path,
            "run",
            "vector search tradeoffs",
            "Vector search is insufficient alone.",
            {
                "001-chatty.md": _material(
                    "Chatty forum thread",
                    "https://chat.test/1",
                    "vector " * 400 + "off-topic rambling " * 200,
                )
            },
        )
        ingest_research_project(project, brain)
        hits = search(brain, "vector")
        # BM25 saturation + length normalization: 400 repeats is not 400x
        assert hits[0].kind == "topic", [(h.kind, round(h.score, 2)) for h in hits]

    def test_hits_carry_their_place_in_the_pyramid(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        ingest_research_project(boosted(tmp_path), brain)
        hits = search(brain, "inventory systems", kind="topic")
        assert hits
        assert hits[0].kind == "topic"
        assert hits[0].parent  # the domain it descends from


class TestLint:
    def test_a_healthy_brain_is_clean(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        ingest_research_project(boosted(tmp_path), brain)
        assert lint(brain) == []

    def test_report_sections_are_reachable(self, tmp_path: Path) -> None:
        """Reports used to be orphans: nothing linked to them at all."""
        brain = tmp_path / "brain"
        project = _leaf(
            tmp_path,
            "run",
            "topic",
            "summary",
            {"001-a.md": _material("Doc", "https://r.test/1", "Body.")},
        )
        (project / "report.md").write_text(
            "## Findings\n\n" + "real analysis prose. " * 10, encoding="utf-8"
        )
        report = ingest_research_project(project, brain)
        assert report.report_notes
        body = report.topic_note.read_text(encoding="utf-8")
        assert "## Report sections" in body
        for note in report.report_notes:
            assert f"(../reports/{note.name})" in body
        assert [f for f in lint(brain) if f.check == "unreachable"] == []

    def test_dead_links_are_found(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        report = ingest_research_project(boosted(tmp_path), brain)
        note = report.topic_note
        note.write_text(
            note.read_text(encoding="utf-8") + "\n- [[nowhere-at-all]]\n",
            encoding="utf-8",
        )
        checks = [f for f in lint(brain) if f.check == "dead-link"]
        assert [f.detail for f in checks] == ["[[nowhere-at-all]]"]

    def test_quoted_wikilinks_in_scraped_pages_are_not_links(
        self, tmp_path: Path
    ) -> None:
        """An article ABOUT wikis is not a note WITH links."""
        brain = tmp_path / "brain"
        project = _leaf(
            tmp_path,
            "run",
            "topic",
            "summary",
            {
                "001-a.md": _material(
                    "Wiki syntax explained",
                    "https://w.test/1",
                    "Write [[note-name]] to link. See also [[another-note]].",
                )
            },
        )
        ingest_research_project(project, brain)
        assert [f for f in lint(brain) if f.check == "dead-link"] == []

    def test_stale_and_drifted_notes_are_reported(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        ingest_research_project(boosted(tmp_path), brain)
        source = notes_in(brain / "notes" / "sources")[0]
        text = source.read_text(encoding="utf-8")
        text = text.replace(
            '"type": "source"'.replace('"type": ', "type: "),
            "type: " + json.dumps("source"),
        ).replace("---\n", '---\nstale_after: "2020-01-01T00:00:00Z"\n', 1)
        text = text.replace("corroboration: 1", "corroboration: 99")
        source.write_text(text, encoding="utf-8")
        checks = {f.check for f in lint(brain)}
        assert "stale" in checks
        assert "corroboration-drift" in checks

    def test_duplicate_urls_are_reported(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        ingest_research_project(boosted(tmp_path), brain)
        source = notes_in(brain / "notes" / "sources")[0]
        clone = source.with_name("clone.md")
        clone.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        assert any(f.check == "duplicate-url" for f in lint(brain))

    def test_untyped_notes_are_reported(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        ingest_research_project(boosted(tmp_path), brain)
        (brain / "notes" / "imported").mkdir(parents=True, exist_ok=True)
        (brain / "notes" / "imported" / "bare.md").write_text(
            "no frontmatter here\n", encoding="utf-8"
        )
        (brain / "notes" / "imported" / "odd.md").write_text(
            '---\ntype: "spaceship"\n---\n\nbody\n', encoding="utf-8"
        )
        checks = {f.check for f in lint(brain)}
        assert "no-frontmatter" in checks
        assert "unknown-type" in checks

    def test_rebuild_rewrites_legacy_frontmatter_only(self, tmp_path: Path) -> None:
        """The migration path for brains written before values were encoded."""
        brain = tmp_path / "brain"
        ingest_research_project(boosted(tmp_path), brain)
        source = notes_in(brain / "notes" / "sources")[0]
        legacy = (
            "---\ntitle: Docker Security: A Practical Guide\n"
            "slug: legacy\ntype: source\nurl: https://legacy.test/1\n"
            'projects: ["p1", "p2"]\ncorroboration: 7\n---\n\nLegacy body.\n'
        )
        source.write_text(legacy, encoding="utf-8")

        changed = rebuild(brain).changed
        assert source in changed
        note = parse_note(source.read_text(encoding="utf-8"))
        assert note.meta["title"] == "Docker Security: A Practical Guide"
        assert note.meta["corroboration"] == "2"  # re-derived from projects
        assert note.body.strip() == "Legacy body."  # knowledge untouched

        yaml = pytest.importorskip("yaml")
        text = source.read_text(encoding="utf-8")
        assert yaml.safe_load(text[4 : text.find("\n---\n", 3)])["title"]

    def test_rebuild_is_idempotent(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        ingest_research_project(boosted(tmp_path), brain)
        assert rebuild(brain).changed == []  # nothing to do on a current brain

    def test_oversized_root_index_is_flagged(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        ingest_research_project(boosted(tmp_path), brain)
        index = brain / "index.md"
        index.write_text(index.read_text() + "x" * 9000, encoding="utf-8")
        assert any(f.check == "index-too-big" for f in lint(brain))

    def test_cli_lint_exit_codes(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        brain = tmp_path / "brain"
        report = ingest_research_project(boosted(tmp_path), brain)
        assert main(["--brain", str(brain), "lint"]) == 0
        assert "0 findings" in capsys.readouterr().out

        report.topic_note.write_text(
            report.topic_note.read_text(encoding="utf-8") + "\n- [[gone]]\n",
            encoding="utf-8",
        )
        assert main(["--brain", str(brain), "lint"]) == 1
        out = capsys.readouterr().out
        assert "dead-link" in out and "1 findings" in out

    def test_cli_rebuild_is_separate_and_read_write(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """lint stays read-only; rebuild is the verb that may write."""
        brain = tmp_path / "brain"
        ingest_research_project(boosted(tmp_path), brain)
        assert main(["--brain", str(brain), "rebuild"]) == 0
        assert "0 notes rewritten" in capsys.readouterr().out

    def test_stale_is_advisory_not_a_gate_failure(self, tmp_path: Path) -> None:
        """A fact going stale must not turn CI red without a commit."""
        brain = tmp_path / "brain"
        ingest_research_project(boosted(tmp_path), brain)
        source = notes_in(brain / "notes" / "sources")[0]
        source.write_text(
            source.read_text(encoding="utf-8").replace(
                "---\n", '---\nstale_after: "2020-01-01T00:00:00Z"\n', 1
            ),
            encoding="utf-8",
        )
        findings = lint(brain)
        stale = [f for f in findings if f.check == "stale"]
        assert stale and stale[0].severity == "warning"
        assert main(["--brain", str(brain), "lint"]) == 0
        assert main(["--brain", str(brain), "lint", "--warnings-as-errors"]) == 1

    def test_as_of_pins_the_staleness_clock(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        ingest_research_project(boosted(tmp_path), brain)
        source = notes_in(brain / "notes" / "sources")[0]
        source.write_text(
            source.read_text(encoding="utf-8").replace(
                "---\n", '---\nstale_after: "2030-06-01T00:00:00Z"\n', 1
            ),
            encoding="utf-8",
        )
        assert not [f for f in lint(brain, as_of="2029-01-01") if f.check == "stale"]
        assert [f for f in lint(brain, as_of="2031-01-01") if f.check == "stale"]

    def test_a_stale_index_is_reported(self, tmp_path: Path) -> None:
        """Regenerate and compare: a map of a place that changed is worse than none."""
        brain = tmp_path / "brain"
        ingest_research_project(boosted(tmp_path), brain)
        assert not [f for f in lint(brain) if f.check == "index-stale"]
        notes_in(brain / "notes" / "sources")[0].unlink()
        assert [f for f in lint(brain) if f.check == "index-stale"]

    def test_bad_dates_are_reported(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        ingest_research_project(boosted(tmp_path), brain)
        source = notes_in(brain / "notes" / "sources")[0]
        source.write_text(
            source.read_text(encoding="utf-8").replace(
                "---\n", '---\npublished: "2026-13-45"\n', 1
            ),
            encoding="utf-8",
        )
        assert [f for f in lint(brain) if f.check == "bad-date"]

    def test_unreachable_notes_are_reported(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        report = ingest_research_project(boosted(tmp_path), brain)
        # drop a source's citation from its topic note; the note is now
        # findable only by search, which is what the check exists to catch
        child = report.sub_reports[0].topic_note
        body = child.read_text(encoding="utf-8")
        orphaned = report.sub_reports[0].source_notes[0].stem
        lines = [line for line in body.splitlines() if f"/{orphaned}.md)" not in line]
        child.write_text("\n".join(lines) + "\n", "utf-8")
        findings = [f for f in lint(brain) if f.check == "unreachable"]
        assert [f.path.stem for f in findings] == [orphaned]


class TestLinkGraph:
    def test_backlinks_resolve(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        report = ingest_research_project(boosted(tmp_path), brain)
        outgoing, incoming = link_graph(brain)
        domain = report.topic_note.stem
        child = report.sub_reports[0].topic_note.stem
        assert child in outgoing[domain]
        assert domain in incoming[child]

    def test_archived_pages_carry_no_edges(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        ingest_research_project(boosted(tmp_path), brain)
        outgoing, _ = link_graph(brain)
        for path, note in _iter_notes(brain):
            if note.meta.get("type") == "source":
                slug = note.meta.get("slug") or path.stem
                assert outgoing[slug] == set()


class TestContext:
    def test_breadcrumbs_trace_the_descent(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        report = ingest_research_project(boosted(tmp_path), brain)
        source = report.sub_reports[0].source_notes[0]
        trail = ancestors(brain, source.stem)
        assert trail[0] == "Agent brains, surveyed"  # the domain
        assert trail[-1] == "Inventory of systems"  # the topic that cites it

    def test_a_root_has_no_ancestors(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        report = ingest_research_project(boosted(tmp_path), brain)
        assert ancestors(brain, report.topic_note.stem) == []
        assert ancestors(brain, "not-a-note-at-all") == []

    def test_unmatched_terms_are_named(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        ingest_research_project(boosted(tmp_path), brain)
        _hits, coverage = context(brain, "markdown zzzqqq")
        assert coverage.unmatched_terms == ["zzzqqq"]
        assert any("zzzqqq" in signal for signal in coverage.signals())

    def test_single_run_concentration_is_reported(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        ingest_research_project(boosted(tmp_path), brain)
        _hits, coverage = context(brain, "inventory")
        assert len(coverage.runs) == 1
        assert any("one research run" in s for s in coverage.signals())

    def test_signals_name_a_missing_evidence_level(self, tmp_path: Path) -> None:
        """The honest gap: a claim supported only by summaries."""
        brain = tmp_path / "brain"
        ingest_research_project(boosted(tmp_path), brain)
        _hits, coverage = context(brain, "converging", kind="domain")
        assert any("no source archive" in s for s in coverage.signals())

    def test_social_tier_hits_are_counted(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        project = _leaf(
            tmp_path,
            "run",
            "topic",
            "summary",
            {
                "001-s.md": (
                    "---\ntitle: Reddit thread\nurl: https://r.test/1\n"
                    "source_type: social\n---\n\nunverifiable forum claim\n"
                )
            },
        )
        ingest_research_project(project, brain)
        _hits, coverage = context(brain, "unverifiable forum claim", kind="source")
        assert coverage.social == 1
        assert any("social-tier" in s for s in coverage.signals())

    def test_cli_context_prints_hits_and_coverage(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        brain = tmp_path / "brain"
        ingest_research_project(boosted(tmp_path), brain)
        assert main(["--brain", str(brain), "context", "inventory"]) == 0
        out = capsys.readouterr().out
        assert "> here" in out  # the descent path
        assert "Coverage:" in out

    def test_cli_context_exits_nonzero_without_hits(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        brain = tmp_path / "brain"
        ingest_research_project(boosted(tmp_path), brain)
        assert main(["--brain", str(brain), "context", "zzzqqq"]) == 1
        assert "no note in this brain contains" in capsys.readouterr().out


class TestAdversarialInput:
    """Findings from an adversarial review of the shipped implementation."""

    def test_a_string_value_of_null_survives_rebuild(self, tmp_path: Path) -> None:
        """`Note.meta` cannot tell the string "null" from the literal null, so
        a rewrite driven by it would silently destroy the value."""
        brain = tmp_path / "brain"
        (brain / "notes" / "imported").mkdir(parents=True)
        note = brain / "notes" / "imported" / "n.md"
        note.write_text(
            _frontmatter({"title": "null", "type": "note", "slug": "n", "count": "25"})
            + "\n\nbody\n",
            encoding="utf-8",
        )
        before = note.read_text(encoding="utf-8")
        rebuild(brain)
        rebuild(brain)
        meta = parse_note(note.read_text(encoding="utf-8")).meta
        assert meta["title"] == "null"  # still a string
        assert meta["count"] == "25"
        assert note.read_text(encoding="utf-8") == before  # and stable

    def test_a_key_containing_a_colon_round_trips(self, tmp_path: Path) -> None:
        block = _frontmatter({"weird: key": "v", "type": "note"})
        assert parse_note(f"{block}\n\nbody\n").meta["weird: key"] == "v"

    def test_a_leading_byte_order_mark_does_not_hide_frontmatter(self) -> None:
        assert parse_note('﻿---\ntitle: "x"\n---\n\nbody\n').meta == {"title": "x"}

    def test_generated_report_list_does_not_score(self, tmp_path: Path) -> None:
        """`## Report sections` was added after `_own_body` and was missed."""
        brain = tmp_path / "brain"
        project = _leaf(
            tmp_path,
            "run",
            "unrelated subject",
            "unrelated summary",
            {"001-a.md": _material("Doc", "https://x.test/1", "Body.")},
        )
        (project / "report.md").write_text(
            "## Zymurgy\n\n" + "distinctive section prose. " * 10, encoding="utf-8"
        )
        ingest_research_project(project, brain)
        hits = search(brain, "zymurgy")
        # the section itself, not the topic note that merely links to it
        assert hits[0].kind == "report"

    def test_content_provenance_is_recorded_and_checked(self, tmp_path: Path) -> None:
        """A body must not end up wearing provenance it did not come from."""
        brain = tmp_path / "brain"
        report = ingest_research_project(boosted(tmp_path), brain)
        shared = next(
            p
            for p in notes_in(brain / "notes" / "sources")
            if parse_note(p.read_text()).meta["url"] == "https://s.test/1"
        )
        meta = parse_note(shared.read_text(encoding="utf-8")).meta
        # the fuller archive won, so its run is the one credited with the body
        assert meta["content_from"].endswith("sub_02_formats")
        assert meta["content_from"] in json.loads(meta["projects"])
        assert not [f for f in lint(brain) if f.check == "orphaned-content"]

        # strip that run from the citations and lint must notice
        text = shared.read_text(encoding="utf-8")
        shared.write_text(
            text.replace(json.dumps(meta["content_from"]) + ", ", "", 1).replace(
                ", " + json.dumps(meta["content_from"]), "", 1
            ),
            encoding="utf-8",
        )
        assert [f for f in lint(brain) if f.check == "orphaned-content"]
        assert report.sub_reports  # sanity

    def test_an_explicit_related_field_creates_edges_anywhere(
        self, tmp_path: Path
    ) -> None:
        """Reports and sources cannot carry body links; `related` is the way."""
        brain = tmp_path / "brain"
        report = ingest_research_project(boosted(tmp_path), brain)
        source = report.sub_reports[0].source_notes[0]
        target = report.sub_reports[1].topic_note.stem
        text = source.read_text(encoding="utf-8")
        source.write_text(
            text.replace("---\n", f"---\nrelated: {json.dumps([target])}\n", 1),
            encoding="utf-8",
        )
        outgoing, incoming = link_graph(brain)
        assert target in outgoing[source.stem]
        assert source.stem in incoming[target]
