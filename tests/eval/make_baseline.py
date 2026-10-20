"""Re-pin tests/eval/baseline.json after an ACCEPTED ranking change.

    uv run python tests/eval/make_baseline.py "<why: decision file>"

Floors sit a small tolerance below the measured value (above, for the
false-positive rate). A ranking change that would move a metric past its
floor must re-pin here in the same commit, with a decision file saying why.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from brain_builder import build_brain  # noqa: E402

from brainkit.evaluate import evaluate, load_all_cases  # noqa: E402

TOLERANCE = 0.02


def main(reason: str) -> None:
    metrics: dict[str, dict[str, object]] = {}
    with tempfile.TemporaryDirectory() as tmp:
        brain = build_brain(Path(tmp))
        cases = load_all_cases(HERE)
        # Pinned PER SPLIT: a held-out regression must not hide behind a dev
        # gain in a combined number.
        for split in ("dev", "heldout"):
            summary = evaluate(brain, cases, "brainkit", split).summary()
            for stratum, row in summary.items():
                for metric, value in row.items():
                    if metric == "n":
                        continue
                    lower_is_better = metric == "false_positive_rate"
                    floor = value + TOLERANCE if lower_is_better else value - TOLERANCE
                    metrics[f"{split}.{stratum}.{metric}"] = {
                        "value": round(value, 4),
                        "floor": round(min(max(floor, 0.0), 1.0), 4),
                        "direction": "lower" if lower_is_better else "higher",
                    }
    commit = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True
    ).stdout.strip()
    (HERE / "baseline.json").write_text(
        json.dumps(
            {"measured_at": commit, "reason": reason, "metrics": metrics}, indent=1
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main(" ".join(sys.argv[1:]) or "baseline")
