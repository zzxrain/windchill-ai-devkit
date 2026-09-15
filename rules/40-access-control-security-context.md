---
trigger: model_decision
description: 当任务涉及 Windchill Access Control、AccessPermission、WTPrincipal、SessionContext、SessionHelper、SessionServerHelper、Administrator、权限绕过或 Security Label 时应用本规则。
---

# Windchill Access Control 与 Security Context 规则

## 1. 默认保持调用方的安全上下文

普通业务代码应保持当前 Principal 和正常 Access Control 语义。

不得为了：

- 避免权限异常
- 让 Persistence 操作成功
- 扩大查询结果
- 简化实现

就自动：

- 切换 Administrator
- 关闭 Access Control
- 替换 Principal
- 使用 non-access-controlled query

权限问题应首先分析实际授权模型和业务 API，而不是寻找绕过方式。

## 2. 权限提升必须有明确依据并限制范围

只有在 PTC 官方机制、明确的系统任务或经过批准的项目设计确实要求时，才允许临时提升权限或 bypass Access Control。

Administrator Principal 与关闭 Access Control Enforcement 是不同机制，不得任意互换。

权限提升应限制在完成目标操作所需的最小代码范围。

## 3. 改变 Security Context 必须恢复 previous state

临时切换 Principal / Administrator 或修改 Access Enforcement 时必须：

1. 保存原始状态
2. 执行最小范围的操作
3. 在 finally 或等效可靠路径恢复原始状态

不得假设原来的：

- Principal 一定是普通用户
- Access Enforcement 一定是 enabled

因此必须恢复 `previous`，而不是硬编码一个“默认状态”。

## 4. 服务端必须执行可信授权判断

不得只依赖：

- UI 按钮是否可见
- JavaScript
- HTTP / JSON 中传入的用户名
- 客户端声明的 Role 或管理员标志

完成敏感操作授权。

当前 Principal 应来自可信的 Windchill Security Context。

需要对象权限时，应使用 Windchill Access Control 语义；Group / Organization / Team Role membership 不得自动替代具体对象的 AccessPermission 判断。

## 5. Access Control bypass 不等于数据可以暴露

通过 Administrator、Access Control bypass 或 non-access-controlled query 获取到数据后，仍必须确认：

`这些数据最终允许暴露给谁`

不得因为服务器能够读取数据，就直接把原本普通用户无权访问的数据返回到：

- UI
- REST / WRS
- 文件
- 日志
- 外部系统

## 6. 后台和异步代码必须明确执行身份

Queue、Listener、Event、异步任务或后台 Service 不得假设天然以 Administrator 身份执行，也不得假设提交线程的 Security Context 会自动正确传递。

不得自行通过 ThreadLocal、Thread 或 Executor 模拟 Windchill Security Context。

需要改变 Context 时，同样必须遵守最小范围和恢复 previous state 的原则。

## 7. 权限异常不得自动转化为权限提升

不得使用以下 fallback：

`权限失败 → setAdministrator / disableAccessControl → 重试`

除非该行为本身就是经过明确批准的业务设计。

AI Agent 也不得自行创建通用的 `runAsAdmin()`、`disableAccessControl()` 等绕过权限 Utility 作为普通问题的快捷方案。

## 8. Security Label 场景遵守 Windchill Security Framework

项目启用 Security Labels 时，不得只考虑普通 ACL。

自定义 Security Label Evaluator 应使用 PTC 提供的扩展机制，并正确处理 Principal、Label 和 Framework 提供的对象表示。

不得假设 Evaluator 总能收到完整 Persistable；如果可能出现 `AccessControlSurrogate`，应按对应 Framework 语义处理。

## 9. Security API 必须按目标版本验证

涉及 `SessionContext`、`SessionHelper`、`SessionServerHelper`、`AccessControlHelper`、`AccessPermission`、`WTPrincipal` 或 Security Label API 时，应通过目标版本 Javadoc / API Lookup 验证。

如果 Principal、ACL、Domain、Security Label 或后台 Security Context 的实际行为必须依赖真实 Runtime 才能确认，应明确标记：

`待 Windchill 环境验证`