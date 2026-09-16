# Windchill AI DevKit Packaging

本文档定义 Windchill AI DevKit 的 Plugin ZIP 构建和发布边界。

当前目标：

```text
DevKit Git Repository
+
Pinned Golden Reference Submodule
        ↓
Self-contained Qoder Plugin ZIP
```

这里的 `Self-contained` 指：

```text
Rules
Skills
Golden Reference
Project Templates
Plugin Metadata
```

不代表当前版本已经内置 API Lookup Runtime。

普通开发人员安装最终 ZIP 时，不需要访问 Golden Reference Git Repository。

---

## 1. Package Model

源码状态：

```text
windchill-ai-devkit
        │
        └── skills/windchill-golden-reference
                │
                └── Git Submodule @ exact commit SHA
```

Git 父仓库只记录：

```text
Submodule Repository URL
+
Submodule Commit SHA
```

最终 Plugin ZIP 不应保留这种 Git Submodule 依赖关系。

构建阶段必须将 Golden Reference 的实际文件展开到：

```text
skills/windchill-golden-reference/
```

最终结构：

```text
windchill-ai-devkit-<version>.zip
├── .qoder-plugin/
│   └── plugin.json
├── rules/
├── skills/
│   ├── qmind-enterprise-router/
│   │   └── SKILL.md
│   └── windchill-golden-reference/
│       ├── SKILL.md
│       ├── CATALOG.md
│       ├── README.md
│       ├── SOURCES.md
│       ├── CURATION_NOTES.md
│       └── references/
├── templates/
├── mcp.json
└── README.md
```

Plugin ZIP 内不包含：

```text
.git/
.gitmodules
.gitignore
.idea/
Git Credential
Codeup Credential
```

---

## 2. Prerequisites

Release Machine 需要：

```text
git
tar
zip
unzip
awk
find
sort
```

建议同时安装：

```text
qoder
```

或：

```text
qodercn
```

用于执行 Plugin Validation。

---

## 3. Golden Repository Authentication

Golden Reference Repository 可以是需要认证的企业私有 Git：

```text
https://codeup.aliyun.com/60d04cfaccca0c526834b7ad/AI_Projects/windchill-customization-reference.git
```

认证只发生在：

```text
Source Checkout
CI
Release Build
```

认证信息不得写入：

```text
.gitmodules
plugin.json
Packaging Script
Plugin ZIP
```

Release Machine 应使用自己的：

```text
Git Credential Manager
macOS Keychain
SSH Agent
CI Credential
Service Account
```

完成 Git 认证。

---

## 4. Prepare Source

推荐完整 Clone：

```bash
git clone --recurse-submodules \
  <windchill-ai-devkit-repository-url>
```

如果 DevKit 已经 Clone：

```bash
git submodule update --init --recursive
```

检查：

```bash
git submodule status
```

再确认 Golden：

```bash
git -C skills/windchill-golden-reference rev-parse HEAD
```

父仓库记录的 gitlink：

```bash
git ls-tree HEAD skills/windchill-golden-reference
```

两者 SHA 必须一致。

---

## 5. Clean Working Tree Requirement

正式 Package 必须来自已经 Commit 的 Repository 状态。

构建前：

```bash
git status
```

必须：

```text
nothing to commit, working tree clean
```

Golden Submodule 同样必须：

```bash
git -C skills/windchill-golden-reference status
```

工作区不干净时，Packaging Script 会直接失败。

这样可以避免将：

```text
未提交代码
临时调试代码
本地实验 Reference
```

混入 Release。

---

## 6. Build

在 DevKit Repository 根目录执行：

```bash
./scripts/package-plugin.sh
```

脚本会：

```text
Validate Git State
        ↓
Read Plugin Name / Version
        ↓
Verify Golden gitlink SHA
        ↓
Archive DevKit Runtime Files
        ↓
Archive Golden Actual Files
        ↓
Assemble Staging Directory
        ↓
Validate Required Files
        ↓
Run Qoder Validation When Available
        ↓
Build ZIP
        ↓
Validate ZIP Structure
        ↓
Generate SHA-256
```

Plugin Version 直接读取：

```text
.qoder-plugin/plugin.json
```

因此 Packaging 文档和脚本不需要针对每个 Patch Version 修改文件名逻辑。

---

## 7. Output

默认输出：

```text
dist/
├── windchill-ai-devkit-<version>.zip
└── windchill-ai-devkit-<version>.zip.sha256
```

例如 0.5.1：

```text
dist/
├── windchill-ai-devkit-0.5.1.zip
└── windchill-ai-devkit-0.5.1.zip.sha256
```

`dist/` 和 `build/` 不提交到 Git Repository。

---

## 8. ZIP Verification

首先读取当前版本：

```bash
PLUGIN_VERSION="$(awk -F'"' '/"version"[[:space:]]*:/ { print $4; exit }' .qoder-plugin/plugin.json)"
```

查看 ZIP：

```bash
unzip -Z1 "dist/windchill-ai-devkit-${PLUGIN_VERSION}.zip"
```

必须能够看到：

```text
.qoder-plugin/plugin.json
skills/qmind-enterprise-router/SKILL.md
skills/windchill-golden-reference/SKILL.md
skills/windchill-golden-reference/CATALOG.md
```

检查 Golden Reference 数量：

```bash
unzip -Z1 "dist/windchill-ai-devkit-${PLUGIN_VERSION}.zip" \
  | grep 'skills/windchill-golden-reference/references/.*/reference.md$' \
  | wc -l
```

当前 Baseline 预期：

```text
62
```

---

## 9. Qoder Validation

如果本机安装：

```text
qoder
```

执行：

```bash
qoder plugins validate build/plugin-package/windchill-ai-devkit
```

如果中国版 CLI 为：

```text
qodercn
```

执行：

```bash
qodercn plugins validate build/plugin-package/windchill-ai-devkit
```

Packaging Script 会自动尝试执行上述 Validation。

如果两者都不存在：

```text
Qoder validation skipped
```

必须理解为：

```text
Packaging completed
≠
Qoder CLI validation completed
```

---

## 10. Qoder Upload Test

最终发布前应使用真实 ZIP 做安装测试。

在 Qoder 中：

```text
Extensions
    ↓
Plugins
    ↓
Add Plugin / Upload Plugin
```

选择：

```text
dist/windchill-ai-devkit-<version>.zip
```

安装后确认：

```text
Plugin Name
Plugin Version
Rules
QMind Skill
Golden Reference Skill
MCP Server Configuration
```

均能正确发现。

注意：

```text
MCP Server Configuration 可发现
≠
API Lookup Runtime 已成功启动
```

API Lookup Runtime 需要单独 SIT。

---

## 11. Golden Runtime Model

开发人员安装 Plugin ZIP 后：

```text
Qoder
    ↓
Installed Plugin
    ↓
skills/windchill-golden-reference
    ↓
local files
```

Qoder Runtime 不访问：

```text
Codeup
GitHub
Golden Git Repository
```

因此普通开发人员：

```text
不需要 Codeup 用户
不需要 Golden Repository Read Permission
不需要 Token
不需要 SSH Key
不需要执行 git submodule
```

---

## 12. API Lookup Runtime Dependency

当前 0.5.x 的：

```text
windchill-api-lookup
```

仍然是独立 Python Runtime / CLI。

Plugin 的：

```text
mcp.json
```

当前启动：

```text
windchill-api-lookup serve
```

因此：

```text
Plugin ZIP 成功构建
```

不代表：

```text
开发人员机器已经具备 API Lookup Runtime
```

当前内部测试前提是某个已批准 Python Runtime 中已经安装：

```text
windchill-api-lookup
```

并确保该命令能够被 Qoder MCP Process 找到。

推荐开发环境：

```text
~/.venvs/windchill-api-lookup
```

这一边界属于当前版本已知限制。

计划在后续版本评估：

```text
Standalone Binary
```

目标是进一步形成：

```text
Plugin-local API Lookup Runtime
+
Python-free End-user Installation
```

PTC Javadoc ZIP 不随 Plugin 分发。

项目仍负责提供与目标 Windchill Version 匹配、合法获得的 Javadoc ZIP。

---

## 13. Release Boundary

一个正式 Release 至少应明确：

```text
DevKit Version
DevKit Commit SHA
Golden Commit SHA
Plugin ZIP
Plugin ZIP SHA-256
```

Golden Repository 更新后，旧 ZIP 不会自动发生变化。

需要：

```text
Update Golden
        ↓
Review
        ↓
Update DevKit gitlink
        ↓
Build New Plugin ZIP
        ↓
Install / Acceptance Test
        ↓
Release
```

---

## 14. Release Candidate and Final Release

建议先建立明确的 Acceptance Baseline：

```text
Committed DevKit
+
Committed Golden
+
Plugin Version
        ↓
Package
        ↓
Install
        ↓
Acceptance
```

Acceptance 未完成前，不应声称：

```text
0.5.1 Acceptance Passed
Full SIT Passed
API Lookup Runtime Validated
```

Acceptance 通过后，再记录最终：

```text
DevKit SHA
Golden SHA
ZIP SHA-256
```

---

## 15. Packaging Principle

Plugin Packaging 的目标不是简单：

```text
zip repository
```

而是：

```text
从明确的 DevKit Commit
+
明确的 Golden Commit
构建一个自包含、可验证、可复现的 Qoder Plugin Release。
```

这里的自包含边界必须明确：

```text
0.5.x
Rules / Skills / Golden
→ Self-contained in Plugin ZIP

API Lookup Runtime
→ External Runtime Dependency
```