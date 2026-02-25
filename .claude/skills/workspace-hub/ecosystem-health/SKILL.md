---
name: ecosystem-health
description: "Parallel health check agent for workspace-hub — verifies encoding guard, hook wiring, uv availability, skill frontmatter, and work queue integrity at session end or after repo-sync"
version: 1.0.0
category: workspace-hub
author: workspace-hub
type: skill
last_updated: 2026-02-19
wrk_ref: WRK-211
trigger: session-exit, post-repo-sync
auto_execute: false
related_skills:
  - repo-sync
  - improve
  - interoperability
  - claude-reflect
tags:
  - ecosystem
  - health-checks
  - agent-teams
  - automation
  - parallel-agent
platforms: [all]
capabilities: []
requires: []
see_also: []
---

# /ecosystem-health — Parallel Health Check Agent

Runs a structured suite of health checks against workspace-hub after a pull or
at session exit. Designed to be spawned as a **parallel agent** — it does not
block the main orchestrator.

## Usage

```
/ecosystem-health           — full suite, report only
/ecosystem-health --fix     — fix auto-fixable issues (encoding conversions)
/ecosystem-health --signal  — emit JSON signal for /improve consumption
```

Or spawned by the orchestrator:
```python
Task(
    subagent_type="Bash",
    description="Run ecosystem health checks",
    prompt="Run .claude/hooks/check-encoding.sh and the checks in the ecosystem-health skill. Report results.",
    run_in_background=True
)
```

## When to Run

| Trigger | Who spawns it |
|---------|---------------|
| End of `/repo-sync` (Phase 5) | repo-sync skill |
| Session exit | `ecosystem-health-check.sh` stop hook |
| Manual | User runs `/ecosystem-health` |
| After bulk file operations | Orchestrator spawns as parallel agent |

## Health Check Suite

### Group 1: Cross-Platform Guard

| # | Check | Command | Pass |
|---|-------|---------|------|
| 1 | Hook wired | `git config core.hooksPath` | `.claude/hooks` |
| 2 | pre-commit executable | `test -x .claude/hooks/pre-commit` | exit 0 |
| 3 | post-merge executable | `test -x .claude/hooks/post-merge` | exit 0 |
| 4 | uv available | `command -v uv` | found |
| 5 | .gitattributes rules | `grep -c working-tree-encoding .gitattributes` | >= 4 |
| 6 | Encoding clean | `.claude/hooks/check-encoding.sh` | exit 0 |

**Auto-fix**: If check 1-3 fail, run `bash scripts/operations/setup-hooks.sh`.
If check 6 fails, convert flagged files with iconv or uv Python.

### Group 2: Work Queue Integrity

| # | Check | Command | Pass |
|---|-------|---------|------|
| 7 | Index generates | `uv run --no-project python scripts/work-queue/generate-index.py` | exit 0 |
| 8 | No orphan WRK items | All `working/` items have `plan_approved: true` | 0 violations |
| 9 | No gate violations | `working/` items have `plan_reviewed: true` (Route B/C only) | 0 violations |

### Group 3: Skill Frontmatter Quality

| # | Check | Pass |
|---|-------|------|
| 10 | All SKILL.md have `name:`, `version:`, `tags:` | 0 missing |
| 11 | No SKILL.md > 400 lines | 0 violations |
| 12 | Bidirectional links | For any A→B in `related_skills`, B→A also present | 0 asymmetric |

### Group 4: Signal Backlog

| # | Check | Pass |
|---|-------|------|
| 13 | Pending signals | `.claude/state/pending-reviews/` file count | < 50 |
| 14 | Improve changelog recent | `improve-changelog.yaml` updated within 7 days | pass |

## Output Format

```
=== Ecosystem Health Check — 2026-02-19 ===

Group 1: Cross-Platform Guard
  [PASS] Hook wired: .claude/hooks
  [PASS] pre-commit: executable
  [FAIL] uv: not found in PATH
         Fix: curl -LsSf https://astral.sh/uv/install.sh | sh

Group 2: Work Queue Integrity
  [PASS] Index generates: exit 0
  [WARN] 2 working/ items missing plan_reviewed: WRK-205, WRK-199

Group 3: Skill Frontmatter
  [PASS] All skills have required frontmatter
  [WARN] 3 asymmetric related_skills links (see WRK-207)

Group 4: Signal Backlog
  [PASS] 12 pending signals (< 50)

Summary: 1 FAIL, 2 WARN, 11 PASS
```

## JSON Signal (for /improve)

When `--signal` flag is used, emit to `.claude/state/pending-reviews/ecosystem-review.jsonl`:

```json
{
  "timestamp": "2026-02-19T12:00:00Z",
  "source": "ecosystem-health",
  "severity": "fail|warn|info",
  "check": "check name",
  "detail": "human readable detail",
  "auto_fixed": false
}
```

One line per failed/warned check. `/improve` Phase 3 reads these signals.

## Implementation

When this skill is invoked, execute these steps:

### Step 1: Group 1 checks (bash, fast)
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

### Step 2: Group 2 checks
```bash
echo "=== Group 2: Work Queue Integrity ==="
uv run --no-project python "$REPO/scripts/work-queue/generate-index.py" >/dev/null 2>&1 \
    && echo "  [PASS] Index generates" \
    || echo "  [FAIL] Index generation failed"

# Gate violations in working/
grep -rL "plan_approved: true" "$REPO/.claude/work-queue/working/" 2>/dev/null \
    | sed 's/.*\///' | while read f; do echo "  [WARN] Missing plan_approved: $f"; done
```

### Step 3: Skill frontmatter (quick scan)
```bash
echo "=== Group 3: Skill Frontmatter ==="
missing=0
while IFS= read -r skill; do
    grep -q "^name:" "$skill" && grep -q "^version:" "$skill" && grep -q "^tags:" "$skill" \
        || { echo "  [WARN] Missing frontmatter fields: $skill"; ((missing++)); }
done < <(find "$REPO/.claude/skills" -name "SKILL.md" -not -path "*/_archive/*")
[[ $missing -eq 0 ]] && echo "  [PASS] All skills have required frontmatter"
```

### Step 4: Signal backlog
```bash
echo "=== Group 4: Signal Backlog ==="
count=$(ls "$REPO/.claude/state/pending-reviews/"*.jsonl 2>/dev/null | wc -l)
[[ $count -lt 50 ]] && echo "  [PASS] $count pending signal files" || echo "  [WARN] $count pending signal files (> 50)"
```

## Integration with /repo-sync

The `/repo-sync` skill Phase 5 should spawn this as a background agent:

```
After Phase 4 (encoding check), spawn ecosystem-health as a parallel agent.
Report its findings in the Phase 5 summary table.
```

## Related

- `/interoperability` — standards this skill verifies
- `/repo-sync` — spawns this after every pull
- `/improve` — consumes JSON signals from this check
- `WRK-207` — bidirectional skill linking (check 12)
- `WRK-209` — uv enforcement (check 4)
- `ecosystem-health-check.sh` — stop hook that calls this skill
