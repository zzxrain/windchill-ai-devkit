from bs4 import BeautifulSoup
from pathlib import Path
from zipfile import ZipFile


def read_class_html(
    zip_path: str,
    qualified_class_name: str,
) -> str:
    """
    从 Windchill Javadoc ZIP 中读取指定 Java Class 的 HTML。

    例如：
        wt.part.WTPart
    转换为：
        Javadoc/wt/part/WTPart.html
    """

    zip_file_path = Path(zip_path)

    if not zip_file_path.exists():
        raise FileNotFoundError(
            f"Javadoc ZIP 不存在: {zip_file_path}"
        )

    if not zip_file_path.is_file():
        raise ValueError(
            f"指定路径不是文件: {zip_file_path}"
        )

    class_path = qualified_class_name.replace(".", "/")
    html_path = f"Javadoc/{class_path}.html"

    with ZipFile(zip_file_path, "r") as zip_file:
        try:
            content = zip_file.read(html_path)
        except KeyError as exc:
            raise ValueError(
                f"在 Javadoc 中没有找到 Class: "
                f"{qualified_class_name}"
            ) from exc

    return content.decode("utf-8", errors="replace")

def parse_class_metadata(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")

    title_element = soup.select_one("h1.title")

    if title_element is None:
        raise ValueError(
            "无法在 Javadoc HTML 中找到 Class Title"
        )

    title = title_element.get_text(
        " ",
        strip=True,
    )

    package_element = soup.select_one(
        ".package-label-in-type"
    )

    if package_element is None:
        raise ValueError(
            "无法在 Javadoc HTML 中找到 Package"
        )

    package_text = package_element.parent.get_text(
        " ",
        strip=True,
    )

    package_name = package_text.removeprefix(
        "Package "
    )

    class_description = soup.select_one(
        "section.class-description"
    )

    if class_description is None:
        raise ValueError(
            "无法在 Javadoc HTML 中找到 Class Description"
        )

    block = class_description.select_one(
        "div.block"
    )

    description = ""

    if block is not None:
        description = block.get_text(
            " ",
            strip=True,
        )

    supported = parse_boolean_metadata(
        description,
        "Supported API",
    )

    extendable = parse_boolean_metadata(
        description,
        "Extendable",
    )

    return {
        "title": title,
        "package": package_name,
        "description": description,
        "supported": supported,
        "extendable": extendable,
    }

def parse_boolean_metadata(
    text: str,
    label: str,
) -> bool | None:
    """
    从普通文本中提取 PTC boolean metadata。

    例如：
        Supported API: true
        Extendable: false
    """

    normalized_text = " ".join(
        text.split()
    )

    true_value = f"{label}: true"
    false_value = f"{label}: false"

    if true_value in normalized_text:
        return True

    if false_value in normalized_text:
        return False

    return None

def parse_methods(
    html: str,
    method_name: str | None = None,
) -> list[dict]:
    """
    解析 Javadoc Class 页面中的 Method Detail。

    如果指定 method_name，则只返回该名称的方法，
    包括所有 overload。
    """

    soup = BeautifulSoup(html, "lxml")

    methods = []

    for section in soup.select("section.detail"):
        name_element = section.select_one(
            "span.element-name"
        )

        if name_element is None:
            continue

        name = name_element.get_text(
            " ",
            strip=True,
        )

        if method_name is not None and name != method_name:
            continue

        signature_element = section.select_one(
            "div.member-signature"
        )

        if signature_element is None:
            continue

        return_type_element = section.select_one(
            "span.return-type"
        )

        parameters_element = section.select_one(
            "span.parameters"
        )

        exceptions_element = section.select_one(
            "span.exceptions"
        )

        description_element = section.select_one(
            "div.block"
        )

        return_type = None

        if return_type_element is not None:
            return_type = return_type_element.get_text(
                " ",
                strip=True,
            )

        parameters = ""

        if parameters_element is not None:
            parameters = parameters_element.get_text(
                " ",
                strip=True,
            )

        throws = []

        if exceptions_element is not None:
            for exception_link in exceptions_element.select("a"):
                exception_name = exception_link.get_text(
                    " ",
                    strip=True,
                )

                throws.append(exception_name)

        description = ""

        if description_element is not None:
            description = description_element.get_text(
                " ",
                strip=True,
            )

        supported = parse_boolean_metadata(
            description,
            "Supported API",
        )

        deprecated = (
            section.select_one(
                ".deprecation-block"
            )
            is not None
        )

        methods.append(
            {
                "name": name,
                "javadoc_id": section.get("id"),
                "signature": signature_element.get_text(
                    " ",
                    strip=True,
                ),
                "return_type": return_type,
                "parameters": parameters,
                "throws": throws,
                "supported": supported,
                "deprecated": deprecated,
                "description": description,
            }
        )

    return methods