---
trigger: model_decision
description: 当任务涉及 Windchill 日志、Logger、Log4j2、异常记录、调试信息、诊断代码、性能日志、JCA Debug 或生产问题排查相关代码时应用本规则。
---

# Windchill Logging 与 Diagnostics 规则

## 1. 使用 Windchill 当前版本的标准 Logging 机制

自定义 Java 代码应使用目标 Windchill 版本采用的标准 Logging Framework。

不得在正式服务端代码中使用：

- `System.out.println`
- `System.err.println`
- `Throwable.printStackTrace()`

作为正常日志或错误处理方式。

涉及 Logger API 或配置格式时，应以目标 Windchill 版本为准，不得复制旧版本 Log4j 配置方式。

---

## 2. Logger 应与代码职责对应

Logger 应使用明确、稳定的类别，通常与实现类或功能 package 对应。

不得为了方便：

- 所有代码共用一个全局 Logger
- 创建大量动态 Logger Name
- 使用不相关的 PTC Logger 记录自定义业务日志

Logger 命名应便于运维人员针对特定功能独立调整日志级别。

---

## 3. 正确选择日志级别

日志级别应表达事件严重性，而不是开发人员希望“多打印一点”。

一般原则：

- `ERROR`：操作失败或系统无法按预期完成
- `WARN`：异常或风险情况，但当前操作仍可能继续
- `INFO`：少量重要业务或生命周期信息
- `DEBUG`：问题诊断所需的执行信息
- `TRACE`：高粒度调用和内部状态诊断

不得把普通正常路径大量记录为 `ERROR` 或 `WARN`。

不得默认在高频路径使用大量 `INFO` 日志。

---

## 4. 异常日志必须保留真正的异常原因

记录异常时，应保留原始 Throwable / Cause。

不得只记录：

`e.getMessage()`

然后丢失：

- Exception Type
- Stack Trace
- Root Cause

也不得 catch 异常后只写日志并继续把业务操作描述为成功。

异常处理和业务回滚应遵守对应 Service / Transaction Rule。

---

## 5. 避免同一个异常在每一层重复记录

如果异常需要继续向上抛出，应避免在每一个调用层都记录相同完整 Stack Trace。

应在具有足够业务上下文且真正处理该异常的边界记录日志。

底层若无法增加有价值的诊断信息，可直接传播异常。

如果重新包装异常，应保留原始 cause。

---

## 6. 日志必须包含有价值的诊断上下文

对重要失败或复杂操作，日志应根据场景包含足够定位问题的信息，例如：

- 当前操作名称
- 对象类型
- OID / Number 等稳定识别信息
- Queue / Event / Service 名称
- 关键业务阶段
- 必要的执行结果或耗时

不得仅记录：

`operation failed`

而没有足够上下文。

但诊断上下文必须遵守敏感信息要求。

---

## 7. 不得记录敏感信息

不得将以下内容直接写入日志：

- Password
- Token
- Session Cookie
- Authorization Header
- Private Key
- Secret
- 完整 Credential
- 不必要的个人敏感信息
- 用户无权访问的业务数据内容

排查认证或集成问题时，也应优先记录：

- 状态
- 标识符
- 摘要
- 长度
- 脱敏值

而不是完整敏感 Payload。

---

## 8. 不得无边界记录大型对象和 Payload

不得为了调试直接长期记录：

- 完整 Persistable
- 大型 JSON / XML
- 文件内容
- BOM 全结构
- QueryResult 全量数据
- HTTP Request / Response 全文

这可能造成：

- 日志爆量
- MethodServer IO 压力
- 磁盘快速增长
- 敏感信息泄露
- 真实错误被大量日志淹没

如确需诊断，应限制范围、长度和日志级别。

---

## 9. 高频路径中的日志必须考虑性能

对于：

- Builder / DataUtility
- Validator
- Listener
- 循环
- 大批量处理
- Queue
- 高频 Service

不得为每个对象无条件生成大量 DEBUG / INFO 日志。

昂贵的日志参数构造、对象序列化或数据库查询不得仅为了生成一个当前不会输出的 DEBUG 日志而执行。

---

## 10. 不得依赖日志控制业务逻辑

Logging Level 只用于可观测性。

不得出现：

`如果 DEBUG 开启，则执行业务步骤`

这类会使系统行为随 Logger Level 改变的逻辑。

调试日志开启与否不得改变：

- Transaction
- Access Control
- Versioning
- 数据修改
- 业务结果

---

## 11. 优先使用已有的 Windchill 诊断能力

排查 Windchill Framework 问题时，应优先寻找目标版本已有的：

- 专用 Log4j Logger
- JCA / MVC `jcaDebug`
- JavaScript Debug / Logging
- Framework Debug 参数
- 对应 MethodServer / BackgroundMethodServer 日志

不得第一反应就在 PTC Framework 内部增加大量自定义打印代码。

---

## 12. 临时诊断代码不得成为永久噪音

为定位问题临时增加的：

- TRACE 日志
- 大量对象状态输出
- Timing 日志
- 特殊 Debug 开关

在问题解决后应评估是否：

- 删除
- 降低日志级别
- 转成可配置诊断能力

不得把一次性 Troubleshooting 输出永久留在高频生产路径。

---

## 13. 后台与异步操作日志应便于关联

Queue、Listener、Scheduled Task 和后台处理由于脱离原始请求，应根据场景记录能够进行关联的标识，例如：

- Queue Entry / Task 标识
- 业务对象 OID
- 操作类型
- 业务关联 ID

但不得自行假设 HTTP Request Context 会持续存在。

Security Context 和敏感信息要求仍然适用。

---

## 14. 日志配置必须遵守 Windchill 配置机制

需要调整 Logger Level、Appender 或 Log4j 配置时，应使用目标版本 Windchill 支持的配置机制。

不得为了临时诊断：

- 随意替换 PTC Logging 配置
- 修改无关 Logger
- 将整个系统长期设置为 DEBUG / TRACE

配置文件修改同时遵守：

`60-configuration-customization-files.md`

---

## 15. 区分“代码诊断能力”和“已完成 Runtime 验证”

增加日志只能提高可诊断性，不代表已经验证 Runtime 行为。

如果必须通过真实 Windchill 环境才能确认：

- Event 是否触发
- Queue 是否执行
- Transaction 是否回滚
- Access Control 行为
- 页面 Builder 调用
- 性能和并发问题

应明确标记：

`待 Windchill 环境验证`

不得仅因为已经加入诊断日志就声称问题已经验证或解决。