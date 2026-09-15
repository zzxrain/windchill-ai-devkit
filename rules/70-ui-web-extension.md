---
trigger: model_decision
description: 当任务涉及 Windchill JCA、MVC、ComponentBuilder、TableBuilder、AttributePanel、DataUtility、UI Validator、FormProcessor、Action、ActionModel、Wizard、JSP 或 Information Page 定制时应用本规则。
---

# Windchill UI 与 Web 扩展规则

## 1. 优先使用 Windchill 正式 UI 扩展机制

实现 Windchill UI 功能时，应优先评估已有的：

- JCA / MVC Component
- ComponentBuilder
- Table / AttributePanel
- DataUtility
- UI Validator
- FormProcessor
- Action / ActionModel
- Wizard
- Information Page 扩展点

不得为了快速实现页面功能而绕过现有 Windchill UI Framework，自行建立一套与平台割裂的控制器和页面机制。

具体 API 和扩展点必须与目标 Windchill 版本匹配。

---

## 2. Component Config 与 Component Data 职责必须区分

MVC Builder 中应保持配置和数据职责清晰：

- `ComponentConfigBuilder` 负责描述组件结构、列、属性、显示方式等 UI 配置
- `ComponentDataBuilder` 负责获取组件所需业务数据

不得无必要地在 Config 构建过程中执行大量：

- Persistence Query
- Remote Call
- 业务修改
- 数据库写操作

如果 Config 与 Data 之间需要传递请求级数据，应优先使用 Framework 提供的 `ComponentParams` 或 Config，而不是 Builder 实例字段。

---

## 3. Builder 必须按 Singleton / 多线程语义设计

Windchill MVC Builder 默认可能以 Singleton 方式被多个请求并发使用。

因此不得在 Builder 实例字段中保存：

- 当前用户
- 当前对象
- Request
- ComponentParams
- 查询结果
- 页面临时状态
- 其他请求级可变数据

请求级数据应通过方法参数、`ComponentParams` 或对应 Framework Context 传递。

不得假设一次 Builder 实例只服务一个用户或一个请求。

---

## 4. UI 层不得承担完整业务服务职责

Builder、DataUtility、Validator、FormProcessor、JSP 等 UI 扩展点应主要负责其对应的 UI / 请求职责。

包含以下特征的业务操作应优先进入明确的服务端业务层：

- 多个业务对象修改
- 复杂事务
- Version / Checkout / Checkin
- Access Control
- 可由多个入口复用
- 与 UI 无关的核心业务规则

不得把核心业务规则分别复制到多个 Builder、Validator 或 FormProcessor 中。

Service / Transaction 行为遵守：

`30-persistence-query-transaction.md`

和：

`50-service-event-queue.md`

---

## 5. UI Validator 不能替代服务端授权

UI Validator 可用于决定 Action 或 UI Component 的：

- ENABLED
- DISABLED
- HIDDEN
- PERMITTED
- DENIED

等界面行为。

但 UI 可见性和可操作性不等于最终安全授权。

不得因为 Action 已被 Validator 隐藏或禁用，就省略真正的服务端 Access Control 或业务校验。

`validateFormSubmission()` 虽然运行在服务端，可以作为 Wizard / UI 提交阶段的重要校验点，但仍不能自动替代：

- FormProcessor 中必要的输入重验
- Service Boundary 中的最终授权
- 对象当前状态检查
- Version / Working Copy 检查
- 核心业务不变量

敏感操作的最终授权必须在真正执行该业务操作的可信服务端边界完成。

不同 Validation Phase 支持的 Method、Status 和客户端行为不得互相类推。

例如某个 Post-select Validator 支持：

```text
PROMPT_FOR_CONFIRMATION
```

不能因此自动推导：

```text
validateFormSubmission()
```

阶段也存在完全相同的交互能力。

精确行为必须以目标版本 Windchill API / Guide 为准。

遵守：

`40-access-control-security-context.md`

---

## 6. FormProcessor 必须重新验证客户端输入

FormProcessor / Action Command 不得信任：

- Hidden Field
- URL Parameter
- JavaScript 校验结果
- 客户端传入的 OID
- 用户名、Role 或权限标志
- 客户端声明的业务状态

服务端应重新确认完成业务操作所必需的：

- 输入合法性
- 对象身份
- 对象当前状态
- 权限
- Version / Working Copy
- 业务约束

复杂业务操作应调用服务层，而不是全部直接实现在 FormProcessor 中。

---

## 7. DataUtility 应保持表示层职责

DataUtility 主要用于将对象或属性转换成 Windchill UI 所需的显示 / 编辑组件。

不得无必要地在 DataUtility 中执行：

- 数据修改
- Checkout / Checkin
- 创建业务对象
- 大量数据库查询
- 长时间远程调用

DataUtility 可能在表格大量行和属性渲染过程中反复执行。

如果需要额外数据，应特别注意 N+1 查询和页面性能。

当目标版本支持相应模式时，应优先：

```text
setModelData()
    ↓
针对待处理对象集合批量准备数据
    ↓
getDataValue()
    ↓
读取已准备的数据并完成 UI 渲染
```

批量准备不等于必须把所有数据压成一个查询。

应根据：

- 对象数量
- Query 条件
- 数据库参数限制
- Windchill Persistence 语义

决定一次或少量批量调用。

如果 DataUtility 使用实例字段保存预取结果，必须同时确认其注册和生命周期不会让多个无关请求共享该可变状态。

不得把 Builder 的 Singleton 语义或 DataUtility 的实例生命周期相互混淆。

具体 DataUtility lifecycle / cardinality 行为必须以目标 Windchill 版本配置和官方资料为准。

---

## 8. Action / ActionModel 应使用 Windchill 配置机制

新增或修改 Action、ActionModel、Wizard Step 或组件注册时，应使用目标版本 Windchill 支持的配置方式。

不得：

- 直接修改 PTC 标准 Action 配置作为默认方案
- 猜测 Action Name、Object Type 或 Component ID
- 在多个 JSP 中复制硬编码 URL 来代替 Action Framework

自定义配置文件的维护和传播同时遵守：

`60-configuration-customization-files.md`

---

## 9. UI 文本应使用 ResourceBundle

面向用户的：

- Label
- Title
- Message
- Validation Feedback
- Action 文本

应优先通过 Windchill ResourceBundle / Localization 机制提供。

不得把大量用户可见文本直接硬编码在 Java、JSP 或 JavaScript 中。

需要根据用户 Locale 展示内容时，应使用客户端 Locale 对应的 Windchill 国际化机制，而不是默认服务器 Locale。

---

## 10. UI 数据量和渲染成本必须受到控制

Table、Tree、Picker 或其他列表型组件可能面对大量 Windchill 数据。

不得为了展示页面而默认：

- 查询全部对象
- 一次性加载全部记录
- 在每一行执行独立数据库查询
- 在每个 Cell 重复执行昂贵业务逻辑

查询和分页行为遵守：

`30-persistence-query-transaction.md`

---

## 11. 优先使用 Windchill 提供的调试能力

排查 JCA / MVC 页面问题时，应优先使用目标版本支持的诊断能力，例如：

- `jcaDebug`
- 对应 JCA / MVC Log4j Logger
- Browser JavaScript Logging
- Framework 已提供的调试信息

不得为了诊断问题长期把大量临时输出写入生产代码。

具体 Logging 要求遵守：

`80-logging-diagnostics.md`