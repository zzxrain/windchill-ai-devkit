"""Read-only, version-specific queries. No ZIP access during lookup."""

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path

from windchill_api_lookup.errors import ApiLookupError
from windchill_api_lookup.models import ApiClass, ApiMethod
from windchill_api_lookup.storage import SCHEMA_VERSION, connect_readonly, index_path


def _class(row) -> ApiClass:
    values = dict(row)
    values.pop("id")
    for field in ("supported", "extendable", "deprecated"):
        values[field] = None if values[field] is None else bool(values[field])
    return ApiClass(**values)


def _method(row) -> ApiMethod:
    values = dict(row)
    values.pop("id")
    values.pop("class_id")
    values["throws"] = json.loads(values.pop("throws_json"))
    for field in ("supported", "deprecated"):
        values[field] = None if values[field] is None else bool(values[field])
    return ApiMethod(**values)


class Repository:
    def __init__(self, home: str | Path, version: str):
        self.version = version
        self.path = index_path(home, version)

    @contextmanager
    def _open(self):
        if not self.path.exists():
            raise ApiLookupError("VERSION_NOT_INSTALLED", f"未安装版本: {self.version}")
        connection = None
        try:
            connection = connect_readonly(self.path)
            if connection.execute("PRAGMA user_version").fetchone()[0] != SCHEMA_VERSION:
                raise ApiLookupError("INDEX_UNAVAILABLE", "索引 schema 版本不兼容，请重新构建")
            metadata = connection.execute("SELECT * FROM index_metadata WHERE singleton = 1").fetchone()
            if (metadata is None or metadata["status"] != "complete"
                    or metadata["schema_version"] != SCHEMA_VERSION
                    or metadata["windchill_version"] != self.version):
                raise ApiLookupError("INDEX_UNAVAILABLE", "索引未完成或版本不匹配")
            yield connection, metadata
        except (sqlite3.Error, ValueError, TypeError, KeyError) as exc:
            raise ApiLookupError("INDEX_UNAVAILABLE", f"索引不可用: {exc}") from exc
        finally:
            if connection is not None:
                connection.close()

    def metadata(self) -> dict:
        with self._open() as (_, metadata):
            result = dict(metadata)
            result.pop("singleton")
            report = json.loads(result.pop("report_json"))
            result["summary"] = {key: value for key, value in report.items() if key != "pages"}
            return result

    def report(self) -> dict:
        with self._open() as (_, metadata):
            return json.loads(metadata["report_json"])

    def query(self, qualified_name: str, *, include_methods: bool = False,
              name: str | None = None, javadoc_id: str | None = None) -> dict:
        """Return provenance and records from the same database snapshot."""
        with self._open() as (connection, metadata):
            row = self._class_row(connection, qualified_name)
            result = {
                "version": self.version,
                "source": {key: metadata[key] for key in
                           ("source_sha256", "parser_version", "schema_version")},
                "class": asdict(_class(row)),
            }
            if include_methods:
                result["methods"] = [asdict(method) for method in
                                     self._methods(connection, row["id"], name, javadoc_id)]
            return result

    def get_class(self, qualified_name: str) -> ApiClass:
        with self._open() as (connection, _):
            row = self._class_row(connection, qualified_name)
            return _class(row)

    @staticmethod
    def _class_row(connection, qualified_name):
        row = connection.execute("SELECT * FROM api_class WHERE qualified_name = ?", (qualified_name,)).fetchone()
        if row is None:
            raise ApiLookupError("NOT_FOUND", f"Class 不存在: {qualified_name}")
        return row

    def lookup_methods(self, qualified_name: str, name: str | None = None,
                       javadoc_id: str | None = None) -> tuple[ApiClass, list[ApiMethod]]:
        with self._open() as (connection, _):
            row = self._class_row(connection, qualified_name)
            return _class(row), self._methods(connection, row["id"], name, javadoc_id)

    @staticmethod
    def _methods(connection, class_id, name, javadoc_id):
        sql = "SELECT * FROM api_method WHERE class_id = ?"
        params = [class_id]
        if name is not None:
            sql += " AND name = ?"
            params.append(name)
        if javadoc_id is not None:
            sql += " AND javadoc_id = ?"
            params.append(javadoc_id)
        methods = [_method(item) for item in connection.execute(sql + " ORDER BY javadoc_id", params)]
        if not methods and (name is not None or javadoc_id is not None):
            raise ApiLookupError("NOT_FOUND", f"Method 不存在: {javadoc_id or name}")
        return methods


def list_versions(home: str | Path) -> list[dict]:
    results = []
    for path in sorted((Path(home).expanduser() / "api-index").glob("*/api.sqlite")):
        try:
            results.append(Repository(home, path.parent.name).metadata())
        except ApiLookupError as exc:
            results.append({"windchill_version": path.parent.name, "status": "unavailable", "error": exc.code})
    return results
