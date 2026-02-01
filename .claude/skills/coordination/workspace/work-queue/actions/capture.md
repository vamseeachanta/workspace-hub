# Work Queue: Capture Action

> Parse user input into work items and file them in the pending queue.

## Trigger

Invoked when `/work add <description>` is called, or when `/work` is called with descriptive content (not an action verb).

## Input Processing

### 1. Parse Input

Detect single vs multi-request:
- **Single item**: One clear task description
- **Multi-item**: Contains numbered lists, bullet points, "and also", "plus", semicolons separating distinct tasks

```
Single: "Fix login redirect in aceengineer-website"
Multi:  "1. Fix login redirect 2. Add dark mode toggle 3. Update footer links"
```

### 2. Duplicate Check

Before creating, scan existing items in `pending/`, `working/`, and `blocked/` directories:

```bash
QUEUE_DIR="${WORKSPACE_ROOT}/.claude/work-queue"
for dir in pending working blocked; do
  grep -l "title:.*${SEARCH_TERM}" "${QUEUE_DIR}/${dir}/"*.md 2>/dev/null
done
```

If a match is found with >80% title similarity, warn the user and ask whether to proceed.

### 3. Classify Complexity

| Complexity | Criteria |
|------------|----------|
| simple | <50 words, single clear change, 1 repo, known files |
| medium | 50-200 words, clear outcome but unknown files, 1-2 repos |
| complex | >200 words, architectural changes, 3+ repos, ambiguous scope, 3+ distinct features |

### 4. Extract Metadata

From the description, infer:
- **title**: Concise imperative phrase (max 60 chars)
- **target_repos**: Repository names mentioned or implied
- **priority**: Default `medium`; infer `high` if words like "urgent", "critical", "broken", "fix"; infer `low` if "nice to have", "eventually", "when possible"
- **complexity**: Per classification above

### 5. Generate ID

```bash
NEXT_ID=$(bash "${WORKSPACE_ROOT}/scripts/work-queue/next-id.sh")
SLUG=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-' | head -c 40)
FILENAME="WRK-${NEXT_ID}-${SLUG}.md"
```

### 6. Create Work Item File

Write to `${QUEUE_DIR}/pending/${FILENAME}` using the appropriate template:
- simple/medium -> `work-item-simple.md` template
- complex -> `work-item-complex.md` template

Fill in all frontmatter fields. Set `created_at` to current ISO 8601 timestamp.

### 7. Context Document (Complex Items Only)

For complex items or when input exceeds 500 words, create a companion context document:

```
${QUEUE_DIR}/assets/CONTEXT-${ID}-${SLUG}.md
```

This preserves the verbatim original request and links to extracted WRK items.

### 8. Sync to Target Repos

For each repo in `target_repos`, mirror the work item:

```bash
for REPO in ${TARGET_REPOS}; do
  REPO_QUEUE="${WORKSPACE_ROOT}/${REPO}/.claude/work-queue"
  # Create repo-local queue structure if needed
  mkdir -p "${REPO_QUEUE}/pending" "${REPO_QUEUE}/working" "${REPO_QUEUE}/archive"
  # Copy work item
  cp "${QUEUE_DIR}/pending/${FILENAME}" "${REPO_QUEUE}/pending/${FILENAME}"
  # Initialize or update repo-local state.yaml
done
```

Update the work item's `synced_to` field in both master and local copies:

```yaml
synced_to:
  - achantas-data
```

### 9. Confirm to User

Output a summary:

```
Created WRK-001: Fix login redirect
  Priority: medium | Complexity: simple | Repo: aceengineer-website
  File: .claude/work-queue/pending/WRK-001-fix-login-redirect.md
```

For multi-item captures:
```
Created 3 work items:
  WRK-001: Fix login redirect (simple, aceengineer-website)
  WRK-002: Add dark mode toggle (medium, aceengineer-website)
  WRK-003: Update footer links (simple, aceengineer-website)
```

## Error Handling

- If `next-id.sh` fails, fall back to timestamp-based ID: `WRK-YYYYMMDD-HHMMSS`
- If queue directory doesn't exist, create it with full structure
- If duplicate found, prompt user for action (skip, create anyway, update existing)

## State Updates

After successful capture:
- Increment counter in `state.yaml`
- Log capture event with timestamp
- Regenerate index: `python .claude/work-queue/scripts/generate-index.py`
