"""Command-line adapter; JSON results on stdout, errors on stderr."""

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from zipfile import BadZipFile

from windchill_api_lookup.errors import ApiLookupError
from windchill_api_lookup.indexer import build_index
from windchill_api_lookup.parser.archive import ScanReport, scan_javadoc
from windchill_api_lookup.parser.ptc_javadoc import parse_class_metadata, parse_methods, read_class_html
from windchill_api_lookup.repository import Repository
from windchill_api_lookup.queries import Queries, default_home
from windchill_api_lookup.responses import failure, success

EXIT_CODES = {
    "INVALID_ARGUMENT": 2, "NOT_FOUND": 3, "VERSION_NOT_INSTALLED": 4,
    "PARSE_FAILED": 5, "INDEX_UNAVAILABLE": 6, "INDEX_CONFLICT": 7,
    "BUILD_IN_PROGRESS": 7, "SOURCE_CHANGED": 7,
}


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ApiLookupError("INVALID_ARGUMENT", message)


def _parser() -> ArgumentParser:
    parser = ArgumentParser(description="查询本地 Windchill Javadoc API 索引")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("scan-javadoc", "add-javadoc", "versions", "get-class", "search-method", "get-method", "get-index-status", "index-report"):
        command = commands.add_parser(name)
        command.add_argument("--json", action="store_true", help="输出结构化 JSON")
        command.add_argument("--home", default=default_home(),
                             help="数据根目录，索引位于其 api-index 子目录")
        if name in {"scan-javadoc", "add-javadoc"}:
            command.add_argument("--zip", required=True, dest="zip_path")
        if name not in {"scan-javadoc", "versions"}:
            command.add_argument("--version", required=True)
        if name == "add-javadoc":
            command.add_argument("--replace", action="store_true", help="构建成功后替换已有版本索引")
        if name in {"get-class", "search-method", "get-method"}:
            command.add_argument("qualified_name")
        if name == "search-method":
            command.add_argument("method_name", nargs="?", help="精确名称；省略时列出本页全部方法")
        if name == "get-method":
            command.add_argument("javadoc_id", help="原始重载锚点，含括号时请加引号")
    serve = commands.add_parser("serve", help="启动只读 stdio MCP 服务")
    serve.add_argument("--home", default=default_home(), help="本地索引数据根目录")
    return parser


def _run(args) -> dict:
    if args.command == "scan-javadoc":
        source = Path(args.zip_path).expanduser()
        if not source.is_file():
            raise ApiLookupError("INVALID_ARGUMENT", f"Javadoc ZIP 不存在或不是文件: {source}")
        report = ScanReport()
        for page in scan_javadoc(str(source)):
            report.record(page)
        if report.failed or not report.parsed_classes:
            raise ApiLookupError("PARSE_FAILED", "全量扫描未通过", {"report": asdict(report)})
        return {"report": asdict(report)}
    if args.command == "add-javadoc":
        return build_index(args.zip_path, args.version, args.home, args.replace)
    queries = Queries(args.home)
    if args.command == "versions":
        return queries.list_versions()
    if args.command == "get-index-status":
        return queries.get_index_status(args.version)
    if args.command == "index-report":
        return {"version": args.version, "report": Repository(args.home, args.version).report()}
    if args.command == "get-class":
        return queries.get_class(args.version, args.qualified_name)
    if args.command == "search-method":
        return queries.search_method(args.version, args.qualified_name, args.method_name)
    return queries.get_method(args.version, args.qualified_name, args.javadoc_id)


def _legacy(argv: list[str]) -> None:
    html = read_class_html(argv[0], argv[1])
    if len(argv) == 2:
        metadata = parse_class_metadata(html, argv[1])
        print(f"Class:      {metadata.qualified_name}")
        print(f"Package:    {metadata.package_name}")
        print(f"Supported:  {metadata.supported}")
        print(f"Extendable: {metadata.extendable}")
        print(f"Deprecated: {metadata.deprecated}")
    else:
        methods = parse_methods(html, argv[2])
        print(f"Methods: {argv[1]}.{argv[2]}")
        print(f"Overloads: {len(methods)}")
        for method in methods:
            print(f"ID:         {method.javadoc_id}")
            print(f"Signature:  {method.signature}")
            print(f"Return:     {method.return_type}")
            print(f"Supported:  {method.supported}")
            print(f"Deprecated: {method.deprecated}")
            print(f"Throws:     {', '.join(method.throws)}")


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    try:
        if len(argv) in (2, 3) and argv[0].lower().endswith(".zip"):
            _legacy(argv)
            return 0
        args = _parser().parse_args(argv)
        if args.command == "serve":
            from windchill_api_lookup.server import create_server
            create_server(args.home).run(transport="stdio")
            return 0
        result = _run(args)
        # Human output is formatted JSON in v1, with a stable machine envelope.
        print(json.dumps(success(result), ensure_ascii=False, indent=None if args.json else 2))
        return 0
    except (ApiLookupError, OSError, BadZipFile, ValueError) as exc:
        if not isinstance(exc, ApiLookupError):
            exc = ApiLookupError("PARSE_FAILED" if isinstance(exc, (ValueError, BadZipFile)) else "INDEX_UNAVAILABLE", str(exc))
        print(json.dumps(failure(exc),
                         ensure_ascii=False), file=sys.stderr)
        return EXIT_CODES[exc.code]


if __name__ == "__main__":
    raise SystemExit(main())
