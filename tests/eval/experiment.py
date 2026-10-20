"""Measure a ranking change against the current defaults, dev then held-out.

    uv run python tests/eval/experiment.py _MIN_IDF_COVERAGE=0.5 [_X=...] \
        [--base _X=...]

Arguments before ``--base`` override brainkit.brain module constants for the
CANDIDATE; arguments after it override them for the BASELINE. Each side
starts from the defaults in the source — the baseline's overrides never leak
into the candidate. Two identical configurations are refused: a +0.000 must
mean "no effect", never "measured the same thing twice". Prints both
summaries per split and the paired-bootstrap verdicts (Recall@5, MRR).
Tune on dev; look at held-out once, then write the decision record.
"""

from __future__ import annotations

import ast
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from brain_builder import build_brain  # noqa: E402

import brainkit.brain as brain_module  # noqa: E402
from brainkit.evaluate import (  # noqa: E402
    Case,
    Report,
    compare,
    evaluate,
    load_all_cases,
    render,
)


def _parse(args: list[str]) -> dict[str, object]:
    out: dict[str, object] = {}
    for arg in args:
        name, _, value = arg.partition("=")
        if not hasattr(brain_module, name):
            raise SystemExit(f"no such constant: {name}")
        out[name] = ast.literal_eval(value)
    return out


def _run(
    brain: Path, cases: list[Case], split: str, overrides: dict[str, object]
) -> Report:
    saved = {k: getattr(brain_module, k) for k in overrides}
    for k, v in overrides.items():
        setattr(brain_module, k, v)
    try:
        return evaluate(brain, cases, "brainkit", split)
    finally:
        for k, v in saved.items():
            setattr(brain_module, k, v)


def main(argv: list[str]) -> None:
    cut = argv.index("--base") if "--base" in argv else len(argv)
    overrides = _parse(argv[:cut])
    base_overrides = _parse(argv[cut + 1 :])

    def effective(overrides: dict[str, object]) -> dict[str, object]:
        names = set(overrides) | set(base_overrides)
        return {n: overrides.get(n, getattr(brain_module, n)) for n in names}

    if effective(overrides) == effective(base_overrides):
        raise SystemExit("candidate and baseline are the same configuration")
    cases = load_all_cases(HERE)
    with tempfile.TemporaryDirectory() as tmp:
        brain = build_brain(Path(tmp))
        for split in ("dev", "heldout"):
            base = _run(brain, cases, split, base_overrides)
            cand = _run(brain, cases, split, overrides)
            print(f"===== {split}  candidate: {overrides}  base: {base_overrides}")
            print(render(cand))
            print("--- baseline")
            print(render(base))
            for metric in ("recall", "mrr"):
                v = compare(cand, base, metric)
                print(
                    f"{split} {metric}: {v.delta:+.3f} [{v.low:+.3f}, {v.high:+.3f}]"
                    f" -> {v.verdict}"
                )


if __name__ == "__main__":
    main(sys.argv[1:])
