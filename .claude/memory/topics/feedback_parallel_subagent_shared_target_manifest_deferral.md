> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-16
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_parallel_subagent_shared_target_manifest_deferral.md

---
name: feedback-parallel-subagent-shared-target-manifest-deferral
description: "When dispatching parallel write-only subagents that need to edit shared cross-link / index / log files, partition into unique-target (subagent edits directly) vs shared-target (subagent emits old_string+new_string deltas in YAML manifest, main session applies in deterministic order). Avoids last-write-wins race without serializing the whole authoring phase."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 58f6d77d-d489-489a-8a6f-d4407be06c12
---

When two or more parallel write-only subagents both need to insert content into the same shared file (cross-link target, index, log), DO NOT let them Edit it directly in parallel. Partition each subagent's write surface into:

- **Unique-target files** — written directly via `Write` / `Edit` tools (no collision possible)
- **Shared-target files** — subagent emits `target` + `old_string` (3-8 lines unique-identifying context) + `new_string` (the same old_string with new section appended) in YAML `shared_cross_link_deltas` block of its manifest. Main session applies these in Phase C with controlled per-issue ordering, and may need to re-anchor or re-locate insertions across the second subagent's deltas (because the first subagent's edits modify the file state the second subagent's `old_string` referenced).

**Why:** `Edit`'s `old_string`-find is non-transactional across subagent process boundaries. Two parallel subagents that each Read a file (state v1), then Edit at different times, will both succeed only if their `old_string` anchors don't overlap or interfere. With same anchor (e.g., both want to insert before `## Standards anchor`), the second subagent's `old_string` no longer matches v1 once the first commits its edit. Result: silent edit-skip or section landing in wrong location.

**How to apply:**

1. In subagent dispatch prompt, list explicit `Files YOU MUST WRITE` (unique to this subagent) vs `Files you MUST NOT WRITE (deferred to main session due to parallel-subagent collision)`
2. For deferred files, instruct: "emit the proposed section text in your manifest as `shared_cross_link_deltas` with `target`, `old_string`, `new_string` keys"
3. Subagent runs validation gates (tests, manual constraint checks) BEFORE returning manifest — main session trusts the gates passed against the unique-target files; shared-target deltas go into a re-validation pass after main applies
4. Main session: (a) `ls`-verify all subagent-claimed files on disk per [[feedback_subagent_write_phantom]]; (b) apply each subagent's shared-target deltas in Phase C with judgment (re-anchor as needed if second subagent's `old_string` was made stale by first subagent's edit); (c) re-run validation; (d) commit each issue atomically with its own `Closes #NN` trailer
5. Each shared-target file may be edited TWICE per session (once per commit) to keep the per-issue commit story atomic

**Known pitfalls:**

- Subagent-emitted `old_string` anchors can cause structural violations (e.g., H2 inserted between H3 subsections of a parent H2) — main session should structurally validate Edit deltas before apply, not blind-apply
- The pattern adds main-session integration overhead; reserve for I/O-bound authoring work (wiki page authoring) where parallelization payoff exceeds the integration cost
- Do not attempt with >2 parallel subagents — shared-target collision-management overhead grows quadratically; 3+ subagents should run sequentially

**Pilot reference (LIVE — 2026-05-15):** llm-wiki PE Phase 2 sub-issues [#82](https://github.com/vamseeachanta/llm-wiki/issues/82) (sand control) + [#83](https://github.com/vamseeachanta/llm-wiki/issues/83) (multi-zone & smart completions) authored in parallel from a single Claude Code session; commits [`5bc269fb`](https://github.com/vamseeachanta/llm-wiki/commit/5bc269fb) + [`863c7e96`](https://github.com/vamseeachanta/llm-wiki/commit/863c7e96). Total wall-clock ~30 min vs estimated 4-5 hours sequential. Five shared-target files (perforating.md, perforation-strategy.md, ESP, index, log) edited TWICE — once per commit — without any race or conflict. See exit handoff `docs/session-handoffs/2026-05-15-issues-82-83-sand-control-multi-zone-exit.md` for full pattern walkthrough.

**Related:**
- [[feedback_parallel_agent_write_only_pattern]] — base pattern this extends (subagents write, main commits; doesn't address shared-target collision)
- [[feedback_multi_agent_commit_serialization]] — umbrella git-lock-serialization principle
- [[feedback_subagent_write_phantom]] — main session must `ls` before trusting subagent reports
- [[feedback_parallel_gh_issue_create_reverses_numbers]] — sister-pattern for GitHub issue-creation race
