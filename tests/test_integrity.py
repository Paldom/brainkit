"""Data-integrity regressions: each test failed on v0.2.0.

Every case here is a path by which brainkit lost or corrupted knowledge on a
real input — reproduced on the October 2026 research run before it was fixed.
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest
from conftest import notes_in

from brainkit import parse_note, raw_frontmatter
from brainkit.brain import (
    WriterBusyError,
    ingest_notes,
    ingest_research_project,
    lint,
    rebuild,
    search,
)

FAILED = (
    '*Meta-summarization failed: codex exec failed (exit 1): ease log in again.",\n'
    '    "type": "invalid_request_error",\n    "code": "refresh_token_invalidated"\n'
    "  }\n}\n2026-10-19T21:29:03Z ERROR codex_api: 401 Unauthorized*"
)


def _material(title: str, url: str, body: str) -> str:
    return f"---\ntitle: {json.dumps(title)}\nurl: {url}\n---\n\n{body}\n"


def _run(
    root: Path,
    name: str,
    summary: str | None,
    *,
    report: str | None = None,
    materials: dict[str, str] | None = None,
) -> Path:
    project = root / name
    (project / "materials").mkdir(parents=True, exist_ok=True)
    (project / "result.json").write_text(
        json.dumps({"topic": f"topic {name}", "meta_summary": summary}),
        encoding="utf-8",
    )
    for filename, content in (materials or {}).items():
        (project / "materials" / filename).write_text(content, encoding="utf-8")
    if report is not None:
        (project / "report.md").write_text(report, encoding="utf-8")
    return project


class TestFailedSynthesis:
    """V1: an upstream summarizer crash must not become ranked knowledge."""

    def _boosted(self, tmp_path: Path) -> Path:
        parent = tmp_path / "boosted"
        (parent / "subprojects").mkdir(parents=True)
        (parent / "result.json").write_text(
            json.dumps({"overarching_topic": "big topic", "super_summary": None}),
            encoding="utf-8",
        )
        (parent / "report.md").write_text(
            "# Super-summary unavailable\n", encoding="utf-8"
        )
        report = (
            "# Research Report\n\n## Consolidated Analysis\n\n"
            + FAILED
            + "\n\n## Takeaways\n\nWikis compound knowledge across sessions "
            "when they are maintained by an agent.\n"
        )
        _run(
            parent / "subprojects",
            "sub_01_x",
            FAILED,
            report=report,
            materials={
                "001-a.md": _material(
                    "Gist", "https://gist.test/a", "Raw sources stay immutable."
                )
            },
        )
        return parent

    def test_failure_text_never_reaches_a_synthesis_note(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        ingest_research_project(self._boosted(tmp_path), brain)
        for path in (brain / "notes").rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            assert "Meta-summarization failed" not in text, path
            assert "refresh_token_invalidated" not in text, path
            assert "Super-summary unavailable" not in text, path

    def test_failed_run_is_flagged_and_sources_survive(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        ingest_research_project(self._boosted(tmp_path), brain)
        (topic,) = notes_in(brain / "notes" / "topics")
        note = parse_note(topic.read_text(encoding="utf-8"))
        assert note.meta["synthesis"] == "failed"
        assert "description" not in note.meta
        assert len(notes_in(brain / "notes" / "sources")) == 1
        # the healthy report section still lands; the failed one does not
        titles = [
            parse_note(p.read_text(encoding="utf-8")).title
            for p in notes_in(brain / "notes" / "reports")
        ]
        assert any(t.startswith("Takeaways") for t in titles)
        assert not any(t.startswith("Consolidated Analysis") for t in titles)

    def test_failed_synthesis_does_not_outrank_sources(self, tmp_path: Path) -> None:
        """Query the REAL source text: the failed run's topic note must not
        out-rank (or even outscore via a synthesis prior) the source."""
        brain = tmp_path / "brain"
        ingest_research_project(self._boosted(tmp_path), brain)
        hits = search(brain, "raw sources stay immutable")
        assert hits and hits[0].kind == "source"
        topics = [h for h in hits if h.kind == "topic"]
        assert all("synthesis-failed" in h.labels for h in topics)
        assert all(h.score <= hits[0].score for h in topics)

    def test_ordinary_source_mentioning_failure_is_kept(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        project = _run(
            tmp_path,
            "ok",
            "A healthy summary about error handling.",
            materials={
                "001-a.md": _material(
                    "Errors",
                    "https://e.test/a",
                    "Meta-summarization failed is a message some tools print.",
                )
            },
        )
        ingest_research_project(project, brain)
        (source,) = notes_in(brain / "notes" / "sources")
        assert "Meta-summarization failed" in source.read_text(encoding="utf-8")


class TestImportIdentity:
    """V2: two different notes that share a title are two notes."""

    def test_same_title_different_files_both_survive(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        (src / "a.md").write_text(
            '---\ntitle: "Plan"\nauthor: "a"\n---\nbody one\n', encoding="utf-8"
        )
        (src / "b.md").write_text(
            '---\ntitle: "Plan"\nauthor: "b"\n---\nbody two\n', encoding="utf-8"
        )
        brain = tmp_path / "brain"
        ingest_notes(src, brain)
        bodies = sorted(
            parse_note(p.read_text(encoding="utf-8")).body.strip()
            for p in notes_in(brain / "notes" / "imported")
        )
        assert bodies == ["body one", "body two"]

    def test_reimport_updates_in_place(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        (src / "a.md").write_text(
            '---\ntitle: "Plan"\nauthor: "a"\n---\nv1\n', encoding="utf-8"
        )
        brain = tmp_path / "brain"
        ingest_notes(src, brain)
        (src / "a.md").write_text(
            '---\ntitle: "Plan"\nauthor: "a"\n---\nv2 is the newer text\n',
            encoding="utf-8",
        )
        ingest_notes(src, brain)
        (only,) = notes_in(brain / "notes" / "imported")
        assert "v2" in only.read_text(encoding="utf-8")

    def test_explicit_slug_collision_in_one_batch_is_an_error(
        self, tmp_path: Path
    ) -> None:
        src = tmp_path / "src"
        src.mkdir()
        for name in ("a", "b"):
            (src / f"{name}.md").write_text(
                f'---\ntitle: "{name}"\nslug: "same"\nauthor: "x"\n---\nbody\n',
                encoding="utf-8",
            )
        with pytest.raises(ValueError, match="same"):
            ingest_notes(src, tmp_path / "brain")

    def test_explicit_slug_cannot_escape_the_brain(self, tmp_path: Path) -> None:
        src = tmp_path / "evil.md"
        src.write_text(
            '---\ntitle: "x"\nslug: "../../escape"\nauthor: "x"\n---\nbody\n',
            encoding="utf-8",
        )
        brain = tmp_path / "brain"
        ingest_notes(src, brain)
        assert not (tmp_path / "escape.md").exists()
        assert len(notes_in(brain / "notes" / "imported")) == 1


class TestSourceMerge:
    """V3: a thin note for a known URL must not erase the richer archive."""

    def test_short_import_keeps_archive_and_provenance(self, tmp_path: Path) -> None:
        archive = "A long archived article body. " * 40
        project = _run(
            tmp_path,
            "run1",
            "summary",
            materials={
                "001-a.md": '---\ntitle: "Article"\nurl: https://x.test/a\n'
                'content_digest: "sha256:abc"\npublished: "2026-01-02"\n---\n\n'
                + archive
            },
        )
        brain = tmp_path / "brain"
        ingest_research_project(project, brain)
        (source,) = notes_in(brain / "notes" / "sources")
        before = parse_note(source.read_text(encoding="utf-8"))

        thin = tmp_path / "thin.md"
        thin.write_text(
            '---\ntitle: "x"\nurl: "https://x.test/a"\ntags: ["kept"]\n---\ntiny\n',
            encoding="utf-8",
        )
        ingest_notes(thin, brain)
        after = parse_note(source.read_text(encoding="utf-8"))
        assert after.body.strip() == archive.strip()
        for key in ("content_from", "content_digest", "resource", "published"):
            assert after.meta[key] == before.meta[key], key
        assert json.loads(dict(raw_frontmatter(source.read_text()))["tags"]) == ["kept"]

    def test_force_replaces_and_moves_attribution(self, tmp_path: Path) -> None:
        project = _run(
            tmp_path,
            "run1",
            "summary",
            materials={
                "001-a.md": _material("Article", "https://x.test/a", "long " * 50)
            },
        )
        brain = tmp_path / "brain"
        ingest_research_project(project, brain)
        thin = tmp_path / "thin.md"
        thin.write_text(
            '---\ntitle: "Fixed"\nurl: "https://x.test/a"\n---\ncorrected\n',
            encoding="utf-8",
        )
        ingest_notes(thin, brain, force=True)
        (source,) = notes_in(brain / "notes" / "sources")
        after = parse_note(source.read_text(encoding="utf-8"))
        assert after.body.strip() == "corrected"
        # the body no longer came from run1, so run1 must not be credited for it
        assert "content_from" not in after.meta
        assert after.meta["title"] == "Fixed"
        assert not [f for f in lint(brain) if f.check == "orphaned-content"]


class TestTypedPassthrough:
    """V4: lists and objects stay lists and objects."""

    def test_structured_values_round_trip(self, tmp_path: Path) -> None:
        src = tmp_path / "t.md"
        src.write_text(
            "---\n"
            'title: "Typed"\n'
            'tags: ["x", "y"]\n'
            'derived_from: ["a", "b"]\n'
            'verified: [{"by": "human:d", "at": "2026-10-01T00:00:00Z"}]\n'
            "---\nbody\n",
            encoding="utf-8",
        )
        brain = tmp_path / "brain"
        ingest_notes(src, brain)
        (note,) = notes_in(brain / "notes" / "imported")
        raw = dict(raw_frontmatter(note.read_text(encoding="utf-8")))
        assert json.loads(raw["tags"]) == ["x", "y"]
        assert json.loads(raw["derived_from"]) == ["a", "b"]
        assert json.loads(raw["verified"]) == [
            {"by": "human:d", "at": "2026-10-01T00:00:00Z"}
        ]

    def test_rebuild_repairs_double_encoded_values(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        imported = brain / "notes" / "imported"
        imported.mkdir(parents=True)
        (imported / "old.md").write_text(
            '---\ntitle: "Old"\nslug: "old"\ntype: "note"\n'
            'tags: "[\\"x\\", \\"y\\"]"\n---\n\nbody\n',
            encoding="utf-8",
        )
        rebuild(brain)
        raw = dict(raw_frontmatter((imported / "old.md").read_text()))
        assert json.loads(raw["tags"]) == ["x", "y"]


class TestNoOpIngest:
    """V5: re-ingesting identical input changes nothing, the log included."""

    def test_reingest_is_byte_inert_including_log(self, tmp_path: Path) -> None:
        project = _run(
            tmp_path,
            "run1",
            "A summary.",
            materials={"001-a.md": _material("A", "https://x.test/a", "body text")},
        )
        brain = tmp_path / "brain"
        first = ingest_research_project(project, brain)
        assert first.changed > 0
        snapshot = {p: p.read_bytes() for p in brain.rglob("*") if p.is_file()}
        again = ingest_research_project(project, brain)
        assert again.changed == 0
        assert {p: p.read_bytes() for p in brain.rglob("*") if p.is_file()} == snapshot


@contextmanager
def _held_lock(brain: Path) -> Iterator[None]:
    """Hold the brain's writer lock from ANOTHER process for the duration."""
    lock = brain / ".brainkit" / "lock"
    lock.parent.mkdir(parents=True, exist_ok=True)
    holder = subprocess.Popen(
        [
            sys.executable,
            "-c",
            "import fcntl, os, sys, time\n"
            f"fd = os.open({str(lock)!r}, os.O_CREAT | os.O_RDWR)\n"
            "fcntl.flock(fd, fcntl.LOCK_EX)\n"
            "print('locked', flush=True)\n"
            "time.sleep(60)\n",
        ],
        stdout=subprocess.PIPE,
        text=True,
    )
    try:
        assert holder.stdout is not None
        assert holder.stdout.readline().strip() == "locked"
        yield
    finally:
        holder.kill()
        holder.wait()
        if holder.stdout is not None:
            holder.stdout.close()


class TestPreflightAndAtomicity:
    def test_malformed_child_leaves_brain_untouched(self, tmp_path: Path) -> None:
        parent = tmp_path / "boosted"
        (parent / "subprojects").mkdir(parents=True)
        (parent / "result.json").write_text(
            json.dumps({"overarching_topic": "t", "super_summary": "s"}),
            encoding="utf-8",
        )
        _run(
            parent / "subprojects",
            "sub_01",
            "ok",
            materials={"001-a.md": _material("A", "https://x.test/a", "body")},
        )
        bad = parent / "subprojects" / "sub_02"
        bad.mkdir()
        (bad / "result.json").write_text("{not json", encoding="utf-8")
        brain = tmp_path / "brain"
        with pytest.raises(ValueError, match="sub_02"):
            ingest_research_project(parent, brain)
        assert not (brain / "notes").exists()

    def test_concurrent_writer_is_refused(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        with _held_lock(brain), pytest.raises(WriterBusyError):
            ingest_research_project(_run(tmp_path, "run1", "s"), brain)

    def test_dead_writer_frees_the_brain(self, tmp_path: Path) -> None:
        """The OS lock dies with its process: no stale-lock cleanup needed."""
        brain = tmp_path / "brain"
        with _held_lock(brain):
            pass  # holder killed here
        ingest_research_project(_run(tmp_path, "run1", "s"), brain)

    def test_leftover_lock_file_is_harmless(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        (brain / ".brainkit").mkdir(parents=True)
        (brain / ".brainkit" / "lock").write_text("12345\n", encoding="utf-8")
        ingest_research_project(_run(tmp_path, "run1", "s"), brain)

    def test_no_temp_files_left_behind(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        ingest_research_project(
            _run(
                tmp_path,
                "run1",
                "s",
                materials={"001-a.md": _material("A", "https://x.test/a", "b")},
            ),
            brain,
        )
        assert not [p for p in brain.rglob("*") if ".tmp-" in p.name]


class TestProvenanceAdmission:
    """A title is a label, not evidence: title-only imports are flagged."""

    def test_title_only_import_warns(self, tmp_path: Path) -> None:
        src = tmp_path / "t.md"
        src.write_text('---\ntitle: "Just a title"\n---\nbody\n', encoding="utf-8")
        report = ingest_notes(src, tmp_path / "brain")
        assert report.written
        assert any("title is not provenance" in w for w in report.warnings)

    def test_authored_import_does_not_warn(self, tmp_path: Path) -> None:
        src = tmp_path / "t.md"
        src.write_text(
            '---\ntitle: "T"\nderived_from: ["x"]\n---\nbody\n', encoding="utf-8"
        )
        report = ingest_notes(src, tmp_path / "brain")
        assert report.warnings == []


class TestNonFiniteValues:
    """``json.loads`` accepts NaN/Infinity; writing them back must not crash."""

    def test_infinity_in_material_frontmatter_ingests(self, tmp_path: Path) -> None:
        project = _run(
            tmp_path,
            "run1",
            "s",
            materials={
                "001-a.md": "---\ntitle: T\nurl: https://x.test/a\n"
                "content_digest: Infinity\n---\n\nbody\n"
            },
        )
        brain = tmp_path / "brain"
        ingest_research_project(project, brain)
        (source,) = notes_in(brain / "notes" / "sources")
        assert parse_note(source.read_text()).meta["content_digest"] == "Infinity"

    def test_nan_in_imported_note_stays_a_string(self, tmp_path: Path) -> None:
        src = tmp_path / "n.md"
        src.write_text('---\ntitle: "T"\nauthor: "a"\nrank: NaN\n---\nb\n')
        brain = tmp_path / "brain"
        ingest_notes(src, brain)
        rebuild(brain)
        assert lint(brain) == []


class TestReviewFindings:
    """Regressions for the defects the Phase 0 cross-review found."""

    def _src(self, tmp_path: Path, files: dict[str, str]) -> Path:
        src = tmp_path / "src"
        src.mkdir(exist_ok=True)
        for name, text in files.items():
            (src / name).write_text(text, encoding="utf-8")
        return src

    def test_explicit_slug_and_title_cannot_collide(self, tmp_path: Path) -> None:
        src = self._src(
            tmp_path,
            {
                "a.md": '---\ntitle: "Plan"\nauthor: "x"\n---\nbody one\n',
                "b.md": '---\ntitle: "Other"\nslug: "plan"\nauthor: "x"\n---\nbody two\n',
            },
        )
        brain = tmp_path / "brain"
        ingest_notes(src, brain)
        bodies = sorted(
            parse_note(p.read_text()).body.strip()
            for p in notes_in(brain / "notes" / "imported")
        )
        assert bodies == ["body one", "body two"]

    def test_explicit_slug_held_by_another_origin_is_refused(
        self, tmp_path: Path
    ) -> None:
        brain = tmp_path / "brain"
        first = tmp_path / "one"
        first.mkdir()
        (first / "a.md").write_text(
            '---\ntitle: "A"\nslug: "keep"\nauthor: "x"\n---\nfirst\n'
        )
        ingest_notes(first, brain)
        second = tmp_path / "two"
        second.mkdir()
        (second / "b.md").write_text(
            '---\ntitle: "B"\nslug: "keep"\nauthor: "x"\n---\nsecond\n'
        )
        with pytest.raises(ValueError, match="already belongs"):
            ingest_notes(second, brain)
        (note,) = notes_in(brain / "notes" / "imported")
        assert "first" in note.read_text()

    def test_reserved_slug_cannot_destroy_content(self, tmp_path: Path) -> None:
        src = self._src(
            tmp_path,
            {"x.md": '---\ntitle: "X"\nslug: "index"\nauthor: "a"\n---\nkeep me\n'},
        )
        brain = tmp_path / "brain"
        ingest_notes(src, brain)
        (note,) = notes_in(brain / "notes" / "imported")
        assert note.name == "index-note.md"
        assert "keep me" in note.read_text()

    def test_directory_named_like_a_material_fails_before_writes(
        self, tmp_path: Path
    ) -> None:
        project = _run(
            tmp_path,
            "run1",
            "s",
            materials={"001-a.md": _material("A", "https://x.test/a", "body")},
        )
        (project / "materials" / "002-broken.md").mkdir()
        brain = tmp_path / "brain"
        report = ingest_research_project(project, brain)
        assert len(report.source_notes) == 1

    def test_symlinked_level_cannot_redirect_writes(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        outside = tmp_path / "outside"
        outside.mkdir()
        (brain / "notes").mkdir(parents=True)
        (brain / "notes" / "sources").symlink_to(outside)
        project = _run(
            tmp_path,
            "run1",
            "s",
            materials={"001-a.md": _material("A", "https://x.test/a", "body")},
        )
        with pytest.raises(ValueError, match="outside the brain"):
            ingest_research_project(project, brain)
        assert list(outside.iterdir()) == []

    def test_retitled_reimport_updates_the_same_note(self, tmp_path: Path) -> None:
        src = self._src(
            tmp_path, {"a.md": '---\ntitle: "Old title"\nauthor: "x"\n---\nv1\n'}
        )
        brain = tmp_path / "brain"
        ingest_notes(src, brain)
        (src / "a.md").write_text('---\ntitle: "New title"\nauthor: "x"\n---\nv2\n')
        ingest_notes(src, brain)
        (note,) = notes_in(brain / "notes" / "imported")
        meta = parse_note(note.read_text()).meta
        assert meta["title"] == "New title" and "v2" in note.read_text()

    def test_url_import_keeps_supplied_runs(self, tmp_path: Path) -> None:
        src = self._src(
            tmp_path,
            {
                "s.md": '---\ntitle: "S"\nurl: "https://s.test"\n'
                'projects: ["runA", "runB"]\ncontent_from: "runA"\n---\nbody\n'
            },
        )
        brain = tmp_path / "brain"
        ingest_notes(src, brain)
        (note,) = notes_in(brain / "notes" / "sources")
        raw = dict(raw_frontmatter(note.read_text()))
        assert json.loads(raw["projects"]) == ["runA", "runB"]
        assert json.loads(raw["corroboration"]) == 2
        assert json.loads(raw["content_from"]) == "runA"
        checks = {f.check for f in lint(brain)}
        assert not checks & {"orphaned-content", "corroboration-drift"}

    def test_unknown_and_falsy_values_survive(self, tmp_path: Path) -> None:
        src = self._src(
            tmp_path,
            {
                "a.md": '---\ntitle: "T"\nauthor: "x"\nreviewed: false\n'
                'status: ""\nextra: {"k": [1, 2]}\n---\nbody\n'
            },
        )
        brain = tmp_path / "brain"
        ingest_notes(src, brain)
        (note,) = notes_in(brain / "notes" / "imported")
        raw = dict(raw_frontmatter(note.read_text()))
        assert json.loads(raw["reviewed"]) is False
        assert json.loads(raw["status"]) == ""
        assert json.loads(raw["extra"]) == {"k": [1, 2]}

    @pytest.mark.parametrize(
        ("front", "reason"),
        [
            ('title: "T"\nauthor: "x"\nverified:\n  - by: human:x\n', "multi-line"),
            ('title: "T"\nauthor: "x"\ntags: ["a"]\ntags: ["b"]\n', "duplicate key"),
        ],
    )
    def test_unreadable_frontmatter_is_refused_not_truncated(
        self, tmp_path: Path, front: str, reason: str
    ) -> None:
        src = self._src(tmp_path, {"a.md": f"---\n{front}---\nbody\n"})
        report = ingest_notes(src, tmp_path / "brain")
        assert report.written == []
        assert reason in report.skipped[0]

    def test_failed_run_title_query_gets_no_synthesis_prior(
        self, tmp_path: Path
    ) -> None:
        brain = tmp_path / "brain"
        failed = _run(
            tmp_path,
            "zebra",
            FAILED,
            materials={"001-a.md": _material("Z", "https://z.test", "zebra stripes")},
        )
        ingest_research_project(failed, brain)
        from brainkit.brain import context

        hits, coverage = context(brain, "topic zebra")
        topic = next(h for h in hits if h.kind == "topic")
        assert "synthesis-failed" in topic.labels
        assert coverage.failed_runs == ["zebra"]
        assert any("synthesis failed upstream" in s for s in coverage.signals())

    def test_reimport_keeps_authored_description(self, tmp_path: Path) -> None:
        text = (
            '---\ntitle: "S"\nurl: "https://s.test"\nauthor: "x"\n'
            'description: "Hand-written summary"\n---\nbody text\n'
        )
        src = self._src(tmp_path, {"s.md": text})
        brain = tmp_path / "brain"
        ingest_notes(src, brain)
        ingest_notes(src, brain)
        (note,) = notes_in(brain / "notes" / "sources")
        assert (
            parse_note(note.read_text()).meta["description"] == "Hand-written summary"
        )


def test_prose_about_failure_is_not_a_crash_report() -> None:
    from brainkit.brain import _synthesis_failed

    assert not _synthesis_failed("Summarization failed to lower costs in our pilot.")
    assert _synthesis_failed("*Meta-summarization failed: codex exec failed*")
    assert _synthesis_failed("# Super-summary unavailable")


def test_research_ingest_matches_v020_bytes(tmp_path: Path) -> None:
    """Existing brains must not churn: research-only ingest of source and
    report notes is byte-identical to v0.2.0 (generation stamp aside).

    The expected bytes were produced by running v0.2.0 on this exact input
    (``tests/golden_fixture.py``). Node notes are excluded on purpose: their
    link format changed to OKF §6.1 markdown links.
    """
    from golden_fixture import build, normalized

    brain = tmp_path / "brain"
    ingest_research_project(build(tmp_path), brain)
    golden = json.loads(
        (Path(__file__).parent / "fixtures" / "golden_v020.json").read_text("utf-8")
    )
    assert normalized(brain) == golden
