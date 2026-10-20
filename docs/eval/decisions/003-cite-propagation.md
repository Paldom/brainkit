# 003 — A run note inherits from what it cites, if it matched nothing itself (promoted, 0.5)

**Change.** After BM25, a domain or topic note whose own prose matched none of
the query terms gets half the score of its best-matching linked child
(`_CITE_PROPAGATION = 0.5`). It is the only way "which research run cites X?"
can surface the run: the run's synthesis rarely repeats a source's words. This
is the plan's graph signal (3.8), in the cheapest form the relational stratum
rewarded.

**Variants measured on dev (Recall@5 / MRR deltas vs no graph signal):**

| variant                                                  | relational R@5  | all R@5    | all MRR    | verdict                                         |
| -------------------------------------------------------- | --------------- | ---------- | ---------- | ----------------------------------------------- |
| propagate to every run note, 0.3                         | 0.33 → 0.67     | +0.014     | **−0.079** | inconclusive (MRR)                              |
| propagate to every run note, 0.6                         | 0.33 → 0.67     | −0.014     | **−0.178** | worse                                           |
| mutual-support bonus 0.2 (hit linked to another top hit) | 0.17 → 0.33     | +0.014     | −0.002     | non-inferior dev; **+0.000 held-out** → deleted |
| only-unmatched, 0.15                                     | 0.33 → 0.50     | +0.014     | +0.003     | non-inferior                                    |
| only-unmatched, 0.3                                      | 0.33 → 0.67     | +0.027     | +0.010     | non-inferior                                    |
| **only-unmatched, 0.5**                                  | **0.33 → 0.67** | **+0.027** | **+0.014** | non-inferior                                    |

Lifting run notes that _already_ match crowded out exact answers on every other
stratum, which is why the promoted form only lifts unmatched ones.

**Held-out, 0.5 only-unmatched:** Recall@5 +0.048 [+0.000, +0.111] non-inferior;
MRR **+0.026 [+0.003, +0.056] → better**.

The mutual-support code was removed, not left switched off.
