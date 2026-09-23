> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-31
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_branch_landed_ask_the_forge_not_an_llm.md

---
name: feedback_branch_landed_ask_the_forge_not_an_llm
description: "To decide whether a branch's work already landed, query the merged-PR record with gh --head; never delegate it to an LLM diff read"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 37fedd46-6633-4600-93d5-75caac26f009
  modified: 2026-07-31T01:36:12.373Z
---

"Did this branch's work land?" is answered by `gh pr list -R <slug> --state merged --head <branch>
--json number,mergedAt`. A hit means a merged PR had that exact branch as its head — the work is in
main, and you get a PR number to cite. No hit, then fall back to ancestry / empty-diff tests.

**Why:** During the 2026-07-30 fleet sweep I told two agents to delegate this adjudication to Codex
as "token-heavy work". That was wrong on both counts. The worldenergydata agent's `codex exec` ran
~15 minutes, was killed by its own timeout, and wrote a 0-byte file; it then resolved all 33
ambiguous branches with one `gh` call each. The forge record is *cheaper* and *stronger* evidence
than a model reading diffs — it is a fact, not an inference, and it cannot hallucinate a merge.

**How to apply:** Reserve Codex/agy delegation for work that genuinely needs judgement over lots of
text (reviewing a large diff, adjudicating conflicting docs). Anything answerable by a `gh`/`git`
query is not token-heavy work — it is a lookup, and delegating it adds latency, a timeout risk, and
a hallucination surface. Ask first: "is there a deterministic query for this?" See
[[feedback_delegate_token_heavy_to_codex]] for what Codex IS right for, and
[[feedback_merge_is_not_done_until_branch_and_worktree_gone]] for why ancestry tests alone
under-report (squash-merge rewrites SHAs, so `--merged` never lists a squash-merged branch).
