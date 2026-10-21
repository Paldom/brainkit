"""researchkit research-pack contract v2: manifest checks, claims, ledger."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, ClassVar

import pytest

from brainkit import parse_note
from brainkit.brain import ingest_research_project


def _material(title: str, url: str, body: str) -> str:
    return (
        f"---\ntitle: {title}\nurl: {url}\nsource_type: web\n"
        f"providers: openai\ntopic: t\nfetched_at: 2026-07-05\n---\n\n{body}\n"
    )


def make_project(tmp_path: Path, materials: dict[str, str] | None = None) -> Path:
    project = tmp_path / "20260705_ai_agents"
    (project / "materials").mkdir(parents=True, exist_ok=True)
    (project / "result.json").write_text(
        json.dumps(
            {
                "topic": "ai agents",
                "meta_summary": "Agents are eating software. Reddit debates runtime safety.",
            }
        ),
        encoding="utf-8",
    )
    for name, text in (
        materials
        or {
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
    ).items():
        (project / "materials" / name).write_text(text, encoding="utf-8")
    return project


def _v2(
    project: Path, *, complete: bool = True, claims: list[dict[str, Any]] | None = None
) -> Path:
    mats = project / "materials"
    entries = []
    for f in sorted(mats.glob("*.md")):
        url = parse_note(f.read_text(encoding="utf-8")).meta["url"]
        entries.append(
            {
                "url": url,
                "status": "fetched",
                "file": f.name,
                "sha256": hashlib.sha256(f.read_bytes()).hexdigest(),
            }
        )
    claims_sha = None
    if claims is not None:
        data = "".join(json.dumps(c) + "\n" for c in claims).encode()
        (project / "claims.jsonl").write_bytes(data)
        claims_sha = hashlib.sha256(data).hexdigest()
    (mats / "index.json").write_text(
        json.dumps(
            {
                "schema_version": 2,
                "entries": entries,
                "claims_sha256": claims_sha,
                "complete": complete,
            }
        ),
        encoding="utf-8",
    )
    return project


def _tree(brain: Path) -> set[str]:
    return (
        {str(p.relative_to(brain)) for p in brain.rglob("*")}
        if brain.exists()
        else set()
    )


class TestManifestChecks:
    @pytest.mark.parametrize(
        ("mutate", "message"),
        [
            (lambda m: m.update(schema_version=3), "schema_version 3 is not supported"),
            (lambda m: m.update(complete=False), "incomplete"),
            (
                lambda m: m["entries"][0].update(sha256="0" * 64),
                "does not match its sha256",
            ),
        ],
    )
    def test_rejected_before_any_write(
        self, tmp_path: Path, mutate: Any, message: str
    ) -> None:
        project = _v2(make_project(tmp_path))
        index = project / "materials" / "index.json"
        manifest = json.loads(index.read_text())
        mutate(manifest)
        index.write_text(json.dumps(manifest))
        brain = tmp_path / "brain"
        with pytest.raises(ValueError, match=message):
            ingest_research_project(project, brain)
        assert not (brain / "notes").exists()

    def test_v1_manifest_still_ingests(self, tmp_path: Path) -> None:
        project = make_project(tmp_path)
        (project / "materials" / "index.json").write_text(
            json.dumps(
                {
                    "entries": [
                        {
                            "url": "https://reddit.test/r/agents",
                            "status": "fetched",
                            "file": "001-reddit-com-agents.md",
                        }
                    ]
                }
            )
        )
        assert (
            len(ingest_research_project(project, tmp_path / "brain").source_notes) == 1
        )


class TestClaims:
    _CLAIMS: ClassVar[list[dict[str, Any]]] = [
        {
            "sentence": "Reddit says agents rock.",
            "canonical_url": "https://reddit.test/r/agents",
        },
        {
            "sentence": "Sandboxing is formally analysed.",
            "canonical_url": "https://arxiv.test/abs/1",
        },
    ]

    def test_topic_note_lists_cited_claims_linked_to_sources(
        self, tmp_path: Path
    ) -> None:
        project = _v2(make_project(tmp_path), claims=self._CLAIMS)
        report = ingest_research_project(project, tmp_path / "brain")
        text = report.topic_note.read_text(encoding="utf-8")
        assert "## Cited claims" in text
        assert "- Reddit says agents rock. ([source](../sources/" in text
        assert "Agents are eating software" in text  # default keeps the synthesis

    def test_without_reports_the_claims_replace_the_synthesis(
        self, tmp_path: Path
    ) -> None:
        project = _v2(make_project(tmp_path), claims=self._CLAIMS)
        report = ingest_research_project(
            project, tmp_path / "brain", include_reports=False
        )
        text = report.topic_note.read_text(encoding="utf-8")
        assert "Agents are eating software" not in text
        assert "Sandboxing is formally analysed." in text

    def test_claims_digest_mismatch_fails_before_writing(self, tmp_path: Path) -> None:
        project = _v2(make_project(tmp_path), claims=self._CLAIMS)
        (project / "claims.jsonl").write_text('{"sentence": "tampered"}\n')
        brain = tmp_path / "brain"
        with pytest.raises(ValueError, match="claims_sha256"):
            ingest_research_project(project, brain)
        assert not (brain / "notes").exists()


class TestLedger:
    def test_reingest_skips_unchanged_captures_and_records_once(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import brainkit.brain as brain_mod

        body = "Formal analysis of agent runtime safety and sandboxing."
        project = make_project(
            tmp_path,
            materials={
                "001-a.md": _material("A", "https://a.test/x", body).replace(
                    "fetched_at:", "content_digest: abc123\nfetched_at:"
                )
            },
        )
        brain = tmp_path / "brain"
        ingest_research_project(project, brain)
        merges: list[str] = []
        real = brain_mod._merge_source

        def counting(*a: Any, **k: Any) -> bool:
            merges.append(str(k["url"]))
            return real(*a, **k)

        monkeypatch.setattr(brain_mod, "_merge_source", counting)
        second = ingest_research_project(project, brain)
        assert merges == [] and len(second.source_notes) == 1
        rows = (brain / ".brainkit" / "ledger.jsonl").read_text().splitlines()
        assert [json.loads(r)["hash"] for r in rows] == ["abc123"]
