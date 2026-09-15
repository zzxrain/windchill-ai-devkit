#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

GOLDEN_PATH="skills/windchill-golden-reference"
BUILD_ROOT="${REPO_ROOT}/build/plugin-package"
DIST_DIR="${REPO_ROOT}/dist"

log() {
  printf '[package] %s\n' "$*"
}

fail() {
  printf '[package] ERROR: %s\n' "$*" >&2
  exit 1
}

require_command() {
  local command_name="$1"

  if ! command -v "${command_name}" >/dev/null 2>&1; then
    fail "Required command not found: ${command_name}"
  fi
}

require_command git
require_command tar
require_command zip
require_command unzip
require_command awk
require_command find
require_command sort

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  fail "Current directory is not inside a Git work tree."
fi

if [[ "$(git rev-parse --show-toplevel)" != "${REPO_ROOT}" ]]; then
  fail "Packaging script must run from the windchill-ai-devkit repository."
fi

if [[ -n "$(git status --porcelain)" ]]; then
  printf '%s\n' "[package] Working tree is not clean:" >&2
  git status --short >&2
  fail "Commit or discard local changes before creating a release package."
fi

if ! git cat-file -e HEAD:.qoder-plugin/plugin.json 2>/dev/null; then
  fail ".qoder-plugin/plugin.json is not tracked in HEAD."
fi

PLUGIN_NAME="$(
  git show HEAD:.qoder-plugin/plugin.json |
    awk -F'"' '/"name"[[:space:]]*:/ { print $4; exit }'
)"

PLUGIN_VERSION="$(
  git show HEAD:.qoder-plugin/plugin.json |
    awk -F'"' '/"version"[[:space:]]*:/ { print $4; exit }'
)"

if [[ -z "${PLUGIN_NAME}" ]]; then
  fail "Unable to read plugin name from .qoder-plugin/plugin.json."
fi

if [[ -z "${PLUGIN_VERSION}" ]]; then
  fail "Unable to read plugin version from .qoder-plugin/plugin.json."
fi

EXPECTED_GOLDEN_SHA="$(
  git ls-tree HEAD "${GOLDEN_PATH}" |
    awk '$1 == "160000" { print $3 }'
)"

if [[ -z "${EXPECTED_GOLDEN_SHA}" ]]; then
  fail "${GOLDEN_PATH} is not recorded as a Git submodule in HEAD."
fi

if [[ ! -e "${GOLDEN_PATH}/.git" ]]; then
  fail "Golden Reference submodule is not initialized. Run: git submodule update --init --recursive"
fi

ACTUAL_GOLDEN_SHA="$(
  git -C "${GOLDEN_PATH}" rev-parse HEAD
)"

if [[ "${ACTUAL_GOLDEN_SHA}" != "${EXPECTED_GOLDEN_SHA}" ]]; then
  fail "Golden Reference checkout does not match DevKit gitlink. Expected ${EXPECTED_GOLDEN_SHA}, actual ${ACTUAL_GOLDEN_SHA}."
fi

if [[ -n "$(git -C "${GOLDEN_PATH}" status --porcelain)" ]]; then
  printf '%s\n' "[package] Golden Reference working tree is not clean:" >&2
  git -C "${GOLDEN_PATH}" status --short >&2
  fail "Commit or discard Golden Reference changes before packaging."
fi

DEVKIT_SHA="$(git rev-parse HEAD)"

STAGE_DIR="${BUILD_ROOT}/${PLUGIN_NAME}"
ZIP_PATH="${DIST_DIR}/${PLUGIN_NAME}-${PLUGIN_VERSION}.zip"
SHA_PATH="${ZIP_PATH}.sha256"

log "Plugin: ${PLUGIN_NAME}"
log "Version: ${PLUGIN_VERSION}"
log "DevKit commit: ${DEVKIT_SHA}"
log "Golden commit: ${EXPECTED_GOLDEN_SHA}"

rm -rf "${BUILD_ROOT}"
mkdir -p "${STAGE_DIR}"
mkdir -p "${DIST_DIR}"

log "Archiving DevKit runtime files from committed HEAD..."

git archive \
  --format=tar \
  HEAD \
  .qoder-plugin \
  rules \
  skills/qmind-enterprise-router \
  mcp.json \
  templates \
  README.md |
  tar -xf - -C "${STAGE_DIR}"

log "Materializing Golden Reference files from pinned submodule commit..."

mkdir -p "${STAGE_DIR}/${GOLDEN_PATH}"

git -C "${GOLDEN_PATH}" archive \
  --format=tar \
  "${EXPECTED_GOLDEN_SHA}" |
  tar -xf - -C "${STAGE_DIR}/${GOLDEN_PATH}"

# Repository-maintenance files are not needed by the installed Qoder plugin.
rm -f "${STAGE_DIR}/${GOLDEN_PATH}/.gitignore"

REQUIRED_FILES=(
  ".qoder-plugin/plugin.json"
  "mcp.json"
  "skills/qmind-enterprise-router/SKILL.md"
  "skills/windchill-golden-reference/SKILL.md"
  "skills/windchill-golden-reference/CATALOG.md"
)

for required_file in "${REQUIRED_FILES[@]}"; do
  if [[ ! -f "${STAGE_DIR}/${required_file}" ]]; then
    fail "Required plugin file is missing from staging: ${required_file}"
  fi
done

if [[ ! -d "${STAGE_DIR}/rules" ]]; then
  fail "Rules directory is missing from staging."
fi

if [[ ! -d "${STAGE_DIR}/${GOLDEN_PATH}/references" ]]; then
  fail "Golden Reference directory is missing from staging."
fi

REFERENCE_COUNT="$(
  find "${STAGE_DIR}/${GOLDEN_PATH}/references" \
    -type f \
    -name 'reference.md' |
    awk 'END { print NR }'
)"

if [[ "${REFERENCE_COUNT}" -eq 0 ]]; then
  fail "No Golden Reference reference.md files were materialized."
fi

if find "${STAGE_DIR}" \
  \( \
    -name '.git' \
    -o -name '.gitmodules' \
    -o -name '.gitignore' \
    -o -name '.idea' \
    -o -name '.DS_Store' \
  \) \
  -print |
  grep -q .; then
  fail "Repository or IDE metadata was found in plugin staging."
fi

log "Golden Reference entries materialized: ${REFERENCE_COUNT}"

if command -v qoder >/dev/null 2>&1; then
  log "Running Qoder plugin validation with qoder..."
  qoder plugins validate "${STAGE_DIR}"
elif command -v qodercn >/dev/null 2>&1; then
  log "Running Qoder plugin validation with qodercn..."
  qodercn plugins validate "${STAGE_DIR}"
else
  log "WARNING: qoder/qodercn CLI not found; Qoder validation skipped."
fi

rm -f "${ZIP_PATH}" "${SHA_PATH}"

log "Creating plugin ZIP..."

(
  cd "${STAGE_DIR}"

  find . \
    -type f \
    -print |
    sed 's#^\./##' |
    LC_ALL=C sort |
    zip -q -X "${ZIP_PATH}" -@
)

if [[ ! -f "${ZIP_PATH}" ]]; then
  fail "Plugin ZIP was not created."
fi

ZIP_ENTRIES="$(unzip -Z1 "${ZIP_PATH}")"

if ! grep -Fxq '.qoder-plugin/plugin.json' <<<"${ZIP_ENTRIES}"; then
  fail "ZIP root does not contain .qoder-plugin/plugin.json."
fi

if ! grep -Fxq 'skills/windchill-golden-reference/SKILL.md' <<<"${ZIP_ENTRIES}"; then
  fail "ZIP does not contain Golden Reference SKILL.md."
fi

if ! grep -Fxq 'skills/windchill-golden-reference/CATALOG.md' <<<"${ZIP_ENTRIES}"; then
  fail "ZIP does not contain Golden Reference CATALOG.md."
fi

if grep -Eq \
  '(^|/)\.git(/|$)|(^|/)\.gitmodules$|(^|/)\.gitignore$|(^|/)\.idea(/|$)' \
  <<<"${ZIP_ENTRIES}"; then
  fail "ZIP unexpectedly contains repository or IDE metadata."
fi

if command -v shasum >/dev/null 2>&1; then
  (
    cd "${DIST_DIR}"
    shasum -a 256 "$(basename "${ZIP_PATH}")" >"$(basename "${SHA_PATH}")"
  )
elif command -v sha256sum >/dev/null 2>&1; then
  (
    cd "${DIST_DIR}"
    sha256sum "$(basename "${ZIP_PATH}")" >"$(basename "${SHA_PATH}")"
  )
else
  log "WARNING: SHA-256 utility not found; checksum file skipped."
fi

log "Package created:"
log "  ${ZIP_PATH}"

if [[ -f "${SHA_PATH}" ]]; then
  log "Checksum:"
  log "  ${SHA_PATH}"
fi

log "DevKit commit:"
log "  ${DEVKIT_SHA}"

log "Golden commit:"
log "  ${EXPECTED_GOLDEN_SHA}"

log "Packaging completed successfully."