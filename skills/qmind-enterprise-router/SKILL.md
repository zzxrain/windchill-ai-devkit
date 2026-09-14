---
name: qmind-enterprise-router
description: >
  企业 QMind 知识路由技能。处理 PTC Windchill、XWorks、MPMLink、ProjectLink、
  Windchill 安装部署、升级、Bulk Migrator、功能应用培训及二次开发问题时，
  根据企业维护的 QMind 注册表选择精确知识库，再调用已安装的官方 QMind Knowledge Base
  Skill 定向检索。用于避免依赖 QMind 自动发现知识库，并在 Coding、Code Review、Debug、
  设计与技术答疑前获取受控的企业/官方知识依据。适用于 Windchill Java 客制化、JCA、
  QuerySpec、WRS/OData、BOM、Workflow、系统配置、部署、升级、数据迁移及功能咨询。
version: 1.1.0
---

# QMind Enterprise Knowledge Router

## 1. 职责边界

本 Skill 是企业 QMind 的**知识路由层**，职责只有三件事：

1. 判断当前任务是否需要企业 QMind 知识；
2. 从 `references/qmind-registry.md` 选择最匹配的知识库并构造检索 Query；
3. 调用官方 QMind Knowledge Base Skill，验证结果后再继续原任务。

本 Skill **不是** Windchill 开发规范本身，也不替代项目 Rules、`AGENTS.md`、ADR、
编译、测试或代码评审。

对于 Windchill 专有行为、PTC API、安装部署、升级、迁移、XWorks、MPMLink 等问题，
不要只依赖模型记忆；存在匹配企业知识库时应优先检索。

官方 QMind Skill Marketplace ID：

`official_vr9O4BTC`

Marketplace ID 仅用于识别目标官方 Skill。实际运行时应调用当前 Qoder 环境中已安装、
且功能描述为 QMind Knowledge Base / QMind 知识库检索的官方 Skill。

---

# 2. 知识权威与冲突处理

必须区分**规范性约束**与**产品事实**。

## 2.1 规范性约束：代码应该怎么写

默认优先级：

1. 当前项目已激活的企业/项目 Rules、`AGENTS.md`；
2. 已批准的项目 ADR / 明确例外；
3. 企业批准的 Golden Reference（如当前环境可访问）；
4. 当前项目既有实现；
5. 模型通用经验。

当前项目代码用于理解兼容约束、依赖、扩展点和既有结构，**不是天然的规范来源**。
如果当前实现与企业规则冲突，不得仅为了“保持现有风格”继续复制不规范实现。
如兼容性要求必须沿用旧模式，应明确指出这是兼容性选择或技术债。

## 2.2 产品事实：PTC 产品/API 实际如何工作

默认优先级：

1. 与目标版本匹配的 PTC 官方/企业审核 QMind 资料；
2. 企业批准且标注适用版本的 Golden Reference；
3. 当前项目中已编译/运行验证的实现；
4. 模型记忆与推断。

如果 Rules 与 PTC 官方产品事实表面冲突：

- Rules 决定团队允许采用的实现方式；
- 官方资料决定 PTC API、产品行为和版本事实；
- 不要自行把二者之一覆盖掉，应指出冲突并选择同时满足二者的方案；无法同时满足时说明原因。

---

# 3. 强制执行规则

## Rule 1 — Router 先选库，不让 QMind 自动发现

不要向官方 QMind Skill 发出：

- “搜索我所有的 QMind”
- “找一个适合的知识库”
- “自动选择知识库”

必须先读取 `references/qmind-registry.md`，由本 Router 选择目标知识库，再明确传递：

- `notebook_name`
- `notebook_id`
- `query`

如果 QMind Skill 不支持结构化参数，使用自然语言明确传递：

> 请仅检索 QMind 知识库 `<notebook_name>`，知识库 ID `<notebook_id>`，
> 检索问题为：`<query>`。

ID 是首要定位依据，名称用于可读性和二次校验。
不要猜测、拼接或生成不存在的知识库 ID。

## Rule 2 — 先路由，再检索，再执行

需要企业知识的任务遵循：

`用户任务 → 任务分类 → 选择 QMind → 构造 Query → QMind 检索 → 验证证据 → 执行原任务`

在必要的 QMind 检索完成前，不要直接生成大量依赖 Windchill 私有/专有 API 的代码或确定性结论。

## Rule 3 — 最小充分检索

默认：

- 选择 **1 个主知识库**；
- 同一知识库先进行 **1 次精确检索**；
- 结果不充分时，优先在同一知识库中**改写 Query 再检索 1 次**；
- 仍不足时才根据 `fallback` / `combine_with` 追加第二知识库；
- 默认最多 2 个知识库；明确跨域且有理由时最多 3 个。

不要因为第一次结果不理想就无差别搜索全部知识库。

## Rule 4 — XWorks 仅在明确命中时具有最高开发优先级

任务明确出现以下任一情况时：

- `xworks` / `XWorks` / `x-works`
- 基于 XWorks 的 Windchill 开发
- XWorks 框架、组件、API、页面、Service、配置或扩展方式

必须优先选择：

`ptc-winidchill-dev-xworks`

如还需要 Windchill 官方底层 API、JCA、QuerySpec、WRS 等，可追加：

`ptc-windchill-dev-general`

不要因为存在通用开发知识库而跳过 XWorks；也不要仅因普通 Windchill 开发就误选 XWorks。

## Rule 5 — 区分功能应用与二次开发

**功能/业务问题**优先路由到 `training-*`：

- 功能怎么使用
- UI 如何操作
- MPMLink/ProjectLink 的业务对象和流程语义

**开发/客制化问题**优先路由到 `dev-*`：

- Java API、JCA、QuerySpec、DataUtility、FormProcessor
- WRS/OData、Workflow customization
- XML/actionModel、xconf、定制页面、系统集成

**功能 + 开发混合问题**通常组合一个业务库和一个开发库，但只检索完成任务所需的最小集合。

## Rule 6 — 版本信息必须进入决策与 Query

如果用户、项目或上下文提供 Windchill 版本（例如 13.0.2、13.1）：

1. 将版本写入检索 Query；
2. 优先选择注册表中明确覆盖该版本的知识库；
3. 若注册表没有版本元数据，不得假设知识库一定适用于该版本；
4. QMind 结果若来自其他版本，应在使用前判断兼容性；
5. 涉及升级、废弃 API、安装部署、WRS/API 差异时，版本不确定会实质影响答案，应明确标注版本风险。

不要为了所有普通问题都追问版本；只有版本会改变实现或结论时才需要阻塞性确认。

## Rule 7 — 检索 Query 必须脱敏

构造 Query 时不要包含无必要的：

- 密码、Token、Cookie、私钥、许可证密钥；
- 完整连接串中的凭据；
- 客户个人信息；
- 与检索目标无关的大段客户专有源码或业务数据。

保留技术语义，移除敏感值。例如把真实 URL、用户名、Token 改成角色或占位符。

---

# 4. 路由算法

## Step 1 — 提取任务特征

提取：

- 产品：Windchill / MPMLink / ProjectLink / Bulk Migrator / XWorks
- 任务类型：开发 / 功能 / 部署 / 升级 / 数据迁移 / 培训 / Troubleshooting
- 技术关键词：Java、JCA、QuerySpec、WRS、OData、BOM、Workflow、xconf 等
- 模块关键词：MPMLink、Process Plan、Operation、ProjectLink 等
- 版本：例如 13.0.2、13.1
- 用户明确指定的知识库名称或 ID

用户明确指定已登记知识库时优先使用；用户给出未知名称/ID 时不要猜测映射。

## Step 2 — 读取注册表

读取：

`references/qmind-registry.md`

只允许从注册表选择已经登记的企业 QMind。

如 Entry 含以下可选治理字段，应参与判断：

- `versions`
- `authority`
- `status`
- `owner`
- `last_verified`

`status: deprecated` 的知识库不得作为默认主库，除非任务就是历史版本/历史行为或用户明确指定。

## Step 3 — 计算匹配优先级

按以下顺序：

1. 用户明确指定且已登记的知识库；
2. `strong_match` 命中；
3. 专用模块/框架知识库；
4. 任务类型匹配；
5. 版本匹配；
6. General/Fallback 知识库。

同等匹配时：

- 专用 > 通用
- 版本精确 > 版本未知
- XWorks 明确命中时 XWorks > Windchill 通用开发
- 官方/企业审核专项资料 > 泛化培训资料
- `active` > `deprecated`

`negative_match` 命中时应显著降权或排除。

## Step 4 — 构造检索 Query

不要简单把用户整句话原样提交给 QMind。

Query 应尽量包含：

- 产品/模块
- 对象
- 技术点
- 用户目标
- 关键英文术语
- Windchill 版本（已知时）
- 需要确认的事实类型：API、配置、行为、限制、示例等

优先查询“完成当前任务所缺失的事实”，而不是泛泛介绍主题。

示例：

用户：

> Windchill 13.0.2 里如何通过 QuerySpec 找到 WTPart 最新迭代？

检索 Query：

> PTC Windchill 13.0.2 WTPart QuerySpec latest version latest iteration Java customization; confirm supported API/classes and recommended query pattern, including VersionControl/Iteration semantics.

用户：

> 基于 XWorks 给 WTPart 页面增加自定义 Action

检索 Query：

> XWorks Windchill WTPart custom action JCA action actionModel FormProcessor NmCommandBean; confirm XWorks extension pattern and required PTC APIs/configuration.

## Step 5 — 调用官方 QMind Skill

每个选中的知识库分别调用一次 QMind Skill，传递：

```text
notebook_name: <注册表精确名称>
notebook_id: <注册表精确 UUID>
query: <生成的检索 Query>
```

如果当前环境可以直接调用官方 QMind Skill，直接调用。

如果无法通过名称定位：

1. 在可用 Skills 中寻找 QMind / QMind Knowledge Base；
2. Marketplace ID 为 `official_vr9O4BTC`；
3. 找到后调用；
4. 仍不可调用时，不得模拟检索结果。

## Step 6 — 验证检索结果

检查：

- 是否来自预期知识库；
- 是否直接回答当前事实缺口；
- 是否与目标版本/模块一致；
- 是否提供足够依据确认关键 PTC API / 配置 / 产品行为；
- 是否与 Rules、ADR、项目实际依赖或已验证实现冲突；
- 是否存在明显跨版本内容或过期资料。

内部按以下状态处理证据：

- `VERIFIED`：足够支撑当前结论；
- `PARTIAL`：可用于方向，但关键事实仍缺证据；
- `UNVERIFIED`：不足以支撑确定性实现。

不要求把这些标签机械输出给用户，但不能把 `PARTIAL/UNVERIFIED` 当成已确认事实。

主库不足时，先改写 Query 重试一次；再不足才追加 fallback/第二知识库。

---

# 5. Windchill Coding / Review 特殊规则

当任务涉及 Windchill 二次开发、代码评审或 Debug：

1. 用 QMind 确认 PTC 开发模式、产品行为和关键 API；
2. 检查当前项目代码以理解版本、依赖、已有扩展点和兼容约束；
3. 当前项目代码不得覆盖已激活的企业 Rules / `AGENTS.md`；
4. 不得仅凭类名规律编造 PTC 类、方法、常量、XML 配置项或参数；
5. 无法确认的重要 PTC API 应标记为 `UNVERIFIED PTC API`，或明确说明需要编译/官方资料验证；
6. 如果任务明确使用 XWorks，遵循 XWorks 框架约束；需要 PTC 底层事实时再用通用开发库补证；
7. 如果存在企业批准的 Golden Reference，可作为实现参考，但仍需确认适用版本；
8. 能执行编译/测试时，以编译、自动测试、受控验证结果进一步确认代码，而不是把 QMind 检索等同于代码已正确；
9. Code Review 时应区分：企业规范符合性、需求符合性、PTC/Windchill 技术正确性。

不要为了展示检索过程而输出冗长日志。用户未要求时，只需在结论中简要说明实际使用的知识库。

---

# 6. 用户可见行为

常规情况下自主路由，不先询问“应该查哪个知识库”。

仅在以下情况需要询问或明确风险：

- 候选库语义冲突且任务存在关键歧义；
- 用户要求的知识库未登记；
- QMind Skill 无法访问目标知识库；
- Windchill 版本会实质改变实现且无法从项目/上下文确定；
- 检索结果不足以验证关键 PTC API 或产品事实。

如实际完成了 QMind 检索，可在结果末尾简要说明：

`知识来源：ptc-xxx（QMind）`

不要输出 UUID，除非用户正在诊断路由问题。

如果未成功调用 QMind，不得声称“已参考企业 QMind”。

---

# 7. 失败与降级策略

## 找不到匹配知识库

- 不要随意选择一个库；
- 通用问题可基于项目上下文和模型能力继续；
- 涉及 Windchill 专有 API/行为时明确说明企业知识库未覆盖或未验证。

## 知识库无权限

- 说明目标知识库名称；
- 不自动换到无关知识库；
- 仅尝试注册表明确配置的 fallback。

## QMind Skill 不可用

- 不模拟 QMind 检索；
- 明确说明官方 QMind Knowledge Base Skill 当前不可用；
- 风险可控时可基于 Rules、当前代码和模型知识继续；
- 关键 PTC API/版本事实保持 `UNVERIFIED`，直到获得可验证依据。

## QMind 与当前项目实现冲突

先判断冲突属于：

- 团队规范冲突；
- Windchill 版本差异；
- XWorks/项目框架约束；
- 历史技术债；
- QMind 内容过时或适用范围不同。

不得默认复制当前代码，也不得默认认为 QMind 一定适用于当前版本。

---

# 8. 扩展原则

新增 QMind 时优先只修改：

`references/qmind-registry.md`

不要为了新增一个知识库修改 Router 算法。

知识库名称、ID、关键词、适用范围、版本、authority、status、fallback 等元数据全部维护在注册表中。

只有新增全局路由行为时才修改 `SKILL.md`，例如：

- 新产品 Codebeamer；
- 新的跨库组合策略；
- 新的权威级别；
- 新的安全/合规路由要求。
