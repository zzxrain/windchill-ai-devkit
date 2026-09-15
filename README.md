# Windchill AI DevKit

Windchill AI DevKit 是面向公司内部 PTC Windchill 二次开发的 Qoder Plugin。

本项目通过企业开发规则、Windchill / XWorks 企业知识、PTC Javadoc API 精确查询、项目级上下文，以及后续接入的 Golden Reference，为 AI Coding Agent 提供受控的 Windchill 二次开发能力。

目标不是让 AI “记住所有 Windchill 知识”，而是建立一套可验证、可维护、可迭代的 Windchill AI Coding Harness。

---

## 1. Goals

本项目主要用于：

- 降低 AI 编造 Windchill / PTC API 的概率
- 约束 AI 遵循企业 Windchill 开发规范
- 避免直接复制历史项目中的低质量实现
- 根据目标 Windchill 版本验证精确 API
- 根据项目实际情况决定是否使用 XWorks
- 区分企业通用规则和客户项目特殊要求
- 明确 DEV / TEST / UAT / PROD 配置边界
- 区分“代码已生成”和“Windchill Runtime 已验证”
- 逐步沉淀企业批准的 Golden Reference
- 为公司持续积累 Windchill AI 开发资产提供统一入口

---

## 2. Architecture

```text
                       Windchill Project
                             │
                             ▼
                         AGENTS.md
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
        Rules              QMind        Golden Reference
          │                  │             (planned)
          └──────────────────┼──────────────────┘
                             │
                             ▼
                  Windchill API Lookup
                             │
                             ▼
                       AI Coding Agent
                             │
                             ▼
                   Build / Test / Review
                             │
                             ▼
                Windchill Runtime Verification
```

各组件职责：

| Component | Responsibility |
|---|---|
| Rules | 定义 AI 必须 / 不得如何开发 |
| QMind Router | 获取 Windchill / XWorks 企业知识 |
| Golden Reference | 提供企业审核通过的推荐实现 |
| API Lookup | 精确验证 PTC Java API |
| AGENTS.md | 描述当前客户项目事实和项目例外 |
| Project Code | 提供当前架构、调用关系和兼容性上下文 |
| Build / Test | 验证代码级结果 |
| Runtime Verification | 验证真实 Windchill Runtime 行为 |

这些能力不能互相替代。

---

## 3. Core Concepts

### Rules

Rules 回答：

> AI Agent 在 Windchill 项目中必须 / 不得怎么开发？

Rules 用于约束高价值、高风险的开发边界，不用于承载全部 Windchill 产品知识。

### QMind

QMind 回答：

> Windchill / XWorks 本身如何工作？

主要用于获取：

- Windchill Customization 知识
- XWorks 实施知识
- 安装部署和升级知识
- 数据迁移知识
- MPMLink / ProjectLink 等模块知识

### Golden Reference

Golden Reference 回答：

> 企业批准的同类实现通常怎么写？

Golden Reference 是经过审核的推荐代码样例，不等同于历史项目代码，也不替代 PTC API 验证。

### API Lookup

API Lookup 回答：

> 当前 Windchill 版本中，这个 PTC Class / Method 是否真实存在？

主要用于确认：

- Class
- Method
- Signature
- Supported
- Extendable
- Deprecated
- Return / Parameter / Throws 等 Javadoc 事实

### Project Context

项目根目录 `AGENTS.md` 回答：

> 当前客户项目实际是什么环境和架构？

例如：

- Windchill Version
- Java Version
- PTC Javadoc ZIP
- XWorks Enabled
- Build Command
- Environment Topology
- Approved Project Exception
- Compatibility Constraint

---

## 4. Authority Model

### Development Decision

判断“代码应该如何实现”时，默认优先级：

1. 企业强制安全、合规、架构要求
2. 已批准项目例外 / ADR / 客户明确要求
3. Windchill AI DevKit Rules
4. 企业批准 Golden Reference
5. 当前项目已有实现
6. 模型自身知识

当前项目代码属于兼容性证据，不自动等同于正确规范。

### Product Facts

判断以下事实时：

- PTC Class 是否存在
- Method Signature
- Supported / Extendable
- Deprecated
- Property
- Extension Point
- WRS / OData 能力
- Windchill 产品行为

应优先依据：

1. 目标版本 PTC Javadoc / 官方资料
2. 企业审核 QMind
3. 与目标版本匹配的 Golden Reference
4. 当前项目已经验证的实现
5. 模型知识

不得根据命名规律猜测 PTC API。

---

## 5. Repository Structure

当前主要结构：

```text
windchill-ai-devkit/
├── .qoder-plugin/
│   └── plugin.json
│
├── rules/
│   ├── 00-core-development-rules.md
│   ├── 10-java.md
│   ├── 20-windchill-api.md
│   ├── 30-persistence-query-transaction.md
│   ├── 35-versioning-object-semantics.md
│   ├── 40-access-control-security-context.md
│   ├── 50-service-event-queue.md
│   ├── 60-configuration-customization-files.md
│   ├── 70-ui-web-extension.md
│   ├── 80-logging-diagnostics.md
│   └── 85-xworks-framework.md
│
├── skills/
│   └── qmind-enterprise-router/
│       ├── SKILL.md
│       └── references/
│           └── qmind-registry.md
│
├── tools/
│   └── windchill-api-lookup/
│
├── templates/
│   └── AGENTS.md
│
├── mcp.json
├── .gitignore
└── README.md
```

后续 Golden Reference 接入后，计划增加：

```text
skills/
└── windchill-golden-reference/
    ├── SKILL.md
    ├── CATALOG.md
    └── references/
```

推荐该目录由独立私有 Git Repository 通过 Git Submodule 提供。

---

## 6. Rules

当前核心 Rules：

| Rule | Scope |
|---|---|
| `00-core-development-rules.md` | 全局基础规则 |
| `10-java.md` | Java 工程边界 |
| `20-windchill-api.md` | PTC API 使用和验证 |
| `30-persistence-query-transaction.md` | Persistence / Query / Transaction |
| `35-versioning-object-semantics.md` | Version / Iteration / Working Copy |
| `40-access-control-security-context.md` | Access Control / Principal / Security Context |
| `50-service-event-queue.md` | Service / Event / Listener / Queue |
| `60-configuration-customization-files.md` | XCONF / Configuration / Environment |
| `70-ui-web-extension.md` | JCA / MVC / UI Extension |
| `80-logging-diagnostics.md` | Logging / Diagnostics |
| `85-xworks-framework.md` | Optional XWorks Framework |

`00` 为基础规则，其余 Rule 根据任务按需应用。

---

## 7. Project AGENTS.md

每个 Windchill 项目建议在项目根目录维护：

```text
AGENTS.md
```

模板位于：

```text
templates/AGENTS.md
```

复制模板后，至少应填写：

- Windchill Version
- Java Version
- PTC Javadoc ZIP
- XWorks Enabled
- XWorks Version
- Custom Package Root
- Build Command
- Runtime Access
- Approved Project Exceptions

项目事实和客户特殊约束应维护在项目自身的 `AGENTS.md` 或 Project Rule 中，不应加入企业通用 Rules。

---

## 8. XWorks Policy

XWorks 是可选项目框架，不是所有 Windchill 项目的默认技术栈。

项目必须在 `AGENTS.md` 中明确：

```text
XWorks Enabled: true
```

或：

```text
XWorks Enabled: false
```

如果项目未启用 XWorks，AI Agent 不得主动将 XWorks 引入当前项目。

如果项目启用了 XWorks，应同时应用：

```text
85-xworks-framework.md
```

并以当前项目实际 XWorks 版本、依赖和现有实现为准。

复杂表单和流程表单可以作为项目评估 XWorks 的重要场景，但是否采用 XWorks 必须由项目架构明确决定。

---

## 9. QMind Enterprise Router

插件包含：

```text
skills/qmind-enterprise-router
```

Router 使用：

```text
skills/qmind-enterprise-router/references/qmind-registry.md
```

维护企业 QMind Registry。

Router 的主要职责：

1. 判断当前任务是否需要企业 QMind
2. 从 Registry 中选择最匹配知识库
3. 构造针对当前事实缺口的 Query
4. 调用官方 QMind Knowledge Base Skill
5. 判断返回证据是否足够支持当前实现

Router 不应：

- 无差别检索所有 QMind
- 让 QMind 自动决定知识库
- 模拟不存在的 QMind 查询结果
- 使用 QMind 覆盖企业 Rules

---

## 10. Project Javadoc Configuration

每个 Windchill 项目通常只对应一个目标 Windchill Version。

因此项目只需要声明：

```text
Windchill Version
+
一个 Javadoc ZIP
```

推荐将 Javadoc 放在项目本地目录：

```text
customer-project/
├── AGENTS.md
├── src/
└── .windchill-ai/
    └── javadoc/
        └── WindchillJavadoc.zip
```

然后在项目：

```text
AGENTS.md
```

配置：

```markdown
- Windchill Version: `13.1.2.0`

### PTC Javadoc

- Javadoc ZIP: `.windchill-ai/javadoc/WindchillJavadoc.zip`
```

未来年份版本也可以：

```markdown
- Windchill Version: `2027`

### PTC Javadoc

- Javadoc ZIP: `.windchill-ai/javadoc/WindchillJavadoc.zip`
```

Javadoc ZIP 文件名不要求包含版本号。

Windchill Version 来自 `AGENTS.md`，不得从 Javadoc 文件名推断。

项目 `.gitignore` 应包含：

```gitignore
.windchill-ai/
```

PTC Javadoc ZIP 不应提交到客户项目 Repository。

也可以将 Javadoc 放在项目目录之外，例如：

```text
/Users/user/ptc-javadoc/WindchillJavadoc.zip
```

然后在 `AGENTS.md` 中配置该路径。

推荐项目相对路径，因为更容易形成统一的团队约定。

---

## 11. Windchill API Lookup

目录：

```text
tools/windchill-api-lookup
```

API Lookup 从项目配置的 PTC Windchill Javadoc ZIP 构建版本隔离的 SQLite Index。

默认数据目录：

```text
~/.windchill-ai
```

典型结构：

```text
~/.windchill-ai/
└── api-index/
    ├── 13.1.2.0/
    │   └── api.sqlite
    └── 2027/
        └── api.sqlite
```

索引文件和 PTC Javadoc 不进入 Git Repository。

一个项目通常只查询一个 Windchill Version。

本机可以因为不同项目同时拥有多个版本 Index。

---

## 12. Automatic Javadoc Index

v0.4 提供 MCP Tool：

```text
ensure_javadoc_index
```

当 Agent 需要精确 PTC API 时：

```text
Read AGENTS.md
        ↓
Read Windchill Version
        ↓
Read Javadoc ZIP
        ↓
Resolve ZIP to absolute path
        ↓
ensure_javadoc_index
        ↓
API Query
```

首次使用某版本：

```text
Javadoc ZIP
     ↓
Parse
     ↓
SQLite
```

后续相同版本和相同 Source：

```text
reused: true
```

不会重复构建。

如果同版本出现不同 Javadoc Source：

```text
INDEX_CONFLICT
```

不会由 Agent 自动覆盖。

---

## 13. Install API Lookup

Python 要求：

```text
Python >= 3.11
```

推荐使用独立 Virtual Environment。

### macOS / Linux

```bash
python3 -m venv ~/.windchill-ai/venv
~/.windchill-ai/venv/bin/python -m pip install ./tools/windchill-api-lookup
```

确认：

```bash
~/.windchill-ai/venv/bin/windchill-api-lookup --help
```

### Windows

```text
python -m venv %USERPROFILE%\.windchill-ai\venv

%USERPROFILE%\.windchill-ai\venv\Scripts\python.exe -m pip install .\tools\windchill-api-lookup
```

确认：

```text
%USERPROFILE%\.windchill-ai\venv\Scripts\windchill-api-lookup.exe --help
```

---

## 14. Manual Javadoc Import

通常不需要开发人员手工导入 Javadoc。

自动索引失败或需要诊断时，可以使用 CLI。

示例：

```bash
windchill-api-lookup add-javadoc \
  --version 13.1.2.0 \
  --zip /path/to/WindchillJavadoc.zip
```

查看已安装版本：

```bash
windchill-api-lookup versions
```

API Lookup 不进行跨版本自动 fallback。

例如当前项目：

```text
Windchill Version = 13.0.2.0
```

但本机只有：

```text
13.1.2.0
```

则不得自动使用 13.1.2.0 的结果代替 13.0.2.0。

---

## 15. MCP

根目录：

```text
mcp.json
```

当前 MCP Server：

```text
windchill-api-lookup
```

默认启动：

```text
windchill-api-lookup serve
```

因此 Qoder Runtime 必须能够找到：

```text
windchill-api-lookup
```

如果 GUI 启动的 Qoder 无法读取 Shell PATH，可将 MCP `command` 配置为实际 executable 的绝对路径。

例如 macOS：

```text
/Users/<user>/.windchill-ai/venv/bin/windchill-api-lookup
```

Windows：

```text
C:\Users\<user>\.windchill-ai\venv\Scripts\windchill-api-lookup.exe
```

---

## 16. API Lookup MCP Capabilities

当前 MCP 提供：

| Tool | Type | Purpose |
|---|---|---|
| `ensure_javadoc_index` | Local cache write | 自动准备当前项目 Javadoc Index |
| `list_versions` | Read-only | 查看本地已有版本 |
| `get_class` | Read-only | Class 精确查询 |
| `search_method` | Read-only | Method / Overload 查询 |
| `get_method` | Read-only | 精确重载查询 |
| `get_index_status` | Read-only | Index Metadata |

API Lookup 可以证明 Javadoc 中的 API Fact，但不能证明：

- 当前业务逻辑正确
- Access Control 正确
- Transaction 正确
- Version / Working Copy 使用正确
- Runtime 行为正确

这些仍需 Rules、代码评审和真实环境验证。

---

## 17. Javadoc Parser Compatibility

当前 Parser 和真实数据验证基线主要针对：

```text
Windchill 13.1.2.0
```

v0.4 允许项目使用：

```text
13.x
2027
未来数字版本标识
```

作为独立 Version Key。

但是：

> Version Naming 支持

和：

> Javadoc HTML Layout 已验证兼容

是两件不同的事情。

如果某历史或未来版本 Javadoc HTML Layout 与当前 Parser 不兼容，Index Build 会失败，而不是静默生成不完整数据。

因此后续需要使用公司实际使用的 Windchill Javadoc 版本逐一做 Parser Compatibility Test。

---

## 18. Golden Reference

Golden Reference 当前为后续核心建设项。

推荐独立维护：

```text
windchill-customization-reference
```

并作为 Git Submodule 挂载到：

```text
skills/windchill-golden-reference
```

推荐结构：

```text
windchill-customization-reference/
├── SKILL.md
├── CATALOG.md
├── README.md
└── references/
    ├── persistence/
    ├── versioning/
    ├── service/
    ├── listener/
    ├── queue/
    ├── security/
    ├── jca/
    ├── workflow/
    ├── wrs/
    └── xworks/
```

Golden Reference 应只包含企业审核通过的高质量样例。

不得把大量未经治理的历史项目代码直接定义为 Golden Reference。

---

## 19. Golden Reference Versioning

Golden Reference Repository 应独立维护和 Review。

DevKit 应固定 Golden Repository Commit，例如：

```text
Windchill AI DevKit 0.4.0
        │
        └── Golden Reference @ <commit>
```

推荐流程：

```text
Golden Reference Change
        ↓
Review
        ↓
Approved
        ↓
Update DevKit Submodule Commit
        ↓
DevKit Release
```

不要让已发布 DevKit 自动跟随 Golden Repository 最新 `main`。

---

## 20. Environment Isolation

DEV、TEST、UAT、PROD 的环境差异必须通过配置或部署机制管理。

不得通过修改业务源码区分不同环境。

原则上，同一个应用版本应使用相同业务代码和构建产物跨环境晋级。

以下内容应配置化：

- Hostname
- URL
- Port
- File Path
- Timeout
- External Endpoint
- Credential
- Secret

不得通过 Hostname、IP、Server Name 或 Installation Path 隐式判断当前环境。

---

## 21. Recommended Agent Workflow

Windchill Coding Task 推荐流程：

```text
Read Project AGENTS.md
        ↓
Understand Existing Code
        ↓
Apply Enterprise Rules
        ↓
Check Project ADR / Exception
        ↓
Need Product Knowledge?
        └── QMind
        ↓
Need Approved Pattern?
        └── Golden Reference
        ↓
Need Exact PTC API?
        │
        ├── ensure_javadoc_index
        └── API Lookup
        ↓
Implement Minimum Necessary Change
        ↓
Build / Test / Static Check
        ↓
Review Git Diff
        ↓
Identify Runtime Verification
```

Agent 不应为了展示工具能力而调用全部知识源。

只使用完成当前任务真正需要的最小集合。

---

## 22. Verification Policy

Agent 只能声明实际执行过的验证。

例如只执行：

```text
Compilation successful
```

不得描述为：

```text
Windchill verified
```

如果没有真实 Windchill Runtime，应明确标记：

```text
待 Windchill 环境验证
```

尤其适用于：

- Listener
- Event
- Queue
- Service Startup
- Access Control
- Principal / Session Context
- Workflow
- JCA Runtime
- Transaction Rollback
- XCONF
- Cluster
- Performance / Concurrency

---

## 23. Repository Security

禁止提交：

- PTC Windchill Javadoc ZIP
- PTC 安装介质
- XWorks 原始部署包
- API Lookup SQLite Index
- Password
- Token
- API Key
- Private Key
- Customer Credential
- Production Secret
- 未经批准的客户源码
- 未经授权重新分发的 PTC 文档

建议 DevKit Repository 和 Golden Reference Repository 使用公司批准的 Private Git Repository。

---

## 24. Recommended `.gitignore`

建议至少包含：

```gitignore
.DS_Store
__pycache__/
*.py[cod]
.pytest_cache/
.venv/
*.egg-info/
build/
dist/

.env
*.sqlite
.windchill-ai/

WindchillJavadoc*.zip
*xworks*.zip
```

实际 XWorks Package 命名规则可根据公司部署包调整。

---

## 25. Internal Pilot

进入公司内部 Pilot 前，建议准备一组固定 Acceptance Cases，例如：

```text
WTPart QuerySpec
Latest Iteration
Transaction
Working Copy
Access Control
Event Listener
Queue
JCA Builder
DataUtility
FormProcessor
XCONF
DEV / UAT / PROD Configuration
XWorks Disabled
XWorks Enabled
Non-existing PTC API
Golden Reference Selection
```

建议对比：

```text
Qoder without Windchill AI DevKit

vs.

Qoder with Windchill AI DevKit
```

重点观察：

- PTC API Hallucination
- Windchill Semantic Error
- Rule Violation
- XWorks Misuse
- Unnecessary Customization
- Security Context Error
- Transaction Error
- Runtime Verification Honesty
- Golden Reference Adoption

---

## 26. Extension Strategy

实际项目出现问题时，应先判断应该增强哪一层。

### Rules

如果 AI 反复违反：

> 必须 / 不得怎么做

则完善 Rules。

### QMind

如果 AI 缺少：

> Windchill / XWorks 产品知识

则完善 QMind。

### Golden Reference

如果 AI 理解原理，但缺少：

> 企业批准的推荐实现

则增加 Golden Reference。

### API Lookup

如果 AI 经常：

> 猜 Class / Method / Signature

则增强 API Lookup。

### Project Context

如果问题只存在于：

> 某个客户项目

则完善项目 `AGENTS.md`、ADR 或 Project Rule。

不要把所有问题都继续堆进企业 Rules。

---

## 27. Scope Control

初版 DevKit 不追求：

- 覆盖所有 Windchill 功能
- 收集所有历史项目代码
- 把 Customization Guide 全部转换成 Rule
- 把所有 PTC 文档放入 Repository
- 自动连接所有 Windchill Runtime
- 替代开发人员 Code Review

初版重点是：

```text
High-value Rules
+
Controlled Knowledge Retrieval
+
Approved Reference Code
+
Exact API Verification
+
Project Context
+
Real Verification
```

---

## 28. Long-Term Direction

内部 Pilot 稳定以后，再根据真实收益评估：

- Golden Reference Repository
- Golden Reference Skill
- Windchill 13.0.2 API Lookup Verification
- More Javadoc Parser Profiles
- Windows x64 standalone API Lookup
- macOS ARM64 standalone API Lookup
- WRS-specific Rule
- XWorks API Lookup
- Automated Benchmark
- Golden Reference Search / MCP
- Code Review Skill
- CI Integration

这些能力应由真实项目需求驱动，而不是为了体系完整提前增加。

---

## 29. Core Principle

Windchill AI DevKit 的核心职责可以概括为：

```text
Rules
告诉 Agent：必须 / 不得怎么做。

QMind
告诉 Agent：Windchill / XWorks 本身是什么、怎么工作。

Golden Reference
告诉 Agent：公司批准的同类实现通常怎么写。

API Lookup
告诉 Agent：这个 PTC API 是否真实存在。

AGENTS.md
告诉 Agent：当前项目实际是什么。

Build / Runtime Verification
告诉我们：最终结果是否真的能够工作。
```

最终目标不是让 AI 自由生成更多 Windchill 代码，而是让 Windchill AI Coding：

```text
更准确
更一致
更可验证
更可维护
更适合企业项目
```