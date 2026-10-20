# 000 — The baseline, and how decisions are made

_2026-10-20 · pinned in `tests/eval/baseline.json` at `f5aecc2` + working tree_

## The eval set

the case set over a pinned 189-note brain (`tests/eval/corpus/`, two real
researchkit runs trimmed to 25 materials per sub-project, plus two small
synthetic multilingual runs — one per split). Strata, each labelled by
construction:

| stratum      | n   | how it is built                                                                                                                                                                                                  |
| ------------ | --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| lexical      | 60  | seeded Kim & Croft field sampling: 2-3 tf-idf terms of one note + 1 noise term                                                                                                                                   |
| paraphrase   | 45  | written by `codex:gpt-6-astra` from the note body only, avoiding obvious keywords; independently matched back to its note by `kimi` (45/45 agreed); title-overlap filter (>70%) rejected 0; spot-checked by hand |
| relational   | 15  | from the citation graph: "which synthesis cites this source" / "what supports this topic"                                                                                                                        |
| title        | 10  | a note's title verbatim — the exact-title guard                                                                                                                                                                  |
| negative     | 12  | off-topic questions the brain cannot answer                                                                                                                                                                      |
| multilingual | 6   | Hungarian (with and without accents), German, Chinese, Japanese, French                                                                                                                                          |

Split into dev / held-out by research-run family (alternating in sorted order),
so near-duplicate evidence never straddles the two.

## Baseline (v0.2.0 ranking + the Unicode tokenizer)

|                              | brainkit      | grep          | degraded (negative control) |
| ---------------------------- | ------------- | ------------- | --------------------------- |
| Recall@5, all                | **0.794**     | 0.515         | 0.169                       |
| lexical                      | 0.950         | 0.900         | 0.233                       |
| paraphrase                   | 0.711         | 0.089         | 0.067                       |
| relational                   | 0.200         | 0.133         | 0.067                       |
| title (R@5 / MRR)            | 1.000 / 0.800 | 0.400 / 0.200 | 0 / 0                       |
| negative false-positive rate | 0.917         | 1.000         | 1.000                       |

brainkit vs grep, Recall@5: **+0.279 [+0.199, +0.360] → better**. The negative
control scores 0.169 ≤ ½ × 0.794: the eval can fail.

What it says, before any tuning:

- **Abstention is the worst gap**: 11 of 12 off-topic questions return hits.
- **Relational** questions are mostly unanswered (0.20) — the stratum graph
  signals are meant for.
- **Exact titles** are always in the top 5 but only #1 in 8 of 10 — the title
  guard (100% top-1) is not met.
- **Paraphrase trails lexical by 24 pp** — above the plan's 15 pp trigger for
  rung 2 (embeddings), _if_ it survives Phase 3.

## The rule for every ranking change

1. Implement behind a module constant, so old and new run in one process.
2. Measure on **dev** with `tests/eval/experiment.py`; tune only on dev.
3. Confirm on **held-out** once, with the paired bootstrap (2,000 resamples, 95%
   CI) on Recall@5 and MRR: promote if `better` or `non-inferior` (margin −5 pp,
   fixed before looking) AND no stratum floor breaks; otherwise delete the
   change. "Inconclusive" is reported as such.
4. Write the decision here as `NNN-<name>.md` with both tables, then re-pin
   `baseline.json` (`tests/eval/make_baseline.py`).

## Addendum — harness corrections after cross-review (same day)

The Phase 2 review found four defects in the harness itself; all fixed before
any further decision:

1. **"Recall@5" was Hit@5** (any relevant note in the top five). It is now
   reported as `hit`, and `recall` is the true fraction of relevant notes
   retrieved — they differ only on multi-answer (relational) cases.
2. **The bootstrap treated queries as independent.** Queries about the same
   evidence are not; it now resamples clusters keyed by the first relevant note.
3. **Evidence straddled the splits** (the multilingual sources were labelled by
   an artificial family). Splits now follow each case's evidence family, and the
   builder and `test_no_evidence_straddles_the_splits` refuse any leak.
4. **7 of 10 "exact-title" queries were truncated titles.** They are whole
   titles now (`test_title_cases_are_whole_titles`).

Decisions 001-003 re-measured on the corrected harness (candidate = the promoted
value, base = without it):

| decision             | dev Recall@5        | dev MRR             | held-out Recall@5   | held-out MRR        | still promoted?                         |
| -------------------- | ------------------- | ------------------- | ------------------- | ------------------- | --------------------------------------- |
| 001 abstention 0.3   | −0.015 non-inferior | −0.015 non-inferior | −0.014 non-inferior | −0.003 non-inferior | yes (FP 0.833/1.000 → 0.167/0.167)      |
| 002 title phrase 0.5 | +0.015 non-inferior | +0.005 non-inferior | +0.000              | +0.017 non-inferior | yes (held-out title MRR 0.611 → 1.000)  |
| 003 propagation 0.5  | +0.030 non-inferior | +0.015 non-inferior | +0.043 non-inferior | +0.024 non-inferior | yes (held-out relational 0.111 → 0.444) |

With cluster resampling the intervals are wider; 003's held-out MRR moves from
"better" to "non-inferior". The conclusions stand.
