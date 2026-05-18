---
name: post-commit-autosync-defeats-test-gate
description: "Plans with push-after-test gating must use SKIP_PUSH=1 git commit, or the post-commit auto-sync hook (WRK-1141) silently pushes the commit before the empirical test can run. Companion to feedback_autosync_silent_pusher."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5db7e4c7-4f76-4d7d-86bc-4906d339cf16
---

**Plans that include a "push only on PASS" empirical-test gate MUST use `SKIP_PUSH=1 git commit ...` for every local-only commit, or the workspace-hub post-commit auto-sync hook (`.git/hooks/post-commit`, ref WRK-1141) silently pushes the commit to origin before the test can run, defeating the gate.**

**Why:** On 2026-05-16 evening, executing #2725 Phase 1 (CLAUDE.md @file import), the r3-absorbed plan explicitly mandated push-after-test sequencing per Claude r1 #5: edit → commit local → empirical fresh-session test → push only on PASS. The implementing session ran `git commit ... -- CLAUDE.md` without `SKIP_PUSH=1`. The post-commit hook auto-pushed the commit (`22aa9fde9`) to origin immediately. The empirical fresh-session test couldn't be the gate anymore — the unverified @import was already on remote. Phases 2-4 were caught and committed with `SKIP_PUSH=1`, but Phase 1 had already leaked.

The hook respects an explicit opt-out (`SKIP_PUSH=1`); the plan didn't specify the mechanism. The implementing agent didn't remember the auto-sync behavior until the first commit had already shipped. Mitigation arrived a commit too late.

Net risk in this specific case was low (the @import line is inert text if `@file` doesn't resolve in Claude Code), but the workflow-gate violation was real and structural — the same plan-shape on a destructive change (e.g., bash-script rewrite, schema migration) would land broken state on origin/main before verification.

**How to apply:**

1. **At plan time**: any plan pseudocode that says "push only on PASS", "commit locally", or otherwise gates push on a test must spell out `SKIP_PUSH=1 git commit` (not bare `git commit`) for every local-only commit. Reviewers should flag bare `git commit` in a push-gated phase as a finding.

2. **At impl time**: before the FIRST commit of a phase with a push-gate, set `export SKIP_PUSH=1` at the shell session level to defeat the hook for all subsequent commits in that phase. Unset only after the empirical test passes and the explicit push is intended.

3. **Recovery if the gate is defeated**: if a commit auto-pushed before verification, surface immediately to the user; the recovery options depend on the change's reversibility:
   - **Reversible/inert change** (text-only directive, doc, comment): continue with `SKIP_PUSH=1` for remaining phases; document the leak in the closeout; revert via new commit only if empirical test fails.
   - **Destructive change** (script behavior change, schema, removed file): `git revert <sha>` immediately, push the revert, then redo properly with `SKIP_PUSH=1`.

4. **Architectural fix candidates** for follow-on consideration:
   - Make the post-commit hook check for a sentinel file (`.skip-push` in `.git/`) or commit-trailer (`Skip-Push: true`) instead of (or in addition to) the env var — env vars are easy to forget in interactive sessions.
   - Add a `# Push gate` comment block to PLAN.md templates that lists the env-var workaround explicitly.

**Do NOT apply when:** the plan has no push-after-test gate (most plans push every commit immediately and that's correct). Don't blanket-disable auto-sync; it's the right default for most work.

**Related:** [[feedback_autosync_silent_pusher]] is the broader observation; this memory is the specific corollary for push-after-test workflows. [[feedback_mock_vs_live_invocation_divergence]] explains why empirical fresh-session tests are non-skippable; this memory explains why their gate can leak.
