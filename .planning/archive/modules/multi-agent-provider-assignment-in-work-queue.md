---
title: "Multi-Agent Provider Assignment in Work Queue"
description: "Claude orchestrates, Codex/Gemini execute — decided during planning"
version: "4.0"
module: work-queue
session:
  id: 2026-02-16-multi-agent-providers
  agent: claude-opus-4-6
review: pending
---

# Multi-Agent Provider Assignment in Work Queue

## Context

CLAUDE.md says "Claude is the orchestrator, not the executor." In practice, Claude does everything. Codex and Gemini are installed but only review Claude's output.

**What we want**: During planning, decide which agent(s) execute each task based on known strengths. Write clear instructions. Let execution run. Come back and check results.

No smart routing, no EWMA engines, no real-time classification. Just thoughtful planning and clear delegation.

**Provider strengths** (known from experience):

| Provider | Good at | Not great at |
|----------|---------|-------------|
| Codex | Focused code tasks, single-file changes, bug fixes, refactoring | Multi-file architecture, nuanced design decisions |
| Gemini | Research, data analysis, summarization, large documents | Precise code edits, test-driven workflows |
| Claude | Everything (but expensive); orchestration, architecture, sensitive data | N/A — use as fallback |

---

## Phase 1: Update Process & Template (WRK-149)

**Complexity**: simple | **Depends on**: nothing

### What changes

**1. `.claude/work-queue/process.md`**

Add to frontmatter template (after `brochure_status:` at line 176):

```yaml
provider:                # claude | codex | gemini (decided during planning)
provider_alt:            # optional second agent for dual-agent mode
```

Add to the Plan section (after line 56) — provider assignment happens during planning, not triage:

```markdown
### Provider Assignment (During Planning)

When writing the plan, decide who executes:

1. Look at what the task actually requires (code? research? architecture?)
2. Match to provider strengths (see table above)
3. If clear fit → assign one provider
4. If borderline or want to compare → assign two (provider + provider_alt)

Write an **Execution Brief** in the WRK body with:
- Which provider(s) and why
- Exact task description for the executor (self-contained, no assumptions)
- Machine-checkable acceptance criteria
- What the user should review when they come back
```

Add `## Execution Brief` to the body template (after `## Plan`):

```markdown
## Execution Brief

### Provider
- **Executor**: <provider> — <one-line rationale>
- **Alt**: <provider_alt or "none">

### Task for Executor
<!-- Self-contained description sent to the executing agent. Include file paths, constraints, expected output. -->

### Done When
- [ ] <specific, verifiable criterion>
- [ ] <test command that must pass>

### For User Review
<!-- What to look at when you come back -->
```

**2. `.claude/work-queue/scripts/generate-index.py`**

- Line 33-38 (`FRONTMATTER_FIELDS`): Add `"provider"`, `"provider_alt"`
- Line 174-192 (`normalize`): Add defaults for both fields
- Lines 594-613 (Master Table): Add `Provider` column

**3. `config/agents/behavior-contract.yaml`**

Add note: provider assignment is a planning-stage decision, not runtime routing.

### Verification

1. `python3 .claude/work-queue/scripts/generate-index.py` succeeds
2. INDEX.md shows `Provider` column (all `-` initially)

---

## Phase 2: Backfill Pending Items (WRK-150)

**Complexity**: medium | **Depends on**: WRK-149

### What changes

Go through all 47 pending items and add `provider:` based on what the task actually needs. No automation — just read each item, decide, write it in.

Simple script `scripts/work-queue/assign-providers.sh` to help:
- Lists all pending items with title + complexity
- We manually fill in the provider column
- Script applies the assignments to frontmatter

**Expected rough split**:

| Provider | ~Count | Why |
|----------|--------|-----|
| claude | 20-25 | Complex architecture, multi-repo, sensitive/personal |
| codex | 15-18 | Implementation, refactoring, bug fixes, config |
| gemini | 4-6 | Research, data analysis, document processing |

Items requiring `claude` regardless: WRK-005, WRK-008, WRK-141, WRK-142, WRK-133 (personal/sensitive).

For items we're unsure about, set both `provider:` and `provider_alt:` — run both when the time comes, compare.

### Verification

1. Every pending item has `provider:` set
2. INDEX.md Provider column populated
3. Spot-check 5 items: YAML still valid

---

## Phase 3: Wire Execution (WRK-151)

**Complexity**: complex | **Depends on**: WRK-149

### What changes

Make the provider adapters actually execute tasks, not just check CLI availability.

**1. `scripts/agents/providers/codex.sh`** — add `execute` action:

```bash
execute)
    task_file="${1:?Usage: codex.sh execute <task_file>}"
    # Extract task body, skip frontmatter
    task_desc=$(awk '/^---$/{if(++c==2)f=1;next}f' "$task_file" | head -80)
    # Run via Codex CLI
    out=$(mktemp) err=$(mktemp)
    echo "$task_desc" | timeout 300 codex exec - >"$out" 2>"$err"
    echo "output=$out errors=$err exit=$?"
    ;;
```

Same pattern for `gemini.sh` (`echo "$task_desc" | gemini -p "..." -y`) and `claude.sh` (`claude -p "$task_desc"`).

**2. `scripts/agents/execute.sh`** — after line 36 ("Execution contract accepted"), add dispatch:

```bash
# Read provider from WRK frontmatter
assigned=$(wrk_get_frontmatter_value "$wrk_id" "provider")
[[ -z "$assigned" ]] && assigned="$provider"

# Dispatch
"$AGENTS_DIR/providers/${assigned}.sh" execute "$(resolve_wrk_file "$wrk_id")"

# If dual-agent mode, also dispatch alt
alt=$(wrk_get_frontmatter_value "$wrk_id" "provider_alt")
if [[ -n "$alt" ]]; then
    "$AGENTS_DIR/providers/${alt}.sh" execute "$(resolve_wrk_file "$wrk_id")"
    echo "Dual-agent: compare outputs from $assigned and $alt"
fi
```

**3. Cross-review — UNCHANGED.** `scripts/review/cross-review.sh` is not touched.

### Verification

1. `codex.sh check` still works (backward compat)
2. `codex.sh execute <test-file>` runs Codex CLI on task content
3. `execute.sh --provider claude WRK-TEST` dispatches to codex when `provider: codex`
4. `cross-review.sh <file> all` still works

---

## Dependency Graph

```
WRK-149 (Phase 1: template + process)
    ├──> WRK-150 (Phase 2: backfill)   [blocked_by: 149]
    └──> WRK-151 (Phase 3: execution)  [blocked_by: 149]
```

## The Workflow After Implementation

```
PLANNING (user present)
  └── Claude plans the work item
  └── Decides provider(s) based on task requirements
  └── Writes Execution Brief with clear instructions
  └── User approves plan → walks away

EXECUTION (autonomous)
  └── execute.sh dispatches to assigned provider(s)
  └── Codex/Gemini/Claude execute the task
  └── If dual-agent: both run independently
  └── Claude validates against "Done When" criteria

CHECKING (user returns)
  └── User reviews "For User Review" section
  └── Sees what was done, test results, any decisions made
  └── Approves or sends back
```

## Critical Files

| File | Phase | Change |
|------|-------|--------|
| `.claude/work-queue/process.md` | 1 | Add provider fields, Execution Brief template, planning-stage assignment |
| `.claude/work-queue/scripts/generate-index.py` | 1 | Add provider to fields + Master Table |
| `config/agents/behavior-contract.yaml` | 1 | Note provider = planning decision |
| `scripts/work-queue/assign-providers.sh` | 2 | New: helper for bulk assignment |
| `scripts/agents/providers/codex.sh` | 3 | Add `execute` action |
| `scripts/agents/providers/gemini.sh` | 3 | Add `execute` action |
| `scripts/agents/providers/claude.sh` | 3 | Add `execute` action |
| `scripts/agents/execute.sh` | 3 | Wire dispatch + dual-agent support |
