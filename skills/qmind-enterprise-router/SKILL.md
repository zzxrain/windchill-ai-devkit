---
name: qmind-enterprise-router
description: >
  企业 QMind 产品知识路由技能。用于确认 PTC Windchill、XWorks、MPMLink、ProjectLink、
  安装部署、升级、Bulk Migrator、功能应用和二次开发中的 Product / Framework Behavior、
  生命周期、配置机制、版本差异和官方扩展语义。对于“怎么实现、给代码、Code Review、
  Debug”等 Windchill-specific 工程任务，本 Skill 只负责产品事实，不负责替代 Golden
  Reference 的实现模式选择，也不替代目标版本 Javadoc 的精确 API Metadata 验证。
  Agent 应自主判断是否需要 QMind，用户无需显式要求查询 QMind 或 PTC 文档。
version: 1.2.2
---

# QMind Enterprise Knowledge Router

## 1. 职责边界

本 Skill 是企业 QMind 的产品知识路由层。

职责：

1. 判断当前任务是否需要 Product / Framework Knowledge；
2. 从 `references/qmind-registry.md` 选择匹配知识库；
3. 获取该知识库已经登记的精确 Notebook ID；
4. 构造针对当前事实缺口的 Question；
5. 使用实际 QMind Tool Contract 调用知识库；
6. 判断检索结果具体证明了什么；
7. 将未覆盖的 Evidence Type 交回 Golden / Project / Build / Runtime。

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

QMind 也不等同于目标版本精确 API Metadata 验证。

例如：

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

如果当前没有可靠的目标版本 Javadoc / API Evidence，应按项目 Rules 标记：

```text
UNVERIFIED PTC API
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

QMind 中出现 API 示例可以作为线索，但不能自动把 Exact API Metadata 标记为 VERIFIED。

Windchill AI DevKit 1.0.0 MVP 不内置 Javadoc API Lookup Runtime。

因此缺少目标版本精确证据时，应按照 `20-windchill-api.md` 降级为：

```text
UNVERIFIED PTC API
```

---

# 3. Mandatory Silent Operation

QMind Router、Registry 选择、Question 构造和 Knowledge Base 调用都是内部过程。

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
直接执行内部调用
        ↓
完成必要证据收集
        ↓
第一个用户可见文本直接回答用户问题
```

只有以下情况可以中断并对用户说话：

- 需要关键澄清；
- 需要用户授权；
- Tool / Skill 失败且无法恢复并影响最终答案；
- 用户明确要求查看检索过程；
- 用户正在诊断 Router 本身。

最终答案中可以简洁说明最终依据，但不要输出内部检索流水。

---

# 4. QMind Runtime Tool Contract

这是本 Router 调用 QMind 时必须遵守的 Runtime Contract。

当前 Qoder QMind `retrieve` Tool 要求至少传递：

```text
notebookId
question
```

Registry 与 Tool 参数的映射必须是：

```text
Registry Entry
    id
     │
     ▼
QMind retrieve
    notebookId
```

以及：

```text
Router constructed query
     │
     ▼
QMind retrieve
    question
```

## 正确调用形态

```json
{
  "notebookId": "01a07fe9-9132-71b5-8eb6-258b8e2bbe6a",
  "question": "PTC Windchill 13.1.2.0 PersistenceManagerEvent event notification and veto semantics; confirm PRE/POST phase semantics, transaction relationship, rollback behavior, and notifyVetoableEvent contract."
}
```

这里的 Notebook ID 必须来自：

```text
references/qmind-registry.md
```

不得根据 Notebook Name 自行构造 UUID。

## 禁止的参数名称

不得把 Router 内部概念直接作为 Tool 参数发送：

```text
notebook_name
notebook_id
query
```

除非未来实际 Tool Schema 明确要求这些字段。

当前 Runtime Contract 中应使用：

```text
notebookId
question
```

## Notebook Name 的用途

Registry 中：

```text
name
```

用于：

- Router 可读性；
- 日志和内部判断；
- Registry Entry 校验；
- fallback / combine_with 关系。

它不是当前 `retrieve` Tool 的必需定位参数。

实际 Tool 定位使用：

```text
notebookId
```

---

# 5. Router Rules

## Rule 1 — Router 先选库

不得要求 QMind 自动搜索所有 Notebook。

必须先读取：

```text
references/qmind-registry.md
```

选择一个具体 Registry Entry，并取得：

```text
name
id
```

其中：

```text
id
```

必须非空。

在调用 QMind Tool 前必须转换为：

```text
notebookId = Registry.id
```

不得调用：

```json
{
  "question": "..."
}
```

而缺少：

```text
notebookId
```

也不得猜测或生成不存在的 Notebook ID。

---

## Rule 2 — QMind Tool 调用前必须做 Parameter Preflight

每次调用 `retrieve` 前，内部检查：

```text
Selected Registry Entry exists?
        ↓
Registry.id exists and is non-empty?
        ↓
question exists and is non-empty?
        ↓
Build Tool Parameters
        ↓
retrieve
```

最小参数必须满足：

```text
notebookId != empty
question != empty
```

如果 Registry Entry 没有 ID：

```text
不要调用 retrieve
```

应将该 Knowledge Source 标记为当前不可调用，而不是只发送 question。

---

## Rule 3 — Tool Parameter Validation Error 允许修正后重试一次

如果 QMind Tool 返回类似：

```text
tool parameter validation failed
required property 'notebookId'
```

这表示：

```text
Tool Contract Error
```

而不是：

```text
QMind Knowledge Base unavailable
QMind 中没有答案
Notebook 不存在
```

Agent 应：

1. 回到已经选择的 Registry Entry；
2. 读取它的 `id`；
3. 使用：

```text
notebookId
question
```

重新构造参数；
4. 重试一次。

不得在缺失 `notebookId` 的情况下重复同一个错误调用。

如果使用正确参数后仍失败，再进入 Failure / Degradation。

---

## Rule 4 — QMind 只解决当前 Product Knowledge Gap

调用 QMind 前应判断：

```text
当前真正缺失的是产品事实吗？
```

如果缺失的是：

```text
Implementation Pattern
```

应交给：

```text
Golden Reference
```

如果缺失的是：

```text
Exact API Metadata
```

而当前又没有目标版本可靠 API Evidence：

```text
遵守 20-windchill-api.md
→ UNVERIFIED PTC API
```

不要因为用户提到了 Windchill，就机械调用 QMind。

---

## Rule 5 — Coding Task 必须执行 Evidence Handoff

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
最终答案是否包含具体 PTC API /
Constant / Signature / Type Capability？
```

如果是，但目标版本 API Metadata 没有可靠证据：

```text
UNVERIFIED PTC API
```

所以：

```text
QMind Search Completed
≠
Task Evidence Completed
```

---

## Rule 6 — 最小充分检索

默认：

- 1 个主知识库；
- 1 次精确 Question；
- 不足时在同一库改写 Question 再查一次；
- 仍不足才使用 fallback / 第二知识库；
- 默认最多 2 个库；
- 明确跨域时最多 3 个。

不得无差别搜索全部知识库。

每增加一个 Knowledge Base，都必须重新从 Registry 取得对应：

```text
id
→ notebookId
```

不能复用上一 Notebook 的 ID。

---

## Rule 7 — XWorks 只在明确命中时优先

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

其 Registry ID 必须转换为：

```text
notebookId
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

- PTC Class；
- Method；
- Status；
- Hook；
- Framework Behavior。

---

## Rule 8 — 区分功能应用与二次开发

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

## Rule 9 — 版本信息进入 Question

已知目标版本时，例如：

```text
13.0.2
13.1.2.0
2027.0.0.0
```

必须写入：

```text
question
```

优先选择 Registry 中版本适配更明确的知识库。

其他版本资料只能作为线索，不能静默当成当前版本事实。

版本未知且会实质改变结论时，应优先从 Project Context 获取。

只有无法获取且确实阻塞结论时才向用户追问。

---

## Rule 10 — Question 必须针对事实缺口

不要简单复制用户整段 Prompt。

Question 应包含：

- Product / Module；
- Object；
- Technical Topic；
- Goal；
- Windchill Version；
- 需要确认的 Product Fact。

例如：

```text
PTC Windchill 13.1.2.0
PersistenceManagerEvent PRE_STORE / PRE_UPDATE / POST_STORE /
POST_UPDATE semantics; ServiceEventListenerAdapter
notifyVetoableEvent veto contract; whether thrown WTException can
rollback the current transaction and prevent the operation; whether
event notification executes inside the emitter transaction.
```

而不是：

```text
帮我写 Listener。
```

如果缺失的是精确 Method Signature，不要把 QMind 检索结果自动视为 Exact API Verification。

---

## Rule 11 — Question 必须脱敏

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

# 6. Routing Algorithm

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

读取选中 Entry 的：

```text
name
id
product
category
scope
priority
versions
authority
status
fallback
combine_with
```

不存在的可选字段按未知处理。

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

## Step 4 — Resolve Notebook ID

从选中 Registry Entry 获取：

```text
id
```

例如：

```text
name:
ptc-windchill-dev-general

id:
01a07fe9-9132-71b5-8eb6-258b8e2bbe6a
```

转换：

```text
notebookId =
01a07fe9-9132-71b5-8eb6-258b8e2bbe6a
```

不得跳过该步骤。

## Step 5 — Build Question

Question 应准确描述当前 Product Knowledge Gap。

例如：

```text
PTC Windchill 13.1.2.0
PersistenceManagerEvent event notification and veto semantics;
confirm PRE/POST phase semantics, transaction relationship,
rollback behavior and notifyVetoableEvent contract.
```

## Step 6 — Invoke QMind

当前 `retrieve` Tool 最小调用参数：

```json
{
  "notebookId": "<Registry.id>",
  "question": "<constructed product question>"
}
```

不要使用：

```json
{
  "notebook_id": "...",
  "query": "..."
}
```

也不要只发送：

```json
{
  "question": "..."
}
```

如果实际 QMind Tool Schema 后续发生变化，应以 Runtime 返回的 Tool Schema / Validation Error 为准更新本 Skill，而不是继续沿用旧参数名称。

## Step 7 — Validate Evidence

检查：

- 是否实际检索了预期 Notebook；
- 来源是否正确；
- Version 是否匹配；
- 是否真正回答当前事实；
- 是否存在跨版本内容；
- 它证明的是 Product Behavior 还是仅提供代码示例；
- 是否仍然存在 Golden / Exact API Metadata 缺口。

内部证据状态：

```text
VERIFIED
PARTIAL
UNVERIFIED
```

这些状态针对具体事实，不针对整个文档。

---

# 7. Evidence Handoff

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

而当前没有目标版本可靠 API Evidence：

```text
UNVERIFIED PTC API
```

不得因为 QMind 文档中出现某个 Symbol，就自动描述成 Exact API Verified。

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

# 8. Coding / Review 特殊规则

Windchill Coding / Review 中：

1. 使用 Rules 确认必须 / 不得做什么；
2. 用 Project Context 理解当前项目；
3. 用 Golden 选择实现模式；
4. 用 QMind / Official Docs 确认产品行为；
5. 对无法精确确认的 API 按 Rules 标记 `UNVERIFIED PTC API`；
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

# 9. Failure and Degradation

## Parameter validation failed

如果出现：

```text
tool parameter validation failed
```

首先判断是否是 Tool Contract 问题。

例如：

```text
params must have required property 'notebookId'
```

处理：

```text
Registry.id
→ notebookId

constructed query
→ question
```

修正参数后重试一次。

这种错误不能被解释成：

```text
Knowledge Base 没有答案
Notebook 无权限
QMind 不可用
```

## No matching QMind

如果没有匹配知识库：

- 不随意选无关库；
- 可以继续使用 Rules / Golden / Project Context；
- Product Fact 无法证明时标记 UNVERIFIED。

## Registry Entry without ID

如果选中的 Registry Entry 没有合法 `id`：

```text
不要调用 retrieve
```

应把该 QMind Source 标记为配置错误。

不得只传：

```text
question
```

继续调用。

## No permission

只使用 Registry 定义的 fallback。

不要自动切换无关知识库。

每次切换 fallback 都必须重新解析它自己的：

```text
Registry.id
→ notebookId
```

## QMind unavailable

使用正确：

```text
notebookId
question
```

仍然调用失败后，才考虑 QMind 当前不可用。

此时：

- 不模拟检索；
- 不编造官方资料；
- Pattern 问题仍可使用 Golden；
- Exact API 未确认时使用 `UNVERIFIED PTC API`；
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

# 10. User-visible Result

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

如果第一次 QMind 调用因为 Tool 参数错误而被内部修正并重试成功：

```text
不需要向用户直播第一次参数错误
```

除非：

- 用户正在调试 DevKit；
- 重试仍然失败；
- 失败直接影响最终结论。

如果需要可追溯性，最终答案中可以简洁说明：

```text
依据：PTC Windchill 13.1.2.0 Customization Guide
```

普通开发任务不要求机械附带：

```text
Knowledge Base Name
Notebook ID
Tool Parameters
```

用户没有必要知道内部 Notebook ID 或 Tool 调用顺序。

---

# 11. Extension Principle

新增 QMind 时优先只修改：

```text
references/qmind-registry.md
```

不要为了增加一个 Knowledge Base 修改 Router 算法。

只有新增全局行为时才修改本文件，例如：

- QMind Runtime Tool Contract 变化；
- 新 Product；
- 新 Evidence Type；
- 新 Authority Level；
- 新 Security Requirement；
- 新 Evidence Handoff 规则；
- 新 User-visible Orchestration Policy。

如果 QMind Runtime 参数名称发生变化：

```text
必须修改本 Skill 的 Runtime Tool Contract
```

不得要求每个 Registry Entry 重复维护 Tool Parameter Name。