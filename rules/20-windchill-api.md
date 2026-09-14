---
trigger: model_decision
description: 当任务涉及 PTC Windchill Java API、wt.*、com.ptc.*、Windchill Service/Helper/Manager、继承 PTC 类、调用 Windchill 平台能力、分析或生成 Windchill 专有 Java 代码时应用本规则。
---

# Windchill API 使用规则

## 目的

本规则用于约束 AI Agent 在 Windchill 二次开发过程中对 PTC Java API 的选择、验证、生成和修改行为。

重点确保：

- 不凭空生成 Windchill API
- 优先采用适合 Customization 使用的 API 和扩展机制
- 正确理解 Supported、Extendable 和 Deprecated 状态
- 识别 Windchill 版本差异
- 降低对 Windchill 内部实现的无意识依赖
- 对无法确认的 PTC API 明确表达不确定性

本规则主要针对 Windchill Java API。

Persistence、Transaction、QuerySpec、Access Control、JCA、WRS 等专项技术要求由对应 Rule 进一步定义。

---

## 1. Windchill API 必须基于实际证据

不得仅依据模型记忆生成 Windchill 专有 API。

涉及以下内容时，应优先从当前项目、目标版本 Javadoc、企业知识库或经过验证的参考实现中确认：

- Java Class
- Interface
- Method
- Constructor
- Method Signature
- Static Field
- Constant
- Annotation
- Service
- Helper
- Manager
- Delegate
- Factory
- Extension Point
- Event
- Listener
- Property Name
- API 使用方式

特别是 `wt.*` 和 `com.ptc.*` 下的 API，不得因为名称看起来符合 Windchill 命名习惯而推测其存在。

如果无法确认某个 API 是否真实存在，应明确标记：

`UNVERIFIED PTC API`

不得将推测出的 API 作为确定代码直接交付。

---

## 2. 优先使用 Windchill Supported API

在存在合理选择的情况下，应优先使用 PTC 定义的 Windchill Supported API。

对于目标 API，应根据目标 Windchill 版本的 Javadoc 检查：

- Class 是否为 `Supported: true`
- Method 是否为 `Supported: true`
- Class 是否为 `Extendable: true`
- API 是否为 Deprecated
- API 是否属于目标 Windchill 版本

需要特别注意：

- Class 可以是 Supported，但其中某个 Method 仍可能不是 Supported。
- 如果 Class 本身不是 Supported，其内部 Method 也不能因为能够调用而被视为 Supported API。
- 只有明确标记为 `Extendable: true` 的 PTC Class，才属于 PTC 明确允许扩展的类。

Supported API 应作为首选，而不是唯一可用范围。

在实际项目确有必要使用 Unsupported API 时，不应机械禁止，但必须：

1. 明确指出其 Unsupported 状态；
2. 说明使用原因；
3. 评估 Maintenance Update 和 Upgrade 风险；
4. 如果存在 Supported 替代方案，应优先说明替代方案；
5. 对关键业务实现，建议由项目 SA 或技术负责人确认。

不得把“当前版本能够编译和运行”解释为“PTC 官方支持”。

---

## 3. 不得将 Classpath 可见性等同于 API 可用性

某个 Class、Method 或第三方组件存在于 Windchill Classpath 中，只说明当前 Runtime 能够加载它。

这不等同于：

- PTC 明确支持 Customization 使用
- API 在后续 Maintenance Release 中保持兼容
- API 在后续 Windchill Release 中保持兼容
- API 属于稳定公共接口

对于 Windchill 内部实现类、内部 Service、内部 Utility 或底层第三方 Library，应避免仅因为当前版本能够 import 就直接使用。

如果必须依赖此类 API，应明确识别其兼容性风险。

---

## 4. 继承 PTC Class 前必须确认扩展能力

AI Agent 不应仅因为某个 PTC Class：

- 不是 `final`
- 具有 `protected` Method
- 可以被 Java 编译器继承

就认为该 Class 适合 Customization 扩展。

继承 PTC Class 前，应优先检查目标版本 Javadoc 中：

`Extendable: true`

如果 `Extendable: false` 或无法确认：

- 优先寻找 PTC 提供的 Delegate、Service、Builder、Validator、Listener、Interface 或其他 Extension Point；
- 如果项目确有必要继承，应明确指出该实现存在升级和兼容风险。

Java 语言允许继承，不代表 PTC 将其定义为稳定扩展点。

---

## 5. 使用 Deprecated API 时应主动寻找替代方案

如果目标 Windchill 版本 Javadoc 将 Class 或 Method 标记为 Deprecated：

1. 不应在新代码中无条件继续采用；
2. 应查找 PTC 推荐的替代 API；
3. 应检查当前项目是否由于版本兼容等原因仍必须保留；
4. 修改历史代码时，不应为了重构而无条件替换 Deprecated API，除非能够确认替代方案及行为兼容性。

如果无法确认替代 API，应保留现有行为并明确指出风险，而不是自行推测新的 PTC API。

---

## 6. API 判断必须匹配目标 Windchill 版本

不得使用其他 Windchill 版本的 Javadoc 作为目标环境 API 存在性的最终证明。

在进行 PTC API 判断时，应首先获取目标 Windchill 版本。

例如：

- 12.1
- 13.0.2.0
- 13.1.2.0

以下情况必须特别注意版本差异：

- 新增 API
- Deprecated API
- Removed API
- Method Signature 变化
- 新增 Extension Point
- JCA/MVC Framework
- WRS
- Workflow
- Search
- Service Infrastructure
- Configuration API

如果只能取得其他版本资料，应明确指出版本不匹配，不得将其描述为目标版本已经确认。

---

## 7. 优先使用 Windchill 已有平台能力

实现 Windchill 业务能力时，应首先寻找 Windchill 已有的：

- Helper
- Service
- Manager
- Delegate
- Factory
- Domain Interface
- Builder
- Validator
- Listener
- Framework API
- 官方 Extension Point

不要为了完成业务操作而自行重复实现 Windchill 已有的平台逻辑。

尤其涉及以下领域时，应优先理解 Windchill 对应的平台语义：

- Persistence
- Version / Iteration
- Checkout / Checkin
- Lifecycle
- Workflow
- Access Control
- Container
- Content
- Ownership
- Change Management
- Structure
- Queue
- Event

不得因为直接组合若干底层 API 可以实现功能，就忽略 Windchill 已经提供的更高层业务 API 或 Service。

---

## 8. 区分业务对象与业务服务

设计新的 Windchill 服务端逻辑时，应避免把复杂业务规则直接堆积到 UI、FormProcessor、Listener 或业务对象中。

应根据实际场景考虑使用 Windchill Service / Manager 模式封装具有完整业务语义的操作。

特别是包含以下特征的操作：

- 多个持久化步骤
- 多个业务对象
- 事务一致性要求
- 权限语义
- 状态变更
- 可被多个入口复用

应优先形成明确的业务服务边界，而不是由多个调用方分别组合底层 API。

---

## 9. 历史项目 API 只能作为参考证据

发现当前项目已经使用某个 PTC API 时，可以将其作为：

- API 存在性的线索
- 当前项目兼容性的证据
- 历史实现方式的参考

但不得自动得出：

- 该 API 是 Supported API
- 该 API 是当前推荐方案
- 该 API 适用于目标 Windchill 新版本
- 新代码应该继续使用相同实现

如果历史代码使用 Unsupported、Deprecated 或明显内部 API，应保留风险意识。

对于新代码，应优先寻找更稳定的官方 API 或项目已批准方案。

---

## 10. Golden Reference 不能代替 API 真实性验证

`windchill-customization-reference` 中经过审核的代码可以作为高优先级实现参考。

但 Golden Reference 仍然具有版本适用范围。

使用参考代码时应确认：

- 参考代码对应的 Windchill 版本
- 当前目标版本
- 涉及 API 在目标版本中的状态
- 是否存在版本差异

不得因为某段代码属于 Golden Reference，就假设其中所有 PTC API 永久兼容所有 Windchill 版本。

---

## 11. API 不确定时的处理顺序

当 Agent 无法确认某个 Windchill API 时，按照以下顺序处理：

1. 检查当前项目依赖和可解析的 Class / Method
2. 检查与目标 Windchill 版本匹配的 Javadoc
3. 检索公司批准的 Windchill 企业知识库
4. 检查与目标版本匹配的 Golden Reference
5. 检查当前项目中经过实际使用的实现
6. 如果仍然无法确认，则标记：

   `UNVERIFIED PTC API`

不要为了完成代码而自行构造一个“可能存在”的 Windchill API。

---

## 12. 使用 Unsupported API 时的输出要求

如果最终方案需要使用 Unsupported API 或无法确认 Supported 状态的 API，应向开发人员明确说明：

- 使用的 Class / Method
- 当前已知的 Supported / Extendable 状态
- 使用该 API 的原因
- 是否存在 Supported 替代方案
- Maintenance Update / Upgrade 风险
- 当前证据来源

如果项目存在专职 SA，对于关键业务逻辑或高风险 Unsupported API，建议由 SA 确认后再作为正式方案使用。

---

## 13. API 代码生成完成后的检查

涉及新增或修改 PTC API 调用时，应至少检查：

- Class 是否真实存在
- Method 是否真实存在
- Method Signature 是否正确
- 参数类型是否正确
- Return Type 是否正确
- Checked Exception 是否正确处理
- API 是否与目标 Windchill 版本匹配
- Supported / Extendable / Deprecated 状态是否已知
- 是否存在更合适的 Windchill 平台 API
- 是否无意引入内部 API 或第三方底层实现

如果当前开发环境无法完成其中某项确认，应明确指出尚未验证的内容。