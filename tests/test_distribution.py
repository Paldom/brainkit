"""Exports, the agent pointer, and the plugin packaging."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from brainkit.brain import export_llms_txt, ingest_research_project, write_exports
from brainkit.cli import _pointer_snippet, main

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture
def brain(tmp_path: Path) -> Path:
    project = tmp_path / "run"
    (project / "materials").mkdir(parents=True)
    (project / "result.json").write_text(
        json.dumps({"topic": "zebra research", "meta_summary": "Zebras, summarised."})
    )
    (project / "materials" / "001.md").write_text(
        '---\ntitle: "Stripes"\nurl: https://z.test\n---\n\nZebra stripes.\n'
    )
    brain = tmp_path / "brain"
    ingest_research_project(project, brain)
    return brain


def test_llms_txt(brain: Path) -> None:
    text, manifest = export_llms_txt(brain)
    assert text.startswith("# Brain\n\n> ")
    assert "## Topics" in text and "Zebras, summarised." in text
    assert "notes/sources/index.md" in text
    notes = manifest["notes"]
    assert isinstance(notes, dict) and len(notes) == 2


def test_write_exports_is_idempotent(
    brain: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    written = write_exports(brain)
    before = {p: p.read_bytes() for p in written}
    write_exports(brain)
    assert {p: p.read_bytes() for p in written} == before
    assert main(["--brain", str(brain), "export", "llms-txt"]) == 0
    assert capsys.readouterr().out.startswith("# Brain")
    assert main(["--brain", str(brain), "export", "llms-txt", "--write"]) == 0
    assert "manifest.json" in capsys.readouterr().out


def test_pointer_names_the_triggers() -> None:
    snippet = _pointer_snippet("brain")
    assert "BEFORE starting research" in snippet
    assert "verify" in snippet and "untrusted" in snippet


def test_plugin_manifest_points_at_the_skill() -> None:
    manifest = json.loads((REPO / ".claude-plugin" / "plugin.json").read_text())
    for path in manifest["skills"]:
        assert (REPO / path / "brainkit" / "SKILL.md").is_file()
    hooks = json.loads((REPO / manifest["hooks"]).read_text())
    (start,) = hooks["hooks"]["SessionStart"]
    command = start["hooks"][0]["command"]
    assert "BRAINKIT_HOOKS" in command and command.endswith("|| true")


def test_session_hook_is_opt_in_and_silent(tmp_path: Path) -> None:
    manifest = json.loads((REPO / ".claude-plugin" / "plugin.json").read_text())
    command = json.loads((REPO / manifest["hooks"]).read_text())["hooks"][
        "SessionStart"
    ][0]["hooks"][0]["command"]
    off = subprocess.run(
        ["sh", "-c", command],
        capture_output=True,
        text=True,
        env={"PATH": "/usr/bin:/bin"},
    )
    assert off.returncode == 0 and off.stdout == ""
