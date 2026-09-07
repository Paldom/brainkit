from pathlib import Path

from hypothesis import settings

settings.register_profile("ci", max_examples=1000)
settings.register_profile("dev", max_examples=25)


def notes_in(directory: Path) -> list[Path]:
    """Concept documents in a level directory.

    ``index.md``/``log.md`` are OKF §3.1 reserved filenames — every level
    carries its own generated index — so a bare ``glob("*.md")`` would count
    the map as one of the territories.
    """
    return sorted(
        p for p in directory.glob("*.md") if p.name not in ("index.md", "log.md")
    )
