---
trigger: model_decision
description: 当任务涉及 Windchill 对象持久化、创建、保存、修改、删除、PersistenceHelper、PersistenceManager、QuerySpec、SearchCondition、QueryResult、Transaction、Advanced Query、分页或数据库访问行为时应用本规则。
---

# Windchill 持久化、查询与事务规则

## 目的

本规则用于约束 AI Agent 在 Windchill 二次开发过程中涉及对象持久化、查询和事务处理时的技术决策与代码生成行为。

重点确保：

- 不把 Windchill Persistence 当作普通 ORM 或通用 CRUD 框架使用
- 优先保持 Windchill 业务服务和数据模型语义
- 正确设计业务事务边界
- 正确使用 QuerySpec、SearchCondition 和 QueryResult
- 避免无边界、高成本或破坏 Access Control 语义的查询
- 避免因多个离散持久化操作造成部分成功和数据不一致
- 对 Advanced Query 和非 Access-Controlled 查询保持明确风险意识

Version / Iteration、Checkout / Checkin 和 Working Copy 等版本对象语义由专项 Rule 定义。

Principal、Access Control、Administrator Context 等安全上下文由专项 Rule 定义。

---

## 1. 不得把 Windchill Persistence 当作普通 CRUD

Windchill 持久化对象通常同时受到以下平台语义影响：

- Business Service
- Access Control
- Container
- Version / Iteration
- Lifecycle
- Event
- Transaction
- Ownership
- Link / Association
- 其他对象类型特有的业务规则

因此，不得仅根据以下模式判断对象应如何修改：

- 对象存在 → `modify`
- 对象不存在 → `save` / `store`
- 不再需要 → `delete`

在生成或修改持久化代码之前，应首先判断：

1. Windchill 是否已经提供对应的业务 Service、Helper 或 Manager
2. 当前操作是否只是单纯持久化，还是具有更高层业务语义
3. 操作是否需要与其他对象修改共同组成一个原子业务操作
4. 对象是否具有 Version、Iteration、Access Control、Container 或其他平台语义
5. 当前项目是否已经存在经过验证的业务服务封装

如果 Windchill 已经提供表达该业务行为的高层 API，应优先评估该 API，而不是直接组合底层 Persistence API。

---

## 2. Persistence API 的使用必须符合对象状态与业务语义

使用以下类型的 API 前：

- `PersistenceHelper`
- `PersistenceManager`
- `PersistenceServerHelper`
- `save`
- `store`
- `modify`
- `delete`
- `find`
- `query`

应先确认：

- 操作对象是否属于正确的 Persistable 类型
- 当前对象是否处于允许该操作的业务状态
- 是否已经存在负责该操作的 Windchill Service
- 是否需要与其他数据库修改处于同一事务中
- 是否存在 Access Control、Versioning 或 Event 等附加影响

不得仅因为某个 Persistence API 在当前代码中能够编译或历史项目中已经使用，就认为它是当前场景的正确业务 API。

如果无法判断对象应通过业务 Service 还是直接 Persistence API 操作，应优先检查：

1. 目标版本 PTC Javadoc
2. PTC Customization Guide
3. 企业 Windchill 知识库
4. Golden Reference
5. 当前项目中经过验证的同类实现

---

## 3. 事务边界应对应完整业务操作

事务的目的不是机械地包裹每一次 Persistence API 调用，而是保证一个具有完整业务语义的操作保持原子性。

如果一个业务操作包含多个相互依赖的数据库修改，例如：

- 创建业务对象并创建关联 Link
- 修改对象并修改 Ownership
- 创建多个必须共同成功的数据对象
- 修改主对象并同步更新相关业务对象
- 一个 Service Operation 内的多个持久化步骤

应评估这些操作是否必须：

`全部成功，或者全部失败`

如果必须，则应建立清晰的 Transaction Boundary。

不得接受以下结果：

1. 第一个数据库操作已经提交
2. 后续操作失败
3. 系统留下业务上不完整或不一致的数据

复杂业务原子操作应优先封装在明确的服务端业务操作中，而不是由多个调用方分别组合离散 Persistence API。

---

## 4. Transaction 必须具备可靠的回滚路径

显式使用 Windchill Transaction 时，应保证异常路径能够可靠 rollback。

典型事务结构应遵循以下原则：

1. Transaction 在业务修改之前启动
2. 所有属于同一原子业务操作的数据库修改位于事务范围内
3. 只有全部业务操作成功后才 commit
4. 任意异常不得绕过 rollback
5. finally 或等效机制必须保证未成功提交的 Transaction 被回滚
6. 不得吞掉导致事务失败的异常并继续将操作描述为成功

不得生成只有：

`start → business code → commit`

而没有异常回滚保障的事务代码。

不得仅为了代码形式统一而给所有单条查询或单条持久化调用创建新的显式 Transaction。

---

## 5. 修改事务代码前必须确认现有事务上下文

Windchill 的某些执行路径可能已经运行在现有数据库事务中。

在以下场景增加新的显式 Transaction 前，应首先理解当前调用路径：

- Business Service
- Event Listener
- Vetoable Event
- Framework Callback
- OOTB Service 调用链
- 已经具有事务管理能力的业务框架

不得仅因为代码中没有直接看到 `new Transaction()`，就假设当前操作不存在事务上下文。

如果无法确认当前 Transaction Boundary，应先分析调用方及相关 Windchill Framework 行为，而不是机械增加新的事务包装。

---

## 6. QuerySpec 必须表达正确的业务查询范围

使用 `QuerySpec` 时，应首先明确：

- 查询对象类型
- 查询条件
- 是否需要查询子类
- 是否需要完整对象
- 是否需要 Join
- 是否涉及 Link
- 是否涉及 Aggregate / Subselect / Compound Query
- 是否存在结果集过大的风险
- 是否需要分页

不得为了“先查出来再说”而默认生成无约束的大范围查询。

尤其对于：

- WTPart
- WTDocument
- EPMDocument
- WTPartMaster
- WTDocumentMaster
- Change Object
- Workflow Object
- 大型自定义业务对象

应避免在没有明确业务条件的情况下查询全部数据。

---

## 7. 必须理解 QuerySpec 的 Descendant Query 行为

QuerySpec 查询某个 Class 时，默认可能同时查询其 concrete persistable subclasses。

因此：

`new QuerySpec(SomeClass.class)`

不能自动理解为只查询该类对应的单一数据库表。

如果业务语义要求：

- 包含所有适用子类

则应保持对应的 descendant 行为。

如果业务语义明确要求：

- 只查询指定 concrete persistable class

才应评估关闭 descendant query。

不得为了性能优化而随意改变 descendant query 行为，因为这可能改变查询结果集合的业务含义。

---

## 8. 查询时只获取实际需要的数据

如果业务逻辑只需要少量属性，例如：

- Number
- Name
- ID
- Timestamp
- Count
- 某个状态字段

应评估使用 `ClassAttribute` / `ColumnExpression` 等方式只查询需要的列，而不是无条件构建完整 Persistable 对象。

查询完整 Class 通常意味着数据库需要返回构建完整对象所需的全部列。

在不需要完整对象时，优先考虑更小的 SELECT 结果，以降低：

- 数据库读取量
- 网络和 JDBC 数据传输
- 对象构建成本
- MethodServer 内存消耗

但不得为了减少字段而破坏后续业务逻辑所需的 Windchill 对象语义。

---

## 9. SearchCondition 必须准确表达查询条件

`SearchCondition` 本质上用于表达 SQL WHERE 条件。

生成 SearchCondition 时必须确认：

- 左侧 Operand
- Operator
- 右侧 Operand
- ClassAttribute 所属 Class
- FROM Clause 中对应的 Class Index
- AND / OR 逻辑关系
- Join 条件
- LIKE、IN、NULL 等操作语义

当 QuerySpec 包含多个 Class、Join 或 CompositeWhereExpression 时，不得猜测 `fromIndices`。

`fromIndices` 必须与 QuerySpec FROM Clause 和对应 WhereExpression 中使用的 Class / ColumnExpression 保持一致。

复杂 QuerySpec 修改前，应先理解现有 FROM、SELECT、JOIN、WHERE 结构，而不是仅在已有代码末尾追加 SearchCondition。

---

## 10. Advanced Query 必须明确识别 Access Control 风险

以下高级查询能力可能影响 Windchill Access Control 处理：

- SubSelect
- Aggregate Function
- INTERSECT
- MINUS
- External Table
- ROWNUM
- 其他需要 Advanced Query 的 SQL 能力

PTC 为防止无意绕过 Access Control，会对部分高级查询执行限制。

因此，不得仅为了消除 `AdvancedQueryAccessException` 而机械生成：

`setAdvancedQueryEnabled(true)`

也不得仅因为：

`PersistenceHelper.manager.find(...)`

执行失败或结果不符合预期，就直接替换为：

`PersistenceServerHelper.manager.query(...)`

后者属于 server-side non-access-controlled query，使用它会改变查询的安全语义。

如果确实需要 Advanced Query 或 non-access-controlled query，必须：

1. 明确说明普通 Access-Controlled Query 为什么不能满足需求
2. 明确查询是否可能绕过 Access Control
3. 评估查询结果是否可能暴露调用 Principal 无权访问的数据
4. 将使用范围限制到最小
5. 遵守 Access Control / Security Context 专项 Rule
6. 对关键场景建议由项目 SA 或技术负责人确认

不得把关闭或绕过 Access Control 当作查询性能优化方式。

---

## 11. 查询结果规模必须受到控制

对于可能返回大量数据的查询，应评估：

- 更严格的 SearchCondition
- Container 或业务范围限制
- Paging
- 分批处理
- 只查询所需 Column
- 是否真正需要全部结果

不得在无法合理估计结果规模的情况下，默认一次性将大量 Windchill 对象加载到内存集合中。

对于批处理、后台任务和大数据量处理场景，应优先考虑 Windchill 支持的分页查询机制。

分页完成后，如果使用需要显式释放的 Paging Session，应按照对应 API 要求正确关闭或释放资源。

---

## 12. QueryResult 的实际结构必须根据 QuerySpec 确认

不得假设所有：

`PersistenceHelper.manager.find(querySpec)`

返回的每个元素都一定是单个业务对象。

QueryResult 中单个元素的结构可能受到以下因素影响：

- SELECT 内容
- 是否选择完整 Class
- 是否选择单个 ColumnExpression
- 多 Class 查询
- Join
- Compound Query
- Paging Query

因此，在生成：

- `nextElement()`
- 类型转换
- `Object[]`
- Persistable cast

等代码前，应根据当前 QuerySpec 的 SELECT 结构确认实际结果类型。

不得仅复制其他 QuerySpec 示例中的 cast 方式。

---

## 13. Join 应优先使用 Windchill 已有模型关系

查询 Windchill 对象关系时，应优先理解已有：

- Link Class
- Modeled Role
- Master / Object Association
- Windchill 提供的导航或业务 API

如果 QuerySpec 需要 Join，应优先根据 Windchill modeled relationship 构建关系，而不是根据数据库表和物理外键自行推测关联条件。

不得把数据库层面存在的列关系自动视为稳定的 Windchill Customization API。

如果已有 Helper、Service 或 Navigation API 能够表达相同业务关系，应评估使用这些更高层 API 是否更加合适。

---

## 14. 不得为了性能直接绕过 Windchill Persistence 层

Windchill 业务数据的正常创建、修改和删除，应遵守企业 Core Rule 中关于 Windchill 平台语义和数据库访问的要求。

不得因为：

- QuerySpec 编写复杂
- Persistence API 性能不符合预期
- Windchill Access Control 限制查询
- 需要批量修改大量对象

就自行改为直接 SQL：

- INSERT
- UPDATE
- DELETE

直接数据库操作只有在 PTC 官方文档针对明确的维护、安装、升级或特定基础设施场景要求时，才可以按照对应官方过程执行。

诊断用途的数据库只读 SQL 与 Windchill Customization 业务代码不是同一个问题，不应混为一谈。

---

## 15. 不得复制示例代码而忽略示例适用范围

PTC Customization Guide、Javadoc、Golden Reference 和历史项目中的 Persistence / Query 示例都应结合其上下文理解。

特别需要确认：

- 示例针对的对象类型
- 是否为教学示例
- 是否省略 Access Control
- 是否省略 Container
- 是否省略 Versioning
- 是否运行在现有 Transaction 中
- 是否只用于演示 QuerySpec API
- 是否适用于目标 Windchill 版本

不得因为某段 PTC 示例可以运行，就自动将它作为所有业务对象的通用实现模板。

---

## 16. Persistence / Query 代码修改完成后的检查

新增或修改 Persistence、Query 或 Transaction 代码后，应根据任务范围检查：

- 是否优先使用了合适的 Windchill Business API
- Persistence 操作与对象状态是否匹配
- 多个数据库修改是否需要统一 Transaction
- Transaction 是否具有可靠 rollback 路径
- 是否理解当前已有 Transaction Boundary
- QuerySpec 查询范围是否符合业务要求
- Descendant Query 行为是否正确
- SearchCondition 和 fromIndices 是否正确
- 是否无意执行大范围查询
- 是否可以只查询必要 Column
- 大结果集是否需要分页
- QueryResult cast 是否与 SELECT 结构匹配
- Advanced Query 是否影响 Access Control
- 是否使用了 non-access-controlled query
- 是否存在直接 SQL 修改 Windchill 业务数据
- 是否需要 Windchill Runtime 环境进行实际验证

如果涉及 Advanced Query、复杂 Join、Transaction Boundary 或大数据量查询，而当前 Agent 无法在实际 Windchill 环境验证，应明确标记：

`待 Windchill 环境验证`

并指出具体需要验证的内容。