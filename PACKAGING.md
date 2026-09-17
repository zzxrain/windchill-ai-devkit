# Windchill AI DevKit Packaging

本文定义 Windchill AI DevKit 1.0.x 的 Packaging、Verification 与 Release 流程。

当前开发版本：

```text
1.0.1
```

已冻结 Baseline：

```text
v1.0.0
```

---

## 1. Release Model

Plugin Release 由以下内容共同定义：

```text
Committed DevKit
+
Pinned Golden Reference Commit
+
Plugin Version
+
Plugin ZIP
+
SHA-256
+
Git Tag
```

发布后的 ZIP 不依赖普通开发人员访问 Golden Git Repository。

---

## 2. 1.0.x Runtime Boundary

1.0.x Plugin Runtime 包含：

```text
Rules
QMind Enterprise Router
Golden Reference
QMind Retrieve Contract Guard
Project Templates
Plugin Metadata
README
```

1.0.x 不包含：

```text
windchill-api-lookup Runtime
PTC Javadoc ZIP
Python Runtime
Automatic Javadoc Index
Automatic Compile Verification
Automatic Runtime Verification
Semantic Product-fact Response Guard
```

`tools/windchill-api-lookup` 可以保留在 Source Repository 中继续开发，但不进入 1.0.x Plugin ZIP。

---

## 3. 1.0.1 Release Purpose

1.0.1 是：

```text
Quality-neutral Performance Patch
```

主要优化：

```text
Golden Reference Minimum Sufficient Evidence
Reference Sufficiency Gate
减少不必要 src/* 深入读取
减少无目的目录扫描
```

不得通过以下方式换取性能：

```text
跳过必要 Golden Preflight
跳过必要 QMind Product Evidence
跳过必要 API Evidence
降低 Technical Correctness
强制限制 Tool Call 总数
使用超时强行提前结束回答
```

发布原则：

```text
Quality First
Performance Second
```

---

## 4. Golden Reference Model

Golden Repository：

```text
https://codeup.aliyun.com/60d04cfaccca0c526834b7ad/AI_Projects/windchill-customization-reference.git
```

DevKit 中位置：

```text
skills/windchill-golden-reference
```

采用：

```text
Git Submodule
```

父 Repository 保存：

```text
Golden Commit SHA
```

Packaging 时把该 Commit 的实际文件物化到 Plugin ZIP。

因此 Installed Plugin 不依赖：

```text
Golden Git Remote
Golden Git Credential
Developer Network Access
```

GitHub Golden Repository 仅作为 Mirror / Inspection Source。

`.gitmodules` 不应因此改为 GitHub URL。

---

## 5. Packaging Preconditions

Packaging 前必须满足：

```text
DevKit working tree clean
Golden working tree clean
Golden checkout == parent gitlink SHA
plugin.json committed
README version current
Release documentation current
```

检查：

```bash
git status --short
git submodule status
git -C skills/windchill-golden-reference status --short
```

检查 SHA：

```bash
git ls-tree HEAD skills/windchill-golden-reference
git -C skills/windchill-golden-reference rev-parse HEAD
```

两者必须一致。

检查当前 Plugin Version：

```bash
grep -n '"version"' .qoder-plugin/plugin.json
```

当前 1.0.1 应为：

```text
"version": "1.0.1"
```

---

## 6. Required Local Commands

Packaging Script 需要：

```text
git
tar
zip
unzip
awk
find
sort
grep
sed
```

SHA-256 使用：

```text
shasum
```

或：

```text
sha256sum
```

Qoder CLI Validation 属于可选能力：

```text
qoder
```

或：

```text
qodercn
```

如果不存在，Packaging 可以继续，但必须理解：

```text
Package Created
≠
Qoder CLI Validation Passed
```

此时必须使用真实 Qoder / Qoder CN 安装 ZIP 完成安装验证。

---

## 7. Build Plugin

在 DevKit Repository 根目录执行：

```bash
./scripts/package-plugin.sh
```

Plugin Name 和 Version 从：

```text
.qoder-plugin/plugin.json
```

读取。

1.0.1 输出：

```text
dist/
├── windchill-ai-devkit-1.0.1.zip
└── windchill-ai-devkit-1.0.1.zip.sha256
```

Packaging 使用：

```text
Committed DevKit HEAD
+
Pinned Golden Commit
```

而不是未提交的 working tree 内容。

---

## 8. Packaged Files

Plugin ZIP 必须包含：

```text
.qoder-plugin/plugin.json
rules/
skills/qmind-enterprise-router/
skills/windchill-golden-reference/
hooks/hooks.json
bin/qmind-retrieve-guard
bin/qmind-retrieve-guard.cmd
bin/qmind-retrieve-guard.ps1
templates/
README.md
```

Golden 必须至少包含：

```text
skills/windchill-golden-reference/SKILL.md
skills/windchill-golden-reference/CATALOG.md
skills/windchill-golden-reference/references/
```

---

## 9. Files Excluded from ZIP

Plugin ZIP 不包含：

```text
.git/
.gitmodules
.gitignore
.idea/
.DS_Store
tools/
mcp.json
PACKAGING.md
scripts/
Python Runtime
PTC Javadoc
Git Credential
```

特别注意：

```text
mcp.json
```

在 1.0.x 中不应存在。

`.qoder-plugin/plugin.json` 同样不应声明：

```text
mcpServers
```

如果未来重新启用 API Lookup，应通过新的 Minor Release 正式修改：

```text
Plugin Manifest
Packaging Script
Runtime Distribution
Documentation
Acceptance Tests
```

不能仅把历史 `mcp.json` 放回 ZIP。

---

## 10. Read Current Version

```bash
PLUGIN_VERSION="$(
  awk -F'"' '/"version"[[:space:]]*:/ { print $4; exit }' \
    .qoder-plugin/plugin.json
)"
```

确认：

```bash
printf '%s\n' "${PLUGIN_VERSION}"
```

1.0.1 Candidate 应输出：

```text
1.0.1
```

---

## 11. ZIP Verification

查看：

```bash
unzip -Z1 "dist/windchill-ai-devkit-${PLUGIN_VERSION}.zip"
```

确认 manifest：

```bash
unzip -Z1 "dist/windchill-ai-devkit-${PLUGIN_VERSION}.zip" \
  | grep -Fx '.qoder-plugin/plugin.json'
```

确认 Rules：

```bash
unzip -Z1 "dist/windchill-ai-devkit-${PLUGIN_VERSION}.zip" \
  | grep -Fx 'rules/00-core-development-rules.md'
```

确认 QMind：

```bash
unzip -Z1 "dist/windchill-ai-devkit-${PLUGIN_VERSION}.zip" \
  | grep -Fx 'skills/qmind-enterprise-router/SKILL.md'
```

确认 Golden：

```bash
unzip -Z1 "dist/windchill-ai-devkit-${PLUGIN_VERSION}.zip" \
  | grep -Fx 'skills/windchill-golden-reference/SKILL.md'
```

确认 Golden CATALOG：

```bash
unzip -Z1 "dist/windchill-ai-devkit-${PLUGIN_VERSION}.zip" \
  | grep -Fx 'skills/windchill-golden-reference/CATALOG.md'
```

确认 Hook：

```bash
unzip -Z1 "dist/windchill-ai-devkit-${PLUGIN_VERSION}.zip" \
  | grep -Fx 'hooks/hooks.json'
```

确认 QMind Guard：

```bash
unzip -Z1 "dist/windchill-ai-devkit-${PLUGIN_VERSION}.zip" \
  | grep -E '^bin/qmind-retrieve-guard(\.cmd|\.ps1)?$'
```

预期三条。

统计 Golden Reference：

```bash
unzip -Z1 "dist/windchill-ai-devkit-${PLUGIN_VERSION}.zip" \
  | grep 'skills/windchill-golden-reference/references/.*/reference.md$' \
  | wc -l
```

应为非零，并与 Source Golden Corpus 一致。

---

## 12. Verify Manifest

```bash
unzip -p \
  "dist/windchill-ai-devkit-${PLUGIN_VERSION}.zip" \
  .qoder-plugin/plugin.json
```

1.0.1 应确认：

```text
name = windchill-ai-devkit
version = 1.0.1
rules = ./rules
QMind Skill 存在
Golden Skill 存在
hooks = ./hooks/hooks.json
无 mcpServers
```

---

## 13. Verify README

```bash
unzip -p \
  "dist/windchill-ai-devkit-${PLUGIN_VERSION}.zip" \
  README.md \
  | head -30
```

必须看到：

```text
当前版本：
1.0.1
```

不得再显示：

```text
当前版本：
1.0.0
```

---

## 14. Verify 1.0.x Exclusions

确认不存在 MCP 配置：

```bash
if unzip -Z1 "dist/windchill-ai-devkit-${PLUGIN_VERSION}.zip" \
  | grep -Eq '^mcp\.json$|^\.mcp\.json$'; then
  echo "ERROR: MCP config must not be packaged in 1.0.x"
  exit 1
fi
```

确认不存在 Tools：

```bash
if unzip -Z1 "dist/windchill-ai-devkit-${PLUGIN_VERSION}.zip" \
  | grep -q '^tools/'; then
  echo "ERROR: tools/ must not be packaged in 1.0.x"
  exit 1
fi
```

确认不存在 Git Metadata：

```bash
unzip -Z1 "dist/windchill-ai-devkit-${PLUGIN_VERSION}.zip" \
  | grep -E '(^|/)\.git(/|$)|(^|/)\.gitmodules$|(^|/)\.gitignore$'
```

正常：

```text
no output
```

---

## 15. SHA-256

查看：

```bash
cat "dist/windchill-ai-devkit-${PLUGIN_VERSION}.zip.sha256"
```

macOS 验证：

```bash
shasum -a 256 \
  "dist/windchill-ai-devkit-${PLUGIN_VERSION}.zip"
```

Linux 如使用：

```bash
sha256sum \
  "dist/windchill-ai-devkit-${PLUGIN_VERSION}.zip"
```

计算结果必须与 `.sha256` 文件一致。

---

## 16. Qoder CLI Validation

如果存在：

```bash
qoder plugins validate build/plugin-package/windchill-ai-devkit
```

或者：

```bash
qodercn plugins validate build/plugin-package/windchill-ai-devkit
```

Packaging Script 会自动尝试。

没有 CLI 时：

```text
WARNING
```

不是 Package Failure。

但仍需要执行实际安装 Smoke Test。

---

## 17. Installation Smoke Test

1.0.1 Candidate 安装流程：

```text
卸载当前 Windchill AI DevKit
        ↓
完全退出 Qoder / Qoder CN
        ↓
重新启动
        ↓
安装 windchill-ai-devkit-1.0.1.zip
        ↓
重新打开测试 Workspace
```

至少检查：

```text
Plugin 可安装
Version = 1.0.1
Rules 可发现
QMind Router 可发现
Golden Skill 可发现
Golden CATALOG 可读取
Golden Reference 可读取
Hook 配置可加载
QMind Retrieve Guard 可执行
```

---

## 18. QMind Guard Smoke

仍使用确定性的 Guard 测试。

缺 `notebookId`：

```text
qoder-qmind retrieve
query only
```

应在 MCP Server 前被 DevKit Guard 阻止。

不得再出现：

```text
tool parameter validation failed:
params must have required property 'notebookId'
```

作为首次失败路径。

合法：

```text
notebookId
+
query
```

必须放行。

---

## 19. Functional Smoke — Listener

使用全新 Chat：

```text
我要监听 WTPart 的持久化事件。

业务要求是在真正写入前检查一个条件，
不满足就阻止操作；
写入成功后再做一段后处理。

这种 Listener 应该怎么设计？
```

正式质量验收维度固定为六项：

```text
Autonomous Trigger
Minimal Evidence Selection
Silent Orchestration
Evidence Routing
Technical Correctness
Runtime Honesty
```

只使用：

```text
PASS
PARTIAL
FAIL
```

最低技术要求：

```text
不得仅根据 PRE / POST 名称推导 vetoability
不得把 POST 自动描述为 transaction commit 后
不得把 Product Convention 扩大为绝对语义
不得把未经验证的 PTC API 声称为 VERIFIED
不得声称 Runtime Verified
```

1.0.1 性能关注：

```text
CATALOG
→ 直接匹配 Reference
→ reference.md
```

如果 Pattern 已经充分，不应默认继续：

```text
ls -R
find
读取所有 src/*
```

但如果具体代码、Review 或 Debug 确实需要 Source，则允许继续读取。

---

## 20. Functional Smoke — DataUtility

使用全新 Chat：

```text
一个 Windchill JCA Table 大约有 2000 行。

其中一列需要根据当前对象再查数据库计算值。
我准备直接在 getDataValue() 里面做 QuerySpec 查询。

这样设计合适吗？应该怎么改？
```

最低技术要求：

```text
识别 N+1 风险
推荐 setModelData / batch preparation
不机械要求一次巨大 IN
考虑 DataUtility lifecycle
考虑 registration / cardinality / mutable state
不声称 Runtime Verified
```

性能关注：

```text
GR-UI-007
```

如果已经足以回答 Pattern，不应为了完整性默认打开 Source。

只有 registration / cardinality 确实影响当前结论时，才增加：

```text
GR-UI-008
```

---

## 21. 1.0.1 Performance Measurements

性能数据不作为第七个质量维度。

单独记录：

```text
Elapsed Time
Tool Call Count
Golden reference.md Reads
Golden src/* Reads
QMind Retrieve Count
```

与 1.0.0 Baseline 比较。

优先判断：

```text
无必要 Tool Call 是否减少
```

而不是只看：

```text
Wall-clock
```

因为 Wall-clock 会受到：

```text
Model Provider Load
Network
Reasoning Effort
Context Length
Local Machine
Tool Runtime
```

影响。

---

## 22. 1.0.1 Acceptance Rule

1.0.1 可以进入 Release Candidate 的条件：

```text
Quality 没有明显下降
+
Technical Correctness 不低于 Baseline
+
Evidence Routing 保持
+
Golden 不必要 Tool Calls 明显减少
```

如果：

```text
100s → 35s
```

但答案错误明显增加，则：

```text
FAIL
```

如果：

```text
100s → 70s
Tool Calls 12 → 6
质量保持
```

则可以认为性能优化有效。

---

## 23. Release Blockers

以下情况不得发布：

```text
Plugin ZIP 无法安装
Plugin Manifest Validation 失败
Golden 未正确物化
Golden SHA 与 gitlink 不一致
Source Working Tree 不干净
README Version 与 Manifest 不一致
Release ZIP 包含 Credential
Release ZIP 意外包含 MCP Config
Release ZIP 意外包含 tools/
QMind Guard 失效
Technical Correctness 相比 1.0.0 明显下降
Agent 声称未经验证的 API 已 VERIFIED
Agent 声称完成实际未执行的 Runtime Verification
```

以下问题可作为 1.0.1 Known Limitation：

```text
API Lookup Runtime 不可用
精确 API 需要人工 / Build 验证
少量 Skill Narration
Golden 仍主要为 Candidate
```

---

## 24. 1.0.0 Baseline Tag

1.0.0 已通过 Annotated Tag 固定：

```text
v1.0.0
```

验证：

```bash
git rev-parse 'v1.0.0^{}'
```

当前 Baseline Commit：

```text
3eb2480033232f81fee56100b3d054d64eeb6069
```

不得为了 1.0.1 修改、移动或重建该 Tag。

---

## 25. 1.0.1 Release Commit

1.0.1 的 Golden 性能实现提交已经独立存在。

Release 文档更新使用：

```text
docs(release): document 1.0.1 performance release
```

后续如果测试暴露真正 Release Bug：

```text
追加新的 fix commit
```

不要重写已 push 的历史。

---

## 26. Push Branch

每次 Release 修改 commit 后立即：

```bash
git push origin main
git push github main
```

再：

```bash
git fetch --all --prune

git rev-parse HEAD
git rev-parse origin/main
git rev-parse github/main

git rev-list --left-right --count HEAD...origin/main
git rev-list --left-right --count HEAD...github/main
```

两个 count 都必须：

```text
0	0
```

---

## 27. Create v1.0.1 Tag

只有在：

```text
Packaging Passed
Installation Smoke Passed
QMind Guard Smoke Passed
Listener Functional Test Passed
DataUtility Functional Test Passed
Performance Regression Passed
```

以后创建。

先确认不存在：

```bash
git tag --list 'v1.0.1'

git ls-remote --tags origin 'refs/tags/v1.0.1*'
git ls-remote --tags github 'refs/tags/v1.0.1*'
```

都为空后：

```bash
git tag -a v1.0.1 \
  -m "Windchill AI DevKit 1.0.1"
```

验证：

```bash
git rev-parse HEAD
git rev-parse 'v1.0.1^{}'
```

必须一致。

---

## 28. Push v1.0.1

只 push 当前 Tag：

```bash
git push origin v1.0.1
git push github v1.0.1
```

不得使用：

```bash
git push --tags
```

验证：

```bash
git ls-remote --tags origin \
  'refs/tags/v1.0.1' \
  'refs/tags/v1.0.1^{}'

git ls-remote --tags github \
  'refs/tags/v1.0.1' \
  'refs/tags/v1.0.1^{}'
```

两个 Remote 的 dereferenced commit 必须一致。

---

## 29. Release Record

发布后至少记录：

```text
Plugin Version
Git Tag
DevKit Commit SHA
Golden Commit SHA
ZIP SHA-256
Reference Count
Qoder Validation Result
Installation Smoke Result
QMind Guard Smoke Result
Listener Quality Result
DataUtility Quality Result
Performance Result
```

查看 DevKit：

```bash
git rev-parse 'v1.0.1^{}'
```

查看 Golden：

```bash
git ls-tree 'v1.0.1' skills/windchill-golden-reference
```

查看 Artifact：

```bash
cat dist/windchill-ai-devkit-1.0.1.zip.sha256
```

---

## 30. Rebuild Released Version

### 1.0.0

```bash
git checkout v1.0.0
git submodule update --init --recursive
./scripts/package-plugin.sh
```

### 1.0.1

```bash
git checkout v1.0.1
git submodule update --init --recursive
./scripts/package-plugin.sh
```

因为：

```text
Plugin Version
DevKit Files
Golden gitlink
```

都由 Release Tag 固定。

---

## 31. Future API Lookup Integration

Javadoc API Lookup 应作为后续 Minor Release 正式进入 Runtime。

需要重新完成：

```text
Runtime Distribution Design
Cross-platform Runtime Strategy
Plugin MCP Configuration
Packaging Integration
Qoder MCP Startup Test
Javadoc Index Test
API Lookup Acceptance
Documentation
```

在此之前：

```text
1.0.x
```

保持：

```text
No Javadoc MCP Runtime Dependency
```