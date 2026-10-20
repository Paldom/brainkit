"""Rung 2: static embeddings in pure Python — an optional, rebuildable layer.

A *static* embedding model is a lookup table: each WordPiece token has a
vector, and a text's vector is the mean of its tokens' vectors. No neural
network runs at query time, so the whole encoder is the standard library:
a BERT WordPiece tokenizer, an int8 table read with ``array``, and a mean.

The model is ``sentence-transformers/static-retrieval-mrl-en-v1``
(Apache-2.0), truncated to its first 256 dimensions (it is trained
Matryoshka-style, so prefixes are meaningful) and quantized per row to int8:
about 7.8 MB instead of 125 MB. ``brainkit vectors pull`` fetches the
original once (sha256-pinned) and converts it; nothing is downloaded
otherwise, and without a model every command works exactly as before.

Vectors are a projection: ``<brain>/.brainkit/vectors/<model>@<rev>/``
holds one row per note SECTION (heading path prefixed with the title),
keyed by the section's content digest, so a rebuild re-embeds only what
changed. Delete the directory and nothing is lost.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import struct
import tempfile
import unicodedata
import urllib.request
from array import array
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

MODEL_ID = "sentence-transformers/static-retrieval-mrl-en-v1"
MODEL_REVISION = "f60985c706f192d45d218078e49e5a8b6f15283a"
MODEL_NAME = f"static-retrieval-mrl-en-v1@{MODEL_REVISION[:8]}"
_FILES = {
    "0_StaticEmbedding/model.safetensors": (
        "164fc63ee9f9267be7378fcbd7df99d09788a2f45244c92aa99ae5a574925716"
    ),
    "0_StaticEmbedding/tokenizer.json": (
        "d241a60d5e8f04cc1b2b3e9ef7a4921b27bf526d9f6050ab90f9267a1f9e5c66"
    ),
}
DIMS = 256
INDEX_VERSION = 1


def default_model_dir() -> Path:
    return Path.home() / ".cache" / "brainkit" / "models" / MODEL_NAME


# --- the tokenizer (BERT uncased WordPiece, as the model's tokenizer.json) --


def _is_punctuation(char: str) -> bool:
    code = ord(char)
    if 33 <= code <= 47 or 58 <= code <= 64 or 91 <= code <= 96 or 123 <= code <= 126:
        return True
    return unicodedata.category(char).startswith("P")


def _is_cjk(code: int) -> bool:
    return (
        0x4E00 <= code <= 0x9FFF
        or 0x3400 <= code <= 0x4DBF
        or 0x20000 <= code <= 0x2A6DF
        or 0xF900 <= code <= 0xFAFF
        or 0x2F800 <= code <= 0x2FA1F
    )


def basic_tokens(text: str) -> list[str]:
    """BertNormalizer + BertPreTokenizer: clean, lowercase, strip accents
    (the uncased convention), isolate CJK characters, split punctuation."""
    out: list[str] = []
    word: list[str] = []

    def flush() -> None:
        if word:
            out.append("".join(word))
            word.clear()

    text = unicodedata.normalize("NFD", text.lower())
    for char in text:
        code = ord(char)
        if code == 0 or code == 0xFFFD or unicodedata.category(char) == "Mn":
            continue
        if char.isspace() or unicodedata.category(char) in ("Cc", "Cf"):
            flush()
        elif _is_punctuation(char) or _is_cjk(code):
            flush()
            out.append(char)
        else:
            word.append(char)
    flush()
    return out


class WordPiece:
    def __init__(self, vocab: dict[str, int], unk: str = "[UNK]") -> None:
        self.vocab = vocab
        self.unk = vocab.get(unk, 0)

    def ids(self, text: str) -> list[int]:
        ids: list[int] = []
        for word in basic_tokens(text):
            if len(word) > 100:
                ids.append(self.unk)
                continue
            start, pieces = 0, []
            while start < len(word):
                end = len(word)
                found = None
                while start < end:
                    piece = word[start:end] if start == 0 else "##" + word[start:end]
                    if piece in self.vocab:
                        found = self.vocab[piece]
                        break
                    end -= 1
                if found is None:
                    pieces = [self.unk]
                    break
                pieces.append(found)
                start = end
            ids.extend(pieces)
        return ids


# --- the model -----------------------------------------------------------


@dataclass
class StaticModel:
    tokenizer: WordPiece
    table: array[int]  # int8 rows, DIMS each
    scales: array[float]  # float32, one per row
    name: str = MODEL_NAME

    @classmethod
    def load(cls, model_dir: Path) -> StaticModel:
        meta = json.loads((model_dir / "meta.json").read_text(encoding="utf-8"))
        if meta.get("dims") != DIMS:
            raise ValueError(
                f"{model_dir}: expected {DIMS} dims, found {meta.get('dims')}"
            )
        vocab = {
            line: i
            for i, line in enumerate(
                (model_dir / "vocab.txt").read_text(encoding="utf-8").split("\n")
            )
        }
        table = array("b")
        table.frombytes((model_dir / "vectors.i8").read_bytes())
        scales = array("f")
        scales.frombytes((model_dir / "scales.f32").read_bytes())
        return cls(WordPiece(vocab), table, scales, str(meta.get("name", MODEL_NAME)))

    def encode(self, text: str) -> list[float]:
        """Mean of the text's token vectors, L2-normalized (zero if no token)."""
        counts = Counter(self.tokenizer.ids(text))
        total = [0.0] * DIMS
        for token, count in counts.items():
            weight = self.scales[token] * count
            row = self.table[token * DIMS : (token + 1) * DIMS]
            total = [t + weight * v for t, v in zip(total, row, strict=True)]
        norm = math.sqrt(sum(v * v for v in total))
        return [v / norm for v in total] if norm else total


def convert(source_dir: Path, out_dir: Path, *, dims: int = DIMS) -> Path:
    """sentence-transformers static model -> int8 table brainkit can load.

    Reads the safetensors header by hand (8-byte length + JSON) and the
    float32 rows directly — no numpy, no safetensors package.
    """
    weights = source_dir / "model.safetensors"
    tokenizer = json.loads((source_dir / "tokenizer.json").read_text(encoding="utf-8"))
    with weights.open("rb") as handle:
        header_len = struct.unpack("<Q", handle.read(8))[0]
        header = json.loads(handle.read(header_len))
        tensor = header["embedding.weight"]
        if tensor["dtype"] != "F32":
            raise ValueError(f"unexpected dtype {tensor['dtype']}")
        rows, width = tensor["shape"]
        start = 8 + header_len + tensor["data_offsets"][0]
        table: array[int] = array("b")
        scales: array[float] = array("f")
        handle.seek(start)
        for _ in range(rows):
            row = array("f")
            row.frombytes(handle.read(width * 4))
            head = row[:dims]
            scale = max((abs(v) for v in head), default=0.0) / 127 or 1.0
            table.extend(max(-127, min(127, round(v / scale))) for v in head)
            scales.append(scale)
    vocab = tokenizer["model"]["vocab"]
    ordered = sorted(vocab, key=lambda token: vocab[token])
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "vectors.i8").write_bytes(table.tobytes())
    (out_dir / "scales.f32").write_bytes(scales.tobytes())
    (out_dir / "vocab.txt").write_text("\n".join(ordered), encoding="utf-8")
    (out_dir / "meta.json").write_text(
        json.dumps(
            {
                "name": MODEL_NAME,
                "model": MODEL_ID,
                "revision": MODEL_REVISION,
                "dims": dims,
                "dtype": "int8-per-row",
                "license": "Apache-2.0",
            },
            indent=1,
        )
        + "\n",
        encoding="utf-8",
    )
    return out_dir


def pull(out_dir: Path | None = None) -> Path:
    """Download the pinned model files (sha256-verified) and convert them.

    The ONLY network access in brainkit, and only when explicitly asked for.
    """
    target = out_dir or default_model_dir()
    raw = target / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    base = f"https://huggingface.co/{MODEL_ID}/resolve/{MODEL_REVISION}/"
    for name, digest in _FILES.items():
        path = raw / Path(name).name
        if not path.is_file() or _sha256(path) != digest:
            with urllib.request.urlopen(base + name, timeout=120) as response:
                path.write_bytes(response.read())
        if _sha256(path) != digest:
            path.unlink()
            raise ValueError(f"{name}: checksum mismatch — refusing to use it")
    return convert(raw, target)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# --- the index -----------------------------------------------------------


def index_dir(brain_dir: Path, model: StaticModel) -> Path:
    return brain_dir / ".brainkit" / "vectors" / model.name


@dataclass
class VectorIndex:
    ids: list[tuple[str, str, str]]  # (slug, section path, digest)
    vectors: array[int]  # int8, `dims` per row
    scales: array[float]  # float32 per row
    dims: int = DIMS

    def rank(
        self,
        query: Sequence[float],
        limit: int,
        fresh: set[tuple[str, str, str]] | None = None,
    ) -> list[tuple[str, float]]:
        """Notes by their best section's cosine with ``query`` (best first).

        With ``fresh`` (the current (slug, section, digest) keys), a row whose
        section has changed since it was embedded is skipped: a stale vector
        would rank the note's NEW text by its OLD meaning.
        """
        best: dict[str, float] = {}
        width = self.dims
        for row, key in enumerate(self.ids):
            if fresh is not None and key not in fresh:
                continue
            slug = key[0]
            vec = self.vectors[row * width : (row + 1) * width]
            score = self.scales[row] * sum(
                q * v for q, v in zip(query, vec, strict=True)
            )
            if score > best.get(slug, -2.0):
                best[slug] = score
        return sorted(best.items(), key=lambda kv: (-kv[1], kv[0]))[:limit]


def load_index_named(brain_dir: Path, name: str) -> VectorIndex | None:
    """The vector index stored under ``name``, or None if absent/inconsistent."""
    if not name:
        return None
    directory = brain_dir / ".brainkit" / "vectors" / name
    try:
        meta = json.loads((directory / "meta.json").read_text(encoding="utf-8"))
        if not isinstance(meta, dict):
            return None
        dims = int(meta.get("dims", 0))
        if meta.get("version") != INDEX_VERSION or dims <= 0:
            return None
        ids: list[tuple[str, str, str]] = []
        for line in (directory / "ids.jsonl").read_text(encoding="utf-8").splitlines():
            slug, section, digest = json.loads(line)
            ids.append((str(slug), str(section), str(digest)))
        vectors: array[int] = array("b")
        vectors.frombytes((directory / "vectors.i8").read_bytes())
        scales: array[float] = array("f")
        scales.frombytes((directory / "scales.f32").read_bytes())
    except (OSError, ValueError, TypeError):
        return None
    if len(scales) != len(ids) or len(vectors) != len(ids) * dims:
        return None
    # A torn write (or a reader racing a writer) pairs one generation's ids
    # with another's vectors; meta.json, written last, pins the checksum.
    if meta.get("checksum") != _checksum(ids, vectors, scales):
        return None
    return VectorIndex(ids, vectors, scales, dims)


def load_index(brain_dir: Path, model: StaticModel) -> VectorIndex | None:
    index = load_index_named(brain_dir, model.name)
    return index if index is not None and index.dims == DIMS else None


def _quantize(vector: Sequence[float]) -> tuple[list[int], float]:
    scale = max((abs(v) for v in vector), default=0.0) / 127 or 1.0
    return [max(-127, min(127, round(v / scale))) for v in vector], scale


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def unit_keys(units: Iterable[tuple[str, str, str]]) -> set[tuple[str, str, str]]:
    """The (slug, section, digest) keys of the current sections."""
    return {(slug, section, _digest(text)) for slug, section, text in units}


def _checksum(
    ids: Sequence[tuple[str, str, str]], vectors: array[int], scales: array[float]
) -> str:
    digest = hashlib.sha256(json.dumps([list(key) for key in ids]).encode("utf-8"))
    digest.update(vectors.tobytes())
    digest.update(scales.tobytes())
    return digest.hexdigest()


# An index directory name: one path component on every platform.
_MODEL_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._@+-]{0,127}")


def build_index(
    brain_dir: Path, model: StaticModel, units: Iterable[tuple[str, str, str]]
) -> tuple[int, int]:
    """(Re)build the section vectors; returns (embedded, reused).

    ``units`` are (slug, section path, text). A unit whose digest is already
    in the old index is reused, not re-embedded.
    """
    old = load_index(brain_dir, model)
    reuse: dict[tuple[str, str, str], tuple[array[int], float]] = {}
    if old is not None:
        for row, key in enumerate(old.ids):
            reuse[key] = (old.vectors[row * DIMS : (row + 1) * DIMS], old.scales[row])
    ids: list[tuple[str, str, str]] = []
    vectors: array[int] = array("b")
    scales: array[float] = array("f")
    embedded = reused = 0
    for slug, section, text in units:
        key = (slug, section, _digest(text))
        if key in reuse:
            vec, scale = reuse[key]
            vectors.extend(vec)
            scales.append(scale)
            reused += 1
        else:
            quantized, scale = _quantize(model.encode(text))
            vectors.extend(quantized)
            scales.append(scale)
            embedded += 1
        ids.append(key)
    _write_index(index_dir(brain_dir, model), ids, vectors, scales, DIMS, model.name)
    return embedded, reused


def _write_index(
    directory: Path,
    ids: Sequence[tuple[str, str, str]],
    vectors: array[int],
    scales: array[float],
    dims: int,
    name: str,
    *,
    external: bool = False,
    extra: dict[str, object] | None = None,
) -> None:
    if not _MODEL_NAME.fullmatch(name) or directory.name != name:
        raise ValueError(f"bad model name {name!r}")
    brain = directory.parent.parent.parent
    # Never write through a symlink out of the brain (a cloned brain may
    # carry `.brainkit/vectors -> ~/.ssh`) — checked BEFORE anything is
    # created, and again after.
    for _ in range(2):
        if not directory.resolve().is_relative_to(brain.resolve()) or any(
            p.is_symlink()
            for p in (directory, directory.parent, directory.parent.parent)
        ):
            raise ValueError(
                f"refusing to write {directory}: it resolves outside the brain"
            )
        directory.mkdir(parents=True, exist_ok=True)
    mask = os.umask(0)
    os.umask(mask)
    meta: dict[str, object] = {
        "version": INDEX_VERSION,
        "model": name,
        "dims": dims,
        "checksum": _checksum(ids, vectors, scales),
        **(extra or {}),
    }
    if external:
        meta["external"] = True
    # Each file replaced atomically, meta.json LAST: until it lands, a reader
    # sees a checksum mismatch and falls back to lexical search.
    for filename, data in (
        ("vectors.i8", vectors.tobytes()),
        ("scales.f32", scales.tobytes()),
        ("ids.jsonl", "".join(json.dumps(list(k)) + "\n" for k in ids).encode()),
        ("meta.json", (json.dumps(meta) + "\n").encode()),
    ):
        fd, tmp = tempfile.mkstemp(dir=directory, prefix=f".{filename}.")
        try:
            # mkstemp makes 0600; a shared brain's readers need the umask mode.
            os.chmod(tmp, 0o666 & ~mask)
            with os.fdopen(fd, "wb") as handle:
                handle.write(data)
            os.replace(tmp, directory / filename)
        except BaseException:
            Path(tmp).unlink(missing_ok=True)
            raise


def export_units(units: Iterable[tuple[str, str, str]]) -> list[dict[str, str]]:
    """The interchange contract, outbound: what an external embedder embeds.

    One record per section: its note id, heading path, content digest and
    text. brainkit never runs the external model; it only accepts vectors
    back for exactly these digests (:func:`import_vectors`).
    """
    return [
        {"id": slug, "section": section, "digest": _digest(text), "text": text}
        for slug, section, text in units
    ]


def import_vectors(
    brain_dir: Path,
    rows: Iterable[dict[str, object]],
    units: Iterable[tuple[str, str, str]],
    *,
    model: str,
) -> int:
    """The interchange contract, inbound: vectors from an external embedder.

    Refused, whole, if any row names a section brainkit does not currently
    have (a stale digest), mixes dimensions or embedders (``model`` /
    ``revision`` fields), or carries a non-finite value: a silently stale or
    mixed index ranks garbage with confidence.

    The embedder fields are checked for CONSISTENCY, not required: the
    export format does not carry them, and ``--model`` already names the
    index. Rows that omit them are trusted to come from one embedder.
    """
    if not _MODEL_NAME.fullmatch(model) or model == MODEL_NAME:
        raise ValueError(f"bad model name {model!r}")
    current = unit_keys(units)
    identity: tuple[object, object] | None = None
    ids: list[tuple[str, str, str]] = []
    vectors: array[int] = array("b")
    scales: array[float] = array("f")
    dims = 0
    for number, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            raise ValueError(f"row {number}: not a JSON object")
        seen = (row.get("model"), row.get("revision"))
        if identity is not None and seen != identity:
            raise ValueError(f"row {number}: mixes embedders {identity} and {seen}")
        identity = seen
        key = (
            str(row.get("id", "")),
            str(row.get("section", "")),
            str(row.get("digest", "")),
        )
        if key not in current:
            raise ValueError(
                f"row {number}: {key[0]!r} section {key[1]!r} is stale or unknown"
            )
        vector = row.get("vector")
        if not isinstance(vector, list) or not vector:
            raise ValueError(f"row {number}: no vector")
        if not all(
            isinstance(v, int | float) and not isinstance(v, bool) for v in vector
        ):
            raise ValueError(f"row {number}: vector values must be numbers")
        values = [float(v) for v in vector]
        if not all(math.isfinite(v) for v in values):
            raise ValueError(f"row {number}: non-finite value")
        if dims and len(values) != dims:
            raise ValueError(f"row {number}: {len(values)} dims, expected {dims}")
        dims = len(values)
        norm = math.sqrt(sum(v * v for v in values)) or 1.0
        quantized, scale = _quantize([v / norm for v in values])
        vectors.extend(quantized)
        scales.append(scale)
        ids.append(key)
    if not ids:
        raise ValueError("no vectors to import")
    directory = brain_dir / ".brainkit" / "vectors" / model
    source_model, source_revision = identity or (None, None)
    source = {"source_model": source_model, "source_revision": source_revision}
    _write_index(
        directory,
        ids,
        vectors,
        scales,
        dims,
        model,
        external=True,
        extra={k: v for k, v in source.items() if v is not None},
    )
    return len(ids)
