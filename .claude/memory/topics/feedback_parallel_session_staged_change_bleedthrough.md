> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-22
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_parallel_session_staged_change_bleedthrough.md

---
name: parallel-session-staged-change-bleedthrough
description: "When committing in a checkout shared with parallel agent sessions (Hermes lanes, Claude Code subagents, cron jobs), `git add <single-path>` is additive — the index may already hold staged changes from another agent. `git commit` will sweep them in. Always run `git diff --cached --name-only` BEFORE `git commit` and verify staged set matches what your `git add` named."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 76ab2ab3-ba1e-4c05-b984-b73d97dafefc
---

In any workspace where parallel sessions can mutate the working tree or stage changes (workspace-hub default ace-linux-1 setup with Hermes lanes + Claude Code subagents + cron jobs), `git add <specific-path>` is additive against the existing index — it does NOT clear other staged changes. `git commit` then captures the entire index state. Single-path adds in shared checkouts can therefore land surprise file mutations from any other session that staged but didn't commit.

**Why:** On 2026-05-15 close-out of the marker-gate + skill-curation session, a `git add docs/sessions/2026-05-14-...md` followed by `git commit -m "docs(sessions): ..."` produced commit `56983fbbc` containing the intended doc-add PLUS five already-staged `email/gmail-*/SKILL.md` file deletes. The deletes had been pre-staged by a parallel session (likely a Hermes lane working on issue #2528 "retire 6 deprecated email skills"). By coincidence the deletions aligned with the planned cleanup target — but the commit attribution was wrong (no link to #2528, no plan-approval marker, bundled into an unrelated docs commit). Auto-sync silently pushed the bundle to origin/main before the bleed-through was detected. Recovery was limited to documenting the incident on #2528 and ticking the relevant acceptance-criteria boxes; reverting would have un-done legitimate cleanup. Memory feedback `feedback_autostash_replay_after_checkout_b` covers the autostash variant of the same root cause; this entry covers the parallel-session-stages variant.

**How to apply:**

1. **BEFORE every `git commit` in workspace-hub**, even when only one path was just `git add`-ed, run:
   ```
   git diff --cached --name-only
   ```
   The output should match your intent EXACTLY. If it shows additional paths you did not `git add`, surface and resolve before committing.
2. If the index has unexpected staged changes:
   - **If they are clearly from a parallel session and clearly aligned with that session's intent**, unstage with `git restore --staged <path>` so the parallel session can commit them under its own attribution.
   - **If they look like accidental drift**, unstage and restore with `git restore <path>` (working-tree restore from HEAD).
3. After commit but before push: re-check via `git show --stat HEAD` that only intended files landed. If auto-sync has not yet pushed, you can `git reset --soft HEAD~1` and recommit narrowly.
4. After auto-sync push (irrecoverable without force-push): document on the relevant issue, do NOT revert if the bleed-through happens to be aligned cleanup.
5. Combine with [[feedback_autostash_replay_after_checkout_b]] (autostash variant) and [[feedback_multi_agent_commit_serialization]] (commit-lock variant) — three distinct mechanisms by which parallel-session state can poison your commit; all three demand a pre-commit `--cached --name-only` verification step.
