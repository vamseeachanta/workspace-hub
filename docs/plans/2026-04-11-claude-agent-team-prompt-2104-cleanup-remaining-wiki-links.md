# Claude agent-team prompt: #2104 cleanup — remaining wiki architecture links

Use this prompt as a single self-contained handoff to Claude Code for a tiny cleanup follow-up.

---

We are in `/mnt/local-analysis/workspace-hub`.

You are Claude Code operating as a focused cleanup agent.
Do not ask the user any questions.

Context:
- Issue #2104 was implemented and closed.
- Main implementation commit: `b7a4b4885`
- Residual known gap: two wiki `CLAUDE.md` files contain uncommitted architecture-context additions in the working tree and were not included in the implementation commit.
- This run should ONLY clean up those two files and post a brief follow-up comment on the closed issue.

Issue context:
- Issue: #2104 https://github.com/vamseeachanta/workspace-hub/issues/2104
- Approval marker already exists: `.planning/plan-approved/2104.md`
- The issue is closed; do NOT reopen unless absolutely necessary. A brief follow-up comment on the closed issue is acceptable.

Owned paths for this cleanup ONLY:
- `knowledge/wikis/marine-engineering/CLAUDE.md`
- `knowledge/wikis/naval-architecture/CLAUDE.md`

Read-only context:
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`
- `docs/plans/2026-04-11-issue-2104-canonical-entry-points-for-ecosystem-intelligence.md`
- GitHub comments on #2104

Forbidden paths:
- every other path in the repo
- do not modify docs, tests, scripts, config, or other wiki files
- do not touch unrelated dirty files already in the worktree

Critical git safety rules:
- First inspect `git status --short`.
- Stage ONLY the two owned paths above.
- Never use `git add .` or broad globs.
- If either file does not contain the intended architecture-context link already, add only the minimal one-line change needed.
- If the worktree state for those files is ambiguous, stop and report clearly.

Success condition:
- Ensure both files contain the parent operating-model cross-reference.
- Commit ONLY those two files.
- Push to `origin main`.
- Post a concise follow-up comment on #2104 explaining that the previously noted residual wiki links were landed in a cleanup commit.

Required verification:
1. Confirm `knowledge/wikis/marine-engineering/CLAUDE.md` contains the parent operating-model reference.
2. Confirm `knowledge/wikis/naval-architecture/CLAUDE.md` contains the parent operating-model reference.
3. Confirm only those two files are staged for the cleanup commit.

Commit message:
- `docs(intelligence): add remaining wiki architecture links for #2104`

GitHub follow-up comment content:
- mention the cleanup commit hash
- say the remaining two wiki architecture links have now been landed
- do not reopen the issue unless required by repo policy

Final return format:
1. What changed
2. Verification performed
3. Exact files committed
4. GitHub comment URL
5. Whether issue was reopened (expected: no)
6. Residual risks or blockers
