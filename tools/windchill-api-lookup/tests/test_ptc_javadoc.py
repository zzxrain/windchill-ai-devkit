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

    metadata = parse_class_metadata(html)

    assert metadata["package"] == "wt.part"
    assert metadata["supported"] is True
    assert metadata["extendable"] is True


def test_work_in_progress_helper_metadata(
    javadoc_zip,
):
    html = read_class_html(
        javadoc_zip,
        "wt.vc.wip.WorkInProgressHelper",
    )

    metadata = parse_class_metadata(html)

    assert metadata["package"] == "wt.vc.wip"
    assert metadata["supported"] is True
    assert metadata["extendable"] is False


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

    assert first["name"] == "checkout"

    assert first["javadoc_id"] == (
        "checkout("
        "wt.vc.wip.Workable,"
        "wt.folder.Folder,"
        "java.lang.String)"
    )

    assert first["return_type"] == "CheckoutLink"
    assert first["supported"] is True
    assert first["deprecated"] is False

    assert "WTException" in first["throws"]

    assert (
        "WorkInProgressException"
        in first["throws"]
    )