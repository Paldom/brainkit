"""Rung 2: the static-embedding encoder, its index, fusion, and the
interchange contract — on a tiny synthetic model (no download)."""

from __future__ import annotations

import json
import math
import struct
from pathlib import Path
from typing import Any

import pytest

import brainkit.brain as brain_module
from brainkit.brain import Corpus, ingest_research_project, search, vector_units
from brainkit.cli import main
from brainkit.vectors import (
    DIMS,
    StaticModel,
    WordPiece,
    basic_tokens,
    build_index,
    convert,
    export_units,
    import_vectors,
    load_index,
    load_index_named,
    pull,
)

# A toy vocabulary with two "meaning clusters": animals and finance.
VOCAB = [
    "[PAD]",
    "[UNK]",
    "zebra",
    "stripe",
    "##s",
    "horse",
    "animal",
    "bank",
    "money",
    "loan",
    "finance",
    ",",
    "the",
]
CLUSTER = {
    "zebra": 0,
    "stripe": 0,
    "##s": 0,
    "horse": 0,
    "animal": 0,
    "bank": 1,
    "money": 1,
    "loan": 1,
    "finance": 1,
}


def _write_model(directory: Path) -> Path:
    """A sentence-transformers-shaped static model: safetensors + tokenizer."""
    directory.mkdir(parents=True, exist_ok=True)
    width = 512  # wider than DIMS, like the real model: convert() truncates
    rows = []
    for token in VOCAB:
        row = [0.0] * width
        if token in CLUSTER:
            row[CLUSTER[token]] = 1.0
            row[2 + VOCAB.index(token)] = 0.1  # a little identity per token
        rows.append(row)
    blob = b"".join(struct.pack(f"<{width}f", *row) for row in rows)
    header = json.dumps(
        {
            "embedding.weight": {
                "dtype": "F32",
                "shape": [len(VOCAB), width],
                "data_offsets": [0, len(blob)],
            }
        }
    ).encode()
    (directory / "model.safetensors").write_bytes(
        struct.pack("<Q", len(header)) + header + blob
    )
    (directory / "tokenizer.json").write_text(
        json.dumps(
            {
                "model": {
                    "type": "WordPiece",
                    "vocab": {t: i for i, t in enumerate(VOCAB)},
                }
            }
        )
    )
    return directory


@pytest.fixture
def model_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    converted = convert(_write_model(tmp_path / "raw"), tmp_path / "model")
    monkeypatch.setenv("BRAINKIT_MODEL_DIR", str(converted))
    return converted


@pytest.fixture
def brain(tmp_path: Path) -> Path:
    project = tmp_path / "run"
    (project / "materials").mkdir(parents=True)
    (project / "result.json").write_text(
        json.dumps({"topic": "notes", "meta_summary": "Mixed notes."})
    )
    for name, title, body in (
        ("001.md", "Equids", "The zebra and the horse."),
        ("002.md", "Lending", "The bank and the loan."),
    ):
        (project / "materials" / name).write_text(
            f"---\ntitle: {title}\nurl: https://{name}.test\n---\n\n{body}\n"
        )
    brain = tmp_path / "brain"
    ingest_research_project(project, brain)
    return brain


def test_basic_tokens_follow_bert_uncased() -> None:
    assert basic_tokens("Zébra, STRIPES!") == ["zebra", ",", "stripes", "!"]
    assert basic_tokens("知识") == ["知", "识"]


def test_wordpiece_greedy_longest_match() -> None:
    piece = WordPiece({t: i for i, t in enumerate(VOCAB)})
    assert piece.ids("stripes") == [VOCAB.index("stripe"), VOCAB.index("##s")]
    assert piece.ids("unknownword") == [VOCAB.index("[UNK]")]


def test_convert_truncates_and_quantizes(model_dir: Path) -> None:
    meta = json.loads((model_dir / "meta.json").read_text())
    assert meta["dims"] == DIMS and meta["license"] == "Apache-2.0"
    assert (model_dir / "vectors.i8").stat().st_size == len(VOCAB) * DIMS


def test_encoder_separates_meanings(model_dir: Path) -> None:
    model = StaticModel.load(model_dir)

    def cos(a: list[float], b: list[float]) -> float:
        return sum(x * y for x, y in zip(a, b, strict=True))

    animals, money = model.encode("zebra stripes"), model.encode("bank loan")
    assert cos(animals, model.encode("horse")) > 0.9
    assert cos(animals, money) < 0.2
    assert model.encode("nothing known") == model.encode("unknown")
    assert math.isclose(sum(v * v for v in animals), 1.0, rel_tol=1e-6)


def test_index_build_reuses_unchanged_sections(model_dir: Path, brain: Path) -> None:
    model = StaticModel.load(model_dir)
    units = vector_units(Corpus(brain))
    embedded, reused = build_index(brain, model, units)
    assert embedded == len(units) and reused == 0
    assert build_index(brain, model, units) == (0, len(units))
    index = load_index(brain, model)
    assert index is not None and len(index.ids) == len(units)


def test_semantic_search_bridges_vocabulary(model_dir: Path, brain: Path) -> None:
    build_index(brain, StaticModel.load(model_dir), vector_units(Corpus(brain)))
    # "animal" occurs in no note; lexically this query is unanswerable.
    assert search(brain, "animal") == []
    hits = search(brain, "animal", vectors=True)
    assert hits and hits[0].title == "Equids" and hits[0].channel == "vector"
    fused = search(brain, "zebra", vectors=True)
    assert fused[0].title == "Equids" and fused[0].channel in ("fused", "vector")


def test_writes_keep_an_existing_index_current(
    model_dir: Path, brain: Path, tmp_path: Path
) -> None:
    model = StaticModel.load(model_dir)
    build_index(brain, model, vector_units(Corpus(brain)))
    before = load_index(brain, model)
    assert before is not None
    project = tmp_path / "run2"
    (project / "materials").mkdir(parents=True)
    (project / "result.json").write_text(
        json.dumps({"topic": "more", "meta_summary": "More."})
    )
    (project / "materials" / "001.md").write_text(
        "---\ntitle: Finance\nurl: https://f.test\n---\n\nmoney money\n"
    )
    ingest_research_project(project, brain)
    after = load_index(brain, model)
    assert after is not None and len(after.ids) > len(before.ids)
    assert len(after.ids) == len(vector_units(Corpus(brain)))


def test_without_a_model_nothing_changes(
    brain: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("BRAINKIT_MODEL_DIR", str(tmp_path / "no-model"))
    plain = [h.slug for h in search(brain, "zebra")]
    assert [h.slug for h in search(brain, "zebra", vectors=True)] == plain


class TestInterchange:
    def test_export_import_roundtrip(self, brain: Path) -> None:
        units = vector_units(Corpus(brain))
        rows = export_units(units)
        assert {"id", "section", "digest", "text"} <= set(rows[0])
        vectors: list[dict[str, Any]] = [
            {**r, "vector": [1.0, 0.0] if "zebra" in r["text"] else [0.0, 1.0]}
            for r in rows
        ]
        assert import_vectors(brain, vectors, units, model="ext-model") == len(rows)
        index = load_index_named(brain, "ext-model")
        assert index is not None and index.dims == 2
        hits = search(brain, "anything", query_vector=[1.0, 0.0])
        assert hits[0].title == "Equids"

    @pytest.mark.parametrize(
        ("mutate", "message"),
        [
            (lambda r: {**r, "digest": "stale"}, "stale"),
            (lambda r: {**r, "vector": [float("nan"), 1.0]}, "non-finite"),
            (lambda r: {**r, "vector": []}, "no vector"),
        ],
    )
    def test_import_refuses_bad_rows(
        self, brain: Path, mutate: object, message: str
    ) -> None:
        units = vector_units(Corpus(brain))
        rows: list[dict[str, Any]] = [
            {**r, "vector": [1.0, 0.0]} for r in export_units(units)
        ]
        rows[0] = mutate(rows[0])  # type: ignore[operator]
        with pytest.raises(ValueError, match=message):
            import_vectors(brain, rows, units, model="ext")

    def test_import_refuses_mixed_dims_and_bad_names(self, brain: Path) -> None:
        units = vector_units(Corpus(brain))
        rows: list[dict[str, Any]] = [
            {**r, "vector": [1.0, 0.0]} for r in export_units(units)
        ]
        rows[-1] = {**rows[-1], "vector": [1.0, 0.0, 0.0]}
        with pytest.raises(ValueError, match="dims"):
            import_vectors(brain, rows, units, model="ext")
        with pytest.raises(ValueError, match="model name"):
            import_vectors(brain, rows, units, model="../escape")
        with pytest.raises(ValueError, match="no vectors"):
            import_vectors(brain, [], units, model="ext")

    def test_query_vector_needs_a_matching_index(self, brain: Path) -> None:
        with pytest.raises(ValueError, match="no imported vector index"):
            search(brain, "x", query_vector=[1.0, 0.0])


class TestCli:
    def test_build_status_search(
        self, model_dir: Path, brain: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert main(["--brain", str(brain), "vectors", "status"]) == 0
        assert "no vector index" in capsys.readouterr().out
        assert main(["--brain", str(brain), "vectors", "build"]) == 0
        assert "embedded" in capsys.readouterr().out
        assert main(["--brain", str(brain), "search", "animal", "--vectors"]) == 0
        assert "Equids" in capsys.readouterr().out
        assert main(["--brain", str(brain), "context", "animal", "--vectors"]) == 0

    def test_export_import_and_query_vector(
        self, brain: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        out = tmp_path / "units.jsonl"
        assert (
            main(["--brain", str(brain), "vectors", "export", "--out", str(out)]) == 0
        )
        rows = [json.loads(line) for line in out.read_text().splitlines()]
        vec_file = tmp_path / "vectors.jsonl"
        vec_file.write_text(
            "".join(
                json.dumps(
                    {**r, "vector": [1.0, 0.0] if "zebra" in r["text"] else [0.0, 1.0]}
                )
                + "\n"
                for r in rows
            )
        )
        assert (
            main(
                [
                    "--brain",
                    str(brain),
                    "vectors",
                    "import",
                    str(vec_file),
                    "--model",
                    "ext",
                ]
            )
            == 0
        )
        qv = tmp_path / "q.json"
        qv.write_text("[1.0, 0.0]")
        capsys.readouterr()
        assert (
            main(["--brain", str(brain), "search", "q", "--query-vector", str(qv)]) == 0
        )
        assert "Equids" in capsys.readouterr().out
        assert main(["--brain", str(brain), "vectors", "export"]) == 0
        assert main(["--brain", str(brain), "vectors", "import"]) == 1
        qv.write_text('{"not": "a list"}')
        assert (
            main(["--brain", str(brain), "search", "q", "--query-vector", str(qv)]) == 1
        )

    def test_status_without_model(
        self, brain: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("BRAINKIT_MODEL_DIR", str(tmp_path / "none"))
        assert main(["--brain", str(brain), "vectors", "status"]) == 0


def test_pull_verifies_checksums(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The one network path: fetched files are rejected on checksum mismatch."""
    import io
    import urllib.request

    def fake_urlopen(url: str, timeout: int) -> io.BytesIO:
        return io.BytesIO(b"not the real model")

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(ValueError, match="checksum mismatch"):
        pull(tmp_path / "m")


def test_experiment_constants_force_fusion(
    model_dir: Path, brain: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    build_index(brain, StaticModel.load(model_dir), vector_units(Corpus(brain)))
    monkeypatch.setattr(brain_module, "_VECTOR_WEIGHT", 1.0)
    monkeypatch.setattr(brain_module, "_FUSION", "maxmin")
    assert search(brain, "zebra")[0].title == "Equids"


class TestReviewFixes:
    def _import(self, brain: Path, model: str = "ext") -> None:
        units = vector_units(Corpus(brain))
        rows: list[dict[str, Any]] = [
            {**r, "vector": [1.0, 0.0] if "zebra" in r["text"] else [0.0, 1.0]}
            for r in export_units(units)
        ]
        import_vectors(brain, rows, units, model=model)

    def test_stale_vectors_are_ignored(self, brain: Path) -> None:
        self._import(brain)
        assert search(brain, "q", query_vector=[1.0, 0.0])[0].title == "Equids"
        # The zebra note now talks about banking: its old vector is stale.
        # By title, not by text: the level index lists the same sentence.
        note = next(d.path for d in Corpus(brain).docs if d.note.title == "Equids")
        note.write_text(note.read_text().replace("The zebra and the horse.", "Bank."))
        titles = [h.title for h in search(brain, "q", query_vector=[1.0, 0.0])]
        assert "Equids" not in titles

    def test_torn_index_is_refused(self, brain: Path) -> None:
        self._import(brain)
        ids = brain / ".brainkit" / "vectors" / "ext" / "ids.jsonl"
        lines = ids.read_text().splitlines()
        ids.write_text("\n".join(reversed(lines)) + "\n")  # same count, wrong pairs
        assert load_index_named(brain, "ext") is None

    @pytest.mark.parametrize("name", ["C:\\outside", "..\\x", "a/b", ".hidden", ""])
    def test_model_names_are_one_component(self, brain: Path, name: str) -> None:
        with pytest.raises(ValueError, match="model name"):
            self._import(brain, model=name)

    def test_import_does_not_write_through_symlinks(
        self, brain: Path, tmp_path: Path
    ) -> None:
        outside = tmp_path / "outside"
        outside.mkdir()
        (brain / ".brainkit" / "vectors").mkdir(parents=True, exist_ok=True)
        (brain / ".brainkit" / "vectors" / "ext").symlink_to(outside)
        with pytest.raises(ValueError, match="outside the brain"):
            self._import(brain)
        assert list(outside.iterdir()) == []

    @pytest.mark.parametrize(
        ("row", "message"),
        [
            ("not an object", "not a JSON object"),
            ({"vector": ["x"]}, "numbers"),
            ({"vector": [True, 1.0]}, "numbers"),
        ],
    )
    def test_import_rejects_malformed_rows(
        self, brain: Path, row: object, message: str
    ) -> None:
        units = vector_units(Corpus(brain))
        good = export_units(units)[0]
        bad = {**good, **row} if isinstance(row, dict) else row
        with pytest.raises(ValueError, match=message):
            import_vectors(brain, [bad], units, model="ext")  # type: ignore[list-item]

    def test_import_refuses_mixed_embedders(self, brain: Path) -> None:
        units = vector_units(Corpus(brain))
        rows: list[dict[str, Any]] = [
            {**r, "vector": [1.0, 0.0], "model": "a"} for r in export_units(units)
        ]
        rows[-1]["model"] = "b"
        with pytest.raises(ValueError, match="mixes embedders"):
            import_vectors(brain, rows, units, model="ext")
        rows[-1]["model"] = "a"
        import_vectors(brain, rows, units, model="ext")
        meta = json.loads((brain / ".brainkit/vectors/ext/meta.json").read_text())
        assert meta["source_model"] == "a"

    def test_two_imported_indexes_are_named_in_the_error(self, brain: Path) -> None:
        self._import(brain, "ext-a")
        self._import(brain, "ext-b")
        with pytest.raises(ValueError, match="ext-a, ext-b"):
            search(brain, "q", query_vector=[1.0, 0.0])

    def test_vectors_survive_also_budget_and_no_terms(
        self, model_dir: Path, brain: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        build_index(brain, StaticModel.load(model_dir), vector_units(Corpus(brain)))
        b = str(brain)
        # "animal" occurs in no note: only the dense arm can find the zebras.
        for argv in (
            ["search", "animal", "--also", "beast", "--vectors"],
            ["context", "animal", "--vectors", "--budget", "4000"],
        ):
            capsys.readouterr()
            assert main(["--brain", b, *argv]) == 0, argv
            assert "Equids" in capsys.readouterr().out, argv
        assert search(brain, "???", vectors=True) == []  # no words, no vector

    def test_query_vector_file_must_be_finite_numbers(
        self, brain: Path, tmp_path: Path
    ) -> None:
        self._import(brain)
        qv = tmp_path / "q.json"
        for text in ("[NaN, 1.0]", "[true, 1.0]", "[]"):
            qv.write_text(text)
            argv = ["--brain", str(brain), "search", "q", "--query-vector", str(qv)]
            assert main(argv) == 1, text

    def test_status_reports_stale_and_imported(
        self, brain: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        self._import(brain)
        (brain / ".brainkit" / "vectors" / "torn").mkdir()
        capsys.readouterr()
        assert main(["--brain", str(brain), "vectors", "status"]) == 0
        out = capsys.readouterr().out
        assert "ext: " in out and "0 stale" in out and "torn: unreadable" in out

    def test_parent_symlink_creates_nothing_outside(
        self, brain: Path, tmp_path: Path
    ) -> None:
        outside = tmp_path / "outside2"
        outside.mkdir()
        (brain / ".brainkit").mkdir(exist_ok=True)
        (brain / ".brainkit" / "vectors").symlink_to(outside)
        with pytest.raises(ValueError, match="outside the brain"):
            self._import(brain)
        assert list(outside.iterdir()) == []

    @pytest.mark.parametrize("meta", ["[]", "null", "{bad json"])
    def test_malformed_meta_falls_back(
        self, brain: Path, meta: str, capsys: pytest.CaptureFixture[str]
    ) -> None:
        self._import(brain)
        (brain / ".brainkit" / "vectors" / "ext" / "meta.json").write_text(meta)
        assert load_index_named(brain, "ext") is None
        assert search(brain, "zebra", vectors=True)  # lexical still answers
        assert main(["--brain", str(brain), "vectors", "status"]) == 0
        assert "unreadable" in capsys.readouterr().out

    def test_index_files_follow_the_umask(self, brain: Path) -> None:
        import os

        old = os.umask(0o022)
        try:
            self._import(brain)
        finally:
            os.umask(old)
        for f in (brain / ".brainkit" / "vectors" / "ext").iterdir():
            assert f.stat().st_mode & 0o777 == 0o644, f.name
