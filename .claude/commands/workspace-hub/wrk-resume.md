---
name: wrk-resume
description: Resume a WRK item from its last checkpoint — reads checkpoint.yaml and loads entry_reads files into context
category: workspace-hub
argument-hint: WRK-NNN
---

# /wrk-resume $ARGUMENTS

Resume a WRK work item from its last checkpoint.

```bash
WRK_ID="$ARGUMENTS"
CHECKPOINT=".claude/work-queue/assets/${WRK_ID}/checkpoint.yaml"

if [ -z "$WRK_ID" ]; then
  echo "Usage: /resume WRK-NNN"
  exit 0
fi

if [ ! -f "$CHECKPOINT" ]; then
  echo "❌ No checkpoint found for ${WRK_ID}."
  echo ""
  echo "Run first:  bash scripts/work-queue/checkpoint.sh ${WRK_ID}"
  exit 0
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Resuming ${WRK_ID}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

uv run --no-project python - "$CHECKPOINT" << 'PYEOF'
import sys, pathlib
try:
    import yaml
except ImportError:
    print("⚠ PyYAML not available — raw output:")
    print(pathlib.Path(sys.argv[1]).read_text())
    sys.exit(0)

data = yaml.safe_load(pathlib.Path(sys.argv[1]).read_text()) or {}

print(f"Title     : {data.get('title','—')}")
print(f"Stage     : {data.get('current_stage','?')} — {data.get('stage_name','?')}")
print(f"Checkpointed: {data.get('checkpointed_at','—')}")
print("")

next_action = str(data.get('next_action', '')).strip()
if next_action:
    print(f"▶ Next action: {next_action}")
else:
    print("⚠ next_action is empty — fill it in checkpoint.yaml before ending sessions.")
print("")

summary = data.get('context_summary') or []
if summary:
    print("Context summary:")
    for item in summary:
        print(f"  • {item}")
    print("")

decisions = data.get('decisions_this_session') or []
if decisions:
    print("Decisions from last session:")
    for d in decisions:
        print(f"  • {d}")
    print("")

artifacts = data.get('artifacts_written') or []
if artifacts:
    print("Artifacts written last session:")
    for a in artifacts:
        print(f"  • {a}")
    print("")

entry_reads = data.get('entry_reads') or []
if entry_reads:
    print("Entry reads (loading into context):")
    for path in entry_reads:
        print(f"  @{path}")
else:
    print("No entry_reads listed in checkpoint.")
PYEOF
```

The files listed under **Entry reads** above are now available — ask Claude to read them or @-mention them directly.
