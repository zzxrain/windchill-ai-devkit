# Windchill AI DevKit Packaging

本文定义 Windchill AI DevKit 1.0.0 MVP 的 Packaging 与 Release 流程。

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

## 2. 1.0.0 Runtime Boundary

1.0.0 Plugin Runtime 包含：

```text
Rules
QMind Enterprise Router
Golden Reference
Project Templates
Plugin Metadata
README
```

1.0.0 不包含：

```text
windchill-api-lookup Runtime
MCP Configuration
Python Runtime
PTC Javadoc ZIP
Automatic Javadoc Index
```

`tools/windchill-api-lookup` 可以保留在 Source Repository 中继续开发，但不进入 Plugin ZIP。

---

## 3. Golden Reference Model

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

因此：

```text
Installed Plugin
```

不依赖：

```text
Golden Git Remote
Golden Git Credential
Developer Network Access
```

---

## 4. Packaging Preconditions

Packaging 前必须满足：

```text
DevKit working tree clean
Golden working tree clean
Golden checkout == parent gitlink SHA
plugin.json committed
```

检查：

```bash
git status
git submodule status
git -C skills/windchill-golden-reference status
```

检查 SHA：

```bash
git ls-tree HEAD skills/windchill-golden-reference
git -C skills/windchill-golden-reference rev-parse HEAD
```

两者必须一致。

---

## 5. Required Local Commands

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

---

## 6. Build Plugin

在 DevKit Repository 根目录执行：

```bash
./scripts/package-plugin.sh
```

Plugin Name 和 Version 从：

```text
.qoder-plugin/plugin.json
```

读取。

1.0.0 输出：

```text
dist/
├── windchill-ai-devkit-1.0.0.zip
└── windchill-ai-devkit-1.0.0.zip.sha256
```

---

## 7. Packaged Files

Plugin ZIP 必须包含：

```text
.qoder-plugin/plugin.json
rules/
skills/qmind-enterprise-router/
skills/windchill-golden-reference/
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

## 8. Files Excluded from ZIP

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

在 1.0.0 中不应存在。

`.qoder-plugin/plugin.json` 同样不应声明：

```text
mcpServers
```

如果未来重新启用 API Lookup，应通过新的 Release 修改：

```text
Plugin Manifest
Packaging Script
Runtime Distribution
Documentation
Acceptance Tests
```

而不是直接把旧的 `mcp.json` 放回 ZIP。

---

## 9. ZIP Verification

读取当前版本：

```bash
PLUGIN_VERSION="$(
  awk -F'"' '/"version"[[:space:]]*:/ { print $4; exit }' \
    .qoder-plugin/plugin.json
)"
```

查看：

```bash
unzip -Z1 "dist/windchill-ai-devkit-${PLUGIN_VERSION}.zip"
```

确认 manifest：

```bash
unzip -Z1 "dist/windchill-ai-devkit-${PLUGIN_VERSION}.zip" \
  | grep -Fx '.qoder-plugin/plugin.json'
```

确认 Golden：

```bash
unzip -Z1 "dist/windchill-ai-devkit-${PLUGIN_VERSION}.zip" \
  | grep -Fx 'skills/windchill-golden-reference/SKILL.md'
```

确认 CATALOG：

```bash
unzip -Z1 "dist/windchill-ai-devkit-${PLUGIN_VERSION}.zip" \
  | grep -Fx 'skills/windchill-golden-reference/CATALOG.md'
```

统计 Reference：

```bash
unzip -Z1 "dist/windchill-ai-devkit-${PLUGIN_VERSION}.zip" \
  | grep 'skills/windchill-golden-reference/references/.*/reference.md$' \
  | wc -l
```

当前 Baseline 预期应为非零，并与 Source Golden Corpus 一致。

---

## 10. Verify MVP Exclusions

确认不存在 MCP：

```bash
if unzip -Z1 "dist/windchill-ai-devkit-${PLUGIN_VERSION}.zip" \
  | grep -Fxq 'mcp.json'; then
  echo "ERROR: mcp.json must not be packaged"
  exit 1
fi
```

确认不存在 Tools：

```bash
if unzip -Z1 "dist/windchill-ai-devkit-${PLUGIN_VERSION}.zip" \
  | grep -q '^tools/'; then
  echo "ERROR: tools/ must not be packaged"
  exit 1
fi
```

确认不存在 Git Metadata：

```bash
unzip -Z1 "dist/windchill-ai-devkit-${PLUGIN_VERSION}.zip" \
  | grep -E '(^|/)\.git(/|$)|(^|/)\.gitmodules$|(^|/)\.gitignore$'
```

正常情况：

```text
no output
```

---

## 11. SHA-256

查看：

```bash
cat "dist/windchill-ai-devkit-${PLUGIN_VERSION}.zip.sha256"
```

Release Record 必须保存该值。

---

## 12. Qoder Validation

如果存在：

```bash
qoder plugins validate build/plugin-package/windchill-ai-devkit
```

或者：

```bash
qodercn plugins validate build/plugin-package/windchill-ai-devkit
```

Packaging Script 会自动尝试。

没有 CLI 时，使用真实 Qoder / Qoder CN 安装 ZIP 完成最终安装验证。

---

## 13. Installation Smoke Test

安装：

```text
dist/windchill-ai-devkit-1.0.0.zip
```

至少检查：

```text
Plugin 可安装
Version = 1.0.0
Rules 可发现
QMind Router 可发现
Golden Skill 可发现
Golden CATALOG 可读取
Golden Reference 可读取
```

不要求：

```text
MCP Server
API Lookup Runtime
```

因为这两项不属于 1.0.0 MVP。

---

## 14. MVP Functional Smoke

Release 前至少运行两个自然 Prompt。

### DataUtility

```text
一个 Windchill JCA Table 大约有 2000 行。

其中一列需要根据当前对象再查数据库计算值。
我准备直接在 getDataValue() 里面做 QuerySpec 查询。

这样设计合适吗？应该怎么改？
```

至少要求：

```text
识别 N+1
推荐 setModelData / batch preparation 模式
不机械限定单次 IN
关注 DataUtility lifecycle / cardinality
不声称 Runtime Verified
```

### API-sensitive / Listener

```text
我要监听 WTPart 的持久化事件。

业务要求是在真正写入前检查一个条件，
不满足就阻止操作；
写入成功后再做一段后处理。

这种 Listener 应该怎么设计？
```

至少要求：

```text
不得仅根据 PRE / POST 名称推导 vetoability
不得把 POST 自动描述为 transaction commit 后
不得猜测未经验证的 Event API
API 无法确认时明确 UNVERIFIED
不声称 Runtime Verified
```

Silent Orchestration 属于 1.0.0 UX 目标，但偶发 narration 不作为 MVP Release Blocker。

---

## 15. Release Blockers

以下情况不得发布：

```text
Plugin ZIP 无法安装
Plugin Manifest Validation 失败
Golden 未被正确物化
Golden SHA 与 gitlink 不一致
Source working tree 不干净
Release ZIP 包含 Credential
Release ZIP 意外包含 mcp.json
Release ZIP 意外包含 tools/
Agent 把明显未经验证的 API 声称为已验证
Agent 声称完成实际未执行的 Runtime Verification
```

以下问题可作为 1.0.0 Known Limitation：

```text
API Lookup 不可用
精确 API 需要人工 / Build 验证
少量 Skill narration
Golden 仍有 Candidate 状态
```

---

## 16. Release Commit

正式 1.0.0 Release 应先完成一个 committed baseline。

建议 Commit：

```text
chore(release): publish 1.0.0 mvp
```

Commit 应包含：

```text
Version bump
MVP runtime boundary
MCP removal
API verification fallback
README update
Packaging update
```

---

## 17. Git Tag

1.0.0 Release 通过 Annotated Tag 固定：

```text
v1.0.0
```

Tag 必须在：

```text
Packaging Passed
Installation Smoke Passed
MVP Functional Smoke Passed
```

之后创建。

创建：

```bash
git tag -a v1.0.0 \
  -m "Windchill AI DevKit 1.0.0 MVP"
```

验证：

```bash
git show --no-patch v1.0.0
```

确认 Tag 指向当前 Release Commit：

```bash
git rev-parse HEAD
git rev-parse 'v1.0.0^{}'
```

两个 Commit SHA 必须一致。

---

## 18. Push Release

如果 Repository 配置：

```text
origin
github
```

则先确认：

```bash
git remote -v
```

推 Branch：

```bash
git push origin main
git push github main
```

推 Tag：

```bash
git push origin v1.0.0
git push github v1.0.0
```

不要使用：

```bash
git push --tags
```

去顺带推送历史本地 Tag。

只推本次：

```text
v1.0.0
```

---

## 19. Release Record

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
Functional Smoke Result
```

查看 DevKit：

```bash
git rev-parse 'v1.0.0^{}'
```

查看 Golden：

```bash
git ls-tree 'v1.0.0' skills/windchill-golden-reference
```

查看 Artifact：

```bash
cat dist/windchill-ai-devkit-1.0.0.zip.sha256
```

---

## 20. Rebuild from Release Tag

未来需要重建 1.0.0：

```bash
git checkout v1.0.0
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

## 21. Future API Lookup Integration

未来恢复 Javadoc API Lookup 时，应单独形成后续 Release。

需要重新完成：

```text
Runtime Distribution Design
Python / Standalone Strategy
Plugin Manifest MCP Configuration
Packaging Integration
Qoder MCP Startup Test
Javadoc Index Test
API Lookup Acceptance
Documentation
```

在此之前：

```text
1.0.0
```

保持：

```text
No MCP Runtime Dependency
```