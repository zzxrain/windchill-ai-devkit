"""MCP adapter for Javadoc index preparation and read-only API queries."""

import json
from collections.abc import Callable
from pathlib import Path
from typing import Annotated, Any

from mcp.server import MCPServer
from mcp.types import CallToolResult, TextContent, ToolAnnotations

from windchill_api_lookup import indexer
from windchill_api_lookup.errors import ApiLookupError
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
        "windchill-api-lookup",
        version="0.4.0",
        log_level="WARNING",
        instructions=(
            "查询当前项目目标 Windchill 版本的 PTC Javadoc API。"
            "目标版本必须来自项目上下文，不得从 Javadoc 文件名推断，也不得自动改用其他版本。"
            "如果项目配置了 Javadoc ZIP，在精确 API 查询前可调用 ensure_javadoc_index 建立或复用本地索引；"
            "项目相对 ZIP 路径应先解析为绝对路径。"
            "Supported 为 null 表示未知；使用方法时同时检查所属类的状态。"
            "方法查询仅返回本页声明的方法及注解成员，不展开继承方法。"
        ),
    )

    readonly = ToolAnnotations(
        read_only_hint=True,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=False,
    )

    cache_write = ToolAnnotations(
        read_only_hint=False,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=False,
    )

    @server.tool(annotations=cache_write)
    def ensure_javadoc_index(version: str, zip_path: str) -> EnvelopeResult:
        """为项目目标版本建立或复用本地 Javadoc API 索引；不会自动覆盖不同来源的同版本索引。"""

        def operation() -> dict:
            source = Path(zip_path).expanduser()
            if not source.is_absolute():
                raise ApiLookupError(
                    "INVALID_ARGUMENT",
                    "zip_path 必须为绝对路径；项目相对路径应先由 Agent 根据项目根目录解析",
                )
            return indexer.build_index(
                source,
                version,
                queries.home,
                replace=False,
            )

        return _result(operation)

    @server.tool(annotations=readonly)
    def list_versions() -> EnvelopeResult:
        """列出本机已有索引的版本和构建摘要；不可用索引显式标记 unavailable。"""
        return _result(queries.list_versions)

    @server.tool(annotations=readonly)
    def get_class(version: str, qualified_name: str) -> EnvelopeResult:
        """按版本和完整类名查询类、Supported/Extendable/Deprecated 与来源信息。"""
        return _result(lambda: queries.get_class(version, qualified_name))

    @server.tool(annotations=readonly)
    def search_method(
        version: str,
        qualified_name: str,
        method_name: str | None = None,
    ) -> EnvelopeResult:
        """按精确方法名返回全部重载；省略名称时列出本页方法。不展开继承方法。"""
        return _result(
            lambda: queries.search_method(
                version,
                qualified_name,
                method_name,
            )
        )

    @server.tool(annotations=readonly)
    def get_method(
        version: str,
        qualified_name: str,
        javadoc_id: str,
    ) -> EnvelopeResult:
        """按 search_method 返回的原始 javadoc_id 精确查询重载，保留 methods 数组格式。"""
        return _result(
            lambda: queries.get_method(
                version,
                qualified_name,
                javadoc_id,
            )
        )

    @server.tool(annotations=readonly)
    def get_index_status(version: str) -> EnvelopeResult:
        """读取索引存储的构建状态、校验值、schema/parser 版本及统计；不重新扫描或构建。"""
        return _result(lambda: queries.get_index_status(version))

    return server


if __name__ == "__main__":
    create_server().run(transport="stdio")