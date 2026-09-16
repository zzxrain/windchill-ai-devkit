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

```text
Listener A 必须先于 Listener B 执行
```

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

`PRE_*` / `POST_*` Event Name 主要描述事件阶段，不得仅根据名称推导：

```text
PRE_* 一定可以 Veto
POST_* 一定不能 Veto
```

实际 Veto 能力必须结合：

- 具体 Event
- Event Key
- 注册方式
- `notifyEvent()` / `notifyVetoableEvent()` callback
- 目标版本官方资料

确认。

PTC Service Event Conventions 中，Pre / Post 是常见事件设计模式：

```text
Pre Event
→ 通常表示操作即将开始
→ 通常用于校验并可能 Veto

Post Event
→ 通常表示操作已经完成到相应 Service Event 阶段
→ 通常用于后处理
```

但这是 Event Design Convention，不得扩大为所有 `PRE_*` / `POST_*` Event 的绝对产品语义。

尤其禁止使用以下泛化表述作为产品事实：

```text
Windchill 的事件基本都是 Vetoable
PersistenceManagerEvent 基本都可以 Veto
PRE Event 天然就是 Vetoable Event
POST Event 天然就是普通非 Veto Event
```

即使某个具体官方示例证明：

```text
POST_STORE 可以发生 Veto 并导致事务回滚
```

也只能证明该具体 Event / Framework 场景，不得扩张为：

```text
所有 Windchill Event 都具有相同 Veto 能力
```

同样，不得因为当前代码选择：

```java
notifyEvent(...)
```

就把“当前实现没有 Veto”扩大为“该 Event 产品语义上绝对不能 Veto”。

---

## 6. POST Event 不等于 Transaction Post-Commit

Windchill Service Event 的：

```text
POST_*
```

不得自动解释为：

```text
数据库事务已经 Commit
```

根据 PTC Service Event Notification 语义，Listener Notification 可以与 Event Emitter：

```text
同一线程
+
同一数据库事务
```

执行。

因此类似：

```text
POST_STORE
```

表示相应 Persistence / Service Event 已进入 Post 阶段，不等同于：

```text
Transaction 已经成功提交
```

同一事务中的 POST Event 如果产生能够传播的 Veto / Exception，仍可能影响原事务并导致回滚。

### 用户使用“成功后”时必须主动澄清事务含义

如果需求使用以下表达：

```text
写入成功后
保存成功后
创建成功后
修改成功后
操作完成后
真正写入后
post processing
```

并且后续动作是否依赖：

```text
事务已经成功 Commit
```

会影响方案正确性，则回答中必须主动区分：

```text
Persistence / Service POST Event
```

与：

```text
Transaction Post-Commit
```

不得直接把用户口语中的：

```text
成功后
```

自动映射为：

```text
POST_STORE
```

然后省略事务状态说明。

### 真正需要 Post-Commit 语义时

如果业务要求是：

```text
只有数据库事务真正成功 Commit 后
才执行某项逻辑
```

不得直接得出：

```text
Windchill 没有 Post-Commit Hook
```

的结论。

PTC Customization Guide 描述了 Transaction Context / Transaction Listener 机制，可以围绕事务状态获得通知，包括：

```text
about to commit
has committed
rolls back
```

并指向 `wt.pom` 中的 Transaction 相关类型，例如：

```text
Transaction
TransactionListener
TransactionCommitListener
```

这些属于 Product / Framework Evidence。

但是具体：

```text
Class
Interface
Method
Signature
Callback
Supported / Deprecated 状态
```

仍属于 Exact API Metadata，必须按照目标 Windchill 版本通过 Javadoc / API Lookup 独立验证。

因此回答 Post-Commit 需求时应区分：

```text
POST_STORE
→ Persistence Event Post Phase

Transaction Commit Listener
→ Transaction Lifecycle

Queue
→ Independent / Background Execution Boundary
```

三者不能互相替代描述。

Queue 可以用于耗时、外部调用或与用户请求解耦的异步处理，但不得因为 Queue 可以延迟执行，就自动把它描述为 Windchill 唯一的 Post-Commit 机制。

如果 Queue Entry 的创建时机、事务提交可见性或失败语义会影响业务正确性，也必须根据目标版本产品事实继续确认。

---

## 7. Queue 用于明确的后台执行边界

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

## 8. 优先使用目标版本支持的 Queue Service API

不得因为历史代码直接操作：

- `ProcessingQueue`
- `ScheduleQueue`
- Queue Entry 实现类

就认为这是当前版本推荐的 Customization API。

涉及 Queue 创建、查询、Entry 添加、删除或执行时，应优先检查目标版本的 Service Layer API，例如对应的 `QueueHelper.manager` / Queue Service 能力。

历史 POM Layer API 与当前 Service Layer API 的 Supported 状态可能不同。

所有 Queue API 必须通过目标版本 Javadoc / API Lookup 验证。

---

## 9. Queue 执行参数和业务逻辑应保持明确

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

## 10. 自定义 Service 启动逻辑必须考虑生命周期

只有确有需要时才自定义 Windchill Service。

涉及 Service Startup / Shutdown 时，应确认：

- Service 依赖关系
- Startup 顺序
- Event Listener 注册
- Queue 初始化
- Security Context

如果启动过程中临时改变 Session Context，必须在可靠的 finally 或等效路径恢复原始状态。

不得假设自定义 Service Number 在后续 Windchill 版本中天然不会与 PTC Service 冲突。

不得因为一个 Class：

- 继承 `StandardManager`
- 实现 Service
- 注册 Event Listener

就自动增加远程调用接口或 `RemoteAccess`。

只有业务确实需要 Remote Method 调用，并且目标版本 API / Service Contract 已确认时，才应增加对应远程能力。

---

## 11. Runtime 行为无法确认时必须明确验证

以下行为如果无法从代码和目标版本资料确定，应标记：

`待 Windchill 环境验证`

尤其包括：

- Event 实际触发时机
- Listener 与事务的实际关系
- Event 是否支持 Veto
- Veto 后的回滚行为
- Transaction Listener 实际 Callback 时机
- Queue 执行 Principal
- Queue 失败 / 重试行为
- Service Startup 顺序

不得把：

```text
当前实现方式
```

反向描述成：

```text
Windchill 产品必然行为
```