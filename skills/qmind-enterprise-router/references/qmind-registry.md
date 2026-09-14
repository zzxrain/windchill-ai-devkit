# QMind Enterprise Knowledge Registry

> 本文件是 `qmind-enterprise-router` 的知识库注册表。
>
> **扩展原则：新增知识库时复制一个 Entry 区块即可。**
> Router 应优先使用 `id` 作为精确定位依据，`name` 用于可读性和校验。
> 不允许根据名称自行猜测 ID。

---

## Registry Schema

每个知识库使用以下基础格式。`versions`、`authority`、`status`、`owner`、`last_verified`
是 v1.1 引入的**可选治理字段**；旧 Entry 可以暂不补齐，缺失时按“未知”处理，不得自行推断。

```yaml
- name: <QMind 后台精确名称>
  id: <QMind Notebook UUID>
  product: <产品，例如 ptc-windchill>
  category: <development | training | deployment | upgrade | migration | other>
  scope: <general | 专用模块/框架>
  priority: <数字，越大优先级越高>

  # Optional governance metadata
  versions:
    - <明确覆盖/验证过的版本，例如 13.0.2>
  authority: <ptc-official | enterprise-approved | mixed | unknown>
  status: <active | deprecated | experimental>
  owner: <维护团队，可选>
  last_verified: <YYYY-MM-DD，可选>

  strong_match:
    - <强触发关键词>
  match:
    - <普通匹配关键词>
  negative_match:
    - <明确不适用的关键词，可为空>
  combine_with:
    - <适合组合使用的知识库 name，可为空>
  fallback:
    - <主库不足时允许追加的知识库 name，可为空>
  description: >
    <知识库用途>
```

### 治理字段语义

- `versions`：仅填写已明确覆盖或验证的版本。缺失/空数组表示**版本未知或未治理**，不是“支持所有版本”。
- `authority`：描述知识内容的来源级别，不代表自动覆盖项目 Rules。
- `status`：`deprecated` 不作为默认主库；`experimental` 结果需要更谨慎验证。
- `owner`：知识库维护责任方。
- `last_verified`：最后一次人工确认元数据/内容适用性的日期，不等同于源文档发布日期。

建议从高价值知识库开始逐步补齐治理字段，不要求一次性清理全部现有 QMind。

### priority 建议

- `100`：强制/框架级专用知识，例如 XWorks
- `90`：专项工具/专项模块
- `80`：通用开发、部署、升级
- `70`：专项功能培训
- `60`：通用功能培训

### 路由约束

1. `strong_match` 只放真正具有区分度的关键词，避免普通词造成误路由。
2. `negative_match` 应用于排除明显错误领域。
3. `combine_with` 表示可组合，不表示每次都必须组合。
4. `fallback` 只在主库检索不足后使用。
5. 名称变更时同步更新 `name`；只要 QMind ID 未变，仍以 `id` 为首要定位依据。
6. 不要为了“看起来完整”猜测 `versions`、`authority` 或 `last_verified`。

---

# Registered QMind Notebooks

## 1. XWorks Windchill Development

```yaml
- name: ptc-winidchill-dev-xworks
  id: 01a07fe9-6b35-7b6a-92b2-cb391cf922c9
  product: ptc-windchill
  category: development
  scope: xworks
  priority: 100
  strong_match:
    - xworks
    - XWorks
    - x-works
    - 基于xworks
    - 基于 XWorks
  match:
    - Windchill开发框架
    - Windchill二次开发框架
    - 客制化框架
    - 开发框架
  negative_match: []
  combine_with:
    - ptc-windchill-dev-general
  fallback:
    - ptc-windchill-dev-general
  description: >
    基于 XWorks 开发框架的 PTC Windchill PLM 开发说明。
    只要任务明确提到 XWorks，应优先检索此知识库。
```

> 注意：`ptc-winidchill-dev-xworks` 中的 `winidchill` 拼写按当前 QMind 后台实际名称保留；
> 如果后台未来改名，请同步修改本注册表的 `name`，ID 不变时仍以 ID 为准。

---

## 2. Windchill General Development

```yaml
- name: ptc-windchill-dev-general
  id: 01a07fe9-9132-71b5-8eb6-258b8e2bbe6a
  product: ptc-windchill
  category: development
  scope: general
  priority: 80
  strong_match:
    - Windchill二次开发
    - Windchill客制化
    - Windchill customization
    - Java customization
    - JCA
    - QuerySpec
    - PersistenceHelper
    - DataUtility
    - FormProcessor
    - WRS
    - OData
  match:
    - WTPart
    - WTDocument
    - WTChange
    - WTPartUsageLink
    - BOM
    - Workflow
    - actionModels.xml
    - actions.xml
    - NmCommandBean
    - Validator
    - xconf
    - Windchill API
    - Java API
    - REST integration
    - integration
  negative_match: []
  combine_with:
    - ptc-winidchill-dev-xworks
    - ptc-windchill-training-mpmlink
    - ptc-windchill-training-project-management
    - ptc-windchill-deploy
  fallback: []
  description: >
    PTC Windchill PLM 通用开发知识库，包含官方客制化指南及常用客制化方法。
    对未明确指定 XWorks 的 Windchill Java/JCA/API/WRS 等二次开发问题，优先使用此库。
```

---

## 3. Windchill MPMLink Training

```yaml
- name: ptc-windchill-training-mpmlink
  id: 01a08003-824f-76f3-8d1a-d53c241ff0e8
  product: ptc-windchill
  category: training
  scope: mpmlink
  priority: 70
  strong_match:
    - MPMLink
    - MPM Link
    - 制造/工艺
    - 制造模块
    - 工艺模块
  match:
    - Process Plan
    - ProcessPlan
    - Operation
    - Manufacturing
    - Manufacturing BOM
    - MBOM
    - mBOM
    - BOP
    - 工艺路线
    - 工艺计划
    - 工序
    - 制造BOM
    - 工艺BOM
    - 工艺管理
  negative_match: []
  combine_with:
    - ptc-windchill-dev-general
    - ptc-winidchill-dev-xworks
  fallback:
    - ptc-windchill-training-general
  description: >
    PTC Windchill MPMLink 制造/工艺模块的功能应用培训说明。
    功能应用问题优先使用此库；涉及二次开发时应再组合开发知识库。
```

---

## 4. Windchill General Training

```yaml
- name: ptc-windchill-training-general
  id: 01a08001-2ea0-7280-9deb-9ed971b6b27a
  product: ptc-windchill
  category: training
  scope: general
  priority: 60
  strong_match:
    - Windchill功能
    - Windchill培训
    - Windchill怎么用
    - Windchill使用
  match:
    - WTPart功能
    - WTDocument功能
    - 变更管理
    - 生命周期
    - 版本管理
    - 文档管理
    - BOM管理
    - 产品结构
    - UI操作
    - 用户操作
    - 功能应用
  negative_match:
    - Java开发
    - 二次开发
    - 客制化开发
  combine_with:
    - ptc-windchill-dev-general
  fallback: []
  description: >
    PTC Windchill PLM 常规/通用功能应用培训说明。
    用于业务功能、用户操作、标准功能解释；纯开发问题不应优先使用此库。
```

---

## 5. Windchill ProjectLink Training

```yaml
- name: ptc-windchill-training-project-management
  id: 01a08000-657b-7cca-a8e0-cf6ae0cdb25a
  product: ptc-windchill
  category: training
  scope: projectlink
  priority: 70
  strong_match:
    - ProjectLink
    - Project Link
    - Windchill项目管理
    - 项目管理模块
  match:
    - Project
    - Plan
    - Activity
    - Milestone
    - Deliverable
    - 项目计划
    - 项目活动
    - 里程碑
    - 交付物
    - 项目模板
    - 项目协同
  negative_match: []
  combine_with:
    - ptc-windchill-dev-general
    - ptc-winidchill-dev-xworks
  fallback:
    - ptc-windchill-training-general
  description: >
    PTC Windchill ProjectLink 项目管理模块功能应用培训说明。
    ProjectLink 功能问题优先使用；涉及定制开发时组合开发知识库。
```

---

## 6. Windchill Deployment

```yaml
- name: ptc-windchill-deploy
  id: 01a07fe9-b662-7e5a-a836-e1a0eb963a21
  product: ptc-windchill
  category: deployment
  scope: general
  priority: 80
  strong_match:
    - Windchill安装
    - Windchill部署
    - Windchill installation
    - Windchill deployment
  match:
    - Apache
    - HTTPServer
    - MethodServer
    - Tomcat
    - Solr
    - LDAP
    - Directory Server
    - HTTPS
    - SSL
    - cluster
    - 集群
    - 负载均衡
    - reverse proxy
    - 反向代理
    - xconf
    - 配置
    - 安装
    - 部署
    - 拓扑
  negative_match:
    - 升级
    - upgrade
  combine_with:
    - ptc-windchill-dev-general
  fallback: []
  description: >
    PTC Windchill 常规安装、配置、部署官方文档内容。
    用于环境安装、基础设施、HTTPS、服务配置、拓扑和部署问题。
```

---

## 7. Windchill Upgrade

```yaml
- name: ptc-windchill-upgrade
  id: 01a07fea-0839-74a6-bcc5-0126c47d6d57
  product: ptc-windchill
  category: upgrade
  scope: general
  priority: 90
  strong_match:
    - Windchill升级
    - Windchill upgrade
    - upgrade
    - 升级指南
  match:
    - source version
    - target version
    - Upgrade Manager
    - CPS
    - Critical Patch Set
    - schema upgrade
    - 数据库升级
    - 升级路径
    - 升级前检查
    - 升级后检查
    - customizations upgrade
    - 客制化升级
  negative_match: []
  combine_with:
    - ptc-windchill-deploy
    - ptc-windchill-dev-general
  fallback: []
  description: >
    PTC Windchill 官方升级指南。
    涉及版本升级、升级路径、Upgrade Manager、升级前后检查、客制化兼容等问题时优先使用。
```

---

## 8. Windchill Bulk Migrator

```yaml
- name: ptc-windchill-bulk-migrator
  id: 01a07fec-f707-741b-856d-5e1f8cd56324
  product: ptc-windchill
  category: migration
  scope: bulk-migrator
  priority: 90
  strong_match:
    - Bulk Migrator
    - Windchill Bulk Migrator
    - WCBulkMigrator
    - bulk migration
  match:
    - 数据迁移工具
    - 批量迁移
    - bulk load
    - migration
    - migrator
    - extraction
    - transformation
    - loading
  negative_match: []
  combine_with:
    - ptc-windchill-deploy
    - ptc-windchill-dev-general
  fallback: []
  description: >
    PTC Windchill Bulk Migrator 官方使用说明。
    明确涉及 Bulk Migrator/WCBulkMigrator 时必须优先使用。
    对一般“历史数据迁移方案”但未明确使用 Bulk Migrator 的问题，不应仅凭 migration 一词强制选择此库。
```

---

# Cross-Knowledge Routing Examples

## Example 1 — XWorks

用户：

> 基于 XWorks 给 WTPart 增加一个自定义 Action。

路由：

1. `ptc-winidchill-dev-xworks`
2. 若 XWorks 库缺少 PTC JCA 底层 API，再查 `ptc-windchill-dev-general`

---

## Example 2 — 普通 Windchill Java 开发

用户：

> QuerySpec 如何查询 WTPart 的最新迭代？

路由：

1. `ptc-windchill-dev-general`

不要查询培训、部署、升级库。

---

## Example 3 — MPMLink 功能

用户：

> MPMLink 中 Process Plan、Operation 和 MBOM 是什么关系？

路由：

1. `ptc-windchill-training-mpmlink`

---

## Example 4 — MPMLink 二次开发

用户：

> 如何通过 Java 获取 MPMLink Process Plan 的 Operations？

路由：

1. `ptc-windchill-training-mpmlink`（确认模块业务对象和功能语义）
2. `ptc-windchill-dev-general`（确认客制化/API 模式）

如果用户明确使用 XWorks：

1. `ptc-windchill-training-mpmlink`
2. `ptc-winidchill-dev-xworks`
3. 必要时才追加 `ptc-windchill-dev-general`

---

## Example 5 — ProjectLink

用户：

> ProjectLink 的项目计划、Activity、Deliverable 怎么使用？

路由：

1. `ptc-windchill-training-project-management`

---

## Example 6 — 部署

用户：

> Windchill Apache HTTPS 配置怎么做？

路由：

1. `ptc-windchill-deploy`

---

## Example 7 — 升级

用户：

> Windchill 12.1 升级到 13.x 时客制化需要关注什么？

路由：

1. `ptc-windchill-upgrade`
2. `ptc-windchill-dev-general`

---

## Example 8 — Bulk Migrator

用户：

> WCBulkMigratorUtil 怎么安装和使用？

路由：

1. `ptc-windchill-bulk-migrator`

---

# How to Add a New QMind Notebook

新增知识库时：

1. 复制下面模板；
2. 填写后台精确 `name`；
3. 填写精确 UUID `id`；
4. 配置 `category` / `scope`；
5. 给真正具有强区分度的关键词放入 `strong_match`；
6. 普通相关词放入 `match`；
7. 如需与其他知识库组合，配置 `combine_with`；
8. 如主库不足时允许回退，配置 `fallback`。

模板：

```yaml
- name: replace-with-exact-qmind-name
  id: replace-with-exact-qmind-uuid
  product: ptc-windchill
  category: other
  scope: general
  priority: 70
  versions: []
  authority: unknown
  status: active
  owner: <optional-owner>
  last_verified: <optional-YYYY-MM-DD>
  strong_match:
    - unique-keyword-1
    - unique-keyword-2
  match:
    - related-keyword-1
    - related-keyword-2
  negative_match: []
  combine_with: []
  fallback: []
  description: >
    Describe exactly what this QMind notebook contains and when it should be used.
```

## 扩展示例：未来加入 Codebeamer

可继续沿用相同 Schema：

```yaml
- name: ptc-codebeamer-dev-general
  id: <future-qmind-id>
  product: ptc-codebeamer
  category: development
  scope: general
  priority: 80
  strong_match:
    - Codebeamer
    - cbQL
    - Tracker
  match:
    - Groovy
    - REST API
    - Workflow Action
  negative_match: []
  combine_with: []
  fallback: []
  description: >
    PTC Codebeamer 通用开发知识库。
```

无需修改 Router 的基本算法；只有当 Codebeamer 需要特殊优先级逻辑时，再更新 `SKILL.md`。
