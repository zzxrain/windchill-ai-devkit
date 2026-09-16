---
trigger: model_decision
description: 当任务涉及 PTC Windchill Java API、wt.*、com.ptc.*、Windchill Service/Helper/Manager、继承 PTC 类、调用 Windchill 平台能力，或需要判断 Windchill 类型的继承、接口、Versioned、Iterated、Workable 等能力时应用本规则。
---

# Windchill API 使用规则

## 1. 1.0.0 MVP API Verification Boundary

Windchill AI DevKit 1.0.0 MVP 不内置：

```text
windchill-api-lookup Runtime
Javadoc MCP Server
Python Runtime
自动 Javadoc Index
```

因此 Agent 不得假装已经执行：

```text
API Lookup
Javadoc Index Query
Target-version Exact API Verification
```

如果当前 Qoder / Project Context 本身提供了可直接读取的目标版本官方 Javadoc 或其他可靠 API 证据，可以使用。

否则精确 PTC API Metadata 必须保持：

```text
UNVERIFIED PTC API
```

1.0.0 的目标是：

```text
宁可明确未验证
也不要生成一个看起来完整但实际错误的 PTC API。
```

---

## 2. 不得猜测 PTC API

涉及 Windchill 专有 API 时，不得仅依据模型记忆、类名习惯或历史代码猜测：

- Class
- Interface
- Method
- Constructor
- Method Signature
- Constant
- Service
- Helper
- Manager
- Extension Point
- Package Name

同样不得仅靠名称猜测某个 PTC 类型：

- 继承哪个父类
- 实现哪些 Interface
- 是否 Versioned
- 是否 Iterated
- 是否 Workable
- 是否 Mastered
- 是否支持某种 Windchill 平台能力

无法确认时必须明确标记：

```text
UNVERIFIED PTC API
```

不得把推测结果作为已经确认的产品事实。

---

## 3. 未验证 API 不得伪装成最终可编译代码

如果实现方案需要某个尚未验证的 PTC API，优先选择以下方式之一。

### Pattern-level Answer

能够只解释设计模式时，优先只给：

```text
Class / Service / Callback 应承担什么职责
数据流如何组织
事务和安全边界如何设计
哪些 API 需要在项目中确认
```

不要为了让答案看起来完整而发明具体 Method。

### Grounded Code

只有某个 Symbol 已直接得到以下任一可靠来源支持时：

```text
目标版本官方文档
当前项目已确认代码
Golden Reference 中明确存在的实现
当前可读取的目标版本 Javadoc
```

才可以把该 Symbol 作为实现依据。

即便如此，也必须尊重该来源能够证明的边界。

Golden 中出现 Method：

```text
不自动证明 Supported / Deprecated 状态。
```

Guide 中出现示例：

```text
不自动证明完整 API Metadata。
```

### Illustrative Code

如果确实需要展示结构但其中仍含未确认 PTC API，必须明确标记：

```text
示意代码 — UNVERIFIED PTC API
```

并且未验证部分不得伪装成已经知道精确调用形式的 Java API。

如果尚未确认：

```text
Method Signature
Constructor Signature
Parameter Count
Parameter Type
Return Type
Throws
Overload
```

则不得输出类似：

```java
SomePtcClass.someMethod(arg1, arg2);
```

这种具有“可直接编译”外观的精确调用。

应改成 Pattern-level 或明显不可编译的占位表达，例如：

```text
<调用目标版本已验证的 Event Key API>
<调用目标版本已验证的 Persistence API>
<使用目标版本已验证的 Callback Signature>
```

或者：

```java
// Pseudocode — exact PTC API signature must be verified
registerListener(listener, VERIFIED_EVENT_KEY);
```

不得用：

```text
在答案末尾补一句 UNVERIFIED PTC API
```

来合理化正文中未经验证的具体：

```text
Method Signature
Constructor
Overload
Parameter List
Return Type
```

如果精确 API 是代码能否成立的关键条件，而当前无法验证，应停止在 Pattern-level。

不得把这种代码描述成：

```text
可直接编译
已按 13.1.2.0 API 验证
生产可用最终代码
```

---

## 4. API 和产品事实必须匹配目标 Windchill Version

API 是否存在、Signature、Deprecated、Supported 和 Extendable 等状态必须与目标 Windchill Version 对应。

目标版本应优先来自：

```text
Project AGENTS.md
Project Configuration
User Input
Project Documentation
```

不得根据以下内容自行猜测版本：

- Javadoc ZIP 文件名
- 其他项目
- Golden Reference
- 本机其他 API Index
- 模型记忆

其他 Windchill Version 的资料最多作为线索。

---

## 5. 必须区分 API Metadata 与 Framework Behavior

Exact API Metadata 包括：

```text
Class
Interface
Method
Constructor
Signature
Return Type
Parameters
Throws
Constant
Supported
Extendable
Deprecated
Inheritance
Implemented Interfaces
```

Framework / Product Behavior 包括：

```text
Event veto semantics
Validation Phase
Wizard interaction
DataUtility lifecycle
Transaction behavior
Queue behavior
Workflow behavior
Configuration semantics
```

二者不能互相替代。

例如：

```text
存在 PRE_STORE Constant
```

不能自动证明：

```text
PRE_STORE 一定可以 Veto
```

又例如：

```text
存在 validateFormSubmission()
```

不能仅根据 Signature 推导：

```text
PROMPT_FOR_CONFIRMATION 的完整客户端行为
```

Framework Behavior 应优先依据：

```text
目标版本 PTC 官方资料
QMind
其他受控产品知识
```

---

## 6. 不得从名称推导产品语义

尤其禁止以下推导：

```text
PRE_*
→ 一定 Vetoable

POST_*
→ 一定不可 Veto

POST_*
→ 一定已经 Commit

LATEST_ITERATION
→ 一定是最新 Revision

Number 唯一
→ 一定只有一个 Version / Iteration

Class 名称看起来像 Versioned
→ 一定实现 Versioned
```

这些都必须取得与事实类型匹配的证据。

---

## 7. 不得从业务唯一性推导版本模型

以下推导无效：

```text
业务 Number 唯一
        ↓
只有一条数据库记录
        ↓
对象不是 Versioned / Iterated
```

Windchill Business Identity 与 Version / Iteration Identity 是不同概念。

涉及：

- Master
- Revision
- Iteration
- Latest
- Working Copy

时，应遵守：

```text
35-versioning-object-semantics.md
```

不得通过：

```text
QueryResult 第一条
最后一条
OID
创建时间
普通字符串排序
```

自行推断“当前”或“最新”。

---

## 8. 优先使用 Supported API 和正式扩展点

存在合理方案时，应优先选择 PTC Supported API。

需要继承 PTC Class 时，应确认 Extendable 状态。

应优先评估 PTC 提供的：

- Service
- Helper
- Delegate
- Interface
- Builder
- Validator
- Listener
- Factory
- 正式 Extension Point

Java 能够访问某个类，不代表该类适合作为长期 Customization API。

---

## 9. Unsupported API 必须显式识别风险

实际项目确有必要使用 Unsupported API 时，可以采用，但必须：

- 明确 Unsupported 或 Unknown 状态；
- 说明为什么必须使用；
- 检查是否存在 Supported 替代；
- 提醒 Maintenance Update / Upgrade 风险。

不得把：

```text
当前可以编译
```

解释成：

```text
PTC Supported
```

---

## 10. Deprecated API 不应成为新代码默认选择

新代码遇到 Deprecated API 时，应优先寻找目标版本推荐替代方案。

但不得仅根据：

- 新版 Guide 使用了不同 API；
- 历史项目使用另一套 API；
- 名称看起来更新；
- 模型认为某写法更现代；

就宣布：

```text
旧 API 已 Deprecated
```

必须有对应证据。

---

## 11. Classpath、历史代码和 Golden 都不是 API 权威证明

以下内容可以作为实现线索：

- Project Code
- Windchill Classpath
- Golden Reference
- Legacy Project
- Guide Example
- 其他版本示例

但它们不能单独证明：

- Supported
- Extendable
- Deprecated
- 当前版本 Signature
- 升级兼容性

Golden 主要证明：

```text
Implementation Pattern
```

不是完整 API Metadata。

---

## 12. 不同 Framework 之间不能推导 API 等价

例如：

```text
XWorks optional validation
```

不能据此证明：

```text
PTC OOTB Validator
```

存在完全等价的：

- Method
- Status
- Hook
- Callback

同样：

```text
Post-select
```

不能自动推导：

```text
Post-submit
```

具有相同 Contract。

跨 Framework / Phase / Version 的结论必须独立确认。

---

## 13. 优先复用 Windchill 平台业务能力

涉及：

- Persistence
- Versioning
- Checkout / Checkin
- Lifecycle
- Workflow
- Access Control
- Content
- Structure
- Queue
- Event

时，应优先寻找 Windchill 平台对应的 Business API 或正式扩展机制。

不得仅因为若干底层 API 可以拼出结果，就绕过平台业务语义。

---

## 14. API 无法验证时的最终输出要求

如果当前 Agent 无法访问目标版本 API Verification 能力：

### 可以输出

```text
推荐实现模式
产品行为依据
Golden-derived Pattern
工程风险
需要项目确认的 API 点
Pattern-level 伪代码
```

### 不得输出为确定事实

```text
未经验证的 Package Name
未经验证的 Method Signature
未经验证的 Constructor Signature
未经验证的 Parameter List
未经验证的 Constant
未经验证的 Supported 状态
未经验证的 Type Hierarchy
未经验证的 Versioning Capability
```

如果答案必须依赖这些内容，应显式说明：

```text
UNVERIFIED PTC API
```

同时必须把未验证部分保持在 Pattern-level。

不得：

```text
先写一个具体 Java 调用
        ↓
不知道 Signature 是否正确
        ↓
最后统一写“请查 Javadoc”
```

正确方式是：

```text
Exact API 未验证
        ↓
不要构造精确调用
        ↓
给 Pattern / Placeholder
        ↓
说明需要验证的具体 Symbol
```

必要时停止在 Pattern-level，不继续伪造精确实现。

---

## 15. Compile 与 Runtime Verification 必须独立声明

只有真实 Target Windchill Classpath Build 才能声明：

```text
Compile Verified
```

只有真实 Windchill 环境中的部署和操作才能声明：

```text
Runtime Verified
```

以下均不等价：

```text
Golden Reference 存在
≠ Compile Verified

Guide 有示例
≠ Compile Verified

Java 语法正确
≠ Windchill Compile Verified

Compile Verified
≠ Runtime Verified
```

当前环境无法完成某一级验证时，应明确说明，不得虚构验证结果。

---

## 16. Future API Lookup

后续版本恢复 Javadoc API Lookup 后，Exact API Metadata 的推荐证据路径为：

```text
Project Windchill Version
        ↓
Target-version Javadoc
        ↓
API Index
        ↓
Exact API Lookup
        ↓
Class / Method / Signature / Status
```

该能力不属于 Windchill AI DevKit 1.0.0 MVP Runtime。