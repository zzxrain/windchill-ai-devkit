# Windchill AI DevKit

Windchill AI DevKit 是面向公司内部 PTC Windchill 二次开发的 Qoder Plugin。

当前版本：

```text
1.0.0
```

发布定位：

```text
MVP
```

1.0.0 的重点不是让 AI 记住全部 Windchill，而是为 Windchill 二次开发建立一套可复用的：

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

让开发人员可以直接用自然语言描述实际开发任务，而不需要先理解 DevKit 内部组件。

---

## 1. 1.0.0 MVP Scope

1.0.0 包含：

```text
Windchill Development Rules
QMind Enterprise Router
Golden Reference
Project Context Template
Autonomous Evidence Routing
Packaging / Release Baseline
```

1.0.0 不包含：

```text
Javadoc API Lookup Runtime
MCP Runtime
Python Runtime
Automatic Target-version API Index
Automatic Compile Verification
Automatic Windchill Runtime Verification
```

`tools/windchill-api-lookup` 可以继续作为后续研发源码保留在 Source Repository 中，但不会进入 1.0.0 Plugin ZIP，也不会由 Plugin 自动启动。

---

## 2. Goals

Windchill AI DevKit 主要用于降低以下问题：

- AI 编造 PTC API；
- AI 混淆 Version / Iteration / Working Copy；
- AI 机械复制历史低质量代码；
- Query / Transaction / Security / Event / Queue 等实现不一致；
- 不同项目 Windchill Version 和技术栈差异；
- XWorks 与标准 Windchill Framework 被错误混用；
- Framework Behavior 与 Engineering Inference 被混为一谈；
- Golden Reference、官方资料和当前项目代码之间没有明确权威边界；
- AI 声称完成实际并未执行的 Compile / Runtime Verification。

---

## 3. 1.0.0 Architecture

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
| QMind Router | 获取 Windchill / XWorks 产品和 Framework 知识 |
| Golden Reference | 提供 Candidate / Approved 实现模式 |
| AGENTS.md | 描述当前项目事实和项目例外 |
| Project Code | 提供兼容性和调用上下文 |
| Build | 真实目标 Classpath 编译验证 |
| Runtime | 真实 Windchill 行为验证 |

这些能力不能机械互相替代。

---

## 4. Evidence Model

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
Event semantics
Wizard behavior
DataUtility lifecycle
Transaction behavior
Queue behavior
Workflow behavior
Configuration mechanism
```

优先：

```text
Target-version PTC Official Documentation
/
Enterprise QMind
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

1.0.0 MVP 不提供自动 Javadoc API Lookup Runtime。

如果当前任务没有足够的目标版本证据，Agent 应：

```text
UNVERIFIED PTC API
```

而不是猜测。

---

## 5. Repository Structure

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

属于 Source Repository 中保留的后续研发代码，不属于 1.0.0 Plugin Runtime。

---

## 6. Rules

核心 Rules：

| Rule | Scope |
|---|---|
| `00-core-development-rules.md` | 基础规则、Evidence Plan、验证边界 |
| `10-java.md` | Java 工程规则 |
| `20-windchill-api.md` | PTC API 使用与 MVP 降级策略 |
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

## 7. Project Context

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

## 8. XWorks Policy

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

## 9. QMind Enterprise Router

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

Agent 根据当前知识缺口自主判断是否需要使用。

QMind 不替代：

```text
Rules
Golden Reference
Project Context
Compile Verification
Runtime Verification
```

---

## 10. Golden Reference

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

## 11. Golden Reference Status

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

## 12. Golden Selection

Windchill-specific Implementation / Design / Review / Debug 默认执行 Golden Catalog Preflight。

内部逻辑：

```text
Need Implementation Pattern?
        ↓
Read CATALOG
        ↓
Strong Match?
   ├── No → Stop
   └── Yes
        ↓
Select Minimum Sufficient Reference
        ↓
Read reference.md
        ↓
Read src/* only when necessary
```

如果一个 Reference 已完整覆盖场景，不应为了数量再增加泛化 Reference。

---

## 13. Autonomous Evidence Orchestration

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

Agent 内部应按需选择证据。

---

## 14. Silent Orchestration

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

受当前 Qoder Agent Runtime 行为影响，极少数情况下仍可能出现内部检索进度文本。

对于 1.0.0 MVP，这属于已知 UX 限制，不代表某项技术事实因此完成验证。

---

## 15. API Verification Policy

1.0.0 不启用自动 Javadoc API Lookup。

因此如果无法从当前可用证据确认某个 PTC API：

```text
UNVERIFIED PTC API
```

Agent 应优先：

```text
给出 Pattern-level 方案
+
指出需要确认的 API 点
```

而不是：

```text
凭模型记忆补齐 Package / Method / Constant
```

对于需要最终投产的代码，仍必须在目标 Windchill Classpath 上完成实际 Build。

---

## 16. Compile Verification

以下内容都不能代替真实编译：

```text
Golden Reference
PTC Guide Example
Java Syntax
Static Analysis
Model Confidence
```

Compile Verification 必须来自目标 Windchill Classpath。

如果 Agent 无法执行项目 Build：

```text
未完成 Compile Verification
```

---

## 17. Runtime Verification

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

---

## 18. Packaging

构建 Plugin：

```bash
./scripts/package-plugin.sh
```

输出：

```text
dist/
├── windchill-ai-devkit-1.0.0.zip
└── windchill-ai-devkit-1.0.0.zip.sha256
```

Packaging 使用：

```text
Committed DevKit HEAD
+
Pinned Golden Commit
```

生成可复现 Release Package。

---

## 19. Plugin ZIP Boundary

1.0.0 ZIP 包含：

```text
.qoder-plugin/
rules/
skills/qmind-enterprise-router/
skills/windchill-golden-reference/
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

## 20. Installation

将：

```text
windchill-ai-devkit-1.0.0.zip
```

安装到公司使用的 Qoder / Qoder CN 环境。

安装后至少确认：

```text
Plugin Version = 1.0.0
Rules 可发现
QMind Router 可发现
Golden Reference Skill 可发现
Golden CATALOG / references 可读取
```

---

## 21. MVP Known Limitations

### Exact API Verification

1.0.0 没有自动 Javadoc API Lookup Runtime。

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

1.0.0 继续通过 Rules / Skills 尽量减少该行为，但不把这一 UX 问题作为 MVP 发布阻塞条件。

---

## 22. Source Maintenance

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

---

## 23. Security

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

## 24. 1.0.0 MVP Release Definition

1.0.0 表示：

```text
Rules 可用
QMind Router 可用
Golden Reference 可用
Project Context 模型可用
Packaging 可重复
Release Baseline 可固定
```

不表示：

```text
所有 PTC API 已自动验证
全部 Golden 已 Approved
所有 Windchill 场景已 Runtime Verified
```

---

## 25. Roadmap

后续优先方向：

```text
API Lookup Runtime packaging
Python-free / Standalone API Lookup
更多 Golden Approved Reference
Automated Regression
更稳定的 Silent Orchestration
Project-level Build Integration
```

Javadoc API Lookup 将在 Runtime / Python 分发策略明确后重新进入 Plugin Runtime。

---

## 26. Release Versioning

Release 使用 Semantic Version：

```text
MAJOR.MINOR.PATCH
```

首个内部 MVP Release：

```text
1.0.0
```

Release Commit 通过 Git Tag 固定：

```text
v1.0.0
```

DevKit Release 同时固定：

```text
DevKit Commit SHA
Golden Commit SHA
Plugin ZIP SHA-256
Git Tag
```