> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-21
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
- Do not attempt with >2 parallel subagents in a single batch — shared-target collision-management overhead grows quadratically; for 3 sub-issues use the **two-batch + solo trailing** pattern instead (see below)

**Two-batch + solo trailing pattern (validated 4 epics — 2026-05-15 to 2026-05-16):** for sub-issue counts of 3, do NOT extend Batch 1 to 3 parallel subagents. Instead:

- **Batch 1**: 2 parallel subagents on 2 sub-issues (the 2 with most disjoint topic surfaces — typically the broader-foundational ones)
- **Batch 2**: 1 solo subagent on the remaining sub-issue (typically the one with the heaviest cross-link surface back to Batch 1 + prior phases — solo dispatch lets it cross-link the now-landed Batch 1 pages without forward-reference fragility)

This preserves the per-pair shared-target collision safety while extending parallelism beyond 2 sub-issues, AND positions the heaviest cross-link work where it benefits most from solo execution.

**Pilot reference (LIVE — 2026-05-15):** llm-wiki PE Phase 2 sub-issues [#82](https://github.com/vamseeachanta/llm-wiki/issues/82) (sand control) + [#83](https://github.com/vamseeachanta/llm-wiki/issues/83) (multi-zone & smart completions) authored in parallel from a single Claude Code session; commits [`5bc269fb`](https://github.com/vamseeachanta/llm-wiki/commit/5bc269fb) + [`863c7e96`](https://github.com/vamseeachanta/llm-wiki/commit/863c7e96). Total wall-clock ~30 min vs estimated 4-5 hours sequential. Five shared-target files (perforating.md, perforation-strategy.md, ESP, index, log) edited TWICE — once per commit — without any race or conflict. See exit handoff `docs/session-handoffs/2026-05-15-issues-82-83-sand-control-multi-zone-exit.md` for full pattern walkthrough.

**Scale validation (LIVE — 4 epics in a row, 2026-05-15 → 2026-05-16):** the two-batch + solo pattern has now shipped through every PE epic with 3 sub-issues:

- PE Phase 2 [#73](https://github.com/vamseeachanta/llm-wiki/issues/73) — Batch 1: #82 + #83 parallel; Batch 2 not applicable (only 2 sub-issues)
- PE Phase 3 [#74](https://github.com/vamseeachanta/llm-wiki/issues/74) — Batch 1: #84 + #85 parallel; Batch 2: #86 solo
- PE Phase 4 [#87](https://github.com/vamseeachanta/llm-wiki/issues/87) — Batch 1: #89 + #90 parallel; Batch 2: #91 solo
- PE Phase 5 [#92](https://github.com/vamseeachanta/llm-wiki/issues/92) — Batch 1: #93 + #94 parallel; Batch 2: #95 solo

The Batch 2 sub-issue in each epic was the highest-cross-link one (well integrity / surface handover — heavy backlinks into Batch 1). In Phase 5 specifically, the two Batch 1 subagents independently converged on the same calc-citation posture (doc-only metadata) WITHOUT inter-agent coordination — strong evidence that when subagents follow structural prompt guidance, posture-consistency emerges naturally and the main session doesn't need to enforce uniformity post-hoc.

PE wiki growth measured under the pattern: 0 pages (pre-Phase 1) → 93 pages (post-Phase 5), ~93 pages across 5 phases with 4 batched-parallel epics. The pattern is now durable beyond pilot status.

**Related:**
- [[feedback_parallel_agent_write_only_pattern]] — base pattern this extends (subagents write, main commits; doesn't address shared-target collision)
- [[feedback_multi_agent_commit_serialization]] — umbrella git-lock-serialization principle
- [[feedback_subagent_write_phantom]] — main session must `ls` before trusting subagent reports
- [[feedback_parallel_gh_issue_create_reverses_numbers]] — sister-pattern for GitHub issue-creation race
