"""Read-only MCP adapter. All application queries are shared with the CLI."""

import json
from collections.abc import Callable
from pathlib import Path
from typing import Annotated, Any

from mcp.server import MCPServer
from mcp.types import CallToolResult, TextContent, ToolAnnotations

from windchill_api_lookup.queries import Queries, default_home
from windchill_api_lookup.responses import query_response

# Preserve the CLI envelope in both MCP content channels, including domain errors.
EnvelopeResult = Annotated[CallToolResult, dict[str, Any]]


def _result(operation: Callable[[], dict]) -> CallToolResult:
    payload = query_response(operation)
    return CallToolResult(
        content=[TextContent(type="text", text=json.dumps(payload, ensure_ascii=False))],
        structured_content=payload,
        is_error=not payload["ok"],
    )


def create_server(home: str | Path | None = None) -> MCPServer:
    queries = Queries(default_home() if home is None else home)
    server = MCPServer(
        "windchill-api-lookup", version="0.3.0", log_level="WARNING",
        instructions=(
            "查询本地指定 Windchill 版本的 PTC Javadoc 索引。先确认项目目标版本；"
            "不得自动改用其他版本。Supported 为 null 表示未知；使用方法时同时检查所属类的状态。"
            "仅返回本页声明的方法及注解成员，不展开继承方法。所有工具只读，索引管理由用户通过 CLI 完成。"
        ),
    )
    readonly = ToolAnnotations(read_only_hint=True, destructive_hint=False,
                               idempotent_hint=True, open_world_hint=False)

    @server.tool(annotations=readonly)
    def list_versions() -> EnvelopeResult:
        """列出本机已有索引的版本和构建摘要；不可用索引显式标记 unavailable。"""
        return _result(queries.list_versions)

    @server.tool(annotations=readonly)
    def get_class(version: str, qualified_name: str) -> EnvelopeResult:
        """按版本和完整类名查询类、Supported/Extendable/Deprecated 与来源信息。"""
        return _result(lambda: queries.get_class(version, qualified_name))

    @server.tool(annotations=readonly)
    def search_method(version: str, qualified_name: str, method_name: str | None = None) -> EnvelopeResult:
        """按精确方法名返回全部重载；省略名称时列出本页方法。不展开继承方法。"""
        return _result(lambda: queries.search_method(version, qualified_name, method_name))

    @server.tool(annotations=readonly)
    def get_method(version: str, qualified_name: str, javadoc_id: str) -> EnvelopeResult:
        """按 search_method 返回的原始 javadoc_id 精确查询重载，保留 methods 数组格式。"""
        return _result(lambda: queries.get_method(version, qualified_name, javadoc_id))

    @server.tool(annotations=readonly)
    def get_index_status(version: str) -> EnvelopeResult:
        """读取索引存储的构建状态、校验值、schema/parser 版本及统计；不重新扫描或构建。"""
        return _result(lambda: queries.get_index_status(version))

    return server


if __name__ == "__main__":
    create_server().run(transport="stdio")
