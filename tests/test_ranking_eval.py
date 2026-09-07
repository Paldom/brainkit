"""A ranking regression harness: P@1 and MRR over a labelled fixture brain.

Without this, every ranking change is unfalsifiable — you can only argue about
it. The corpus is built so each query has ONE defensible answer by
construction: the note that is actually about the thing asked for. Labels come
from how the fixture was written, not from what the ranker currently returns,
which is the only way a harness like this can catch a regression rather than
ratify one.

It is small on purpose. Twelve queries covering the families that break
differently — a term that names a title, a term buried in a long archive, a
concept spread across a synthesis, a query that should reach a primary source —
is enough to notice a regression. It is NOT enough to tune constants on; the
BM25 parameters and the level prior are deliberately left at their defaults
until there is a real labelled corpus.

Honest limitation: most expected notes carry the query terms in their title, so
this measures "does ranking still work at all", not "is ranking good". Current
baseline is P@1 1.000 / MRR 1.000 — the value of that is as a tripwire, not as
evidence the ranker is strong.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from brainkit.brain import search

# (query, slug fragment of the note that should win)
QUERIES: list[tuple[str, str]] = [
    # a query that names a source's title should reach that source
    ("kubernetes operator patterns", "kubernetes"),
    ("postgres vacuum tuning", "postgres"),
    # a concept the synthesis is about, not any single source
    ("what we concluded about caching", "caching-topic"),
    ("overall findings on storage engines", "storage-domain"),
    # a rare term appearing once, in one long archive
    ("zygomorphic", "rambling"),
    # a term the chatty archive repeats but the synthesis explains
    ("sharding", "sharding-topic"),
    # multi-word queries where coverage should decide
    ("write amplification lsm", "lsm"),
    ("replication lag monitoring", "replication"),
    # a title phrase, verbatim
    ("The Vacuum Problem", "postgres"),
    # a term only a report section carries
    ("consensus among reviewers", "--consensus"),
    # a domain-level question
    ("how the storage work is organized", "storage-domain"),
    # a source-level fact nothing summarizes
    ("port 5432 default", "postgres"),
]


def _material(title: str, url: str, body: str, published: str = "2026-01-01") -> str:
    return (
        f"---\ntitle: {json.dumps(title)}\nurl: {url}\n"
        f"source_type: web\npublished: {published}\n---\n\n{body}\n"
    )


@pytest.fixture(scope="module")
def labelled_brain(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """A boosted run whose notes have unambiguous subjects."""
    root = tmp_path_factory.mktemp("eval")
    parent = root / "storage-domain"
    (parent / "subprojects").mkdir(parents=True)
    (parent / "result.json").write_text(
        json.dumps(
            {
                "overarching_topic": "storage-domain: how the storage work is organized",
                "super_summary": (
                    "The storage programme is organized into two workstreams, "
                    "caching and sharding, each with its own findings."
                ),
            }
        ),
        encoding="utf-8",
    )
    (parent / "report.md").write_text(
        "## Consensus\n\nThere is consensus among reviewers that the two "
        "workstreams should stay separate. " * 3,
        encoding="utf-8",
    )

    def leaf(name: str, topic: str, summary: str, materials: dict[str, str]) -> None:
        project = parent / "subprojects" / name
        (project / "materials").mkdir(parents=True)
        (project / "result.json").write_text(
            json.dumps({"topic": topic, "meta_summary": summary}), encoding="utf-8"
        )
        for filename, text in materials.items():
            (project / "materials" / filename).write_text(text, encoding="utf-8")

    leaf(
        "sub_01_caching",
        "caching-topic: what we concluded about caching",
        "We concluded that caching wins when the working set is small.",
        {
            "001-kubernetes.md": _material(
                "kubernetes: Operator Patterns",
                "https://k.test/1",
                "Operator patterns for kubernetes workloads. " * 8,
            ),
            "002-rambling.md": _material(
                "rambling: a very long forum thread",
                "https://f.test/1",
                "opinion " * 600 + " zygomorphic " + "opinion " * 600,
            ),
        },
    )
    leaf(
        "sub_02_sharding",
        "sharding-topic: sharding and replication findings",
        "Sharding is the answer once one node stops fitting the data. "
        "Replication lag monitoring is the operational cost.",
        {
            "001-postgres.md": _material(
                "postgres: The Vacuum Problem",
                "https://p.test/1",
                "Vacuum tuning in postgres, and the port 5432 default. " * 8,
            ),
            "002-lsm.md": _material(
                "lsm: write amplification in log-structured merge trees",
                "https://l.test/1",
                "Write amplification is the dominant cost in lsm trees. " * 8,
            ),
            "003-replication.md": _material(
                "replication: lag monitoring in practice",
                "https://r.test/1",
                "Monitoring replication lag across replicas. " * 8,
            ),
        },
    )
    brain = root / "brain"
    from brainkit.brain import ingest_research_project

    ingest_research_project(parent, brain)
    return brain


def _rank_of(brain: Path, query: str, expect: str) -> int:
    """1-based rank of the expected note, or 0 when it is not in the top 10."""
    for position, hit in enumerate(search(brain, query, limit=10), start=1):
        if expect in hit.path.stem:
            return position
    return 0


def test_precision_at_1_does_not_regress(labelled_brain: Path) -> None:
    ranks = {q: _rank_of(labelled_brain, q, expect) for q, expect in QUERIES}
    hits_at_1 = [q for q, rank in ranks.items() if rank == 1]
    missed = {q: rank for q, rank in ranks.items() if rank != 1}
    precision = len(hits_at_1) / len(QUERIES)
    # Measured baseline: 1.000 on this corpus. Pinned at the measured value on
    # purpose — a threshold set comfortably below what the ranker actually does
    # cannot catch the regression it exists to catch. A change that costs a
    # query should move this line in the same commit, with a reason.
    assert precision >= 1.0, f"P@1 {precision:.3f} (baseline 1.000) — {missed}"


def test_mean_reciprocal_rank_does_not_regress(labelled_brain: Path) -> None:
    ranks = [_rank_of(labelled_brain, q, expect) for q, expect in QUERIES]
    mrr = sum(1 / rank for rank in ranks if rank) / len(ranks)
    assert mrr >= 1.0, f"MRR {mrr:.3f} (baseline 1.000) — ranks {ranks}"


def test_every_query_finds_its_answer_somewhere(labelled_brain: Path) -> None:
    """Recall first: a ranking argument is moot if the note never surfaces."""
    missing = [q for q, expect in QUERIES if not _rank_of(labelled_brain, q, expect)]
    assert missing == [], f"not in the top 10 at all: {missing}"


def test_a_rare_term_beats_a_long_chatty_archive(labelled_brain: Path) -> None:
    """The specific failure BM25 length normalization exists to prevent."""
    hits = search(labelled_brain, "zygomorphic")
    assert hits and "rambling" in hits[0].path.stem
    # ...but a common term in that same archive must not let it win everything
    assert "rambling" not in search(labelled_brain, "sharding")[0].path.stem
