# Issue Closeout Handoff Pattern

Use when an llm-wiki issue has passed substantive validation but the session cannot safely finish commit/push/comment/close.

## When to write a handoff

Write a repo-tracked handoff before ending if any of these are true:

- Tests and adversarial/legal validation passed, but implementation files remain uncommitted.
- `HEAD` and `origin/main` are synced for a handoff commit, but the implementation diff is still dirty.
- The GitHub issue is still open and lacks the final evidence comment.
- There is an untracked planning or scratch directory whose fate must be decided on restart.

## Minimum handoff contents

Capture:

1. **Artifact path** — where the handoff is saved.
2. **Commit and push evidence** — current `HEAD`, `origin/main`, and ahead/behind state for the handoff commit.
3. **Validation evidence** — exact pass/fail summaries for tests, graph/schema validators, legal/public-safety scans, and adversarial reruns.
4. **Dirty-state inventory** — modified and untracked files that remain intentionally preserved.
5. **Issue state** — whether the issue is open/closed, labels applied or not applied, and whether a closeout comment was posted.
6. **Restart checkpoint** — ordered next actions: inspect diff, decide scratch artifacts, stage intended files, commit/push, verify sync, comment/close issue.

## Example restart checklist

```text
1. Inspect final implementation diff.
2. Decide whether scratch planning files stay local-only or are summarized under docs.
3. Stage intended implementation files.
4. Commit and push.
5. Verify HEAD == origin/main and ahead/behind is 0/0.
6. Comment with evidence and close the GitHub issue.
```

## Operator rule

Do not claim issue closeout if the issue is still open or implementation files are still dirty. Say the repo is synced only for the handoff commit, then name the preserved dirty state explicitly.
