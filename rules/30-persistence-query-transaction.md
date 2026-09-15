---
trigger: model_decision
description: 当任务涉及 Windchill 对象持久化、PersistenceHelper、QuerySpec、SearchCondition、QueryResult、Transaction、Advanced Query、分页或数据库访问时应用本规则。
---

# Windchill 持久化、查询与事务规则

## 1. 不得把 Windchill Persistence 当作普通 CRUD

使用 `save`、`modify`、`delete` 等 Persistence API 前，应先确认：

- 对象当前业务状态
- 是否存在更高层 Windchill Service / Helper
- 是否涉及 Versioning、Access Control、Lifecycle、Event 或 Link 语义
- 是否属于一个更大的原子业务操作

不得仅因为 Persistence API 能够编译运行，就认为它是正确的业务操作方式。

## 2. Transaction Boundary 必须对应完整业务操作

多个相互依赖的数据修改如果必须共同成功或共同失败，应处于明确的事务边界中。

显式使用 `Transaction` 时必须保证：

- 成功后才 commit
- 异常路径可靠 rollback
- 未提交事务能够在 finally 或等效路径回滚

不得吞掉导致事务失败的异常后继续报告成功。

同时，不得机械地给每个 Persistence 调用创建新 Transaction；增加事务前应先理解当前 Service、Listener、Framework Callback 是否已经存在事务上下文。

## 3. QuerySpec 必须表达明确且有限的业务范围

生成 QuerySpec 前，应明确：

- 查询哪些 Class
- 是否包含子类
- 查询条件
- Join / Link 关系
- 是否需要完整 Persistable
- 结果规模
- 是否需要分页

不得默认生成无业务边界的大范围查询。

如果改变 descendant query 行为、Join 或复杂 FROM / WHERE 结构，必须确认不会改变原有业务结果。

## 4. SearchCondition 和 QueryResult 不得靠猜

复杂 QuerySpec 中必须正确理解：

- ClassAttribute 与 Class Index
- `fromIndices`
- AND / OR
- Join 条件
- SELECT 内容

不得从其他查询示例直接复制 `fromIndices` 或 cast。

`QueryResult` 中元素可能是单个 Persistable、列值或 `Object[]`；具体结构必须根据当前 QuerySpec 的 SELECT 结构确定。

## 5. 控制查询成本和结果规模

大数据量查询应优先考虑：

- 更精确的业务条件
- 只选择需要的列
- Paging / 分批处理
- 避免一次性把大量对象加载到内存

分页 API 如果要求显式释放 Paging Session，必须按目标版本 API 要求关闭。

不得在循环中无意识执行大量重复数据库查询。

## 6. Advanced Query 不得无意改变 Access Control 语义

不得为了消除 `AdvancedQueryAccessException` 而机械执行：

`setAdvancedQueryEnabled(true)`

也不得为了让查询成功或返回更多结果，直接把 access-controlled query 替换成：

`PersistenceServerHelper.manager.query(...)`

确实需要 Advanced Query 或 non-access-controlled query 时，必须明确：

- 为什么普通查询不能满足需求
- 是否绕过 Access Control
- 返回数据最终会暴露给谁

并遵守 Access Control / Security Context Rule。

## 7. 不得直接 SQL 修改 Windchill 业务数据

正常 Customization 业务代码不得通过 SQL `INSERT / UPDATE / DELETE` 绕过 Windchill Persistence 和业务语义。

PTC 官方明确要求的维护、安装、升级等特殊过程除外。

数据库只读诊断与业务代码直接修改数据库应严格区分。

## 8. 高风险查询和事务必须明确验证边界

涉及以下场景而当前 Agent 无法访问真实 Windchill Runtime 时：

- Advanced Query
- non-access-controlled query
- 复杂 Join
- Transaction Boundary
- 大数据量 Paging

必须明确标记：

`待 Windchill 环境验证`

并指出具体需要验证的行为。