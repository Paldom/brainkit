# 001 — Abstain when nothing covers the question (promoted, threshold 0.3)

**Change.** `search` returns nothing when even its best hit covers less than 30%
of the query's IDF mass (`_ABSTAIN_BELOW = 0.3`). For the coverage ratio only, a
term no note contains is weighted as if one note did (its true IDF is the
maximum possible, which in a small brain made any question with one unfamiliar
word look unanswerable). `context` reports the abstention as a "no confident
match" retrieval gap.

**Rejected variant: a per-note gate** (`_MIN_IDF_COVERAGE = 0.5`, the
markdown-memory recipe). It removed every false positive and destroyed
natural-language questions — dev paraphrase Recall@5 0.760 → 0.120, verdict
`worse`. Paraphrases carry words the corpus never uses. Left at 0.

**Sweep on dev** (query-level, after the coverage floor):

| threshold  | dev Recall@5 Δ | verdict          | dev false-positive rate |
| ---------- | -------------- | ---------------- | ----------------------- |
| 0 (before) | —              | —                | 0.833                   |
| 0.25       | +0.000         | non-inferior     | 0.500                   |
| **0.30**   | **−0.014**     | **non-inferior** | **0.167**               |
| 0.35       | −0.027         | inconclusive     | 0.000                   |
| 0.40       | −0.041         | inconclusive     | 0.000                   |

**Held-out, 0.3 vs no abstention:** Recall@5 −0.016 [−0.048, +0.000]
non-inferior; MRR −0.003 non-inferior; false positives 1.000 → 0.167. The cost
is one paraphrase question per split whose only matching words were common ones.

**Caveat.** The negative stratum is 12 queries; the false-positive figure is
directional, not precise.
