# 002 — Title-phrase bonus (promoted, then REMOVED as redundant with 004)

**Original change.** A query that is a contiguous run of a note's title
multiplied its score by 1.5. Promoted on the first harness: title MRR 0.786 →
1.000 (dev), 0.833 → 1.000 (held-out), Recall@5 unchanged.

**Why it is gone.** On the corrected, regenerated eval set (v2, whole titles),
002 alone and 004 alone produce _identical_ results — title MRR 0.70 → 1.00 on
both splits, nothing else moves — and together they add nothing over either. 004
(a query equal to a note's whole title ranks it first) is the crisper rule and
needs no tuned constant, so it stays and the bonus was deleted. If partial-title
queries ("the first ten words of a long title") ever need help, measure this
again with cases for them.
