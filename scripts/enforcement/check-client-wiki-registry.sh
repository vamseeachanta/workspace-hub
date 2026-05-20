#!/usr/bin/env bash
# Validates config/client-wikis.yml against on-disk + GitHub reality.
# Exit non-zero on any failure. Machine-aware: skip mount checks when not present.
#
# Implements §Pseudocode of docs/plans/2026-05-20-issue-2746-llm-wiki-acma.md
# with three carry-forward fixes from T2/T3 adversarial reviews:
#   Fix 1 — Firewall-grep errexit hazard: use `if grep -qE ... then ... fi`
#           instead of `grep -E ... && { ...; FAILED=1; }` which crashes under
#           `set -e` on the happy (no-match) path.
#   Fix 2 — `local_working_clone` null-guard: yq returns literal "null" when the
#           field is absent; `dirname null` → `.` → `[[ -d . ]]` is TRUE and the
#           clone branch fires spuriously. Guard against null/empty first.
#   Fix 3 — `posture` null-guard: posture is required by the firewall invariant;
#           skipping it silently when missing defeats privacy enforcement. Emit
#           an explicit FAIL and continue to next entry.

set -euo pipefail

# Anchor REPO_ROOT to the script's own location (not the caller's cwd) so the
# env-override path works even when invoked from outside the repo (e.g., /tmp).
SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SELF_DIR" rev-parse --show-toplevel 2>/dev/null || echo "$SELF_DIR")"
# Registry path is overridable for tests; defaults to canonical location.
REGISTRY="${REGISTRY_PATH:-${REPO_ROOT}/config/client-wikis.yml}"

# Precheck dependencies before doing any work.
command -v yq >/dev/null || { echo >&2 "FAIL: yq v4+ required (https://github.com/mikefarah/yq)"; exit 1; }
command -v gh >/dev/null || { echo >&2 "FAIL: gh CLI required"; exit 1; }

# 1. Registry file exists
[[ -f "$REGISTRY" ]] || { echo >&2 "FAIL: registry missing at $REGISTRY"; exit 1; }

# 2. Schema validation: `wikis` must be a list and parse cleanly.
WIKIS_TYPE=$(yq '.wikis | tag' "$REGISTRY" 2>/dev/null || echo "")
if [[ "$WIKIS_TYPE" != "!!seq" ]]; then
  echo >&2 "FAIL: registry $REGISTRY missing or malformed top-level 'wikis' list (got tag=$WIKIS_TYPE)"
  exit 1
fi

FAILED=0

# Collect short_names for later uniqueness check.
SHORT_NAMES=$(yq '.wikis[].short_name' "$REGISTRY")

# ----- Pass A: required-field validation per entry -----
# Determine which entries have all required fields; only those advance to Pass B.
INDICES=$(yq '.wikis | keys | .[]' "$REGISTRY")

declare -a VALID_INDICES=()
for i in $INDICES; do
  SHORT=$(yq ".wikis[$i].short_name" "$REGISTRY")
  REPO=$(yq ".wikis[$i].repo" "$REGISTRY")
  VIS=$(yq ".wikis[$i].visibility" "$REGISTRY")
  RAW_ROOTS_TAG=$(yq ".wikis[$i].raw_roots | tag" "$REGISTRY" 2>/dev/null || echo "")
  POSTURE=$(yq ".wikis[$i].posture" "$REGISTRY")
  STATUS=$(yq ".wikis[$i].status" "$REGISTRY")

  ENTRY_LABEL="$SHORT"
  [[ -z "$ENTRY_LABEL" || "$ENTRY_LABEL" == "null" ]] && ENTRY_LABEL="index=$i"

  ENTRY_OK=1

  if [[ -z "$SHORT" || "$SHORT" == "null" ]]; then
    echo >&2 "FAIL: entry index=$i missing required 'short_name' field"
    FAILED=1
    ENTRY_OK=0
  fi
  if [[ -z "$REPO" || "$REPO" == "null" ]]; then
    echo >&2 "FAIL: $ENTRY_LABEL missing required 'repo' field"
    FAILED=1
    ENTRY_OK=0
  fi
  if [[ -z "$VIS" || "$VIS" == "null" ]]; then
    echo >&2 "FAIL: $ENTRY_LABEL missing required 'visibility' field"
    FAILED=1
    ENTRY_OK=0
  fi
  if [[ "$RAW_ROOTS_TAG" != "!!seq" ]]; then
    echo >&2 "FAIL: $ENTRY_LABEL missing required 'raw_roots' list (got tag=$RAW_ROOTS_TAG)"
    FAILED=1
    ENTRY_OK=0
  fi
  # Fix 3: posture null-guard (required for firewall enforcement).
  if [[ -z "$POSTURE" || "$POSTURE" == "null" ]]; then
    echo >&2 "FAIL: $ENTRY_LABEL missing required 'posture' field"
    FAILED=1
    ENTRY_OK=0
  fi
  if [[ -z "$STATUS" || "$STATUS" == "null" ]]; then
    echo >&2 "FAIL: $ENTRY_LABEL missing required 'status' field"
    FAILED=1
    ENTRY_OK=0
  fi

  if [[ $ENTRY_OK -eq 1 ]]; then
    VALID_INDICES+=("$i")
  fi
done

# ----- Cross-entry: uniqueness of short_name -----
DUPES=$(echo "$SHORT_NAMES" | grep -v '^null$' | sort | uniq -d)
if [[ -n "$DUPES" ]]; then
  echo >&2 "FAIL: duplicate short_name: $DUPES"
  FAILED=1
fi

# ----- Pass B: live-state checks per fully-formed entry -----
for i in "${VALID_INDICES[@]}"; do
  SHORT=$(yq ".wikis[$i].short_name" "$REGISTRY")
  REPO=$(yq ".wikis[$i].repo" "$REGISTRY")
  POSTURE=$(yq ".wikis[$i].posture" "$REGISTRY")
  STATUS=$(yq ".wikis[$i].status" "$REGISTRY")

  # Only check repo existence + archived for bootstrapped/live (not planned/retired).
  if [[ "$STATUS" =~ ^(bootstrapped|live)$ ]]; then
    REPO_JSON=$(gh repo view "$REPO" --json visibility,isArchived 2>/dev/null || echo "")
    if [[ -z "$REPO_JSON" ]]; then
      echo >&2 "FAIL: $SHORT repo $REPO not found on GH"
      FAILED=1
    else
      VIS=$(echo "$REPO_JSON" | yq -r '.visibility')
      ARCHIVED=$(echo "$REPO_JSON" | yq -r '.isArchived')
      if [[ "$POSTURE" == "client-private" && "$VIS" != "PRIVATE" ]]; then
        echo >&2 "FAIL: $SHORT posture=client-private but visibility=$VIS"
        FAILED=1
      fi
      # Governance spec §4.3: isArchived=false required for non-retired entries.
      if [[ "$ARCHIVED" == "true" && "$STATUS" != "retired" ]]; then
        echo >&2 "FAIL: $SHORT status=$STATUS but GH repo isArchived=true"
        FAILED=1
      fi
    fi
  fi

  # Fix 2: local_working_clone null-guard (field may be absent for planned rows).
  CLONE=$(yq ".wikis[$i].local_working_clone" "$REGISTRY")
  if [[ -n "$CLONE" && "$CLONE" != "null" ]] && [[ -d "$(dirname "$CLONE")" ]]; then
    if [[ ! -d "$CLONE/.git" ]]; then
      echo >&2 "FAIL: $SHORT clone $CLONE missing or not a git repo"
      FAILED=1
    else
      # Governance spec §4.3: clone's remote must match `repo`.
      CLONE_REMOTE=$(git -C "$CLONE" config --get remote.origin.url 2>/dev/null || echo "")
      EXPECTED=("https://github.com/$REPO" "https://github.com/$REPO.git" "git@github.com:$REPO.git")
      MATCH=0
      for u in "${EXPECTED[@]}"; do
        if [[ "$CLONE_REMOTE" == "$u" ]]; then MATCH=1; break; fi
      done
      if [[ $MATCH -ne 1 ]]; then
        echo >&2 "FAIL: $SHORT clone $CLONE remote=$CLONE_REMOTE doesn't match expected $REPO"
        FAILED=1
      fi
    fi
  fi

  # Fix 1: Firewall guard via `if grep -qE ... then`. Client-private raw_roots
  # must not match a public llm-wiki path. The bare `grep && ...` form crashes
  # under `set -e` on the happy (no-match) path because grep returns non-zero.
  if [[ "$POSTURE" == "client-private" ]]; then
    RAW_ROOTS=$(yq ".wikis[$i].raw_roots[]" "$REGISTRY")
    if echo "$RAW_ROOTS" | grep -qE '/llm-wiki/?$|/llm-wiki/[^/]'; then
      echo >&2 "FAIL: $SHORT client-private raw_roots overlaps public llm-wiki path (firewall violation)"
      FAILED=1
    fi
  fi
done

exit $FAILED
