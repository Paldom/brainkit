# 007 — Superseded notes rank below what replaced them (×0.5); trust labels

**Change.** A note carrying `superseded_by` keeps ranking — history questions
need it — but at half its score (`_SUPERSEDED_FACTOR = 0.5`) and labelled
`superseded`. An agent-distilled note (`derived_from`, no `verified` by a
`human:` actor) gets no level preference over its own evidence and is labelled
`derived`. `status: draft` notes are not returned unless asked for
(`--include-drafts`). Hygiene flags (`injection`, `hidden-chars`,
`hidden-markup`, `secret`) are computed labels, never stored, never hiding a
note.

**New stratum: lifecycle** (4 cases, `tests/eval/lifecycle/`): pairs of an old
and a new decision linked by `supersedes`/`superseded_by`; the query asks the
question both answer, and the CURRENT one is the label. Two pairs per split.

| split    | MRR without demotion (×1.0)       | MRR with ×0.5 | Recall@5   |
| -------- | --------------------------------- | ------------- | ---------- |
| dev      | 0.500 (the superseded note first) | **1.000**     | 1.000 both |
| held-out | 0.500                             | **1.000**     | 1.000 both |

No other stratum moves (no corpus note carries `superseded_by`). The
derived-note and draft rules are exercised by unit tests
(`tests/test_trust.py`); the eval corpus has no agent-written notes.
