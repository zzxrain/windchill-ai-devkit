# Windchill AI DevKit

Windchill AI DevKit 是面向公司内部 PTC Windchill 二次开发的 Qoder Plugin。

它通过企业开发规则、Windchill / XWorks 企业知识、Golden Reference、PTC Javadoc API 精确查询和项目级上下文，为 AI Coding Agent 提供受控、可验证的 Windchill 二次开发能力。

当前版本：

```text
0.5.0
```

---

## 1. Goals

Windchill AI DevKit 主要解决：

- AI 编造 PTC Class / Method / Signature；
- AI 不理解 Windchill Version / Iteration / Working Copy 等对象语义；
- AI 机械复制历史项目中的低质量代码；
- Transaction、Access Control、Queue、Listener 等高风险场景实现不一致；
- 不同项目的 XWorks、Windchill Version、Java Version 和架构差异；
- 生成代码与真实 Windchill Runtime Verification 混淆；
- 企业 Windchill 开发经验难以稳定提供给 AI Agent。

目标不是让 AI “记住全部 Windchill”，而是建立：

```text
Rules
+
Controlled Knowledge
+
Golden Reference
+
Exact API Verification
+
Project Context
+
Real Verification
```

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
          │                  │                  │
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
| Rules | 定义 Agent 必须 / 不得如何开发 |
| QMind Router | 获取 Windchill / XWorks 产品和企业知识 |
| Golden Reference | 提供候选或批准的推荐实现模式 |
| API Lookup | 精确验证目标版本 PTC Java API |
| AGENTS.md | 描述当前项目事实、环境和项目例外 |
| Project Code | 提供当前架构和兼容性上下文 |
| Build / Test | 验证代码级结果 |
| Runtime Verification | 验证真实 Windchill Runtime 行为 |

这些能力不能互相替代。

---

## 3. Authority Model

### Development Decision

判断“代码应该如何实现”时，默认优先级：

1. 企业强制安全、合规和架构要求；
2. Approved Project Exception / ADR / 客户明确要求；
3. Windchill AI DevKit Rules；
4. Approved Golden Reference；
5. Candidate Golden Reference；
6. 当前项目已有实现；
7. 模型自身知识。

历史项目代码属于兼容性和经验依据，不自动等同于最佳实践。

### Product Facts

判断以下事实时：

- PTC Class 是否存在；
- Method Signature；
- Supported；
- Extendable；
- Deprecated；
- Extension Point；
- Windchill 产品行为；

优先依据：

1. 目标版本 PTC Javadoc / 官方资料；
2. 企业审核 QMind；
3. 与目标版本匹配的 Golden Reference；
4. 当前项目已验证实现；
5. 模型知识。

不得根据命名规律猜测 PTC API。

---

## 4. Repository Structure

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
│   ├── qmind-enterprise-router/
│   │   ├── SKILL.md
│   │   └── references/
│   │
│   └── windchill-golden-reference/       # Git Submodule
│       ├── SKILL.md
│       ├── CATALOG.md
│       ├── README.md
│       ├── SOURCES.md
│       ├── CURATION_NOTES.md
│       └── references/
│
├── tools/
│   └── windchill-api-lookup/
│
├── templates/
│   └── AGENTS.md
│
├── .gitmodules
├── mcp.json
├── .gitignore
└── README.md
```

---

## 5. Rules

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

`00` 为基础 Rule，其余 Rule 根据任务按需应用。

---

## 6. Project Context

每个 Windchill 项目建议在项目根目录维护：

```text
AGENTS.md
```

模板位于：

```text
templates/AGENTS.md
```

至少应维护：

- Windchill Version；
- Java Version；
- PTC Javadoc ZIP；
- XWorks Enabled；
- XWorks Version；
- Custom Package Root；
- Build Command；
- Runtime Access；
- Approved Project Exceptions；
- Compatibility Constraints。

项目事实和客户特殊约束应维护在项目自身，而不是写入企业通用 Rules。

---

## 7. XWorks Policy

XWorks 是可选项目框架，不是所有 Windchill 项目的默认技术栈。

项目必须明确：

```text
XWorks Enabled: true
```

或：

```text
XWorks Enabled: false
```

如果：

```text
XWorks Enabled: false
```

Agent 不得主动：

- 引入 XWorks Dependency；
- 使用 XWorks API；
- 为了套用 Golden Reference 改变项目技术栈。

如果：

```text
XWorks Enabled: true
```

则结合：

```text
85-xworks-framework.md
```

和对应 XWorks Golden Reference 使用。

---

## 8. QMind Enterprise Router

插件包含：

```text
skills/qmind-enterprise-router
```

QMind Router 用于：

1. 判断任务是否需要企业知识；
2. 选择匹配的 QMind Knowledge Base；
3. 构造针对当前事实缺口的 Query；
4. 获取 Windchill / XWorks 产品知识；
5. 判断证据是否足以支持实现。

QMind 不用于替代：

```text
Rules
Golden Reference
API Lookup
Project Context
```

---

## 9. Golden Reference

Golden Reference 回答：

> 同类 Windchill 定制，我们认可的实现模式通常怎么写？

企业 Golden Reference Repository：

```text
https://codeup.aliyun.com/60d04cfaccca0c526834b7ad/AI_Projects/windchill-customization-reference.git
```

在 DevKit 中挂载到：

```text
skills/windchill-golden-reference
```

集成方式：

```text
Git Submodule
```

Golden Repository 与 DevKit 独立维护。

DevKit 固定 Golden Repository 的一个明确 Commit SHA，而不是运行时自动跟随最新 `main`。

---

## 10. Golden Reference Versioning

版本关系：

```text
Windchill AI DevKit Release
        │
        └── Golden Reference @ exact commit SHA
```

更新流程：

```text
Golden Reference Change
        ↓
Review
        ↓
Golden Commit
        ↓
Update DevKit Submodule SHA
        ↓
DevKit Release
```

不要在 `.gitmodules` 中配置：

```text
branch = main
```

已发布 DevKit 必须使用稳定、可复现的 Golden Baseline。

---

## 11. Golden Reference Status

当前 Golden Corpus 主要包含：

```text
62 Candidate References
```

来源包括：

```text
PTC Guide Derived
Legacy Project Derived
XWorks Guide Derived
```

Candidate 可以用于：

- Pattern Discovery；
- Design Reference；
- 初始代码生成；
- Code Review；
- Benchmark。

但 Candidate 不应描述为：

```text
企业最终批准实现
目标项目 Runtime Verified
```

---

## 12. Golden Reference Selection

推荐 Agent Workflow：

```text
Read Project AGENTS.md
        ↓
Identify Task Domain
        ↓
Read Golden CATALOG.md
        ↓
Select Module
        ↓
Select 1–3 References
        ↓
Read reference.md + src/*
        ↓
Apply Rules
        ↓
Verify exact PTC API if needed
        ↓
Adapt to Current Project
```

不要一次性加载整个 Golden Repository。

---

## 13. Golden Git Authentication

Golden Repository 可以要求企业认证。

`.gitmodules` 只保存：

```text
Repository URL
```

DevKit Git Tree 保存：

```text
Golden Commit SHA
```

不得把以下内容写入 DevKit：

```text
Username
Password
Personal Access Token
Private Key
```

认证由：

```text
Developer Git Credential
Release Machine
CI Credential
SSH Agent
```

负责。

认证只发生在：

```text
DevKit Source Maintenance
Build
Release
CI
```

普通开发人员安装最终 Plugin ZIP 时，不需要 Golden Repository 的 Git 权限。

---

## 14. Clone DevKit Source

DevKit 维护人员需要完整源码时，推荐：

```bash
git clone --recurse-submodules \
  <windchill-ai-devkit-repository-url>
```

如果已经完成普通 Clone：

```bash
git submodule update --init --recursive
```

检查：

```bash
git submodule status
```

应看到：

```text
<golden-sha> skills/windchill-golden-reference
```

---

## 15. Update Golden Baseline

Golden Repository 更新以后，不会自动改变已发布 DevKit。

需要显式更新：

```bash
git -C skills/windchill-golden-reference fetch origin
```

然后：

```bash
git -C skills/windchill-golden-reference checkout <approved-golden-sha>
```

检查：

```bash
git diff --submodule=log
```

再由 DevKit 提交新的 gitlink SHA。

---

## 16. Windchill API Lookup

API Lookup 位于：

```text
tools/windchill-api-lookup
```

它回答：

> 当前目标 Windchill Version 中，这个 PTC Java API 是否真实存在？

当前 MCP Tool Contract：

| Tool | Purpose |
|---|---|
| `ensure_javadoc_index` | 建立或复用目标版本 Javadoc Index |
| `list_versions` | 查看本机已有 Index Version |
| `get_class` | 精确查询 Class |
| `search_method` | 查询 Method / Overload |
| `get_method` | 精确查询 Method |
| `get_index_status` | 查看 Index Metadata |

当前状态：

```text
Feature Complete
SIT Pending
```

---

## 17. Windchill Version

API Lookup 当前将 Windchill Version 作为精确 Version Key。

支持：

```text
1～4 段数字 Release Identifier
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

项目应尽量填写实际完整版本，例如：

```text
13.1.2.0
2027.0.0.0
```

不进行跨版本自动 fallback。

---

## 18. Javadoc Configuration

项目通常声明：

```text
Windchill Version
+
一个 PTC Javadoc ZIP
```

推荐：

```text
customer-project/
├── AGENTS.md
├── src/
└── .windchill-ai/
    └── javadoc/
        └── WindchillJavadoc.zip
```

`AGENTS.md` 示例：

```markdown
- Windchill Version: `13.1.2.0`

### PTC Javadoc

- Javadoc ZIP: `.windchill-ai/javadoc/WindchillJavadoc.zip`
```

Windchill Version 不得从 Javadoc ZIP 文件名推断。

---

## 19. API Lookup Local Environment

Python 要求：

```text
Python >= 3.11
```

开发环境推荐：

```text
~/.venvs/windchill-api-lookup
```

例如：

```bash
python3 -m venv ~/.venvs/windchill-api-lookup
source ~/.venvs/windchill-api-lookup/bin/activate
```

安装：

```bash
cd tools/windchill-api-lookup
python -m pip install -e '.[dev]'
```

注意：

```text
~/.venvs/windchill-api-lookup
```

保存 Python Runtime / Dependencies。

而：

```text
~/.windchill-ai
```

保存 API Lookup Data / Cache / Index。

---

## 20. Javadoc Parser Baseline

当前真实验证基线：

```text
Windchill 13.1.2.0
```

全量 Javadoc Index：

```text
HTML Pages:   8137
Classes:      6118
Methods:      23804
Failed Pages: 0
```

其他 Windchill Version 仍应使用真实 Javadoc 做兼容性验证。

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
Need Implementation Pattern?
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

Agent 不应为了展示 Tool 能力而调用全部知识源。

只使用完成当前任务真正需要的最小集合。

---

## 22. Verification Policy

Agent 只能声明实际完成的验证。

例如只执行：

```text
Compilation successful
```

不得描述为：

```text
Windchill Runtime verified
```

没有真实 Windchill Runtime 时，应明确说明：

```text
待 Windchill 环境验证
```

尤其适用于：

- Listener；
- Event；
- Queue；
- Service Startup；
- Access Control；
- Principal / Session Context；
- Workflow；
- JCA Runtime；
- Transaction Rollback；
- XCONF；
- Cluster；
- Performance / Concurrency。

---

## 23. Plugin Packaging Boundary

Git Submodule 在 DevKit Repository 中只保存：

```text
Repository URL
+
Commit Pointer
```

普通：

```bash
git archive
```

不会自动把 Submodule 的真实内容展开进 ZIP。

正式 Plugin Packaging 必须：

```text
Checkout DevKit
        ↓
Authenticate Golden Git
        ↓
Initialize Submodule
        ↓
Materialize Golden Files
        ↓
Build Plugin Staging Directory
        ↓
Build Plugin ZIP
        ↓
Verify ZIP Content
```

最终 Plugin ZIP 必须实际包含：

```text
skills/windchill-golden-reference/SKILL.md
skills/windchill-golden-reference/CATALOG.md
skills/windchill-golden-reference/references/*
```

普通开发人员安装最终 Plugin：

```text
不需要 Codeup Account
不需要 Golden Git Credential
不需要执行 git submodule
```

Qoder Runtime 直接读取 Plugin 中的本地 Golden Reference 文件。

---

## 24. Repository Security

禁止提交：

- PTC Windchill Javadoc ZIP；
- PTC 安装介质；
- XWorks 原始部署包；
- API Lookup SQLite Index；
- Password；
- Token；
- API Key；
- Private Key；
- Customer Credential；
- Production Secret；
- 未经批准的客户源码；
- 未经授权重新分发的 PTC 文档。

Golden Reference 建议维护在公司批准的 Authenticated Private Git Repository。

---

## 25. Current Status

```text
Rules                       Ready
Project AGENTS              Ready
QMind Router                Ready
API Lookup                  Feature Complete / SIT Pending
Javadoc 13.1.2 Baseline     Verified
Golden Corpus               62 Candidates
Golden Skill                Ready
Golden DevKit Integration   Ready in 0.5.0
Plugin Packaging            Next
Acceptance Benchmark        Pending
Full SIT                    Pending
Internal Pilot              Pending
```

---

## 26. Next Steps

Golden Reference 接入完成后：

```text
Plugin Packaging
        ↓
Acceptance Benchmark
        ↓
Full SIT
        ↓
Internal Pilot
```

在 SIT 之前暂不继续扩展 API Lookup MCP。

---

## 27. Core Principle

```text
Rules
告诉 Agent：必须 / 不得怎么做。

QMind
告诉 Agent：Windchill / XWorks 本身是什么、怎么工作。

Golden Reference
告诉 Agent：同类实现通常怎么写。

API Lookup
告诉 Agent：这个 PTC API 是否真实存在。

AGENTS.md
告诉 Agent：当前项目实际是什么。

Build / Runtime Verification
告诉我们：最终结果是否真的能够工作。
```

最终目标是让 Windchill AI Coding：

```text
更准确
更一致
更可验证
更可维护
更适合企业项目
```