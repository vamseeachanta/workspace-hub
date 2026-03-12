#!/usr/bin/env bash
# start-wrk.sh: trunk-vs-branch routing for WRK items (WRK-1141)
# Usage: bash scripts/work-queue/start-wrk.sh WRK-NNN
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
QUEUE_DIR="${REPO_ROOT}/.claude/work-queue"

WRK_ID="${1:-}"
if [[ -z "${WRK_ID}" ]]; then
  echo "Usage: $0 WRK-NNN" >&2
  exit 1
fi

# Locate WRK file (working/ first, then pending/)
WRK_FILE=""
for dir in working pending; do
  candidate="${QUEUE_DIR}/${dir}/${WRK_ID}.md"
  if [[ -f "${candidate}" ]]; then
    WRK_FILE="${candidate}"
    break
  fi
done

if [[ -z "${WRK_FILE}" ]]; then
  echo "start-wrk: ${WRK_ID}.md not found in working/ or pending/" >&2
  exit 1
fi

# Parse frontmatter fields using grep (safe for our controlled YAML format)
complexity="$(grep -m1 "^complexity:" "${WRK_FILE}" | sed 's/^complexity:[[:space:]]*//' | tr -d '"' | tr -d "'")"
compound="$(grep -m1 "^compound:" "${WRK_FILE}" | sed 's/^compound:[[:space:]]*//' | tr -d '"' | tr -d "'")"
title="$(grep -m1 "^title:" "${WRK_FILE}" | sed 's/^title:[[:space:]]*//' | tr -d '"' | tr -d "'")"

# Build slug from title: lowercase, first 5 words, hyphenated
slug="$(echo "${title}" | tr '[:upper:]' '[:lower:]' | \
  sed 's/[^a-z0-9 ]/-/g' | \
  tr -s ' -' '-' | \
  sed 's/^-//;s/-$//' | \
  cut -d'-' -f1-5)"

BRANCH="feature/${WRK_ID}-${slug}"

# Routing precedence:
# 1. compound=true → feature branch regardless of complexity
# 2. complexity=simple → main
# 3. complexity=medium|complex → feature branch

if [[ "${compound}" == "true" ]]; then
  echo "start-wrk: compound=true → feature branch"
  _route="branch"
elif [[ "${complexity}" == "simple" ]]; then
  echo "start-wrk: complexity=simple → commit to main directly"
  _route="main"
elif [[ "${complexity}" == "medium" || "${complexity}" == "complex" ]]; then
  echo "start-wrk: complexity=${complexity} → feature branch"
  _route="branch"
else
  echo "start-wrk: unknown complexity '${complexity}' → defaulting to feature branch" >&2
  _route="branch"
fi

if [[ "${_route}" == "branch" ]]; then
  if git show-ref --verify --quiet "refs/heads/${BRANCH}" 2>/dev/null; then
    echo "start-wrk: branch '${BRANCH}' already exists — switch to it manually if needed" >&2
    exit 0
  fi
  # Branch from trunk regardless of current HEAD to avoid contamination
  # Detect trunk: prefer main, fall back to master, then default branch
  if git show-ref --verify --quiet "refs/heads/main" 2>/dev/null; then
    TRUNK="main"
  elif git show-ref --verify --quiet "refs/heads/master" 2>/dev/null; then
    TRUNK="master"
  else
    TRUNK="$(git rev-parse --abbrev-ref HEAD)"
  fi
  git checkout -b "${BRANCH}" "${TRUNK}"
  echo "start-wrk: created and switched to branch '${BRANCH}' (from ${TRUNK})"
fi
