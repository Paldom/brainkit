# 009 — Rejected: seeded personalized PageRank as a fusion arm

HippoRAG-style graph expansion: restart a personalized PageRank at the top-10
lexical hits (alpha 0.2, three iterations over the undirected link graph) and
fuse its ranking with the lexical one by RRF (k = 60). Candidate vs the current
defaults.

| PPR weight | dev Recall@5        | dev MRR          | held-out Recall@5   | held-out MRR     | outcome  |
| ---------- | ------------------- | ---------------- | ------------------- | ---------------- | -------- |
| 0.5        | +0.000 non-inferior | **−0.145 worse** | −0.008 non-inferior | **−0.156 worse** | rejected |
| 1.0        | −0.016 non-inferior | **−0.234 worse** | −0.008 inconclusive | **−0.228 worse** | rejected |

It does what it is for on the relational stratum (dev, n = 9: Hit@5 0.556 →
0.667, MRR 0.26 → 0.43 at weight 0.5), but it spreads mass from a well-ranked
hit to its parents and siblings everywhere else, pushing the right note down:
lexical dev MRR falls to 0.555 and paraphrase MRR to 0.506. Nine relational
cases cannot pay for that. Citation propagation (decision 003) already gives a
bounded lift to an unmatched parent without reordering the matched notes. The
code was removed. Revisit as a `context`-only expansion (a "related" list beside
the hits, not a re-ranking) if the relational stratum grows.
