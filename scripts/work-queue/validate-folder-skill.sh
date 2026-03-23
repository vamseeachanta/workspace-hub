#!/usr/bin/env bash
# validate-folder-skill.sh — Verify a stage folder-skill has required structure and valid content
# Usage: validate-folder-skill.sh <folder_path>
# WRK-5111 (child-b of WRK-1321)
set -euo pipefail

FOLDER="${1:?Usage: validate-folder-skill.sh <folder_path>}"
ERRORS=0

check() {
    local file="$1" desc="$2"
    if [[ ! -f "$file" ]]; then
        echo "  ✖ MISSING: $desc ($file)" >&2
        ((ERRORS++))
        return 1
    fi
    return 0
}

echo "Validating: $FOLDER"

# 1. SKILL.md exists and has frontmatter
if check "$FOLDER/SKILL.md" "SKILL.md"; then
    # Check frontmatter delimiters
    if ! head -1 "$FOLDER/SKILL.md" | grep -q "^---$"; then
        echo "  ✖ SKILL.md: missing frontmatter (no --- delimiter)" >&2
        ((ERRORS++))
    fi
    # Check required frontmatter fields
    for field in name description version category type stage_order; do
        if ! grep -q "^${field}:" "$FOLDER/SKILL.md"; then
            echo "  ✖ SKILL.md: missing frontmatter field '$field'" >&2
            ((ERRORS++))
        fi
    done
    # Check body is non-empty (content after second ---)
    BODY_LINES=$(awk '/^---$/{n++; next} n>=2' "$FOLDER/SKILL.md" | grep -c '[^ ]' || true)
    if [[ "$BODY_LINES" -lt 1 ]]; then
        echo "  ✖ SKILL.md: body is empty (no content after frontmatter)" >&2
        ((ERRORS++))
    fi
fi

# 2. contract.yaml exists and is valid YAML
if check "$FOLDER/contract.yaml" "contract.yaml"; then
    if ! python3 -c "import yaml; yaml.safe_load(open('$FOLDER/contract.yaml'))" 2>/dev/null; then
        echo "  ✖ contract.yaml: invalid YAML" >&2
        ((ERRORS++))
    fi
    # Check required contract fields
    for field in order name weight; do
        if ! grep -q "^${field}:" "$FOLDER/contract.yaml"; then
            echo "  ✖ contract.yaml: missing field '$field'" >&2
            ((ERRORS++))
        fi
    done
fi

# 3. gotchas.md exists
check "$FOLDER/gotchas.md" "gotchas.md"

# 4. hooks.yaml exists and is valid YAML
if check "$FOLDER/hooks.yaml" "hooks.yaml"; then
    if ! python3 -c "import yaml; yaml.safe_load(open('$FOLDER/hooks.yaml'))" 2>/dev/null; then
        echo "  ✖ hooks.yaml: invalid YAML" >&2
        ((ERRORS++))
    fi
fi

if [[ $ERRORS -eq 0 ]]; then
    echo "  ✔ PASS"
    exit 0
else
    echo "  ✖ FAIL ($ERRORS error(s))" >&2
    exit 1
fi
