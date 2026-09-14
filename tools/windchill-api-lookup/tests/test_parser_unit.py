"""无需本地 PTC ZIP 的回归测试；HTML 片段按 13.1.2.0 的结构构造。"""

from zipfile import ZipFile

import pytest

from windchill_api_lookup.cli import main
from windchill_api_lookup.models import ApiClass, ApiMethod
from windchill_api_lookup.parser.ptc_javadoc import (
    parse_boolean_metadata,
    parse_class_metadata,
    parse_methods,
    read_class_html,
)


CLASS_HTML = """
<div class="header">
  <div class="sub-title"><span class="package-label-in-type">Package</span>
    <a href="package-summary.html">wt.example</a></div>
  <h1 class="title">Class Example</h1>
</div>
<section class="class-description">
  <div class="type-signature"><span class="type-name-label">Example</span></div>
  <div class="block">Example description.
    <br><b>Supported API: </b>true<br><b>Extendable: </b>false</div>
</section>
"""

METHOD_HTML = """
<section class="field-details"><section class="detail" id="service">
  <div class="member-signature"><span class="return-type">Service</span>
    <span class="element-name">service</span></div>
</section></section>
<section class="constructor-details"><section class="detail" id="Example()">
  <div class="member-signature"><span class="element-name">Example</span>
    <span class="parameters">()</span></div>
</section></section>
<section class="method-details" id="method-detail">
  <section class="detail" id="run(java.lang.String)">
    <div class="member-signature"><span class="return-type">void</span>
      <span class="element-name">run</span>
      <span class="parameters">(String value)</span>
      throws <span class="exceptions"><a href="WTException.html">WTException</a>,
      LocalException</span></div>
    <div class="block">Run once.<br><b>Supported API:</b> false</div>
  </section>
  <section class="detail" id="run()">
    <div class="member-signature"><span class="return-type">void</span>
      <span class="element-name">run</span><span class="parameters">()</span></div>
    <div class="deprecation-block"><span class="deprecated-label">Deprecated.</span></div>
  </section>
</section>
"""


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Supported API: true", True),
        ("Supported API: false", False),
        ("Supported\u00a0API :\nTRUE", True),
        ("supported api:false", False),
        ("Supported API: trueValue", None),
        ("Supported API: falsehood", None),
        ("NotSupported API: true", None),
        ("Supported API: true Supported API: false", None),
        ("No metadata", None),
    ],
)
def test_boolean_metadata(text, expected):
    assert parse_boolean_metadata(text, "Supported API") is expected


def test_class_metadata_and_deprecation_scope():
    metadata = parse_class_metadata(CLASS_HTML + METHOD_HTML, "wt.example.Example")
    assert isinstance(metadata, ApiClass)
    assert metadata.qualified_name == "wt.example.Example"
    assert metadata.class_name == "Example"
    assert metadata.package_name == "wt.example"
    assert metadata.supported is True
    assert metadata.extendable is False
    # Method 的 Deprecated 不应传播到 Class。
    assert metadata.deprecated is False
    assert "Example description." in metadata.description


def test_deprecated_class_without_description():
    html = CLASS_HTML.replace('class="block"', 'class="deprecation-block"')
    metadata = parse_class_metadata(html, "wt.example.Example")
    assert metadata.deprecated is True
    assert metadata.description == ""
    assert metadata.supported is None
    assert metadata.extendable is None


@pytest.mark.parametrize("name", ["wrong.Example", "wt.example.Wrong"])
def test_mismatched_class_identity(name):
    with pytest.raises(ValueError, match="不匹配"):
        parse_class_metadata(CLASS_HTML, name)


def test_nested_generic_class():
    html = CLASS_HTML.replace("Example", "Outer.Inner&lt;T&gt;")
    metadata = parse_class_metadata(html, "wt.example.Outer.Inner")
    assert metadata.class_name == "Outer.Inner"
    assert metadata.package_name == "wt.example"


def test_only_methods_and_all_overloads():
    methods = parse_methods(CLASS_HTML + METHOD_HTML)
    assert all(isinstance(method, ApiMethod) for method in methods)
    assert [method.javadoc_id for method in methods] == ["run(java.lang.String)", "run()"]
    assert methods == parse_methods(METHOD_HTML, "run")
    assert parse_methods(METHOD_HTML, "missing") == []
    first, second = methods
    assert first.return_type == "void"
    assert first.parameters == "(String value)"
    assert first.throws == ["WTException", "LocalException"]
    assert first.supported is False
    assert first.deprecated is False
    assert "Run once." in first.description
    assert second.supported is None
    assert second.deprecated is True
    assert second.throws == []


def test_method_without_id_is_not_indexable():
    with pytest.raises(ValueError, match="Javadoc ID"):
        parse_methods(METHOD_HTML.replace('id="run()"', ""))


def test_class_without_methods():
    assert parse_methods(CLASS_HTML) == []


@pytest.fixture
def sample_zip(tmp_path):
    path = tmp_path / "javadoc.zip"
    with ZipFile(path, "w") as archive:
        archive.writestr("Javadoc/wt/example/Example.html", CLASS_HTML + METHOD_HTML)
        archive.writestr("Javadoc/wt/example/Outer.Inner.html", "nested class")
    return str(path)


def test_read_top_level_and_nested_classes(sample_zip):
    assert read_class_html(sample_zip, "wt.example.Example") == CLASS_HTML + METHOD_HTML
    assert read_class_html(sample_zip, "wt.example.Outer.Inner") == "nested class"


def test_missing_class(sample_zip):
    with pytest.raises(ValueError, match="没有找到 Class"):
        read_class_html(sample_zip, "wt.example.Missing")


def test_missing_zip_and_directory(tmp_path):
    with pytest.raises(FileNotFoundError, match="ZIP 不存在"):
        read_class_html(str(tmp_path / "missing.zip"), "wt.example.Example")
    with pytest.raises(ValueError, match="不是文件"):
        read_class_html(str(tmp_path), "wt.example.Example")


@pytest.mark.parametrize("method", [None, "run"])
def test_cli_uses_dataclasses(sample_zip, monkeypatch, capsys, method):
    args = ["windchill-api-lookup", sample_zip, "wt.example.Example"]
    if method:
        args.append(method)
    monkeypatch.setattr("sys.argv", args)
    main()
    output = capsys.readouterr().out
    if method:
        assert "Overloads: 2" in output
        assert "WTException, LocalException" in output
        assert "run(java.lang.String)" in output
    else:
        assert "Package:    wt.example" in output
        assert "Supported:  True" in output
        assert "Deprecated: False" in output
