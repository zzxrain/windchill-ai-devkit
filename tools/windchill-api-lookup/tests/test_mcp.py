"""MCP protocol tests against the same temporary index used by the CLI."""

import asyncio
import json
import os
import sys
from pathlib import Path
from zipfile import ZipFile

import pytest
from mcp import Client, StdioServerParameters

from windchill_api_lookup.cli import main
from windchill_api_lookup.indexer import build_index
from windchill_api_lookup.server import create_server
from test_parser_unit import CLASS_HTML, METHOD_HTML

VERSION = "13.1.2.0"
CLASS = "wt.example.Example"


@pytest.fixture
def indexed_home(tmp_path):
    archive = tmp_path / "docs.zip"
    with ZipFile(archive, "w") as zip_file:
        zip_file.writestr("Javadoc/wt/example/Example.html", CLASS_HTML + METHOD_HTML)
    home = tmp_path / "indexes"
    build_index(archive, VERSION, home)
    archive.unlink()  # MCP must operate without the Javadoc source.
    return home


CASES = [
    ("list_versions", {}, ["versions"]),
    ("get_index_status", {"version": VERSION}, ["get-index-status", "--version", VERSION]),
    ("get_class", {"version": VERSION, "qualified_name": CLASS}, ["get-class", "--version", VERSION, CLASS]),
    ("search_method", {"version": VERSION, "qualified_name": CLASS, "method_name": "run"},
     ["search-method", "--version", VERSION, CLASS, "run"]),
    ("get_method", {"version": VERSION, "qualified_name": CLASS, "javadoc_id": "run()"},
     ["get-method", "--version", VERSION, CLASS, "run()"]),
    ("get_class", {"version": VERSION, "qualified_name": "wt.Missing"},
     ["get-class", "--version", VERSION, "wt.Missing"]),
    ("get_index_status", {"version": "99.0"}, ["get-index-status", "--version", "99.0"]),
    ("get_index_status", {"version": "../escape"}, ["get-index-status", "--version", "../escape"]),
]


@pytest.mark.parametrize("tool,arguments,cli", CASES)
def test_mcp_matches_cli_envelope(indexed_home, capsys, tool, arguments, cli):
    code = main([*cli, "--home", str(indexed_home), "--json"])
    captured = capsys.readouterr()
    expected = json.loads(captured.out if code == 0 else captured.err)

    async def check():
        async with Client(create_server(indexed_home)) as client:
            result = await client.call_tool(tool, arguments)
            assert result.structured_content == expected
            assert json.loads(result.content[0].text) == expected
            assert result.is_error == (code != 0)

    asyncio.run(check())


def test_exactly_five_readonly_tools_and_no_mutations(indexed_home, monkeypatch):
    before = {p.relative_to(indexed_home): p.read_bytes() for p in indexed_home.rglob("*") if p.is_file()}

    def forbidden(*args, **kwargs):
        raise AssertionError("MCP attempted parsing or index management")

    monkeypatch.setattr("windchill_api_lookup.indexer.build_index", forbidden)
    monkeypatch.setattr("windchill_api_lookup.parser.archive.scan_javadoc", forbidden)

    async def check():
        async with Client(create_server(indexed_home)) as client:
            tools = (await client.list_tools()).tools
            assert {tool.name for tool in tools} == {
                "list_versions", "get_class", "search_method", "get_method", "get_index_status",
            }
            for tool in tools:
                assert tool.annotations.read_only_hint is True
                assert tool.annotations.destructive_hint is False
                assert tool.annotations.open_world_hint is False
                assert "home" not in tool.input_schema["properties"]
                assert "zip_path" not in tool.input_schema["properties"]
            for tool, args, _ in CASES[:5]:
                assert not (await client.call_tool(tool, args)).is_error
            assert (await client.call_tool("add_javadoc", {})).is_error

    asyncio.run(check())
    after = {p.relative_to(indexed_home): p.read_bytes() for p in indexed_home.rglob("*") if p.is_file()}
    assert after == before


def test_corrupt_index_preserves_error_code(indexed_home):
    (indexed_home / "api-index" / VERSION / "api.sqlite").write_bytes(b"corrupt")

    async def check():
        async with Client(create_server(indexed_home)) as client:
            result = await client.call_tool("get_index_status", {"version": VERSION})
            assert result.is_error
            assert result.structured_content["error"]["code"] == "INDEX_UNAVAILABLE"
            versions = await client.call_tool("list_versions", {})
            assert versions.structured_content["versions"][0]["status"] == "unavailable"

    asyncio.run(check())


@pytest.mark.parametrize("mode", ["auto", "legacy"])
def test_real_stdio_subprocess(indexed_home, mode, tmp_path):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    env["WINDCHILL_API_HOME"] = str(indexed_home)
    parameters = StdioServerParameters(
        command=sys.executable,
        args=["-m", "windchill_api_lookup.cli", "serve"],
        env=env, cwd=tmp_path,
    )

    async def check():
        async with Client(parameters, mode=mode, read_timeout_seconds=15) as client:
            assert client.server_info.version == "0.3.0"
            assert len((await client.list_tools()).tools) == 5
            result = await client.call_tool("search_method", {
                "version": VERSION, "qualified_name": CLASS, "method_name": "run",
            })
            assert len(result.structured_content["methods"]) == 2
            missing = await client.call_tool("get_class", {"version": "99.0", "qualified_name": CLASS})
            assert missing.is_error
            assert missing.structured_content["error"]["code"] == "VERSION_NOT_INSTALLED"

    asyncio.run(asyncio.wait_for(check(), timeout=30))


def test_empty_home_is_not_created(tmp_path, monkeypatch):
    home = tmp_path / "does-not-exist"
    monkeypatch.setenv("WINDCHILL_API_HOME", str(home))

    async def check():
        async with Client(create_server()) as client:
            result = await client.call_tool("list_versions", {})
            assert result.structured_content == {"ok": True, "versions": []}
            result = await client.call_tool("get_index_status", {"version": VERSION})
            assert result.structured_content["error"]["code"] == "VERSION_NOT_INSTALLED"

    asyncio.run(check())
    assert not home.exists()
