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

必须区分：

```text
Implementation Pattern Evidence
Product / Framework Evidence
API Metadata Verification
Compile Verification
Runtime Verification
```

对应关系：

```text
Golden Reference
→ Implementation Pattern

PTC Guide / QMind
→ Product / Framework Behavior

Target-version Javadoc / API Lookup
→ Exact API Metadata

Target Classpath Build
→ Compile Verification

Actual Windchill Environment
→ Runtime Verification
```

不得把前一层证据描述成后一层验证已经完成。

---

## 9. 不得用猜测掩盖 Windchill 产品事实的不确定性

遇到 Windchill 专有技术事实不确定时，不得先猜一个实现再在结尾补一句：

> 建议再验证。

应根据事实类型主动取得对应证据。

如果仍无法确认，应明确区分：

- 已确认事实
- Golden-derived Pattern
- Engineering Inference
- 尚未确认的假设
- `UNVERIFIED PTC API`

不得为了完成代码而虚构：

- PTC API
- Method Signature
- Constant
- Extension Point
- Framework Behavior
- Versioning Capability
- Event Semantics
- Configuration Item

---

## 10. 回答前必须建立 Internal Evidence Plan

任何 Windchill-specific 技术任务，在形成最终答案前都必须在内部判断：

```text
当前结论需要哪些 Evidence Types？
```

至少检查：

```text
A. Project Context
B. Implementation Pattern
C. Product / Framework Behavior
D. Exact API / Type Metadata
E. Compile Evidence
F. Runtime Evidence
```

这个 Evidence Plan 属于内部过程，不向用户输出。

### A. Project Context

需要回答：

```text
当前项目是什么？
```

证据：

```text
AGENTS.md
Project Code
ADR
Project Configuration
User-provided Context
```

### B. Implementation Pattern

以下任务默认需要检查 Implementation Pattern：

```text
怎么实现
怎么设计
给代码
修改 Windchill-specific 代码
Code Review
Windchill-specific Debug
```

如果 Golden Reference Skill 可用：

```text
必须先执行 CATALOG Preflight
```

Catalog 中没有强匹配：

```text
可以停止 Golden 检索
```

Catalog 中存在直接匹配：

```text
读取最小充分 Reference
```

不得因为已经查到 QMind / PTC Guide 就跳过 Golden Preflight。

### C. Product / Framework Behavior

当结论涉及：

```text
Lifecycle
Event semantics
Validation phase
Wizard behavior
DataUtility lifecycle
Queue behavior
Workflow behavior
Transaction behavior
Configuration mechanism
Official extension semantics
```

需要：

```text
Target-version official documentation
/
QMind
```

不得从 Java Signature、Golden 代码形态或名称自行推断。

### D. Exact API / Type Metadata

当最终答案包含具体：

```text
PTC Class
Method
Constructor
Signature
Return Type
Throws
Constant
Supported
Extendable
Deprecated
Class hierarchy
Implemented interface
Versioned / Iterated / Workable 等类型能力
```

则这些属于 Exact API / Type Metadata。

如果目标版本 Javadoc / API Lookup 已可用：

```text
必须实际执行验证
```

不得只在最终答案中告诉用户：

> 建议再查 Javadoc。

例如：

```text
WTChangeOrder2 是不是 Versioned / Iterated
```

属于目标版本 Type Metadata，不能根据：

```text
number 唯一
业务对象类型
历史代码写法
模型记忆
```

推断。

### E. Compile

只有任务实际执行了 Target Build 才能声明：

```text
Compile Verified
```

### F. Runtime

只有实际部署 / 执行 Windchill Runtime 场景才能声明：

```text
Runtime Verified
```

---

## 11. Required Evidence Set 必须补齐后再回答

识别 Evidence Plan 后，Agent 必须检查：

```text
Required Evidence Set
        ↓
哪些已满足？
        ↓
哪些仍缺失？
        ↓
补齐必要证据
        ↓
Evidence Sufficient?
        ↓
Final Answer
```

不得使用：

```text
找到一个可信来源
        ↓
立即开始回答
```

替代 Evidence Sufficiency Check。

一个证据源只能证明其实际覆盖的事实。

例如：

```text
Golden Reference
```

不能自动证明：

```text
Exact API Metadata
```

而：

```text
Javadoc
```

不能自动证明：

```text
复杂 Framework Behavior
```

同样：

```text
PTC Guide
```

中的代码示例不能自动证明目标版本 API 的所有 Supported / Deprecated / Signature Metadata。

---

## 12. 使用最小充分证据，不机械调用全部能力

Evidence Set Complete 不等于调用所有工具。

错误：

```text
所有 Windchill 请求
→ QMind
→ Golden
→ API Lookup
→ 全部 Rules
```

正确：

```text
根据任务需要选择最小充分集合
```

例如：

```text
普通 Java rename
→ Project Context only
```

```text
DataUtility 性能设计
→ UI Rule
→ Golden Preflight
→ 需要生命周期事实时 QMind
```

```text
生成新的具体 PTC API 调用代码
→ Golden / Product Evidence as needed
→ Exact API Lookup
```

```text
解释 Event veto semantics
→ Event Rule
→ Product / Framework Evidence
→ 精确 Event/API Metadata only when required
```

不得为了展示 DevKit 能力进行无意义重复检索。

---

## 13. 默认静默执行所有内部编排

Rules、Golden、QMind、API Lookup 和 Evidence Plan 都属于内部能力。

### 强制输出规则

在调用 Skill / QMind / Golden / API Lookup：

```text
之前
之间
之后但最终答案尚未形成时
```

不得发送用户可见的进度播报。

禁止：

```text
我先调用企业知识路由技能
我先读取知识库注册表
我先查看 Golden
我找到 GR-XXX，接下来读取
我再查一下 Javadoc
我先确认一下
```

Agent 应直接执行内部调用。

正常情况下：

```text
第一个用户可见文本
=
对用户实际问题的实质回答
```

例外仅包括：

- 必须向用户澄清关键缺失信息；
- 外部 Skill / Tool 需要用户授权；
- 工具执行失败且失败本身影响答案；
- 用户明确要求查看检索过程；
- 用户正在调试 DevKit 本身。

最终答案可以在确有必要时简洁说明：

```text
依据：PTC Windchill 13.1.2.0 Customization Guide
```

或：

```text
该 API Metadata 已按 13.1.2.0 Javadoc 验证
```

但不得输出内部路由流水。

---

## 14. Engineering Inference 必须与已确认事实区分

AI Agent 可以基于：

- Project Code；
- Golden Reference；
- PTC 官方资料；
- 一般软件工程原则；

提出 Engineering Inference。

但必须区分：

```text
PTC Product Fact
API / Type Metadata
Golden-derived Pattern
Project-specific Fact
Engineering Inference
```

不得把：

```text
这个设计通常合理
```

改写成：

```text
Windchill 产品必然这样工作
```

也不得因为某个结论最终碰巧正确，就倒推原始证据链合法。

尤其不得自行推导：

```text
PRE_*   => 一定 vetoable
POST_*  => 一定 non-vetoable

number 唯一
=> 对象一定不是 Versioned

setModelData
=> 整个 Table 永远一次调用

batch load
=> 必须单次 IN query

Framework A 的 warning
=> Framework B 一定存在等价 Status / Hook
```

这些结论都必须使用与其事实类型匹配的独立证据。