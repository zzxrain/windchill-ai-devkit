"""SQLite v1 schema and version-scoped index locations."""

import re
import sqlite3
from pathlib import Path

from windchill_api_lookup.errors import ApiLookupError

SCHEMA_VERSION = 1
PARSER_VERSION = "0.2.0"

SCHEMA = """
PRAGMA foreign_keys = ON;
PRAGMA user_version = 1;
CREATE TABLE index_metadata (
    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
    windchill_version TEXT NOT NULL,
    source_sha256 TEXT NOT NULL,
    schema_version INTEGER NOT NULL,
    parser_version TEXT NOT NULL,
    generated_at TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status = 'complete'),
    class_count INTEGER NOT NULL,
    method_count INTEGER NOT NULL,
    report_json TEXT NOT NULL
);
CREATE TABLE api_class (
    id INTEGER PRIMARY KEY,
    qualified_name TEXT NOT NULL UNIQUE,
    package_name TEXT NOT NULL,
    class_name TEXT NOT NULL,
    class_kind TEXT NOT NULL,
    supported INTEGER CHECK (supported IN (0, 1)),
    extendable INTEGER CHECK (extendable IN (0, 1)),
    deprecated INTEGER NOT NULL CHECK (deprecated IN (0, 1)),
    description TEXT NOT NULL,
    source_path TEXT NOT NULL
);
CREATE INDEX api_class_name_idx ON api_class(class_name);
CREATE TABLE api_method (
    id INTEGER PRIMARY KEY,
    class_id INTEGER NOT NULL REFERENCES api_class(id),
    name TEXT NOT NULL,
    javadoc_id TEXT NOT NULL,
    signature TEXT NOT NULL,
    return_type TEXT,
    supported INTEGER CHECK (supported IN (0, 1)),
    deprecated INTEGER NOT NULL CHECK (deprecated IN (0, 1)),
    parameters TEXT NOT NULL,
    throws_json TEXT NOT NULL,
    description TEXT NOT NULL,
    UNIQUE (class_id, javadoc_id)
);
CREATE INDEX api_method_name_idx ON api_method(class_id, name);
"""


def validate_version(version: str) -> str:
    """
    Validate a project-supplied Windchill release identifier.

    The lookup tool deliberately does not encode Windchill product-version
    semantics. A release identifier is treated as one to four numeric
    segments, for example:

        13.1.2.0
        2027
        2027.0
        2027.0.0
        2027.0.0.0

    The value must come from project context and is never inferred from a
    Javadoc filename.
    """
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]+){0,3}", version):
        raise ApiLookupError(
            "INVALID_ARGUMENT",
            "版本必须为 1～4 段数字版本标识，例如 13.1.2.0、2027 或 2027.0.0.0",
        )
    return version


def index_path(home: str | Path, version: str) -> Path:
    return (
        Path(home).expanduser()
        / "api-index"
        / validate_version(version)
        / "api.sqlite"
    )


def connect_readonly(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(
        path.resolve().as_uri() + "?mode=ro",
        uri=True,
    )
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only = ON")
    return connection