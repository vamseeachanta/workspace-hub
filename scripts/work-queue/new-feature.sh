#!/usr/bin/env bash
# new-feature.sh WRK-NNN
# Scaffold child WRKs from the ## Decomposition section of a Feature WRK spec.
#
# NOTES FOR SPEC AUTHORS:
#   - No pipe characters (|) allowed inside decomposition table cells — they break row parsing.
#   - The children: field written to the Feature WRK uses inline-list YAML: [WRK-A, WRK-B]
#
# Usage:
#   new-feature.sh WRK-NNN
#
# Env vars:
#   WORK_QUEUE_ROOT  Override queue directory (default: <repo-root>/.claude/work-queue)
#                    Useful for hermetic tests.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

WORK_QUEUE_ROOT="${WORK_QUEUE_ROOT:-${REPO_ROOT}/.claude/work-queue}"

# ── Argument validation ───────────────────────────────────────────────────────
WRK_ID="${1:?Usage: new-feature.sh WRK-NNN}"
if [[ ! "$WRK_ID" =~ ^WRK-[0-9]+$ ]]; then
    echo "ERROR: WRK ID must match WRK-[0-9]+ (got: ${WRK_ID})" >&2
    exit 1
fi

# ── Find feature WRK in any queue dir ────────────────────────────────────────
WRK_FILE=""
for dir in pending working blocked archived archive; do
    candidate="${WORK_QUEUE_ROOT}/${dir}/${WRK_ID}.md"
    if [[ -f "$candidate" ]]; then
        WRK_FILE="$candidate"
        break
    fi
done
# Also scan archive subdirs (archive/YYYY-MM/)
if [[ -z "$WRK_FILE" ]]; then
    WRK_FILE=$(find "${WORK_QUEUE_ROOT}/archive" -name "${WRK_ID}.md" 2>/dev/null | head -1 || true)
fi
if [[ -z "$WRK_FILE" ]]; then
    echo "ERROR: ${WRK_ID}.md not found in any queue directory under ${WORK_QUEUE_ROOT}" >&2
    exit 1
fi

# ── Re-run guard: abort if children: already populated ───────────────────────
_existing_children=$(grep '^children:' "$WRK_FILE" | head -1 || true)
# Match inline list with at least one WRK-NNN entry
if echo "$_existing_children" | grep -qE 'WRK-[0-9]+'; then
    echo "ERROR: ${WRK_ID} children list already populated — run new-feature.sh only on fresh features" >&2
    exit 1
fi
# Also check block-list format (- WRK-NNN on following lines)
if grep -A5 '^children:' "$WRK_FILE" | grep -qE '^\s*-\s+WRK-[0-9]+'; then
    echo "ERROR: ${WRK_ID} children list already populated — run new-feature.sh only on fresh features" >&2
    exit 1
fi

# ── Read spec_ref from frontmatter ────────────────────────────────────────────
SPEC_REF=$(grep '^spec_ref:' "$WRK_FILE" | head -1 | sed 's/spec_ref: *//' | tr -d '"' | xargs)
if [[ -z "$SPEC_REF" ]]; then
    echo "ERROR: spec_ref not set in ${WRK_FILE}" >&2
    exit 1
fi
# Resolve relative to REPO_ROOT if not absolute
if [[ "$SPEC_REF" != /* ]]; then
    SPEC_REF="${REPO_ROOT}/${SPEC_REF}"
fi
if [[ ! -f "$SPEC_REF" ]]; then
    echo "ERROR: spec_ref file not found: ${SPEC_REF}" >&2
    exit 1
fi

# ── Inherit category/subcategory ─────────────────────────────────────────────
PARENT_CAT=$(grep '^category:' "$WRK_FILE" | head -1 | awk '{print $2}' | tr -d '"' | xargs)
PARENT_SUB=$(grep '^subcategory:' "$WRK_FILE" | head -1 | awk '{print $2}' | tr -d '"' | xargs)
PARENT_CAT="${PARENT_CAT:-uncategorised}"
PARENT_SUB="${PARENT_SUB:-uncategorised}"

echo "Feature: ${WRK_ID}  Spec: ${SPEC_REF}"
echo ""

# ── Extract decomposition table rows ─────────────────────────────────────────
# Find the ## Decomposition section and collect pipe-delimited table rows.
# Rows are processed line by line after the section header.
in_decomp=0
declare -a ROW_KEYS=()
declare -a ROW_TITLES=()
declare -a ROW_DEPS=()
declare -a ROW_AGENTS=()
declare -a ROW_WRK_REFS=()

while IFS= read -r line; do
    if [[ "$line" =~ ^##[[:space:]]+Decomposition ]]; then
        in_decomp=1
        continue
    fi
    # Stop at the next ## section
    if [[ $in_decomp -eq 1 && "$line" =~ ^##[[:space:]] ]]; then
        in_decomp=0
        continue
    fi
    if [[ $in_decomp -eq 1 ]]; then
        # Process pipe-delimited table rows only
        [[ "$line" =~ ^\| ]] || continue
        # Strip leading/trailing pipe and split by |
        # Expected columns: Child key | Title | Scope | Depends on | Agent | wrk_ref
        IFS='|' read -ra cols <<< "${line}"
        # cols[0] is empty (before first |); real data starts at cols[1]
        [[ ${#cols[@]} -lt 6 ]] && continue
        key="${cols[1]}"
        title="${cols[2]}"
        # scope="${cols[3]}"  # not used currently
        deps="${cols[4]}"
        agent="${cols[5]}"
        wrk_ref="${cols[6]:-}"

        # Trim whitespace
        key="${key#"${key%%[![:space:]]*}"}"; key="${key%"${key##*[![:space:]]}"}"
        title="${title#"${title%%[![:space:]]*}"}"; title="${title%"${title##*[![:space:]]}"}"
        deps="${deps#"${deps%%[![:space:]]*}"}"; deps="${deps%"${deps##*[![:space:]]}"}"
        agent="${agent#"${agent%%[![:space:]]*}"}"; agent="${agent%"${agent##*[![:space:]]}"}"
        wrk_ref="${wrk_ref#"${wrk_ref%%[![:space:]]*}"}"; wrk_ref="${wrk_ref%"${wrk_ref##*[![:space:]]}"}"

        # Skip header row and separator rows
        [[ "$key" == "Child key" ]] && continue
        [[ "$key" =~ ^-+$ ]] && continue
        [[ -z "$key" ]] && continue

        ROW_KEYS+=("$key")
        ROW_TITLES+=("$title")
        ROW_DEPS+=("$deps")
        ROW_AGENTS+=("$agent")
        ROW_WRK_REFS+=("$wrk_ref")
    fi
done < "$SPEC_REF"

if [[ ${#ROW_KEYS[@]} -eq 0 ]]; then
    echo "ERROR: No children parsed from ## Decomposition table in ${SPEC_REF}" >&2
    echo "  Check that the spec has a '## Decomposition' section with a valid pipe table." >&2
    exit 1
fi

# ── PASS 1: Allocate/adopt IDs; build child-key → WRK-ID map ─────────────────
declare -A KEY_TO_ID=()
declare -A KEY_ADOPT_FAIL=()   # tracks keys where adoption target not found

for i in "${!ROW_KEYS[@]}"; do
    key="${ROW_KEYS[$i]}"
    wrk_ref="${ROW_WRK_REFS[$i]}"

    if [[ -n "$wrk_ref" && "$wrk_ref" =~ ^WRK-[0-9]+$ ]]; then
        # ADOPT existing WRK
        existing_file=""
        for dir in pending working blocked archived archive; do
            candidate="${WORK_QUEUE_ROOT}/${dir}/${wrk_ref}.md"
            if [[ -f "$candidate" ]]; then
                existing_file="$candidate"
                break
            fi
        done
        # Also search archive subdirs
        if [[ -z "$existing_file" ]]; then
            existing_file=$(find "${WORK_QUEUE_ROOT}" -name "${wrk_ref}.md" 2>/dev/null | head -1 || true)
        fi

        if [[ -z "$existing_file" ]]; then
            echo "WARNING: wrk_ref ${wrk_ref} not found — skipping adoption of child '${key}'" >&2
            KEY_ADOPT_FAIL["$key"]=1
            continue
        fi

        # Check existing parent: field
        existing_parent=$(grep '^parent:' "$existing_file" | head -1 | awk '{print $2}' | xargs || true)
        if [[ -n "$existing_parent" && "$existing_parent" != "$WRK_ID" ]]; then
            echo "ERROR: Cannot adopt ${wrk_ref} — it already has parent: ${existing_parent}" \
                 "(expected ${WRK_ID} or none)" >&2
            echo "  Integrity violation: a WRK cannot have two feature parents." >&2
            exit 1
        fi

        KEY_TO_ID["$key"]="$wrk_ref"
    else
        # Allocate new ID via next-id.sh
        # next-id.sh uses WORKSPACE_ROOT env var; point it at TMPDIR when testing
        new_id=$(WORKSPACE_ROOT="${WORK_QUEUE_ROOT%/.claude/work-queue}" \
            bash "${REPO_ROOT}/scripts/work-queue/next-id.sh" 2>/dev/null)
        # next-id.sh writes a sentinel file at WORK_QUEUE_ROOT/pending/WRK-NNNN.md
        # Ensure that sentinel ends up in the correct WORK_QUEUE_ROOT pending dir
        SENTINEL_REAL="${REPO_ROOT}/.claude/work-queue/pending/WRK-${new_id}.md"
        SENTINEL_TARGET="${WORK_QUEUE_ROOT}/pending/WRK-${new_id}.md"
        if [[ -f "$SENTINEL_REAL" && "$SENTINEL_REAL" != "$SENTINEL_TARGET" ]]; then
            mv "$SENTINEL_REAL" "$SENTINEL_TARGET" 2>/dev/null || true
        fi
        KEY_TO_ID["$key"]="WRK-${new_id}"
    fi
done

# ── PASS 1b: Pre-validate all Depends on values before writing any files ──────
for i in "${!ROW_KEYS[@]}"; do
    key="${ROW_KEYS[$i]}"
    deps="${ROW_DEPS[$i]}"

    # Skip no-dep rows
    if [[ "$deps" == "—" || "$deps" == "-" || "$deps" == "" ]]; then
        continue
    fi

    # Concrete WRK-NNN reference → validate it exists somewhere
    if [[ "$deps" =~ ^WRK-[0-9]+$ ]]; then
        dep_file=$(find "${WORK_QUEUE_ROOT}" -name "${deps}.md" 2>/dev/null | head -1 || true)
        if [[ -z "$dep_file" ]]; then
            echo "ERROR: Depends on '${deps}' in child '${key}' not found in queue" >&2
            exit 1
        fi
        continue
    fi

    # Symbolic key → must be in our Pass-1 map
    if [[ -z "${KEY_TO_ID[$deps]+isset}" ]]; then
        if [[ -n "${KEY_ADOPT_FAIL[$deps]+isset}" ]]; then
            echo "ERROR: Depends on '${deps}' in child '${key}' refers to a key whose" \
                 "adoption failed — cannot resolve blocked_by." >&2
        else
            echo "ERROR: Depends on '${deps}' in child '${key}' is an unknown child key." \
                 "Valid keys: ${!KEY_TO_ID[*]}" >&2
        fi
        exit 1
    fi
done

# ── PASS 2: Write child files ─────────────────────────────────────────────────
declare -a CHILDREN_IDS=()

for i in "${!ROW_KEYS[@]}"; do
    key="${ROW_KEYS[$i]}"
    title="${ROW_TITLES[$i]}"
    deps="${ROW_DEPS[$i]}"
    agent="${ROW_AGENTS[$i]}"
    wrk_ref="${ROW_WRK_REFS[$i]}"

    # Skip if adoption failed for this key (key absent from map)
    [[ -n "${KEY_ADOPT_FAIL[$key]+isset}" ]] && continue
    [[ -z "${KEY_TO_ID[$key]+isset}" ]] && continue

    child_id="${KEY_TO_ID[$key]}"
    CHILDREN_IDS+=("$child_id")

    # Resolve blocked_by
    blocked_by="[]"
    if [[ "$deps" != "—" && "$deps" != "-" && -n "$deps" ]]; then
        if [[ "$deps" =~ ^WRK-[0-9]+$ ]]; then
            # Concrete reference
            blocked_by="[${deps}]"
        else
            # Symbolic key → resolve
            resolved="${KEY_TO_ID[$deps]}"
            blocked_by="[${resolved}]"
        fi
    fi

    if [[ -n "$wrk_ref" && "$wrk_ref" =~ ^WRK-[0-9]+$ ]]; then
        # ADOPT: update existing WRK frontmatter
        existing_file=""
        for dir in pending working blocked archived archive; do
            candidate="${WORK_QUEUE_ROOT}/${dir}/${wrk_ref}.md"
            if [[ -f "$candidate" ]]; then
                existing_file="$candidate"
                break
            fi
        done
        if [[ -z "$existing_file" ]]; then
            existing_file=$(find "${WORK_QUEUE_ROOT}" -name "${wrk_ref}.md" 2>/dev/null | head -1 || true)
        fi

        existing_parent=$(grep '^parent:' "$existing_file" | head -1 | awk '{print $2}' | xargs || true)
        if [[ -z "$existing_parent" ]]; then
            # Insert parent: after the id: line
            sed -i "s/^id: ${wrk_ref}\$/id: ${wrk_ref}\nparent: ${WRK_ID}/" "$existing_file"
        fi
        # Update blocked_by if the decomposition specifies one
        if [[ "$blocked_by" != "[]" ]]; then
            if grep -q '^blocked_by:' "$existing_file"; then
                sed -i "s/^blocked_by: .*/blocked_by: ${blocked_by}/" "$existing_file"
            else
                sed -i "s/^parent: ${WRK_ID}/parent: ${WRK_ID}\nblocked_by: ${blocked_by}/" "$existing_file"
            fi
        fi
        echo "Adopted  ${child_id}: ${title} (blocked_by: ${blocked_by})"
    else
        # CREATE new child WRK file (sentinel already created by next-id.sh)
        numeric_id="${child_id#WRK-}"
        child_file="${WORK_QUEUE_ROOT}/pending/WRK-${numeric_id}.md"
        cat > "$child_file" <<EOF
---
id: ${child_id}
title: "${title}"
status: pending
priority: high
complexity: medium
created_at: "$(date +%Y-%m-%d)"
parent: ${WRK_ID}
blocked_by: ${blocked_by}
target_repos: [workspace-hub]
computer: ace-linux-1
orchestrator: ${agent:-claude}
plan_workstations: [ace-linux-1]
execution_workstations: [ace-linux-1]
category: ${PARENT_CAT}
subcategory: ${PARENT_SUB}
---

## Mission

<!-- Scope from decomposition row: ${key} -->

## What / Why

<!-- Fill from feature spec section: ### Child: ${key} -->

## Acceptance Criteria

<!-- Copy ACs from feature spec: ### Child: ${key} -->
EOF
        echo "Created  ${child_id}: ${title} (blocked_by: ${blocked_by})"
    fi
done

# ── Update Feature WRK children: list ────────────────────────────────────────
if [[ ${#CHILDREN_IDS[@]} -eq 0 ]]; then
    echo "ERROR: No children were created or adopted (all adoptions may have failed)" >&2
    exit 1
fi

CHILDREN_YAML="[$(IFS=', '; echo "${CHILDREN_IDS[*]}")]"

# Replace existing children: line (handles both [] and existing lists)
if grep -q '^children:' "$WRK_FILE"; then
    # Inline list on same line
    if grep -q "^children: \[" "$WRK_FILE"; then
        sed -i "s/^children: \[.*\]/children: ${CHILDREN_YAML}/" "$WRK_FILE"
    else
        # Block-list format — replace multi-line; use Python for safety
        python3 - "$WRK_FILE" "$CHILDREN_YAML" <<'PYEOF' 2>/dev/null || \
            sed -i "/^children:/{ N; s/children:.*//; }" "$WRK_FILE"
import sys, re
path, yaml_val = sys.argv[1], sys.argv[2]
with open(path) as f:
    content = f.read()
# Replace block-list children: section with inline
content = re.sub(r'^children:\s*\n(\s+-[^\n]*\n)+', f'children: {yaml_val}\n',
                 content, flags=re.MULTILINE)
with open(path, 'w') as f:
    f.write(content)
PYEOF
    fi
else
    echo "children: ${CHILDREN_YAML}" >> "$WRK_FILE"
fi

echo ""
echo "Feature ${WRK_ID} — children updated: ${CHILDREN_YAML}"
