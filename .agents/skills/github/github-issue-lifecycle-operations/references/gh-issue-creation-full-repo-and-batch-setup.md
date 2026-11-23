# Archived Skill: `gh-issue-creation-full-repo-and-batch-setup`

Original path: `/home/vamsee/.hermes/skills/development/gh-issue-creation-full-repo-and-batch-setup`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/development/gh-issue-creation-full-repo-and-batch-setup`
Consolidation date: 2026-04-29

---

---
name: gh-issue-creation-full-repo-and-batch-setup
description: Create multiple related GitHub issues safely by resolving full OWNER/REPO, checking duplicates and labels first, and verifying each created issue.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# GitHub issue creation: full repo resolution + batch setup

Use when asked to add one or more issues to a GitHub repo, especially when the user gives only a short repo name and wants several related issues created quickly.

## Why this exists

Two practical gotchas came up in live use:
1. `gh ... --repo` requires the full `OWNER/REPO` form, not just the repo name.
2. For multi-issue requests, it is safer to draft structured body files, create the issues, then immediately verify titles, URLs, labels, and body content rather than assuming creation succeeded exactly as intended.

## Workflow

1. Resolve the repository identity first.
   - If the user gives only `repo-name`, run:
     - `gh repo view repo-name --json nameWithOwner,url,description`
   - Then use the returned `OWNER/REPO` string for all subsequent commands.

2. Check for likely duplicates before creating anything.
   - Search issue titles/bodies with key terms from the request.
   - Example:
     - `gh issue list --repo OWNER/REPO --state all --limit 100 --search 'keyword1 OR keyword2 OR keyword3'`

3. Inspect available labels.
   - Example:
     - `gh label list --repo OWNER/REPO --limit 200`
   - Reuse the closest existing labels instead of inventing new ones unless explicitly asked.

4. Draft each issue body in a separate temp markdown file.
   - Include:
     - objective
     - scope / questions to answer
     - deliverables
     - constraints / framing
   - This avoids shell quoting problems and makes edits easy.

5. Create the issues.
   - Example:
     - `gh issue create --repo OWNER/REPO --title '...' --body-file /tmp/file.md --label enhancement`

6. If one issue is the umbrella/meta issue, edit it after creation to link the child issue numbers.
   - This is often easier than guessing future issue numbers ahead of time.

7. If you need to post a follow-up comment linking the newly created issues back to a parent/umbrella issue, resolve the issue numbers first and only then write/post the comment body.
   - Safe pattern:
     1. create the issues and capture their numeric IDs
     2. write the comment/body file with the real issue numbers already substituted
     3. post with `--body-file`
   - Do not leave literal placeholders like `#${NEW_NUM}` in the file you send to `gh issue comment`.
   - If a placeholder leaks into a posted comment, immediately add a correction comment with the real issue numbers.

7. Verify every created issue immediately.
   - Use:
     - `gh issue view N --repo OWNER/REPO --json number,title,url,labels,body`
   - Confirm:
     - title matches intent
     - correct labels applied
     - body rendered correctly
     - URLs/issue numbers recorded

8. When posting follow-up comments that mention newly created issue numbers, render placeholders before posting.
   - Do NOT leave shell placeholders like `#${NEW_NUM}` inside a heredoc/body file and assume later interpolation will happen automatically.
   - Safe pattern:
     - create the new issue
     - capture the numeric id
     - write the final body file with the concrete number already substituted
     - then post with `gh issue comment --body-file ...`
   - If a placeholder accidentally lands in a comment, immediately post a correction comment with the exact issue numbers.

## Critical gotcha


`gh --repo` does NOT accept a bare repo name.

Incorrect:
```bash
gh issue list --repo achantas-data
```

Typical failure:
```text
expected the "[HOST/]OWNER/REPO" format
```

Correct:
```bash
gh issue list --repo vamseeachanta/achantas-data
```

## Good fit

- user says "add issues to repo X"
- repo may not be cloned locally
- need to create multiple related research/planning issues
- want fast, low-risk GitHub issue setup with verification

## Verification checklist

- repo resolved to full `OWNER/REPO`
- duplicate search run
- labels inspected
- issue bodies stored in files
- all issue URLs captured
- umbrella issue updated with child references if applicable
- final `gh issue view` verification performed
