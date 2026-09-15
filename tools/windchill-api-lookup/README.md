# windchill-api-lookup

从本地 PTC Windchill Javadoc ZIP 构建版本隔离的 SQLite 索引，并向 CLI / MCP 提供精确的 Class 和 Method 查询。

当前解析布局及真实数据测试基线针对 **Windchill 13.1.2.0**。

其他 Windchill 版本可以作为独立 Source 建立索引，但其 Javadoc HTML Layout 是否兼容当前 Parser 仍需要真实测试。

工具：

- 不从 Javadoc ZIP 文件名推断 Windchill Version
- 不自动切换到其他已安装版本
- 不进行跨版本 fallback
- 不要求 Javadoc ZIP 文件名包含版本号

---

## 1. 安装

Python 要求：

```text
Python >= 3.11
```

进入本目录：

```bash
python -m pip install -e '.[dev]'
windchill-api-lookup --help
```

正式安装可使用构建出的 wheel。

依赖：

- BeautifulSoup
- lxml
- MCP Python SDK
- Python 标准库 sqlite3

索引数据不进入 Git。

---

## 2. Project Javadoc 工作方式

v0.4 推荐由 Windchill Project Context 提供：

```text
Windchill Version
+
一个 Javadoc ZIP 路径
```

例如项目 `AGENTS.md`：

```markdown
- Windchill Version: `13.1.2.0`

### PTC Javadoc

- Javadoc ZIP: `.windchill-ai/javadoc/WindchillJavadoc.zip`
```

或者未来版本：

```markdown
- Windchill Version: `2027`

### PTC Javadoc

- Javadoc ZIP: `.windchill-ai/javadoc/WindchillJavadoc.zip`
```

版本来自 Project Context。

**版本不得从 ZIP 文件名推断。**

因此：

```text
WindchillJavadoc.zip
ptc-javadoc.zip
WindchillJavadoc_13_1_2_0.zip
```

都可以作为 Source。

推荐项目目录：

```text
customer-project/
├── AGENTS.md
├── src/
└── .windchill-ai/
    └── javadoc/
        └── WindchillJavadoc.zip
```

项目 `.gitignore` 应包含：

```gitignore
.windchill-ai/
```

PTC Javadoc 不应提交到客户项目源码 Repository。

---

## 3. 自动索引

MCP 提供：

```text
ensure_javadoc_index
```

参数：

```text
version
zip_path
```

其中：

- `version` 来自项目 `AGENTS.md`
- `zip_path` 必须是本地绝对路径

如果 `AGENTS.md` 使用项目相对路径：

```text
.windchill-ai/javadoc/WindchillJavadoc.zip
```

AI Agent 应先根据项目根目录解析为绝对路径，再调用 MCP。

例如：

```text
/Users/user/work/customer-project/.windchill-ai/javadoc/WindchillJavadoc.zip
```

第一次调用：

```text
ensure_javadoc_index
        ↓
读取 ZIP
        ↓
全量解析
        ↓
建立 SQLite
        ↓
READY
```

后续使用相同：

```text
version
+
source SHA-256
+
parser version
```

时直接复用已有索引。

---

## 4. 本地索引位置

默认数据根目录：

```text
~/.windchill-ai
```

可通过：

```text
WINDCHILL_API_HOME
```

修改。

索引按 Windchill Version 隔离：

```text
~/.windchill-ai/
└── api-index/
    ├── 13.1.2.0/
    │   └── api.sqlite
    └── 2027/
        └── api.sqlite
```

一个项目通常只使用一个 Windchill Version。

本机可以因为不同项目而同时存在多个版本的本地 Index。

查询必须显式使用当前项目 Version。

---

## 5. Version 规则

当前支持安全的数字 Release Identifier，例如：

```text
13.0
13.0.2.0
13.1.2.0
2027
2027.1
2027.1.0
```

版本是 Project Context 声明值。

工具不会根据：

- ZIP 文件名
- 已有 Index
- Model Knowledge

推断版本。

以下值会被拒绝：

```text
../13.1
/tmp/data
13.x
Windchill 2027
```

这样可以防止版本值被用于逃逸本地 Index Root。

---

## 6. Source 冲突

如果当前版本已经存在 Index：

```text
13.1.2.0
```

并且再次提供同一个 ZIP：

```text
SHA-256 unchanged
```

则返回：

```text
reused: true
```

不会重新构建。

如果同一 Version 提供了不同 ZIP：

```text
old SHA != new SHA
```

则返回：

```text
INDEX_CONFLICT
```

不会自动覆盖。

如确认需要替换，可以由开发人员显式执行：

```bash
windchill-api-lookup add-javadoc \
  --version 13.1.2.0 \
  --zip /path/to/new/WindchillJavadoc.zip \
  --replace
```

自动 Agent Workflow 不应静默执行 Source Replacement。

---

## 7. 手工扫描、导入与查询

自动索引是推荐 Agent Workflow。

CLI 仍保留人工诊断和管理能力。

### Scan

```bash
windchill-api-lookup scan-javadoc \
  --zip /path/to/WindchillJavadoc.zip \
  --json
```

扫描不会创建索引。

### Manual Import

```bash
windchill-api-lookup add-javadoc \
  --version 13.1.2.0 \
  --zip /path/to/WindchillJavadoc.zip \
  --home /path/to/data \
  --json
```

### Versions

```bash
windchill-api-lookup versions \
  --home /path/to/data \
  --json
```

### Class

```bash
windchill-api-lookup get-class \
  --version 13.1.2.0 \
  wt.part.WTPart \
  --home /path/to/data \
  --json
```

### Method

```bash
windchill-api-lookup search-method \
  --version 13.1.2.0 \
  wt.vc.wip.WorkInProgressService \
  checkout \
  --home /path/to/data \
  --json
```

### Exact Overload

```bash
windchill-api-lookup get-method \
  --version 13.1.2.0 \
  wt.vc.wip.WorkInProgressService \
  'checkout(wt.vc.wip.Workable,wt.folder.Folder,java.lang.String)' \
  --home /path/to/data \
  --json
```

### Index Report

```bash
windchill-api-lookup index-report \
  --version 13.1.2.0 \
  --home /path/to/data \
  --json
```

---

## 8. Query 语义

`search-method`：

- 按精确方法名称查询
- 返回全部重载
- 省略方法名时返回该类当前页面声明的方法

`get-method`：

- 使用原始 `javadoc_id`
- 精确查询某个重载

当前尚未提供：

- 完全限定参数类型结构化匹配
- 继承方法展开
- Fields
- Constructors

输出包含：

- Class Metadata
- Method Metadata
- Windchill Version
- Source ZIP SHA-256
- HTML Source Path
- Method Anchor

---

## 9. 数据与构建行为

每个版本独立：

```text
<data-home>/api-index/<version>/api.sqlite
```

schema v1 包含：

```text
index_metadata
api_class
api_method
```

类以完整名称唯一。

方法以：

```text
(class_id, javadoc_id)
```

唯一。

`index_metadata` 保存：

- Windchill Version
- Source SHA-256
- Parser Version
- Schema Version
- Build Time
- Class Count
- Method Count
- Full Scan Diagnostics

字段和构造器暂不入库。

枚举常量不作为方法。

注解成员作为方法记录。

---

## 10. Index 构建安全

构建行为：

1. 打开 Source ZIP
2. 计算 Source SHA-256
3. 创建临时 SQLite
4. 全量解析
5. 写入 Metadata
6. 执行 SQLite Integrity Check
7. 再次检查 Source SHA-256
8. 关闭 SQLite
9. 原子替换正式 Index

如果失败：

- 不发布半成品 Index
- 已有工作 Index 保留
- 临时数据库清理

同版本使用排他 Build Lock。

可能出现：

```text
api.build.lock
.building-*.sqlite
```

强制终止或断电可能留下这些文件。

确认没有运行中的 Build Process 后才能人工清理。

---

## 11. Metadata

`supported` / `extendable`：

```text
1
0
NULL
```

JSON：

```text
true
false
null
```

`null` 表示 Javadoc 中无法可靠确认。

方法的 Supported 状态独立于 Class。

使用方法时仍应同时检查所属 Class 的 Supported 状态。

---

## 12. Parser 边界

当前真实 Parser Baseline：

```text
Windchill 13.1.2.0
```

当前 Parser 对 Javadoc HTML Layout 有结构假设。

因此：

> 支持新的 Windchill Version Identifier

不等于：

> 已经证明所有历史或未来 Javadoc HTML Layout 都兼容。

未知 Layout 会：

```text
PARSE_FAILED
```

而不是静默生成不完整 Index。

后续应使用实际版本 Javadoc 对 Parser 进行兼容性验证。

---

## 13. 错误契约

| 退出码 | code | 含义 |
|---|---|---|
| 0 | — | 成功 |
| 2 | INVALID_ARGUMENT | 参数、版本或路径错误 |
| 3 | NOT_FOUND | 未找到 Class / Method |
| 4 | VERSION_NOT_INSTALLED | 没有该版本 Index |
| 5 | PARSE_FAILED | ZIP 或 Javadoc 页面解析失败 |
| 6 | INDEX_UNAVAILABLE | Index 损坏、不兼容或读写失败 |
| 7 | INDEX_CONFLICT | 同版本存在不同 Source / Parser Index |
| 7 | BUILD_IN_PROGRESS | 已有同版本构建 |
| 7 | SOURCE_CHANGED | Build 期间 Source ZIP 变化 |

`versions` 会列出不可用 Index：

```text
status: unavailable
```

不会静默隐藏。

---

## 14. MCP

启动：

```bash
windchill-api-lookup serve
```

或：

```bash
windchill-api-lookup serve \
  --home /path/to/data
```

MCP 使用 stdio。

stdout 只用于 MCP Protocol。

日志写 stderr。

CLI 与 MCP 共用 Repository / Query Layer。

---

## 15. MCP Tools

v0.4 提供六个 Tool。

| Tool | Mutation | Purpose |
|---|---|---|
| `ensure_javadoc_index` | Local cache write | 建立或复用项目 Javadoc Index |
| `list_versions` | Read-only | 列出已有版本 |
| `get_class` | Read-only | 精确 Class 查询 |
| `search_method` | Read-only | Method / Overload 查询 |
| `get_method` | Read-only | 精确重载查询 |
| `get_index_status` | Read-only | 查看 Index Metadata |

`ensure_javadoc_index` 只修改：

```text
WINDCHILL_API_HOME
```

下的派生 Index。

它不会修改：

- Project Source
- AGENTS.md
- Javadoc ZIP

---

## 16. Qoder 推荐 Workflow

项目：

```text
AGENTS.md
```

声明：

```text
Windchill Version
Javadoc ZIP
```

当 Agent 需要精确 PTC API：

```text
Read AGENTS.md
        ↓
Version = project Windchill Version
        ↓
Javadoc = configured ZIP
        ↓
Resolve Javadoc path to absolute path
        ↓
ensure_javadoc_index
        ↓
get_class / search_method / get_method
```

如果 Index 已存在：

```text
ensure
↓
reused: true
```

开销很小。

如果首次使用：

```text
ensure
↓
Build
↓
reused: false
```

之后查询只访问 SQLite。

---

## 17. Qoder Plugin 配置

仓库根目录：

```text
mcp.json
```

配置：

```json
{
  "mcpServers": {
    "windchill-api-lookup": {
      "command": "windchill-api-lookup",
      "args": ["serve"]
    }
  }
}
```

Qoder GUI 不一定继承用户 Shell 的 Virtual Environment PATH。

如果提示找不到命令，应将已安装插件中的 `command` 改为实际 executable 的绝对路径，例如：

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

`WINDCHILL_API_HOME` 指向数据根目录。

它不指向：

- ZIP
- 单个 SQLite

Javadoc ZIP 由 Project Context 提供。

---

## 18. 验证

执行：

```bash
python -m pytest -q
```

真实 Javadoc Integration Test：

```bash
WINDCHILL_JAVADOC_ZIP=/path/to/WindchillJavadoc_13_1_2_0.zip \
python -m pytest -q
```

未设置真实 ZIP 时：

- Synthetic HTML Test 执行
- SQLite Test 执行
- MCP Test 执行
- Failure Recovery Test 执行
- Version Isolation Test 执行

真实 ZIP 测试跳过。

---

## 19. 当前未实现

当前尚未实现：

- 继承方法展开
- Structured Java Type Parsing
- Fields
- Constructors
- 多种 Javadoc Layout Profile
- Standalone Executable Packaging

这些能力应根据真实项目需求逐步增加。

当前优先保证：

```text
Project Javadoc
+
Automatic Local Index
+
Exact Version Isolation
+
Exact API Query
```