import re
from pathlib import Path
from zipfile import ZipFile

from bs4 import BeautifulSoup

from windchill_api_lookup.models import ApiClass, ApiMethod


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

    parts = qualified_class_name.split(".")

    with ZipFile(zip_file_path, "r") as zip_file:
        # Javadoc 将嵌套类写成 package/Outer.Inner.html。
        candidates = [
            "Javadoc/" + "/".join(parts[:index] + [".".join(parts[index:])]) + ".html"
            for index in range(len(parts) - 1, -1, -1)
        ]
        archive_paths = set(zip_file.namelist())
        matches = [path for path in candidates if path in archive_paths]
        if not matches:
            raise ValueError(
                f"在 Javadoc 中没有找到 Class: "
                f"{qualified_class_name}"
            )
        if len(matches) > 1:
            raise ValueError(f"Javadoc Class 路径不唯一: {qualified_class_name}")
        content = zip_file.read(matches[0])

    return content.decode("utf-8", errors="replace")

def parse_class_metadata(
    html: str,
    qualified_class_name: str,
) -> ApiClass:
    soup = BeautifulSoup(html, "lxml")

    title_element = soup.select_one("h1.title")

    if title_element is None:
        raise ValueError(
            "无法在 Javadoc HTML 中找到 Class Title"
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

    # 包名来自 HTML；不能用 rsplit('.') 推导，否则会误判嵌套类。
    prefix = f"{package_name}."
    if not qualified_class_name.startswith(prefix):
        raise ValueError("指定 Class 与 Javadoc Package 不匹配")
    class_name = qualified_class_name[len(prefix):]
    type_name_element = class_description.select_one(".type-name-label")
    if type_name_element is None:
        raise ValueError("无法在 Javadoc HTML 中找到 Class Name")
    type_name = type_name_element.get_text(" ", strip=True).split("<", 1)[0].strip()
    if class_name != type_name:
        raise ValueError("指定 Class 与 Javadoc Class Name 不匹配")

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

    return ApiClass(
        qualified_name=qualified_class_name,
        package_name=package_name,
        class_name=class_name,
        supported=supported,
        extendable=extendable,
        deprecated=class_description.select_one(".deprecation-block") is not None,
        description=description,
    )

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

    # 缺失和冲突均保留为未知，避免把 trueValue 之类的文本当成 true。
    values = {
        match.lower()
        for match in re.findall(
            rf"(?<!\w){re.escape(label)}\s*:\s*(true|false)\b",
            " ".join(text.split()),
            flags=re.IGNORECASE,
        )
    }
    if len(values) != 1:
        return None
    return values.pop() == "true"

def parse_methods(
    html: str,
    method_name: str | None = None,
) -> list[ApiMethod]:
    """
    解析 Javadoc Class 页面中的 Method Detail。

    如果指定 method_name，则只返回该名称的方法，
    包括所有 overload。
    """

    soup = BeautifulSoup(html, "lxml")

    methods: list[ApiMethod] = []

    # 字段和构造器也使用 section.detail，必须限制在 Method Details 内。
    for section in soup.select("section.method-details section.detail"):
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
            raise ValueError(f"Method 缺少 Signature: {name}")

        javadoc_id = section.get("id")
        if not isinstance(javadoc_id, str) or not javadoc_id.strip():
            raise ValueError(f"Method 缺少 Javadoc ID: {name}")

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
            # 部分异常类型只有纯文本，没有 <a> 链接。
            throws = [
                exception.strip()
                for exception in exceptions_element.get_text("", strip=False).split(",")
                if exception.strip()
            ]

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
            ApiMethod(
                name=name,
                javadoc_id=javadoc_id,
                signature=signature_element.get_text(
                    " ",
                    strip=True,
                ),
                return_type=return_type,
                parameters=parameters,
                throws=throws,
                supported=supported,
                deprecated=deprecated,
                description=description,
            )
        )

    return methods
