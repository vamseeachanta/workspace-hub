---
name: ecosystem-health-step-1-group-1-checks-bash-fast
description: 'Sub-skill of ecosystem-health: Step 1: Group 1 checks (bash, fast) (+3).'
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Step 1: Group 1 checks (bash, fast) (+3)

## Step 1: Group 1 checks (bash, fast)

```bash
REPO="$(git rev-parse --show-toplevel)"
echo "=== Group 1: Cross-Platform Guard ==="

# Check 1
val=$(git config core.hooksPath 2>/dev/null || echo "NOT SET")
[[ "$val" == ".claude/hooks" ]] && echo "  [PASS] Hook wired: $val" || echo "  [FAIL] core.hooksPath=$val (expected .claude/hooks)"

# Check 2-3
for h in pre-commit post-merge; do
    f="$REPO/.claude/hooks/$h"
    [[ -x "$f" ]] && echo "  [PASS] $h: executable" || echo "  [FAIL] $h: missing or not executable"
done

# Check 4
command -v uv >/dev/null 2>&1 && echo "  [PASS] uv: $(uv --version)" || echo "  [FAIL] uv: not found"

# Check 5
count=$(grep -c working-tree-encoding "$REPO/.gitattributes" 2>/dev/null || echo 0)
[[ "$count" -ge 4 ]] && echo "  [PASS] .gitattributes: $count encoding rules" || echo "  [WARN] .gitattributes: only $count encoding rules (expected >= 4)"

# Check 6
"$REPO/.claude/hooks/check-encoding.sh" && echo "  [PASS] Encoding: clean" || echo "  [FAIL] Encoding: bad files detected (see above)"
```


## Step 2: Group 2 checks

```bash
echo "=== Group 2: Work Queue Integrity ==="
uv run --no-project python "$REPO/.claude/work-queue/scripts/generate-index.py" >/dev/null 2>&1 \
    && echo "  [PASS] Index generates" \
    || echo "  [FAIL] Index generation failed"

# Gate violations in working/
grep -rL "plan_approved: true" "$REPO/.claude/work-queue/working/" 2>/dev/null \
    | sed 's/.*\///' | while read f; do echo "  [WARN] Missing plan_approved: $f"; done
```


## Step 3: Skill frontmatter (quick scan)

```bash
echo "=== Group 3: Skill Frontmatter ==="
missing=0
while IFS= read -r skill; do
    grep -q "^name:" "$skill" && grep -q "^version:" "$skill" && grep -q "^tags:" "$skill" \
        || { echo "  [WARN] Missing frontmatter fields: $skill"; ((missing++)); }
done < <(find "$REPO/.claude/skills" -name "SKILL.md" -not -path "*/_archive/*")
[[ $missing -eq 0 ]] && echo "  [PASS] All skills have required frontmatter"
```


## Step 4: Signal backlog

```bash
echo "=== Group 4: Signal Backlog ==="
count=$(ls "$REPO/.claude/state/pending-reviews/"*.jsonl 2>/dev/null | wc -l)
[[ $count -lt 50 ]] && echo "  [PASS] $count pending signal files" || echo "  [WARN] $count pending signal files (> 50)"
```
