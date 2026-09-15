---
trigger: model_decision
description: 当任务涉及 PTC Windchill Java API、wt.*、com.ptc.*、Windchill Service/Helper/Manager、继承 PTC 类或调用 Windchill 平台能力时应用本规则。
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

需要精确 API 事实时，应优先使用目标版本的 Javadoc / API Lookup。

无法确认时必须明确标记：

`UNVERIFIED PTC API`

不得把推测结果作为已经确认的代码交付。

## 2. API 和产品行为事实必须匹配当前项目 Windchill Version

API 是否存在、签名、Deprecated、Supported 和 Extendable 状态，都必须以当前项目声明的 Windchill Version 为准。

以下描述同样属于需要证据支持的产品事实：

- 某 API 已经被另一个 API 正式替代
- 某 API 在某个版本已经 Removed / Deprecated / Unsupported
- 某 Extension Point 是官方推荐方案
- 某 Event 一定可以或不可以 Veto
- 某 Framework Callback 在特定阶段一定会被调用
- 某行为适用于全部 Windchill 13.x / 2027.x

当前项目 Windchill Version 应优先从项目 `AGENTS.md` 获取。

版本标识不得从以下内容自行推断：

- Javadoc ZIP 文件名
- 其他项目
- Golden Reference
- 当前模型知识
- 已安装的其他版本 API Index

其他 Windchill 版本的资料只能作为线索，不得作为目标版本已经确认的证明。

不得在无法确认目标版本时静默假设版本。

不同官方示例采用不同的新旧 API 或 Coding Style，也不能单独证明：

```text
旧 API 已被正式替代
```

或：

```text
旧 API 已被 Deprecated / Removed
```

必须以目标版本官方资料或 Javadoc 状态为准。

## 3. 项目 Javadoc 自动索引

如果项目 `AGENTS.md` 配置了：

`PTC Javadoc / Javadoc ZIP`

则需要精确 PTC API 事实时，应使用该 ZIP 为当前项目 Windchill Version 建立或复用本地 API Index。

推荐流程：

1. 读取项目 `Windchill Version`
2. 读取项目 `Javadoc ZIP`
3. 如果 Javadoc ZIP 使用项目相对路径，先根据项目根目录解析为绝对路径
4. 调用 `ensure_javadoc_index`
5. 索引准备成功后，再使用 `get_class`、`search_method`、`get_method` 等查询工具

不得：

- 从 Javadoc 文件名猜测 Windchill Version
- 因本机已经存在其他版本索引而切换版本
- 在同版本不同 Javadoc Source 发生冲突时自动覆盖已有索引
- 在索引构建失败后把 API 结果描述为已经验证

`ensure_javadoc_index` 建立的是本地派生缓存，不修改项目源码和 Javadoc ZIP。

如果索引已存在且来源一致，应直接复用。

如果自动索引失败，应保留错误信息，并将相关 API 标记为未验证。

## 4. 优先使用 Supported API 和正式扩展点

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

## 5. Unsupported API 不是绝对禁止，但必须显式识别风险

实际项目确有必要使用 Unsupported API 时，可以采用，但必须：

- 明确指出 Unsupported 或未知状态
- 说明采用原因
- 优先说明是否存在 Supported 替代方案
- 识别 Maintenance Update / Upgrade 风险

关键业务或高风险实现应由项目 SA 或技术负责人确认。

不得把“当前能够编译运行”解释为“PTC 官方支持”。

## 6. Deprecated API 不应成为新代码默认选择

新代码遇到 Deprecated API 时，应优先检查目标版本是否存在推荐替代方案。

修改历史代码时，如果无法确认替代方案行为兼容，不得为了“清理 Deprecated”而自行替换。

不得因为：

- 新版 Guide 示例使用另一个 API
- 当前项目更多代码使用另一个 API
- API 名称看起来更新
- 模型认为某写法“更现代”

就自行宣布旧 API 已 Deprecated 或被替代。

## 7. Classpath、历史代码和参考代码都不是 API 权威证明

以下内容都可以作为线索或兼容性证据：

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

同样，不同 Framework 之间只能借鉴设计思想。

例如：

```text
XWorks optional validation
```

不能仅通过语义类比推导：

```text
PTC OOTB Validator 一定存在完全等价的 Status / Method / Hook
```

精确产品事实应回到目标版本官方资料或 API Lookup。

## 8. 优先复用 Windchill 平台业务能力

涉及 Persistence、Versioning、Checkout、Lifecycle、Workflow、Access Control、Content、Structure、Queue、Event 等平台语义时，应先寻找相应的 Windchill Business API。

不得仅因为若干底层 API 能够拼出结果，就绕过已有的平台 Service 或正式业务语义。

## 9. 完成代码后验证实际使用到的 PTC API

至少确认本次新增或修改 API 的：

- Class / Method 是否真实存在
- Signature 和参数是否正确
- Return Type / Checked Exception 是否正确
- 目标版本是否匹配
- Supported / Extendable / Deprecated 状态是否符合预期

无法确认的部分必须明确说明，而不是声称已经验证。