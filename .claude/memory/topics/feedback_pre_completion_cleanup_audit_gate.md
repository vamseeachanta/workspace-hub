> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-22
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_pre_completion_cleanup_audit_gate.md

---
name: feedback-pre-completion-cleanup-audit-gate
description: "Run pre-completion-cleanup-audit skill before reporting \"all done\"; surface residue in CLEAN/EXPECTED/UNEXPECTED buckets; never relay completion with UNEXPECTED residue present"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: cc26971a-8770-49db-81b9-ae41eb299110
---

Before claiming a task complete ("all done", "task complete", "ready for review",
or handing back to user/orchestrator), invoke the audit defined in
`.claude/skills/coordination/pre-completion-cleanup-audit/SKILL.md`.

**Why:** Sessions repeatedly accumulate sibling-repo state, orphan stashes,
`/tmp/` scratch, and abandoned lock/trash directories that force later
heavyweight remediation passes. Today's `/mnt/local-analysis/` cleanup reclaimed
~78 MB across two consecutive user-prompted rounds that should have been
incremental gates per sub-task — both rounds surfaced residue from prior
session-completions that shipped "all done" without an audit. Hermes is the
orchestrator best positioned to enforce this; standalone agents must do it
themselves until Hermes flow-through ships (tracked at
[#2750](https://github.com/vamseeachanta/workspace-hub/issues/2750)).

**How to apply:**

1. After completing the requested work, before composing the final status
   message, run the 5-step audit (repo working-tree state, sibling-of-canonical
   state, `/tmp/` scratch, lock/trash-stage state, session-doc state).
2. Classify findings in three buckets:
   - **CLEAN**: no residue → proceed to "all done"
   - **EXPECTED**: residue traces to the task (e.g., new handoff doc not yet
     committed) → surface explicitly in the completion message
   - **UNEXPECTED**: residue doesn't trace to the task → BLOCK completion;
     resolve via commit / archive / delete / escalate before relaying done
3. Never relay "all done" with UNEXPECTED residue present.

**Do NOT apply when:** trivial single-tool-call tasks ("show me the diff");
mid-task checkpoints (only run before completion, not between steps); inside
subagent contexts that report back to a main session (main session runs once,
not N times).

Related:
- Skill: `.claude/skills/coordination/pre-completion-cleanup-audit/SKILL.md`
- Rule (cross-provider): `config/agents/SHARED_SOUL.md` Must-Fire Rules block
- Heavyweight downstream skill: [[mnt-analysis-cleanup]]
- Hermes integration tracker: [#2750](https://github.com/vamseeachanta/workspace-hub/issues/2750)
- Adjacent: [[feedback_hermes_session_grep_journal_vs_active]] (filed earlier same session)
