---
trigger: model_decision
description: 当任务涉及 Windchill Master、Version、Revision、Iteration、Latest、VersionControl、RevisionControlled、Iterated、Mastered、Workable、Checkout、Checkin、Working Copy、Original Copy 或版本对象修改与查询时应用本规则。
---

# Windchill 版本对象语义规则

## 目的

本规则用于约束 AI Agent 在处理 Windchill 版本化对象时的技术判断和代码生成行为。

重点确保：

- 正确区分 Master、Version、Iteration 和 Working Copy
- 不把“同一个业务对象”误解为“同一个持久化对象实例”
- 不混淆 latest version 与 latest iteration
- 修改 Workable / RevisionControlled 对象前理解 Checkout / Checkin 语义
- 查询版本对象时明确需要哪一个业务版本
- 正确处理 Original 与 Working Copy
- 避免直接持久化操作破坏 Windchill Version Control 语义
- 避免根据 UI 显示、OID 或局部对象状态错误推断版本关系

Persistence、QuerySpec 和 Transaction 由专项 Persistence Rule 定义。

Access Control、Principal 和安全上下文由专项 Security Context Rule 定义。

Lifecycle、Change Management 和 Workflow 的业务规则不在本 Rule 中展开。

---

## 1. Versioned Object 不是普通单记录对象

Windchill 中的版本化业务对象不能按照普通数据库实体理解。

对于具有版本控制能力的对象，应根据实际类型判断其是否涉及：

- Master
- Version
- Iteration
- Working Copy
- Original Copy
- Checkout State
- Version Control
- Work In Progress

不得简单认为：

`找到一个 WTPart / WTDocument / EPMDocument 实例`

就等于：

`找到了业务上唯一正确的那个对象`

同一个业务对象可能同时存在多个 Version 和多个 Iteration，并可能存在 Working Copy。

因此，在读取、修改、关联或返回 Versioned Object 前，应明确当前业务场景实际需要的是哪一种对象状态。

---

## 2. 必须区分 Master 与 Iteration Object

Windchill Master-Iteration Pattern 中，Master 与 Iteration 是不同的业务角色。

Master 通常表示跨版本保持稳定的业务身份。

Iteration Object 表示该业务身份在某一个 Version / Iteration 下的具体状态。

例如在典型 Part 模型中：

- `WTPartMaster` 表示 Part identity
- `WTPart` 表示某个具体 Version / Iteration

因此不得把：

`WTPartMaster`

和：

`WTPart`

视为可以互换的数据对象。

在处理属性、关联、查询和 Link 时，应首先确认关系实际定义在：

- Master level
- Version / Revision level
- Iteration level

不得仅根据变量名、数据库字段或相似业务含义推断关联层级。

---

## 3. 修改属性前必须确认属性属于哪个层级

Master 属性和 Iteration Object 属性具有不同语义。

Master 上的属性通常代表跨所有 Versions / Iterations 保持一致的身份级信息。

Iteration Object 上的属性则可能随 Version / Iteration 变化。

因此，修改版本化对象属性前，应确认：

1. 属性定义在哪个对象层级
2. 修改是否应该影响所有 Version / Iteration
3. 修改是否只应该影响当前 Iteration
4. 是否存在对应的业务 API
5. 是否需要通过 Checkout / Working Copy 完成修改

不得为了方便而：

- 从 Iteration 对象错误修改 Master 数据
- 从 Master 对象模拟 Iteration 级变化
- 将 Master 属性复制到每个 Iteration 作为替代方案

---

## 4. Version 与 Iteration 不得混为一谈

Version 和 Iteration 表示不同层级的变化。

典型表现例如（有些企业的Version规则可能并非A->B->C）：

`A.1 → A.2 → A.3 → B.1`

其中：

- `A → B` 表示 Version / Revision 层级变化
- `.1 → .2 → .3` 表示同一 Version 内的 Iteration 变化

因此不得将：

`最新 Iteration`

自动理解为：

`整个 Master 下的最新 Version`

也不得将：

`Version A 的最新 Iteration`

自动理解为：

`业务上当前最新对象`

如果需求中出现：

- latest
- current
- newest
- previous
- previous version
- latest revision
- latest iteration

Agent 必须首先确定这些词在当前业务场景中的精确定义。

如果需求无法区分，应明确指出语义不确定性，而不是自行选择一种“latest”。

---

## 5. 查询 Versioned Object 时必须明确目标语义

查询版本化对象时，应根据业务需求明确至少以下维度：

- 指定 Master 下全部 Version？
- 指定 Version 下全部 Iteration？
- 每个 Version 的 Latest Iteration？
- 整个 Master 的 Latest Version？
- Latest Version 的 Latest Iteration？
- 是否包括 Working Copy？
- 是否只返回 Original？
- 是否限定当前用户可见的 Working Copy？

不得使用一个简单的 QuerySpec 查询后，仅通过：

- 第一条结果
- 最后一条结果
- 默认排序
- OID 大小
- 修改时间
- 创建时间

推断“最新版本”。

Windchill Version Control 语义应通过适合的 Version Control API 或明确的版本查询逻辑表达。

---

## 6. “Latest” 必须明确是哪一种 Latest

代码和需求中出现 `latest` 时，应避免单独使用这个概念。

应尽可能明确为：

- latest iteration
- latest version / revision
- latest version + latest iteration
- latest non-working iteration
- latest object according to a ConfigSpec

不同含义可能产生不同对象。

例如，获得某个 Iterated Object 的 latest iteration，并不意味着已经完成了跨所有 Versions 的 latest version 选择。

因此不得生成含义模糊的：

`getLatestXXX()`

调用而不理解该 API 的具体 Version Control 语义。

如果使用 `VersionControlHelper` 或其他 Version Control API，应通过目标版本 Javadoc 确认该方法的：

- 输入对象类型
- 返回范围
- Working Copy 行为
- 参数含义
- Version / Iteration 范围

---

## 7. Working Copy 与 Original 必须明确区分

Checkout 后的 Working Copy 与被 Checkout 的 Original Object 不是可以随意互换的引用。

处理 Workable Object 时，应根据场景判断：

- 对象是否已经 Checked Out
- 当前对象是否为 Working Copy
- 当前对象是否为 Original
- Working Copy 属于哪个 Principal
- 当前用户是否有权访问 Working Copy
- 当前业务操作应该作用于 Original 还是 Working Copy

不得仅因为对象：

`isCheckedOut == true`

就认为当前对象本身是 Working Copy。

不得仅因为存在 Working Copy，就自动使用该 Working Copy。

如果业务逻辑明确需要当前用户的 Working Copy，应通过 Windchill Work In Progress API 确认和取得对应对象。

---

## 8. 修改 Workable Object 前应确认是否需要 Checkout

对于具有 Work In Progress 语义的对象，不能默认直接：

`PersistenceHelper.manager.modify(object)`

就是正确的业务修改方式。

在修改前，应确认：

1. 对象是否为 Workable
2. 当前修改是否属于需要 Checkout / Checkin 管理的业务变化
3. 对象当前是否已经 Checked Out
4. 当前拿到的是 Original 还是 Working Copy
5. 当前 Principal 是否拥有或可以使用该 Working Copy
6. Windchill 是否已有完成该业务操作的 Service / Helper

如果业务语义要求通过 Checkout / Checkin 修改，则应：

`Original → Checkout → Working Copy → Modify → Checkin`

而不是直接修改 Original。

但不得反过来建立：

`所有 Versioned Object 修改都必须 Checkout`

这样的绝对规则。

具体操作必须根据对象类型和对应 Windchill Business API 判断。

---

## 9. 不得无条件自动 Checkout

AI Agent 不应为了让修改代码能够成功，而遇到 Workable Object 就自动执行 Checkout。

自动 Checkout 会改变：

- 对象状态
- 用户工作上下文
- Ownership
- Working Copy
- 后续 Checkin 行为
- UI 中用户看到的状态
- 其他并发用户的操作能力

因此，除非业务流程明确要求，否则不得隐式增加：

`checkout → modify → checkin`

逻辑。

如果实现采用自动 Checkout，应明确：

- 为什么业务允许自动 Checkout
- 对象已被其他用户 Checkout 时如何处理
- 已存在当前用户 Working Copy 时如何处理
- Checkin comment / folder 等所需上下文
- 中途失败时对象状态如何处理

---

## 10. 已 Checked Out 对象需要单独处理

当业务操作接收到一个已经 Checked Out 的对象时，不能假设：

`继续 checkout`

或：

`直接修改`

一定正确。

应至少考虑：

### 当前用户已经 Checkout

可能需要取得已有 Working Copy，而不是重复 Checkout。

### 其他用户已经 Checkout

通常不能把其他用户的 Working Copy 当作当前业务对象使用。

不得通过：

- Administrator
- 关闭 Access Control
- 强制修改
- 直接 Persistence API

规避正常的 Work In Progress 语义。

确需特殊管理行为时，应由明确的业务要求和 PTC API 支撑。

---

## 11. Working Copy 是否出现在查询结果中不能靠猜测

不同查询、ConfigSpec 和 Windchill Framework 可能对 Working Copy 有不同处理方式。

因此不得假定：

`QueryResult 一定包含 Working Copy`

或：

`QueryResult 一定只包含 Original`

如果业务需要 Working Copy，应明确设计 Working Copy 的获取逻辑。

如果业务明确只需要 Original，应明确排除或转换 Working Copy。

如果需要实现：

`用户自己 Checkout 的对象显示 Working Copy，其他对象显示 Original`

应使用适合的 Windchill Work In Progress API 和当前 Principal 语义实现，而不是根据对象属性手工猜测。

---

## 12. Previous Object 必须明确是 Previous Version 还是 Previous Iteration

“上一版”“前一个版本”等自然语言在 Windchill 中具有歧义。

可能表示：

`A.3 → A.2`

也可能表示：

`B.x → A.x`

因此在实现：

- previous
- predecessor
- history
- compare with previous
- previous revision

等需求时，应首先明确：

- Previous Iteration
- Previous Version / Revision
- Previous Released Version
- Previous Business Baseline

不得仅因为某个 Version Control API 名称包含：

`predecessor`

就直接认定其业务含义等同于“上一 Revision”。

---

## 13. Version Control 操作必须优先使用 Windchill Version Control API

涉及以下行为时：

- 获取 Version
- 获取 Iteration
- 获取 Latest Iteration
- 获取 Previous Version
- 获取 Master
- 创建新 Version
- 创建新 Iteration
- Checkout
- Checkin
- Undo Checkout
- Working Copy 查询

应优先使用对应的 Windchill Version Control / Work In Progress API。

不得通过手工修改以下信息模拟版本控制：

- Version identifier
- Iteration identifier
- Branch identifier
- Checkout state
- Master reference
- Versioning-related database attributes

不得使用直接 Persistence 修改或 SQL 更新模拟：

- revise
- iterate
- checkout
- checkin

---

## 14. 不得根据字符串自行实现 Version 排序

Windchill Version identifier 可能受到 Versioning Scheme 和项目配置影响。

因此不得假设 Version 永远是：

`A, B, C, D...`

也不得通过普通 String 比较判断：

`A < B < C`

更不得通过：

- 字符串排序
- ASCII 比较
- 手工字母加一
- 数字解析

替代 Windchill Version Control 语义。

如果需要：

- latest version
- next version
- version ordering

应使用适用于目标 Windchill 版本和业务对象的官方 Version Control 机制。

---

## 15. 不得通过 Iteration 字符串自行判断先后关系

同样，不应依赖类似：

`1`
`2`
`3`

这样的显示字符串自行计算 Iteration 关系。

Iteration identifier 属于 Windchill Version Control 模型的一部分。

需要 predecessor、latest 或 ordering 时，应优先使用对应 Version Control API 或经过验证的 Windchill 查询方式。

---

## 16. Master、Version、Iteration 层级的 Link 必须正确识别

Windchill 中不同 Link 可能关联：

- Master ↔ Master
- Version ↔ Master
- Version ↔ Version
- Iteration-level object
- 其他具体 modeled relationship

例如业务上看起来都是：

`Part 和 Document 有关系`

实际可能属于不同层级的 Link。

因此创建、查询或删除 Link 前，应确认：

1. Link Class
2. Role A / Role B 类型
3. 关联发生在 Master 还是 Version / Iteration 层
4. 是否已有对应 Helper / Service / Navigation API
5. Version 变化后该关联应如何表现

不得为了让类型匹配而随意从 Version 转 Master，或从 Master 随意寻找某个 Version 再建立关联。

---

## 17. OID 不能替代版本业务语义

Windchill Object Identifier 标识的是具体对象实例。

不得仅持有一个 OID 后就认为：

`这个 OID 永远代表该业务对象的当前版本`

当业务要求表达：

`这一个具体历史对象`

时，持有具体 Version / Iteration OID 可能是正确的。

但当业务要求表达：

`这个业务对象，无论后续产生什么 Version`

时，应评估是否应该持有 Master 或其他稳定业务标识。

因此在：

- 外部系统集成
- URL 参数
- 自定义表
- Queue 参数
- Workflow 数据
- 配置记录

中保存 Windchill 对象引用前，应明确需要保存的是：

`具体 Iteration identity`

还是：

`跨版本业务 identity`

---

## 18. ConfigSpec 与 Version Selection 不应混为一谈

在结构、BOM、配置过滤等场景中，“应该使用哪个 Part Version”通常不只是简单的 Latest Version 问题。

它可能受到：

- View
- State
- Effectivity
- Baseline
- Working Copy
- ConfigSpec
- Navigation Criteria

等因素影响。

因此如果当前业务属于配置结构场景，不得简单用：

`latest version`

替代 Windchill ConfigSpec / Navigation Criteria 的版本选择逻辑。

Version Control Rule 负责保证对象版本语义正确，但具体结构过滤逻辑应遵守对应业务域和 ConfigSpec 的规则。

---

## 19. 不得复制其他对象类型的 Versioning 模式而不确认能力

WTPart、WTDocument、EPMDocument 以及其他 Versioned / RevisionControlled / Workable 对象具有相似的基础 Version Control 能力，但其业务 Service 和对象语义并不完全相同。

不得仅因为以下代码适用于 WTPart：

`VersionControlHelper...`
`WorkInProgressHelper...`

就自动认为相同实现适用于任何其他 Windchill 类型。

应确认：

- 对象实际实现的接口
- 对应业务 Service
- 当前对象类型的 PTC Javadoc
- 目标 Windchill 版本
- 项目中经过验证的同类实现

共享的基础接口可以用于判断能力，但业务操作应优先考虑对象类型对应的业务 API。

---

## 20. Version / Working Copy 相关 API 必须经过产品事实验证

当生成或修改涉及以下 API 的代码时，应优先通过目标版本 PTC Javadoc 或 API Lookup 确认实际签名和语义：

- `VersionControlHelper`
- `VersionControlService`
- `WorkInProgressHelper`
- `WorkInProgressService`
- `Versioned`
- `Iterated`
- `Mastered`
- `Workable`
- 以及实际业务对象对应的 Version Control API

不得根据模型记忆猜测：

- Method name
- Parameter type
- Boolean parameter semantics
- Return type
- Throws
- Supported status

尤其对于带有多个 Boolean 参数或多个 overload 的 API，应进行精确方法验证。

---

## 21. Versioning 代码修改后的检查

新增或修改 Version / Iteration / Working Copy 相关代码后，应根据任务范围检查：

- 当前业务对象是否 Versioned / Iterated / Workable
- 当前代码处理的是 Master 还是 Iteration Object
- 属性属于 Master level 还是 Iteration level
- Version 与 Iteration 是否正确区分
- `latest` 的业务含义是否明确
- 是否错误地把 Latest Iteration 当作 Latest Version
- 是否需要 Working Copy
- 当前对象是否 Original 或 Working Copy
- Checked Out 状态是否被正确处理
- 是否存在重复 Checkout 风险
- 其他用户 Checkout 的场景是否被考虑
- 修改是否应该通过 Checkout / Checkin
- 是否误用 Persistence API 绕过 Version Control
- Previous 指的是 Previous Iteration 还是 Previous Version
- Version identifier 是否被手工解析或排序
- Link 是否建立在正确的版本层级
- OID 是否保存了正确的对象身份层级
- ConfigSpec 场景是否错误地简化成 Latest Version
- 所使用的 PTC API 是否经过目标版本验证

如果 Version Selection、Working Copy Ownership、Checkout State 或 Version Control API 行为必须依赖真实 Windchill 环境确认，而当前 Agent 无法访问该环境，应明确标记：

`待 Windchill 环境验证`

并指出具体需要验证的 Version / Iteration / Working Copy 行为。