"""Storage, failure recovery and command contracts using actual temporary databases."""

import json
import sqlite3
from dataclasses import asdict
from zipfile import ZipFile

import pytest

from windchill_api_lookup.cli import main
from windchill_api_lookup.errors import ApiLookupError
from windchill_api_lookup.indexer import build_index
from windchill_api_lookup.parser.archive import ScanReport, scan_javadoc
from windchill_api_lookup.parser.ptc_javadoc import parse_class_page
from windchill_api_lookup.repository import Repository, list_versions
from windchill_api_lookup.storage import index_path
from test_parser_unit import CLASS_HTML, METHOD_HTML

VERSION = "13.1.2.0"
CLASS = "wt.example.Example"
SOURCE_PATH = "Javadoc/wt/example/Example.html"


@pytest.fixture
def archive(tmp_path):
    path = tmp_path / "javadoc.zip"
    with ZipFile(path, "w") as zip_file:
        zip_file.writestr(SOURCE_PATH, CLASS_HTML + METHOD_HTML)
        zip_file.writestr("Javadoc/wt/example/package-summary.html", "package")
        zip_file.writestr("Javadoc/wt/example/doc-files/info.html", b"\xff")
        zip_file.writestr("Javadoc/wt/example/class-use/Example.html", "usage")
    return path


@pytest.fixture
def home(tmp_path):
    return tmp_path / "data"


def test_archive_accounts_for_every_html(archive):
    report = ScanReport()
    for page in scan_javadoc(str(archive)):
        report.record(page)
    assert report.html_pages == 4
    assert report.candidates == report.parsed_classes == 1
    assert report.skipped == 3
    assert report.failed == 0
    assert report.methods == 2
    assert report.unknown_method_supported == 1
    assert report.pages[0]["diagnostics"][0]["subject"] == "run()"


def test_database_roundtrip_and_provenance(archive, home):
    result = build_index(archive, VERSION, home)
    assert result["class_count"] == 1
    assert result["method_count"] == 2
    expected_class, expected_methods = parse_class_page(CLASS_HTML + METHOD_HTML, CLASS, SOURCE_PATH)
    repository = Repository(home, VERSION)
    actual_class, actual_methods = repository.lookup_methods(CLASS, "run")
    assert actual_class == expected_class
    assert actual_methods == sorted(expected_methods, key=lambda method: method.javadoc_id)
    assert repository.get_class(CLASS) == expected_class
    assert repository.lookup_methods(CLASS, javadoc_id="run()")[1][0].supported is None
    payload = repository.query(CLASS, include_methods=True)
    assert payload["class"] == asdict(expected_class)
    assert payload["source"]["source_sha256"] == result["source_sha256"]
    assert payload["version"] == VERSION
    assert payload["methods"][0]["supported"] is None
    assert repository.report()["html_pages"] == 4
    assert list_versions(home)[0]["status"] == "complete"
    # Queries must be independent of the ZIP after import.
    archive.unlink()
    assert repository.get_class(CLASS).supported is True


def test_idempotent_import_and_explicit_replacement(archive, home):
    first = build_index(archive, VERSION, home)
    original = index_path(home, VERSION).read_bytes()
    second = build_index(archive, VERSION, home)
    assert second["reused"] is True
    assert second["generated_at"] == first["generated_at"]
    assert index_path(home, VERSION).read_bytes() == original
    with ZipFile(archive, "w") as zip_file:
        zip_file.writestr(SOURCE_PATH, CLASS_HTML + METHOD_HTML.replace("Run once.", "Run twice."))
    with pytest.raises(ApiLookupError) as error:
        build_index(archive, VERSION, home)
    assert error.value.code == "INDEX_CONFLICT"
    assert index_path(home, VERSION).read_bytes() == original
    rebuilt = build_index(archive, VERSION, home, replace=True)
    assert rebuilt["source_sha256"] != first["source_sha256"]
    assert rebuilt["method_count"] == 2


def test_bad_page_does_not_replace_working_index(archive, home):
    build_index(archive, VERSION, home)
    original = index_path(home, VERSION).read_bytes()
    with ZipFile(archive, "a") as zip_file:
        zip_file.writestr("Javadoc/wt/example/Broken.html", "unrecognized layout")
    with pytest.raises(ApiLookupError) as error:
        build_index(archive, VERSION, home, replace=True)
    assert error.value.code == "PARSE_FAILED"
    assert error.value.details["summary"]["failed"] == 1
    assert error.value.details["errors"][0]["source_path"].endswith("Broken.html")
    assert index_path(home, VERSION).read_bytes() == original
    assert not list(index_path(home, VERSION).parent.glob(".building-*"))
    assert not index_path(home, VERSION).with_suffix(".build.lock").exists()


def test_interrupted_build_preserves_old_index(archive, home, monkeypatch):
    build_index(archive, VERSION, home)
    original = index_path(home, VERSION).read_bytes()

    def interrupted(_):
        raise KeyboardInterrupt()

    monkeypatch.setattr("windchill_api_lookup.indexer.scan_javadoc", interrupted)
    with pytest.raises(KeyboardInterrupt):
        build_index(archive, VERSION, home, replace=True)
    assert index_path(home, VERSION).read_bytes() == original
    assert len(list(index_path(home, VERSION).parent.iterdir())) == 1


def test_publish_failure_preserves_old_index(archive, home, monkeypatch):
    build_index(archive, VERSION, home)
    original = index_path(home, VERSION).read_bytes()

    def denied(*_):
        raise OSError("cannot replace")

    monkeypatch.setattr("windchill_api_lookup.indexer.os.replace", denied)
    with pytest.raises(ApiLookupError, match="cannot replace"):
        build_index(archive, VERSION, home, replace=True)
    assert index_path(home, VERSION).read_bytes() == original


def test_concurrent_build_lock_is_respected(archive, home):
    target = index_path(home, VERSION)
    target.parent.mkdir(parents=True)
    lock = target.with_suffix(".build.lock")
    lock.write_text("another builder")
    with pytest.raises(ApiLookupError) as error:
        build_index(archive, VERSION, home)
    assert error.value.code == "BUILD_IN_PROGRESS"
    assert lock.read_text() == "another builder"


def test_source_change_prevents_publication(archive, home, monkeypatch):
    digests = iter(["before", "after"])
    monkeypatch.setattr("windchill_api_lookup.indexer._sha256", lambda _: next(digests))
    with pytest.raises(ApiLookupError) as error:
        build_index(archive, VERSION, home)
    assert error.value.code == "SOURCE_CHANGED"
    assert not index_path(home, VERSION).exists()


def test_not_found_and_version_isolation(archive, home):
    build_index(archive, VERSION, home)
    repository = Repository(home, VERSION)
    for query in [lambda: repository.get_class("missing.Class"),
                  lambda: repository.lookup_methods(CLASS, "missing"),
                  lambda: repository.lookup_methods(CLASS, javadoc_id="run(int)"),
                  lambda: repository.get_class("' OR 1=1 --")]:
        with pytest.raises(ApiLookupError) as error:
            query()
        assert error.value.code == "NOT_FOUND"
    with pytest.raises(ApiLookupError) as error:
        Repository(home, "13.0.2.0").get_class(CLASS)
    assert error.value.code == "VERSION_NOT_INSTALLED"
    assert not index_path(home, "13.0.2.0").exists()


@pytest.mark.parametrize("version", ["../13.1", "", "/tmp/data", "13.x", "13.1/other"])
def test_version_cannot_escape_home(archive, home, version):
    with pytest.raises(ApiLookupError) as error:
        build_index(archive, version, home)
    assert error.value.code == "INVALID_ARGUMENT"
    assert not home.exists()


@pytest.mark.parametrize("corruption", ["schema", "status", "bytes"])
def test_unavailable_index_is_not_not_found(archive, home, corruption):
    build_index(archive, VERSION, home)
    target = index_path(home, VERSION)
    if corruption == "bytes":
        target.write_bytes(b"not a database")
    else:
        connection = sqlite3.connect(target)
        with connection:
            connection.execute("PRAGMA user_version = 999" if corruption == "schema" else "DELETE FROM index_metadata")
        connection.close()
    with pytest.raises(ApiLookupError) as error:
        Repository(home, VERSION).get_class(CLASS)
    assert error.value.code == "INDEX_UNAVAILABLE"
    assert list_versions(home)[0]["status"] == "unavailable"


def test_cli_build_query_and_error_contracts(archive, home, capsys):
    common = ["--version", VERSION, "--home", str(home), "--json"]
    assert main(["add-javadoc", "--zip", str(archive), *common]) == 0
    assert json.loads(capsys.readouterr().out)["class_count"] == 1
    assert main(["get-method", *common, CLASS, "run()"]) == 0
    captured = capsys.readouterr()
    result = json.loads(captured.out)
    assert captured.err == ""
    assert result["methods"][0]["javadoc_id"] == "run()"
    assert result["class"]["supported"] is True
    assert main(["search-method", *common, CLASS, "missing"]) == 3
    captured = capsys.readouterr()
    assert captured.out == ""
    assert json.loads(captured.err)["error"]["code"] == "NOT_FOUND"
    assert main(["get-class", "--json"]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert json.loads(captured.err)["error"]["code"] == "INVALID_ARGUMENT"


def test_conflicting_metadata_has_diagnostic(archive):
    with ZipFile(archive, "w") as zip_file:
        zip_file.writestr(SOURCE_PATH, CLASS_HTML.replace("Example description.", "Supported API: false"))
    page = next(scan_javadoc(str(archive)))
    assert page.api_class.supported is None
    assert page.diagnostics[0]["code"] == "METADATA_CONFLICT"


def test_unknown_structure_and_missing_method_name_are_errors():
    with pytest.raises(ValueError, match="未识别"):
        parse_class_page(CLASS_HTML + '<section class="detail" id="unknown"></section>', CLASS)
    with pytest.raises(ValueError, match="Name"):
        parse_class_page(CLASS_HTML + METHOD_HTML.replace('class="element-name"', 'class="missing"'), CLASS)


def test_no_arg_method_without_parameter_span():
    html = CLASS_HTML + METHOD_HTML.replace('<span class="parameters">()</span>', "()")
    _, methods = parse_class_page(html, CLASS)
    assert methods[1].parameters == "()"


def test_annotation_elements_and_enum_constants():
    annotation = CLASS_HTML.replace("Class Example", "Annotation Interface Example")
    html = annotation + '''<section class="member-details"><section class="detail" id="value()">
        <div class="member-signature"><span class="return-type">int</span>
        <span class="element-name">value</span></div></section></section>'''
    metadata, methods = parse_class_page(html, CLASS)
    assert metadata.class_kind == "annotation"
    assert methods[0].javadoc_id == "value()"
    enum_html = CLASS_HTML.replace("Class Example", "Enum Class Example")
    metadata, methods = parse_class_page(enum_html + '<section class="constant-details"><section class="detail" id="ONE"></section></section>', CLASS)
    assert metadata.class_kind == "enum"
    assert methods == []


@pytest.mark.parametrize("content", ["empty", "corrupt", "duplicate"])
def test_invalid_archive_never_publishes(archive, home, content):
    if content == "corrupt":
        archive.write_bytes(b"not a zip")
    elif content == "empty":
        with ZipFile(archive, "w"):
            pass
    else:
        with ZipFile(archive, "a") as zip_file:
            with pytest.warns(UserWarning, match="Duplicate"):
                zip_file.writestr(SOURCE_PATH, CLASS_HTML)
    with pytest.raises(ApiLookupError) as error:
        build_index(archive, VERSION, home)
    assert error.value.code == "PARSE_FAILED"
    assert not index_path(home, VERSION).exists()
    assert not index_path(home, VERSION).with_suffix(".build.lock").exists()


def test_summary_without_method_details_fails():
    html = CLASS_HTML + '<section class="method-summary"><a href="#run()">run</a></section>'
    with pytest.raises(ValueError, match="Method Summary"):
        parse_class_page(html, CLASS)
