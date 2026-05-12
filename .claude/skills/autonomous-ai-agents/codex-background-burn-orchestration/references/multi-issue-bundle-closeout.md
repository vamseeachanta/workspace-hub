# Multi-issue Codex bundle closeout

Use this reference when deliberately burning Codex capacity over a short window and grouping multiple approved issues from the same repository into one isolated lane.

## When bundling is appropriate

Bundle issues only when all are true:
- Same repository and same base branch.
- Each issue is open and `status:plan-approved` or explicitly authorized for prep/blocker-only work.
- The work shares setup/validation cost, e.g. CI dependency repair + smoke tests + bounded migration in one package.
- The prompt requires per-issue commit/comment/closure decisions, not a single vague "finish everything" outcome.
- A partial result can be cleanly reported without pretending the whole bundle is complete.

Avoid bundling when issues have different risk classes, need different reviewers, touch unrelated product decisions, or one blocked issue could cause Codex to abandon otherwise closable work.

## Prompt contract for bundled lanes

Require Codex to:
1. Verify live issue state for every issue before editing.
2. Keep changes scoped by issue and make separate commits where practical.
3. Run the shared validation once after the bundle and any narrow per-issue tests before closing.
4. For each issue, choose exactly one terminal state:
   - landed + pushed + evidence comment + close, or
   - blocker evidence comment + leave open.
5. Never close a blocked issue just because another issue in the bundle succeeded.
6. Report token usage, branch, commit(s), and clean-state proof.

## Controller closeout checklist

After the Codex process exits:
- Inspect the Codex transcript for claimed completions, blockers, and token usage.
- Run `git status --short` in the worktree and verify the pushed branch/commits.
- Cross-check each issue with `gh issue view --json state,labels,comments`.
- Remove temporary `status:working` labels from issues that are closed or explicitly parked as blocked.
- Keep the worktree/branch until the user accepts the bundle summary or cleanup is explicitly safe; if preserving evidence, say so.

## Useful outcome shape

Report a table with repo, branch, Codex tokens, outcome, closed issues, open blockers, commit SHAs, and verification evidence. This keeps burn accounting separate from issue-completion accounting.
