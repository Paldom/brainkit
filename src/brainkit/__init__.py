"""brainkit: portable, human-readable agent brain in Git-native markdown."""

import json
import re
import unicodedata
from dataclasses import dataclass, field
from importlib.metadata import PackageNotFoundError, version

__all__ = ["Note", "frontmatter_block", "parse_note", "raw_frontmatter", "slugify"]

try:
    __version__ = version("brainkit")
except PackageNotFoundError:  # pragma: no cover - source tree without install
    __version__ = "0.0.0"

_SLUG_STRIP = re.compile(r"[^a-z0-9]+")


def _unquote(value: str) -> str:
    """Decode one frontmatter value written by :func:`brainkit.brain._yaml_value`.

    The emitter writes JSON, so the reader is ``json.loads``: a quoted string
    comes back as the bare string, and anything that is not JSON at all (a
    legacy plain scalar, or hand-written frontmatter) is returned untouched.

    Non-string JSON — ``tags: ["a", "b"]``, ``source_count: 25`` — keeps its
    raw text, because :class:`Note` metadata is a flat string mapping. A
    caller that wants the structure back calls ``json.loads`` on it; nothing
    silently stringifies a list into something that looks like one.
    """
    try:
        decoded = json.loads(value)
    except ValueError:
        return value
    return decoded if isinstance(decoded, str) else value


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


def frontmatter_block(text: str) -> str | None:
    """The raw text between the leading ``---`` fences, or None."""
    text = text.removeprefix("\ufeff")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 3)
    if end == -1:
        if not text.endswith("\n---"):
            return None
        end = len(text) - 4
    return text[4:end]


def raw_frontmatter(text: str) -> list[tuple[str, str]]:
    """Frontmatter as ``(key, raw value text)`` pairs, decoded but not typed.

    The value side is returned EXACTLY as written. :class:`Note` metadata is a
    flat string mapping, which cannot distinguish a value written as the JSON
    string ``"null"`` from one written as the JSON literal ``null`` — so any
    caller that rewrites frontmatter must work from this, not from
    ``Note.meta``, or a title of "null" becomes an actual null on the next
    rewrite.
    """
    block = frontmatter_block(text)
    if block is None:
        return []
    pairs: list[tuple[str, str]] = []
    for line in block.splitlines():
        key, sep, value = _split_key(line)
        if sep:
            pairs.append((key, value))
    return pairs


def _split_key(line: str) -> tuple[str, str, str]:
    """Split one frontmatter line into (key, ":", value).

    A key may itself be a quoted JSON string containing a colon, so the naive
    partition-on-first-colon has to be preceded by a scan of the quoted form.
    """
    if line.startswith('"'):
        try:
            decoder = json.JSONDecoder()
            key, index = decoder.raw_decode(line)
        except ValueError:
            key, index = None, 0
        if isinstance(key, str) and line[index:].startswith(":"):
            return key, ":", line[index + 1 :].strip()
    key, sep, value = line.partition(":")
    return key.strip(), sep, value.strip()


def parse_note(text: str) -> Note:
    """Parse a markdown document with optional ``---`` frontmatter.

    Frontmatter is a leading block of ``key: value`` lines between ``---``
    fences. Values are decoded to plain strings; a leading byte-order mark is
    tolerated, since an editor that adds one would otherwise make the whole
    block invisible.
    """
    # ponytail: flat key: value, LF line endings only — swap in a YAML parser
    # if nesting is ever needed; normalize CRLF upstream if Windows sources appear
    original = text
    text = text.removeprefix("\ufeff")
    if not text.startswith("---\n"):
        return Note(body=original)
    # closing fence = a line that is exactly "---" (mid-text or at EOF);
    # search from 3 so an empty frontmatter block ("---\n---\n") still closes
    end = text.find("\n---\n", 3)
    if end == -1:
        if text.endswith("\n---"):
            end = len(text) - 4
        else:
            return Note(body=original)
    meta: dict[str, str] = {}
    for line in text[4:end].splitlines():
        key, sep, value = _split_key(line)
        if sep:
            meta[key] = _unquote(value)
    body = text[end + 4 :]
    return Note(meta=meta, body=body.removeprefix("\n"))
