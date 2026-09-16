---
name: qmind-enterprise-router
description: >
  企业 QMind 产品知识路由技能。用于确认 PTC Windchill、XWorks、MPMLink、ProjectLink、
  安装部署、升级、Bulk Migrator、功能应用和二次开发中的 Product / Framework Behavior、
  生命周期、配置机制、版本差异和官方扩展语义。对于“怎么实现、给代码、Code Review、
  Debug”等 Windchill-specific 工程任务，本 Skill 只负责产品事实，不负责替代 Golden
  Reference 的实现模式选择，也不替代 Javadoc/API Lookup 的精确 API Metadata 验证。
  Agent 应自主判断是否需要 QMind，用户无需显式要求查询 QMind 或 PTC 文档。
version: 1.2.1
---

# QMind Enterprise Knowledge Router

## 1. 职责边界

本 Skill 是企业 QMind 的产品知识路由层。

职责：

1. 判断当前任务是否需要 Product / Framework Knowledge；
2. 从 `references/qmind-registry.md` 选择匹配知识库；
3. 构造针对当前事实缺口的 Query；
4. 调用官方 QMind Knowledge Base Skill；
5. 判断检索结果具体证明了什么；
6. 将未覆盖的 Evidence Type 交回 Golden / API Lookup / Build / Runtime。

用户无需在 Prompt 中显式要求：

```text
查询 QMind
查询 PTC Guide
查询企业知识库
使用 qmind-enterprise-router
```

QMind 主要回答：

```text
Windchill / XWorks 本身是什么？
Framework 怎么工作？
某个产品机制、生命周期、配置或行为是什么？
```

QMind 不主要回答：

```text
我们这类代码应该采用哪个工程实现模式？
```

这个问题优先属于：

```text
Golden Reference
```

QMind 也不负责精确确认：

```text
Class
Method
Signature
Supported
Extendable
Deprecated
Type hierarchy
Implemented interfaces
```

这些优先属于：

```text
Target-version Javadoc
/
API Lookup
```

---

# 2. Knowledge Boundary

## 2.1 Development Decision

规范性优先级：

1. Project Rules / `AGENTS.md`
2. Approved ADR / Exception
3. Enterprise Rules
4. Approved Golden Reference
5. Candidate Golden Reference
6. Existing Project Code
7. Model Knowledge

QMind 中的产品资料不能覆盖企业明确的开发约束。

## 2.2 Framework / Product Behavior

例如：

- Validation Phase；
- Event 语义；
- Wizard 客户端行为；
- DataUtility Framework lifecycle；
- Workflow；
- Queue；
- XCONF；
- 产品配置；
- 官方 Extension Point；
- 安装部署；
- 升级和迁移。

优先依据：

```text
Target-version PTC Official Documentation
+
Enterprise-reviewed QMind
```

## 2.3 Exact API Metadata

例如：

- Class 是否存在；
- Method 是否存在；
- Signature；
- Return；
- Throws；
- Supported；
- Extendable；
- Deprecated；
- Class hierarchy；
- Implemented interface；
- Versioned / Iterated / Workable 等类型能力。

优先：

```text
Target-version Javadoc
/
windchill-api-lookup
```

QMind 中出现 API 示例可以作为线索，但不能自动把 Exact API Metadata 标记为 VERIFIED。

---

# 3. Mandatory Silent Operation

QMind Router、Registry 选择、Knowledge Base 调用和 Query 改写都是内部过程。

**调用本 Skill 或 QMind Knowledge Base 前，不得发送用户可见的进度说明。**

禁止：

```text
我先调用企业知识路由技能
我先读取注册表
根据注册表我准备查询 ptc-xxx
我先查一下官方指南
我已经找到结果，再继续看看 Golden
```

Agent 应：

```text
直接调用内部能力
        ↓
完成必要证据收集
        ↓
第一个用户可见文本直接回答用户问题
```

只有以下情况可以中断并对用户说话：

- 需要关键澄清；
- 需要用户授权；
- Tool / Skill 失败且影响最终答案；
- 用户明确要求查看检索过程；
- 用户正在诊断 Router 本身。

最终答案中可以简洁说明最终依据，但不要输出检索流水。

---

# 4. Router Rules

## Rule 1 — Router 先选库

不得要求 QMind 自动搜索所有 Notebook。

必须先读取：

```text
references/qmind-registry.md
```

再选择：

```text
notebook_name
notebook_id
query
```

如果 QMind Skill 不支持结构化参数，明确指定目标 Notebook。

不得猜测或生成不存在的 Notebook ID。

---

## Rule 2 — QMind 只解决当前 Product Knowledge Gap

调用 QMind 前应先问：

```text
当前真正缺失的是产品事实吗？
```

如果当前缺失的是：

```text
Implementation Pattern
```

应交给：

```text
Golden Reference
```

如果当前缺失的是：

```text
Exact API Metadata
```

应交给：

```text
Javadoc / API Lookup
```

不要因为用户提到了 Windchill，就机械调用 QMind。

---

## Rule 3 — Coding Task 必须执行 Evidence Handoff

如果原始任务属于：

```text
怎么实现
怎么设计
给代码
修改代码
Code Review
Windchill-specific Debug
```

QMind 检索完成后，不得直接认为 Evidence Set Complete。

在最终回答前必须检查：

```text
Implementation Pattern needed?
        ↓
Yes
        ↓
Golden Catalog Preflight 已执行？
```

如果没有：

```text
执行 Golden Preflight
```

还必须检查：

```text
最终答案是否包含具体 PTC API / Constant /
Signature / Type Capability？
```

如果是，并且 Target-version API Lookup 可用：

```text
执行 API Verification
```

所以：

```text
QMind Search Completed
≠
Task Evidence Completed
```

---

## Rule 4 — 最小充分检索

默认：

- 1 个主知识库；
- 1 次精确 Query；
- 不足时在同一库改写 Query 再查一次；
- 仍不足才使用 fallback / 第二知识库；
- 默认最多 2 个库；
- 明确跨域时最多 3 个。

不得无差别搜索全部知识库。

---

## Rule 5 — XWorks 只在明确命中时优先

任务明确出现：

```text
XWorks
xworks
x-works
```

或 Project Context：

```text
XWorks Enabled: true
```

且任务属于 XWorks 实现范围时，优先：

```text
ptc-winidchill-dev-xworks
```

需要 Windchill OOTB 底层产品事实时，可追加：

```text
ptc-windchill-dev-general
```

如果：

```text
XWorks Enabled: false
```

XWorks 知识最多用于理解设计概念，不得据此证明当前技术栈存在等价：

- PTC Class
- Method
- Status
- Hook
- Framework Behavior

---

## Rule 6 — 区分功能应用与二次开发

功能 / 业务问题优先：

```text
training-*
```

例如：

- UI 怎么使用；
- MPMLink / ProjectLink 业务语义；
- 功能操作流程。

开发 / 客制化产品知识优先：

```text
dev-*
```

例如：

- JCA / MVC Framework；
- Validator Framework；
- Event / Service；
- WRS / OData；
- Workflow customization；
- XCONF。

实现代码模式仍应检查 Golden。

---

## Rule 7 — 版本信息进入 Query

已知目标版本时，例如：

```text
13.0.2
13.1.2.0
2027.0.0.0
```

必须写入检索 Query。

优先选择注册表中版本适配更明确的知识库。

其他版本资料只能作为线索，不能静默当成当前版本事实。

版本未知且会实质改变结论时，应优先从 Project Context 获取。

只有无法获取且确实阻塞结论时才向用户追问。

---

## Rule 8 — Query 必须针对事实缺口

不要简单复制用户整段 Prompt。

Query 应包含：

- Product / Module；
- Object；
- Technical Topic；
- Goal；
- Windchill Version；
- 需要确认的 Product Fact。

例如：

```text
PTC Windchill 13.1.2.0
DataUtility setModelData lifecycle and cardinality behavior;
confirm framework lifecycle semantics, not implementation code.
```

而不是：

```text
帮我优化 DataUtility。
```

如果缺失的是精确 Method Signature，不要扩大 QMind Query，应转到 API Lookup。

---

## Rule 9 — Query 必须脱敏

不得发送无必要的：

- Password
- Token
- Cookie
- Private Key
- License Key
- Customer Personal Data
- Customer Credential
- 与事实检索无关的大段专有源码

保留技术语义，移除敏感值。

---

# 5. Routing Algorithm

## Step 1 — Identify Knowledge Gap

先判断：

```text
当前缺失的是：

Product Behavior?
Framework Contract?
Configuration?
Lifecycle?
Version Difference?
Installation / Upgrade / Migration?
```

如果都不是：

```text
不要机械调用 QMind
```

## Step 2 — Read Registry

读取：

```text
references/qmind-registry.md
```

只允许选择已登记 Knowledge Base。

如果 Entry 提供：

- versions
- authority
- status
- owner
- last_verified
- fallback
- combine_with

则应参与判断。

`deprecated` 不作为默认主库。

## Step 3 — Select Notebook

顺序：

1. 用户明确指定且已登记；
2. strong_match；
3. 专用产品 / 模块；
4. Task Type；
5. Version；
6. General fallback。

同等条件：

```text
专用 > 通用
版本精确 > 版本未知
active > deprecated
```

## Step 4 — Build Query

Query 应准确描述当前 Product Knowledge Gap。

例如：

```text
PTC Windchill 13.1.2.0
PersistenceManagerEvent event notification and veto semantics;
confirm whether vetoability is determined by PRE/POST naming or by
specific event/callback contract.
```

## Step 5 — Invoke QMind

传递：

```text
notebook_name
notebook_id
query
```

如果官方 QMind Skill 无法调用：

```text
不得模拟结果
```

## Step 6 — Validate Evidence

检查：

- 来源是否正确；
- Version 是否匹配；
- 是否真正回答当前事实；
- 是否存在跨版本内容；
- 它证明的是 Product Behavior 还是仅提供代码示例；
- 是否仍然存在 Golden / API Metadata 缺口。

内部证据状态：

```text
VERIFIED
PARTIAL
UNVERIFIED
```

这些状态针对具体事实，不针对整个文档。

---

# 6. Evidence Handoff

QMind 完成后必须执行 Handoff Check。

## Implementation Pattern

如果任务需要：

```text
实现
设计
代码
Code Review
Debug
```

检查：

```text
Golden Catalog Preflight 是否已完成？
```

没有则完成后再回答。

## Exact API

如果最终答案包含：

```text
PTC Class
Method
Constant
Signature
Supported
Extendable
Deprecated
Type capability
```

检查：

```text
Target-version API verification 是否需要且可执行？
```

可执行则实际执行。

不可执行则标记：

```text
UNVERIFIED PTC API
```

## Compile

QMind 不证明：

```text
Compile Verified
```

## Runtime

QMind 不证明：

```text
Runtime Verified
```

---

# 7. Coding / Review 特殊规则

Windchill Coding / Review 中：

1. 使用 Rules 确认必须 / 不得做什么；
2. 用 Project Context 理解当前项目；
3. 用 Golden 选择实现模式；
4. 用 QMind / Official Docs 确认产品行为；
5. 用 Javadoc / API Lookup 确认 Exact API Metadata；
6. 用 Build 验证编译；
7. 用 Runtime 验证真实行为。

不得让任一单一证据源替代全部其他证据类型。

尤其不得：

```text
读了 Guide
→ 就直接补齐所有工程实现细节
```

也不得：

```text
看了 Golden
→ 就把 API Supported 状态当成已验证
```

---

# 8. Failure and Degradation

## No matching QMind

如果没有匹配知识库：

- 不随意选无关库；
- 可以继续使用 Rules / Golden / Project Context；
- Product Fact 无法证明时标记 UNVERIFIED。

## No permission

只使用 Registry 定义的 fallback。

不要自动切换无关知识库。

## QMind unavailable

- 不模拟检索；
- 不编造官方资料；
- Pattern 问题仍可使用 Golden；
- Exact API 可使用 API Lookup；
- Product / Framework Fact 保持 UNVERIFIED。

## Conflict with Project Code

先判断：

- Project exception；
- Version difference；
- XWorks difference；
- Technical debt；
- Outdated knowledge；
- Product Fact vs Engineering Preference。

不得默认复制当前代码。

---

# 9. User-visible Result

正常用户应该看到：

```text
问题
    ↓
直接结论 / 方案 / 代码
```

而不是：

```text
问题
    ↓
我先调用 QMind
    ↓
我先读取 Registry
    ↓
我查到一个文档
    ↓
我再看看 Golden
    ↓
最终答案
```

如果需要可追溯性，最终答案中可以简洁说明：

```text
依据：PTC Windchill 13.1.2.0 Customization Guide
```

普通开发任务不要求机械附带：

```text
知识来源：ptc-xxx
```

用户没有必要知道内部 Notebook ID 或 Tool 调用顺序。

---

# 10. Extension Principle

新增 QMind 时优先只修改：

```text
references/qmind-registry.md
```

不要为了增加一个 Knowledge Base 修改 Router 算法。

只有新增全局行为时才修改本文件，例如：

- 新 Product；
- 新的 Evidence Type；
- 新 Authority Level；
- 新 Security Requirement；
- 新 Evidence Handoff 规则；
- 新 User-visible Orchestration Policy。