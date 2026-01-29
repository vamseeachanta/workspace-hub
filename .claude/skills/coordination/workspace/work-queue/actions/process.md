# Work Queue: Process Action

> Select, triage, and execute the next work item from the queue.

## Trigger

Invoked when `/work run`, `/work`, or `/work` with action verbs (go, start, next, process) is called.

## Pipeline Overview

```
Select -> Triage -> Claim -> Pre-check -> Execute -> Test -> Archive
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
| C | complex | Plan -> Explore -> Implement -> Test -> Review -> Archive |

Validate or reclassify the complexity from capture phase. The triage agent may upgrade complexity if the item is more involved than initially classified.

## Step 3: Claim

Move item from `pending/` to `working/` in both master and repo-local queues:

```bash
# Master queue
mv "${QUEUE_DIR}/pending/${ITEM_FILE}" "${QUEUE_DIR}/working/${ITEM_FILE}"

# Repo-local queues
for REPO in ${TARGET_REPOS}; do
  REPO_QUEUE="${WORKSPACE_ROOT}/${REPO}/.claude/work-queue"
  if [[ -f "${REPO_QUEUE}/pending/${ITEM_FILE}" ]]; then
    mv "${REPO_QUEUE}/pending/${ITEM_FILE}" "${REPO_QUEUE}/working/${ITEM_FILE}"
  fi
done
```

Update frontmatter (both copies):
```yaml
status: claimed
claimed_at: <ISO 8601>
route: A  # or B or C
```

## Step 4: Pre-check (Repo Readiness)

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

## Step 5: Execute (Route-Dependent)

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

1. **Plan**: Generate spec in `specs/modules/` using plan template
   - Set `spec_ref` field in work item to spec path
   - Bidirectional link: spec links back to WRK item
   - **Sync spec to target repos**: Copy plan to each `<target-repo>/specs/modules/<module>/plan.md`
2. **Explore**: Deep codebase exploration across all target repos
3. **Implement**: Multi-step implementation following spec phases
4. **Review**: Self-review pass checking acceptance criteria

## Step 6: Test

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

## Step 7: Commit

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

## Step 8: Archive

Archive in both master and repo-local queues:

```bash
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
