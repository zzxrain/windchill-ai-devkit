---
trigger: always_on
---

# Windchill AI 辅助开发基础规则

## 目的

本规则主要用于约束 AI Agent 在 Windchill 二次开发过程中的技术分析、方案选择、代码生成、代码修改和代码评审行为，同时作为开发工程师的基础开发参考。

适用于：

- 技术方案设计
- 代码生成
- 代码修改
- 重构
- 缺陷修复
- 调试
- 代码评审
- Windchill 技术分析

Java、Windchill API、安全、配置、日志、集成以及数据迁移工具开发等具体要求，由对应专项 Rule 进一步定义。

---

## 1. 开发规范的权威顺序

当判断“代码应该如何实现”时，按照以下优先级执行：

1. 企业强制性的安全、合规、架构和开发要求
2. 当前项目已经批准的例外情况（项目系统架构顾问或客户要求）
3. 企业 Windchill 开发规则
4. 企业审核通过的 Golden Reference (windchill-customization-reference仓库)
5. 当前项目已有实现
6. 模型自身知识和经验

项目规则可以对企业规则进行补充、细化或加强。

不建议项目规则削弱企业强制规则，如果某个项目确实需要违反企业基线规则，需要记录原因、影响和适用范围。

**现有项目代码属于兼容性证据，不属于开发规范本身。**

不得仅因为某种实现已经存在于当前项目中，就自动继续复制该实现。

如果现有代码与更高优先级规则冲突，应优先遵守更高优先级规则；如果为了兼容历史实现必须继续沿用，应明确指出这是项目例外或技术债。

---

## 2. Windchill 产品事实与开发规范必须区分

“应该怎么开发”和“Windchill 实际支持什么”属于两个不同的判断维度。

当判断以下 Windchill 产品事实时：

- 某个 PTC Java 类是否存在
- 某个方法签名是否正确
- 某个 API 是否属于 Supported API
- 某个类是否允许继承
- 某个属性或配置项是否存在
- 某个 WRS/OData Entity、Function 或 Action 是否存在
- 某个扩展点是否受到官方支持
- 某种行为是否适用于当前 Windchill 版本

按照以下证据优先级判断：

1. 与目标 Windchill 版本匹配的 PTC 官方文档和 Javadoc
2. 基于 PTC 官方资料建立并审核的企业知识库
3. 与目标版本匹配且经过验证的 Golden Reference (windchill-customization-reference仓库)
4. 已经在目标 Windchill 环境成功编译、部署或运行验证的代码
5. 当前项目已有代码
6. 模型自身知识和记忆

不得把历史项目代码或模型记忆作为 PTC API 正确性的最终依据。

---

## 3. 优先使用 Windchill OOTB 与配置能力

在引入新的自定义代码之前，应依次判断需求是否可以通过以下方式满足：

1. Windchill 现有 OOTB 能力
2. Windchill 支持的配置能力
3. Windchill 支持的定制扩展机制
4. 自定义代码开发

支持的配置能力包括但不限于：

- Property
- Preference
- Soft Type
- Attribute
- Object Initialization Rule
- Lifecycle
- Workflow
- Access Control
- Template
- Business Rule
- 其他 Windchill 管理配置能力

在能够满足业务需求的情况下，应优先选择侵入性最小、升级影响最小的方案。

不得为了使用代码而重复实现 Windchill 已经能够通过 OOTB 或配置机制完成的功能（除非基于一个足够合理的理由）。

对于数据模型扩展，如果 Soft Type 和属性能够满足需求，应优先评估 Soft Type，而不是直接创建新的 modeled business object。

---

## 4. 优先使用 Windchill Supported API

Windchill 定制开发必须优先使用 PTC 定义的 Supported API 和官方支持的扩展机制。

使用 PTC Java API 时必须考虑：

- Class 是否为 `Supported: true`
- Method 是否为 `Supported: true`
- 如果需要继承 Class，该 Class 是否为 `Extendable: true`
- API 是否适用于目标 Windchill 版本
- API 是否已经被标记为 Deprecated

类存在于 Windchill classpath 中，并不代表该类属于 Supported API。

某个类属于 Supported API，也不代表该类中的所有方法都属于 Supported API。

只有在 Javadoc 或对应 PTC Customization 文档明确允许时，才应继承或扩展 PTC 类。

强烈注意：Supported/Extendable的值，不作为强制考虑，因为实际开发过程中，经常使用标记为false的API/Class，但可以提醒使用者此风险。


不得凭空生成或猜测：

- PTC Java 类
- 方法名
- 方法签名
- 常量
- Property 名称
- Service 注册项
- Extension Point
- WRS/OData Entity
- WRS/OData Function
- WRS/OData Action

遇到无法确认的 Windchill 专有技术事实，应首先使用公司批准的企业知识检索机制进行验证。

如果经过可用知识源检索后仍然无法确认，应明确标记：

`UNVERIFIED PTC API`

并说明需要进一步验证，不得将推测内容描述为已经确认的 PTC API。

---

## 5. 保护 PTC 提供的标准实现

正常情况下，不应直接修改或替换 PTC 提供的 Java 类、运行时实现或标准文件作为定制方案。

应优先选择：

- 支持的配置方式
- Custom Class
- Delegate
- Service
- Listener
- Builder
- DataUtility
- Validator
- FormProcessor
- Extension Point
- XCONF
- Custom Resource
- 其他 PTC 官方支持的定制方式

如果 PTC 官方定制机制明确要求修改 PTC 提供的文件，应：

- 保留 PTC 原始版本
- 使用 Windchill 官方提供的 customization maintenance 机制管理修改
- 保证 Site Modification 可以被识别和追踪
- 考虑 Maintenance Update 和 Upgrade 对修改文件的覆盖风险

不得仅因为某个文件可以被修改，并且修改后系统能够运行，就认为直接修改该文件属于推荐的 Windchill 定制方式。

---

## 6. Windchill 版本属于技术上下文的一部分

Windchill API、扩展机制和产品行为可能随版本发生变化。

当方案涉及版本敏感能力时，应首先确定目标 Windchill 版本。

版本信息应优先从以下来源获取：

1. 当前项目 `AGENTS.md`
2. 项目文档
3. Build 或 Dependency 信息
4. 环境配置
5. 用户明确提供的信息

以下内容尤其需要考虑 Windchill 版本：

- PTC Java API
- JCA
- MVC
- WRS/OData
- Workflow API
- 配置项和 Property
- Java/JDK 版本
- 数据库支持
- Solr/Search
- 部署方式
- Upgrade
- Maintenance Update
- PTC 定制机制

如果版本未知，并且版本差异可能实质影响解决方案，应明确指出版本不确定性。

不得在没有依据的情况下默认使用某个 Windchill 版本的 API 或行为。

---

## 7. 最小化定制范围

优先采用能够正确满足需求的最小修改方案。

除非需求明确要求，否则不要顺带引入与当前任务无关的：

- 大范围重构
- 新框架
- 新基础设施
- 新抽象层
- 新依赖
- Package 大规模调整
- 配置结构调整
- 公共 API 变更

修改现有 Windchill 项目时，应尽可能保持：

- 现有业务行为
- 已发布接口
- 数据模型兼容性
- 外部系统接口兼容性
- 升级兼容性

不要为没有实际需求的未来场景提前设计复杂扩展。

Windchill 定制应持续优化以下目标：

- 可维护性
- 可支持性
- 可升级性
- 可诊断性
- 与 Windchill 内部实现的低耦合
- 变更影响面的可控性

---

### 7.1 第三方依赖与类库引入约束

Windchill Runtime 自身包含大量 PTC 组件及第三方类库。新增第三方 JAR、Framework 或运行时依赖可能导致：

- Classpath 或 ClassLoader 冲突
- 同一类库不同版本之间的兼容性问题
- Windchill Maintenance Update 或 Upgrade 后产生冲突
- PTC 已包含类库被重复打包或覆盖
- Transitive Dependency 引入不可控依赖
- 安全漏洞和后续补丁维护风险
- 开源许可证与商业使用合规风险
- 增加部署、运维和故障诊断复杂度

因此，不得仅因为某个第三方类库能够方便实现功能，就直接将其引入 Windchill 项目。

在新增第三方依赖之前，应按照以下顺序进行评估：

1. 判断 JDK 标准类库是否已经能够满足需求
2. 判断 PTC Windchill API 或官方扩展机制是否已经提供对应能力
3. 判断当前项目已经批准并使用的公共组件是否能够满足需求
4. 检查目标 Windchill Runtime / SDK 是否已经包含能够满足需求的相关能力或类库
5. 只有以上方式均不能合理满足需求时，才评估新增第三方依赖

优先复用 Windchill 或项目已有能力，但不得仅因为某个第三方类存在于 Windchill Classpath 中，就默认认为该类适合被 Customization 代码直接依赖。

使用 Windchill Runtime 已包含的第三方类库时，应根据实际情况确认：

- 当前目标 Windchill 版本是否包含该类库
- 实际使用的类库版本
- PTC 是否将其作为可供定制代码使用的能力，或项目是否已有经过验证的使用方式
- Maintenance Update 或 Upgrade 时该依赖发生变化的风险

不得在没有充分理由的情况下，将 Windchill 已经包含的第三方类库以另一个版本再次打包或部署到 Windchill Runtime。

如果确实需要新增第三方依赖，应至少确认：

- 引入该依赖的明确业务或技术必要性
- JDK、Windchill API 和现有项目依赖无法合理替代
- 使用的具体版本及其与目标 JDK、Windchill 版本的兼容性
- 是否与 Windchill 已包含的 JAR 或 Transitive Dependency 存在冲突
- 运行时 Classpath / ClassLoader 影响
- 部署和升级影响
- 安全漏洞风险
- License 和商业使用合规性
- 后续维护责任

AI Agent 不得自行决定新增第三方运行时依赖。

当实现方案需要新增第三方 JAR、Framework 或其他外部运行时依赖时，应首先向开发人员说明：

1. 为什么现有能力不能满足需求
2. 建议引入的组件和版本
3. 可选的替代方案
4. 对 Windchill Runtime、部署和升级可能产生的影响
5. 已识别的主要风险

如果项目设置了专职 SA（系统架构顾问 / System Architect），新增第三方运行时依赖原则上必须由 SA 确认或批准后再实施。

如果项目没有专职 SA，则应由项目技术负责人或承担架构职责的人员进行确认。

未经确认，不应直接修改项目依赖配置、下载第三方 JAR 或将新的第三方运行时依赖加入 Windchill 部署包。

## 8. 保持 Windchill 平台语义

不得为了让代码“能够运行”而绕过 Windchill 平台本身的重要业务语义。

修改 Windchill 对象或业务行为前，应根据场景考虑：

- Access Control
- 当前 Principal
- Session Context
- Container Context
- Version
- Iteration
- Checkout / Checkin
- Lifecycle
- Workflow
- Persistence
- Transaction
- Event / Listener
- Queue
- Cluster
- Background Processing

不得使用直接 SQL 更新 Windchill 管理的业务数据来替代正常 Windchill API，除非 PTC 官方文档针对特定维护或升级场景明确要求这样操作。

不得为了规避权限问题，将：

- 关闭 Access Control
- 切换 Administrator
- 提升 Principal 权限

作为通用解决方案。

如果 PTC 官方支持的定制模式明确要求临时提升权限或临时关闭 Access Control，则必须：

1. 明确为什么需要这样做
2. 将影响范围限制到最小
3. 使用可靠的恢复机制
4. 在异常情况下也必须恢复原始安全上下文

---

## 9. 正确管理 Windchill 配置

如果 Windchill 提供标准配置管理机制，应使用该机制维护配置。

不得把生成后的运行时配置文件作为定制配置的唯一源文件。

例如，对于应由 XCONF 管理的 Property，应优先通过：

- Site XCONF
- Custom XCONF
- `xconfmanager`
- 对应 PTC 官方配置机制

进行维护和传播。

不应直接修改 `wt.properties` 等最终生成配置文件作为标准开发方案。

以下环境相关内容原则上应配置化，而不是硬编码在业务代码中：

- Hostname
- URL
- Port
- 文件路径
- Timeout
- 用户名
- Password
- Token
- Secret
- 外部服务地址
- 环境差异参数

凭证、密码和 Secret 必须使用适合的安全机制管理。

---

## 10. 修改代码前必须理解上下文

在修改已有 Windchill 代码之前，应先理解与当前变更相关的上下文。

根据任务范围，应检查：

- 当前类的职责
- 调用方
- 被调用方
- 相关接口
- 相关 Service 或 Helper
- 对象类型
- Windchill 扩展点
- Persistence 行为
- Transaction 边界
- Version / Iteration 语义
- Access Control
- 项目已有 ADR
- 项目 Rules
- 项目特殊兼容要求

不要仅根据单个源文件中的局部代码直接进行修改。

如果现有项目实现明显违反企业规范，应区分：

- 当前任务必须修复的问题
- 与当前任务无关的历史技术债

不要在没有需求依据的情况下顺带重构所有历史问题。

---

## 11. 验证与完成状态

开发任务完成时，应执行当前开发环境能够实际完成的验证。

在 IDE / Repository 环境中，根据条件执行：

- 语法和静态错误检查
- 可执行的本地编译
- 可执行的自动化测试
- 修改范围检查
- Git Diff Review
- 企业 Rules Compliance Review
- 项目 Rules Compliance Review

不得声称执行了实际未执行的验证。

对于必须依赖 Windchill Build、部署或 Runtime 环境才能确认的行为，
如果当前 Agent 无法访问对应环境，应明确标记为：

`待 Windchill 环境验证`

并指出需要验证的关键事项。

“代码已实现”不等同于“Windchill 运行验证通过”。

---

## 12. 明确处理不确定性

Windchill 开发中，不得使用“看起来合理”的代码掩盖信息不足。

遇到不确定问题时，应依次：

1. 检查当前项目代码和项目上下文
2. 检查适用的企业 Rules 和 ADR
3. 检索批准的企业 Windchill 知识源
4. 必要时确认目标 Windchill 版本
5. 检查可用的 PTC Javadoc 或官方资料
6. 仅在缺失信息实质阻止正确决策时向用户提出问题

输出中必须区分：

- 已确认事实
- 有依据的推断
- 尚未确认的假设

宁可明确说明某个 Windchill 技术点尚未确认，也不要生成虚假的 PTC API 或伪造产品行为。