"""Build the eval brain from the pinned corpus (shared by tests and scripts)."""

from __future__ import annotations

import os
from pathlib import Path

from brainkit.brain import (
    Corpus,
    ingest_notes,
    ingest_research_project,
    model_dir,
    vector_units,
)
from brainkit.vectors import StaticModel
from brainkit.vectors import build_index as build_vectors

HERE = Path(__file__).parent


def runs() -> list[Path]:
    return sorted(
        p
        for base in (HERE / "corpus", HERE / "synthetic")
        for p in base.iterdir()
        if (p / "result.json").is_file()
    )


def build_brain(root: Path) -> Path:
    brain = root / "brain"
    for run in runs():
        ingest_research_project(run, brain)
    # The lifecycle stratum: old/new decision pairs linked by supersession.
    for split in ("dev", "heldout"):
        ingest_notes(HERE / "lifecycle" / split, brain, namespace=f"lifecycle-{split}")
    if os.environ.get("BRAINKIT_MODEL_DIR"):
        # Rung 2 experiments: section vectors for the eval brain.
        model = StaticModel.load(model_dir())
        build_vectors(brain, model, vector_units(Corpus(brain)))
    return brain
