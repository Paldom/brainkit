import re

from hypothesis import given
from hypothesis import strategies as st

from brainkit import Note, parse_note, slugify


def test_slugify_basic() -> None:
    assert slugify("Hello, World!") == "hello-world"


def test_slugify_unicode_folds_to_ascii() -> None:
    assert slugify("Crème Brûlée") == "creme-brulee"


def test_slugify_empty_and_symbol_only() -> None:
    assert slugify("") == ""
    assert slugify("!!!") == ""


@given(st.text())
def test_slugify_output_is_safe(text: str) -> None:
    slug = slugify(text)
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug) or slug == ""


@given(st.text())
def test_slugify_idempotent(text: str) -> None:
    assert slugify(slugify(text)) == slugify(text)


def test_parse_note_without_frontmatter() -> None:
    note = parse_note("just a body\n")
    assert note.meta == {}
    assert note.body == "just a body\n"


def test_parse_note_with_frontmatter() -> None:
    note = parse_note("---\ntitle: My Note\ntags: a, b\n---\nbody text\n")
    assert note.meta == {"title": "My Note", "tags": "a, b"}
    assert note.body == "body text\n"
    assert note.title == "My Note"
    assert note.slug == "my-note"


def test_parse_note_empty_frontmatter() -> None:
    assert parse_note("---\n---\nbody") == Note(meta={}, body="body")


def test_parse_note_fence_must_be_exact() -> None:
    # "----" and "--- trailing" are not fences; only a line of exactly "---" is
    note = parse_note("---\ntitle: a\n----\nbody\n---\nrest")
    assert note.meta == {"title": "a"}
    assert note.body == "rest"
    unclosed = "---\nk: v\n--- trailing\nmore\n"
    assert parse_note(unclosed) == Note(body=unclosed)


def test_parse_note_fence_at_eof() -> None:
    assert parse_note("---\ntitle: t\n---") == Note(meta={"title": "t"})


def test_parse_note_unclosed_fence_is_body() -> None:
    text = "---\ntitle: broken\n"
    assert parse_note(text) == Note(body=text)


def test_parse_note_skips_lines_without_colon() -> None:
    note = parse_note("---\ntitle: ok\nnot a pair\n---\nb")
    assert note.meta == {"title": "ok"}


def test_note_explicit_slug_wins() -> None:
    note = Note(meta={"title": "Some Title", "slug": "custom"})
    assert note.slug == "custom"


def test_note_defaults() -> None:
    note = Note()
    assert note.title == ""
    assert note.slug == ""


@given(st.dictionaries(st.text(), st.text()), st.text())
def test_parse_note_never_raises(meta: dict[str, str], body: str) -> None:
    lines = "".join(f"{k}: {v}\n" for k, v in meta.items())
    parse_note(f"---\n{lines}---\n{body}")
