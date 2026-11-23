#!/usr/bin/env bash
# workstation-handoff.sh — Package GSD planning context into a portable
# tar.gz bundle for cross-machine agent work distribution.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"

# Source workstation identity helpers
# shellcheck source=scripts/lib/workstation-lib.sh
if [[ -f "${REPO_ROOT}/scripts/lib/workstation-lib.sh" ]]; then
  source "${REPO_ROOT}/scripts/lib/workstation-lib.sh"
fi

##############################################################################
# Usage
##############################################################################
usage() {
  cat <<'USAGE'
Usage: workstation-handoff.sh [OPTIONS]

Package GSD planning state into a portable handoff bundle.

Options:
  --phase N         Phase number to package
  --wrk WRK-ID      WRK item to package (e.g. WRK-123)
  --output PATH     Custom output path (default: /tmp/handoff-{phase}-{ts}.tar.gz)
  --dry-run         List what would be included without creating the bundle
  -h, --help        Show this help

Examples:
  workstation-handoff.sh --phase 3
  workstation-handoff.sh --wrk WRK-123
  workstation-handoff.sh --phase 3 --output /tmp/my-handoff.tar.gz
  workstation-handoff.sh --phase 3 --dry-run
USAGE
}

##############################################################################
# Argument parsing
##############################################################################
PHASE=""
WRK_ID=""
OUTPUT=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --phase)   PHASE="$2"; shift 2 ;;
    --wrk)     WRK_ID="$2"; shift 2 ;;
    --output)  OUTPUT="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 1 ;;
  esac
done

if [[ -z "${PHASE}" && -z "${WRK_ID}" ]]; then
  echo "Error: --phase or --wrk is required." >&2
  usage
  exit 1
fi

##############################################################################
# Validate .planning/ exists
##############################################################################
PLANNING_DIR="${REPO_ROOT}/.planning"
if [[ ! -d "${PLANNING_DIR}" ]]; then
  echo "Error: ${PLANNING_DIR} does not exist. Nothing to hand off." >&2
  exit 1
fi

##############################################################################
# Resolve identifiers
##############################################################################
TIMESTAMP="$(date -u +%Y%m%dT%H%M%S)"
MACHINE="$(hostname -s)"
GIT_BRANCH="$(git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD)"
GIT_SHA="$(git -C "${REPO_ROOT}" rev-parse HEAD)"

# Build a label used in filenames and branch names
if [[ -n "${PHASE}" ]]; then
  LABEL="phase-${PHASE}"
else
  LABEL="$(echo "${WRK_ID}" | tr '[:upper:]' '[:lower:]')"
fi

RESULT_BRANCH="handoff/${LABEL}-${MACHINE}-${TIMESTAMP}"

if [[ -z "${OUTPUT}" ]]; then
  OUTPUT="/tmp/handoff-${LABEL}-${TIMESTAMP}.tar.gz"
fi

##############################################################################
# Collect files
##############################################################################
declare -a BUNDLE_FILES=()

add_if_exists() {
  local rel="$1"
  if [[ -f "${REPO_ROOT}/${rel}" ]]; then
    BUNDLE_FILES+=("${rel}")
  fi
}

# .planning/ core documents
add_if_exists ".planning/PROJECT.md"
add_if_exists ".planning/ROADMAP.md"
add_if_exists ".planning/REQUIREMENTS.md"
add_if_exists ".planning/STATE.md"

# Phase-specific files
if [[ -n "${PHASE}" ]]; then
  add_if_exists ".planning/phases/${PHASE}/PLAN.md"
  add_if_exists ".planning/phases/${PHASE}/CONTEXT.md"
  add_if_exists ".planning/phases/${PHASE}/RESEARCH.md"
fi

# If WRK ID given, look for a matching file under .planning/
if [[ -n "${WRK_ID}" ]]; then
  while IFS= read -r -d '' f; do
    rel="${f#"${REPO_ROOT}/"}"
    BUNDLE_FILES+=("${rel}")
  done < <(find "${PLANNING_DIR}" -type f -name "*${WRK_ID}*" -print0 2>/dev/null || true)
fi

# Locate PLAN.md for source-file extraction
PLAN_FILE=""
if [[ -n "${PHASE}" && -f "${REPO_ROOT}/.planning/phases/${PHASE}/PLAN.md" ]]; then
  PLAN_FILE="${REPO_ROOT}/.planning/phases/${PHASE}/PLAN.md"
fi

# Best-effort: extract referenced source files from PLAN.md
declare -a SOURCE_FILES=()
if [[ -n "${PLAN_FILE}" ]]; then
  # Grep for paths that look like project files (contain a slash and an extension)
  while IFS= read -r path; do
    # Strip leading ./ if present
    path="${path#./}"
    if [[ -f "${REPO_ROOT}/${path}" ]]; then
      SOURCE_FILES+=("${path}")
    fi
  done < <(grep -oE '[a-zA-Z0-9_./-]+/[a-zA-Z0-9_.-]+\.[a-zA-Z0-9]+' "${PLAN_FILE}" 2>/dev/null | sort -u || true)
fi

##############################################################################
# Dry-run — print manifest and exit
##############################################################################
if [[ "${DRY_RUN}" == true ]]; then
  echo "=== Handoff dry-run ==="
  echo "Phase:         ${PHASE:-n/a}"
  echo "WRK:           ${WRK_ID:-n/a}"
  echo "Machine:       ${MACHINE}"
  echo "Result branch: ${RESULT_BRANCH}"
  echo "Output:        ${OUTPUT}"
  echo ""
  echo "Planning files:"
  for f in "${BUNDLE_FILES[@]}"; do
    echo "  ${f}"
  done
  if [[ ${#SOURCE_FILES[@]} -gt 0 ]]; then
    echo ""
    echo "Source files (referenced in PLAN.md):"
    for f in "${SOURCE_FILES[@]}"; do
      echo "  ${f}"
    done
  fi
  exit 0
fi

##############################################################################
# Build staging directory
##############################################################################
STAGING="$(mktemp -d)"
trap 'rm -rf "${STAGING}"' EXIT

HANDOFF_DIR="${STAGING}/handoff"
mkdir -p "${HANDOFF_DIR}/.planning" "${HANDOFF_DIR}/source-files"

# Copy planning files, preserving directory structure
for f in "${BUNDLE_FILES[@]}"; do
  dest="${HANDOFF_DIR}/${f}"
  mkdir -p "$(dirname "${dest}")"
  cp "${REPO_ROOT}/${f}" "${dest}"
done

# Copy source files
for f in "${SOURCE_FILES[@]}"; do
  dest="${HANDOFF_DIR}/source-files/${f}"
  mkdir -p "$(dirname "${dest}")"
  cp "${REPO_ROOT}/${f}" "${dest}"
done

##############################################################################
# Generate HANDOFF.json
##############################################################################
ALL_FILES=()
for f in "${BUNDLE_FILES[@]}"; do ALL_FILES+=("${f}"); done
for f in "${SOURCE_FILES[@]}"; do ALL_FILES+=("source-files/${f}"); done

# Build JSON array of files
FILES_JSON="["
first=true
for f in "${ALL_FILES[@]}"; do
  if [[ "${first}" == true ]]; then
    first=false
  else
    FILES_JSON+=","
  fi
  FILES_JSON+="\"${f}\""
done
FILES_JSON+="]"

cat > "${HANDOFF_DIR}/HANDOFF.json" <<EOF
{
  "version": 1,
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "source_machine": "${MACHINE}",
  "phase": ${PHASE:-null},
  "wrk_id": ${WRK_ID:+\"${WRK_ID}\"}${WRK_ID:-null},
  "git_branch": "${GIT_BRANCH}",
  "git_sha": "${GIT_SHA}",
  "result_branch": "${RESULT_BRANCH}",
  "files_included": ${FILES_JSON}
}
EOF

##############################################################################
# Generate HANDOFF.md
##############################################################################
{
  echo "# Handoff Context"
  echo ""
  echo "**Project:** $(basename "${REPO_ROOT}")"
  if [[ -n "${PHASE}" ]]; then
    echo "**Phase:** ${PHASE}"
  fi
  if [[ -n "${WRK_ID}" ]]; then
    echo "**Work Item:** ${WRK_ID}"
  fi
  echo "**Source machine:** ${MACHINE}"
  echo "**Git branch:** ${GIT_BRANCH}"
  echo "**Git SHA:** ${GIT_SHA}"
  echo "**Generated:** $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""

  # Instructions
  echo "---"
  echo ""
  if [[ -n "${PHASE}" ]]; then
    echo "You are continuing work on **phase ${PHASE}**. Below is your planning context."
    echo "When you are finished, commit your results to a branch named:"
    echo ""
    echo "    ${RESULT_BRANCH}"
  else
    echo "You are continuing work on **${WRK_ID}**. Below is your planning context."
    echo "When you are finished, commit your results to a branch named:"
    echo ""
    echo "    ${RESULT_BRANCH}"
  fi
  echo ""

  # Inline PLAN.md if available
  if [[ -n "${PLAN_FILE}" && -f "${PLAN_FILE}" ]]; then
    echo "---"
    echo "## PLAN.md (phase ${PHASE})"
    echo ""
    cat "${PLAN_FILE}"
    echo ""
  fi

  # Summarize REQUIREMENTS.md
  REQ="${REPO_ROOT}/.planning/REQUIREMENTS.md"
  if [[ -f "${REQ}" ]]; then
    echo "---"
    echo "## REQUIREMENTS.md (excerpt)"
    echo ""
    head -80 "${REQ}"
    echo ""
    echo "_[truncated — full file included in bundle]_"
    echo ""
  fi

  # Summarize ROADMAP.md
  ROAD="${REPO_ROOT}/.planning/ROADMAP.md"
  if [[ -f "${ROAD}" ]]; then
    echo "---"
    echo "## ROADMAP.md (excerpt)"
    echo ""
    head -80 "${ROAD}"
    echo ""
    echo "_[truncated — full file included in bundle]_"
    echo ""
  fi

  # Recent git log
  echo "---"
  echo "## Recent commits"
  echo ""
  echo '```'
  git -C "${REPO_ROOT}" log --oneline -10
  echo '```'

} > "${HANDOFF_DIR}/HANDOFF.md"

##############################################################################
# Create tar.gz
##############################################################################
tar -czf "${OUTPUT}" -C "${STAGING}" handoff

echo "Handoff bundle created: ${OUTPUT}"
echo "Result branch:          ${RESULT_BRANCH}"
echo "Files included:         ${#ALL_FILES[@]}"
