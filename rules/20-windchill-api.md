---
trigger: model_decision
description: 当任务涉及 PTC Windchill Java API、wt.*、com.ptc.*、Windchill Service/Helper/Manager、继承 PTC 类、调用 Windchill 平台能力，或需要判断 Windchill 类型的继承/接口/Versioned/Iterated/Workable 等能力时应用本规则。
---

# Windchill API 使用规则

## 1. 不得猜测 PTC API

涉及 Windchill 专有 API 时，不得仅依据模型记忆或命名习惯生成不存在或未经确认的：

- Class / Interface
- Method / Constructor
- Method Signature
- Constant
- Service / Helper / Manager
- Extension Point

同样不得猜测某个 PTC 类型：

- 继承哪个父类
- 实现哪些 Interface
- 是否 Versioned
- 是否 Iterated
- 是否 Workable
- 是否 Mastered
- 是否支持某种平台能力

这些都属于目标版本 Exact API / Type Metadata。

无法确认时必须明确标记：

`UNVERIFIED PTC API`

不得把推测结果作为已经确认的代码或产品事实交付。

---

## 2. API 和产品行为事实必须匹配当前项目 Windchill Version

API 是否存在、签名、Deprecated、Supported 和 Extendable 状态，都必须以当前项目声明的 Windchill Version 为准。

以下描述同样属于需要证据支持的产品事实：

- 某 API 已经被另一个 API 正式替代
- 某 API 在某个版本已经 Removed / Deprecated / Unsupported
- 某 Extension Point 是官方推荐方案
- 某 Event 一定可以或不可以 Veto
- 某 Framework Callback 在特定阶段一定会被调用
- 某行为适用于全部 Windchill 13.x / 2027.x
- 某 Persistable 类型一定不支持 Version / Iteration
- 某业务 Number 一定只对应一个持久化对象实例

当前项目 Windchill Version 应优先从：

```text
AGENTS.md
Project Context
User Input
```

获取。

版本标识不得从以下内容自行推断：

- Javadoc ZIP 文件名
- 其他项目
- Golden Reference
- 当前模型知识
- 已安装的其他版本 API Index

其他 Windchill 版本资料只能作为线索，不得作为目标版本已经确认的证明。

不得在无法确认目标版本时静默假设版本。

---

## 3. Exact API Verification 是执行要求，不只是建议

当任务要求：

```text
生成代码
修改代码
Code Review
给出具体 PTC API 调用
```

并且最终答案将使用新的或被修改的具体 PTC Symbol 时，应判断是否需要 Exact API Verification。

需要验证的典型内容：

```text
Class
Interface
Method
Constructor
Signature
Parameter
Return Type
Throws
Constant
Supported
Extendable
Deprecated
Inheritance
Implemented Interfaces
Versioned / Iterated / Workable / Mastered capability
```

如果：

```text
目标 Windchill Version 已知
+
项目 Javadoc 已配置
+
API Lookup 可访问
```

则在最终回答前必须实际执行：

```text
ensure_javadoc_index
+
必要的 get_class / search_method / get_method
```

不得用：

> 建议你再检查 Javadoc。

替代 Agent 当前能够完成的 API Lookup。

只验证本次答案实际依赖的 Symbol，不需要扫描全部依赖。

如果 API Lookup 当前不可访问：

- 可以继续给出 Pattern-level 方案；
- 可以引用已经确认的 Framework Behavior；
- 但未经确认的具体 API 必须标记 `UNVERIFIED PTC API`；
- 不得声称“已按目标版本精确验证”。

---

## 4. 项目 Javadoc 自动索引

如果项目 `AGENTS.md` 配置了：

```text
PTC Javadoc / Javadoc ZIP
```

则需要精确 PTC API 事实时，应使用该 ZIP 为当前项目 Windchill Version 建立或复用本地 API Index。

推荐内部流程：

1. 读取 Project `Windchill Version`
2. 读取 Project `Javadoc ZIP`
3. 如果 Javadoc ZIP 使用项目相对路径，解析为绝对路径
4. 调用 `ensure_javadoc_index`
5. 索引成功后使用：
   - `get_class`
   - `search_method`
   - `get_method`
6. 只查询当前任务实际需要的 API

不得：

- 从 Javadoc 文件名猜测 Windchill Version
- 因本机已经存在其他版本索引而切换版本
- 在同版本不同 Javadoc Source 冲突时自动覆盖已有索引
- 在索引失败后把结果描述为已经验证

`ensure_javadoc_index` 建立本地派生缓存，不修改项目源码和 Javadoc ZIP。

如果索引已存在且来源一致，应直接复用。

如果自动索引失败，应保留错误，并将相关 API 标记为未验证。

---

## 5. 区分 API Metadata 与 Framework Behavior

Javadoc / API Lookup 适合确认：

```text
Class
Method
Signature
Return
Throws
Constant
Supported
Extendable
Deprecated
Inheritance
Interfaces
```

但不能仅凭 API Metadata 推导复杂 Framework Behavior。

例如：

```text
存在 PRE_STORE Constant
```

不能自动证明：

```text
PRE_STORE 一定 vetoable
```

又例如：

```text
存在 validateFormSubmission()
```

不能仅靠 Signature 自动推导：

```text
PROMPT_FOR_CONFIRMATION 的完整客户端交互
```

Framework Behavior 应使用：

```text
Target-version PTC Guide
QMind
Official Product Documentation
```

独立确认。

---

## 6. 优先使用 Supported API 和正式扩展点

存在合理方案时，应优先选择 PTC Supported API。

需要继承 PTC Class 时，应检查其 `Extendable` 状态，并优先评估 PTC 提供的：

- Service / Helper
- Delegate
- Interface
- Builder / Validator
- Listener
- Factory
- 其他正式 Extension Point

Java 能够访问或继承某个类，不代表它是稳定的 Customization API。

---

## 7. Unsupported API 不是绝对禁止，但必须显式识别风险

实际项目确有必要使用 Unsupported API 时，可以采用，但必须：

- 明确指出 Unsupported 或未知状态
- 说明采用原因
- 优先说明是否存在 Supported 替代方案
- 识别 Maintenance Update / Upgrade 风险

关键业务或高风险实现应由项目 SA 或技术负责人确认。

不得把：

```text
当前能够编译运行
```

解释为：

```text
PTC 官方支持
```

---

## 8. Deprecated API 不应成为新代码默认选择

新代码遇到 Deprecated API 时，应优先检查目标版本是否存在推荐替代方案。

修改历史代码时，如果无法确认替代方案行为兼容，不得为了“清理 Deprecated”而自行替换。

不得因为：

- 新版 Guide 示例使用另一个 API
- 当前项目更多代码使用另一个 API
- API 名称看起来更新
- 模型认为某写法“更现代”

就自行宣布旧 API 已 Deprecated 或被替代。

---

## 9. Classpath、历史代码和参考代码都不是 API 权威证明

以下内容可以作为线索或兼容性证据：

- 当前项目代码
- Windchill Classpath
- Golden Reference
- 历史项目
- 其他版本示例

但它们不能单独证明某个 API：

- 是 Supported
- 是推荐方案
- 适用于目标版本
- 会在升级后保持兼容
- 已经替代另一个 API

同样，当前代码或业务假设不能证明某个类型：

```text
一定是 / 不是 Versioned
一定是 / 不是 Iterated
一定只有一个持久化实例
```

这些应回到目标版本 Type Metadata 和产品语义。

---

## 10. 不得从业务唯一性推导对象版本模型

以下推导无效：

```text
业务 Number 唯一
        ↓
只有一条数据库记录
        ↓
对象不是 Versioned / Iterated
```

Windchill Business Identity 与 Version / Iteration Identity 是不同问题。

当 Query 结果数量、Latest、Version、Iteration 或 Master Identity 会影响实现时，应分别确认：

```text
对象 Type Metadata
+
Windchill Versioning Semantics
+
当前业务希望返回哪个层级
```

不得简单：

```text
qr.nextElement()
```

后就把第一条结果描述为唯一、最新或当前业务对象，除非对应语义已经得到独立证明。

---

## 11. 不同 Framework 之间不能推导 API 等价

例如：

```text
XWorks optional validation
```

不能仅通过语义类比推导：

```text
PTC OOTB Validator 一定存在完全等价的 Status / Method / Hook
```

同样：

```text
某 Golden Reference 使用一个 callback
```

不能自动证明：

```text
另一个 Event / Validation Phase 存在相同 callback 语义
```

结论必须使用对应 Framework / Phase / Version 的独立证据。

---

## 12. 优先复用 Windchill 平台业务能力

涉及：

- Persistence
- Versioning
- Checkout
- Lifecycle
- Workflow
- Access Control
- Content
- Structure
- Queue
- Event

等平台语义时，应先寻找相应 Windchill Business API。

不得仅因为若干底层 API 能够拼出结果，就绕过已有的平台 Service 或正式业务语义。

---

## 13. 完成代码前验证实际使用到的 PTC API

对本次新增或修改的 PTC API，最终回答前至少确认：

- Class / Method 是否真实存在
- Signature 和参数是否正确
- Return Type / Checked Exception 是否正确
- Constant 是否存在
- 目标版本是否匹配
- Supported / Extendable / Deprecated 状态是否符合当前设计要求
- 必要的 Type Capability 是否已经确认

如果工具可以验证：

```text
Agent 应自己验证
```

如果工具当前不能验证：

```text
明确标记 UNVERIFIED
```

不得一边输出确定性代码，一边把验证责任简单转交给用户。