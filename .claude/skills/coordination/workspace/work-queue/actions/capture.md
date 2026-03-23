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

### 5. Generate ID (GitHub-first, with offline fallback)

```bash
# gh-next-id.sh creates a GitHub issue and returns its number as the WRK ID.
# If gh is unavailable, it returns a LOCAL-YYYYMMDD-HHMMSS-hostname fallback.
GH_OUTPUT=$(bash "${WORKSPACE_ROOT}/scripts/work-queue/gh-next-id.sh" --title "$TITLE")
NEXT_ID=$(echo "$GH_OUTPUT" | sed -n '1p')
ISSUE_URL=$(echo "$GH_OUTPUT" | sed -n '2p')

FILENAME="WRK-${NEXT_ID}.md"
```

> **Deprecation notice**: `next-id.sh` (machine-range-based numbering) is deprecated.
> New captures MUST use `gh-next-id.sh`. The old script now logs a warning and
> delegates to `gh-next-id.sh`.

### 6. Create Work Item File

Write to `${QUEUE_DIR}/pending/${FILENAME}` using the appropriate template:
- simple/medium -> `work-item-simple.md` template
- complex -> `work-item-complex.md` template

Fill in all frontmatter fields. Set `created_at` to current ISO 8601 timestamp.

If the ID is a LOCAL fallback (starts with `LOCAL-`), add `provisional_id: true` to frontmatter.
The `github_issue_ref` is set at creation time (from `ISSUE_URL`) — no post-hoc step needed.

### 7. Store GitHub Issue Reference

The GitHub issue was already created by `gh-next-id.sh` in step 5. Store the reference:

```bash
# ISSUE_URL is already available from step 5
# Add github_issue_ref to frontmatter
if [[ "$ISSUE_URL" != "offline" ]]; then
  # Issue created — store ref directly in frontmatter
  # github_issue_ref: https://github.com/vamseeachanta/workspace-hub/issues/NNN

  # Update issue body with full WRK content
  uv run --no-project python "${WORKSPACE_ROOT}/scripts/knowledge/update-github-issue.py" \
    "WRK-${NEXT_ID}" --update
fi
```

If `gh` was unavailable (offline capture), the item gets a `WRK-LOCAL-*` ID with
`provisional_id: true`. Run `promote-local-ids.sh` when connectivity returns to
promote to real GitHub-derived IDs.

### 8. Context Document (Complex Items Only)

For complex items or when input exceeds 500 words, create a companion context document:

```
${QUEUE_DIR}/assets/CONTEXT-${ID}-${SLUG}.md
```

This preserves the verbatim original request and links to extracted WRK items.

### 9. Sync to Target Repos

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

### 10. Confirm to User

Output a summary:

```
Created WRK-001: Fix login redirect
  Priority: medium | Complexity: simple | Repo: aceengineer-website
  File: .claude/work-queue/pending/WRK-001-fix-login-redirect.md
  Issue: https://github.com/<owner>/<repo>/issues/NNN
```

For multi-item captures:
```
Created 3 work items:
  WRK-001: Fix login redirect (simple, aceengineer-website)
  WRK-002: Add dark mode toggle (medium, aceengineer-website)
  WRK-003: Update footer links (simple, aceengineer-website)
```

## Error Handling

- If `gh-next-id.sh` returns a LOCAL ID (gh unavailable), capture proceeds with `WRK-LOCAL-*` ID and `provisional_id: true`. Run `promote-local-ids.sh` later.
- If queue directory doesn't exist, create it with full structure
- If duplicate found, prompt user for action (skip, create anyway, update existing)

## State Updates

After successful capture:
- Increment counter in `state.yaml`
- Log capture event with timestamp
- Regenerate index: `python .claude/work-queue/scripts/generate-index.py`
