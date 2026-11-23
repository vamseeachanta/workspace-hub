# Resume-after-compaction checklist for GitHub issue execution

Use when a GitHub issue execution session resumes after context compaction, a preserved task list, or a tool-call ceiling.

## Durable pattern

1. Treat preserved task lists as state hints, not proof of completion.
2. Rehydrate live state before continuing:
   - inspect the GitHub issue body/comments/labels;
   - inspect local repo status, branch/worktree, and relevant artifacts;
   - inspect the expected plan/artifact paths, but do not assume they exist.
3. If an expected plan/artifact path is missing, pivot to live issue comments and repo search as source of truth; record the missing path as a gap, not as failure of the whole task.
4. Continue from the first incomplete durable deliverable. For artifact-producing issues, produce/verify outputs before moving to review/commit/closeout.
5. When tool-call limits interrupt execution, final status must be evidence-bounded:
   - current task state;
   - exact files/commands inspected;
   - what remains unverified;
   - next executable checkpoint.
6. Never close or mark complete based only on restored todos or partial search evidence.

## Evidence format

Use concise status bullets:

- Current state
- Evidence
- Gap/blocker
- Next action

This prevents false closure after compaction and gives the next agent a deterministic restart point.
