# Windchill Project Context

> 本文件描述当前 Windchill 项目的项目级事实、技术基线、架构决策和已批准例外。
>
> 企业通用开发规范由 `windchill-ai-devkit` Rules 提供，本文件不重复企业级 Rules。
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

- `<PDMLink / MPMLink / ProjectLink / Workflow / Custom UI / WRS / Integration / Data Migration / Other>`

---

## 2. Windchill Platform Baseline

- Windchill Version: `<REQUIRED，例如 13.0.2.0、13.1.2.0、2027.0.0.0>`
- Java Version: `<REQUIRED，例如 17>`
- Database: `<Oracle | PostgreSQL | SQL Server | Other | Unknown>`
- Operating System: `<OPTIONAL>`
- Deployment Mode: `<Single Node | Cluster | Unknown>`

### Installed Windchill Modules

- `<例如 PDMLink>`
- `<例如 MPMLink>`
- `<例如 ProjectLink>`

没有特殊模块时填写：

`None`

### Version Rule

本节声明的 Windchill Version 是当前项目唯一目标版本。

版本应填写项目实际使用的完整 Release Identifier，例如：

```text
13.1.2.0
2027.0.0.0
```

Windchill Version 不得由 Javadoc ZIP 文件名推断。

其他项目代码、QMind、Golden Reference 或模型知识中出现的其他 Windchill 版本只能作为参考，不得自动替代当前项目版本。

如果 DEV、TEST、UAT、PROD 的 Windchill 版本存在差异，应在此明确说明：

`<None 或具体差异>`

### PTC Javadoc

- Javadoc ZIP: `<推荐填写项目相对路径；没有则填写 N/A>`

推荐：

```text
.windchill-ai/javadoc/WindchillJavadoc.zip
```

Javadoc ZIP：

- 仅用于当前项目目标 Windchill Version 的 API 验证；
- 一个项目通常只配置一个 Javadoc ZIP；
- 文件名不要求包含 Windchill Version；
- 不应提交到项目 Git Repository；
- 项目相对路径应由 AI Agent 根据项目根目录解析为绝对路径后再交给 API Lookup。

如果配置了 Javadoc ZIP，AI Agent 在需要精确 PTC API 事实时，应确保该 ZIP 已建立本地 API Index。

本地索引属于派生缓存，不进入项目 Repository。

---

## 3. XWorks

- Enabled: `<REQUIRED: true | false>`
- XWorks Version: `<Enabled=true 时填写，例如 13.0.2；否则填写 N/A>`

### Project Decision

如果：

`Enabled: false`

则当前项目未采用 XWorks，AI Agent 不得主动将 XWorks 引入项目。

如果：

`Enabled: true`

则当前项目采用 XWorks，AI Agent 应同时遵守：

`85-xworks-framework.md`

并以当前项目实际使用的 XWorks 版本、依赖和现有实现作为项目级上下文。

是否采用 XWorks 是项目架构决策，不得由 AI Agent 根据需求自行决定。

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
```

### Main Customization Areas

- `<例如 part>`
- `<例如 document>`
- `<例如 workflow>`
- `<例如 change>`
- `<例如 integration>`
- `<例如 jca>`
- `<例如 service>`

### Existing Frameworks / Shared Components

- `<没有则填写 None>`

### Important Existing Services / Extension Points

- `<没有则填写 None>`

只记录对当前项目架构有实质影响的内容。

---

## 5. Architecture Decisions

记录会实质影响 AI 代码生成的重要项目级架构决策。

### ADR / Approved Decisions

| ID | Decision | Status |
|---|---|---|
| `<ADR-001>` | `<decision>` | `<Approved>` |

没有时填写：

`None`

如果项目存在独立 ADR，例如：

```text
docs/adr/
```

AI Agent 应优先读取与当前任务相关的 ADR。

---

## 6. Approved Project Exceptions

只有已经批准、且确实偏离企业默认规则的项目例外才记录在这里。

| ID | Exception | Reason | Scope | Approved By |
|---|---|---|---|---|
| `<EX-001>` | `<exception>` | `<reason>` | `<scope>` | `<role>` |

没有例外时填写：

`None`

以下情况不自动构成 Approved Exception：

- 历史代码已经这样实现
- 其他客户项目这样实现
- 某开发人员以前这样实现
- 当前代码可以运行

如因兼容性必须沿用某种非推荐模式，应明确记录原因和适用范围。

---

## 7. Compatibility Constraints

必须保持兼容的内容：

### Public Java API

`<None 或说明>`

### External Interface

`<None 或说明>`

### Data Model

`<None 或说明>`

### Workflow / Lifecycle

`<None 或说明>`

### Historical Business Behavior

`<None 或说明>`

当前项目已有代码属于兼容性证据，不自动等同于企业开发规范。

---

## 8. Environment Topology

| Environment | Exists | Purpose |
|---|---|---|
| DEV | `<true | false>` | Development |
| TEST | `<true | false>` | Integration / System Test |
| UAT | `<true | false>` | User Acceptance Test |
| PROD | `<true | false>` | Production |

### Environment Configuration

环境差异应通过配置或部署机制管理。

项目如有重要环境配置，仅记录配置项名称：

| Configuration Key | Purpose | Sensitive |
|---|---|---|
| `<property.name>` | `<purpose>` | `<true | false>` |

本文件不得保存：

- Password
- Token
- API Key
- Private Key
- Database Password
- Session Cookie
- Production Credential
- 其他 Secret

---

## 9. External Integrations

| System | Purpose | Interface | Direction | Notes |
|---|---|---|---|---|
| `<system>` | `<purpose>` | `<REST / WRS / SOAP / MQ / File / Other>` | `<Inbound / Outbound / Both>` | `<notes>` |

没有外部集成时填写：

`None`

如接口存在 DEV / UAT / PROD 差异，只记录逻辑名称或配置 Key，不记录真实 Credential。

---

## 10. Build & Verification

### Build Command

```text
<REQUIRED>
```

### Automated Test Command

```text
<没有则填写 N/A>
```

### Static Analysis / Quality Command

```text
<没有则填写 N/A>
```

### Additional Verification

`<没有则填写 None>`

---

## 11. Windchill Runtime Access

- Agent Can Access Windchill Runtime: `<true | false>`
- Allowed Environment: `<DEV | TEST | UAT | None>`
- Deployment Allowed: `<true | false>`
- Runtime Test Allowed: `<true | false>`

如果 AI Agent 无法访问真实 Windchill Runtime，则：

`代码已实现`

或：

`编译通过`

不得描述为：

`Windchill Runtime 验证通过`

必须依赖真实环境确认的行为应标记：

`待 Windchill 环境验证`

典型包括：

- Listener 实际触发
- Event / Veto 行为
- Queue 执行
- Service Startup
- Transaction 回滚
- Access Control
- Principal / Session Context
- Workflow Runtime
- JCA / MVC 页面行为
- XCONF 实际生效
- Cluster 行为
- Performance / Concurrency

---

## 12. Golden Reference

企业批准的 Golden Reference 可以作为当前项目的实现参考。

### Explicit Project References

| Scenario | Golden Reference ID | Notes |
|---|---|---|
| `<scenario>` | `<GR-xxx>` | `<notes>` |

没有项目明确指定时填写：

`Use enterprise Golden Reference catalog when applicable.`

Golden Reference 不替代：

- 当前项目事实
- 企业 Rules
- Project ADR / Approved Exception
- 目标版本 PTC Javadoc / API Lookup
- 当前项目兼容性要求

使用 Golden Reference 时应确认其：

- Windchill Version
- XWorks 状态
- 适用业务场景
- 相关 PTC API
- 当前项目架构兼容性

不得机械复制不匹配当前项目的 Reference。

---

## 13. Sensitive / Restricted Areas

如存在 AI Agent 不应直接修改或必须人工 Review 的区域，记录在此。

| Path / Area | Constraint |
|---|---|
| `<path or module>` | `<Review required / Do not modify / Other>` |

没有时填写：

`None`

---

## 14. Project Verification Checklist

完成代码修改后，根据当前任务和实际环境检查：

- [ ] Build 已执行或明确说明无法执行
- [ ] Automated Test 已执行或明确说明不存在
- [ ] Static Check 已执行或明确说明不存在
- [ ] Git Diff 已检查
- [ ] 没有无关重构
- [ ] 没有未经批准的新运行时依赖
- [ ] 没有硬编码环境特定值
- [ ] 没有提交 Secret / Credential
- [ ] 关键 PTC API 已按需要验证
- [ ] 使用 Golden Reference 时已确认适用性
- [ ] 已遵守当前项目 XWorks Enabled 状态
- [ ] Runtime-only 行为已明确标记

未实际执行的验证不得描述为已完成。

---

## 15. Agent Working Instructions

AI Agent 处理当前项目任务时，应按以下顺序：

1. 读取本 `AGENTS.md`
2. 确认 Windchill Version 和 Java Version
3. 确认 XWorks Enabled 状态
4. 阅读当前任务相关代码和调用关系
5. 检查相关 ADR 和 Approved Project Exception
6. 应用 `windchill-ai-devkit` Rules
7. 需要 Windchill / XWorks 产品知识时使用企业 QMind
8. 需要企业批准实现模式时检查 Golden Reference
9. 需要精确 PTC API 事实时：
   - 读取当前项目 Windchill Version；
   - 读取 PTC Javadoc ZIP；
   - 必要时自动建立或复用本地 Javadoc API Index；
   - 再执行 Windchill API Lookup
10. 只实施完成当前任务所需的最小修改
11. 执行当前环境真正能够完成的 Build / Test / Review
12. 明确指出仍需 Windchill Runtime 验证的行为

不得根据模型记忆自行补全项目事实。

---

## 16. Missing Information Policy

如果以下信息缺失，并且会实质影响实现正确性：

- Windchill Version
- Java Version
- XWorks Enabled
- Project Architecture Decision
- Compatibility Constraint
- Build / Verification Method

AI Agent 应：

1. 先检查当前仓库能否找到可靠证据；
2. 无法确认时明确指出缺失项；
3. 只有缺失信息确实阻止正确决策时才向用户询问。

如果任务要求精确 PTC API 验证，但项目没有配置可用的 Javadoc ZIP，Agent 应明确说明无法完成目标版本 API 精确验证。

不得自行猜测不存在的项目事实。