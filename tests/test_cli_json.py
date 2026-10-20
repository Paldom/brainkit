"""Machine interfaces: --json records, --explain, --why."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from brainkit.brain import SCHEMA, ingest_research_project
from brainkit.cli import main


@pytest.fixture
def brain(tmp_path: Path) -> Path:
    project = tmp_path / "run"
    (project / "materials").mkdir(parents=True)
    (project / "result.json").write_text(
        json.dumps({"topic": "zebra research", "meta_summary": "Zebras have stripes."})
    )
    (project / "materials" / "001.md").write_text(
        '---\ntitle: "Stripe origins"\nurl: https://z.test\nsource_type: social\n'
        "published: 2026-02-03\n---\n\nZebra stripes deter flies.\n"
    )
    brain = tmp_path / "brain"
    ingest_research_project(project, brain)
    return brain


def _run(capsys: pytest.CaptureFixture[str], *argv: str) -> tuple[int, str]:
    code = main(list(argv))
    return code, capsys.readouterr().out


def test_search_json(brain: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code, out = _run(capsys, "--brain", str(brain), "search", "zebra stripes", "--json")
    data = json.loads(out)
    assert code == 0 and data["schema"] == SCHEMA
    first = data["hits"][0]
    assert {"rank", "id", "path", "kind", "score", "url", "runs", "labels"} <= set(
        first
    )
    assert not first["path"].startswith("/")
    source = next(h for h in data["hits"] if h["kind"] == "source")
    assert source["trust"] == "social" and "social" in source["labels"]
    assert source["runs"] == ["run"]


def test_search_json_no_hits(brain: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code, out = _run(capsys, "--brain", str(brain), "search", "unicorn", "--json")
    assert code == 1 and json.loads(out)["hits"] == []


def test_search_explain(brain: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code, out = _run(capsys, "--brain", str(brain), "search", "zebra", "--explain")
    assert code == 0 and "explain:" in out and "level_prior" in out
    code, out = _run(
        capsys, "--brain", str(brain), "search", "zebra", "--explain", "--json"
    )
    assert "explain" in json.loads(out)["hits"][0]


def test_search_why(brain: Path, capsys: pytest.CaptureFixture[str]) -> None:
    sources = sorted((brain / "notes" / "sources").glob("*-*.md"))
    slug = sources[0].stem
    _code, out = _run(capsys, "--brain", str(brain), "search", "zebra", "--why", slug)
    assert "rank" in out and "matched zebra" in out
    _code, out = _run(capsys, "--brain", str(brain), "search", "unicorn", "--why", slug)
    assert "abstained" in out
    _code, out = _run(capsys, "--brain", str(brain), "search", "z", "--why", "nope")
    assert "no such note" in out
    _code, out = _run(
        capsys,
        "--brain",
        str(brain),
        "search",
        "zebra",
        "--why",
        slug,
        "--kind",
        "topic",
    )
    assert "filtered out" in out


def test_context_json(brain: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code, out = _run(
        capsys, "--brain", str(brain), "context", "zebra stripes unicorn", "--json"
    )
    data = json.loads(out)
    assert code == 0
    assert data["coverage"]["unmatched_terms"] == ["unicorn"]
    assert data["coverage"]["signals"]
    source = next(h for h in data["hits"] if h["kind"] == "source")
    assert source["breadcrumbs"][0]["title"] == "zebra research"


def test_context_human_breadcrumbs(
    brain: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code, out = _run(capsys, "--brain", str(brain), "context", "stripes flies")
    assert code == 0 and "> here" in out and "Coverage:" in out


def test_eval_cli_bad_cases(
    tmp_path: Path, brain: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    bad = tmp_path / "bad.jsonl"
    bad.write_text("not json\n")
    assert main(["--brain", str(brain), "eval", str(bad)]) == 1
    assert "not a valid eval case" in capsys.readouterr().err


def test_eval_cli_misses(
    tmp_path: Path, brain: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    cases = tmp_path / "c.jsonl"
    cases.write_text('{"id": "1", "query": "unicorn", "relevant": ["x"]}\n')
    assert main(["--brain", str(brain), "eval", str(cases), "--misses", "5"]) == 0
    assert "miss 1" in capsys.readouterr().out
