# Feature-First Planning + AI Agent Chunking — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Introduce a feature layer above individual WRK items so large work is planned as a whole, decomposed into AI-agent-sized execution chunks, and tracked with explicit linking and dependency management.

**Architecture:** A Feature WRK (`type: feature`) acts as an epic — it owns the master plan, goes through full Stage 1–7 planning (including cross-review and Stage 7 hard gate), then spawns child WRKs at Stage 7 exit. Each child WRK is sized to fit one agent context window. Existing WRKs are untouched; all new fields are opt-in and backward-compatible.

**Tech Stack:** Bash, Python (uv run --no-project), YAML frontmatter, Markdown, existing work-queue scripts

**WRK:** WRK-1127 | **Route:** C | **Complexity:** complex

---

## Scope: Three Child WRKs Under This Feature

This feature spec covers the full design. Execution is split into three child WRKs spawned at Stage 7 exit:

| Child | Title | Depends on |
|-------|-------|------------|
| WRK-A | Model, heuristic docs, SKILL.md update | — |
| WRK-B | Tooling (new-feature.sh, dep_graph, INDEX.md) | WRK-A |
| WRK-C | Process integration (stage contracts, whats-next, stage 9 routing) | WRK-A |

WRK-B and WRK-C can run in parallel after WRK-A.

---

## Feature Lifecycle (how Feature WRKs behave)

```
Feature WRK created (pending)
  → Stages 1–7  full planning pipeline
      Stage 1:  capture review (hard gate — user approves scope)
      Stage 2:  resource intelligence
      Stage 3:  triage (complexity: complex, type: feature)
      Stage 4:  plan draft (EnterPlanMode → this document)
      Stage 5:  user reviews plan draft (hard gate)
      Stage 6:  cross-review (Claude + Codex + Gemini)
      Stage 7:  user approves final plan (hard gate)
  → Stage 7 exit:  new-feature.sh spawns child WRKs
  → Feature WRK status: "coordinating" (new status value)
  → Children execute through their own Stages 1–20
  → Feature WRK closes when ALL children reach status: archived
  → Stage 19/20 run on feature WRK itself as normal
```

---

## Chunk-Sizing Heuristic (canonical rule)

A WRK is **one agent chunk** if it satisfies ALL of the following:

| Constraint | Limit | Rationale |
|------------|-------|-----------|
| Repos touched | ≤ 1 | Cross-repo changes pollute context fast |
| Files changed | ≤ 5 | Keeps Stage 10 execution scannable |
| Plan section length | ≤ 150 words | Forces tight scope boundary |
| Stage 10 sub-phases | ≤ 3 | One agent session, one coherent thread |
| Independent test scope | ≤ 1 module | TDD gate verifiable in one run |

If any constraint is exceeded → create a Feature WRK and decompose into children.

**Planning weight rule (hard):** Feature WRKs are not shortcuts. They must complete full Stage 1–7 (including Stage 6 cross-review) before any child WRK enters the queue. Planning first; execution second — always.

---

## File Map

### New files to create

| File | Responsibility |
|------|---------------|
| `scripts/work-queue/new-feature.sh` | Create Feature WRK + scaffold child WRKs from decomposition |
| `scripts/work-queue/feature-status.sh` | Print feature completion % (children done/total) |
| `scripts/work-queue/feature-close-check.sh` | Exit 0 if all children archived; else exit 1 |
| `config/work-queue/feature-template.md` | Feature WRK frontmatter + body template |
| `config/work-queue/chunk-sizing.yaml` | Machine-readable chunk heuristic (referenced by scripts) |
| `.claude/rules/feature-planning.md` | Canonical chunk-sizing rule + feature lifecycle prose |
| `specs/wrk/WRK-1127/wrk-1127-feature-first-planning.md` | This document (feature plan) |

### Files to modify

| File | Change |
|------|--------|
| `.claude/work-queue/scripts/generate-index.py` | Add `type`, `phases` to `normalize()`; add "By Feature" rollup section |
| `scripts/work-queue/dep_graph.py` | Render feature trees (parent → children with status) |
| `scripts/work-queue/whats-next.sh` | Show feature completion % alongside individual WRK items |
| `.claude/skills/coordination/workspace/work-queue/SKILL.md` | Add Feature layer section |
| `.claude/skills/coordination/workspace/work-queue-workflow/SKILL.md` | Add feature lifecycle stage contracts |
| `scripts/work-queue/stages/stage-09-routing.yaml` | Add routing decision: "is this a feature? → spawn children" |
| `.claude/work-queue/pending/WRK-1127.md` | Add `spec_ref`, `type: feature`, update status |

---

## Chunk 1: Model, Heuristic Docs, SKILL.md (WRK-A work)

### Task 1: chunk-sizing.yaml — machine-readable heuristic

**Files:**
- Create: `config/work-queue/chunk-sizing.yaml`

- [ ] Write `config/work-queue/chunk-sizing.yaml`:

```yaml
# Canonical chunk-sizing heuristic for AI agent work items
# Referenced by new-feature.sh and feature-planning.md
version: "1.0"
max_repos: 1
max_files_changed: 5
max_plan_words: 150
max_stage10_phases: 3
max_test_modules: 1
# If any limit exceeded → use a Feature WRK and decompose into children
```

- [ ] Verify file is valid YAML:
```bash
uv run --no-project python -c "import yaml; yaml.safe_load(open('config/work-queue/chunk-sizing.yaml'))"
```
Expected: no output (no error)

- [ ] Commit:
```bash
git add config/work-queue/chunk-sizing.yaml
git commit -m "feat(work-queue): add chunk-sizing heuristic YAML"
```

---

### Task 2: feature-planning.md rule file

**Files:**
- Create: `.claude/rules/feature-planning.md`

- [ ] Write `.claude/rules/feature-planning.md`:

```markdown
# Feature Planning Rules

> When work is too large for one agent context window, use a Feature WRK.

## When to Create a Feature WRK

Read `config/work-queue/chunk-sizing.yaml`. If ANY limit is exceeded, create a
Feature WRK instead of a regular WRK. Never try to fit oversized work into one item.

## Feature WRK Lifecycle

1. Create Feature WRK with `type: feature` in frontmatter
2. Run full Stages 1–7 (planning + Stage 6 cross-review + Stage 7 hard gate)
3. At Stage 7 exit: run `scripts/work-queue/new-feature.sh WRK-NNN` to scaffold children
4. Feature WRK moves to status `coordinating`; children are queued as pending
5. Feature WRK closes automatically when all children reach `archived`

**Hard rule:** No child WRK enters the queue before Stage 7 is complete on the feature.

## Decomposition in the Feature Plan

The feature plan (Stage 4b artifact) MUST include a `## Decomposition` section with:
- Child title and one-sentence scope
- Which files/skills each child needs (entry_reads)
- Explicit dependencies between children (`blocked_by:`)
- Preferred agent per child (`orchestrator:`)

## Linking and Dependency Fields

| Field | Set on | Meaning |
|-------|--------|---------|
| `type: feature` | Feature WRK | Marks this as an orchestrating item |
| `children: [WRK-A, WRK-B]` | Feature WRK | All child WRKs spawned by this feature |
| `parent: WRK-NNN` | Child WRK | Points to the feature that owns it |
| `blocked_by: [WRK-A]` | Child WRK | Sequential dependency on sibling |
| `entry_reads:` | Child checkpoint | Files/skills loaded at stage start |
| `orchestrator:` | Child WRK | Preferred AI provider for execution |
```

- [ ] Verify file is ≤ 400 lines (hard limit):
```bash
wc -l .claude/rules/feature-planning.md
```
Expected: < 400

- [ ] Commit:
```bash
git add .claude/rules/feature-planning.md
git commit -m "feat(rules): add feature-planning rules with chunk-sizing heuristic"
```

---

### Task 3: feature-template.md

**Files:**
- Create: `config/work-queue/feature-template.md`

- [ ] Write `config/work-queue/feature-template.md`:

```markdown
---
id: WRK-NNN
title: "<feature title>"
type: feature
status: pending
priority: high
complexity: complex
created_at: "YYYY-MM-DD"
target_repos: []
computer: ace-linux-1
plan_workstations: [ace-linux-1]
execution_workstations: [ace-linux-1]
category: ""
subcategory: ""
spec_ref: specs/wrk/WRK-NNN/wrk-NNN-<short-name>.md
children: []         # populated by new-feature.sh at Stage 7 exit
plan_reviewed: false
plan_approved: false
percent_complete: 0
---

## Mission

One sentence. Defines the scope boundary — what is IN and what is OUT.

## What / Why

2-3 paragraphs. What problem does this solve and why now.

## Acceptance Criteria

- [ ] AC1
- [ ] AC2

## Decomposition

<!-- REQUIRED for Feature WRKs — filled in at Stage 4b -->
<!-- new-feature.sh reads this section to scaffold child WRKs -->

| Child key | Title | Scope (one sentence) | Depends on | Agent |
|-----------|-------|----------------------|------------|-------|
| child-a | ... | ... | — | claude |
| child-b | ... | ... | child-a | codex |

### Child: child-a

**Files/skills needed (entry_reads):**
- `specs/wrk/WRK-NNN/wrk-NNN-<short-name>.md`
- `.claude/skills/...`

**Acceptance Criteria:**
- [ ] ...

### Child: child-b

**Files/skills needed (entry_reads):**
- ...

**Acceptance Criteria:**
- [ ] ...
```

- [ ] Commit:
```bash
git add config/work-queue/feature-template.md
git commit -m "feat(work-queue): add feature WRK template with decomposition section"
```

---

### Task 4: Update work-queue SKILL.md — Feature layer section

**Files:**
- Modify: `.claude/skills/coordination/workspace/work-queue/SKILL.md`

- [ ] Read current SKILL.md to locate insertion point (after `## Complexity Routing` section)

- [ ] Add `## Feature Layer` section after `## Complexity Routing`:

```markdown
## Feature Layer (Epic-level work)

When a work item exceeds chunk-sizing limits (`config/work-queue/chunk-sizing.yaml`),
create a **Feature WRK** instead of a regular WRK:

```bash
scripts/work-queue/new-feature.sh  # interactive scaffold
# or manually: copy config/work-queue/feature-template.md
```

Feature WRK lifecycle:
- Full Stage 1–7 planning (Stage 6 cross-review + Stage 7 hard gate mandatory)
- At Stage 7 exit → `new-feature.sh WRK-NNN` spawns child WRKs
- Feature WRK status becomes `coordinating`; children queue as `pending`
- Feature closes when all children are `archived`

Key frontmatter fields:
- `type: feature` — marks this as an orchestrating item
- `children: [WRK-A, WRK-B]` — populated by new-feature.sh
- Child WRKs carry `parent: WRK-NNN` and optional `blocked_by: [sibling]`

Feature status: `scripts/work-queue/feature-status.sh WRK-NNN`
```

- [ ] Verify SKILL.md is still ≤ 250 lines (its pruned target):
```bash
wc -l .claude/skills/coordination/workspace/work-queue/SKILL.md
```

- [ ] Commit:
```bash
git add .claude/skills/coordination/workspace/work-queue/SKILL.md
git commit -m "feat(skill): add Feature layer section to work-queue SKILL.md"
```

---

### Task 5: Update generate-index.py — add type/phases to normalize()

**Files:**
- Modify: `.claude/work-queue/scripts/generate-index.py`

- [ ] Read lines 37–50 and 198–272 of `generate-index.py`

- [ ] In `FRONTMATTER_FIELDS` list (line ~37), add:
```python
"type", "phases", "parent",   # feature layer fields
```
(Note: `children` and `parent` already exist — only add `type` and `phases` if missing)

- [ ] In `normalize()` function, add defaults for new fields:
```python
item.setdefault("type", "task")        # "task" | "feature"
item.setdefault("phases", [])
```

- [ ] Run generate-index.py to verify no regression:
```bash
uv run --no-project python .claude/work-queue/scripts/generate-index.py
```
Expected: `Generated .../INDEX.md with NNN items.` (no errors)

- [ ] Commit:
```bash
git add .claude/work-queue/scripts/generate-index.py
git commit -m "feat(index): add type/phases fields to normalize() for feature layer"
```

---

## Chunk 2: Tooling — new-feature.sh, feature-status.sh, dep_graph (WRK-B work)

### Task 6: new-feature.sh — scaffold child WRKs from feature decomposition

**Files:**
- Create: `scripts/work-queue/new-feature.sh`

This script:
1. Takes `WRK-NNN` as argument
2. Reads the `## Decomposition` table from the feature spec
3. For each child row: runs `next-id.sh`, creates a child `.md` with correct frontmatter
4. Sets `parent: WRK-NNN`, `blocked_by:` from decomposition deps, `entry_reads:` from the child section
5. Updates the Feature WRK's `children:` list
6. Prints a summary of created children

- [ ] Write `scripts/work-queue/new-feature.sh`:

```bash
#!/usr/bin/env bash
# new-feature.sh WRK-NNN
# Scaffolds child WRKs from the ## Decomposition section of a Feature WRK spec
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

WRK_ID="${1:?Usage: new-feature.sh WRK-NNN}"
PENDING_DIR=".claude/work-queue/pending"
ASSETS_DIR=".claude/work-queue/assets"

# Find the feature WRK file
WRK_FILE=$(find "$PENDING_DIR" -name "${WRK_ID}.md" 2>/dev/null | head -1)
if [[ -z "$WRK_FILE" ]]; then
  echo "ERROR: ${WRK_ID}.md not found in pending/" >&2
  exit 1
fi

# Extract spec_ref from frontmatter
SPEC_REF=$(grep '^spec_ref:' "$WRK_FILE" | sed 's/spec_ref: *//' | tr -d '"')
if [[ -z "$SPEC_REF" || ! -f "$SPEC_REF" ]]; then
  echo "ERROR: spec_ref not set or file not found: $SPEC_REF" >&2
  exit 1
fi

echo "Feature: $WRK_ID  Spec: $SPEC_REF"
echo ""

# Parse decomposition table rows: | child-key | title | scope | depends-on | agent |
# Skips header and separator rows
CHILDREN=()
while IFS='|' read -r _ key title scope deps agent _; do
  key="${key// /}"
  [[ -z "$key" || "$key" == "Child key" || "$key" =~ ^-+$ ]] && continue
  title="${title## }"; title="${title%% }"
  scope="${scope## }"; scope="${scope%% }"
  deps="${deps## }";  deps="${deps%% }"
  agent="${agent## }"; agent="${agent%% }"

  CHILD_ID=$(bash scripts/work-queue/next-id.sh)
  CHILDREN+=("$CHILD_ID")

  # Build blocked_by list
  BLOCKED_BY="[]"
  if [[ "$deps" != "—" && "$deps" != "-" && -n "$deps" ]]; then
    BLOCKED_BY="[${deps}]"
  fi

  cat > "${PENDING_DIR}/${CHILD_ID}.md" <<EOF
---
id: ${CHILD_ID}
title: "${title}"
status: pending
priority: high
complexity: medium
created_at: "$(date +%Y-%m-%d)"
parent: ${WRK_ID}
blocked_by: ${BLOCKED_BY}
target_repos: []
computer: ace-linux-1
orchestrator: ${agent:-claude}
plan_workstations: [ace-linux-1]
execution_workstations: [ace-linux-1]
category: ""
subcategory: ""
---

## Mission

${scope}

## What / Why

<!-- Filled from feature spec section: ### Child: ${key} -->

## Acceptance Criteria

<!-- Copy ACs from feature spec: ### Child: ${key} -->
EOF

  echo "Created ${CHILD_ID}: ${title} (blocked_by: ${BLOCKED_BY})"
done < <(grep '^|' "$SPEC_REF" | grep -v 'Child key\|---')

# Update children list on Feature WRK
CHILDREN_YAML="[$(IFS=', '; echo "${CHILDREN[*]}")]"
sed -i "s/^children: \[\]/children: ${CHILDREN_YAML}/" "$WRK_FILE"
sed -i "s/^status: pending/status: coordinating/" "$WRK_FILE"

echo ""
echo "Feature ${WRK_ID} → coordinating. Children: ${CHILDREN_YAML}"
echo "Regenerating INDEX.md..."
uv run --no-project python .claude/work-queue/scripts/generate-index.py
```

- [ ] Make executable:
```bash
chmod +x scripts/work-queue/new-feature.sh
```

- [ ] Write test — dry-run against WRK-1127 (integration test):
```bash
# Test: verify new-feature.sh exits 0 and creates child files
bash scripts/work-queue/new-feature.sh WRK-1127 2>&1
ls .claude/work-queue/pending/ | grep WRK-112  # should show new children
```
Expected: 3 new child files created, WRK-1127.md has `children:` populated

- [ ] Commit:
```bash
git add scripts/work-queue/new-feature.sh
git commit -m "feat(work-queue): add new-feature.sh to scaffold child WRKs from feature decomposition"
```

---

### Task 7: feature-status.sh

**Files:**
- Create: `scripts/work-queue/feature-status.sh`

- [ ] Write `scripts/work-queue/feature-status.sh`:

```bash
#!/usr/bin/env bash
# feature-status.sh WRK-NNN
# Print completion % for a Feature WRK (children done/archived vs total)
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

WRK_ID="${1:?Usage: feature-status.sh WRK-NNN}"

# Find feature WRK in any state dir
WRK_FILE=$(find .claude/work-queue/pending .claude/work-queue/working \
  .claude/work-queue/blocked -name "${WRK_ID}.md" 2>/dev/null | head -1)
[[ -z "$WRK_FILE" ]] && WRK_FILE=$(find .claude/work-queue/archive -name "${WRK_ID}.md" 2>/dev/null | head -1)
[[ -z "$WRK_FILE" ]] && { echo "ERROR: ${WRK_ID} not found" >&2; exit 1; }

# Extract children list
CHILDREN=$(grep '^children:' "$WRK_FILE" | sed 's/children: *\[//;s/\]//' | tr ',' ' ')
if [[ -z "$CHILDREN" ]]; then
  echo "${WRK_ID}: no children (standalone item)"
  exit 0
fi

TOTAL=0; DONE=0
for CHILD in $CHILDREN; do
  CHILD="${CHILD// /}"
  [[ -z "$CHILD" ]] && continue
  TOTAL=$((TOTAL + 1))
  STATUS=$(find .claude/work-queue -name "${CHILD}.md" 2>/dev/null -exec grep '^status:' {} \; | head -1 | awk '{print $2}')
  [[ "$STATUS" == "archived" || "$STATUS" == "done" ]] && DONE=$((DONE + 1))
  printf "  %-12s  %s\n" "$CHILD" "${STATUS:-unknown}"
done

PCT=$(( TOTAL > 0 ? DONE * 100 / TOTAL : 0 ))
echo ""
echo "Feature ${WRK_ID}: ${DONE}/${TOTAL} children complete (${PCT}%)"
```

- [ ] Make executable and test:
```bash
chmod +x scripts/work-queue/feature-status.sh
bash scripts/work-queue/feature-status.sh WRK-1127
```
Expected: lists child WRKs with statuses and completion %

- [ ] Commit:
```bash
git add scripts/work-queue/feature-status.sh
git commit -m "feat(work-queue): add feature-status.sh for child completion tracking"
```

---

### Task 8: feature-close-check.sh

**Files:**
- Create: `scripts/work-queue/feature-close-check.sh`

- [ ] Write `scripts/work-queue/feature-close-check.sh`:

```bash
#!/usr/bin/env bash
# feature-close-check.sh WRK-NNN
# Exit 0 if all children are archived; exit 1 otherwise (used as gate condition)
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

WRK_ID="${1:?Usage: feature-close-check.sh WRK-NNN}"
WRK_FILE=$(find .claude/work-queue -name "${WRK_ID}.md" 2>/dev/null | head -1)
[[ -z "$WRK_FILE" ]] && { echo "ERROR: ${WRK_ID} not found" >&2; exit 1; }

CHILDREN=$(grep '^children:' "$WRK_FILE" | sed 's/children: *\[//;s/\]//' | tr ',' ' ')
[[ -z "$CHILDREN" ]] && { echo "PASS: no children"; exit 0; }

FAIL=0
for CHILD in $CHILDREN; do
  CHILD="${CHILD// /}"; [[ -z "$CHILD" ]] && continue
  STATUS=$(find .claude/work-queue -name "${CHILD}.md" 2>/dev/null \
    -exec grep '^status:' {} \; | head -1 | awk '{print $2}')
  if [[ "$STATUS" != "archived" ]]; then
    echo "BLOCK: ${CHILD} is ${STATUS:-unknown} (not archived)"
    FAIL=1
  fi
done

if [[ $FAIL -eq 0 ]]; then
  echo "PASS: all children archived — feature ${WRK_ID} may close"
  exit 0
else
  exit 1
fi
```

- [ ] Make executable and test:
```bash
chmod +x scripts/work-queue/feature-close-check.sh
bash scripts/work-queue/feature-close-check.sh WRK-1127 && echo "PASS" || echo "BLOCKED (expected)"
```
Expected: BLOCKED (children not yet archived)

- [ ] Commit:
```bash
git add scripts/work-queue/feature-close-check.sh
git commit -m "feat(work-queue): add feature-close-check.sh for gate enforcement"
```

---

### Task 9: dep_graph.py — feature tree rendering

**Files:**
- Modify: `scripts/work-queue/dep_graph.py`

- [ ] Read `dep_graph.py` to understand current rendering approach

- [ ] Add a `--feature WRK-NNN` flag that prints an ASCII tree:

```
WRK-1127 [coordinating] Feature-first planning
├── WRK-1128 [working]  Model + docs           (agent: claude)
├── WRK-1129 [pending]  Tooling                (blocked_by: WRK-1128, agent: codex)
└── WRK-1130 [pending]  Process integration    (blocked_by: WRK-1128, agent: gemini)
```

- [ ] Add test:
```bash
# Smoke test — verify --feature flag exits 0 and prints tree
uv run --no-project python scripts/work-queue/dep_graph.py --feature WRK-1127
```
Expected: tree output with no traceback

- [ ] Commit:
```bash
git add scripts/work-queue/dep_graph.py
git commit -m "feat(dep_graph): add --feature flag for ASCII feature tree rendering"
```

---

### Task 10: INDEX.md — "By Feature" section

**Files:**
- Modify: `.claude/work-queue/scripts/generate-index.py`

- [ ] Read the section of `generate-index.py` that renders section headers in INDEX.md

- [ ] After the existing `## By Category` section, add a `## By Feature` section that:
  - Lists only items where `type == "feature"`
  - For each feature: title, status, children count, completion %
  - Format: `| WRK-NNN | title | coordinating | 1/3 (33%) |`

- [ ] Run and verify:
```bash
uv run --no-project python .claude/work-queue/scripts/generate-index.py
grep -A 10 "By Feature" .claude/work-queue/INDEX.md
```
Expected: "By Feature" section present

- [ ] Commit:
```bash
git add .claude/work-queue/scripts/generate-index.py
git commit -m "feat(index): add By Feature section to INDEX.md"
```

---

## Chunk 3: Process Integration (WRK-C work)

### Task 11: Stage 9 routing — feature detection

**Files:**
- Modify: `scripts/work-queue/stages/stage-09-routing.yaml`

- [ ] Read `stage-09-routing.yaml` to understand current routing logic

- [ ] Add a routing decision block for feature items:

```yaml
feature_routing:
  condition: "frontmatter.type == 'feature' and stage7_complete"
  action: |
    Run: scripts/work-queue/new-feature.sh WRK-NNN
    Set status: coordinating
    Log: "Feature WRK-NNN decomposed into N children"
  next_stage: null   # Feature WRK waits; children run their own lifecycles
```

- [ ] Verify YAML is valid:
```bash
uv run --no-project python -c "import yaml; yaml.safe_load(open('scripts/work-queue/stages/stage-09-routing.yaml'))"
```

- [ ] Commit:
```bash
git add scripts/work-queue/stages/stage-09-routing.yaml
git commit -m "feat(stage-09): add feature routing — run new-feature.sh on type:feature items"
```

---

### Task 12: work-queue-workflow SKILL.md — feature lifecycle contracts

**Files:**
- Modify: `.claude/skills/coordination/workspace/work-queue-workflow/SKILL.md`

- [ ] Read the current SKILL.md to find the lifecycle section

- [ ] Add a `## Feature WRK Lifecycle` section covering:
  - Stage 7 exit artifact: `feature-decomposition.yaml` (child WRK IDs, deps, agents)
  - New status value: `coordinating`
  - Feature close gate: `feature-close-check.sh` in Stage 19 blocking condition
  - `entry_reads` auto-population: each child checkpoint includes `spec_ref` from parent feature

- [ ] Verify line count ≤ target:
```bash
wc -l .claude/skills/coordination/workspace/work-queue-workflow/SKILL.md
```

- [ ] Commit:
```bash
git add .claude/skills/coordination/workspace/work-queue-workflow/SKILL.md
git commit -m "feat(skill): add Feature WRK lifecycle contracts to work-queue-workflow"
```

---

### Task 13: whats-next.sh — feature completion % display

**Files:**
- Modify: `scripts/work-queue/whats-next.sh`

- [ ] Read current `whats-next.sh` output format

- [ ] After the "HIGH priority" section, add a "Features in progress" section:
  - Run `feature-status.sh` for any WRK with `status: coordinating`
  - Show: `WRK-NNN [2/3] Feature title`

- [ ] Test:
```bash
bash scripts/work-queue/whats-next.sh 2>&1 | head -40
```
Expected: "Features in progress" section appears if any coordinating features exist

- [ ] Commit:
```bash
git add scripts/work-queue/whats-next.sh
git commit -m "feat(whats-next): show feature completion % for coordinating feature WRKs"
```

---

### Task 14: Update WRK-1127 itself

**Files:**
- Modify: `.claude/work-queue/pending/WRK-1127.md`

- [ ] Update WRK-1127.md frontmatter to reflect this plan:

```yaml
type: feature
spec_ref: specs/wrk/WRK-1127/wrk-1127-feature-first-planning.md
complexity: complex
plan_reviewed: false
plan_approved: false
```

- [ ] Commit:
```bash
git add .claude/work-queue/pending/WRK-1127.md specs/wrk/WRK-1127/wrk-1127-feature-first-planning.md
git commit -m "chore(WRK-1127): add spec_ref and type:feature to frontmatter"
```

---

## Decomposition (for new-feature.sh at Stage 7 exit)

| Child key | Title | Scope (one sentence) | Depends on | Agent |
|-----------|-------|----------------------|------------|-------|
| child-a | Model, heuristic docs, SKILL.md | Chunk-sizing YAML, feature-planning rules, feature template, SKILL.md update, generate-index.py normalize() | — | claude |
| child-b | Tooling scripts + INDEX.md | new-feature.sh, feature-status.sh, feature-close-check.sh, dep_graph --feature, INDEX.md By Feature | child-a | claude |
| child-c | Process integration | Stage 9 routing, work-queue-workflow SKILL.md, whats-next.sh feature section | child-a | claude |

### Child: child-a

**Files/skills needed (entry_reads):**
- `specs/wrk/WRK-1127/wrk-1127-feature-first-planning.md`
- `.claude/skills/coordination/workspace/work-queue/SKILL.md`
- `config/work-queue/chunk-sizing.yaml` (to create)
- `.claude/rules/feature-planning.md` (to create)
- `config/work-queue/feature-template.md` (to create)
- `.claude/work-queue/scripts/generate-index.py`

**Acceptance Criteria:**
- [ ] `config/work-queue/chunk-sizing.yaml` exists and is valid YAML
- [ ] `.claude/rules/feature-planning.md` exists, ≤ 400 lines
- [ ] `config/work-queue/feature-template.md` exists with `## Decomposition` section
- [ ] `generate-index.py normalize()` has defaults for `type` and `phases`
- [ ] `work-queue/SKILL.md` has `## Feature Layer` section
- [ ] All changes committed

### Child: child-b

**Files/skills needed (entry_reads):**
- `specs/wrk/WRK-1127/wrk-1127-feature-first-planning.md`
- `scripts/work-queue/next-id.sh`
- `scripts/work-queue/dep_graph.py`
- `.claude/work-queue/scripts/generate-index.py`
- `scripts/work-queue/whats-next.sh` (read only)

**Acceptance Criteria:**
- [ ] `new-feature.sh WRK-1127` creates 3 child WRK files without error
- [ ] `feature-status.sh WRK-1127` prints correct completion %
- [ ] `feature-close-check.sh WRK-1127` exits 1 (children not done) correctly
- [ ] `dep_graph.py --feature WRK-1127` prints ASCII tree
- [ ] INDEX.md contains `## By Feature` section after regeneration
- [ ] All scripts are executable and committed

### Child: child-c

**Files/skills needed (entry_reads):**
- `specs/wrk/WRK-1127/wrk-1127-feature-first-planning.md`
- `scripts/work-queue/stages/stage-09-routing.yaml`
- `.claude/skills/coordination/workspace/work-queue-workflow/SKILL.md`
- `scripts/work-queue/whats-next.sh`
- `scripts/work-queue/feature-status.sh` (from child-b, must be done first)

**Acceptance Criteria:**
- [ ] `stage-09-routing.yaml` has `feature_routing:` block, valid YAML
- [ ] `work-queue-workflow/SKILL.md` has `## Feature WRK Lifecycle` section
- [ ] `whats-next.sh` shows "Features in progress" section when coordinating items exist
- [ ] All changes committed

---

## Overall Acceptance Criteria (Feature WRK-1127)

- [ ] Chunk-sizing heuristic is documented in machine-readable form (`chunk-sizing.yaml`) AND prose (`.claude/rules/feature-planning.md`)
- [ ] Feature WRK template exists with `## Decomposition` section
- [ ] `new-feature.sh` scaffolds child WRKs with correct `parent`, `blocked_by`, `orchestrator` fields
- [ ] `feature-status.sh` and `feature-close-check.sh` work correctly
- [ ] `dep_graph.py --feature` renders feature trees
- [ ] INDEX.md includes `## By Feature` rollup section
- [ ] Stage 9 routing handles `type: feature` items
- [ ] `work-queue-workflow/SKILL.md` documents feature lifecycle
- [ ] `whats-next.sh` shows feature completion
- [ ] All existing tests and scripts pass without modification (backward compatible)
- [ ] WRK-1127 itself has `type: feature`, `spec_ref` set, `children:` populated by new-feature.sh
