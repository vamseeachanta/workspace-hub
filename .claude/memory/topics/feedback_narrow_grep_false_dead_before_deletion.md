> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-10
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_narrow_grep_false_dead_before_deletion.md

---
name: feedback_narrow_grep_false_dead_before_deletion
description: "A scope-limited grep can return a confident false-\"dead\" reading and nearly greenlight deleting a LIVE subsystem — always re-grep wide (adversarially) before any archival/deletion."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f7fadb7c-8e14-45c9-8014-2cbd970bbd6d
---

2026-06-15 (#3103, epic #3078 follow-up): proposed archiving the entire `.claude/agent-library/` (46 files) as "dead claude-flow boilerplate with no live consumer." My evidence was a grep for `agent-library` scoped to `.claude/skills .claude/hooks .github .git/hooks config` — which returned EMPTY, so I concluded "no live consumer" and drafted a deletion plan. **The premise was false.** An adversarial reviewer re-grepped WIDE and found it is LIVE: 4 devops skills (`.claude/skills/operations/devops/*.md`) + the TDD workflow (`.claude/workflows/standard-development.yaml`) + `.claude/agent-skills-map.yaml` all load `@.claude/agent-library/...` agent defs, and `.claude/docs/workspace-structure.md:120` explicitly warns "HIGH RISK to rename — loaded by standard-development.yaml + 4 devops skills." Deleting it would have broken the TDD workflow + 4 skills.

**Why:** my grep missed `.claude/workflows/`, `.claude/agent-skills-map.yaml`, `.claude/skills/operations/devops/`, and `scripts/` because I hand-picked dirs/extensions. A scoped grep proves absence ONLY within its scope; "I grepped and found nothing" is exactly as trustworthy as the grep's breadth.

**How to apply (before ANY deletion/archival):**
- Grep the WHOLE repo for the target name (`grep -rI <name> .` minus `.git`/auto-gen state), not a hand-picked subset of dirs. Then narrow.
- Run an ADVERSARIAL reviewer whose explicit job is "prove this is still consumed" — its broad re-grep is the cheapest insurance against a catastrophic delete. This is why deletion plans require adversarial review at the plan stage (`feedback_adversarial_review_stance`).
- Check for an explicit guardrail file (here `.claude/docs/workspace-structure.md` HIGH-RISK-to-rename table) before touching shared dirs.
- Distinguish a dead RUNNER from live DATA: the claude-flow orchestrator *scripts* (agent_orchestrator.sh etc.) were genuinely dead and safe to delete (PR #3105), but the agent `.md` DEFINITIONS in the same family are live (loaded directly via @-refs). Same naming family ≠ same liveness.

Related: [[feedback_subagent_acceptance_metric_drives_signal_deletion]], [[feedback_parallel_agents_shared_mutable_tool_path]], the "verify coverage assumptions empirically" SOUL rule.
