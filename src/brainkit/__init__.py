"""brainkit: portable, human-readable agent brain in Git-native markdown."""

import re
import unicodedata
from dataclasses import dataclass, field
from importlib.metadata import PackageNotFoundError, version

__all__ = ["Note", "parse_note", "slugify"]

try:
    __version__ = version("brainkit")
except PackageNotFoundError:  # pragma: no cover - source tree without install
    __version__ = "0.0.0"

_SLUG_STRIP = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    """Turn arbitrary text into a filesystem- and URL-safe kebab-case slug."""
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return _SLUG_STRIP.sub("-", ascii_text.lower()).strip("-")


@dataclass(frozen=True)
class Note:
    """A single markdown note: frontmatter metadata plus body text."""

    meta: dict[str, str] = field(default_factory=dict)
    body: str = ""

    @property
    def title(self) -> str:
        return self.meta.get("title", "")

    @property
    def slug(self) -> str:
        return self.meta.get("slug") or slugify(self.title)


def parse_note(text: str) -> Note:
    """Parse a markdown document with optional ``---`` frontmatter.

    Frontmatter is a leading block of ``key: value`` lines between ``---``
    fences. Values are kept as plain strings.
    """
    # ponytail: flat key: value, LF line endings only — swap in a YAML parser
    # if nesting is ever needed; normalize CRLF upstream if Windows sources appear
    if not text.startswith("---\n"):
        return Note(body=text)
    # closing fence = a line that is exactly "---" (mid-text or at EOF);
    # search from 3 so an empty frontmatter block ("---\n---\n") still closes
    end = text.find("\n---\n", 3)
    if end == -1:
        if text.endswith("\n---"):
            end = len(text) - 4
        else:
            return Note(body=text)
    meta: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()
    body = text[end + 4 :]
    return Note(meta=meta, body=body.removeprefix("\n"))
