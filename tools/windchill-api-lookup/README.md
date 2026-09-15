# windchill-api-lookup

从本地 PTC Windchill Javadoc ZIP 构建版本隔离的 SQLite 索引，并向 CLI / MCP 提供精确的 Class 和 Method 查询。

当前真实 Parser Baseline：

```text
Windchill 13.1.2.0
```

真实全量索引验证：

```text
HTML Pages:     8137
Classes:        6118
Methods:        23804
Failed Pages:   0
Schema Version: 1
Parser Version: 0.2.0
```

其他 Windchill 版本可以作为独立 Source 建立索引，但其 Javadoc HTML Layout 是否兼容当前 Parser 仍需要使用真实 Javadoc 验证。

工具遵循以下原则：

- 不从 Javadoc ZIP 文件名推断 Windchill Version
- 不自动切换到其他已安装版本
- 不进行跨版本 fallback
- 不要求 Javadoc ZIP 文件名包含版本号
- 一个项目通常只配置一个目标版本和一个 Javadoc ZIP

---

## 1. Python Environment

Python 要求：

```text
Python >= 3.11
```

开发环境推荐使用独立 Virtual Environment。

macOS 示例：

```bash
python3 -m venv ~/.venvs/windchill-api-lookup
source ~/.venvs/windchill-api-lookup/bin/activate
```

安装开发版本：

```bash
cd tools/windchill-api-lookup

python -m pip install -e '.[dev]'
```

运行：

```bash
windchill-api-lookup --help
```

Python Virtual Environment 与 API Index 数据是两个不同概念：

```text
~/.venvs/windchill-api-lookup
    → Python Runtime / Dependencies / Executable

~/.windchill-ai
    → Javadoc API Index Data
```

Virtual Environment 属于可重建运行环境，不应提交 Git。

---

## 2. Project Javadoc 工作方式

Windchill Project Context 提供：

```text
Windchill Version
+
一个 Javadoc ZIP 路径
```

例如：

```markdown
- Windchill Version: `13.1.2.0`

### PTC Javadoc

- Javadoc ZIP: `.windchill-ai/javadoc/WindchillJavadoc.zip`
```

未来版本例如：

```markdown
- Windchill Version: `2027.0.0.0`

### PTC Javadoc

- Javadoc ZIP: `.windchill-ai/javadoc/WindchillJavadoc.zip`
```

版本来自 Project Context。

**版本不得从 ZIP 文件名推断。**

以下文件名都可以作为 Source：

```text
WindchillJavadoc.zip
ptc-javadoc.zip
WindchillJavadoc_13_1_2_0.zip
```

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

如果 `AGENTS.md` 使用：

```text
.windchill-ai/javadoc/WindchillJavadoc.zip
```

AI Agent 应先根据项目根目录解析为绝对路径，再调用 MCP。

首次使用：

```text
ensure_javadoc_index
        ↓
Source SHA-256
        ↓
Javadoc Scan
        ↓
SQLite Build
        ↓
Integrity Check
        ↓
Atomic Publish
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

时直接复用已有 Index。

---

## 4. 本地索引位置

默认数据根目录：

```text
~/.windchill-ai
```

可以通过：

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
    ├── 2027.0.0.0/
    │   └── api.sqlite
    └── 2027.1.0.0/
        └── api.sqlite
```

一个项目通常只使用一个 Windchill Version。

同一开发机可以因为不同项目同时存在多个 Version Index。

查询必须显式使用当前项目 Version。

---

## 5. Version 规则

Windchill Version 被视为 Project Context 提供的 Release Identifier。

当前允许：

```text
1～4 段纯数字
```

例如：

```text
13
13.1
13.1.2
13.1.2.0

2027
2027.0
2027.0.0
2027.0.0.0
2027.1.0.0
```

实际项目应尽量填写完整版本，例如：

```text
13.1.2.0
2027.0.0.0
```

工具不会根据以下内容推断版本：

- ZIP 文件名
- 已有 Index
- Model Knowledge
- Golden Reference
- 其他项目

以下值会被拒绝：

```text
../13.1
/tmp/data
13.x
13.1.2.0.1
2027-R1
Windchill 2027
```

---

## 6. CLI Index Progress

真实 Windchill Javadoc 可能包含数千个 HTML 页面。

首次建立 Index 可能需要一定时间。

普通交互式终端执行：

```bash
windchill-api-lookup add-javadoc \
  --version 13.1.2.0 \
  --zip ~/Downloads/WindchillJavadoc_13_1_2_0.zip
```

会显示类似：

```text
[windchill-api-lookup] Calculating Javadoc source checksum...
[windchill-api-lookup] Discovering Javadoc HTML pages...
[windchill-api-lookup] Indexing Javadoc: 250/8137 HTML pages (3.1%)
[windchill-api-lookup] Indexing Javadoc: 500/8137 HTML pages (6.1%)
...
[windchill-api-lookup] Validating index and source checksum...
[windchill-api-lookup] Publishing local API index...
[windchill-api-lookup] Javadoc API index build complete.
```

Progress 输出到：

```text
stderr
```

最终 JSON 仍输出到：

```text
stdout
```

使用：

```text
--json
```

时不会输出 Progress，以保持机器调用结果稳定。

非交互式 TTY 场景同样不会输出 Human Progress。

---

## 7. Source 冲突

如果当前版本已经存在 Index，并且再次提供同一 Source ZIP：

```text
SHA-256 unchanged
```

返回：

```text
reused: true
```

不会重新构建。

如果同一 Version 提供不同 ZIP：

```text
old SHA != new SHA
```

返回：

```text
INDEX_CONFLICT
```

不会自动覆盖。

如果确认需要替换，由开发人员显式执行：

```bash
windchill-api-lookup add-javadoc \
  --version 13.1.2.0 \
  --zip /path/to/new/WindchillJavadoc.zip \
  --replace
```

Agent 自动 Workflow 不应静默执行 Source Replacement。

---

## 8. 手工扫描、导入与查询

自动索引是推荐 Agent Workflow。

CLI 保留人工诊断和管理能力。

### Scan

```bash
windchill-api-lookup scan-javadoc \
  --zip /path/to/WindchillJavadoc.zip \
  --json
```

扫描不会创建正式 Index。

### Manual Import

```bash
windchill-api-lookup add-javadoc \
  --version 13.1.2.0 \
  --zip /path/to/WindchillJavadoc.zip
```

指定 Data Home：

```bash
windchill-api-lookup add-javadoc \
  --version 13.1.2.0 \
  --zip /path/to/WindchillJavadoc.zip \
  --home /path/to/data
```

### Versions

```bash
windchill-api-lookup versions
```

### Class

```bash
windchill-api-lookup get-class \
  --version 13.1.2.0 \
  wt.part.WTPart
```

### Method

```bash
windchill-api-lookup search-method \
  --version 13.1.2.0 \
  wt.vc.wip.WorkInProgressService \
  checkout
```

### Exact Overload

```bash
windchill-api-lookup get-method \
  --version 13.1.2.0 \
  wt.vc.wip.WorkInProgressService \
  'checkout(wt.vc.wip.Workable,wt.folder.Folder,java.lang.String)'
```

### Index Status

```bash
windchill-api-lookup get-index-status \
  --version 13.1.2.0
```

### Index Report

```bash
windchill-api-lookup index-report \
  --version 13.1.2.0
```

---

## 9. Query 语义

`search-method`：

- 按精确 Method Name 查询
- 返回全部 Overload
- 省略 Method Name 时返回该页面声明的方法

`get-method`：

- 使用原始 `javadoc_id`
- 精确查询某个 Overload

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

## 10. 数据模型

每个版本独立：

```text
<data-home>/api-index/<version>/api.sqlite
```

schema v1：

```text
index_metadata
api_class
api_method
```

Class 以完整名称唯一。

Method 以：

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

Fields 和 Constructors 暂不入库。

Enum Constants 不作为 Method。

Annotation Members 作为 Method 记录。

---

## 11. Index 构建安全

构建过程：

```text
Source ZIP
    ↓
SHA-256
    ↓
Temporary SQLite
    ↓
Full Parse
    ↓
Metadata
    ↓
SQLite Integrity Check
    ↓
Source SHA-256 Recheck
    ↓
Close SQLite
    ↓
Atomic Replace
```

如果构建失败：

- 不发布半成品 Index
- 已有有效 Index 保留
- 临时数据库清理

同版本使用排他 Build Lock。

可能出现：

```text
api.build.lock
.building-*.sqlite
```

强制终止或断电可能留下相关文件。

确认没有运行中的 Build Process 后才能人工清理。

---

## 12. Metadata

`supported` / `extendable` 在 SQLite：

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

`null` 表示当前 Javadoc 无法可靠确认。

Method Supported 独立于 Class。

使用 Method 时仍应同时检查所属 Class 的 Supported 状态。

---

## 13. Parser 边界

当前真实 Parser Baseline：

```text
Windchill 13.1.2.0
```

当前真实全量测试：

```text
8137 HTML pages
6118 parsed classes
23804 methods
0 failed pages
```

当前 Parser 对 PTC Javadoc HTML Layout 有结构假设。

因此：

> Version Identifier 被接受

不等于：

> 该版本 Javadoc Layout 已经验证兼容。

例如：

```text
2027.0.0.0
```

作为 Version Identifier 已受支持。

但在取得真实 `2027.0.0.0` Javadoc 并执行全量测试以前，不应声称其 Javadoc Layout 已经 VERIFIED。

未知 Layout 会：

```text
PARSE_FAILED
```

而不是静默生成不完整 Index。

---

## 14. 错误契约

| 退出码 | code | 含义 |
|---|---|---|
| 0 | — | 成功 |
| 2 | INVALID_ARGUMENT | 参数、版本或路径错误 |
| 3 | NOT_FOUND | 未找到 Class / Method |
| 4 | VERSION_NOT_INSTALLED | 没有该版本 Index |
| 5 | PARSE_FAILED | ZIP 或 Javadoc 页面解析失败 |
| 6 | INDEX_UNAVAILABLE | Index 损坏、不兼容或读写失败 |
| 7 | INDEX_CONFLICT | 同版本存在不同 Source / Parser Index |
| 7 | BUILD_IN_PROGRESS | 已有同版本 Build |
| 7 | SOURCE_CHANGED | Build 期间 Source ZIP 变化 |

`versions` 会列出不可用 Index：

```text
status: unavailable
```

不会静默隐藏。

---

## 15. MCP

启动：

```bash
windchill-api-lookup serve
```

或者：

```bash
windchill-api-lookup serve \
  --home /path/to/data
```

MCP 使用：

```text
stdio
```

stdout 仅用于 MCP Protocol。

程序日志应写 stderr。

CLI 与 MCP 共用：

```text
Repository
Queries
Indexer
```

---

## 16. MCP Tools

v0.4 提供六个 Tool：

| Tool | Mutation | Purpose |
|---|---|---|
| `ensure_javadoc_index` | Local cache write | 建立或复用项目 Javadoc Index |
| `list_versions` | Read-only | 列出已有版本 |
| `get_class` | Read-only | 精确 Class 查询 |
| `search_method` | Read-only | Method / Overload 查询 |
| `get_method` | Read-only | 精确 Overload 查询 |
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

当前 `ensure_javadoc_index` 仍为同步构建。

首次真实 Javadoc Build 的 MCP 调用耗时需要在 Qoder 客户端继续验证。

如果后续证明存在客户端 Timeout，再考虑：

- MCP Progress Notification
- Background Build Job
- Polling Status

当前阶段不提前增加异步复杂度。

---

## 17. Qoder 推荐 Workflow

项目 `AGENTS.md` 声明：

```text
Windchill Version
Javadoc ZIP
```

Agent 需要精确 PTC API 时：

```text
Read AGENTS.md
        ↓
Version = Project Windchill Version
        ↓
Javadoc = Configured ZIP
        ↓
Resolve ZIP to Absolute Path
        ↓
ensure_javadoc_index
        ↓
get_class / search_method / get_method
```

已有相同 Index：

```text
ensure
↓
reused: true
```

首次使用：

```text
ensure
↓
Build
↓
reused: false
```

后续 Query 只访问 SQLite。

---

## 18. Qoder Plugin 配置

仓库根目录：

```text
mcp.json
```

典型配置：

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

Qoder GUI 不一定继承用户 Shell PATH。

开发阶段如果 Qoder 找不到命令，可以使用 Virtual Environment 中 executable 的绝对路径：

```text
~/.venvs/windchill-api-lookup/bin/windchill-api-lookup
```

例如实际展开后：

```text
/Users/<user>/.venvs/windchill-api-lookup/bin/windchill-api-lookup
```

不要在共享 Repository 中硬编码某个开发人员的 Home 路径。

`WINDCHILL_API_HOME` 指向：

```text
API Index Data Root
```

例如：

```text
~/.windchill-ai
```

它不指向：

- Python venv
- Javadoc ZIP
- 单个 SQLite

---

## 19. 验证

普通 Unit / Integration Test：

```bash
python -m pytest -q
```

使用真实 13.1.2.0 Javadoc：

```bash
WINDCHILL_JAVADOC_ZIP=~/Downloads/WindchillJavadoc_13_1_2_0.zip \
python -m pytest -q
```

未配置真实 Javadoc 时：

- Synthetic HTML Test 执行
- SQLite Test 执行
- MCP Test 执行
- Failure Recovery Test 执行
- Version Isolation Test 执行

真实 Javadoc Test 跳过。

---

## 20. 当前未实现

当前暂不实现：

- Inherited Method Expansion
- Structured Java Type Parsing
- Fields
- Constructors
- Multi-layout Parser Profiles
- Standalone Executable Packaging
- Background MCP Index Build

当前优先保证：

```text
Project Javadoc
+
Automatic Local Index
+
Exact Version Isolation
+
Exact API Query
+
Observable First-time Build
```