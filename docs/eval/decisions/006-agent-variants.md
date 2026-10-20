# 006 — Agent-supplied query variants (`--also`): shipped opt-in

**Change.** `search --also "<variant>"` (repeatable) fuses the query with
rephrasings the CALLING AGENT supplies: reciprocal-rank fusion, k = 60, the
original query at double weight, +0.05/+0.02 top-rank bonus, and the variants
ignored when the original's top hit is already confident (IDF coverage ≥ 0.85
and a ≥ 15% score gap). brainkit itself never rewrites a query — no model inside
it — and equal-weight expansion measured badly elsewhere (gbrain: 93% → 55%
recall).

**Measured on the paraphrase stratum** with two variants per question written
offline by `kimi` (`tests/eval/variants_paraphrase.jsonl`: one keyword-style,
one rephrasing; no facts added):

| split         | Recall@5 plain → fused     | verdict               | MRR plain → fused      | verdict      |
| ------------- | -------------------------- | --------------------- | ---------------------- | ------------ |
| dev (25)      | 0.720 → **0.840** (+0.120) | non-inferior          | 0.591 → 0.690 (+0.099) | **better**   |
| held-out (20) | 0.600 → **0.700** (+0.100) | inconclusive (n = 20) | 0.534 → 0.578          | non-inferior |

**Decision.** Ship as an option, default behaviour unchanged (a search without
`--also` is exactly what it was). The bundled skill tells agents to retry a weak
search with one keyword-style variant.

**Consequence for Phase 6.** Even with variants, held-out paraphrase Recall@5
(0.70) trails lexical (0.968) by ~27 pp — above the plan's 15 pp trigger for
rung 2 (embeddings). Without variants the gap is ~37 pp.
