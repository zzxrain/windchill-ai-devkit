---
trigger: model_decision
description: 当任务涉及 Windchill Access Control、AccessPermission、WTPrincipal、SessionContext、SessionHelper、SessionServerHelper、Administrator Context、权限绕过、Security Label、Security Evaluator 或任何需要判断当前执行身份和授权状态的服务端代码时应用本规则。
---

# Windchill Access Control 与 Security Context 规则

## 目的

本规则用于约束 AI Agent 在 Windchill 二次开发中处理执行身份、访问控制和安全上下文时的技术判断与代码生成行为。

重点确保：

- 不绕过 Windchill Access Control 来解决普通业务问题
- 明确代码当前以哪个 Principal 身份执行
- 正确管理 Session Context
- 正确管理 Access Control Enforcement 状态
- Administrator Context 和 Access Control bypass 只在明确必要的场景使用
- 临时权限提升必须可靠恢复
- 查询、持久化和后台任务不得无意改变安全语义
- Security Label 相关扩展符合 Windchill 的安全模型
- 不把“代码能运行”误认为“代码具有正确授权语义”

Authentication、SSO、SAML、OIDC、Kerberos 等用户认证机制不在本 Rule 中展开。

HTTP / Web 输入安全、CSRF、XSS 等 Web Security 问题由 Web / Integration 专项 Rule 处理。

---

## 1. Windchill Security Context 属于业务语义的一部分

Windchill 服务端代码的执行结果可能受到以下因素影响：

- 当前 Principal
- Session Context
- Access Control Enforcement
- Object Domain
- Container / Organization Context
- Access Permission
- Security Label
- 对象类型和状态
- 当前调用所处的 Windchill Framework

因此不得只根据：

`代码是否成功执行`

判断实现是否正确。

同一段代码以：

- 普通用户
- 站点管理员
- 组织管理员
- 其他系统身份

执行时，可能产生完全不同的授权结果。

AI Agent 在修改涉及安全敏感操作的代码前，应明确当前操作预期以哪个身份执行。

---

## 2. 默认应保留调用方的 Principal 和 Access Control 语义

普通业务操作原则上应在当前调用方的正常 Windchill Security Context 中执行。

不得为了：

- 避免 NotAuthorizedException
- 让查询返回更多数据
- 让 Persistence 操作成功
- 简化代码
- 绕过 ACL 配置问题
- 解决测试环境权限问题

就自动：

- 切换 Administrator
- 关闭 Access Control
- 替换当前 Principal
- 使用 non-access-controlled 查询

如果普通业务需求需要某个用户操作对象，应优先判断：

1. 用户是否本来应该具有对应权限
2. ACL / Domain / Lifecycle / Security Label 配置是否正确
3. 是否已有 Windchill Business API 表达该操作
4. 当前代码是否错误地选择了对象或上下文

而不是直接提升权限。

---

## 3. 权限提升必须有明确的技术或业务依据

只有在以下类型场景中才应评估临时权限提升：

- PTC 官方定制机制明确要求
- 后台系统任务本身设计为 system-level operation
- 安装、初始化或系统维护逻辑
- 已批准的业务功能明确需要系统身份执行
- 当前项目已有经过确认的架构设计

即使存在合法需求，也应选择影响最小的方案。

不得因为 Administrator 可以“解决所有权限问题”，就把 Administrator 作为默认执行身份。

---

## 4. 切换 Administrator 必须保存并恢复原始 Session Context

如果确实需要临时切换 Administrator，应遵循以下原则：

1. 保存原始 Session Context
2. 创建明确的临时 Context
3. 只在必要的最小代码范围内切换 Administrator
4. 无论业务成功或失败，都必须恢复原始 Context
5. 恢复逻辑必须位于 finally 或等效的可靠清理路径中
6. 不得让提升后的身份泄漏到后续无关代码

不得生成如下逻辑：

`setAdministrator → business code → return`

而没有保证恢复原始 Session Context。

也不得假设异常抛出后 Windchill 会自动恢复 Agent 手工修改的 Session Context。

---

## 5. 关闭 Access Control 必须保存并恢复原始 Enforcement 状态

如果 PTC 官方机制或已经批准的系统级实现确实需要临时 bypass Access Control，应：

1. 获取并保存原始 Access Enforcement 状态
2. 在最小范围内关闭 Enforcement
3. 在 finally 或等效路径恢复原始状态
4. 不得假定原始状态一定是 `true`
5. 不得简单在结束时硬编码“重新开启”

正确原则是：

`保存 previous → 临时修改 → 恢复 previous`

而不是：

`关闭 → 操作 → 强制开启`

因为当前代码可能被调用于已有特殊 Security Context 中。

---

## 6. Administrator 与关闭 Access Control 不是同一个概念

不得把以下两种操作视为等价：

- 以 Administrator Principal 执行
- 禁用 Access Control Enforcement

它们改变的是不同层面的安全语义。

因此不得因为某个 PTC 示例允许两种方式之一，就任意互换。

选择哪一种方式必须基于：

- 对应 PTC 官方扩展机制
- 当前 API 的要求
- 项目安全设计
- 最小权限原则
- 对业务日志和审计的影响

如果无法确认，应明确标记风险并要求进一步验证。

---

## 7. 不得把 PTC 特殊场景推广成全局规则

PTC 文档中存在某些明确要求提升权限或 bypass Access Control 的特殊机制。

例如部分 Windchill Queue Service 公共 API 的官方定制说明要求调用前设置 Administrator 或 bypass Access Control。

该规则只能理解为：

`该特定 API / Framework 的官方调用要求`

不得扩展成：

`所有 Queue 代码都应该永久以 Administrator 执行`

或：

`所有后台任务都应该关闭 Access Control`

更不得推广成所有 Customization 的通用实现模式。

使用这类特殊模式时，应保留对应官方依据或项目设计依据。

---

## 8. 安全敏感业务操作应显式考虑 Access Permission

如果业务行为本身需要某项 Windchill 权限，应评估是否需要通过 Windchill Access Control API 显式确认调用方具有对应 AccessPermission。

例如可能涉及：

- READ
- MODIFY
- DELETE
- CREATE
- CHANGE_PERMISSIONS
- 其他对象类型支持的权限

不得自行通过：

- 用户名
- Group 名称
- Role 名称
- 是否为 Administrator
- UI 是否显示某个按钮

来替代真正的 Access Control 判断。

UI Action 可见不等于服务端已经完成授权。

服务端敏感操作应依赖 Windchill 实际授权语义，而不是信任调用方 UI。

---

## 9. 服务端权限检查不得只依赖前端校验

即使：

- Action Validator
- JCA UI
- JavaScript
- WRS Client
- 外部系统

已经限制了用户操作，服务端仍不能因此假定请求已经获得授权。

如果服务端 Customization 执行安全敏感操作，应确保最终权限判断发生在可信服务端边界。

不得将以下内容视为授权证据：

- 前端隐藏按钮
- 请求参数中的用户名
- 浏览器传入的角色
- 客户端声明的管理员标志
- 外部调用方传入的权限字段

---

## 10. Principal 必须来自可信 Windchill Security Context

涉及当前用户身份时，应优先使用 Windchill 当前 Session / Principal 机制。

不得从以下不可信来源自行构造当前 Principal 身份：

- HTTP 参数
- 自定义 Header
- URL 参数
- 表单字段
- JSON Payload 中的用户名

除非当前实现属于已经建立可信边界的认证 / SSO 集成机制，并且该身份映射过程已由对应架构设计定义。

业务代码不应自行承担“相信客户端传入用户名”的身份认证职责。

---

## 11. 不得通过用户名判断权限

以下模式原则上不应作为授权逻辑：

`if ("wcadmin".equals(userName))`

或：

`if (userName.startsWith("admin"))`

或根据固定用户名列表直接给予业务权限。

身份和授权属于不同问题。

即使确实存在特殊系统用户，也应通过 Windchill 已定义的安全机制、Group / Role / Permission 或明确项目安全模型表达，而不是散落在业务代码中的字符串判断。

---

## 12. Group / Organization / Role 判断不能自动替代 Access Control

某个用户属于某 Group、Organization 或 Team Role，并不自动意味着该用户对具体对象拥有某项 AccessPermission。

因此：

`membership check`

和：

`object access check`

必须区分。

如果业务规则本身定义为：

“只有某 Role 才能执行该业务动作”

可以进行角色判断。

如果业务规则定义为：

“只有对该对象具有 MODIFY 权限的人才能修改”

则应判断对象访问权限。

不得用其中一种语义替代另一种语义。

---

## 13. Access Control 与 Persistence / Query 必须保持一致

查询和持久化 API 的选择可能改变 Access Control 行为。

不得为了获得更多查询结果而随意从：

`access-controlled query`

切换成：

`non-access-controlled query`

也不得因为 Agent 使用了 server-side API，就自动认为授权不再重要。

如果查询绕过 Access Control，应按照本 Rule 中的权限 bypass 要求进行评估，并同时遵守 Persistence / Query / Transaction Rule。

---

## 14. Access Control bypass 后取得的数据仍然是敏感数据

当代码通过系统级身份或关闭 Access Control 获得原本普通用户不可见的数据后，不得直接把这些结果：

- 返回给当前用户
- 输出到 UI
- 返回到 REST / WRS
- 写入普通用户可访问的文件
- 写入无保护日志
- 传给外部系统

bypass Access Control 只改变服务器内部访问能力，不代表调用用户自动获得了这些数据的授权。

因此系统级代码必须重新确认：

`数据最终暴露给谁`

而不仅仅考虑：

`服务器是否能够读到数据`

---

## 15. 后台任务必须明确“以谁的身份执行”

对于：

- Queue
- Scheduled Task
- Background Processing
- Event 后处理
- 异步服务
- 远程服务

不得模糊当前 Principal 语义。

设计时应明确：

- 是否继承提交用户身份
- 是否以系统身份执行
- 是否需要重新建立 Security Context
- 最终数据访问应遵循谁的权限
- 结果是否会暴露给原始用户

后台运行并不等于天然拥有 Administrator 权限。

具体行为必须根据 Windchill Framework 和项目设计确认。

---

## 16. Event / Listener 中不得随意改变安全上下文

Listener 或 Event Handler 通常运行在某个已有调用链中。

因此不得在 Listener 中：

- 无条件 setAdministrator
- 无条件关闭 Access Control
- 改变 Principal 后不恢复
- 假设事件一定由普通用户触发
- 假设事件一定由 Administrator 触发

如果 Listener 确实需要临时提升权限，应：

- 明确原因
- 将范围限制在局部
- 恢复原始 Context
- 考虑 Event 所在 Transaction 和调用链

具体 Event 设计由 Service / Event / Queue Rule 进一步约束。

---

## 17. Security Label 属于 Access Control 模型的一部分

如果对象启用了 Windchill Security Label，则普通 ACL 判断并不是唯一的安全条件。

处理 Security-Labeled Object 时，应考虑：

- 当前 Principal
- Security Label Name
- Security Label Value
- Participant 是否受到该 Label 限制
- Participant 是否允许修改该 Label
- 对象实际安全标签状态

不得通过绕过普通 ACL 就自动认为可以忽略 Security Label 语义。

如果项目启用了 Security Labels，安全相关 Customization 必须把它们纳入设计范围。

---

## 18. 自定义 Security Label Evaluator 必须保持 PTC Evaluator 语义

如果业务需要自定义 Security Label 判断逻辑，应优先使用 PTC 提供的 Security Label Evaluator 扩展机制。

不得自行在业务代码中重复实现一套与 Windchill Security Label Framework 并行的权限系统。

实现自定义 evaluator 时，应：

- 明确是判断“是否受限制”还是“是否允许修改 Label”
- 正确处理 Principal
- 正确处理 Label Name / Value
- 理解默认 evaluator 的行为
- 只有在业务要求明确时才覆盖默认逻辑
- 必要时复用 superclass 默认判断，而不是无意完全取代默认行为

如果 evaluator 访问外部系统或执行大量判断，应同时评估批量调用和性能。

---

## 19. Security Label Evaluator 不得假定总能收到完整 Persistable

Windchill Access Control Framework 在某些查询场景中可能使用 `AccessControlSurrogate` 代表真实 Persistable。

因此自定义安全 evaluator 不得无条件：

- cast 为具体业务 Class
- 调用只有完整 Persistable 才具备的方法
- 假定所有对象属性都已经加载

如果 evaluator 需要访问对象类型或其他属性，应首先判断实际传入对象是否为 surrogate，并仅使用该 Framework 明确提供的安全信息。

不得为了绕过 surrogate 而强制重新加载完整对象，除非已经确认这样做符合对应 PTC 扩展机制和性能要求。

---

## 20. 不得自行缓存授权结果而忽略安全上下文

Access Control 结果可能受到以下因素影响：

- Principal
- Group / Organization membership
- Object
- Domain
- Lifecycle State
- Security Label
- ACL 配置
- 其他运行时上下文

因此不得简单以：

`objectOid -> allowed`

建立长期全局缓存。

如果确实需要缓存安全判断结果，必须保证 cache key 和生命周期能够表达所有影响授权的关键上下文，并评估权限变化后的失效机制。

没有充分依据时，应优先让 Windchill Security Framework 完成授权判断。

---

## 21. 不得吞掉 Not Authorized 异常后继续操作

当 Windchill API 因权限不足拒绝操作时，不得：

1. 捕获授权异常
2. 忽略异常
3. 提升 Administrator
4. 重新执行
5. 对调用方表现为正常成功

除非该 fallback 本身就是经过明确批准的业务设计。

权限异常首先意味着：

`当前 Security Context 无权执行该操作`

Agent 应优先分析授权模型，而不是自动寻找绕过方式。

---

## 22. 权限异常不应暴露过多安全内部信息

向最终用户或外部调用方返回授权失败时，应避免泄露：

- 内部 Group 结构
- 管理员账号
- Security Label 内部配置
- Domain 结构
- ACL 内部实现
- 用户原本无权获知的对象信息

服务端日志可以保留适合诊断的上下文，但同时应遵守 Logging / Diagnostics Rule 中的敏感信息要求。

---

## 23. Security Context 不能依赖 Thread 外泄

Session Context、Principal 和 Access Control Enforcement 属于当前执行上下文的一部分。

如果代码：

- 创建新线程
- 使用 Executor
- 启动异步任务
- 将工作转移到 Queue

不得假定原线程中的 Security Context 会自动以正确方式传递到新的执行环境。

应使用 Windchill 官方支持的后台执行机制，并根据该 Framework 的安全语义重新确认执行 Principal 和 Access Control 状态。

不得自行复制 ThreadLocal 或内部 Session 数据模拟 Windchill Security Context。

---

## 24. 不得将 Access Control bypass 做成通用 Utility 默认能力

应避免创建这类容易被滥用的通用工具：

`runAsAdmin(Runnable)`

`disableAccessControl(Runnable)`

`executeWithoutPermissionCheck(...)`

如果项目确实需要统一封装安全上下文切换，应：

- 使用明确的语义名称
- 限制可调用范围
- 自动保证恢复
- 记录使用原因
- 避免成为所有权限问题的快捷方案
- 由项目架构设计确认

AI Agent 不得为了减少重复代码，自行引入一个全局“绕过权限”工具类。

---

## 25. Security API 必须经过目标版本验证

涉及以下类型 API 时，应通过目标 Windchill 版本的 Javadoc 或 API Lookup 验证：

- `SessionContext`
- `SessionHelper`
- `SessionServerHelper`
- `AccessControlHelper`
- `AccessPermission`
- `WTPrincipal`
- `SecurityLabeled`
- `UnrestrictedPrincipalEvaluator`
- `AccessControlSurrogate`
- 其他 Access Control / Security Label API

必须确认：

- Class 是否存在
- Method signature
- 参数含义
- Return type
- Throws
- Supported status
- 版本适用性

不得根据历史代码或模型记忆猜测安全 API。

对于影响 Principal 或 Access Control Enforcement 的 API，应特别谨慎，因为 API 误用可能扩大数据访问范围。

---

## 26. Access Control 代码修改后的检查

新增或修改 Security Context / Access Control 相关代码后，应根据任务范围检查：

- 当前代码预期以哪个 Principal 执行
- 是否保留了正常调用方权限语义
- 是否存在不必要的 Administrator 切换
- 是否存在不必要的 Access Control bypass
- 提升前的 Session Context 是否保存
- 异常情况下是否一定恢复原始 Context
- 原 Access Enforcement 状态是否保存并恢复
- 是否错误地假定原状态一定为 enabled
- 服务端敏感操作是否有正确权限判断
- 是否仅依赖 UI 或客户端做授权
- Query 是否无意绕过 Access Control
- bypass 后取得的数据是否会错误暴露给普通用户
- Background / Queue / Listener 执行 Principal 是否明确
- Security Label 是否影响当前对象
- 自定义 Evaluator 是否正确处理 AccessControlSurrogate
- 是否存在硬编码用户名或 Administrator 判断
- 是否将 Group / Role 判断错误替代 Object Permission
- 是否创建了容易滥用的通用 bypass Utility
- 所有安全相关 PTC API 是否经过目标版本验证

如果 Principal、ACL、Domain、Security Label 或 Background Security Context 行为必须依赖真实 Windchill Runtime 才能确认，而当前 Agent 无法访问对应环境，应明确标记：

`待 Windchill 环境验证`

并说明需要使用哪些用户、对象权限和执行场景进行验证。