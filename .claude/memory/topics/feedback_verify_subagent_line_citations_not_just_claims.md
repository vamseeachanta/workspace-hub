> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-29
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_verify_subagent_line_citations_not_just_claims.md

---
name: feedback_verify_subagent_line_citations_not_just_claims
description: "When relaying subagent findings, re-check the file:line coordinates too — not just the substance — before asserting they were verified"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d17618ea-b9fc-4295-b5b2-d388c9417153
  modified: 2026-07-26T03:49:33.386Z
---

When a subagent reports a defect as `path/file.py:NNN-MMM`, verifying **the claim** is not the
same as verifying **the coordinates**. Check both before repeating the citation, and never write
"every cited line was re-verified" unless each line number was individually opened.

**Why:** live incident 2026-07-25, digitalmodel OrcaFlex review. Five review agents reported
findings; the main session verified the *substance* of the load-bearing ones by reading the code
(the relabel at `orcawave_runner.py:739-742` was real, `tonnes_to_kg` really was uncalled there)
and then carried the *surrounding* line numbers into a plan verbatim. Three were wrong:
`:661-664` was cited as the Hz→rad/s conversion but is a `@staticmethod` docstring; the real sites
are `:686`, `:687`, `:710`, `:719`. The plan's provenance section asserted every line had been
re-verified. Adversarial review caught it and issued NON-APPROVE partly on that basis.

The conclusions built on those lines were still correct — the frequency/RAO handling *is* sound —
so nothing downstream was wrong. But a plan that misplaces its own evidence is not auditable, and
in this ecosystem plans are the artifact reviewers act on.

**How to apply:**
- Verifying substance = "does this defect exist?". Verifying coordinates = "is it *here*?".
  Both are required before a citation goes into a plan, an issue, or a report.
- Cheapest reliable check: `git show origin/main:<path> | sed -n 'N,Mp'` for each range, in one
  batched command. Do it while writing the document, not after.
- Line numbers drift between the branch a subagent read and `origin/main`. Agents working in a
  stale checkout will report stale coordinates that are locally true and remotely wrong — see
  [[feedback_verify_generated_state_against_origin_not_working_copy]].
- If a range cannot be cheaply confirmed, cite the **symbol** (`def process_summary_by_model_and_cfg`)
  rather than a line number. A symbol survives drift; a line number does not.
- Only claim "re-verified" for what was actually opened. Scope the provenance sentence to the
  truth: "the defect claims were re-verified; line coordinates are as reported by the review agents."

**Related incident from the same session — the other half of the same discipline:** an agent's
*conclusion* was also wrong (it claimed a units bug caused a −0.855 benchmark correlation; the
consensus path is RAO-only and `np.corrcoef` is scale-invariant, so a 1000× factor is provably
invisible to it). That claim had already been published to two GitHub issues before adversarial
review caught it, requiring a public correction. Same root discipline: adversarially review the
plan *before* acting on it, per [[feedback_adversarial_review_stance]].

See [[project_orcaflex_ecosystem_review_2026_07_25]].
