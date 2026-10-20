# 008 — Rung 2 (embeddings): built, measured, shipped OPT-IN, not default

**Trigger.** After Phase 3, held-out paraphrase Recall@5 trailed lexical by ~37
pp (~27 pp even with agent variants, decision 006): above the plan's 15 pp
trigger.

**What was built** (stdlib only — no new dependency):

- `sentence-transformers/static-retrieval-mrl-en-v1` (Apache-2.0), a static
  (lookup-table) model: first 256 Matryoshka dims, int8 per row, 7.8 MB. A
  stdlib BERT-uncased WordPiece tokenizer and mean-pooling encoder.
  `brainkit vectors pull` fetches the pinned revision (sha256-verified) and
  converts it; it is the only network access in brainkit.
- Section-level vectors (title > heading path prefixed), digest-keyed and
  re-embedded only on change, in `.brainkit/vectors/<model>@<rev>/` — a
  rebuildable projection. 22,575 sections of a 1,238-note brain: 29 s to build,
  9.3 MB, 2.7 s per vector search (pure-Python int8 cosine).
- Fusion with the lexical ranking: RRF (k = 60, top-rank bonus) or Basic
  Memory's max + 0.3·min; a "vector rescue" lets a strong semantic match (cosine
  ≥ τ) answer a query lexical abstention would have refused.
- The interchange contract (`vectors export` / `vectors import` /
  `search --query-vector`) for an EXTERNAL embedder: brainkit never runs that
  model and refuses stale digests, mixed dims and non-finite values.

**Measured** (candidate vs current lexical defaults, eval set v2):

| setting                      | dev Recall@5   | dev MRR             | held-out Recall@5   | held-out MRR        |
| ---------------------------- | -------------- | ------------------- | ------------------- | ------------------- |
| RRF w = 1.0                  | +0.014 n-i     | −0.042 inconclusive | +0.040 n-i          | −0.046 inconclusive |
| RRF w = 1.0, rescue 0.35     | +0.030 n-i     | −0.026 inconclusive | +0.056 n-i          | −0.030 inconclusive |
| RRF w = 0.5, rescue 0.35     | +0.030 n-i     | −0.005 inconclusive | +0.056 n-i          | −0.009 inconclusive |
| **RRF w = 0.3, rescue 0.35** | **+0.030 n-i** | **+0.004 n-i**      | **+0.056 n-i**      | **+0.009 n-i**      |
| RRF w = 0.5, rescue 0.45     | +0.014 n-i     | −0.021 inconclusive | +0.056 n-i          | −0.009 inconclusive |
| max+0.3·min, rescue 0.35     | +0.030 n-i     | −0.029 inconclusive | +0.020 inconclusive | −0.013 inconclusive |

(n-i = non-inferior.) At the best setting, by stratum:

| stratum                         | dev before → after        | held-out before → after   |
| ------------------------------- | ------------------------- | ------------------------- |
| paraphrase Hit@5                | 0.760 → **0.840** (+8 pp) | 0.600 → **0.650** (+5 pp) |
| lexical MRR                     | 0.868 → **0.784** (−8 pp) | 0.793 → 0.773             |
| title MRR, negatives, lifecycle | unchanged                 | unchanged                 |

**Decision: ship opt-in, keep lexical the default.** Non-inferior on both
splits, but below the plan's exit bar (+10 pp paraphrase at no regression), and
it costs exact-term queries 8 pp of dev MRR: the vector arm pushes
semantically-near notes above the one that literally contains the asked-for
terms. `search --vectors` / `context --vectors` use w = 0.3, rescue 0.35.

The cheaper lever for paraphrases remains agent-supplied variants (006, +8-12
pp, no model, no index). A stronger encoder (the plan's `[onnx]` extra:
bge-small, EmbeddingGemma 2) is the next experiment; it needs a new dependency
and therefore the owner's sign-off.
