---
trigger: model_decision
description: 当任务涉及 Windchill Property、XCONF、xconfmanager、site.xconf、declarations.xconf、wt.properties、Safe Area、wtSafeArea、PTC 标准文件、环境配置或 DEV/UAT/PROD 配置差异时应用本规则。
---

# Windchill 配置与定制文件规则

## 1. 优先使用 Windchill 官方配置机制

修改 Windchill 配置时，应优先使用目标版本提供的正式机制，例如：

- `xconfmanager`
- `site.xconf`
- Custom XCONF
- PTC 提供的专用配置文件或管理机制

不得把直接修改最终运行时文件作为默认方案。

具体配置方式必须以目标 Windchill 版本文档为准。

---

## 2. 不得直接维护生成后的 Property 文件

对于由 XCONF 管理的 Property，不应直接修改：

`wt.properties`

或其他最终生成的 `*.properties` 文件作为配置源。

应通过 `xconfmanager` / XCONF 维护配置并传播到目标 Property 文件。

生成后的 Property 文件属于运行结果，不应成为唯一的配置源。

注意：并非所有 Property 文件都适合通过 `xconfmanager` 管理；遇到特殊文件时必须根据目标版本 PTC 文档确认。

---

## 3. PTC 提供的 XCONF 文件默认不得直接修改

PTC 提供的 `*.xconf` 文件通常应视为只读。

需要新增或覆盖配置时，应优先：

- 使用 `site.xconf`
- 创建 Custom XCONF
- 通过 `xconfmanager` 注册和传播配置

不得为了方便直接修改 PTC 标准 XCONF 文件。

对于 `site.xconf`、`declarations.xconf` 等特殊文件，也应优先通过 PTC 提供的工具管理，而不是手工编辑内部结构。

---

## 4. 大量自定义 Property 应使用 Custom XCONF

如果需要增加或维护较多自定义 Property，不应生成大量独立的：

`xconfmanager -s ...`

操作作为长期配置方案。

应优先评估创建项目自己的 declarative XCONF，并由 Windchill 配置机制统一管理和传播。

自定义 Property 应：

- 使用明确的命名空间
- 避免与 PTC Property 冲突
- 明确默认值和环境覆盖关系

---

## 5. 修改 PTC 标准文件时必须使用官方 Customization Maintenance 机制

如果业务确实需要修改 PTC 发布的标准文件，应使用目标版本要求的 Safe Area / customization maintenance 机制。

典型情况下应保留：

- `wtSafeArea/ptcOrig`：PTC 原始版本
- `wtSafeArea/siteMod`：项目修改版本

Maintenance Update 后，应能够比较项目修改与 PTC 新版本变化。

不得只修改 Windchill Runtime 目录中的 PTC 文件而不保留可追踪的定制来源。

---

## 6. 能新增 Custom 文件时，优先避免修改 PTC 文件

如果 Windchill 提供：

- Site-specific 文件
- Custom 配置文件
- Extension Point
- 自定义资源文件
- 可注册的 Custom Class

应优先采用这些方式，而不是修改 PTC OOTB 文件。

只有在对应官方定制机制确实要求修改 PTC 文件时，才进入 Safe Area 管理流程。

---

## 7. 环境差异必须配置化

以下内容原则上不得直接硬编码在业务代码中：

- Hostname
- URL
- Port
- 文件系统路径
- Timeout
- 外部服务地址
- 环境标识
- 用户名
- Password / Token / Secret

DEV、TEST、UAT、PROD 等环境之间的差异，应通过配置或部署机制提供，而不是通过修改业务源码实现。

不得为了适配不同环境，在业务代码中散布类似：

```java
if (isProd) {
    ...
} else {
    ...
}