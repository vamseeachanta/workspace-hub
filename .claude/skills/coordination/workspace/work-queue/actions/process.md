# Work Queue: Process Action

> Select, triage, and execute the next work item from the queue.

## Trigger

Invoked when `/work run`, `/work`, or `/work` with action verbs (go, start, next, process) is called.

## Pipeline Overview

```
Select -> Triage -> Dependency Check -> Auto-Claim -> Pre-check -> Execute -> Test -> Cross-Review -> Commit -> Auto-Archive
```

## Step 1: Select Next Item

Priority order for selecting from `pending/`:
1. Items with `priority: high` (oldest first)
2. Items with `priority: medium` (oldest first)
3. Items with `priority: low` (oldest first)

```bash
QUEUE_DIR="${WORKSPACE_ROOT}/.claude/work-queue"
# Find highest priority pending item
for priority in high medium low; do
  ITEM=$(grep -rl "priority: ${priority}" "${QUEUE_DIR}/pending/"*.md 2>/dev/null | head -1)
  [[ -n "$ITEM" ]] && break
done
```

If no items found, report "Queue empty - nothing to process."

## Step 2: Triage

Read the work item and classify its complexity route:

| Route | Complexity | Pipeline |
|-------|-----------|----------|
| A | simple | Implement -> Test -> Archive |
| B | medium | Explore -> Implement -> Test -> Archive |
| C | complex | Plan+Explore -> Implement -> Test -> Review -> Archive |

Validate or reclassify the complexity from capture phase. The triage agent may upgrade complexity if the item is more involved than initially classified.

## Step 3: Dependency Check

Before claiming any item, validate that all dependencies are satisfied:

1. Read the `blocked_by` field from the work item frontmatter
2. For each ID in `blocked_by`, check if that item exists in `archive/`
3. If ANY blocker is NOT archived (still in `pending/`, `working/`, or `blocked/`), SKIP this item
4. Log: `"Skipping WRK-NNN: blocked by WRK-MMM (status: pending)"`
5. Move to the next item in priority order (return to Step 1)

```bash
BLOCKED_BY=$(grep "blocked_by:" "$ITEM" | sed 's/blocked_by: *\[//;s/\]//' | tr ',' '\n' | tr -d ' "')
for DEP_ID in $BLOCKED_BY; do
  [[ -z "$DEP_ID" ]] && continue
  # Check if dependency is archived
  ARCHIVED=$(find "${QUEUE_DIR}/archive" -name "${DEP_ID}-*.md" 2>/dev/null | head -1)
  if [[ -z "$ARCHIVED" ]]; then
    # Find where the blocker currently lives
    for dir in pending working blocked; do
      DEP_FILE=$(find "${QUEUE_DIR}/${dir}" -name "${DEP_ID}-*.md" 2>/dev/null | head -1)
      [[ -n "$DEP_FILE" ]] && echo "Skipping ${ITEM_ID}: blocked by ${DEP_ID} (status: ${dir})" && break
    done
    SKIP=true
    break
  fi
done
```

If the item is skipped due to unmet dependencies, select the next item by priority and repeat from Step 1.

## Step 4: Auto-Claim

Claiming happens automatically when processing begins -- no manual intervention required.

The item is moved from `pending/` to `working/` in both master and repo-local queues:

```bash
# Ensure working/ directory exists
mkdir -p "${QUEUE_DIR}/working"

# Master queue
mv "${QUEUE_DIR}/pending/${ITEM_FILE}" "${QUEUE_DIR}/working/${ITEM_FILE}"

# Repo-local queues
for REPO in ${TARGET_REPOS}; do
  REPO_QUEUE="${WORKSPACE_ROOT}/${REPO}/.claude/work-queue"
  mkdir -p "${REPO_QUEUE}/working"
  if [[ -f "${REPO_QUEUE}/pending/${ITEM_FILE}" ]]; then
    mv "${REPO_QUEUE}/pending/${ITEM_FILE}" "${REPO_QUEUE}/working/${ITEM_FILE}"
  fi
done
```

Update frontmatter automatically (both copies):
```yaml
status: working
claimed_at: <ISO 8601 timestamp>
route: A  # or B or C
```

This replaces the previous manual claim step. The item transitions to `working` status as soon as the process pipeline selects it and dependencies are satisfied.

## Step 5: Pre-check (Repo Readiness)

For each repository in `target_repos`:

```bash
cd "${WORKSPACE_ROOT}/${REPO}"
# Check clean working tree
[[ -z "$(git status --porcelain)" ]] || BLOCKED="dirty working tree"
# Check on main/default branch
BRANCH=$(git symbolic-ref --short HEAD)
# Check tests pass (if test runner exists)
```

If any repo fails pre-check:
- Move item to `blocked/` directory
- Set `blocked_by` field with reason
- Log the block and move to next item

## Step 6: Execute (Route-Dependent)

### Route A (Simple)

Delegate directly to a general-purpose subagent:

```
Task(subagent_type="general-purpose"):
  "Implement work item WRK-{id}: {title}

   Target repos: {target_repos}

   What: {description}

   Acceptance criteria:
   {criteria}

   Rules:
   - Use TDD: write test first, then implement
   - Make minimal changes
   - Commit with message: feat(work-queue): WRK-{id} - {title}"
```

### Route B (Medium)

1. **Explore**: Spawn Explore subagent to find relevant files and understand current code
2. **Implement**: Pass explore findings to general-purpose subagent for implementation
3. Uses same TDD and commit rules as Route A

### Route C (Complex)

1. **Plan+Explore**: Generate spec in `specs/modules/` using plan template. The plan agent performs deep codebase exploration across all target repos as part of spec creation — no separate Explore step.
   - Set `spec_ref` field in work item to spec path
   - Bidirectional link: spec links back to WRK item
   - **Sync spec to target repos**: Copy plan to each `<target-repo>/specs/modules/<module>/plan.md`
   - Explore findings are embedded directly in the spec (relevant files, current patterns, dependencies)
2. **Implement**: Multi-step implementation following spec phases
3. **Review**: Self-review pass checking acceptance criteria

## Step 7: Test

After implementation:

```bash
cd "${WORKSPACE_ROOT}/${REPO}"
# Run repo-specific test suite
# Python: pytest
# Node: npm test
# Go: go test ./...
```

If tests fail:
- Increment attempt counter (max 3)
- Return to Execute step with error context
- After 3 failures: mark as `status: failed` with `failure_reason`

## Step 8: Cross-Review Gate (MANDATORY)

After tests pass, all changes MUST pass cross-review before committing. This is a hard gate — commits are blocked until reviews clear.

### Review Submission

Generate a diff of all staged changes and submit for review:

```bash
REVIEW_SCRIPT="${WORKSPACE_ROOT}/scripts/review/cross-review.sh"

# Generate diff for review
cd "${WORKSPACE_ROOT}/${REPO}"
git diff HEAD > "/tmp/wrk-${ID}-review.diff"

# Submit to all reviewers (Claude + Codex + Gemini)
bash "${REVIEW_SCRIPT}" "/tmp/wrk-${ID}-review.diff" all --type implementation
```

For Route C items, the plan spec must also have been reviewed during the Plan+Explore phase:

```bash
# Route C only: plan review (3 iterations required)
bash "${REVIEW_SCRIPT}" "${SPEC_PATH}" all --type plan
```

### Gate Criteria

Review results are written to `scripts/review/results/`. The gate checks:

1. Parse each reviewer's output for a verdict line: `APPROVE`, `REQUEST_CHANGES`, or `REJECT`
2. **Pass condition**: No reviewer returned `REJECT` and no P1 (critical) issues were raised
3. **Fail condition**: Any `REJECT` verdict OR any unresolved P1 issue

```bash
RESULTS_DIR="${WORKSPACE_ROOT}/scripts/review/results"
LATEST=$(ls -t "${RESULTS_DIR}"/implementation-* 2>/dev/null | head -3)
BLOCKED=false

for RESULT in $LATEST; do
  if grep -q "REJECT" "$RESULT" || grep -q "P1" "$RESULT"; then
    BLOCKED=true
    REVIEWER=$(basename "$RESULT" | sed 's/implementation-//;s/-[0-9]*.*//')
    echo "Cross-review BLOCKED by ${REVIEWER}: $(grep -E 'REJECT|P1' "$RESULT" | head -1)"
  fi
done

if [[ "$BLOCKED" == "true" ]]; then
  echo "Fix P1 issues and re-run: bash ${REVIEW_SCRIPT} <diff> all --type implementation"
  # Return to Step 6 (Execute) to address feedback
  exit 1
fi
```

### On Failure

If the review gate fails:
- Log which reviewer(s) blocked and the P1 issues
- Return to Step 6 (Execute) to address the feedback
- Increment `review_attempts` in frontmatter (max 3 cycles)
- After 3 failed review cycles, mark as `status: review_blocked` for manual intervention

```yaml
review_attempts: 1
last_review: <ISO 8601>
review_blocked_by: "codex: P1 - missing error handling in auth flow"
```

### Reviewer Availability

If a reviewer CLI is not installed (e.g., `codex` or `gemini`), the script logs a fallback notice but does NOT block the commit. At minimum, the Claude self-review must pass. The gate degrades gracefully:

- 3 reviewers available: all 3 must clear (no REJECT/P1)
- 2 reviewers available: both must clear
- 1 reviewer (Claude only): Claude must clear

## Step 9: Commit

For each target repo with changes:

```bash
cd "${WORKSPACE_ROOT}/${REPO}"
git add -A
git commit -m "feat(work-queue): WRK-${ID} - ${TITLE}"
```

Update work item frontmatter with commit SHA:
```yaml
commit: "abc1234"
```

## Step 10: Auto-Archive

After tests pass and commit is complete, automatically check whether the item qualifies for archiving:

### Acceptance Criteria Check

1. Parse the work item's `## Acceptance Criteria` section
2. Count all checklist items matching `- [x]` (completed) and `- [ ]` (incomplete)
3. If ALL criteria are checked (`- [x]`), proceed to archive
4. If ANY criteria remain unchecked (`- [ ]`), leave the item in `working/` and add a note:

```yaml
auto_archive_blocked: true
auto_archive_note: "N of M acceptance criteria incomplete"
```

### Archive Execution

When all acceptance criteria are satisfied, archive in both master and repo-local queues:

```bash
# Check acceptance criteria
TOTAL=$(grep -c '- \[.\]' "$ITEM_FILE" || echo "0")
CHECKED=$(grep -c '- \[x\]' "$ITEM_FILE" || echo "0")

if [[ "$TOTAL" -gt 0 && "$CHECKED" -eq "$TOTAL" ]]; then
  # All criteria met - auto-archive
  # Master queue
  bash "${WORKSPACE_ROOT}/scripts/work-queue/archive-item.sh" "WRK-${ID}"

  # Repo-local queues
  for REPO in ${TARGET_REPOS}; do
    REPO_QUEUE="${WORKSPACE_ROOT}/${REPO}/.claude/work-queue"
    ARCHIVE_DIR="${REPO_QUEUE}/archive/$(date +%Y-%m)"
    mkdir -p "${ARCHIVE_DIR}"
    if [[ -f "${REPO_QUEUE}/working/${ITEM_FILE}" ]]; then
      mv "${REPO_QUEUE}/working/${ITEM_FILE}" "${ARCHIVE_DIR}/${ITEM_FILE}"
    fi
  done
else
  echo "Auto-archive skipped: ${CHECKED}/${TOTAL} acceptance criteria met"
  # Leave in working/ with note
fi
```

Both copies get completion metadata:
```yaml
status: done
completed_at: <ISO 8601>
duration_minutes: <calculated>
route_used: A  # or B or C
attempts: 1
```

## Failure Handling

```
Attempt 1: Execute normally
Attempt 2: Re-execute with additional context from failure
Attempt 3: Re-execute with broader exploration
Attempt 4+: Mark as failed, leave in working/ for manual review
```

Failed items:
```yaml
status: failed
failure_reason: "Tests failing after 3 attempts: assertion error in test_login"
failed_at: <ISO 8601>
attempts: 3
```

## Blocked Item Management

Items move to `blocked/` when:
- Target repo has dirty working tree
- Target repo has failing tests
- Dependency on another WRK item not yet done
- External dependency (PR pending, deployment needed)

Blocked items are checked by daily-reflect for staleness (>7 days).

## State Updates

After processing:
- Update `state.yaml` with last processed item and timestamp
- Increment processed counter
- Track route usage for triage accuracy feedback

## Batch Processing Mode

When invoked with `/work run --batch`, process all Route A (simple) items in sequence:

1. Filter pending items where `complexity: simple`
2. Sort by priority (`high` -> `medium` -> `low`), then by ID (ascending)
3. For each item:
   a. Run Dependency Check (Step 3) -- skip if dependencies unmet
   b. Auto-claim (move to `working/`)
   c. Execute Route A pipeline (Implement -> Test)
   d. Run Cross-Review Gate (Step 8) -- block commit if REJECT or P1 issues
   e. If reviews pass and tests pass, commit and auto-archive
   f. If tests or reviews fail, mark `status: failed` with `failure_reason` and continue to next item
4. Report summary: `"Batch complete: N processed, M succeeded, K failed"`

```bash
# Batch mode pseudocode
PROCESSED=0; SUCCEEDED=0; FAILED=0
for ITEM in $(get_simple_items_sorted_by_priority); do
  PROCESSED=$((PROCESSED + 1))
  if check_dependencies "$ITEM"; then
    auto_claim "$ITEM"
    if execute_route_a "$ITEM" && run_tests "$ITEM" && cross_review "$ITEM"; then
      commit "$ITEM"
      auto_archive "$ITEM"
      SUCCEEDED=$((SUCCEEDED + 1))
    else
      mark_failed "$ITEM"
      FAILED=$((FAILED + 1))
    fi
  else
    echo "Skipped $(get_id "$ITEM"): unmet dependencies"
    PROCESSED=$((PROCESSED - 1))
  fi
done
echo "Batch complete: ${PROCESSED} processed, ${SUCCEEDED} succeeded, ${FAILED} failed"
```

Batch mode only processes Route A (simple) items. Medium and complex items are skipped and left in `pending/` for individual processing via `/work run`.
