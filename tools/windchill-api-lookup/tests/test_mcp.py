"""MCP protocol tests against temporary Javadoc indexes."""

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
YEAR_VERSION = "2027"
CLASS = "wt.example.Example"


@pytest.fixture
def indexed_home(tmp_path):
    archive = tmp_path / "docs.zip"
    with ZipFile(archive, "w") as zip_file:
        zip_file.writestr(
            "Javadoc/wt/example/Example.html",
            CLASS_HTML + METHOD_HTML,
        )

    home = tmp_path / "indexes"
    build_index(archive, VERSION, home)

    # Read-only MCP queries must remain independent of the original ZIP.
    archive.unlink()
    return home


def create_test_archive(path: Path) -> Path:
    with ZipFile(path, "w") as zip_file:
        zip_file.writestr(
            "Javadoc/wt/example/Example.html",
            CLASS_HTML + METHOD_HTML,
        )
    return path


CASES = [
    ("list_versions", {}, ["versions"]),
    (
        "get_index_status",
        {"version": VERSION},
        ["get-index-status", "--version", VERSION],
    ),
    (
        "get_class",
        {"version": VERSION, "qualified_name": CLASS},
        ["get-class", "--version", VERSION, CLASS],
    ),
    (
        "search_method",
        {
            "version": VERSION,
            "qualified_name": CLASS,
            "method_name": "run",
        },
        ["search-method", "--version", VERSION, CLASS, "run"],
    ),
    (
        "get_method",
        {
            "version": VERSION,
            "qualified_name": CLASS,
            "javadoc_id": "run()",
        },
        ["get-method", "--version", VERSION, CLASS, "run()"],
    ),
    (
        "get_class",
        {
            "version": VERSION,
            "qualified_name": "wt.Missing",
        },
        ["get-class", "--version", VERSION, "wt.Missing"],
    ),
    (
        "get_index_status",
        {"version": "99.0"},
        ["get-index-status", "--version", "99.0"],
    ),
    (
        "get_index_status",
        {"version": "../escape"},
        ["get-index-status", "--version", "../escape"],
    ),
]


@pytest.mark.parametrize("tool,arguments,cli", CASES)
def test_mcp_matches_cli_envelope(
    indexed_home,
    capsys,
    tool,
    arguments,
    cli,
):
    code = main([*cli, "--home", str(indexed_home), "--json"])
    captured = capsys.readouterr()
    expected = json.loads(
        captured.out if code == 0 else captured.err
    )

    async def check():
        async with Client(create_server(indexed_home)) as client:
            result = await client.call_tool(tool, arguments)
            assert result.structured_content == expected
            assert json.loads(result.content[0].text) == expected
            assert result.is_error == (code != 0)

    asyncio.run(check())


def test_mcp_tool_contracts_and_readonly_queries_do_not_mutate(
    indexed_home,
):
    before = {
        path.relative_to(indexed_home): path.read_bytes()
        for path in indexed_home.rglob("*")
        if path.is_file()
    }

    async def check():
        async with Client(create_server(indexed_home)) as client:
            tools = (await client.list_tools()).tools
            tools_by_name = {tool.name: tool for tool in tools}

            assert set(tools_by_name) == {
                "ensure_javadoc_index",
                "list_versions",
                "get_class",
                "search_method",
                "get_method",
                "get_index_status",
            }

            ensure_tool = tools_by_name["ensure_javadoc_index"]
            assert ensure_tool.annotations.read_only_hint is False
            assert ensure_tool.annotations.destructive_hint is False
            assert ensure_tool.annotations.idempotent_hint is True
            assert ensure_tool.annotations.open_world_hint is False
            assert "version" in ensure_tool.input_schema["properties"]
            assert "zip_path" in ensure_tool.input_schema["properties"]
            assert "home" not in ensure_tool.input_schema["properties"]

            for name, tool in tools_by_name.items():
                if name == "ensure_javadoc_index":
                    continue
                assert tool.annotations.read_only_hint is True
                assert tool.annotations.destructive_hint is False
                assert tool.annotations.open_world_hint is False
                assert "home" not in tool.input_schema["properties"]
                assert "zip_path" not in tool.input_schema["properties"]

            for tool, args, _ in CASES[:5]:
                result = await client.call_tool(tool, args)
                assert not result.is_error

    asyncio.run(check())

    after = {
        path.relative_to(indexed_home): path.read_bytes()
        for path in indexed_home.rglob("*")
        if path.is_file()
    }

    assert after == before


def test_ensure_javadoc_index_builds_and_reuses_year_version(
    tmp_path,
):
    archive = create_test_archive(
        tmp_path / "WindchillJavadoc.zip"
    )
    home = tmp_path / "indexes"

    async def check():
        async with Client(create_server(home)) as client:
            first = await client.call_tool(
                "ensure_javadoc_index",
                {
                    "version": YEAR_VERSION,
                    "zip_path": str(archive.resolve()),
                },
            )

            assert not first.is_error
            assert first.structured_content["ok"] is True
            assert first.structured_content["reused"] is False
            assert first.structured_content["windchill_version"] == YEAR_VERSION

            query = await client.call_tool(
                "get_class",
                {
                    "version": YEAR_VERSION,
                    "qualified_name": CLASS,
                },
            )

            assert not query.is_error
            assert query.structured_content["version"] == YEAR_VERSION
            assert (
                query.structured_content["class"]["qualified_name"]
                == CLASS
            )

            second = await client.call_tool(
                "ensure_javadoc_index",
                {
                    "version": YEAR_VERSION,
                    "zip_path": str(archive.resolve()),
                },
            )

            assert not second.is_error
            assert second.structured_content["reused"] is True

    asyncio.run(check())

    assert (
        home
        / "api-index"
        / YEAR_VERSION
        / "api.sqlite"
    ).is_file()


def test_ensure_javadoc_index_requires_absolute_path(tmp_path):
    home = tmp_path / "indexes"

    async def check():
        async with Client(create_server(home)) as client:
            result = await client.call_tool(
                "ensure_javadoc_index",
                {
                    "version": VERSION,
                    "zip_path": ".windchill-ai/javadoc/docs.zip",
                },
            )

            assert result.is_error
            assert (
                result.structured_content["error"]["code"]
                == "INVALID_ARGUMENT"
            )

    asyncio.run(check())


def test_corrupt_index_preserves_error_code(indexed_home):
    (
        indexed_home
        / "api-index"
        / VERSION
        / "api.sqlite"
    ).write_bytes(b"corrupt")

    async def check():
        async with Client(create_server(indexed_home)) as client:
            result = await client.call_tool(
                "get_index_status",
                {"version": VERSION},
            )
            assert result.is_error
            assert (
                result.structured_content["error"]["code"]
                == "INDEX_UNAVAILABLE"
            )

            versions = await client.call_tool(
                "list_versions",
                {},
            )
            assert (
                versions.structured_content["versions"][0]["status"]
                == "unavailable"
            )

    asyncio.run(check())


@pytest.mark.parametrize("mode", ["auto", "legacy"])
def test_real_stdio_subprocess(
    indexed_home,
    mode,
    tmp_path,
):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(
        Path(__file__).resolve().parents[1] / "src"
    )
    env["WINDCHILL_API_HOME"] = str(indexed_home)

    parameters = StdioServerParameters(
        command=sys.executable,
        args=[
            "-m",
            "windchill_api_lookup.cli",
            "serve",
        ],
        env=env,
        cwd=tmp_path,
    )

    async def check():
        async with Client(
            parameters,
            mode=mode,
            read_timeout_seconds=15,
        ) as client:
            assert client.server_info.version == "0.4.0"
            assert len((await client.list_tools()).tools) == 6

            result = await client.call_tool(
                "search_method",
                {
                    "version": VERSION,
                    "qualified_name": CLASS,
                    "method_name": "run",
                },
            )

            assert len(
                result.structured_content["methods"]
            ) == 2

            missing = await client.call_tool(
                "get_class",
                {
                    "version": "99.0",
                    "qualified_name": CLASS,
                },
            )

            assert missing.is_error
            assert (
                missing.structured_content["error"]["code"]
                == "VERSION_NOT_INSTALLED"
            )

    asyncio.run(
        asyncio.wait_for(
            check(),
            timeout=30,
        )
    )


def test_empty_home_is_not_created(
    tmp_path,
    monkeypatch,
):
    home = tmp_path / "does-not-exist"
    monkeypatch.setenv(
        "WINDCHILL_API_HOME",
        str(home),
    )

    async def check():
        async with Client(create_server()) as client:
            result = await client.call_tool(
                "list_versions",
                {},
            )
            assert result.structured_content == {
                "ok": True,
                "versions": [],
            }

            result = await client.call_tool(
                "get_index_status",
                {"version": VERSION},
            )
            assert (
                result.structured_content["error"]["code"]
                == "VERSION_NOT_INSTALLED"
            )

    asyncio.run(check())
    assert not home.exists()