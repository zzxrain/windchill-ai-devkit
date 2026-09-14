"""Shared read-only application queries for CLI and MCP adapters."""

import os
from pathlib import Path

from windchill_api_lookup.repository import Repository, list_versions


def default_home() -> str:
    return os.environ.get("WINDCHILL_API_HOME", str(Path.home() / ".windchill-ai"))


class Queries:
    def __init__(self, home: str | Path):
        self.home = Path(home).expanduser()

    def list_versions(self) -> dict:
        return {"versions": list_versions(self.home)}

    def get_class(self, version: str, qualified_name: str) -> dict:
        return Repository(self.home, version).query(qualified_name)

    def search_method(self, version: str, qualified_name: str, method_name: str | None = None) -> dict:
        return Repository(self.home, version).query(qualified_name, include_methods=True, name=method_name)

    def get_method(self, version: str, qualified_name: str, javadoc_id: str) -> dict:
        return Repository(self.home, version).query(qualified_name, include_methods=True, javadoc_id=javadoc_id)

    def get_index_status(self, version: str) -> dict:
        # Stored build status and counts; no re-indexing or filesystem mutation.
        return {"version": version, "index": Repository(self.home, version).metadata()}
