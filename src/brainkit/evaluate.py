"""Retrieval evaluation: the referee every ranking change has to pass.

Without a labelled eval, ranking work is taste. This module scores rankers on
a JSONL set of cases and compares two of them with a paired bootstrap, so a
change is promoted on evidence — or reported, honestly, as inconclusive.

A case is one JSON object per line::

    {"id": "lex-001", "query": "…", "relevant": ["slug", …],
     "required": ["slug", …], "negative": false,
     "stratum": "lexical", "family": "<research run>", "split": "dev"}

``relevant``: any of these in the top k counts as a hit. ``required``: every
one of these must be retrieved (multi-source questions). ``negative``: the
brain holds no answer, so the right result is no result at all.

Three rankers ship with the harness: ``brainkit`` (the real search), ``grep``
(every note containing a query term, ranked by occurrence count — the
baseline every peer system turned out to be closer to than it hoped), and
``degraded`` (grep's candidates in alphabetical order) — the negative
control: if the real ranker does not clearly beat it, the eval is vacuous.
"""

from __future__ import annotations

import json
import math
import random
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from brainkit.brain import Corpus, _fold, _own_body, _tokens, search

K = 5
DEEP_K = 10
# A change may cost at most this much Recall@5 and still count as
# non-inferior. Fixed BEFORE looking at any held-out result.
NON_INFERIORITY_MARGIN = 0.05

Ranker = Callable[["Snapshot", str, int], list[str]]


class Snapshot:
    """One parse of the brain, shared by every query of an evaluation."""

    def __init__(self, brain_dir: Path) -> None:
        self.brain_dir = brain_dir
        self.corpus = Corpus(brain_dir)
        self.folded = [
            (doc.path.stem, _fold(f"{doc.note.title}\n{_own_body(doc.note)}"))
            for doc in self.corpus.docs
        ]


@dataclass(frozen=True)
class Case:
    id: str
    query: str
    relevant: tuple[str, ...] = ()
    required: tuple[str, ...] = ()
    negative: bool = False
    stratum: str = "lexical"
    family: str = ""
    split: str = "dev"


@dataclass(frozen=True)
class CaseResult:
    case: Case
    ranked: tuple[str, ...]

    @property
    def answered(self) -> bool:
        """Did the ranker return anything in the top five (negatives: a
        false positive)? Judged at K, the depth a caller actually reads."""
        return bool(self.ranked[:K])

    @property
    def hit(self) -> float:
        """Hit@5: ANY relevant note in the top five."""
        if self.case.negative:
            return float(not self.answered)
        return float(bool(set(self.ranked[:K]) & set(self.case.relevant)))

    @property
    def recall(self) -> float:
        """Recall@5: the FRACTION of relevant notes in the top five. Equal to
        Hit@5 for single-answer cases; lower when a multi-answer question
        found only some of its evidence."""
        if self.case.negative:
            return float(not self.answered)
        relevant = set(self.case.relevant)
        if not relevant:
            return 0.0
        return len(set(self.ranked[:K]) & relevant) / len(relevant)

    @property
    def all_required(self) -> float:
        """Every explicitly REQUIRED note within the top ten (cases without a
        ``required`` list score as Hit@5 — "any of these 25 sources" is not
        a must-retrieve-all question)."""
        need = set(self.case.required)
        return float(need <= set(self.ranked[:DEEP_K])) if need else self.hit

    @property
    def precision(self) -> float:
        """P@5 with a FIXED denominator of five — dividing by the number of
        results returned is the bug that inflated a published benchmark."""
        if self.case.negative:
            return float(not self.answered)
        return len(set(self.ranked[:K]) & set(self.case.relevant)) / K

    @property
    def mrr(self) -> float:
        """MRR@10 (reciprocal rank of the first relevant note in the top 10)."""
        if self.case.negative:
            return float(not self.answered)
        for rank, slug in enumerate(self.ranked[:DEEP_K], start=1):
            if slug in self.case.relevant:
                return 1 / rank
        return 0.0

    @property
    def ndcg(self) -> float:
        """Binary-gain nDCG@5."""
        if self.case.negative:
            return float(not self.answered)
        gains = [
            1 / math.log2(rank + 1)
            for rank, slug in enumerate(self.ranked[:K], start=1)
            if slug in self.case.relevant
        ]
        ideal = sum(
            1 / math.log2(r + 1) for r in range(1, min(K, len(self.case.relevant)) + 1)
        )
        return sum(gains) / ideal if ideal else 0.0

    @property
    def false_positive(self) -> float:
        """A negative case that returned anything at all."""
        return float(self.case.negative and self.answered)


METRICS = ("hit", "recall", "all_required", "precision", "mrr", "ndcg")


@dataclass
class Report:
    ranker: str
    results: list[CaseResult]
    by_stratum: dict[str, dict[str, float]] = field(default_factory=dict)

    def summary(self) -> dict[str, dict[str, float]]:
        """Mean of each metric per stratum, plus ``all`` and the FP rate."""
        groups: dict[str, list[CaseResult]] = {}
        for result in self.results:
            groups.setdefault(result.case.stratum, []).append(result)
        groups["all"] = [r for r in self.results if not r.case.negative]
        out: dict[str, dict[str, float]] = {}
        for name, rows in sorted(groups.items()):
            if not rows:
                continue
            out[name] = {m: _mean([getattr(r, m) for r in rows]) for m in METRICS}
            out[name]["n"] = float(len(rows))
        negatives = [r for r in self.results if r.case.negative]
        if negatives:
            out.setdefault("negative", {})["false_positive_rate"] = _mean(
                [r.false_positive for r in negatives]
            )
        return out


def _mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def load_cases(path: Path) -> list[Case]:
    cases: list[Case] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
            cases.append(
                Case(
                    id=str(raw["id"]),
                    query=str(raw["query"]),
                    relevant=tuple(raw.get("relevant", ())),
                    required=tuple(raw.get("required", ())),
                    negative=bool(raw.get("negative", False)),
                    stratum=str(raw.get("stratum", "lexical")),
                    family=str(raw.get("family", "")),
                    split=str(raw.get("split", "dev")),
                )
            )
        except (ValueError, KeyError, TypeError) as e:
            raise ValueError(f"{path}:{number}: not a valid eval case ({e})") from e
    return cases


def brainkit_ranker(snap: Snapshot, query: str, k: int) -> list[str]:
    hits = search(snap.brain_dir, query, limit=k, corpus=snap.corpus)
    return [hit.path.stem for hit in hits]


def _grep_candidates(snap: Snapshot, query: str) -> list[tuple[str, int]]:
    terms = [t for t in dict.fromkeys(_tokens(query)) if t]
    scored: list[tuple[str, int]] = []
    for slug, text in snap.folded:
        count = sum(text.count(term) for term in terms)
        if count:
            scored.append((slug, count))
    return scored


def grep_ranker(snap: Snapshot, query: str, k: int) -> list[str]:
    """``grep -c`` for every query term, summed: the honest baseline."""
    scored = _grep_candidates(snap, query)
    scored.sort(key=lambda pair: (-pair[1], pair[0]))
    return [slug for slug, _count in scored[:k]]


def degraded_ranker(snap: Snapshot, query: str, k: int) -> list[str]:
    """The negative control: grep's candidates, in alphabetical order."""
    return sorted(slug for slug, _count in _grep_candidates(snap, query))[:k]


RANKERS: dict[str, Ranker] = {
    "brainkit": brainkit_ranker,
    "grep": grep_ranker,
    "degraded": degraded_ranker,
}


def evaluate(
    brain_dir: Path,
    cases: Sequence[Case],
    ranker: str = "brainkit",
    split: str = "all",
    snapshot: Snapshot | None = None,
) -> Report:
    rank = RANKERS[ranker]
    snap = snapshot or Snapshot(brain_dir)
    chosen = [c for c in cases if split == "all" or c.split == split]
    results = [
        CaseResult(case, tuple(rank(snap, case.query, DEEP_K))) for case in chosen
    ]
    return Report(ranker=ranker, results=results)


@dataclass(frozen=True)
class Comparison:
    metric: str
    delta: float
    low: float
    high: float
    verdict: str


def compare(
    candidate: Report,
    baseline: Report,
    metric: str = "recall",
    resamples: int = 2000,
    seed: int = 7,
) -> Comparison:
    """Paired CLUSTER bootstrap of ``candidate - baseline`` over shared cases.

    Queries about the same evidence are not independent observations —
    nineteen paraphrases of one improved note would otherwise look like
    overwhelming evidence. Cases are grouped by their first relevant note,
    and whole groups are resampled.

    Verdicts, decided on the 95% interval: ``better`` (whole interval above
    zero), ``non-inferior`` (above minus the fixed margin), ``worse`` (whole
    interval below minus the margin), else ``inconclusive`` — which is an
    allowed answer, and the honest one on a small set.
    """
    base = {r.case.id: getattr(r, metric) for r in baseline.results}
    clusters: dict[str, list[float]] = {}
    for r in candidate.results:
        # Negative cases count: their Recall@5 is 1 for a correct abstention,
        # so a change that stops answering unanswerable questions is credited.
        if r.case.id in base:
            key = r.case.relevant[0] if r.case.relevant else r.case.id
            clusters.setdefault(key, []).append(getattr(r, metric) - base[r.case.id])
    if not clusters:
        return Comparison(metric, 0.0, 0.0, 0.0, "inconclusive")
    # One value per evidence note: its mean difference. Fewer than two notes
    # cannot support any verdict but "inconclusive".
    per_note = [_mean(group) for group in clusters.values()]
    if len(per_note) < 2:
        return Comparison(metric, _mean(per_note), 0.0, 0.0, "inconclusive")
    diffs = per_note
    rng = random.Random(seed)
    means = sorted(
        _mean([diffs[rng.randrange(len(diffs))] for _ in diffs])
        for _ in range(resamples)
    )
    low = means[int(0.025 * resamples)]
    high = means[int(0.975 * resamples) - 1]
    delta = _mean(diffs)
    if low > 0:
        verdict = "better"
    elif low > -NON_INFERIORITY_MARGIN:
        verdict = "non-inferior"
    elif high < -NON_INFERIORITY_MARGIN:
        verdict = "worse"
    else:
        verdict = "inconclusive"
    return Comparison(metric, delta, low, high, verdict)


def render(report: Report) -> str:
    """A human-readable table of a report's summary."""
    lines = [f"ranker: {report.ranker}  ({len(report.results)} cases)"]
    summary = report.summary()
    header = f"{'stratum':14} {'n':>4} " + " ".join(f"{m:>12}" for m in METRICS)
    lines.append(header)
    for name, row in summary.items():
        if "n" not in row:
            continue
        cells = " ".join(f"{row[m]:12.3f}" for m in METRICS)
        lines.append(f"{name:14} {int(row['n']):4d} {cells}")
    if "false_positive_rate" in summary.get("negative", {}):
        fp = summary["negative"]["false_positive_rate"]
        lines.append(f"negative false-positive rate: {fp:.3f}")
    return "\n".join(lines)


def misses(report: Report, limit: int = 10) -> list[str]:
    """The first ``limit`` failed cases, for diagnosis with --explain."""
    out: list[str] = []
    for result in report.results:
        if result.hit < 1:
            got = ", ".join(result.ranked[:3]) or "(nothing)"
            want = (
                "(no answer)"
                if result.case.negative
                else ", ".join(result.case.relevant[:2])
            )
            out.append(
                f"{result.case.id} [{result.case.stratum}] {result.case.query!r}: want {want}; got {got}"
            )
        if len(out) >= limit:
            break
    return out


def load_all_cases(directory: Path) -> list[Case]:
    """Every ``cases*.jsonl`` file in ``directory``, in name order."""
    cases: list[Case] = []
    for path in sorted(directory.glob("cases*.jsonl")):
        cases.extend(load_cases(path))
    return cases
