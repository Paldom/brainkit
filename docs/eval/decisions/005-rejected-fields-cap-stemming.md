# 005 — Rejected: field weights, per-run cap; stemming inconclusive (off)

All measured on the corrected harness (decision 000 addendum), candidate vs the
current defaults.

| change                                      | dev Recall@5                         | dev MRR             | held-out Recall@5 | held-out MRR | outcome                                                       |
| ------------------------------------------- | ------------------------------------ | ------------------- | ----------------- | ------------ | ------------------------------------------------------------- |
| description ×1.0 + tags ×0.5 as BM25 fields | +0.000                               | −0.001              | +0.000            | −0.005       | **rejected — code removed**                                   |
| at most 3 hits per research run             | −0.015                               | −0.011              | +0.014            | −0.002       | **rejected — code removed** (dev lexical Hit@5 0.931 → 0.897) |
| Harman S-stemmer (plurals)                  | +0.015 [−0.075, +0.100] inconclusive | −0.007 inconclusive | **+0.058 better** | +0.000       | **off** — inconclusive on the tuning split                    |

Stemming is the interesting one: it lifts paraphrase questions (dev Hit@5 0.720
→ 0.800) and held-out recall clearly, but on dev it halves the relational
stratum (0.667 → 0.333) and costs lexical MRR. With n = 6 relational dev cases
that may be noise; the rule says tune on dev, and dev says inconclusive, so it
stays a documented switch (`_STEM`) rather than a default. Revisit when the eval
grows.

The plan's 3.3 field weights were sized from other systems' corpora (title 4,
tags 3.5, description 2.5). Here descriptions are generated from the note's own
first paragraph, so they repeat body terms and add nothing.
