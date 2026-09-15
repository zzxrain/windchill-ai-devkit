# Windchill Project Context

> 本文件用于描述当前 Windchill 项目的项目级事实、技术基线、架构约束和已批准例外。
>
> 企业通用开发规范由 `windchill-ai-devkit` 提供，本文件不重复企业级 Rules。
>
> AI Agent 在开始 Windchill 二次开发任务前，应优先读取本文件。
>
> 标记为 `<REQUIRED>` 的内容应在项目启用 AI Coding 前填写。
> 未提供的信息视为未知，不得由 AI Agent 自行猜测。

---

## 1. Project Information

- Project Name: `<REQUIRED>`
- Customer / Organization: `<OPTIONAL>`
- Project Type: `<Implementation | Upgrade | Maintenance | Enhancement | Other>`
- Repository: `<OPTIONAL>`
- Main Branch: `<OPTIONAL>`
- Technical Owner: `<OPTIONAL>`

### Project Scope

当前项目主要涉及：

- `<PDMLink>`
- `<MPMLink>`
- `<ProjectLink>`
- `<Workflow>`
- `<Custom UI>`
- `<WRS / OData>`
- `<External Integration>`
- `<Data Migration>`
- `<Other>`

删除不适用项。

---

## 2. Windchill Platform Baseline

- Windchill Version: `<REQUIRED，例如 13.0.2.0>`
- Java Version: `<REQUIRED，例如 17>`
- Database: `<Oracle | PostgreSQL | SQL Server | Other>`
- Operating System: `<OPTIONAL>`
- Deployment Mode: `<Single Node | Cluster | Unknown>`
- Search / Solr Version: `<OPTIONAL>`

### Installed Windchill Modules

- `<例如 PDMLink>`
- `<例如 MPMLink>`
- `<例如 ProjectLink>`
- `<例如 Supplier Management>`

没有特殊模块时填写：

`None`

### Version Rule

AI Agent 必须以本节声明的 Windchill Version 作为当前项目目标版本。

不得因为：

- 其他项目使用不同版本
- QMind 中存在其他版本资料
- Golden Reference 来自其他版本
- 模型熟悉其他版本

而自动改变当前项目目标版本。

如果 DEV、UAT、PROD 的 Windchill 版本不一致，应在本文件中明确说明。

---

## 3. XWorks

- Enabled: `<REQUIRED: true | false>`
- XWorks Version: `<Enabled=true 时填写，例如 13.0.2；否则填写 N/A>`

### XWorks Rule

如果：

`Enabled: false`

AI Agent 不得：

- import `com.ptc.xworks.*`
- 生成 XWorks Java 代码
- 使用 XWorks Listener Framework
- 使用 XWorks Workflow Framework
- 使用 XmlObject / XmlObjectStoreManager
- 使用 XWorks WQL
- 创建 XWorks 配置
- 增加 XWorks JAR 或部署依赖

如果：

`Enabled: true`

AI Agent 应：

- 遵循项目现有 XWorks 架构
- 应用 `85-xworks-framework.md`
- 优先复用已有 XWorks Framework 能力
- 不自行修改 XWorks Framework Core
- 根据项目实际 XWorks 版本验证 API

如果本项目尚未决定是否采用 XWorks，不得填写 `true`。

---

## 4. Customization Structure

### Custom Package Root

`<REQUIRED，例如 com.company.customer>`

### Main Source Locations

```text
<例如：
src/
codebase/
wtCustom/
>