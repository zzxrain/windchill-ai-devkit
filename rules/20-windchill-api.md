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

## 2. API 事实必须匹配目标 Windchill 版本

API 是否存在、签名、Deprecated、Supported 和 Extendable 状态，都必须以目标 Windchill 版本为准。

其他 Windchill 版本的资料只能作为线索，不得作为目标版本已经确认的证明。

不得在无法确认目标版本时静默假设版本。

## 3. 优先使用 Supported API 和正式扩展点

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

## 4. Unsupported API 不是绝对禁止，但必须显式识别风险

实际项目确有必要使用 Unsupported API 时，可以采用，但必须：

- 明确指出 Unsupported 或未知状态
- 说明采用原因
- 优先说明是否存在 Supported 替代方案
- 识别 Maintenance Update / Upgrade 风险

关键业务或高风险实现应由项目 SA 或技术负责人确认。

不得把“当前能够编译运行”解释为“PTC 官方支持”。

## 5. Deprecated API 不应成为新代码默认选择

新代码遇到 Deprecated API 时，应优先检查目标版本是否存在推荐替代方案。

修改历史代码时，如果无法确认替代方案行为兼容，不得为了“清理 Deprecated”而自行替换。

## 6. Classpath、历史代码和参考代码都不是 API 权威证明

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

精确产品事实应回到目标版本官方资料或 API Lookup。

## 7. 优先复用 Windchill 平台业务能力

涉及 Persistence、Versioning、Checkout、Lifecycle、Workflow、Access Control、Content、Structure、Queue、Event 等平台语义时，应先寻找相应的 Windchill Business API。

不得仅因为若干底层 API 能够拼出结果，就绕过已有的平台 Service 或正式业务语义。

## 8. 完成代码后验证实际使用到的 PTC API

至少确认本次新增或修改 API 的：

- Class / Method 是否真实存在
- Signature 和参数是否正确
- Return Type / Checked Exception 是否正确
- 目标版本是否匹配
- Supported / Extendable / Deprecated 状态是否符合预期

无法确认的部分必须明确说明，而不是声称已经验证。