
---

# 根目录 `README.md`

```markdown
# Windchill AI DevKit

Windchill AI DevKit 是面向公司内部 PTC Windchill 二次开发的 Qoder Plugin。

本项目通过企业开发规则、Windchill/XWorks 企业知识、Golden Reference、PTC Javadoc API 精确查询以及项目级上下文，为 AI Coding Agent 提供受控的 Windchill 二次开发能力。

目标不是让 AI “记住所有 Windchill 知识”，而是建立一套可验证、可维护、可迭代的 Windchill AI Coding Harness。

---

## 1. Goals

本项目主要解决以下问题：

- 降低 AI 编造 Windchill / PTC API 的概率
- 约束 AI 遵循企业 Windchill 开发规范
- 避免直接复制历史项目中的低质量实现
- 复用企业批准的 Golden Reference
- 根据 Windchill 版本获取精确 API 事实
- 根据项目实际情况处理 XWorks
- 区分企业通用规则和客户项目特殊要求
- 明确 DEV / TEST / UAT / PROD 配置边界
- 区分“代码已生成”和“Windchill Runtime 已验证”
- 为公司后续持续积累 Windchill AI 开发资产提供统一入口

---

## 2. Architecture

```text
                        Windchill Project
                              │
                              ▼
                          AGENTS.md
                              │
           ┌──────────────────┼──────────────────┐
           │                  │                  │
           ▼                  ▼                  ▼
         Rules              QMind        Golden Reference
           │                  │                  │
           └──────────────────┼──────────────────┘
                              │
                              ▼
                   Windchill API Lookup
                              │
                              ▼
                        AI Coding Agent
                              │
                              ▼
                    Build / Test / Review
                              │
                              ▼
                 Windchill Runtime Verification