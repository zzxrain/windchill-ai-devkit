---
trigger: model_decision
description: 仅当当前项目已明确启用 XWorks，或项目代码、依赖、配置、AGENTS.md 中能够确认存在 XWorks 时应用本规则。项目未启用 XWorks 时，不得生成、引用或建议直接实现任何 XWorks 代码。
---

# XWorks 框架开发规则

## 定位

XWorks 是 PTC 实施团队在 Windchill Customization 机制之上形成的实施开发框架。

它不是所有 Windchill 项目的默认技术栈。

是否在项目中采用 XWorks，应由项目架构和实际需求决定。复杂表单、流程表单及相关实施扩展是评估采用 XWorks 的主要场景之一。

本规则只适用于已经明确采用 XWorks 的项目。

XWorks 不替代 Windchill 平台规则。以下专项 Rule 仍然优先适用：

- Windchill API
- Persistence / Transaction
- Versioning
- Access Control
- Service / Event / Queue
- Configuration
- UI / Web Extension
- Logging / Diagnostics

---

## 1. 未启用 XWorks 的项目不得使用 XWorks

如果当前项目没有明确启用 XWorks，AI Agent 不得：

- import `com.ptc.xworks.*`
- 生成依赖 XWorks 的 Java 代码
- 创建 XWorks 配置文件
- 使用 XWorks Annotation
- 使用 XWorks Listener Framework
- 使用 XWorks Workflow 扩展
- 使用 XmlObject / XmlObjectStoreManager
- 使用 XWorks WQL
- 增加 XWorks JAR 或部署配置

不得因为：

- 企业拥有 XWorks 部署包
- 其他项目使用过 XWorks
- XWorks 可以简化当前需求

就自动把 XWorks 引入当前项目。

如果复杂需求可能适合 XWorks，但当前项目尚未启用，只能在架构方案层提示：

`可由项目架构负责人评估是否引入 XWorks`

不得直接按照 XWorks 方案编码。

---

## 2. 必须先确认当前项目是否启用 XWorks

使用 XWorks 前，应优先从当前项目确认，例如：

- `AGENTS.md` 或项目架构文档明确声明
- 项目存在 XWorks JAR / dependency
- 已存在 `com.ptc.xworks.*` 代码
- 已存在 XWorks 配置目录
- 已存在 XWorks Spring / Action 配置
- 已存在 XWorks Form、Listener、Workflow 或 XmlObject 实现

如果无法确认，应按：

`项目未启用 XWorks`

处理，而不是自行假设可以使用。

---

## 3. XWorks 属于项目级技术选择，不属于 Windchill 强制规范

不得把：

`Windchill 项目`

自动推导为：

`应该使用 XWorks`

XWorks 主要用于解决复杂实施场景中的统一开发和管理问题。

对于简单需求，如果 Windchill OOTB、标准 JCA/MVC、配置或少量普通 Customization 已能合理完成，不应为了统一技术栈而强制引入 XWorks。

特别是没有复杂表单需求的项目，应避免仅为了使用框架而增加额外依赖和实施复杂度。

---

## 4. 已启用 XWorks 的项目应优先复用框架能力

如果项目已经采用 XWorks，并且框架已经提供对应能力，应优先评估已有的：

- Annotation
- Template Class
- Delegate
- Service
- Listener Interface
- Workflow Callback
- Helper / Utility
- Toolbox
- 配置机制

不得无必要重新建立与 XWorks 平行的：

- 表单持久化机制
- Listener 注册机制
- Workflow Callback 机制
- 属性访问 Utility
- 流程辅助数据管理机制

如果决定绕过已有 XWorks 能力，应有明确的项目技术原因。

---

## 5. 优先扩展 XWorks，不修改 XWorks 核心

项目需求应优先通过：

- XWorks 配置
- Annotation
- Interface
- Template
- Delegate
- Spring 扩展
- 预留扩展点

实现。

不得直接修改 XWorks Framework 核心代码作为普通项目定制方式。

如果当前项目确实维护自己的 XWorks Patch / Fork，必须以项目明确的版本管理和升级策略为准。

同样不得因为使用 XWorks 而绕过 PTC Windchill OOTB 的正常 Customization 机制。

---

## 6. 复杂表单场景优先评估 XWorks Form Framework

当项目已经启用 XWorks，并存在以下需求时，应优先评估 XWorks Form Framework：

- 复杂流程表单
- 多区域或多明细表格表单
- 表单数据需要独立持久化
- 表单数据需要与 Windchill PBO 建立关联
- 表单需要统一创建、编辑、查询和验证机制
- 多个流程或业务场景需要复用表单基础能力

应优先使用 XWorks 已有的：

- XmlObject 数据模型
- Form Builder Template
- FormProcessorDelegate
- Workflow Form Delegate
- Annotation 驱动的字段配置

不得在已经采用 XWorks Form Framework 的项目中，再自行建立另一套重复的复杂表单基础框架。

---

## 7. XWorks 表单数据应使用 XmlObject 数据层

对于设计为 XWorks 表单数据的 JavaBean，应优先使用：

- `XmlObject`
- `XmlObjectMarker`
- `XmlObjectStoreManager`
- XWorks 提供的关联和 Store API

进行数据管理。

不得为同一类 XWorks 表单数据另外编写 JDBC 或直接 SQL CRUD。

属性是：

- 独立字段
- XML 持久化字段

应根据查询、索引和业务扩展需求决定，而不是机械采用单一方式。

---

## 8. XmlObject 不得替代 Windchill 核心 PLM 对象

XWorks XmlObject 主要用于：

- 流程表单数据
- 实施项目辅助业务数据
- 与 Windchill PBO 关联的扩展数据

不得因为 XmlObject 开发更简单，就用它替代需要 Windchill 核心业务语义的对象，例如：

- WTPart
- WTDocument
- EPMDocument
- Change Object
- 其他需要 Versioning、Lifecycle、Access Control 或标准业务行为的数据

是否使用 XmlObject，应根据业务对象生命周期和平台语义决定。

---

## 9. XWorks 表单仍必须遵守服务端校验和事务语义

客户端 JavaScript 校验不能替代服务端验证。

XWorks FormProcessor / Delegate 中仍应根据业务需要确认：

- 输入合法性
- 当前对象状态
- Access Control
- Version / Working Copy
- 数据合并规则
- Transaction Boundary

不得因为 XWorks 已封装 FormProcessor，就假设安全、事务和业务校验已经自动正确。

复杂事务遵守：

`30-persistence-query-transaction.md`

安全语义遵守：

`40-access-control-security-context.md`

---

## 10. XWorks Workflow 扩展优先替代散落的 Workflow Java Expression

在已经启用 XWorks Workflow 扩展的项目中，应优先使用：

- Transition Trigger
- WorkItem Callback
- Robot Expression
- Routing Expression
- Workflow Definition / Annotation

承载可复用的流程业务逻辑。

应避免继续将大量 Java 代码直接嵌入：

- Workflow Expression Robot
- Connector Expression
- Activity Transition

业务逻辑应尽可能进入可测试、可复用和可配置的 Java Class。

---

## 11. XWorks Listener 必须集中注册和管理

如果项目已经启用 XWorks Listener Framework，新增 Windchill Event Listener 时，应优先：

1. 实现对应 XWorks Listener Interface
2. 保持 Listener Class 职责单一
3. 在 `listeners.conf` 中集中注册

不得再无必要地将新的 Listener 注册分散到多个自定义 Service 中。

新增 Listener 前必须检查：

- 当前 `listeners.conf`
- 已存在 Listener Class
- 相同 Event
- 相同对象类型
- 相同业务目的

避免：

- 重复注册
- 同一业务重复执行
- Listener 相互干扰
- Listener 递归触发
- 一个 Listener 承担过多无关业务

XWorks 只负责 Listener 的组织和注册管理。

Windchill Event 本身的同步、Transaction、Veto 等语义仍遵守：

`50-service-event-queue.md`

---

## 12. XWorks 配置属于框架控制面

开发或修改 XWorks 功能时，不能只检查 Java 代码。

应根据任务同时检查相关配置，例如：

- `listeners.conf`
- `xmlobject.classes.conf`
- `workflowTemplateDef.conf`
- `workflowForms.conf`
- `promotionNoticeOptions.conf`
- XWorks Spring 配置
- XWorks Property / XCONF
- Action / ActionModel 配置

新增实现时，应确认是否需要注册。

删除实现时，应确认是否存在遗留注册。

不得形成：

`Java Class 已删除，但配置仍然激活`

的隐蔽行为。

---

## 13. 优先复用经过项目验证的 XWorks Utility

项目已启用 XWorks 且存在适合的公共能力时，应优先评估：

- `AttributesHelper`
- `XWorksHelper`
- Related Object Service
- ACL Toolbox
- Container Team Toolbox
- Object Type / Attribute Toolbox
- 其他项目已验证的 XWorks Utility

避免重复创建行为不一致的：

- IBAUtil
- AttributeUtil
- WindchillUtils
- CommonUtils

但 XWorks Utility 只是实现复用手段，不能绕过 Windchill API、权限、事务或版本语义。

---

## 14. WQL 只负责简化查询表达

XWorks WQL 可用于简化 QuerySpec / StatementSpec 构造。

但它不改变 Windchill Persistence 和 Access Control 语义。

不得因为使用 WQL 就默认：

- 查询一定经过 Access Control
- Advanced Query 一定安全
- non-access-controlled query 可以直接使用
- 原生 SQL Expression 不存在注入或安全风险

使用 WQL 时仍必须遵守：

`30-persistence-query-transaction.md`

和：

`40-access-control-security-context.md`

动态查询参数不得直接拼接不可信外部输入。

---

## 15. XWorks 版本必须以项目实际部署包为准

企业当前持有并使用经过项目验证的 XWorks 13.0.2 部署包。

对于 Windchill 13.0.2 项目，如果项目明确采用该部署包，可以将其作为当前项目 XWorks 实现和兼容性的高优先级证据。

但不得因此推导：

- 所有 Windchill 13.x 都兼容
- XWorks 13.0.2 可直接用于 13.1 或其他版本
- 历史 XWorks 文档中的所有 API 与 13.0.2 完全一致
- XWorks 属于 PTC Windchill 公共 Supported API

生成 XWorks 代码时，应优先依据：

1. 当前项目实际 XWorks 代码和依赖
2. XWorks 13.0.2 部署包及其 JavaDoc / 示例
3. 企业已验证的 XWorks 项目实现
4. XWorks 历史实施文档

无法确认具体 Class、Method、Annotation 或配置时，应标记：

`UNVERIFIED XWORKS API`

不得根据模型记忆猜测 XWorks API。

---

## 16. XWorks 示例不能直接等同于项目标准

XWorks 文档和示例代码属于高价值实施参考，但不得机械复制。

使用示例前，应确认：

- 对应 XWorks 版本
- 对应 Windchill 版本
- 当前项目是否启用了相同模块
- 是否符合当前企业 Rules
- 是否存在新的项目实现方式

示例中的 SQL、WQL、Listener、Workflow、表单或 Utility 用法如果与更高优先级 Rule 冲突，应以企业 Rule 和当前项目架构为准。

---

## 17. XWorks 不改变 Windchill 核心平台边界

即使 XWorks 已经封装某项能力，仍必须遵守 Windchill 的：

- Access Control
- Version / Iteration
- Checkout / Checkin
- Transaction
- Lifecycle
- Event
- Queue
- Container
- Configuration
- Logging

XWorks 可以统一和简化实现，但不能成为绕过 Windchill 平台语义的理由。