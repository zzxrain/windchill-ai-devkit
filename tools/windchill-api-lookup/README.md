# windchill-api-lookup

从本地 PTC Windchill Javadoc ZIP 构建版本独立的 SQLite 索引，查询类和方法。
当前解析布局及真实数据测试针对 **13.1.2.0**。其他版本需要实测，不根据文件名
推断版本，也不自动切换到其他已安装版本。

## 安装

Python 要求为 3.11+；当前本地验证环境是 Python 3.14。进入此目录执行：

```bash
python -m pip install -e '.[dev]'
windchill-api-lookup --help
```

正式安装可使用构建出的 wheel。程序依赖 BeautifulSoup 和 lxml，数据库使用
Python 标准库 sqlite3。索引数据不进入 Git。

## 扫描、导入与查询

默认数据根目录为 `~/.windchill-ai`，可以通过 `WINDCHILL_API_HOME` 或每个
子命令的 `--home` 指定。以下操作写入显式指定的数据目录：

```bash
# 扫描并输出每页处理结果；不创建索引。
windchill-api-lookup scan-javadoc --zip /path/to/WindchillJavadoc_13_1_2_0.zip --json

# 操作者显式确认文档版本。
windchill-api-lookup add-javadoc --version 13.1.2.0 \
  --zip /path/to/WindchillJavadoc_13_1_2_0.zip --home /path/to/data --json

windchill-api-lookup versions --home /path/to/data --json
windchill-api-lookup get-class --version 13.1.2.0 \
  wt.part.WTPart --home /path/to/data --json
windchill-api-lookup search-method --version 13.1.2.0 \
  wt.vc.wip.WorkInProgressService checkout --home /path/to/data --json
windchill-api-lookup get-method --version 13.1.2.0 \
  wt.vc.wip.WorkInProgressService \
  'checkout(wt.vc.wip.Workable,wt.folder.Folder,java.lang.String)' \
  --home /path/to/data --json
windchill-api-lookup index-report --version 13.1.2.0 --home /path/to/data --json
```

`search-method` 按精确方法名称返回全部重载；省略方法名时返回该类所有声明方法。
`get-method` 按原始 `javadoc_id` 精确查询。输出包含所属类的元数据、版本、
来源 ZIP 的 SHA-256、HTML 路径和方法锚点。方法参数与返回类型仍是展示文本，
尚未提供按完全限定参数类型列表匹配的接口。

所有新命令均输出 JSON；`--json` 使用紧凑格式，省略时使用缩进格式。
成功结果写 stdout，错误 JSON 写 stderr。查询失败不会产生成功结果。
原有 `<zip> <qualified-class> [method-name]` 文本查询保留兼容，但新集成应使用子命令。

## 数据与构建行为

```text
<data-home>/api-index/13.1.2.0/api.sqlite
```

schema v1 包含 `index_metadata`、`api_class`、`api_method` 三张表。
类以完整名称唯一，方法以 `(class_id, javadoc_id)` 唯一。`index_metadata`
保存版本、来源校验值、parser/schema 版本、构建时间、计数和完整逐页诊断。
字段和构造器暂不入库；枚举常量也不作为方法。注解成员作为方法记录。

构建一次打开 ZIP、每个类页面构造一次 DOM。所有 HTML 页面均计入报告：
辅助页明确跳过，未知候选结构、重复锚点或无法解析的候选页会导致整个构建失败。
无参方法允许签名中的裸 `()`；嵌套类路径使用 `Outer.Inner.html`。
索引类页按 UTF-8 严格解码，其他编码的 doc-files 附件不参与 API 解析。

- `supported` / `extendable` 在数据库中保存为 `1 / 0 / NULL`，JSON 中为
  `true / false / null`。缺失或非法元数据与冲突元数据在诊断中分别记录。
- 方法的 Supported 独立读取；调用方还需要检查所属类的 Supported。
- 方法查询只覆盖本页声明及注解成员，不展开继承方法。
- 相同来源和 parser 版本的重复导入复用已有索引。来源或 parser 版本不同时
  报冲突，使用 `--replace` 才允许重建。
- 重建使用同目录临时数据库、事务和完整性检查，全部通过才替换正式文件。
  失败或普通中断保留旧索引。构建前后校验 ZIP 未发生变化。
- 同版本构建使用排他锁。强制终止或断电可能留下 `api.build.lock` 与
  `.building-*.sqlite`；确认没有构建进程后才能清理这些遗留文件。
- 查询通过只读 SQLite 连接，不再读取 ZIP。schema 不兼容时要求重新构建；
  v1 不提供原地迁移。

## 错误契约

| 退出码 | code | 含义 |
| --- | --- | --- |
| 0 | — | 成功 |
| 2 | INVALID_ARGUMENT | 参数或版本格式错误 |
| 3 | NOT_FOUND | 已安装版本中未找到类或指定方法 |
| 4 | VERSION_NOT_INSTALLED | 没有该版本索引 |
| 5 | PARSE_FAILED | ZIP 或页面解析失败 |
| 6 | INDEX_UNAVAILABLE | 索引损坏、不兼容或读写失败 |
| 7 | INDEX_CONFLICT / BUILD_IN_PROGRESS / SOURCE_CHANGED | 来源冲突、已有构建或源文件改变 |

`versions` 会列出不可用索引并标记 `status: unavailable`，不静默隐藏它们。
完整的失败页报告可通过 `scan-javadoc` 取得；成功构建的报告通过 `index-report` 取得。

## 验证

```bash
python -m pytest -q
WINDCHILL_JAVADOC_ZIP=/path/to/WindchillJavadoc_13_1_2_0.zip python -m pytest -q
```

未设置 ZIP 时，真实集成测试跳过；合成 HTML、真实临时 SQLite、失败恢复、版本
隔离和 CLI 错误契约测试仍运行。设置 ZIP 后还会全量构建并验证典型类、嵌套类、
注解成员及 `checkout` 七个重载的数据库往返结果。该基线针对 13.1.2.0。

当前尚未实现继承方法展开、结构化 Java 类型解析和跨平台可执行文件打包。


## v0.3：只读 MCP

`serve` 使用官方 [MCP Python SDK v2](https://py.sdk.modelcontextprotocol.io/)
提供 stdio 服务；依赖范围为 `mcp>=2.2,<3`。CLI 与 MCP 共用 `Queries` 和
Repository，MCP 不访问 SQLite 底层或解析 Javadoc，也不导入或替换索引。
索引 parser 版本仍为 `0.2.0`，已有 schema v1 数据可以直接查询，无需重建。

```bash
windchill-api-lookup serve --home /path/to/data
```

服务启动后等待 MCP 请求；stdout 仅用于协议，不打印 CLI 成功 envelope。
程序日志写 stderr。退出客户端会关闭其启动的服务进程。

仅提供以下五个工具，均声明只读；数据根目录在进程启动时固定，工具参数中不含路径：

| Tool | 参数 | 语义 |
| --- | --- | --- |
| `list_versions` | 无 | 列出已有版本及不可用状态 |
| `get_class` | `version`, `qualified_name` | 完整类名精确查询 |
| `search_method` | `version`, `qualified_name`, 可选 `method_name` | 精确名称的全部重载；省略则返回本页方法 |
| `get_method` | `version`, `qualified_name`, `javadoc_id` | 原始锚点对应的具体重载 |
| `get_index_status` | `version` | 存储的构建状态、来源校验值、schema/parser 版本和统计 |

`get_index_status` 不执行实时完整性扫描，也不重新校验原始 ZIP；损坏或不兼容的
索引在读取失败时返回 `INDEX_UNAVAILABLE`。对应 CLI 命令是 `get-index-status`。

MCP 的 `structuredContent` 和文本 `content` 保存同一份 CLI JSON envelope：
成功为 `{"ok": true, ...}`，业务失败为 `{"ok": false, "error": {"code": ..., "message": ..., "details": ...}}`。
业务失败同时设置 MCP `isError: true`。参数缺失、类型不符合工具 schema 或未知工具
由 SDK 按 MCP 协议处理。`get_method` 继续使用单项 `methods` 数组，保持与 CLI 一致。

## Qoder 插件配置

仓库根目录的 `mcp.json` 已配置 `windchill-api-lookup serve`，插件清单通过
`"mcpServers": "./mcp.json"` 引用它。配置格式依据
[Qoder CN 官方插件文档](https://docs.qoder.cn/qoder-plugins)。

先在准备使用的 Python 环境安装 v0.3，然后通过 CLI 导入 Javadoc。默认数据根目录
是 `~/.windchill-ai`；此前 `/tmp` 下的验证索引不是自动安装到该目录的正式索引。

GUI 启动的 Qoder 不一定能找到已激活虚拟环境中的命令。如果提示找不到程序，
将已安装插件配置中的 `command` 改成该虚拟环境内可执行文件的绝对路径，例如：

```json
{
  "mcpServers": {
    "windchill-api-lookup": {
      "command": "/absolute/path/to/venv/bin/windchill-api-lookup",
      "args": ["serve"],
      "env": {
        "WINDCHILL_API_HOME": "/absolute/path/to/data"
      }
    }
  }
}
```

`WINDCHILL_API_HOME` 指向包含 `api-index` 的数据根目录，不指向 ZIP 或单个数据库。
Javadoc 位置仅通过 `add-javadoc --zip` 指定，MCP 配置无需保存它。
每次查询显式传入项目的 Windchill 版本，缺失时不自动跨版本回退。

将更新后的插件安装到 Qoder 并重新加载后，应能发现恰好五个工具。首次验收查询
`WTPart`、`checkout` 重载、不存在的类和未安装版本。仓库源码修改不会自动更新
客户端已安装的插件副本。协议测试覆盖现代及 legacy 握手，真实 Qoder UI 连接仍需在客户端验证。
