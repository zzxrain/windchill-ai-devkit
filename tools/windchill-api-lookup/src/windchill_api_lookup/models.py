from dataclasses import dataclass, field


@dataclass
class ApiClass:
    qualified_name: str
    package_name: str
    class_name: str

    supported: bool | None
    extendable: bool | None
    deprecated: bool

    description: str = ""
    class_kind: str = "class"
    source_path: str = ""


@dataclass
class ApiMethod:
    name: str
    javadoc_id: str
    signature: str

    return_type: str | None

    supported: bool | None
    deprecated: bool

    parameters: str = ""
    throws: list[str] = field(default_factory=list)
    description: str = ""
