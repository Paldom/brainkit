"""The read-only MCP server: both protocol eras, every tool, errors."""

from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from brainkit.brain import ingest_research_project
from brainkit.mcp import MODERN, TOOLS, Server, serve

META: dict[str, Any] = {"_meta": {"io.modelcontextprotocol/protocolVersion": MODERN}}


@pytest.fixture
def brain(tmp_path: Path) -> Path:
    project = tmp_path / "run"
    (project / "materials").mkdir(parents=True)
    (project / "result.json").write_text(
        json.dumps({"topic": "zebra research", "meta_summary": "Zebras, summarised."})
    )
    (project / "materials" / "001.md").write_text(
        '---\ntitle: "Stripes"\nurl: https://z.test\n---\n\n## Findings\n\n'
        "Zebra stripes deter biting flies.\n"
    )
    brain = tmp_path / "brain"
    ingest_research_project(project, brain)
    return brain


def _call(server: Server, method: str, params: dict[str, object] | None = None) -> Any:
    response = _handle(
        server, {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}
    )
    assert response is not None
    return response


def _handle(server: Server, message: dict[str, Any]) -> Any:
    return server.handle(message)


def _tool(server: Server, name: str, **arguments: object) -> Any:
    return _call(server, "tools/call", {**META, "name": name, "arguments": arguments})[
        "result"
    ]


class TestEras:
    def test_discover(self, brain: Path) -> None:
        result = _call(Server(brain), "server/discover", META)["result"]
        assert result["resultType"] == "complete"
        assert MODERN in result["supportedVersions"]
        assert result["cacheScope"] == "public" and result["ttlMs"] > 0
        assert (
            result["_meta"]["io.modelcontextprotocol/serverInfo"]["name"] == "brainkit"
        )
        assert len(result["instructions"]) <= 2048

    def test_legacy_initialize_never_answers_modern(self, brain: Path) -> None:
        server = Server(brain)
        assert (
            _call(server, "initialize", {"protocolVersion": "2025-06-18"})["result"][
                "protocolVersion"
            ]
            == "2025-06-18"
        )
        assert (
            _call(server, "initialize", {"protocolVersion": MODERN})["result"][
                "protocolVersion"
            ]
            == "2025-11-25"
        )
        legacy = _call(server, "tools/list")["result"]
        assert "resultType" not in legacy and legacy["tools"]
        assert _call(server, "ping")["result"] == {}

    def test_unsupported_version(self, brain: Path) -> None:
        error = _call(
            Server(brain),
            "tools/list",
            {"_meta": {"io.modelcontextprotocol/protocolVersion": "1900-01-01"}},
        )["error"]
        assert error["code"] == -32022 and MODERN in error["data"]["supported"]

    def test_notifications_get_no_answer(self, brain: Path) -> None:
        assert (
            Server(brain).handle(
                {"jsonrpc": "2.0", "method": "notifications/initialized"}
            )
            is None
        )

    def test_unknown_method_and_bad_messages(self, brain: Path) -> None:
        server = Server(brain)
        assert _call(server, "nope/never", META)["error"]["code"] == -32601
        assert _handle(server, {"jsonrpc": "2.0", "id": 3})["error"]["code"] == -32600
        bad = _handle(
            server, {"jsonrpc": "2.0", "id": 4, "method": "tools/list", "params": []}
        )
        assert bad is not None and bad["error"]["code"] == -32602
        assert _handle(server, {"jsonrpc": "2.0"}) is None


class TestTools:
    def test_listing_is_read_only_and_deterministic(self, brain: Path) -> None:
        result = _call(Server(brain), "tools/list", META)["result"]
        names = [t["name"] for t in result["tools"]]
        assert names == [t["name"] for t in TOOLS]
        assert all(t["annotations"]["readOnlyHint"] for t in result["tools"])
        assert result["resultType"] == "complete" and result["cacheScope"] == "public"

    def test_search_context_read_verify_lint_fetch(self, brain: Path) -> None:
        server = Server(brain)
        hits = _tool(server, "search", query="zebra stripes")["structuredContent"][
            "hits"
        ]
        assert hits and hits[0]["breadcrumbs"] is not None
        source = next(h for h in hits if h["kind"] == "source")
        assert source["url"] == "https://z.test"
        fused = _tool(server, "search", query="zebra", also=["biting flies"])
        assert fused["isError"] is False
        ctx = _tool(server, "context", query="zebra stripes")["structuredContent"]
        assert ctx["signals"]
        packed = _tool(server, "context", query="zebra", budget=200)[
            "structuredContent"
        ]
        assert packed["used_chars"] <= 200
        note = _tool(server, "read_note", id=source["id"], level="outline")
        assert "Findings" in note["structuredContent"]["content"]
        assert _tool(server, "verify", ref=source["id"], quote="deter biting flies")[
            "structuredContent"
        ]["found"]
        assert "findings" in _tool(server, "lint")["structuredContent"]
        assert (
            _tool(server, "fetch", id=source["id"])["structuredContent"]["level"]
            == "full"
        )

    def test_tool_errors_are_results(self, brain: Path) -> None:
        server = Server(brain)
        assert _tool(server, "read_note", id="missing")["isError"] is True
        assert _tool(server, "verify", ref="missing", quote="x")["isError"] is True
        assert _tool(server, "search", query="x", as_of="soon")["isError"] is True

    @pytest.mark.parametrize(
        "arguments",
        [{}, {"query": ""}, {"query": "x", "limit": 0}, {"query": "x", "also": "y"}],
    )
    def test_invalid_arguments(self, brain: Path, arguments: dict[str, object]) -> None:
        response = _call(
            Server(brain),
            "tools/call",
            {**META, "name": "search", "arguments": arguments},
        )
        assert response["error"]["code"] == -32602

    def test_invalid_context_and_read_arguments(self, brain: Path) -> None:
        server = Server(brain)
        for name, arguments in (
            ("context", {"query": "x", "budget": 0}),
            ("read_note", {"id": "x", "level": "huge"}),
            ("nope", {}),
            ("search", "not-an-object"),
            ("search", {"query": "x", "kind": 3}),
        ):
            response = _call(
                server, "tools/call", {**META, "name": name, "arguments": arguments}
            )
            assert response["error"]["code"] == -32602, name


class TestResources:
    def test_list_templates_read(self, brain: Path) -> None:
        server = Server(brain)
        assert (
            _call(server, "resources/list", META)["result"]["resources"][0]["uri"]
            == "brain://index"
        )
        assert _call(server, "resources/templates/list", META)["result"][
            "resourceTemplates"
        ]
        index = _call(server, "resources/read", {**META, "uri": "brain://index"})[
            "result"
        ]
        assert "Brain index" in index["contents"][0]["text"]
        assert index["cacheScope"] == "private"
        hits = _tool(server, "search", query="stripes")["structuredContent"]["hits"]
        note = _call(
            server, "resources/read", {**META, "uri": f"brain://note/{hits[0]['id']}"}
        )
        assert note["result"]["contents"][0]["text"]
        for uri in ("brain://note/missing", "file:///etc/passwd"):
            assert (
                _call(server, "resources/read", {**META, "uri": uri})["error"]["code"]
                == -32602
            )

    def test_missing_index(self, tmp_path: Path) -> None:
        error = _call(
            Server(tmp_path), "resources/read", {**META, "uri": "brain://index"}
        )
        assert error["error"]["code"] == -32602


def test_serve_loop(brain: Path) -> None:
    lines = "\n".join(
        [
            json.dumps(
                {"jsonrpc": "2.0", "id": 1, "method": "server/discover", "params": META}
            ),
            "",
            "{not json",
            json.dumps([1, 2]),
            json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
        ]
    )
    out = io.StringIO()
    serve(brain, io.StringIO(lines + "\n"), out)
    responses = [json.loads(line) for line in out.getvalue().splitlines()]
    assert [r.get("error", {}).get("code") for r in responses] == [None, -32700, -32600]


def test_cli_stdio_roundtrip(brain: Path) -> None:
    request = json.dumps(
        {"jsonrpc": "2.0", "id": 9, "method": "server/discover", "params": META}
    )
    done = subprocess.run(
        [sys.executable, "-m", "brainkit.cli", "--brain", str(brain), "mcp"],
        input=request + "\n",
        capture_output=True,
        text=True,
        timeout=60,
        check=True,
    )
    assert json.loads(done.stdout)["result"]["resultType"] == "complete"


class TestReviewFixes:
    def test_also_keeps_as_of(self, brain: Path) -> None:
        def kinds(**extra: object) -> set[str]:
            data = _tool(Server(brain), "search", query="zebra", **extra)
            return {h["kind"] for h in data["structuredContent"]["hits"]}

        assert "topic" in kinds(also=["flies"])
        # The topic note was generated today: not known as of 2020.
        assert "topic" not in kinds(also=["flies"], as_of="2020-01-01")

    def test_context_exclude_without_budget(self, brain: Path) -> None:
        first = _tool(Server(brain), "context", query="zebra")["structuredContent"]
        top = first["hits"][0]["id"]
        again = _tool(Server(brain), "context", query="zebra", exclude=[top])
        assert top not in {h["id"] for h in again["structuredContent"]["hits"]}

    def test_unexpected_errors_do_not_end_the_session(
        self, brain: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        server = Server(brain)

        def boom(_args: object) -> dict[str, object]:
            raise PermissionError("unreadable note")

        monkeypatch.setattr(server, "_lint", boom)
        assert _tool(server, "lint")["isError"] is True

        def crash(_method: str, _params: object) -> dict[str, object]:
            raise RuntimeError("bug")

        monkeypatch.setattr(server, "_dispatch", crash)
        assert _call(server, "tools/list")["error"]["code"] == -32603

    def test_symlinks_out_of_the_brain_are_not_served(
        self, brain: Path, tmp_path: Path
    ) -> None:
        secret = tmp_path / "secret.md"
        secret.write_text("---\ntitle: Secret\nurl: https://s.test\n---\n\nhunter2\n")
        (brain / "notes" / "sources" / "leak.md").symlink_to(secret)
        data = _tool(Server(brain), "search", query="hunter2")["structuredContent"]
        assert data["hits"] == []
        (brain / "index.md").unlink()
        (brain / "index.md").symlink_to(secret)
        response = _call(Server(brain), "resources/read", {"uri": "brain://index"})
        assert "error" in response

    def test_signals_describe_what_is_returned(self, brain: Path) -> None:
        first = _tool(Server(brain), "context", query="zebra")["structuredContent"]
        every = [h["id"] for h in first["hits"]]
        data = _tool(Server(brain), "context", query="zebra", exclude=every)
        content = data["structuredContent"]
        assert content["hits"] == []
        assert not any("independent source" in s for s in content["signals"])
