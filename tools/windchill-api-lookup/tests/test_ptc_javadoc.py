import os
from pathlib import Path

import pytest

from windchill_api_lookup.parser.ptc_javadoc import (
    parse_class_metadata,
    parse_methods,
    read_class_html,
)


JAVADOC_ZIP = os.environ.get(
    "WINDCHILL_JAVADOC_ZIP"
)


@pytest.fixture
def javadoc_zip() -> str:
    if not JAVADOC_ZIP:
        pytest.skip(
            "未设置 WINDCHILL_JAVADOC_ZIP"
        )

    path = Path(JAVADOC_ZIP)

    if not path.exists():
        pytest.skip(
            f"Javadoc ZIP 不存在: {path}"
        )

    return str(path)


def test_wtpart_metadata(javadoc_zip):
    html = read_class_html(
        javadoc_zip,
        "wt.part.WTPart",
    )

    metadata = parse_class_metadata(html, "wt.part.WTPart")

    assert metadata.qualified_name == "wt.part.WTPart"
    assert metadata.package_name == "wt.part"
    assert metadata.class_name == "WTPart"
    assert metadata.supported is True
    assert metadata.extendable is True
    assert metadata.deprecated is False


def test_work_in_progress_helper_metadata(
    javadoc_zip,
):
    html = read_class_html(
        javadoc_zip,
        "wt.vc.wip.WorkInProgressHelper",
    )

    metadata = parse_class_metadata(html, "wt.vc.wip.WorkInProgressHelper")

    assert metadata.package_name == "wt.vc.wip"
    assert metadata.supported is True
    assert metadata.extendable is False


def test_checkout_overloads(javadoc_zip):
    html = read_class_html(
        javadoc_zip,
        "wt.vc.wip.WorkInProgressService",
    )

    methods = parse_methods(
        html,
        "checkout",
    )

    assert len(methods) == 7

    first = methods[0]

    assert first.name == "checkout"

    assert first.javadoc_id == (
        "checkout("
        "wt.vc.wip.Workable,"
        "wt.folder.Folder,"
        "java.lang.String)"
    )

    assert first.return_type == "CheckoutLink"
    assert first.supported is True
    assert first.deprecated is False

    assert "WTException" in first.throws

    assert (
        "WorkInProgressException"
        in first.throws
    )

def test_class_not_found(javadoc_zip):
    with pytest.raises(
        ValueError,
        match="没有找到 Class",
    ):
        read_class_html(
            javadoc_zip,
            "wt.foo.ThisClassDoesNotExist",
        )


def test_full_index_matches_real_javadoc(javadoc_zip, tmp_path):
    from windchill_api_lookup.indexer import build_index
    from windchill_api_lookup.parser.ptc_javadoc import parse_class_page
    from windchill_api_lookup.repository import Repository

    result = build_index(javadoc_zip, "13.1.2.0", tmp_path)
    summary = result["summary"]
    assert summary["failed"] == 0
    assert summary["html_pages"] == summary["parsed_classes"] + summary["skipped"]
    repository = Repository(tmp_path, "13.1.2.0")
    for qualified_name in [
        "wt.part.WTPart", "wt.vc.wip.WorkInProgressHelper",
        "wt.vc.wip.WorkInProgressService",
        "wt.change2.flexible.FlexibleChangeHelper.ChangeAssociationMode",
        "wt.jmx.annotations.MBeanOperationImpact",
    ]:
        html = read_class_html(javadoc_zip, qualified_name)
        expected_class, expected_methods = parse_class_page(html, qualified_name)
        actual_class, actual_methods = repository.lookup_methods(qualified_name)
        expected_class.source_path = actual_class.source_path
        assert actual_class == expected_class
        assert actual_methods == sorted(expected_methods, key=lambda method: method.javadoc_id)
    assert len(repository.lookup_methods("wt.vc.wip.WorkInProgressService", "checkout")[1]) == 7
