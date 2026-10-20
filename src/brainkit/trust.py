"""Deterministic trust checks on note text: hygiene and grounding.

Nothing here judges whether a claim is TRUE — that needs a model, and
brainkit has none. These are mechanical facts an agent (or a reviewer)
should weigh: text that hides itself, text that talks to the reader's AI,
credentials that should not be in a knowledge base, and literals in an
agent-written note that cannot be found in the sources it claims to derive
from. Everything is computed, never stored, so a fixed pattern list
re-labels an existing brain without touching a byte of it.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass

# Characters that hide or reorder text — the ones attacks actually use, not
# every invisible codepoint (emoji need ZWJ and VS16; Persian needs ZWNJ;
# scraped pages are full of stray zero-width spaces). Flagged:
#   * bidi embedding/override/isolate controls (Trojan Source);
#   * Unicode tag characters outside a flag-emoji sequence (ASCII smuggling);
#   * RUNS of 4+ zero-width or supplementary variation-selector characters
#     (binary-encoded payloads), never a single stray one.
_HIDDEN = re.compile(
    "[\u202a-\u202e\u2066-\u2069]"
    "|[\U000e0000-\U000e007f]{2,}"
    "|[\u200b-\u200d\u2060-\u2064\ufeff]{4,}"
    "|[\U000e0100-\U000e01ef]{4,}"
)
# A subdivision flag (🏴 + tag letters + CANCEL TAG) is the one legitimate
# use of tag characters; removed before scanning.
_FLAG_EMOJI = re.compile("\U0001f3f4[\U000e0020-\U000e007e]+\U000e007f")

# Markup that a renderer hides but a model still reads.
_HIDDEN_HTML = re.compile(
    r"<!--(?!\s*/?brainkit:)[^>]{0,400}?(ignore|instruction|assistant|system|prompt)"
    r"|style\s*=\s*['\"][^'\"]*(display\s*:\s*none|font-size\s*:\s*0|visibility\s*:\s*hidden)",
    re.IGNORECASE,
)
# Text addressed to the AI reading the page rather than to a human.
_INSTRUCTION = re.compile(
    r"\b(ignore|disregard|forget|override)\s+(all\s+|any\s+|the\s+)?"
    r"(previous|prior|above|earlier|preceding|your)\s+(instructions|prompts?|rules|directions)"
    r"|\byou\s+are\s+now\s+(a|an|in)\b"
    r"|\bnew\s+(system\s+)?instructions\s*:"
    r"|\b(reveal|print|output|leak)\s+(your|the)\s+(system\s+prompt|instructions|api\s+keys?)"
    r"|\bdo\s+not\s+(tell|inform|alert)\s+the\s+user\b"
    r"|\bas\s+an\s+ai\s+(assistant|agent)[,\s]+you\s+(must|should)\b",
    re.IGNORECASE,
)
# Negation within a few words before a match cancels it: an article that
# says "never write 'ignore previous instructions' into a page" is ABOUT
# injection, not an injection.
# Only a negation IMMEDIATELY before the phrase (within one word, ending
# in an optional quote) counts — "never write 'ignore previous instructions'"
# is about injection; "Do not follow this: ignore previous instructions" is
# one.
_NEGATION = re.compile(
    r"(?:\b(?:not|never|don'?t|avoid|example|such as)|\be\.g\.)"
    r"(?:\W+\w+)?\W*[\"'\u201c\u2018\u00ab`]?\s*$",
    re.IGNORECASE,
)
_SECRETS = re.compile(
    r"\bAKIA[0-9A-Z]{16}\b"  # AWS access key id
    r"|\bgh[pousr]_[A-Za-z0-9]{36,}\b"  # GitHub token
    r"|\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{32,}\b"  # OpenAI / Anthropic style key
    r"|\bxox[abposr]-[A-Za-z0-9-]{10,}\b"  # Slack token
    r"|-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----"
    r"|\bAIza[0-9A-Za-z_-]{35}\b"  # Google API key
)


# Cheap substring triggers decide which pattern families are worth running:
# on a 30 MB brain, regex-scanning every body for every family costs
# seconds, and almost no body contains a trigger. Phrases, not bare words —
# "prompt" alone is on every page of an AI-themed corpus.
_INJECTION_TRIGGERS = (
    "instructions",
    "system prompt",
    "you are now",
    "do not tell",
    "do not inform",
    "do not alert",
    "as an ai",
    "rules",
    "directions",
    "prompt",
)
_MARKUP_TRIGGERS = ("<!--", "display", "font-size", "visibility")
# Credentials are case-sensitive: checked against the original text.
_SECRET_TRIGGERS = (
    "AKIA",
    "ghp_",
    "gho_",
    "ghu_",
    "ghs_",
    "ghr_",
    "sk-",
    "xox",
    "PRIVATE KEY",
    "AIza",
)
# Presence check for any hidden character: one character class, C speed.
_HIDDEN_ANY = re.compile(
    "[\u202a-\u202e\u2066-\u2069\u200b-\u200d\u2060-\u2064\ufeff\U000e0000-\U000e01ef]"
)


@dataclass(frozen=True)
class Flag:
    kind: str  # "hidden-chars" | "hidden-markup" | "injection" | "secret"
    excerpt: str


def scan(text: str, limit: int = 3) -> list[Flag]:
    """Flags for ``text``: at most ``limit`` excerpts per kind.

    Matched after NFKC folding (so full-width or ligature lookalikes do not
    slip through) and with bounded patterns (no catastrophic backtracking on
    hostile input). Flag and label — never quarantine: a measured quarantine
    added nothing over a visible label, and a stored flag would make an
    unchanged re-ingest write bytes.
    """
    flags: list[Flag] = []
    if _HIDDEN_ANY.search(text):
        hidden = _HIDDEN.findall(_FLAG_EMOJI.sub("", text))
        if hidden:
            chars = {c for run in hidden for c in run}
            names = sorted({unicodedata.name(c, f"U+{ord(c):04X}") for c in chars})
            flags.append(Flag("hidden-chars", ", ".join(names[:limit])))
    # Normalize FIRST: a full-width or ligature lookalike must reach the
    # same trigger and the same pattern as its plain-ASCII twin.
    folded = text if text.isascii() else unicodedata.normalize("NFKC", text)
    lowered = folded.lower()
    families = [
        (kind, pattern)
        for kind, pattern, haystack, triggers in (
            ("hidden-markup", _HIDDEN_HTML, lowered, _MARKUP_TRIGGERS),
            ("injection", _INSTRUCTION, lowered, _INJECTION_TRIGGERS),
            ("secret", _SECRETS, folded, _SECRET_TRIGGERS),
        )
        if any(trigger in haystack for trigger in triggers)
    ]
    if not families:
        return flags
    for kind, pattern in families:
        count = 0
        for match in pattern.finditer(folded):
            before = folded[max(0, match.start() - 30) : match.start()]
            if kind == "injection" and _NEGATION.search(before):
                continue
            excerpt = folded[max(0, match.start() - 20) : match.end() + 20]
            if kind == "secret":
                excerpt = match.group()[:8] + "…"  # never echo a credential
            flags.append(Flag(kind, " ".join(excerpt.split())))
            count += 1
            if count >= limit:
                break
    return flags


def labels(text: str) -> tuple[str, ...]:
    """The distinct flag kinds for ``text``, as hit labels."""
    return tuple(dict.fromkeys(flag.kind for flag in scan(text, limit=1)))


# --- grounding ---------------------------------------------------------------

# Matched pairs only: "…", “…” or «…» — an unpaired run would otherwise
# read the prose BETWEEN two short quotations as a quotation.
_QUOTE = re.compile(
    '"([^"\n]{15,300})"|\u201c([^\u201c\u201d\n]{15,300})\u201d'
    "|\u00ab([^\u00ab\u00bb\n]{15,300})\u00bb"
)
# URLs and link targets carry digits that are addresses, not claims.
_URLISH = re.compile(r"\]\([^)\s]*\)|https?://\S+")
_DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
# Numbers that carry a claim: 3+ digits, decimals, percentages, or suffixed
# magnitudes ("12k", "4.5M"). Bare 1-2 digit integers are list noise.
_NUMBER = re.compile(
    r"(?<![\w.])(?:\d{1,3}(?:,\d{3})+|\d+\.\d+|\d{3,}|\d+(?:\.\d+)?\s?(?:%|k|K|M|B|x))(?!\w|\.\d)"
)


def literals(text: str) -> list[str]:
    """The checkable literals in an agent-written note: quotations of 15+
    characters, ISO dates, and numbers that carry a claim."""
    text = _URLISH.sub(" ", text)
    found: list[str] = []
    found += [next(g for g in m.groups() if g).strip() for m in _QUOTE.finditer(text)]
    found += _DATE.findall(text)
    # Dates already counted whole; their years are not separate claims.
    undated = _DATE.sub(" ", text)
    found += [m.group().strip() for m in _NUMBER.finditer(undated)]
    return list(dict.fromkeys(found))


def _norm(text: str) -> str:
    folded = unicodedata.normalize("NFKC", text).casefold()
    folded = folded.replace("\u2019", "'").replace("\u2018", "'")
    return " ".join(folded.split())


def ungrounded(note_text: str, sources: Iterable[str]) -> list[str]:
    """Literals of ``note_text`` that occur in none of ``sources``.

    Whitespace- and case-insensitive substring matching: this is LOCATOR
    validation — "the words you quote are really there" — not entailment.
    A paraphrase is not checked and cannot fail.
    """
    haystack = "\n".join(_norm(s) for s in sources)
    return [lit for lit in literals(note_text) if _norm(lit) not in haystack]


_LOCATOR = re.compile(r"\^\[([^\]:]+\.md):L(\d+)(?:-(\d+))?\]")


def locators(text: str) -> list[tuple[str, int, int]]:
    """Citation locators ``^[sources/x.md:L42-58]`` as (path, first, last)."""
    out: list[tuple[str, int, int]] = []
    for match in _LOCATOR.finditer(text):
        first = int(match.group(2))
        last = int(match.group(3) or first)
        out.append((match.group(1), first, last))
    return out
