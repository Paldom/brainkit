# 004 — A query equal to a note's whole title ranks that note first (promoted)

**Why 002 was not enough.** With whole titles in the title stratum (the review
found 7 of 10 cases had been truncated to ten words), one dev case still lost: a
report section titled "Data Quality Notes (<its topic>)" — the parent topic note
contains nearly every query word and carries the higher level prior, so it
out-scored the note the query literally names.

**Change.** A note whose entire title equals the query (after the same folding
as search) sorts ahead of every other hit; everything else keeps its score order
(`_EXACT_TITLE_FIRST = True`).

|          | dev title MRR | held-out title MRR | dev all MRR | Recall@5                |
| -------- | ------------- | ------------------ | ----------- | ----------------------- |
| 002 only | 0.929         | 1.000              | 0.699       | —                       |
| **+004** | **1.000**     | **1.000**          | 0.706       | unchanged (both splits) |

Dev MRR +0.007 [+0.000, +0.025] non-inferior; held-out identical.
