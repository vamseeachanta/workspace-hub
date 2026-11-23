# Archived Skill: `github-issue-label-existence-audit`

Original path: `/home/vamsee/.hermes/skills/github/github-issue-label-existence-audit`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/github/github-issue-label-existence-audit`
Consolidation date: 2026-04-29

---

---
name: github-issue-label-existence-audit
description: Prevent GitHub issue creation failures by auditing exact label existence, duplicate titles, and partial-create risk before calling gh issue create.
version: 1.0.0
author: Hermes Agent
category: github
tags: [github, issues, labels, triage, gh]
---

# GitHub Issue Label Existence Audit

Use when drafting or creating GitHub issues with `gh issue create`, especially in repos with inconsistent label taxonomies.

## Why
A plausible label can still be absent in the target repo. In live use, issue creation failed because labels assumed from prior inspection or other repos (`tests`, `area:ecosystem-sync`, `parsing`, `releases`) were not actually present in `vamseeachanta/workspace-hub`. The safe path is to verify exact label existence before creation.

## Workflow
1. Confirm target repo explicitly.
   - Example: `gh repo view <owner/repo>` or inspect `git remote -v`.

2. Verify GitHub auth before side effects.
   - `gh auth status`

3. Audit labels in the target repo.
   - `gh label list --repo <owner/repo>`
   - For every planned label, do an exact-match check. Do not rely on memory or on labels from another repo.

4. Search for duplicates before create.
   - Use both broad keyword search and exact-title search:
   - `gh issue list --repo <owner/repo> --state all --search 'keyword1 OR keyword2'`
   - `gh issue list --repo <owner/repo> --state all --search '"Exact proposed title"'`

5. Prepare body files first.
   - Use `--body-file` instead of inline multiline shell strings.

6. Rewrite labels to only existing repo labels before creation.
   - If a label is missing, either:
     - replace it with the closest existing taxonomy label, or
     - omit it, or
     - create the label first only if that is explicitly in scope.

7. Create issues one by one, not as a blind batch, when taxonomy confidence is low.
   - This localizes failures and makes verification easier.

8. If `gh issue create` fails, verify whether GitHub created nothing or partially created an issue.
   - Re-run exact-title search immediately.
   - Only retry after correcting labels or other failing inputs.

9. Verify each created issue.
   - `gh issue view <url-or-number> --repo <owner/repo> --json number,title,labels,url`

10. Update any local helper scripts after live findings.
   - If real execution disproves your assumed label set, patch the scripts/docs immediately so the next operator does not repeat the failure.

## Minimal command pattern
```bash
gh label list --repo <owner/repo>
gh issue list --repo <owner/repo> --state all --search '"Exact proposed title"'
gh issue create --repo <owner/repo> --title '...' --label bug --label priority:medium --body-file /tmp/issue.md
gh issue view <number-or-url> --repo <owner/repo> --json number,title,labels,url
```

## Practical lessons
- "Listed earlier" is not enough; verify exact labels right before creation.
- Repo taxonomies drift. Generic labels like `tests` may be absent even when they seem obvious.
- Failed label application does not mean an issue was created; confirm before retrying.
- After live issue creation, reflect the corrected taxonomy in command bundles and operator docs immediately.
