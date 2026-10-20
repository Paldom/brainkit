"""Regressions for defects found by cross-model review of Phases 0-1."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from conftest import notes_in

from brainkit import parse_note, raw_frontmatter
from brainkit.brain import (
    _synthesis_failed,
    _synthesis_missing,
    ingest_notes,
    ingest_research_project,
    link_graph,
    lint,
    rebuild,
    search,
)
from brainkit.cli import main

REPO = Path(__file__).resolve().parent.parent


def _material(title: str, url: str, body: str) -> str:
    return f"---\ntitle: {json.dumps(title)}\nurl: {url}\n---\n\n{body}\n"


def _run(root: Path, name: str, materials: dict[str, str], summary: str = "s") -> Path:
    project = root / name
    (project / "materials").mkdir(parents=True)
    (project / "result.json").write_text(
        json.dumps({"topic": f"topic {name}", "meta_summary": summary})
    )
    for filename, text in materials.items():
        (project / "materials" / filename).write_text(text)
    return project


class TestImportIdentity:
    def test_same_relative_path_in_two_roots_is_two_notes(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        for project, body in (("a", "first body"), ("b", "second body")):
            notes = tmp_path / project / "notes"
            notes.mkdir(parents=True)
            (notes / "plan.md").write_text(
                f'---\ntitle: "Plan {project}"\nauthor: "x"\n---\n{body}\n'
            )
            ingest_notes(notes, brain)
        bodies = sorted(
            parse_note(p.read_text()).body.strip()
            for p in notes_in(brain / "notes" / "imported")
        )
        assert bodies == ["first body", "second body"]

    def test_adding_an_explicit_slug_moves_the_note(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        (src / "a.md").write_text('---\ntitle: "Plan"\nauthor: "x"\n---\nv1\n')
        brain = tmp_path / "brain"
        ingest_notes(src, brain)
        (src / "a.md").write_text(
            '---\ntitle: "Plan"\nslug: "my-plan"\nauthor: "x"\n---\nv2\n'
        )
        ingest_notes(src, brain)
        assert [p.name for p in notes_in(brain / "notes" / "imported")] == [
            "my-plan.md"
        ]

    def test_author_id_is_kept(self, tmp_path: Path) -> None:
        src = tmp_path / "n.md"
        src.write_text('---\ntitle: "T"\nid: "urn:okf:x"\nauthor: "a"\n---\nbody\n')
        brain = tmp_path / "brain"
        ingest_notes(src, brain)
        (note,) = notes_in(brain / "notes" / "imported")
        assert parse_note(note.read_text()).meta["id"] == "urn:okf:x"


class TestMergeSemantics:
    def _url_note(self, tmp_path: Path, extra: str) -> Path:
        src = tmp_path / "s.md"
        src.write_text(
            f'---\ntitle: "S"\nurl: "https://s.test"\nauthor: "a"\n{extra}---\nbody\n'
        )
        return src

    def test_reimport_does_not_duplicate_verification(self, tmp_path: Path) -> None:
        src = self._url_note(
            tmp_path, 'verified: [{"by": "human:x", "at": "2026-10-01"}]\n'
        )
        brain = tmp_path / "brain"
        for _ in range(3):
            ingest_notes(src, brain)
        (note,) = notes_in(brain / "notes" / "sources")
        verified = json.loads(dict(raw_frontmatter(note.read_text()))["verified"])
        assert verified == [{"by": "human:x", "at": "2026-10-01T00:00:00Z"}]

    def test_authored_value_updates_on_reimport(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        ingest_notes(self._url_note(tmp_path, "reviewed: false\n"), brain)
        ingest_notes(self._url_note(tmp_path, "reviewed: true\n"), brain)
        (note,) = notes_in(brain / "notes" / "sources")
        assert json.loads(dict(raw_frontmatter(note.read_text()))["reviewed"]) is True

    def test_blank_value_does_not_erase_a_claim(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        ingest_notes(self._url_note(tmp_path, 'status: "stable"\n'), brain)
        ingest_notes(self._url_note(tmp_path, 'status: ""\n'), brain)
        (note,) = notes_in(brain / "notes" / "sources")
        assert parse_note(note.read_text()).meta["status"] == "stable"


class TestFailureEnvelopes:
    @pytest.mark.parametrize(
        "text",
        [
            "# Super-summary unavailable\n\nThe run produced no synthesis.",
            "Super-summary unavailable.",
            "Meta-summary unavailable (no providers)",
            '{"error": {"type": "invalid_request_error", "message": "log in"}}',
            "No code changed this turn — the deliverable was the article.",
        ],
    )
    def test_envelopes_are_failures(self, text: str) -> None:
        assert _synthesis_failed(text)

    def test_generic_status_key_is_not_a_synthesis_status(self) -> None:
        assert not _synthesis_failed("A useful synthesis.", {"status": "error"})
        assert _synthesis_failed("x", {"synthesis_status": "failed"})

    def test_null_super_summary_is_flagged(self) -> None:
        assert _synthesis_missing({"overarching_topic": "t", "super_summary": None})
        assert not _synthesis_missing({"topic": "t"})
        assert not _synthesis_missing({"meta_summary": "ok", "super_summary": None})


class TestLinks:
    def _brain(self, tmp_path: Path) -> tuple[Path, Path, Path]:
        brain = tmp_path / "brain"
        report = ingest_research_project(
            _run(
                tmp_path,
                "run",
                {"001.md": _material("A", "https://a.test", "# Intro\n\nbody text")},
            ),
            brain,
        )
        (source,) = notes_in(brain / "notes" / "sources")
        return brain, report.topic_note, source

    def test_anchor_must_name_a_heading(self, tmp_path: Path) -> None:
        brain, topic, source = self._brain(tmp_path)
        topic.write_text(
            topic.read_text()
            + f"\n- [ok](../sources/{source.name}#intro)"
            + f"\n- [bad](../sources/{source.name}#absent)\n"
        )
        dead = [f.detail for f in lint(brain) if f.check == "dead-link"]
        assert dead == [f"({source.stem}#absent)"]

    def test_link_to_a_level_index_is_navigation(self, tmp_path: Path) -> None:
        brain, topic, _source = self._brain(tmp_path)
        topic.write_text(topic.read_text() + "\n- [all](../sources/index.md)\n")
        assert [f for f in lint(brain) if f.check == "dead-link"] == []

    def test_brain_path_with_dotdot_keeps_edges(self, tmp_path: Path) -> None:
        _brain, topic, source = self._brain(tmp_path)
        (tmp_path / "sub").mkdir()
        odd = tmp_path / "sub" / ".." / "brain"
        outgoing, _incoming = link_graph(odd)
        assert source.stem in outgoing[topic.stem]
        assert [f for f in lint(odd) if f.check == "unreachable"] == []

    def test_legacy_title_with_dash_survives_migration(self, tmp_path: Path) -> None:
        brain, topic, source = self._brain(tmp_path)
        text = topic.read_text()
        lines = [
            f"- [[{source.stem}]] — Cost — Benefit: a title"
            if f"({source.name}" in line or f"/{source.name})" in line
            else line
            for line in text.splitlines()
        ]
        topic.write_text("\n".join(lines) + "\n")
        rebuild(brain)
        assert f"- [Cost — Benefit: a title](../sources/{source.name})" in (
            topic.read_text()
        )


class TestTimeAndScripts:
    def test_staleness_compares_instants(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        imported = brain / "notes" / "imported"
        imported.mkdir(parents=True)
        (imported / "x.md").write_text(
            '---\ntitle: "X"\nslug: "x"\ntype: "note"\n'
            'stale_after: "2026-10-20T23:00:00-10:00"\n---\n\nbody\n'
        )
        assert not [
            f for f in lint(brain, as_of="2026-10-20T00:00:00Z") if f.check == "stale"
        ]
        assert [
            f for f in lint(brain, as_of="2026-10-21T12:00:00Z") if f.check == "stale"
        ]

    def test_korean_partial_word_query_matches(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        ingest_research_project(
            _run(
                tmp_path,
                "ko",
                {
                    "001.md": _material(
                        "korean", "https://ko.test", "한국어 지식 베이스"
                    )
                },
            ),
            brain,
        )
        assert search(brain, "한국")[0].title == "korean"

    def test_rebuild_refuses_unreadable_frontmatter(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        imported = brain / "notes" / "imported"
        imported.mkdir(parents=True)
        legacy = (
            '---\ntitle: "X"\nslug: "x"\ntype: "note"\n'
            "verified:\n  - by: human:x\n---\n\nbody\n"
        )
        (imported / "x.md").write_text(legacy)
        report = rebuild(brain)
        assert (imported / "x.md").read_text() == legacy
        assert report.refused and "multi-line" in report.refused[0]

    def test_rebuild_normalizes_okf_timestamps(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        imported = brain / "notes" / "imported"
        imported.mkdir(parents=True)
        (imported / "x.md").write_text(
            '---\ntitle: "X"\nslug: "x"\ntype: "note"\n'
            'stale_after: "2099-01-01"\n---\n\nbody\n'
        )
        rebuild(brain)
        assert not [f for f in lint(brain) if f.check == "date-only-timestamp"]


class TestSafety:
    def test_symlinked_state_dir_is_refused(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        brain.mkdir()
        outside = tmp_path / "outside"
        outside.mkdir()
        (brain / ".brainkit").symlink_to(outside)
        with pytest.raises(ValueError, match="outside the brain"):
            ingest_research_project(_run(tmp_path, "r", {}), brain)
        assert list(outside.iterdir()) == []

    def test_directory_material_is_reported(self, tmp_path: Path) -> None:
        project = _run(tmp_path, "r", {"001.md": _material("A", "https://a", "b")})
        (project / "materials" / "002-odd.md").mkdir()
        report = ingest_research_project(project, tmp_path / "brain")
        assert "materials/002-odd.md: not a file" in report.skip_reasons


class TestCli:
    def test_ingest_notes_force_and_warnings(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        brain = tmp_path / "brain"
        long_body = "archived text " * 50
        ingest_research_project(
            _run(
                tmp_path, "r", {"001.md": _material("A", "https://a.test", long_body)}
            ),
            brain,
        )
        thin = tmp_path / "thin.md"
        thin.write_text('---\ntitle: "Fix"\nurl: "https://a.test"\n---\nfixed\n')
        assert main(["--brain", str(brain), "ingest-notes", str(thin), "--force"]) == 0
        (source,) = notes_in(brain / "notes" / "sources")
        assert parse_note(source.read_text()).body.strip() == "fixed"
        titled = tmp_path / "t.md"
        titled.write_text('---\ntitle: "Only"\n---\nbody\n')
        assert main(["--brain", str(brain), "ingest-notes", str(titled)]) == 0
        assert "title is not provenance" in capsys.readouterr().err

    def test_busy_brain_exits_nonzero(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        from test_integrity import _held_lock

        brain = tmp_path / "brain"
        project = _run(tmp_path, "r", {})
        with _held_lock(brain):
            assert main(["--brain", str(brain), "ingest", str(project)]) == 1
        assert "being written" in capsys.readouterr().err


def test_skill_is_one_file_for_every_agent() -> None:
    claude = REPO / ".claude" / "skills" / "brainkit" / "SKILL.md"
    agents = REPO / ".agents" / "skills" / "brainkit" / "SKILL.md"
    assert agents.resolve() == claude.resolve()


def test_skill_prose_matches_current_behaviour() -> None:
    skill = (REPO / ".claude" / "skills" / "brainkit" / "SKILL.md").read_text()
    assert "`[[slug]]` links down" not in skill
    assert "no primary source" not in skill


class TestPhase2Review:
    def test_namespace_keeps_identity_across_checkouts(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        for checkout in ("a", "b"):
            notes = tmp_path / checkout / "notes"
            notes.mkdir(parents=True)
            (notes / "one.md").write_text(
                f'---\ntitle: "One"\nauthor: "x"\n---\nfrom {checkout}\n'
            )
            ingest_notes(notes, brain, namespace="team-notes")
        (note,) = notes_in(brain / "notes" / "imported")
        assert "from b" in note.read_text()

    def test_adding_a_url_moves_the_import(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        (src / "a.md").write_text('---\ntitle: "A"\nauthor: "x"\n---\nbody text\n')
        brain = tmp_path / "brain"
        ingest_notes(src, brain)
        (src / "a.md").write_text(
            '---\ntitle: "A"\nauthor: "x"\nurl: "https://a.test"\n---\nbody text\n'
        )
        ingest_notes(src, brain)
        assert notes_in(brain / "notes" / "imported") == []
        assert len(notes_in(brain / "notes" / "sources")) == 1

    def test_written_files_keep_a_readable_mode(self, tmp_path: Path) -> None:
        import os
        import stat

        old = os.umask(0o022)
        try:
            brain = tmp_path / "brain"
            ingest_research_project(
                _run(tmp_path, "r", {"001.md": _material("A", "https://a", "b")}),
                brain,
            )
        finally:
            os.umask(old)
        for path in (brain / "notes").rglob("*.md"):
            assert stat.S_IMODE(path.stat().st_mode) == 0o644, path
        (source,) = notes_in(brain / "notes" / "sources")
        source.chmod(0o640)
        ingest_research_project(
            _run(tmp_path, "r2", {"001.md": _material("A", "https://a", "longer b")}),
            brain,
        )
        assert stat.S_IMODE(source.stat().st_mode) == 0o640  # mode preserved

    def test_bad_as_of_is_a_clean_error(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        brain = tmp_path / "brain"
        ingest_research_project(_run(tmp_path, "r", {}), brain)
        assert main(["--brain", str(brain), "lint", "--as-of", "soon"]) == 1
        assert "Error:" in capsys.readouterr().err

    def test_json_errors_are_json(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert main(["--brain", str(tmp_path / "none"), "search", "x", "--json"]) == 2
        data = json.loads(capsys.readouterr().out)
        assert data["error"]["type"] == "FileNotFoundError"

    def test_index_on_a_busy_brain_is_a_clean_error(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        from test_integrity import _held_lock

        brain = tmp_path / "brain"
        ingest_research_project(_run(tmp_path, "r", {}), brain)
        with _held_lock(brain):
            assert main(["--brain", str(brain), "index"]) == 1
        assert "being written" in capsys.readouterr().err

    def test_search_json_carries_breadcrumbs(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        brain = tmp_path / "brain"
        ingest_research_project(
            _run(tmp_path, "r", {"001.md": _material("A", "https://a", "zebra")}),
            brain,
        )
        assert main(["--brain", str(brain), "search", "zebra", "--json"]) == 0
        hits = json.loads(capsys.readouterr().out)["hits"]
        source = next(h for h in hits if h["kind"] == "source")
        assert source["breadcrumbs"][0]["title"] == "topic r"


class TestPhase3Review:
    def _brain(self, tmp_path: Path) -> Path:
        brain = tmp_path / "brain"
        ingest_research_project(
            _run(
                tmp_path,
                "r",
                {"001.md": _material("Stripes", "https://z.test", "zebra stripes")},
                summary="A summary about animals.",
            ),
            brain,
        )
        return brain

    def test_propagated_hit_survives_kind_filter(self, tmp_path: Path) -> None:
        brain = self._brain(tmp_path)
        hits = search(brain, "zebra", kind="topic")
        assert [h.channel for h in hits] == ["propagated"]

    def test_propagation_channel_independent_of_explain(self, tmp_path: Path) -> None:
        brain = self._brain(tmp_path)
        plain = {h.slug: h.channel for h in search(brain, "zebra", limit=5)}
        explained = {
            h.slug: h.channel for h in search(brain, "zebra", limit=5, explain=True)
        }
        assert plain == explained and "propagated" in plain.values()

    def test_why_explains_a_propagated_hit(self, tmp_path: Path) -> None:
        from brainkit.brain import why

        brain = self._brain(tmp_path)
        topic = next(h for h in search(brain, "zebra") if h.kind == "topic")
        out = why(brain, "zebra", topic.slug)
        assert "rank" in out and "lifted by what it cites" in out

    def test_abstention_returns_nothing(self, tmp_path: Path) -> None:
        assert search(self._brain(tmp_path), "volcanic basalt cooling") == []

    def test_exact_title_ranks_first(self, tmp_path: Path) -> None:
        brain = self._brain(tmp_path)
        assert search(brain, "Stripes")[0].title == "Stripes"

    def test_namespace_ignores_checkout_folder_name(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        for checkout in ("checkout-a", "checkout-b"):
            folder = tmp_path / checkout
            folder.mkdir()
            (folder / "one.md").write_text(
                f'---\ntitle: "One"\nauthor: "x"\n---\nfrom {checkout}\n'
            )
            ingest_notes(folder, brain, namespace="team")
        (note,) = notes_in(brain / "notes" / "imported")
        assert "checkout-b" in note.read_text()

    def test_import_cannot_shadow_another_level(self, tmp_path: Path) -> None:
        brain = self._brain(tmp_path)
        (source,) = notes_in(brain / "notes" / "sources")
        evil = tmp_path / "evil.md"
        evil.write_text(
            f'---\ntitle: "X"\nslug: "{source.stem}"\nauthor: "a"\n---\nbody\n'
        )
        with pytest.raises(ValueError, match="already the id"):
            ingest_notes(evil, brain)

    def test_duplicate_slug_is_a_lint_error(self, tmp_path: Path) -> None:
        brain = self._brain(tmp_path)
        (source,) = notes_in(brain / "notes" / "sources")
        imported = brain / "notes" / "imported"
        imported.mkdir()
        (imported / "dup.md").write_text(
            f'---\ntitle: "D"\nslug: "{source.stem}"\ntype: "note"\n---\n\nbody\n'
        )
        assert [f for f in lint(brain) if f.check == "duplicate-slug"]

    def test_url_move_keeps_old_id_resolvable(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        (src / "a.md").write_text('---\ntitle: "A"\nauthor: "x"\n---\nbody a\n')
        (src / "b.md").write_text(
            '---\ntitle: "B"\nauthor: "x"\nrelated: ["a"]\n---\nbody b\n'
        )
        brain = tmp_path / "brain"
        ingest_notes(src, brain)
        (src / "a.md").write_text(
            '---\ntitle: "A"\nauthor: "x"\nurl: "https://a.test"\n---\nbody a\n'
        )
        ingest_notes(src, brain)
        assert [f for f in lint(brain) if f.check == "dead-link"] == []
        outgoing, _incoming = link_graph(brain)
        (source,) = notes_in(brain / "notes" / "sources")
        assert source.stem in outgoing["b"]

    def test_mode_follows_the_current_umask(self, tmp_path: Path) -> None:
        import os
        import stat

        old = os.umask(0o077)
        try:
            brain = self._brain(tmp_path)
        finally:
            os.umask(old)
        (source,) = notes_in(brain / "notes" / "sources")
        assert stat.S_IMODE(source.stat().st_mode) == 0o600
