---
trigger: always_on
---

# Windchill AI 辅助开发基础规则

本规则定义 AI Agent 在 Windchill 二次开发中的基础行为约束。

专项技术要求由对应 Rule 定义；当专项 Rule 与本规则存在更具体的要求时，优先遵循专项 Rule。

## 1. 遵循正确的规则与证据优先级

判断“代码应该如何实现”时，优先级为：

1. 企业强制性的安全、合规、架构和开发要求
2. 当前项目已批准的例外、架构决策和客户明确要求
3. 企业 Windchill 开发规则
4. Approved Golden Reference
5. Candidate Golden Reference
6. 当前项目已有实现
7. 模型自身知识

Approved Golden Reference 可以作为企业认可的实现模式依据。

Candidate Golden Reference 可以作为模式识别、设计参考和初始实现依据，但不得描述为企业最终批准实现或目标项目 Runtime Verified。

现有项目代码属于兼容性和经验依据，不自动等同于正确规范。

如果历史实现与更高优先级规则冲突，不得仅因为“项目以前就是这样写的”而继续复制。

对于 Windchill 产品事实，应优先依据与目标版本匹配的 PTC 官方资料、Javadoc / API Lookup 和批准的企业知识源，而不是模型记忆或历史代码。

---

## 2. 优先使用 Windchill OOTB、配置和正式扩展机制

引入自定义代码前，应优先评估：

1. Windchill OOTB 能力
2. Windchill 配置能力
3. PTC 提供的正式扩展机制
4. 自定义代码

在能够满足需求的情况下，优先选择侵入性更低、升级影响更小的方案。

不得为了使用代码而重复实现 Windchill 已有的平台能力。

正常情况下，不得直接修改或替换 PTC 标准 Java 类、运行时实现或标准文件。

---

## 3. Windchill 版本属于开发上下文

Windchill API、JDK、扩展机制和产品行为可能随版本变化。

涉及版本敏感能力时，应优先从以下上下文确定目标版本：

- 项目 `AGENTS.md`
- 项目配置或依赖
- 项目文档
- 用户明确提供的信息

不得在没有依据的情况下默认某个 Windchill 版本。

如果版本未知且可能影响方案正确性，应明确指出该不确定性。

---

## 4. 保持 Windchill 平台语义

不得为了让代码“能够运行”而绕过 Windchill 的核心平台语义。

根据任务需要，应考虑：

- Persistence / Transaction
- Version / Iteration / Working Copy
- Access Control / Principal / Session Context
- Container
- Lifecycle / Workflow
- Event / Queue / Background Processing
- 对象关系和业务 Service

这些领域的具体要求遵循对应专项 Rule。

不得使用直接 SQL 修改 Windchill 管理的业务数据来替代正常 Windchill API，PTC 官方明确要求的特殊维护或升级场景除外。

---

## 5. 坚持最小必要定制

只实施完成当前需求所必需的修改。

除非任务明确要求，不得顺带：

- 大范围重构
- 更换框架
- 新增基础设施
- 创建无必要的抽象层
- 修改公共 API
- 大规模调整 Package 或配置结构
- 处理与当前任务无关的历史技术债

应尽量保持已有业务行为、数据模型和外部接口兼容性。

不要为没有明确需求的未来场景提前设计复杂扩展。

---

## 6. 谨慎引入第三方运行时依赖

AI Agent 不得自行新增第三方 JAR、Framework 或其他运行时依赖。

需要新依赖时，应优先确认：

1. JDK 是否已有能力
2. Windchill 是否已有正式 API 或扩展机制
3. 项目是否已有批准的组件

确实需要新增依赖时，应向开发人员说明必要性，以及主要的：

- Windchill / JDK 兼容风险
- Classpath / ClassLoader 冲突风险
- Upgrade / Maintenance Update 风险
- Security / License 风险

未经项目技术负责人或相应架构角色确认，不应直接将新的运行时依赖加入项目。

不得因为某个第三方类已经存在于 Windchill Classpath 中，就自动认为它适合 Customization 代码依赖。

---

## 7. 修改前理解项目上下文

修改现有代码前，应先检查与当前任务直接相关的：

- 当前实现及调用关系
- 项目已有类似实现
- 对象类型和业务语义
- 项目 Rules / AGENTS.md
- 相关 Windchill API 和扩展机制

不要仅根据单个代码片段就进行大范围修改。

如果发现与当前任务无关的历史问题，应指出但不要顺带全面重构。

---

## 8. 只声明真正完成的验证

完成任务后，应执行当前环境能够实际完成的验证，例如：

- 编译或语法检查
- 自动化测试
- 静态检查
- Git Diff / 修改范围检查

不得声称执行了实际未执行的验证。

如果某项行为必须依赖真实 Windchill Build、部署或 Runtime 环境确认，而当前 Agent 无法访问该环境，应明确标记：

`待 Windchill 环境验证`

并指出需要验证的关键行为。

“代码已实现”不等同于“Windchill 运行验证通过”。

必须区分以下证据和验证层次：

```text
Implementation Pattern Evidence
API Metadata Verification
Compile Verification
Runtime Verification
```

其中：

- PTC Guide、Golden Reference 可以为实现模式提供依据；
- 目标版本 Javadoc / API Lookup 用于精确 API Metadata；
- 真实目标 Classpath Build 用于 Compile Verification；
- 实际 Windchill 环境中的部署和操作用于 Runtime Verification。

不得把前一层证据描述成后一层验证已经完成。

---

## 9. 不得用猜测掩盖 Windchill 产品事实的不确定性

遇到 Windchill 专有技术事实不确定时，应优先：

1. 检查当前项目上下文
2. 使用适用的专项 Rules
3. 根据事实类型选择正确证据源
4. 查询目标版本 Javadoc / API Lookup
5. 检索批准的企业 Windchill 知识源
6. 检查适用的 Golden Reference

如果仍无法确认，应明确区分：

- 已确认事实
- 有依据的推断
- 尚未确认的假设

不得为了完成代码而虚构 PTC API、配置项、扩展点或产品行为。

---

## 10. 自主选择最小充分证据源

用户只需要描述实际 Windchill 开发问题，不需要了解或显式点名 DevKit 内部组件。

用户无需在 Prompt 中要求：

```text
使用 Rules
查询 Golden Reference
查询 QMind
查看 PTC Customization Guide
调用 API Lookup
```

Agent 应根据任务本身自主判断需要哪些证据源。

默认职责划分：

```text
项目事实 / 项目约束
→ AGENTS.md / Project Code / ADR

代码必须或不得怎么实现
→ Rules

同类实现通常怎么写
→ Golden Reference

Windchill / XWorks 产品行为、Framework Contract、
配置机制、生命周期和官方扩展语义
→ QMind / 目标版本官方产品资料

PTC Class / Method / Signature / Return / Throws /
Supported / Extendable / Deprecated 等精确 API Metadata
→ 目标版本 Javadoc / API Lookup

代码是否在目标依赖中成立
→ Compile / Build

真实 Event、Transaction、UI、Queue、Workflow、
Access Control 等运行行为是否成立
→ Windchill Runtime Verification
```

这些证据源不能机械互相替代。

例如：

- Golden Reference 中出现某个 API，不自动证明它在目标版本属于 Supported API；
- Customization Guide 展示某个 Method，不自动等同于完成目标版本精确 Signature 验证；
- Javadoc 中存在一个 Method，不自动证明某个 Framework Behavior 一定成立；
- 当前项目已有代码能运行，不自动证明它属于 PTC Supported API；
- 静态检查通过，不自动等同于真实编译；
- 编译通过，不自动等同于 MethodServer Runtime Verification。

Agent 应使用完成当前任务所需的最小充分证据集合。

不得为了展示 DevKit 能力而对每个请求机械调用：

```text
QMind
+
Golden Reference
+
API Lookup
+
所有 Rules
```

简单任务可以只使用项目上下文和适用 Rules。

只有当实现模式、产品事实或精确 API Metadata 确实影响当前结论时，才应增加对应证据源。

---

## 11. 默认静默执行内部证据编排

Rules、Golden Reference、QMind、API Lookup 等属于 Agent 内部能力。

普通开发任务中，默认不要向用户逐步播报：

```text
我先加载 Skill
我先读取 Registry
我现在选择 QMind
我现在读取 Golden CATALOG
我现在调用 API Lookup
```

应优先直接给出：

- 结论；
- 实现方案；
- 必要代码；
- 关键风险；
- 尚未完成的验证。

以下情况可以简要暴露证据来源：

- 用户要求解释依据；
- Code Review 需要可追溯性；
- 产品版本或 API 状态会影响关键结论；
- 多个实现存在重要架构取舍；
- 证据冲突；
- 某项关键事实仍为 `UNVERIFIED`；
- 用户正在诊断 DevKit 本身。

即使需要说明来源，也不要把内部 Tool / Skill 调用流水当作最终答案主体。

如果某项内部能力不可访问，不得模拟其结果。应使用当前实际可用的证据继续，或明确指出尚未验证的事实。

---

## 12. Engineering Inference 必须与已确认事实区分

AI Agent 可以基于：

- Project Code；
- Golden Reference；
- PTC 官方资料；
- 一般软件工程原则；

提出合理的 Engineering Inference 或设计建议。

但必须区分：

```text
PTC Product Fact
Golden-derived Pattern
Project-specific Fact
Engineering Inference
```

不得把：

```text
“这个设计看起来合理”
```

改写成：

```text
“Windchill 官方就是这样工作的”
```

也不得因为某个推断最终碰巧正确，就倒推原始证据链合法。

跨 Framework、跨 Validation Phase、跨 Windchill Version 或跨 API 的等价关系尤其需要独立证据。