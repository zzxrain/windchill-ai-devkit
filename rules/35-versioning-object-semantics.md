---
trigger: model_decision
description: 当任务涉及 Windchill Master、Version、Revision、Iteration、Latest、Checkout、Checkin、Working Copy、VersionControl 或 WorkInProgress 时应用本规则。
---

# Windchill 版本对象语义规则

## 1. 必须区分 Master、Version 和 Iteration

版本化 Windchill 对象不能视为普通单记录实体。

处理查询、属性或 Link 前，必须明确当前代码操作的是：

- Master
- 某个 Version / Revision
- 某个 Iteration

例如 `WTPartMaster` 与 `WTPart` 表示不同的对象层级，不得互换使用。

属性和关联也必须确认实际定义在哪个层级。

## 2. “Latest / Current / Previous” 必须明确具体语义

不得把：

- latest iteration
- latest revision / version
- latest revision 的 latest iteration
- previous iteration
- previous revision
- ConfigSpec 选择出的对象

混为同一概念。

不得通过第一条/最后一条查询结果、OID、创建时间或普通字符串排序推断“最新版本”。

需求含义不明确时，应先指出歧义，而不是自行选择一种 latest。

## 3. 必须区分 Original 与 Working Copy

对象 `isCheckedOut` 不代表当前对象本身就是 Working Copy。

涉及 Workable 对象时，应确认：

- 当前对象是 Original 还是 Working Copy
- 是否已经 Checkout
- Working Copy 属于哪个 Principal
- 当前操作应作用于哪一个对象

需要 Working Copy 时，应使用对应 Work In Progress API 获取，不得自行猜测或转换。

## 4. 不得为了修改成功而自动 Checkout

对于 Workable 对象，应根据业务语义判断是否需要 Checkout / Checkin。

不得建立：

`所有版本对象修改都必须 Checkout`

这样的绝对规则，也不得因为直接修改失败就自动加入：

`checkout → modify → checkin`

如果对象已被 Checkout，应区分：

- 当前用户已有 Working Copy
- 其他用户已 Checkout

不得通过 Administrator、关闭 Access Control 或直接 Persistence 修改绕过正常 WIP 语义。

## 5. Version Control 行为必须使用 Windchill Version Control / WIP 机制

涉及以下行为时，应优先使用目标版本正式 API：

- revise / new version
- iteration
- latest / predecessor
- checkout / checkin / undo checkout
- working copy
- master / version navigation

不得通过 Persistence、SQL 或手工修改：

- Version / Iteration identifier
- Branch identifier
- Checkout state
- Master reference

模拟 Windchill Version Control。

## 6. 不得自行计算 Version / Iteration 顺序

Version 和 Iteration identifier 可能受到 Versioning Scheme 和项目配置影响。

不得通过：

- 字符串比较
- ASCII 顺序
- 字母递增
- 数字解析

实现 latest、previous、next 或 ordering。

必须使用适用于当前对象和目标版本的 Windchill Version Control 机制。

## 7. 对象引用必须匹配业务身份层级

保存 OID、创建 Link 或与外部系统交换对象标识时，应明确需要的是：

- 某个具体 Version / Iteration
- 还是跨版本稳定的 Master identity

不得把具体 Iteration OID 当作永远代表“当前业务对象”的稳定标识。

Link 也必须确认 Role A / Role B 实际关联的是 Master 还是 Version / Iteration。

## 8. ConfigSpec 场景不能简化成 Latest Version

BOM、结构和配置过滤中的对象选择可能受到 View、State、Effectivity、Baseline、Working Copy、ConfigSpec 或 Navigation Criteria 等条件影响。

不得简单用“取 latest version”替代 Windchill 配置选择语义。

## 9. Versioning API 必须按目标版本验证

使用 `VersionControl*`、`WorkInProgress*`、`Versioned`、`Iterated`、`Mastered`、`Workable` 等 API 时，应通过目标版本 Javadoc / API Lookup 验证实际 API 和 overload。

无法确认 Working Copy、Checkout ownership 或版本选择行为时，明确标记：

`待 Windchill 环境验证`