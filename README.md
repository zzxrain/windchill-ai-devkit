# Windchill AI DevKit

Windchill AI DevKit 是面向公司内部 PTC Windchill 二次开发的 Qoder Plugin。

当前版本：

```text
1.0.1
```

当前发布定位：

```text
1.0.x Stable MVP
```

Windchill AI DevKit 的目标不是让 AI 记住全部 Windchill，而是建立一套可复用的：

```text
Rules
+
Enterprise Knowledge
+
Golden Reference
+
Project Context
+
Evidence Boundary
```

让开发人员可以直接使用自然语言描述真实 Windchill 开发任务，而不需要先理解 DevKit 内部组件。

---

## 1. Current Release

### 1.0.1

1.0.1 是基于 1.0.0 的质量优先性能优化版本。

主要变化：

```text
Golden Reference Minimum Sufficient Evidence
+
Reference Sufficiency Gate
+
减少无必要 src/* 深入读取
+
减少无目的目录扫描
+
保留完整 Evidence Handoff
```

1.0.1 不改变：

```text
Rules Authority
QMind Product Evidence
Golden Evidence Boundary
API Verification Boundary
Compile Verification Boundary
Runtime Verification Boundary
```

核心原则：

```text
减少没有新增证据价值的 Tool Call
而不是
减少保证技术正确性所需的 Evidence
```

因此：

```text
Quality First
Performance Second
```

如果性能提升导致技术正确性下降，则不接受该优化。

### 1.0.0

1.0.0 是首个 MVP Baseline。

Git Tag：

```text
v1.0.0
```

它固定了：

```text
Rules
QMind Enterprise Router
Golden Reference
Project Context
QMind Retrieve Contract Guard
Packaging / Release Baseline
```

1.0.1 在此基础上仅优化 Golden Evidence 获取效率。

---

## 2. Runtime Scope

1.0.1 Plugin Runtime 包含：

```text
Windchill Development Rules
QMind Enterprise Router
Golden Reference
Project Context Template
QMind Retrieve Contract Guard
Plugin Metadata
README
```

1.0.1 不包含：

```text
Javadoc API Lookup Runtime
PTC Javadoc
Python Runtime
Automatic Target-version API Index
Automatic Compile Verification
Automatic Windchill Runtime Verification
Semantic Product-fact Response Guard
```

Source Repository 中仍保留：

```text
tools/windchill-api-lookup
```

作为后续版本研发代码。

它不进入 1.0.1 Plugin ZIP，也不会由 1.0.1 Plugin 自动启动。

---

## 3. Goals

Windchill AI DevKit 主要用于降低以下问题：

- AI 编造 PTC API；
- AI 混淆 Version / Iteration / Working Copy；
- AI 机械复制历史低质量代码；
- Query / Transaction / Security / Event / Queue 等实现不一致；
- 不同项目 Windchill Version 和技术栈差异；
- XWorks 与标准 Windchill Framework 被错误混用；
- Framework Behavior 与 Engineering Inference 被混为一谈；
- Golden Reference、官方资料和当前项目代码之间没有明确权威边界；
- AI 声称完成实际并未执行的 Compile / Runtime Verification；
- Agent 为简单问题进行无必要的重复 Evidence Retrieval。

---

## 4. Architecture

```text
                   Windchill Project
                          │
                          ▼
                      AGENTS.md
                          │
                          ▼
                   AI Coding Agent
                          │
               Internal Evidence Plan
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
      Rules             QMind        Golden Reference
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                          ▼
                 Project Code / Build
                          │
                          ▼
              Windchill Runtime Verification
```

职责：

| Component | Responsibility |
|---|---|
| Rules | 定义代码必须 / 不得如何实现 |
| QMind Router | 获取 Windchill / XWorks Product / Framework Knowledge |
| Golden Reference | 提供 Candidate / Approved Implementation Pattern |
| AGENTS.md | 描述当前项目事实和项目例外 |
| QMind Contract Guard | 阻止 malformed QMind retrieve 请求进入 MCP |
| Project Code | 提供兼容性和调用上下文 |
| Build | 真实目标 Classpath 编译验证 |
| Runtime | 真实 Windchill 行为验证 |

这些能力不能机械互相替代。

---

## 5. Evidence Model

### Development Decision

判断“代码应该如何实现”时，默认优先级：

1. 企业强制安全、合规、架构要求；
2. Approved Project Exception / ADR / 客户明确要求；
3. Windchill AI DevKit Rules；
4. Approved Golden Reference；
5. Candidate Golden Reference；
6. 当前项目已有实现；
7. 模型自身知识。

现有项目代码属于兼容性和历史经验，不自动等同于规范。

### Product / Framework Behavior

例如：

```text
Validation Phase
Event Semantics
Wizard Behavior
DataUtility Lifecycle
Transaction Behavior
Queue Behavior
Workflow Behavior
Configuration Mechanism
```

优先：

```text
Target-version PTC Official Documentation
/
Enterprise QMind
```

不得把：

```text
usually
typical
example
convention
```

无依据扩大为：

```text
always
all
must
never
```

### Exact API Metadata

例如：

```text
Class
Method
Signature
Constant
Return Type
Throws
Supported
Extendable
Deprecated
Inheritance
Implemented Interfaces
```

1.0.1 不提供自动 Javadoc API Lookup Runtime。

如果当前任务没有足够的目标版本证据，Agent 应：

```text
UNVERIFIED PTC API
```

并优先退回：

```text
Pattern-level
/
Pseudocode
```

而不是猜测精确 API。

---

## 6. Repository Structure

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
│   └── windchill-golden-reference/
│       ├── SKILL.md
│       ├── CATALOG.md
│       ├── README.md
│       ├── SOURCES.md
│       ├── CURATION_NOTES.md
│       └── references/
│
├── hooks/
│   └── hooks.json
│
├── bin/
│   ├── qmind-retrieve-guard
│   ├── qmind-retrieve-guard.cmd
│   └── qmind-retrieve-guard.ps1
│
├── templates/
│   └── AGENTS.md
│
├── tools/
│   └── windchill-api-lookup/
│
├── scripts/
│   └── package-plugin.sh
│
├── PACKAGING.md
├── .gitmodules
├── .gitignore
└── README.md
```

注意：

```text
tools/windchill-api-lookup
```

属于 Source Repository 中保留的后续研发代码，不属于 1.0.1 Plugin Runtime。

---

## 7. Rules

核心 Rules：

| Rule | Scope |
|---|---|
| `00-core-development-rules.md` | 基础规则、Evidence Plan、验证边界 |
| `10-java.md` | Java 工程规则 |
| `20-windchill-api.md` | PTC API 使用与未验证 API 降级策略 |
| `30-persistence-query-transaction.md` | Persistence / Query / Transaction |
| `35-versioning-object-semantics.md` | Version / Iteration / Working Copy |
| `40-access-control-security-context.md` | Access Control / Security Context |
| `50-service-event-queue.md` | Service / Event / Listener / Queue |
| `60-configuration-customization-files.md` | XCONF / Configuration |
| `70-ui-web-extension.md` | JCA / MVC / UI Extension |
| `80-logging-diagnostics.md` | Logging / Diagnostics |
| `85-xworks-framework.md` | Optional XWorks Framework |

`00-core-development-rules.md` 为 always-on 基础规则。

其他 Rule 根据任务自动匹配。

---

## 8. Project Context

每个 Windchill 项目建议在 Repository 根目录维护：

```text
AGENTS.md
```

模板：

```text
templates/AGENTS.md
```

建议维护：

- Windchill Version；
- Java Version；
- XWorks Enabled；
- XWorks Version；
- Custom Package Root；
- Build Command；
- Runtime Access；
- PTC Javadoc 位置（如项目具备）；
- Approved Project Exceptions；
- Compatibility Constraints。

项目事实和客户例外不应写入企业通用 Rules。

---

## 9. XWorks Policy

XWorks 是可选技术栈。

项目应明确：

```text
XWorks Enabled: true
```

或：

```text
XWorks Enabled: false
```

未明确启用 XWorks 时，不得因为 Golden 中存在 XWorks Reference 就：

- 引入 XWorks Dependency；
- 调用 XWorks API；
- 假设标准 Windchill 存在等价 Hook；
- 改变当前项目架构。

---

## 10. QMind Enterprise Router

Plugin 包含：

```text
skills/qmind-enterprise-router
```

QMind Router 主要回答：

> Windchill / XWorks 产品本身如何工作？

例如：

- Framework Behavior；
- 生命周期；
- Configuration；
- Validation；
- Event；
- Workflow；
- 安装部署；
- 升级迁移。

用户无需显式写：

```text
查询 QMind
使用企业知识库
```

Agent 根据当前 Product / Framework Knowledge Gap 自主判断是否需要使用。

QMind 不替代：

```text
Rules
Golden Reference
Project Context
Exact API Metadata
Compile Verification
Runtime Verification
```

---

## 11. QMind Retrieve Contract Guard

1.0.x 包含：

```text
PreToolUse Hook
+
qmind-retrieve-guard
```

该 Guard 只负责确定性的 Runtime Contract：

```text
qoder-qmind retrieve
必须包含：
notebookId
+
query
```

如果缺少必需参数：

```text
Block before MCP invocation
```

然后要求 Agent：

```text
QMind Router
→ Registry
→ notebookId + query
→ retry
```

该 Hook 不维护 Windchill 产品知识。

它不会通过正则判断：

```text
某 Event 是否 Vetoable
某 API Signature 是否正确
某 Lifecycle 是否成立
```

这些事实仍由对应 Evidence Source 负责。

---

## 12. Golden Reference

Golden Reference 回答：

> 同类 Windchill 定制通常如何实现？

DevKit 使用 Git Submodule 固定 Golden Reference 的精确 Commit SHA。

企业 Golden Repository：

```text
https://codeup.aliyun.com/60d04cfaccca0c526834b7ad/AI_Projects/windchill-customization-reference.git
```

Plugin 发布时不会要求普通开发人员访问该 Git Repository。

Packaging 会把固定 Commit 中的 Golden 内容物化进入 Plugin ZIP。

---

## 13. Golden Reference Status

当前 Golden Corpus 主要为：

```text
Candidate
```

Candidate 可以用于：

- Pattern Discovery；
- Design Reference；
- Initial Code Generation；
- Code Review；
- Benchmark。

Candidate 不等于：

```text
Enterprise Approved
Compile Verified
Runtime Verified
```

Agent 必须保留这一边界。

---

## 14. Golden Minimum Sufficient Evidence

1.0.1 新增 Quality-first Evidence Budget。

Windchill-specific Implementation / Design / Review / Debug 仍然执行 Golden Catalog Preflight。

内部逻辑：

```text
Need Implementation Pattern?
        ↓
Read CATALOG
        ↓
Strong Match?
   ├── No → Stop Golden Lookup
   └── Yes
        ↓
Select Minimum Sufficient Reference
        ↓
Read reference.md
        ↓
Reference Sufficiency Gate
        ↓
Need source implementation detail?
   ├── No → Stop Golden Lookup
   └── Yes
        ↓
Read minimum necessary src/*
```

对于 Pattern-level 问题，如果：

```text
reference.md
```

已经直接支持所需实现模式，则默认不再深入：

```text
src/*
```

但这只意味着：

```text
Stop Golden Lookup
```

不意味着：

```text
Stop Product Verification
Stop API Verification
Stop Compile Verification
Stop Runtime Verification
```

---

## 15. Golden Tool Call Discipline

1.0.1 优先减少：

```text
重复读取同一 Reference
无目的 ls -R
无目的 find
读取整个 Reference Source Tree
为了“保险”继续读取相邻 Reference
已经有充分 Pattern Evidence 后继续探索
```

如果必须读取 Golden Source，应能回答：

```text
这个额外 Tool Call 具体要解决哪个尚未解决的问题？
```

允许继续深入的典型场景：

```text
用户明确要求具体代码
修改已有实现
Code Review
Debug / Troubleshooting
reference.md 不足以支持所需实现细节
```

因此：

```text
Evidence Coverage
```

保持不变；

优化的是：

```text
Evidence Retrieval Depth
```

---

## 16. Autonomous Evidence Orchestration

普通开发人员只需要描述实际任务。

例如：

```text
一个 Windchill JCA Table 有 2000 行，
DataUtility 每一行都需要查询数据库，
应该怎么优化？
```

开发人员不需要写：

```text
请查询 Golden
请查询 QMind
请加载某个 Rule
```

Agent 内部按真正存在的 Evidence Gap 选择对应 Evidence。

原则：

```text
Demand-driven Evidence
而不是
Checklist-driven Evidence
```

---

## 17. Silent Orchestration

Skill / Router / Golden 检索属于内部工作。

正常情况下最终回答应直接提供：

- 结论；
- 设计；
- 代码；
- 风险；
- 未验证项。

不应把内部过程作为答案主体，例如：

```text
我先加载 Skill
我先读取 Registry
我现在查询 Golden
```

受当前 Qoder Agent Runtime 行为影响，少数情况下仍可能出现内部检索进度文本。

对于 1.0.x，这属于已知 UX 限制，不代表某项技术事实因此完成验证。

---

## 18. API Verification Policy

1.0.1 不启用自动 Javadoc API Lookup Runtime。

因此如果无法从当前可用证据确认某个 PTC API：

```text
UNVERIFIED PTC API
```

Agent 应优先：

```text
Pattern-level
+
需要确认的 API Symbol
```

而不是：

```text
凭模型记忆补齐 Package / Method / Constant / Signature
```

尤其不得：

```text
先生成一个未经验证的精确 API 调用
+
最后补一句“请对照 Javadoc”
```

来规避 Exact API Evidence Requirement。

对于需要最终投产的代码，仍必须在目标 Windchill Classpath 上完成实际 Build。

---

## 19. Compile Verification

以下内容都不能代替真实编译：

```text
Golden Reference
PTC Guide Example
Java Syntax
Static Analysis
Model Confidence
Javadoc Metadata
```

Compile Verification 必须来自目标 Windchill Classpath。

如果 Agent 无法执行项目 Build：

```text
Not Compile Verified
```

---

## 20. Runtime Verification

以下行为必须以实际 Windchill Runtime 为最终依据：

- Event 实际触发；
- Transaction / Rollback；
- UI lifecycle；
- Workflow；
- Queue；
- Security Context；
- Access Control；
- Cluster；
- Background processing。

代码实现完成：

```text
≠ Runtime Verified
```

Javadoc 验证成功：

```text
≠ Runtime Verified
```

---

## 21. Packaging

构建 Plugin：

```bash
./scripts/package-plugin.sh
```

当前输出：

```text
dist/
├── windchill-ai-devkit-1.0.1.zip
└── windchill-ai-devkit-1.0.1.zip.sha256
```

Packaging 使用：

```text
Committed DevKit HEAD
+
Pinned Golden Commit
```

生成可复现 Release Package。

---

## 22. Plugin ZIP Boundary

1.0.1 ZIP 包含：

```text
.qoder-plugin/
rules/
skills/qmind-enterprise-router/
skills/windchill-golden-reference/
hooks/
bin/
templates/
README.md
```

不包含：

```text
.git/
.gitmodules
.gitignore
tools/
mcp.json
Python Runtime
PTC Javadoc
Source Repository Metadata
```

---

## 23. Installation

将：

```text
windchill-ai-devkit-1.0.1.zip
```

安装到公司使用的 Qoder / Qoder CN 环境。

建议对同版本开发 Candidate：

```text
卸载旧版本
→ 完全退出 Qoder
→ 重启
→ 安装新 ZIP
```

安装后至少确认：

```text
Plugin Version = 1.0.1
Rules 可发现
QMind Router 可发现
Golden Reference Skill 可发现
Golden CATALOG / references 可读取
PreToolUse Hook 可加载
QMind Retrieve Guard 可工作
```

---

## 24. 1.0.1 Acceptance

1.0.1 的目标不是单纯缩短 wall-clock time。

正式验收使用以下六个质量维度：

```text
Autonomous Trigger
Minimal Evidence Selection
Silent Orchestration
Evidence Routing
Technical Correctness
Runtime Honesty
```

质量判断只使用：

```text
PASS
PARTIAL
FAIL
```

1.0.1 必须保证：

```text
Technical Correctness
不得因为性能优化明显下降
```

性能另外记录：

```text
Elapsed Time
Tool Call Count
Golden reference.md Reads
Golden src/* Reads
QMind Retrieve Count
```

性能不是第七个质量维度。

---

## 25. Performance Acceptance Principle

1.0.1 采用：

```text
Quality-neutral Performance Optimization
```

接受：

```text
质量保持
+
Tool Calls 明显减少
```

不接受：

```text
Wall-clock 显著降低
+
Technical Correctness 下降
```

Wall-clock 受：

```text
LLM Provider Load
Network
Model Reasoning Effort
Context Size
Tool Runtime
```

等因素影响。

因此更稳定的性能指标是：

```text
不必要的 Tool Calls 是否减少
Golden Source Reads 是否减少
Evidence Coverage 是否保持
```

---

## 26. Known Limitations

### Exact API Verification

1.0.1 没有自动 Javadoc API Lookup Runtime。

精确 API 最终仍需要：

```text
Target Javadoc
Target Classpath Build
```

确认。

### Golden Status

当前 Golden Corpus 主要为 Candidate，而不是 Approved。

### Runtime Verification

DevKit 本身不能替代真实 Windchill 测试环境。

### Silent Orchestration

当前 Qoder Runtime 下，内部 Skill narration 仍可能偶发出现。

1.0.1 继续通过 Rules / Skills 尽量减少该行为，但不把这一 UX 问题单独作为 Patch Release 阻塞条件。

---

## 27. Source Maintenance

Golden Repository 独立维护。

更新流程：

```text
Golden Change
        ↓
Golden Review
        ↓
Golden Commit
        ↓
Update DevKit gitlink
        ↓
DevKit Release
```

发布后的 DevKit 不跟随 Golden `main` 自动变化。

`.gitmodules` 中 Golden authoritative remote 保持：

```text
https://codeup.aliyun.com/60d04cfaccca0c526834b7ad/AI_Projects/windchill-customization-reference.git
```

GitHub Repository 仅可作为 Mirror / Inspection Source。

---

## 28. Security

不得向 Repository 或 Plugin ZIP 写入：

```text
Password
Token
Cookie
Private Key
License Key
Customer Credential
```

Golden Git Authentication 由：

```text
Developer Credential
CI Credential
SSH Agent
Release Machine
```

负责。

普通 Plugin 用户不需要 Golden Git 权限。

---

## 29. Release Definition

### 1.0.0

1.0.0 表示：

```text
Rules 可用
QMind Router 可用
Golden Reference 可用
Project Context 可用
QMind Retrieve Contract Guard 可用
Packaging Baseline 可固定
```

### 1.0.1

1.0.1 在 1.0.0 基础上增加：

```text
Golden Quality-first Evidence Budget
Reference Sufficiency Gate
Golden Source-read Optimization
```

它不表示：

```text
自动 Javadoc API Verification 已可用
全部 Golden 已 Approved
所有 Windchill 场景已 Runtime Verified
```

---

## 30. Roadmap

后续优先方向：

```text
Javadoc Exact API Lookup Runtime
Cross-platform Runtime Packaging
更多 Golden Approved Reference
Automated Regression
更稳定的 Silent Orchestration
Project-level Build Integration
```

Javadoc API Lookup 将在 Runtime Distribution Strategy 明确后进入后续版本。

---

## 31. Release Versioning

Release 使用 Semantic Version：

```text
MAJOR.MINOR.PATCH
```

已冻结：

```text
v1.0.0
```

当前开发版本：

```text
1.0.1
```

1.0.1 只有在：

```text
Packaging Passed
Installation Smoke Passed
Functional Quality Passed
Performance Regression Passed
```

后才创建：

```text
v1.0.1
```

DevKit Release 同时固定：

```text
DevKit Commit SHA
Golden Commit SHA
Plugin ZIP SHA-256
Git Tag
```