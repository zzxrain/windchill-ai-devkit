---
trigger: model_decision
description: 当任务涉及 Windchill Service、Manager、StandardManager、Event、Listener、Vetoable Event、Queue、ProcessingQueue、ScheduleQueue 或后台处理时应用本规则。
---

# Windchill Service、Event 与 Queue 规则

## 1. 业务操作应具有清晰的 Service Boundary

具有完整业务语义、可能被多个入口复用或包含多个持久化步骤的操作，应优先放在明确的服务端业务边界中。

不得把复杂业务逻辑长期堆积在：

- UI / Controller / FormProcessor
- Listener
- Utility
- JSP
- 调用方临时拼装代码

中。

如果 Windchill 已有对应 Service / Helper，应优先复用已有平台能力。

---

## 2. Service 内的数据修改必须保持事务一致性

一个业务操作包含多个必须共同成功的数据修改时，应具有明确的 Transaction Boundary。

不得由多个调用方分别组合若干 Persistence 操作，导致部分成功。

具体 Transaction 使用遵守：

`30-persistence-query-transaction.md`

---

## 3. 不得把 Windchill Event Listener 当作异步任务

Windchill Service Event Listener 默认是同步通知。

Listener 与 Event Emitter 可能运行在：

- 同一线程
- 同一数据库事务

因此不得假设 Listener：

- 已经异步执行
- 不影响原始请求响应时间
- 拥有独立事务
- 可以安全执行任意耗时逻辑

Listener 中应避免无必要的长时间数据库、网络或大批量处理。

真正需要与原始业务解耦的耗时操作，应评估 Queue 或其他 Windchill 后台机制。

---

## 4. 不得依赖 Listener 执行顺序

同一事件可能存在多个 Listener。

不得设计依赖：

`Listener A 必须先于 Listener B 执行`

的业务逻辑，除非对应 Windchill Framework 明确定义并保证该顺序。

多个 Listener 应尽量保持相互独立。

---

## 5. 正确区分普通 Event 与 Vetoable Event

只有业务上确实需要阻止当前操作时，才应使用 Vetoable Event 语义。

Veto Listener 抛出的异常可能影响事件发出方的原始事务。

因此：

- 不得吞掉应该传播的 veto 异常
- 不得把普通后处理异常随意转化成 veto
- Event Emitter 必须正确处理事务回滚

Listener 中的副作用也必须考虑原事务最终可能回滚。

---

## 6. Queue 用于明确的后台执行边界

需要以下特征时，应评估使用 Windchill Queue：

- 与用户请求解耦
- 长时间处理
- 延迟或计划执行
- 后台批处理
- 失败后可独立诊断或重试

不得仅为了“看起来异步”而创建新的 Queue。

Queue 任务属于独立的后台执行过程，不得假定提交线程中的：

- Transaction
- Principal
- Session Context
- ThreadLocal 状态

会自动以正确方式传递到 Queue 执行阶段。

安全上下文遵守：

`40-access-control-security-context.md`

---

## 7. 优先使用目标版本支持的 Queue Service API

不得因为历史代码直接操作：

- `ProcessingQueue`
- `ScheduleQueue`
- Queue Entry 实现类

就认为这是当前版本推荐的 Customization API。

涉及 Queue 创建、查询、Entry 添加、删除或执行时，应优先检查目标版本的 Service Layer API，例如对应的 `QueueHelper.manager` / Queue Service 能力。

历史 POM Layer API 与当前 Service Layer API 的 Supported 状态可能不同。

所有 Queue API 必须通过目标版本 Javadoc / API Lookup 验证。

---

## 8. Queue 执行参数和业务逻辑应保持明确

Queue Entry 应调用职责明确、可独立执行的服务端方法。

不得让 Queue 方法依赖：

- Web Request
- UI Session
- 页面对象
- 当前线程临时状态
- 只有提交阶段才存在的内存对象

Queue 执行所需的数据必须能够在后台执行时可靠获得。

涉及持久化对象时，应明确传递的是对象标识还是具体业务状态，并在执行时重新确认其当前有效性。

---

## 9. 自定义 Service 启动逻辑必须考虑生命周期

只有确有需要时才自定义 Windchill Service。

涉及 Service Startup / Shutdown 时，应确认：

- Service 依赖关系
- Startup 顺序
- Event Listener 注册
- Queue 初始化
- Security Context

如果启动过程中临时改变 Session Context，必须在可靠的 finally 或等效路径恢复原始状态。

不得假设自定义 Service Number 在后续 Windchill 版本中天然不会与 PTC Service 冲突。

---

## 10. Runtime 行为无法确认时必须明确验证

以下行为如果无法从代码和目标版本资料确定，应标记：

`待 Windchill 环境验证`

尤其包括：

- Event 实际触发时机
- Listener 与事务的实际关系
- Veto 后的回滚行为
- Queue 执行 Principal
- Queue 失败 / 重试行为
- Service Startup 顺序