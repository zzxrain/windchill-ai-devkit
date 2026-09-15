"""PTC 13.1.2.0 Javadoc parsing; database-independent public DTOs."""

import re
from pathlib import Path
from zipfile import ZipFile

from bs4 import BeautifulSoup, Tag

from windchill_api_lookup.models import (
    ApiClass,
    ApiMethod,
)


def read_class_html(
    zip_path: str,
    qualified_class_name: str,
) -> str:
    path = Path(zip_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Javadoc ZIP 不存在: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"指定路径不是文件: {path}"
        )

    parts = qualified_class_name.split(".")

    with ZipFile(path) as archive:
        candidates = [
            "Javadoc/"
            + "/".join(
                parts[:i]
                + [
                    ".".join(
                        parts[i:]
                    )
                ]
            )
            + ".html"
            for i in range(
                len(parts) - 1,
                -1,
                -1,
            )
        ]

        paths = set(
            archive.namelist()
        )

        matches = [
            candidate
            for candidate in candidates
            if candidate in paths
        ]

        if not matches:
            raise ValueError(
                "在 Javadoc 中没有找到 Class: "
                f"{qualified_class_name}"
            )

        if len(matches) > 1:
            raise ValueError(
                "Javadoc Class 路径不唯一: "
                f"{qualified_class_name}"
            )

        return archive.read(
            matches[0]
        ).decode(
            "utf-8",
            errors="replace",
        )


def _text(
    element: Tag | None,
) -> str:
    return (
        " ".join(
            element.get_text(
                " ",
                strip=True,
            ).split()
        )
        if element
        else ""
    )


def boolean_values(
    text: str,
    label: str,
) -> set[str]:
    return {
        value.lower()
        for value in re.findall(
            rf"(?<!\w)"
            rf"{re.escape(label)}"
            rf"\s*:\s*"
            rf"(true|false)\b",
            " ".join(
                text.split()
            ),
            flags=re.IGNORECASE,
        )
    }


def parse_boolean_metadata(
    text: str,
    label: str,
) -> bool | None:
    """
    缺失或冲突为未知，不把 trueValue 等文本识别为 true。
    """
    values = boolean_values(
        text,
        label,
    )

    return (
        values.pop() == "true"
        if len(values) == 1
        else None
    )


def _parse_class(
    soup: BeautifulSoup,
    qualified_name: str,
) -> ApiClass:
    title = soup.select_one(
        "h1.title"
    )

    if title is None:
        raise ValueError(
            "无法在 Javadoc HTML 中找到 Class Title"
        )

    package_label = soup.select_one(
        ".package-label-in-type"
    )

    if package_label is None:
        raise ValueError(
            "无法在 Javadoc HTML 中找到 Package"
        )

    package_name = _text(
        package_label.parent
    ).removeprefix(
        "Package "
    )

    section = soup.select_one(
        "section.class-description"
    )

    if section is None:
        raise ValueError(
            "无法在 Javadoc HTML 中找到 Class Description"
        )

    prefix = package_name + "."

    if not qualified_name.startswith(
        prefix
    ):
        raise ValueError(
            "指定 Class 与 Javadoc Package 不匹配"
        )

    class_name = qualified_name[
        len(prefix):
    ]

    name_element = section.select_one(
        ".type-name-label"
    )

    if name_element is None:
        raise ValueError(
            "无法在 Javadoc HTML 中找到 Class Name"
        )

    type_name = _text(
        name_element
    ).split(
        "<",
        1,
    )[0].strip()

    if type_name != class_name:
        raise ValueError(
            "指定 Class 与 Javadoc Class Name 不匹配"
        )

    kinds = {
        "Annotation Interface ": "annotation",
        "Annotation Type ": "annotation",
        "Enum Class ": "enum",
        "Enum ": "enum",
        "Record Class ": "record",
        "Interface ": "interface",
        "Class ": "class",
    }

    title_text = _text(title)

    kind = next(
        (
            value
            for label, value
            in kinds.items()
            if title_text.startswith(label)
        ),
        None,
    )

    if kind is None:
        raise ValueError(
            "无法识别 Class Kind: "
            f"{title_text}"
        )

    description = _text(
        section.select_one(
            "div.block"
        )
    )

    return ApiClass(
        qualified_name=qualified_name,
        package_name=package_name,
        class_name=class_name,
        supported=parse_boolean_metadata(
            description,
            "Supported API",
        ),
        extendable=parse_boolean_metadata(
            description,
            "Extendable",
        ),
        deprecated=(
            section.select_one(
                ".deprecation-block"
            )
            is not None
        ),
        description=description,
        class_kind=kind,
    )


def _parse_methods(
    soup: BeautifulSoup,
    method_name: str | None = None,
) -> list[ApiMethod]:
    methods = []
    seen = set()

    selector = (
        "section.method-details "
        "section.detail"
    )

    if _text(
        soup.select_one(
            "h1.title"
        )
    ).startswith(
        "Annotation "
    ):
        selector += (
            ", section.member-details "
            "section.detail"
        )

    for section in soup.select(
        selector
    ):
        signature = section.select_one(
            "div.member-signature"
        )

        name_element = section.select_one(
            "span.element-name"
        )

        if name_element is None:
            raise ValueError(
                "Method 缺少 Name: "
                f"{section.get('id')}"
            )

        name = _text(
            name_element
        )

        if signature is None:
            raise ValueError(
                f"Method 缺少 Signature: {name}"
            )

        anchor = section.get(
            "id"
        )

        if (
            not isinstance(
                anchor,
                str,
            )
            or not anchor.strip()
        ):
            raise ValueError(
                f"Method 缺少 Javadoc ID: {name}"
            )

        if anchor in seen:
            raise ValueError(
                "重复的 Method Javadoc ID: "
                f"{anchor}"
            )

        seen.add(anchor)

        return_type = signature.select_one(
            "span.return-type"
        )

        parameters = signature.select_one(
            "span.parameters"
        )

        if (
            return_type is None
            or (
                parameters is None
                and not anchor.endswith(
                    "()"
                )
            )
        ):
            raise ValueError(
                "Method 缺少 Return Type 或 Parameters: "
                f"{anchor}"
            )

        if (
            method_name is not None
            and name != method_name
        ):
            continue

        exceptions = signature.select_one(
            "span.exceptions"
        )

        throws = (
            []
            if exceptions is None
            else [
                " ".join(
                    part.split()
                )
                for part in exceptions.get_text(
                    "",
                    strip=False,
                ).split(",")
                if part.strip()
            ]
        )

        description = _text(
            section.select_one(
                "div.block"
            )
        )

        methods.append(
            ApiMethod(
                name=name,
                javadoc_id=anchor,
                signature=_text(
                    signature
                ),
                return_type=_text(
                    return_type
                ),
                parameters=(
                    _text(parameters)
                    if parameters
                    else "()"
                ),
                throws=throws,
                supported=parse_boolean_metadata(
                    description,
                    "Supported API",
                ),
                deprecated=(
                    section.select_one(
                        ".deprecation-block"
                    )
                    is not None
                ),
                description=description,
            )
        )

    return methods


def parse_class_metadata(
    html: str,
    qualified_class_name: str,
) -> ApiClass:
    return _parse_class(
        BeautifulSoup(
            html,
            "lxml",
        ),
        qualified_class_name,
    )


def parse_methods(
    html: str,
    method_name: str | None = None,
) -> list[ApiMethod]:
    """
    解析本页声明的方法；为兼容单独 HTML 片段，不验证 Class 容器。
    """
    return _parse_methods(
        BeautifulSoup(
            html,
            "lxml",
        ),
        method_name,
    )


def _has_fragment_link(
    section: Tag,
) -> bool:
    return (
        section.find(
            "a",
            href=lambda value: (
                isinstance(
                    value,
                    str,
                )
                and value.startswith("#")
            ),
        )
        is not None
    )


def parse_class_page(
    html: str,
    qualified_name: str,
    source_path: str = "",
) -> tuple[
    ApiClass,
    list[ApiMethod],
]:
    """
    批量入口：只构建一次 DOM，并检查无法解释的方法详情布局。
    """
    soup = BeautifulSoup(
        html,
        "lxml",
    )

    metadata = _parse_class(
        soup,
        qualified_name,
    )

    metadata.source_path = source_path

    recognized = {
        id(section)
        for section in soup.select(
            "section.method-details section.detail, "
            "section.field-details section.detail, "
            "section.constructor-details section.detail, "
            "section.constant-details section.detail"
            + (
                ", section.member-details section.detail"
                if metadata.class_kind == "annotation"
                else ""
            )
        )
    }

    if any(
        id(section) not in recognized
        for section in soup.select(
            "section.detail"
        )
    ):
        raise ValueError(
            "存在未识别的 Member Details 结构"
        )

    # This check runs for every parsed class page. Use BeautifulSoup's native
    # find() for the simple section lookup instead of invoking SoupSieve CSS
    # matching for another full-document selector pass.
    summary = soup.find(
        "section",
        class_="method-summary",
    )

    method_details = soup.find(
        "section",
        class_="method-details",
    )

    if (
        summary is not None
        and _has_fragment_link(summary)
        and method_details is None
    ):
        raise ValueError(
            "存在 Method Summary，但缺少 Method Details"
        )

    return (
        metadata,
        _parse_methods(soup),
    )