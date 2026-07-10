"""Tests for brain ingestion, indexing, and retrieval."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from brainkit.brain import (
    IngestReport,
    build_index,
    ingest_research_project,
    search,
)
from brainkit.cli import main


def _material(title: str, url: str, body: str, providers: str = "openai") -> str:
    return (
        f"---\ntitle: {title}\nurl: {url}\nsource_type: web\n"
        f"providers: {providers}\ntopic: t\nfetched_at: 2026-07-05\n---\n\n{body}\n"
    )


def make_project(
    tmp_path: Path,
    name: str = "20260705_ai_agents",
    topic: str = "ai agents",
    summary: str = "Agents are eating software. Reddit debates runtime safety.",
    materials: dict[str, str] | None = None,
) -> Path:
    project = tmp_path / name
    (project / "materials").mkdir(parents=True, exist_ok=True)
    (project / "result.json").write_text(
        json.dumps({"topic": topic, "meta_summary": summary}), encoding="utf-8"
    )
    if materials is None:
        materials = {
            "001-reddit-com-agents.md": _material(
                "Agents thread",
                "https://reddit.test/r/agents",
                "Reddit says agents rock.",
            ),
            "002-arxiv-org-paper.md": _material(
                "Agent safety paper",
                "https://arxiv.test/abs/1",
                "Formal analysis of agent runtime safety and sandboxing.",
            ),
        }
    for filename, content in materials.items():
        (project / "materials" / filename).write_text(content, encoding="utf-8")
    return project


class TestIngest:
    def test_ingest_creates_topic_and_source_notes(self, tmp_path: Path) -> None:
        project = make_project(tmp_path)
        brain = tmp_path / "brain"
        report = ingest_research_project(project, brain)

        assert isinstance(report, IngestReport)
        assert report.topic == "ai agents"
        assert report.topic_note.is_file()
        assert len(report.source_notes) == 2
        assert report.skipped_sources == 0

        topic_text = report.topic_note.read_text(encoding="utf-8")
        assert "type: topic" in topic_text
        assert "Agents are eating software" in topic_text
        assert "[[" in topic_text  # wiki links to sources

        source_text = report.source_notes[0].read_text(encoding="utf-8")
        assert "type: source" in source_text
        assert "url: https://" in source_text
        assert "topics: ai agents" in source_text

        index = (brain / "index.md").read_text(encoding="utf-8")
        assert "## ai agents" in index
        assert "https://arxiv.test/abs/1" in index

    def test_reingest_is_idempotent(self, tmp_path: Path) -> None:
        project = make_project(tmp_path)
        brain = tmp_path / "brain"
        first = ingest_research_project(project, brain)
        second = ingest_research_project(project, brain)
        assert [p.name for p in first.source_notes] == [
            p.name for p in second.source_notes
        ]
        sources = list((brain / "notes" / "sources").glob("*.md"))
        assert len(sources) == 2

    def test_shared_source_accumulates_topics(self, tmp_path: Path) -> None:
        shared = _material(
            "Shared doc", "https://shared.test/doc", "Common knowledge body."
        )
        p1 = make_project(
            tmp_path, "p1", topic="topic one", materials={"001-shared.md": shared}
        )
        p2 = make_project(
            tmp_path, "p2", topic="topic two", materials={"001-shared.md": shared}
        )
        brain = tmp_path / "brain"
        ingest_research_project(p1, brain)
        ingest_research_project(p2, brain)

        sources = list((brain / "notes" / "sources").glob("*.md"))
        assert len(sources) == 1  # same URL -> one note
        text = sources[0].read_text(encoding="utf-8")
        assert "topics: topic one, topic two" in text

        index = (brain / "index.md").read_text(encoding="utf-8")
        assert index.count("https://shared.test/doc") == 2  # listed under both topics

    def test_material_without_url_or_body_is_skipped(self, tmp_path: Path) -> None:
        materials = {
            "001-nourl.md": "---\ntitle: No URL\n---\n\nBody without provenance.\n",
            "002-empty.md": _material("Empty", "https://e.test/x", ""),
            "003-good.md": _material("Good", "https://g.test/y", "Real body."),
        }
        project = make_project(tmp_path, materials=materials)
        report = ingest_research_project(project, tmp_path / "brain")
        assert len(report.source_notes) == 1
        assert report.skipped_sources == 2

    def test_project_without_materials_dir(self, tmp_path: Path) -> None:
        project = tmp_path / "bare"
        project.mkdir()
        (project / "result.json").write_text(
            json.dumps({"topic": "bare topic", "meta_summary": "s"}), encoding="utf-8"
        )
        report = ingest_research_project(project, tmp_path / "brain")
        assert report.source_notes == []
        assert "(none downloaded)" in report.topic_note.read_text(encoding="utf-8")

    def test_missing_result_json_raises_with_absolute_path(
        self, tmp_path: Path
    ) -> None:
        project = tmp_path / "unrun"
        project.mkdir()
        with pytest.raises(FileNotFoundError, match="looked for: /") as exc:
            ingest_research_project(project, tmp_path / "brain")
        assert str(project / "result.json") in str(exc.value)

    def test_non_object_result_json_raises(self, tmp_path: Path) -> None:
        project = tmp_path / "weird"
        project.mkdir()
        (project / "result.json").write_text("[1, 2]", encoding="utf-8")
        with pytest.raises(ValueError, match="JSON object"):
            ingest_research_project(project, tmp_path / "brain")


class TestIndexAndSearch:
    def test_index_on_empty_brain(self, tmp_path: Path) -> None:
        index = build_index(tmp_path / "brain")
        assert "0 topics · 0 sources" in index.read_text(encoding="utf-8")

    def test_index_describes_each_source(self, tmp_path: Path) -> None:
        project = make_project(tmp_path)
        brain = tmp_path / "brain"
        ingest_research_project(project, brain)
        index = (brain / "index.md").read_text(encoding="utf-8")
        assert "— Reddit says agents rock." in index
        assert "— Formal analysis of agent runtime safety" in index

    def test_index_description_skips_headings_images_and_truncates(
        self, tmp_path: Path
    ) -> None:
        prose = "word " * 60  # well past the 160-char cap
        materials = {
            "001-noisy.md": _material(
                "Noisy page",
                "https://n.test/1",
                f"# Page heading\n\n![banner](x.png)\n\n{prose}",
            ),
            "002-heading-only.md": _material(
                "Heading only", "https://n.test/2", "# Nothing but a heading"
            ),
        }
        project = make_project(tmp_path, materials=materials)
        brain = tmp_path / "brain"
        ingest_research_project(project, brain)
        index = (brain / "index.md").read_text(encoding="utf-8")
        noisy_line = next(line for line in index.splitlines() if "n.test/1" in line)
        assert "Page heading" not in noisy_line
        assert "![banner]" not in noisy_line
        assert "— word word" in noisy_line
        assert noisy_line.endswith("…")
        heading_only = next(line for line in index.splitlines() if "n.test/2" in line)
        assert "—" not in heading_only  # no prose -> no description

    def test_search_ranks_and_cites(self, tmp_path: Path) -> None:
        project = make_project(tmp_path)
        brain = tmp_path / "brain"
        ingest_research_project(project, brain)

        hits = search(brain, "runtime safety sandboxing")
        assert hits
        top = hits[0]
        assert top.title == "Agent safety paper"
        assert top.url == "https://arxiv.test/abs/1"
        assert "safety" in top.snippet.lower()

    def test_title_match_outranks_body_match(self, tmp_path: Path) -> None:
        materials = {
            "001-title.md": _material(
                "Kubernetes guide", "https://k.test/1", "content here"
            ),
            "002-body.md": _material(
                "Other doc", "https://k.test/2", "kubernetes mentioned once in body"
            ),
        }
        project = make_project(tmp_path, materials=materials)
        brain = tmp_path / "brain"
        ingest_research_project(project, brain)
        hits = search(brain, "kubernetes")
        assert hits[0].url == "https://k.test/1"

    def test_search_empty_query_and_no_match(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        ingest_research_project(make_project(tmp_path), brain)
        assert search(brain, "!!!") == []
        assert search(brain, "zzzunfindable") == []

    def test_search_limit(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        ingest_research_project(make_project(tmp_path), brain)
        assert len(search(brain, "agents reddit safety", limit=1)) == 1


class TestCli:
    def test_ingest_search_list_index_flow(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        project = make_project(tmp_path)
        brain = str(tmp_path / "brain")

        assert main(["--brain", brain, "ingest", str(project)]) == 0
        out = capsys.readouterr().out
        assert "Ingested 'ai agents'" in out and "2 source notes" in out

        assert main(["--brain", brain, "search", "sandboxing"]) == 0
        out = capsys.readouterr().out
        assert "<https://arxiv.test/abs/1>" in out

        assert main(["--brain", brain, "list"]) == 0
        out = capsys.readouterr().out
        assert "topic" in out and "source" in out and "3 notes" in out

        assert main(["--brain", brain, "index"]) == 0
        assert (tmp_path / "brain" / "index.md").is_file()

    def test_cli_error_paths(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        brain = str(tmp_path / "brain")
        assert main(["--brain", brain, "ingest", str(tmp_path / "missing")]) == 1
        assert "Error:" in capsys.readouterr().err

        # Searching a brain directory that does not exist is a path mistake,
        # not an empty result — fail loudly (exit 2) rather than "No matches",
        # so a wrong/relative --brain can't masquerade as an empty brain.
        assert main(["--brain", brain, "search", "anything"]) == 2
        assert "not found" in capsys.readouterr().err

        # A real, populated brain with no hit for the query IS "No matches".
        project = make_project(tmp_path)
        assert main(["--brain", brain, "ingest", str(project)]) == 0
        capsys.readouterr()
        assert main(["--brain", brain, "search", "zzz-nonexistent-term"]) == 1
        assert "No matches" in capsys.readouterr().out

        assert main(["--brain", brain]) == 0  # no command -> help
        assert "usage:" in capsys.readouterr().out

    def test_brain_default_from_env(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("BRAINKIT_DIR", str(tmp_path / "envbrain"))
        monkeypatch.chdir(tmp_path)
        project = make_project(tmp_path)
        assert main(["ingest", str(project)]) == 0
        assert (tmp_path / "envbrain" / "index.md").is_file()


class TestSlugDrift:
    def test_same_url_different_titles_stays_one_note(self, tmp_path: Path) -> None:
        # The citation title (and hence researchkit's filename stem) can
        # change between runs; the URL is the identity.
        m1 = _material("Old Title", "https://drift.test/doc", "Body one.")
        m2 = _material("Renamed Title!", "https://drift.test/doc", "Body two.")
        p1 = make_project(
            tmp_path, "p1", topic="t one", materials={"001-old-title.md": m1}
        )
        p2 = make_project(
            tmp_path, "p2", topic="t two", materials={"007-renamed-title.md": m2}
        )
        brain = tmp_path / "brain"
        ingest_research_project(p1, brain)
        ingest_research_project(p2, brain)

        sources = list((brain / "notes" / "sources").glob("*.md"))
        assert len(sources) == 1
        text = sources[0].read_text(encoding="utf-8")
        assert "topics: t one, t two" in text

    def test_digest_prefix_collision_falls_back_to_full_digest(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import brainkit.brain as brain_mod

        sources_dir = tmp_path / "sources"
        sources_dir.mkdir()
        (sources_dir / "deadbeef-other.md").write_text(
            "---\nurl: https://other.test/x\n---\n\nbody\n", encoding="utf-8"
        )
        monkeypatch.setattr(
            brain_mod, "_source_slug", lambda url, stem: "deadbeef-mine"
        )
        path = brain_mod._source_note_path(
            sources_dir, "https://mine.test/y", "001-mine"
        )
        assert path.name != "deadbeef-other.md"
        assert len(path.stem) == 40  # full sha1


class TestManifestDrivenIngest:
    def test_stale_file_not_in_manifest_is_ignored(self, tmp_path: Path) -> None:
        project = make_project(tmp_path)
        manifest = {
            "entries": [
                {"status": "fetched", "file": "001-reddit-com-agents.md"},
                {"status": "failed", "url": "https://dead.test/x"},
            ]
        }
        (project / "materials" / "index.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
        # 002-arxiv... exists on disk but is NOT in the current manifest
        report = ingest_research_project(project, tmp_path / "brain")
        assert len(report.source_notes) == 1
        assert "reddit" in report.source_notes[0].name

    def test_manifest_entry_with_missing_file_fails_closed(
        self, tmp_path: Path
    ) -> None:
        # A listed-but-missing material means the project dir is corrupt;
        # ingesting a partial set would wrongly prune still-cited sources.
        project = make_project(tmp_path)
        manifest = {
            "entries": [
                {"status": "fetched", "file": "001-reddit-com-agents.md"},
                {"status": "fetched", "file": "999-vanished.md"},
            ]
        }
        (project / "materials" / "index.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
        with pytest.raises(ValueError, match="missing from"):
            ingest_research_project(project, tmp_path / "brain")

    def test_manifest_rejects_malformed_entries(self, tmp_path: Path) -> None:
        project = make_project(tmp_path)
        for bad in ([42], [{"status": "fetched", "file": 123}]):
            (project / "materials" / "index.json").write_text(
                json.dumps({"entries": bad}), encoding="utf-8"
            )
            with pytest.raises(ValueError):
                ingest_research_project(project, tmp_path / "brain")

    def test_malformed_manifest_fails_closed(self, tmp_path: Path) -> None:
        project = make_project(tmp_path)
        (project / "materials" / "index.json").write_text("not json", encoding="utf-8")
        with pytest.raises(ValueError, match="not a valid materials manifest"):
            ingest_research_project(project, tmp_path / "brain")

    def test_manifest_file_entries_cannot_escape_materials_dir(
        self, tmp_path: Path
    ) -> None:
        project = make_project(tmp_path)
        secret = tmp_path / "secret.md"
        secret.write_text(
            "---\ntitle: Secret\nurl: https://s.test/x\n---\n\nclassified\n",
            encoding="utf-8",
        )
        for traversal in ("../../secret.md", "..\\..\\secret.md"):
            manifest = {"entries": [{"status": "fetched", "file": traversal}]}
            (project / "materials" / "index.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )
            # basename containment maps to materials/secret.md, which does
            # not exist -> fail closed, and never reads outside materials/
            with pytest.raises(ValueError, match="missing from"):
                ingest_research_project(project, tmp_path / "brain")


class TestCitationFallback:
    def test_topic_hits_cite_the_research_run(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        brain = tmp_path / "brain"
        ingest_research_project(make_project(tmp_path), brain)
        # "software" only appears in the topic note's meta-summary
        assert main(["--brain", str(brain), "search", "eating software"]) == 0
        out = capsys.readouterr().out
        assert "(research run: 20260705_ai_agents)" in out


class TestReingestReconciliation:
    def test_dropped_citation_is_pruned_from_brain(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        project = make_project(tmp_path)  # cites reddit + arxiv
        first = ingest_research_project(project, brain)
        assert len(first.source_notes) == 2

        # The re-run project no longer cites arxiv
        (project / "materials" / "002-arxiv-org-paper.md").unlink()
        second = ingest_research_project(project, brain)
        assert len(second.source_notes) == 1
        assert second.pruned_sources == 1
        remaining = [p.name for p in (brain / "notes" / "sources").glob("*.md")]
        assert len(remaining) == 1
        assert "reddit" in remaining[0]

    def test_prune_spares_sources_still_cited_by_other_projects(
        self, tmp_path: Path
    ) -> None:
        shared = _material("Shared", "https://shared.test/doc", "Common body.")
        p1 = make_project(tmp_path, "p1", topic="t one", materials={"001-a.md": shared})
        p2 = make_project(tmp_path, "p2", topic="t two", materials={"001-a.md": shared})
        brain = tmp_path / "brain"
        ingest_research_project(p1, brain)
        ingest_research_project(p2, brain)

        # p1 re-runs and drops the shared source
        (p1 / "materials" / "001-a.md").unlink()
        report = ingest_research_project(p1, brain)
        assert report.pruned_sources == 0  # p2 still cites it
        sources = list((brain / "notes" / "sources").glob("*.md"))
        assert len(sources) == 1
        text = sources[0].read_text(encoding="utf-8")
        assert "projects: p2" in text


class TestBoostedIngest:
    def _boosted_project(self, tmp_path: Path) -> Path:
        parent = tmp_path / "20260708_boosted"
        parent.mkdir()
        (parent / "result.json").write_text(
            json.dumps(
                {
                    "decomposed": True,
                    "overarching_topic": "big topic",
                    "super_summary": "Cross-cutting synthesis of the subs.",
                    "subprojects": ["sub_01", "sub_02"],
                }
            ),
            encoding="utf-8",
        )
        (parent / "report.md").write_text(
            "# Super\n\n## Tensions\n\nWhere the subs disagree, at length enough "
            "to pass the stub filter.\n",
            encoding="utf-8",
        )
        for i, sub_topic in enumerate(["memory systems", "orchestration"], start=1):
            make_project(
                parent / "subprojects",
                name=f"sub_{i:02d}",
                topic=sub_topic,
                materials={
                    f"001-doc{i}.md": _material(
                        f"Doc {i}", f"https://sub.test/{i}", f"Body of sub {i}."
                    )
                },
            )
        return parent

    def test_recurses_into_subprojects(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        report = ingest_research_project(self._boosted_project(tmp_path), brain)
        assert report.topic == "big topic"
        assert "Cross-cutting synthesis" in report.topic_note.read_text(
            encoding="utf-8"
        )
        assert len(report.sub_reports) == 2
        assert {r.topic for r in report.sub_reports} == {
            "memory systems",
            "orchestration",
        }
        # both subs' sources landed in the brain
        sources = list((brain / "notes" / "sources").glob("*.md"))
        assert len(sources) == 2

    def test_unrun_subproject_is_reported_not_fatal(self, tmp_path: Path) -> None:
        parent = self._boosted_project(tmp_path)
        unrun = parent / "subprojects" / "sub_03"
        unrun.mkdir()
        report = ingest_research_project(parent, tmp_path / "brain")
        assert len(report.sub_reports) == 2
        assert any("sub_03" in r for r in report.skip_reasons)
        # an un-run sub is not a skipped SOURCE (red-team B7)
        assert report.skipped_sources == 0

    def test_include_reports_reaches_subprojects(self, tmp_path: Path) -> None:
        parent = self._boosted_project(tmp_path)
        sub_report = (
            "# Report\n\nintro long enough to pass the stub filter easily.\n\n"
            "## Key findings\n\nMemory injection amplification is the standout "
            "risk found across sources.\n\n## Sources\n\n- x\n"
        )
        (parent / "subprojects" / "sub_01" / "report.md").write_text(
            sub_report, encoding="utf-8"
        )
        brain = tmp_path / "brain"
        report = ingest_research_project(parent, brain, include_reports=True)
        assert report.report_notes  # parent super-summary sections
        assert report.sub_reports[0].report_notes
        notes = {p.name for p in (brain / "notes" / "reports").glob("*.md")}
        assert any("key-findings" in n for n in notes)
        assert not any("sources" in n for n in notes)  # stub section skipped
        # report chunks are searchable and cite the run (identity is
        # parent-qualified so boosted re-runs can't collide)
        hits = search(brain, "memory injection amplification")
        assert hits and hits[0].project == "20260708_boosted/sub_01"

    def test_include_reports_reingest_is_idempotent(self, tmp_path: Path) -> None:
        project = make_project(tmp_path)
        (project / "report.md").write_text(
            "## Only section\n\nA body comfortably past the forty character "
            "stub filter.\n",
            encoding="utf-8",
        )
        brain = tmp_path / "brain"
        ingest_research_project(project, brain, include_reports=True)
        ingest_research_project(project, brain, include_reports=True)
        assert len(list((brain / "notes" / "reports").glob("*.md"))) == 1


class TestBoostedReingestIdentity:
    def test_two_boosted_runs_with_same_sub_names_coexist(self, tmp_path: Path) -> None:
        # researchkit names subs sub_NN_<slug> with no timestamp; two boosted
        # runs of the same topic must not prune each other (red-team B1).
        def boosted(name: str, url: str) -> Path:
            parent = tmp_path / name
            parent.mkdir()
            (parent / "result.json").write_text(
                json.dumps({"overarching_topic": "same big topic"}),
                encoding="utf-8",
            )
            make_project(
                parent / "subprojects",
                name="sub_01_memory",
                topic="memory systems",
                materials={"001-doc.md": _material("Doc", url, "Body text.")},
            )
            return parent

        brain = tmp_path / "brain"
        ingest_research_project(boosted("20260701_run", "https://a.test/1"), brain)
        second = ingest_research_project(
            boosted("20260708_run", "https://b.test/2"), brain
        )
        assert second.sub_reports[0].pruned_sources == 0
        sources = list((brain / "notes" / "sources").glob("*.md"))
        assert len(sources) == 2  # run 1's source survived run 2's ingest
        topics = list((brain / "notes" / "topics").glob("*.md"))
        assert len(topics) == 4  # 2 parents + 2 distinct sub topic notes


class TestReportChunker:
    def test_duplicate_headings_get_distinct_notes(self, tmp_path: Path) -> None:
        project = make_project(tmp_path)
        (project / "report.md").write_text(
            "## Key findings\n\nFirst provider block, long enough to keep here.\n\n"
            "## Key findings\n\nSecond provider block, also long enough to keep.\n",
            encoding="utf-8",
        )
        brain = tmp_path / "brain"
        report = ingest_research_project(project, brain, include_reports=True)
        assert len(report.report_notes) == 2
        names = sorted(p.name for p in (brain / "notes" / "reports").glob("*.md"))
        assert len(names) == 2 and any(n.endswith("-2.md") for n in names)
        bodies = [
            (brain / "notes" / "reports" / n).read_text(encoding="utf-8") for n in names
        ]
        assert any("First provider" in b for b in bodies)
        assert any("Second provider" in b for b in bodies)

    def test_headings_inside_code_fences_do_not_split(self, tmp_path: Path) -> None:
        project = make_project(tmp_path)
        (project / "report.md").write_text(
            "## Real section\n\nProse before the example, long enough to keep.\n\n"
            "```markdown\n## Fenced pseudo-heading\ncontent inside the fence\n```\n\n"
            "closing prose after the fence.\n",
            encoding="utf-8",
        )
        brain = tmp_path / "brain"
        report = ingest_research_project(project, brain, include_reports=True)
        assert len(report.report_notes) == 1
        body = report.report_notes[0].read_text(encoding="utf-8")
        assert "Fenced pseudo-heading" in body  # stayed inside the one note
        assert body.count("```") == 2  # fences balanced


class TestSkipReasons:
    def test_reasons_name_file_and_cause(self, tmp_path: Path) -> None:
        materials = {
            "001-nourl.md": "---\ntitle: No URL\n---\n\nBody without provenance.\n",
            "002-empty.md": _material("Empty", "https://e.test/x", ""),
        }
        project = make_project(tmp_path, materials=materials)
        report = ingest_research_project(project, tmp_path / "brain")
        assert "materials/001-nourl.md: no 'url' in frontmatter" in report.skip_reasons
        assert "materials/002-empty.md: empty body" in report.skip_reasons

    def test_cli_verbose_prints_reasons(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        materials = {
            "001-nourl.md": "---\ntitle: No URL\n---\n\nBody.\n",
        }
        project = make_project(tmp_path, materials=materials)
        brain = str(tmp_path / "brain")
        assert main(["--brain", brain, "-v", "ingest", str(project)]) == 0
        out = capsys.readouterr().out
        assert "skipped materials/001-nourl.md: no 'url' in frontmatter" in out


class TestSearchKinds:
    def test_kind_filter(self, tmp_path: Path) -> None:
        brain = tmp_path / "brain"
        ingest_research_project(make_project(tmp_path), brain)
        assert all(
            "sources" in str(h.path) for h in search(brain, "agents", kind="source")
        )
        assert all(
            "topics" in str(h.path) for h in search(brain, "agents", kind="topic")
        )

    def test_topic_note_outranks_chatty_source(self, tmp_path: Path) -> None:
        # A long off-domain source mentioning the term more often than the
        # topic note must not win on raw term frequency.
        chatty = _material(
            "Chatty archive",
            "https://offdomain.test/x",
            "freqai " * 6 + "unrelated import pipeline text.",
        )
        project = make_project(
            tmp_path,
            topic="freqai strategies",
            summary="freqai strategy tuning findings. freqai models compared.",
            materials={"001-chatty.md": chatty},
        )
        brain = tmp_path / "brain"
        ingest_research_project(project, brain)
        hits = search(brain, "freqai")
        assert hits[0].path.parent.name == "topics"


class TestIngestNotes:
    def test_url_note_merges_with_project_sources(self, tmp_path: Path) -> None:
        from brainkit.brain import ingest_notes

        brain = tmp_path / "brain"
        ingest_research_project(make_project(tmp_path), brain)
        extra = tmp_path / "extra"
        extra.mkdir()
        # same URL as an ingested project source -> merges, no duplicate
        (extra / "again.md").write_text(
            "---\ntitle: Agents thread\nurl: https://reddit.test/r/agents\n"
            "topic: hand notes\n---\n\nMy own annotations.\n",
            encoding="utf-8",
        )
        (extra / "fresh.md").write_text(
            "---\ntitle: Wiki lesson\nurl: https://wiki.test/lesson\n---\n\n"
            "Lesson learned body.\n",
            encoding="utf-8",
        )
        written, skipped = ingest_notes(extra, brain)
        assert len(written) == 2 and not skipped
        sources = list((brain / "notes" / "sources").glob("*.md"))
        assert len(sources) == 3  # 2 from project + 1 fresh; shared URL merged
        merged = next(p for p in sources if "reddit" in p.read_text(encoding="utf-8"))
        assert "hand notes" in merged.read_text(encoding="utf-8")

    def test_urlless_and_bare_files(self, tmp_path: Path) -> None:
        from brainkit.brain import ingest_notes

        brain = tmp_path / "brain"
        d = tmp_path / "d"
        d.mkdir()
        (d / "wiki.md").write_text(
            "---\ntitle: Team lesson\nproject: crypto-agents\n---\n\nLesson body.\n",
            encoding="utf-8",
        )
        (d / "bare.md").write_text("no frontmatter at all\n", encoding="utf-8")
        # frontmatter without any provenance field is also rejected (B5)
        (d / "meta-only.md").write_text(
            "---\nfoo: bar\n---\n\nBody.\n", encoding="utf-8"
        )
        written, skipped = ingest_notes(d, brain)
        assert len(written) == 1
        assert (brain / "notes" / "imported" / "team-lesson.md").is_file()
        assert skipped == [
            "bare.md: no provenance frontmatter (need url/project/title)",
            "meta-only.md: no provenance frontmatter (need url/project/title)",
        ]

    def test_imported_note_without_project_cites_note_path(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        from brainkit.brain import ingest_notes

        brain = tmp_path / "brain"
        f = tmp_path / "titled.md"
        f.write_text(
            "---\ntitle: Odd lesson\n---\n\nAn odd searchable lessonbody.\n",
            encoding="utf-8",
        )
        ingest_notes(f, brain)
        assert main(["--brain", str(brain), "search", "lessonbody"]) == 0
        out = capsys.readouterr().out
        assert "(research run: )" not in out
        assert "(note: odd-lesson.md)" in out

    def test_missing_path_raises(self, tmp_path: Path) -> None:
        from brainkit.brain import ingest_notes

        with pytest.raises(FileNotFoundError, match="not found"):
            ingest_notes(tmp_path / "nope", tmp_path / "brain")

    def test_cli_ingest_notes(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        f = tmp_path / "one.md"
        f.write_text(
            "---\ntitle: One\nurl: https://one.test/x\n---\n\nBody.\n",
            encoding="utf-8",
        )
        brain = str(tmp_path / "brain")
        assert main(["--brain", brain, "ingest-notes", str(f)]) == 0
        assert "Ingested 1 notes" in capsys.readouterr().out


class TestPathResolution:
    def test_relative_path_falls_back_to_pwd(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Simulate `uv run --directory`: cwd changed, $PWD still the caller's.
        caller = tmp_path / "caller"
        caller.mkdir()
        project = make_project(caller, name="research_runs")
        elsewhere = tmp_path / "toolrepo"
        elsewhere.mkdir()
        monkeypatch.chdir(elsewhere)
        monkeypatch.setenv("PWD", str(caller))
        brain = str(tmp_path / "brain")
        assert main(["--brain", brain, "ingest", "research_runs"]) == 0
        assert project.name == "research_runs"


class TestSameTopicProjects:
    def test_same_topic_different_runs_keep_separate_topic_notes(
        self, tmp_path: Path
    ) -> None:
        m1 = _material("Doc A", "https://a.test/1", "Body A.")
        m2 = _material("Doc B", "https://b.test/2", "Body B.")
        p1 = make_project(
            tmp_path, "run1", topic="same topic", materials={"001-a.md": m1}
        )
        p2 = make_project(
            tmp_path, "run2", topic="same topic", materials={"001-b.md": m2}
        )
        brain = tmp_path / "brain"
        r1 = ingest_research_project(p1, brain)
        r2 = ingest_research_project(p2, brain)
        assert r1.topic_note != r2.topic_note

        index = (brain / "index.md").read_text(encoding="utf-8")
        assert "## same topic (run1)" in index
        assert "## same topic (run2)" in index
        # each run's section lists only its own source
        run1_section = index.split("## same topic (run1)")[1].split("## ")[0]
        assert "https://a.test/1" in run1_section
        assert "https://b.test/2" not in run1_section


def test_slug_collision_projects_keep_separate_topic_notes(tmp_path: Path) -> None:
    # "foo bar" and "foo-bar" slugify identically; the hash suffix must keep
    # their topic notes distinct.
    m = _material("Doc", "https://c.test/1", "Body.")
    p1 = make_project(tmp_path, "foo bar", topic="same", materials={"001-a.md": m})
    p2 = make_project(tmp_path, "foo-bar", topic="same", materials={"001-a.md": m})
    brain = tmp_path / "brain"
    r1 = ingest_research_project(p1, brain)
    r2 = ingest_research_project(p2, brain)
    assert r1.topic_note != r2.topic_note
    assert len(list((brain / "notes" / "topics").glob("*.md"))) == 2


def test_prune_recomputes_topics_from_remaining_projects(tmp_path: Path) -> None:
    shared = _material("Shared", "https://s.test/doc", "Body.")
    p1 = make_project(tmp_path, "p1", topic="topic one", materials={"001-a.md": shared})
    p2 = make_project(tmp_path, "p2", topic="topic two", materials={"001-a.md": shared})
    brain = tmp_path / "brain"
    ingest_research_project(p1, brain)
    ingest_research_project(p2, brain)

    (p1 / "materials" / "001-a.md").unlink()
    ingest_research_project(p1, brain)

    source = next((brain / "notes" / "sources").glob("*.md"))
    text = source.read_text(encoding="utf-8")
    assert "projects: p2" in text
    assert "topics: topic two" in text  # topic one no longer claimed
