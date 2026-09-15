"""Build a temporary index, validate it, then atomically publish it."""

import hashlib
import json
import os
import sqlite3
import tempfile
from collections.abc import Callable
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from windchill_api_lookup.errors import ApiLookupError
from windchill_api_lookup.parser.archive import ScanReport, scan_javadoc
from windchill_api_lookup.repository import Repository
from windchill_api_lookup.storage import (
    PARSER_VERSION,
    SCHEMA,
    SCHEMA_VERSION,
    index_path,
)

ProgressCallback = Callable[
    [str, int | None, int | None],
    None,
]


def _emit_progress(
    callback: ProgressCallback | None,
    phase: str,
    current: int | None = None,
    total: int | None = None,
) -> None:
    if callback is not None:
        callback(phase, current, total)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(
            lambda: stream.read(1024 * 1024),
            b"",
        ):
            digest.update(block)
    return digest.hexdigest()


def _count_html_pages(path: Path) -> int:
    with ZipFile(path) as archive:
        return sum(
            1
            for entry in archive.infolist()
            if entry.filename.endswith(".html")
            and not entry.is_dir()
        )


def build_index(
    zip_path: str | Path,
    version: str,
    home: str | Path,
    replace: bool = False,
    progress: ProgressCallback | None = None,
) -> dict:
    """
    Build or reuse a version-scoped Javadoc index.

    Version is explicitly supplied by project context or the operator and is
    never guessed from the Javadoc filename.
    """
    source = Path(zip_path).expanduser()
    target = index_path(home, version)

    if not source.is_file():
        raise ApiLookupError(
            "INVALID_ARGUMENT",
            f"Javadoc ZIP 不存在或不是文件: {source}",
        )

    if source.resolve() == target.resolve():
        raise ApiLookupError(
            "INVALID_ARGUMENT",
            "ZIP 与索引输出路径不能相同",
        )

    target.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    lock = target.with_suffix(".build.lock")

    try:
        lock_stream = lock.open("x")
    except FileExistsError as exc:
        raise ApiLookupError(
            "BUILD_IN_PROGRESS",
            f"该版本已有构建锁: {lock}",
        ) from exc

    temporary = None

    try:
        with lock_stream:
            lock_stream.write(str(os.getpid()))

        _emit_progress(
            progress,
            "checksum",
        )

        checksum = _sha256(source)

        if target.exists():
            try:
                current = Repository(
                    home,
                    version,
                ).metadata()
            except ApiLookupError:
                if not replace:
                    raise
            else:
                if (
                    current["source_sha256"] == checksum
                    and current["parser_version"] == PARSER_VERSION
                    and not replace
                ):
                    _emit_progress(
                        progress,
                        "reused",
                    )
                    return {
                        **current,
                        "reused": True,
                        "index_path": str(target),
                    }

                if not replace:
                    raise ApiLookupError(
                        "INDEX_CONFLICT",
                        "该版本已有不同来源或解析器版本的索引；"
                        "使用 --replace 明确重建",
                    )

        _emit_progress(
            progress,
            "discovering",
        )

        total_html_pages = _count_html_pages(source)

        fd, name = tempfile.mkstemp(
            prefix=".building-",
            suffix=".sqlite",
            dir=target.parent,
        )
        os.close(fd)

        temporary = Path(name)
        report = ScanReport()
        connection = sqlite3.connect(temporary)

        try:
            connection.executescript(SCHEMA)

            with connection:
                for processed, page in enumerate(
                    scan_javadoc(str(source)),
                    start=1,
                ):
                    if page.status == "parsed":
                        metadata = asdict(
                            page.api_class
                        )

                        cursor = connection.execute(
                            "INSERT INTO api_class "
                            "(qualified_name, package_name, class_name, "
                            "class_kind, supported, extendable, deprecated, "
                            "description, source_path) VALUES "
                            "(:qualified_name, :package_name, :class_name, "
                            ":class_kind, :supported, :extendable, "
                            ":deprecated, :description, :source_path)",
                            metadata,
                        )

                        class_id = cursor.lastrowid

                        for method in page.methods:
                            values = asdict(method)
                            values["class_id"] = class_id
                            values["throws_json"] = json.dumps(
                                values.pop("throws"),
                                ensure_ascii=False,
                            )

                            connection.execute(
                                "INSERT INTO api_method "
                                "(class_id, name, javadoc_id, signature, "
                                "return_type, supported, deprecated, "
                                "parameters, throws_json, description) "
                                "VALUES "
                                "(:class_id, :name, :javadoc_id, "
                                ":signature, :return_type, :supported, "
                                ":deprecated, :parameters, :throws_json, "
                                ":description)",
                                values,
                            )

                    report.record(page)

                    _emit_progress(
                        progress,
                        "indexing",
                        processed,
                        total_html_pages,
                    )

                if (
                    report.failed
                    or not report.parsed_classes
                ):
                    raise ApiLookupError(
                        "PARSE_FAILED",
                        "全量解析未通过，未发布索引",
                        {
                            "summary": report.summary(),
                            "errors": [
                                page
                                for page in report.pages
                                if page["status"] == "error"
                            ],
                        },
                    )

                _emit_progress(
                    progress,
                    "validating",
                )

                if _sha256(source) != checksum:
                    raise ApiLookupError(
                        "SOURCE_CHANGED",
                        "构建期间 ZIP 发生变化，未发布索引",
                    )

                generated_at = datetime.now(
                    timezone.utc
                ).isoformat()

                connection.execute(
                    "INSERT INTO index_metadata "
                    "VALUES "
                    "(1, ?, ?, ?, ?, ?, 'complete', ?, ?, ?)",
                    (
                        version,
                        checksum,
                        SCHEMA_VERSION,
                        PARSER_VERSION,
                        generated_at,
                        report.parsed_classes,
                        report.methods,
                        json.dumps(
                            asdict(report),
                            ensure_ascii=False,
                        ),
                    ),
                )

                if (
                    connection.execute(
                        "PRAGMA integrity_check"
                    ).fetchone()[0]
                    != "ok"
                ):
                    raise ApiLookupError(
                        "INDEX_UNAVAILABLE",
                        "索引完整性检查失败",
                    )

                if (
                    connection.execute(
                        "PRAGMA foreign_key_check"
                    ).fetchone()
                    is not None
                ):
                    raise ApiLookupError(
                        "INDEX_UNAVAILABLE",
                        "索引外键检查失败",
                    )
        finally:
            connection.close()

        _emit_progress(
            progress,
            "publishing",
        )

        # SQLite is closed before publication, including on Windows.
        os.replace(
            temporary,
            target,
        )
        temporary = None

        _emit_progress(
            progress,
            "complete",
            total_html_pages,
            total_html_pages,
        )

        return {
            **Repository(
                home,
                version,
            ).metadata(),
            "reused": False,
            "index_path": str(target),
        }

    except (
        BadZipFile,
        UnicodeError,
    ) as exc:
        raise ApiLookupError(
            "PARSE_FAILED",
            f"无法解析 ZIP: {exc}",
        ) from exc

    except sqlite3.IntegrityError as exc:
        raise ApiLookupError(
            "PARSE_FAILED",
            f"索引数据约束冲突: {exc}",
        ) from exc

    except (
        OSError,
        sqlite3.Error,
    ) as exc:
        raise ApiLookupError(
            "INDEX_UNAVAILABLE",
            f"索引构建失败: {exc}",
        ) from exc

    finally:
        if temporary is not None:
            temporary.unlink(
                missing_ok=True
            )

        lock.unlink(
            missing_ok=True
        )