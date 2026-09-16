# Windchill AI DevKit

Windchill AI DevKit 是面向公司内部 PTC Windchill 二次开发的 Qoder Plugin。

它通过企业开发规则、Windchill / XWorks 企业知识、Golden Reference、PTC Javadoc API 精确查询和项目级上下文，为 AI Coding Agent 提供受控、可验证的 Windchill 二次开发能力。

当前版本：

```text
0.5.1
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
- 企业 Windchill 开发经验难以稳定提供给 AI Agent；
- 普通开发人员需要显式知道 Golden / QMind / API Lookup 才能正确使用 DevKit。

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

并让这些能力由 Agent 根据自然开发任务自主编排，而不是要求用户手工指定内部工具。

---

## 2. Architecture

```text
                       Windchill Project
                             │
                             ▼
                         AGENTS.md
                             │
                             ▼
                    AI Coding Agent
                             │
                Autonomous Evidence Routing
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
| Golden Reference | 提供 Candidate / Approved 推荐实现模式 |
| API Lookup | 精确验证目标版本 PTC Java API Metadata |
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

产品事实必须进一步区分事实类型。

#### Exact API Metadata

例如：

- Class 是否存在；
- Method Signature；
- Return Type；
- Parameters；
- Throws；
- Supported；
- Extendable；
- Deprecated。

优先：

```text
Target-version PTC Javadoc
/
Windchill API Lookup
```

#### Framework / Product Behavior

例如：

- Validation Phase；
- Event 生命周期；
- Wizard 客户端交互；
- Workflow 行为；
- 配置机制；
- 官方扩展点语义。

优先：

```text
Target-version PTC Official Documentation
/
Enterprise-reviewed QMind
```

Golden Reference 可以提供实现模式和产品事实线索，但不能自动替代精确 API 或产品行为验证。

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
├── scripts/
│   └── package-plugin.sh
│
├── PACKAGING.md
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
| `00-core-development-rules.md` | 全局基础规则、证据编排与验证边界 |
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

项目应明确：

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

跨 Framework 的概念可以作为设计线索，但不能自动证明存在等价 PTC Class、Method、Status 或 Hook。

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
5. 判断证据是否足以支持当前结论。

0.5.1 起，用户无需显式要求：

```text
查询 QMind
查询 PTC Guide
选择某个知识库
```

Agent 应根据任务自主判断是否需要检索。

QMind 不用于替代：

```text
Rules
Golden Reference
API Lookup
Project Context
Compile Verification
Runtime Verification
```

---

## 9. Golden Reference

Golden Reference 回答：

> 同类 Windchill 定制，我们认可或候选的实现模式通常怎么写？

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

DevKit 固定 Golden Repository 的明确 Commit SHA，而不是 Runtime 自动跟随 `main`。

0.5.1 起，用户无需在 Prompt 中显式写：

```text
请查询 Golden Reference
```

Agent 应根据任务是否需要实现模式，自主选择最小充分 Reference。

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

当前 Golden Corpus：

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
目标项目 Compile Verified
目标项目 Runtime Verified
```

---

## 12. Golden Reference Selection

推荐内部 Agent Workflow：

```text
Read Project Context
        ↓
Identify Task Domain
        ↓
Need Implementation Pattern?
        │
        └── Read Golden CATALOG
                ↓
          Select Minimum Sufficient Reference
                ↓
          Read reference.md + required src/*
                ↓
Apply Rules
        ↓
Verify Product / API Facts if needed
        ↓
Adapt to Current Project
```

如果 1 个核心 Reference 已足够，就只使用 1 个。

默认最多选择 1～3 个最小充分 Reference。

不要一次性加载整个 Golden Repository。

---

## 13. Autonomous Evidence Orchestration

0.5.1 的主要行为变化是：

```text
用户自然描述 Windchill 开发任务
        ↓
Agent 判断任务和风险
        ↓
按需选择证据
        ↓
直接完成任务
```

用户不需要知道 DevKit 内部组件名。

内部职责：

```text
Project Fact
→ AGENTS.md / Project Code / ADR

Development Guardrail
→ Rules

Implementation Pattern
→ Golden Reference

Framework / Product Behavior
→ QMind / Official Documentation

Exact API Metadata
→ Javadoc / API Lookup

Compilation
→ Build

Actual Product Behavior
→ Runtime Verification
```

Agent 不应为了展示能力而机械调用所有组件。

---

## 14. Silent Orchestration

Rules、Golden Reference、QMind 和 API Lookup 默认属于 Agent 内部能力。

常规用户回答中，不应连续播报：

```text
我先加载 Skill
我先读取 Registry
我选择某个 QMind
我再读取 Golden CATALOG
```

应优先给用户：

- 结论；
- 实现方案；
- 必要代码；
- 风险；
- 未验证项。

用户要求依据、Code Review、证据冲突或关键事实未确认时，可以简要说明来源。

---

## 15. Golden Git Authentication

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

普通开发人员安装最终 Plugin ZIP 时，不需要 Golden Repository Git 权限。

---

## 16. Clone DevKit Source

DevKit 维护人员需要完整源码时：

```bash
git clone --recurse-submodules \
  <windchill-ai-devkit-repository-url>
```

已有普通 Clone：

```bash
git submodule update --init --recursive
```

检查：

```bash
git submodule status
```

---

## 17. Update Golden Baseline

更新 Golden：

```bash
git -C skills/windchill-golden-reference fetch origin
git -C skills/windchill-golden-reference checkout <approved-golden-sha>
```

检查：

```bash
git diff --submodule=log
```

然后由 DevKit 提交新的 gitlink SHA。

---

## 18. Windchill API Lookup

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
Standalone Distribution Pending
Full MCP SIT Pending
```

---

## 19. Windchill Version

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

项目应尽量填写实际完整版本。

不进行跨版本自动 fallback。

---

## 20. Javadoc Configuration

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

PTC Javadoc ZIP 不随 DevKit Plugin 分发。

---

## 21. API Lookup Local Environment

0.5.1 的 API Lookup Runtime 仍为独立 Python Runtime。

要求：

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

cd tools/windchill-api-lookup
python -m pip install -e '.[dev]'
```

当前：

```text
~/.venvs/windchill-api-lookup
```

保存 Python Runtime / Dependencies。

```text
~/.windchill-ai
```

保存 API Lookup Data / Cache / Index。

Standalone Binary Distribution 计划放到后续版本实现，不属于 0.5.1 范围。

---

## 22. Javadoc Parser Baseline

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

## 23. Verification Policy

必须区分：

```text
Implementation Pattern Evidence
API Metadata Verification
Compile Verification
Runtime Verification
```

例如：

```text
PTC Guide / Golden Reference
→ 可以证明实现模式有依据

Target-version Javadoc / API Lookup
→ 可以证明 API Metadata

Target Build / Classpath
→ 可以证明 Compile Verification

Actual Windchill Runtime
→ 才能证明 Runtime Verification
```

Agent 只能声明实际完成的验证。

没有真实 Windchill Runtime 时，应明确：

```text
待 Windchill 环境验证
```

---

## 24. Plugin Packaging

正式 Packaging 定义在：

```text
PACKAGING.md
```

构建：

```bash
./scripts/package-plugin.sh
```

Packaging workflow 会：

```text
Verify Clean Git State
        ↓
Verify Golden gitlink
        ↓
Materialize Golden
        ↓
Assemble Plugin
        ↓
Validate Required Files
        ↓
Run Qoder Validation When Available
        ↓
Create ZIP
        ↓
Validate ZIP
        ↓
Generate SHA-256
```

最终 Plugin ZIP 包含 Golden Reference 本地文件。

普通 Plugin 用户：

```text
不需要 Codeup Account
不需要 Golden Git Credential
不需要执行 git submodule
```

需要注意：

```text
Plugin ZIP 自包含 Rules / Skills / Golden
≠
API Lookup Runtime 已自包含
```

0.5.1 的 `windchill-api-lookup` 仍为外部 Runtime Dependency。

---

## 25. Repository Security

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

## 26. Current Status

```text
Rules                          Ready
Project AGENTS                 Ready
QMind Router                   Ready
Golden Corpus                  62 Candidates
Golden Skill                   Ready
Golden DevKit Integration      Ready
Javadoc 13.1.2 Baseline        Verified
API Lookup                     Feature Complete
API Lookup Distribution        External Python Runtime
Plugin Packaging Workflow      Validated
Plugin ZIP Install             Validated on 0.5.0 baseline
Smoke / Regression             Complete
Autonomous Orchestration       Ready in 0.5.1
Natural Prompt Acceptance      Pending
Full MCP / Runtime SIT         Pending
Internal Pilot                 Pending
```

---

## 27. 0.5.1 Acceptance

0.5.1 重点验证：

```text
Natural User Prompt
        ↓
Autonomous Trigger
        ↓
Minimal Evidence Selection
        ↓
Silent Orchestration
        ↓
Correct Evidence Routing
        ↓
Technically Correct Result
```

Acceptance Prompt 不应显式要求：

```text
Rules
Golden Reference
QMind
Customization Guide
API Lookup
```

因为测试目标正是验证 Agent 是否可以自主使用这些能力。

---

## 28. Next Steps

```text
0.5.1 Natural Prompt Acceptance
        ↓
0.5.1 Release Baseline
        ↓
0.6.0 API Lookup Standalone Distribution
        ↓
Full MCP / Runtime SIT
        ↓
Internal Pilot
```

0.6.0 主要目标：

```text
macOS ARM64 standalone executable
Windows x64 standalone executable
Python-free end-user installation
Plugin-local MCP startup
Javadoc indexing E2E
Qoder MCP E2E
```

---

## 29. Core Principle

```text
Rules
告诉 Agent：必须 / 不得怎么做。

QMind
告诉 Agent：Windchill / XWorks 本身是什么、怎么工作。

Golden Reference
告诉 Agent：同类实现通常怎么写。

API Lookup
告诉 Agent：目标版本 PTC API Metadata 是什么。

AGENTS.md
告诉 Agent：当前项目实际是什么。

Build
告诉我们：代码能否在目标依赖中成立。

Runtime Verification
告诉我们：真实 Windchill 行为是否符合预期。
```

最终目标是让 Windchill AI Coding：

```text
用户自然提出开发问题
        ↓
Agent 自主寻找必要证据
        ↓
输出准确、可验证、可维护的实现
```