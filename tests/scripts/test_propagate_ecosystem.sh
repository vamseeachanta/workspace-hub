#!/usr/bin/env bash
# ABOUTME: Regression tests for scripts/propagate-ecosystem.sh shared-skill propagation

set -uo pipefail

PASS=0; FAIL=0
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SCRIPT_SRC="$ROOT/scripts/propagate-ecosystem.sh"

pass() { echo "PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "FAIL: $1"; echo "  $2"; FAIL=$((FAIL + 1)); }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Build isolated fixture workspace whose root mirrors workspace-hub layout.
mkdir -p "$TMP/scripts" "$TMP/.claude/skills/_internal/meta" "$TMP/.claude/skills/_internal/workflows"
cp "$SCRIPT_SRC" "$TMP/scripts/propagate-ecosystem.sh"
printf 'meta-skill\n' > "$TMP/.claude/skills/_internal/meta/SKILL.md"
printf 'workflow-skill\n' > "$TMP/.claude/skills/_internal/workflows/SKILL.md"

# Repo discovered by script: must have .claude/skills directory.
mkdir -p "$TMP/repo-a/.claude/skills"
# Historical placeholder-file representation seen in ecosystem.
printf '../../../.claude/skills/_internal/meta\n' > "$TMP/repo-a/.claude/skills/meta"
printf '../../../.claude/skills/_internal/workflows\n' > "$TMP/repo-a/.claude/skills/workflows"

# T1: dry-run should classify placeholder files as existing link placeholders, not "new".
out1="$(bash "$TMP/scripts/propagate-ecosystem.sh" --skills-only --dry-run --verbose 2>&1)"
if [[ "$out1" == *"repo-a/meta -> _internal/meta (would replace placeholder file)"* ]] && \
   [[ "$out1" == *"repo-a/workflows -> _internal/workflows (would replace placeholder file)"* ]]; then
  pass "dry-run detects placeholder files"
else
  fail "dry-run detects placeholder files" "$out1"
fi

# T2: real run should replace placeholder regular files with symlinks.
out2="$(bash "$TMP/scripts/propagate-ecosystem.sh" --skills-only --verbose 2>&1)"
if [[ -L "$TMP/repo-a/.claude/skills/meta" ]] && [[ -L "$TMP/repo-a/.claude/skills/workflows" ]]; then
  pass "real run converts placeholder files to symlinks"
else
  fail "real run converts placeholder files to symlinks" "$out2"
fi

# T3: symlinks should point at workspace shared skills.
meta_target="$(readlink "$TMP/repo-a/.claude/skills/meta" 2>/dev/null || true)"
wf_target="$(readlink "$TMP/repo-a/.claude/skills/workflows" 2>/dev/null || true)"
if [[ "$meta_target" == ../../../.claude/skills/_internal/meta ]] && \
   [[ "$wf_target" == ../../../.claude/skills/_internal/workflows ]]; then
  pass "symlink targets are relative shared-skill paths"
else
  fail "symlink targets are relative shared-skill paths" "meta=$meta_target workflows=$wf_target"
fi

echo ""
echo "Results: PASS=$PASS FAIL=$FAIL"
[[ "$FAIL" -eq 0 ]]
