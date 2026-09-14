# windchill-api-lookup

从本地 PTC Windchill Javadoc ZIP 查询类元数据和方法重载。当前解析器针对
13.1.2.0 的 HTML 结构，ZIP 内路径为 `Javadoc/<package>/<Class>.html`。
嵌套类使用 `Outer.Inner.html`。其他版本需用实际 Javadoc 验证。

在此目录安装、运行：

```bash
python -m pip install -e '.[dev]'
windchill-api-lookup /path/to/WindchillJavadoc_13_1_2_0.zip wt.part.WTPart
windchill-api-lookup /path/to/WindchillJavadoc_13_1_2_0.zip wt.vc.wip.WorkInProgressService checkout
```

Python 接口：

```python
from windchill_api_lookup.parser.ptc_javadoc import (
    read_class_html, parse_class_metadata, parse_methods,
)

html = read_class_html(zip_path, "wt.part.WTPart")
metadata = parse_class_metadata(html, "wt.part.WTPart")  # ApiClass
methods = parse_methods(html, "getNumber")             # list[ApiMethod]
print(metadata.supported)
```

`supported` / `extendable` 保留 `True`、`False`、`None` 三态；缺失或冲突为
`None`。方法的 Supported 独立读取，调用方还需检查所属类的状态。
方法查询只返回本页 Method Details，不展开继承的方法；找不到名称时返回空列表。
`javadoc_id` 保留原始重载锚点，`signature`、`parameters` 为展示文本。

测试：

```bash
python -m pytest -q
WINDCHILL_JAVADOC_ZIP=/path/to/WindchillJavadoc_13_1_2_0.zip python -m pytest -q
```

未设置 ZIP 时只运行合成 HTML 单元测试，真实 Javadoc 集成测试会跳过。
集成测试中的 `checkout` 七个重载基线针对 13.1.2.0。
