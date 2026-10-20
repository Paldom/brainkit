"""The retrieval eval, run as part of the gate.

Builds the pinned eval brain once, scores the real ranker and two controls,
and holds every metric to the floor committed in ``tests/eval/baseline.json``.
A ranking change that drops a metric past its floor fails here; one that
improves it should re-pin the baseline (``tests/eval/make_baseline.py``) with
a decision file in ``docs/eval/decisions/``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from brainkit.cli import main
from brainkit.evaluate import (
    Case,
    CaseResult,
    Report,
    compare,
    evaluate,
    load_all_cases,
    load_cases,
    misses,
    render,
)

EVAL = Path(__file__).parent / "eval"
sys.path.insert(0, str(EVAL))

from brain_builder import build_brain  # noqa: E402


@pytest.fixture(scope="module")
def brain(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return build_brain(tmp_path_factory.mktemp("eval"))


@pytest.fixture(scope="module")
def cases() -> list[Case]:
    return load_all_cases(EVAL)


@pytest.fixture(scope="module")
def reports(brain: Path, cases: list[Case]) -> dict[str, Report]:
    return {
        name: evaluate(brain, cases, name) for name in ("brainkit", "grep", "degraded")
    }


def test_eval_set_covers_every_stratum(cases: list[Case]) -> None:
    strata = {case.stratum for case in cases}
    assert {"lexical", "paraphrase", "relational", "title", "negative"} <= strata
    assert {case.split for case in cases} == {"dev", "heldout"}
    assert len(cases) >= 140


def test_metrics_hold_their_floors(reports: dict[str, Report]) -> None:
    baseline = json.loads((EVAL / "baseline.json").read_text(encoding="utf-8"))
    results = reports["brainkit"].results
    summaries = {
        split: Report(
            "brainkit", [r for r in results if r.case.split == split]
        ).summary()
        for split in ("dev", "heldout")
    }
    failures = []
    for key, pinned in baseline["metrics"].items():
        split, stratum, metric = key.split(".")
        value = summaries[split][stratum][metric]
        if pinned["direction"] == "higher" and value < pinned["floor"]:
            failures.append(f"{key}: {value:.4f} < floor {pinned['floor']}")
        if pinned["direction"] == "lower" and value > pinned["floor"]:
            failures.append(f"{key}: {value:.4f} > ceiling {pinned['floor']}")
    assert not failures, "\n".join(failures)


def test_negative_control_is_reachable(reports: dict[str, Report]) -> None:
    """The eval must be able to fail: a degraded ranker scores ≤ half."""
    real = reports["brainkit"].summary()["all"]["recall"]
    weak = reports["degraded"].summary()["all"]["recall"]
    assert weak <= real / 2


def test_brainkit_beats_the_grep_baseline(reports: dict[str, Report]) -> None:
    verdict = compare(reports["brainkit"], reports["grep"], "recall")
    assert verdict.verdict == "better", verdict


def test_render_and_misses(reports: dict[str, Report]) -> None:
    text = render(reports["brainkit"])
    assert "paraphrase" in text and "false-positive" in text
    assert misses(reports["degraded"], 3)


def _result(
    relevant: tuple[str, ...], ranked: tuple[str, ...], case_id: str = "x", **kw: object
) -> CaseResult:
    case = Case(id=case_id, query="q", relevant=relevant, **kw)  # type: ignore[arg-type]
    return CaseResult(case, ranked)


class TestMetrics:
    def test_positive_case(self) -> None:
        r = _result(("b",), ("a", "b", "c"))
        assert r.recall == 1.0 and r.mrr == 0.5
        assert r.precision == pytest.approx(1 / 5)  # fixed denominator
        assert 0 < r.ndcg < 1

    def test_required_set(self) -> None:
        r = _result(("a", "b"), ("a", "c"), required=("a", "b"))
        assert r.hit == 1.0 and r.recall == 0.5 and r.all_required == 0.0

    def test_negative_case(self) -> None:
        assert _result((), (), negative=True).recall == 1.0
        hit = _result((), ("a",), negative=True)
        assert hit.recall == 0.0 and hit.false_positive == 1.0

    def test_miss(self) -> None:
        r = _result(("z",), ("a", "b"))
        assert r.recall == r.mrr == r.ndcg == 0.0


class TestCompare:
    def _report(self, hits: list[bool]) -> Report:
        return Report(
            ranker="r",
            # One evidence note per case: each is its own bootstrap cluster.
            results=[
                _result((f"t{i}",), (f"t{i}",) if hit else ("x",), case_id=str(i))
                for i, hit in enumerate(hits)
            ],
        )

    def test_verdicts(self) -> None:
        good, bad = self._report([True] * 40), self._report([False] * 40)
        assert compare(good, bad).verdict == "better"
        assert compare(bad, good).verdict == "worse"
        assert compare(good, good).verdict == "non-inferior"
        mixed = self._report([True, False] * 4)
        flipped = self._report([False, True] * 4)
        assert compare(mixed, flipped).verdict == "inconclusive"

    def test_queries_about_one_note_are_one_cluster(self) -> None:
        """Nineteen wins on one note plus one loss is two observations."""
        cand = Report(
            "c",
            [_result(("a",), ("a",), case_id=str(i)) for i in range(19)]
            + [_result(("b",), ("x",), case_id="19")],
        )
        base = Report(
            "b",
            [_result(("a",), ("x",), case_id=str(i)) for i in range(19)]
            + [_result(("b",), ("b",), case_id="19")],
        )
        assert compare(cand, base).verdict == "inconclusive"

    def test_no_shared_cases(self) -> None:
        assert compare(Report("a", []), Report("b", [])).verdict == "inconclusive"


def test_load_cases_rejects_bad_lines(tmp_path: Path) -> None:
    bad = tmp_path / "cases.jsonl"
    bad.write_text('{"id": "1", "query": "q"}\n{"query": "missing id"}\n')
    with pytest.raises(ValueError, match=":2:"):
        load_cases(bad)


def test_eval_cli(brain: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cases = str(EVAL / "cases_generated.jsonl")
    assert main(["--brain", str(brain), "eval", cases, "--compare", "grep"]) == 0
    out = capsys.readouterr().out
    assert "ranker: brainkit" in out and "vs grep" in out
    assert main(["--brain", str(brain), "eval", cases, "--json", "--split", "dev"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["ranker"] == "brainkit" and "all" in data["summary"]


def test_exact_title_guard(reports: dict[str, Report]) -> None:
    """A query that IS a note's title must return that note first."""
    title = reports["brainkit"].summary()["title"]
    assert title["mrr"] == 1.0


def test_no_evidence_straddles_the_splits(cases: list[Case]) -> None:
    """Tuning on dev must not see held-out evidence (or vice versa)."""
    splits_of: dict[str, set[str]] = {}
    for case in cases:
        for slug in (*case.relevant, *case.required):
            splits_of.setdefault(slug, set()).add(case.split)
    assert [s for s, found in splits_of.items() if len(found) > 1] == []


def test_title_cases_are_whole_titles(brain: Path, cases: list[Case]) -> None:
    from brainkit import parse_note

    titles = {
        p.stem: parse_note(p.read_text(encoding="utf-8")).title
        for p in (brain / "notes").rglob("*.md")
    }
    for case in (c for c in cases if c.stratum == "title"):
        assert case.query == titles[case.relevant[0]]


def test_single_evidence_note_is_inconclusive() -> None:
    cand = Report("c", [_result(("a",), ("a",), case_id=str(i)) for i in range(5)])
    base = Report("b", [_result(("a",), ("x",), case_id=str(i)) for i in range(5)])
    assert compare(cand, base).verdict == "inconclusive"
