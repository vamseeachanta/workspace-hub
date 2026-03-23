#!/usr/bin/env bash
# migrate-stage-to-folder.sh — Scaffold a stage folder-skill from bare .md + contract YAML
# Usage: migrate-stage-to-folder.sh <stage_number> [--remove-originals]
# WRK-5111 (child-b of WRK-1321)
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo /mnt/local-analysis/workspace-hub)"
MAPPING_FILE="$REPO_ROOT/.claude/skills/workspace-hub/work-queue-orchestrator/references/stage-mapping.yaml"
STAGES_DIR="$REPO_ROOT/.claude/skills/workspace-hub/stages"
CONTRACTS_DIR="$REPO_ROOT/scripts/work-queue/stages"

STAGE_NUM="${1:?Usage: migrate-stage-to-folder.sh <stage_number> [--remove-originals]}"
REMOVE_ORIGINALS=false
[[ "${2:-}" == "--remove-originals" ]] && REMOVE_ORIGINALS=true

# Zero-pad stage number
NN=$(printf "%02d" "$STAGE_NUM")

# Read stage info from mapping YAML using Python (yq not available)
_yaml_field() {
    python3 -c "
import yaml, sys
with open('$MAPPING_FILE') as f:
    data = yaml.safe_load(f)
for s in data['stages']:
    if s['order'] == $STAGE_NUM:
        print(s.get('$1', ''))
        sys.exit(0)
sys.exit(1)
"
}

SLUG=$(_yaml_field slug)
NAME=$(_yaml_field name)
WEIGHT=$(_yaml_field weight)
INVOCATION=$(_yaml_field invocation)
HUMAN_GATE=$(_yaml_field human_gate)

if [[ -z "$SLUG" || "$SLUG" == "null" ]]; then
    echo "ERROR: Stage $STAGE_NUM not found in stage-mapping.yaml" >&2
    exit 1
fi

# Source files
SRC_MD="$STAGES_DIR/stage-${NN}-${SLUG}.md"
SRC_YAML="$CONTRACTS_DIR/stage-${NN}-${SLUG}.yaml"

# Destination folder
DEST="$STAGES_DIR/stage-${NN}-${SLUG}"

if [[ ! -f "$SRC_MD" ]]; then
    echo "SKIP: $SRC_MD does not exist (already migrated?)" >&2
    exit 0
fi

if [[ ! -f "$SRC_YAML" ]]; then
    echo "ERROR: Contract $SRC_YAML not found" >&2
    exit 1
fi

echo "Migrating stage $NN ($NAME) → $DEST/"

# 1. Create folder
mkdir -p "$DEST"

# 2. Read bare .md content
BODY=$(cat "$SRC_MD")

# 3. Generate SKILL.md with frontmatter + body
cat > "$DEST/SKILL.md" << SKILL_EOF
---
name: stage-${NN}-${SLUG}
description: "Stage ${NN}: ${NAME}"
version: 1.0.0
category: workspace-hub
type: skill
stage_order: ${STAGE_NUM}
invocation: ${INVOCATION}
weight: ${WEIGHT}
human_gate: ${HUMAN_GATE}
---

${BODY}
SKILL_EOF

# 4. Copy contract YAML
cp "$SRC_YAML" "$DEST/contract.yaml"

# 5. Extract hooks from contract → hooks.yaml
python3 -c "
import yaml
with open('$SRC_YAML') as f:
    contract = yaml.safe_load(f)
hooks = {
    'pre_enter_hooks': contract.get('pre_enter_hooks', []) or [],
    'pre_exit_hooks': contract.get('pre_exit_hooks', []) or [],
}
with open('$DEST/hooks.yaml', 'w') as f:
    f.write('# Stage $NN hooks — extracted from contract\n')
    yaml.dump(hooks, f, default_flow_style=False, sort_keys=False)
"

# 6. Write gotchas.md template
cat > "$DEST/gotchas.md" << GOTCHAS_EOF
# Stage ${NN}: ${NAME} — Gotchas

## Operational Lessons

<!-- Populated from gatepass sub-skills and operational experience -->

## Edge Cases

<!-- Stage-specific edge cases -->
GOTCHAS_EOF

# 7. Optionally remove bare .md
if $REMOVE_ORIGINALS; then
    rm "$SRC_MD"
    echo "  Removed: $SRC_MD"
fi

echo "  ✔ Stage $NN migrated: SKILL.md, contract.yaml, gotchas.md, hooks.yaml"
