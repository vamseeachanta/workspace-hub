---
name: workflow-gatepass-no-bypass-rules
description: 'Sub-skill of workflow-gatepass: No-Bypass Rules.'
version: 1.0.6
category: workspace-hub
type: reference
scripts_exempt: true
---

# No-Bypass Rules

## No-Bypass Rules


- Stage 1 exit gate (`user-review-capture.yaml`) may not be bypassed; Route A may use
  `n/a: true` with non-empty `reason` field (`n/a_reason`). Route B/C: field required.
- No implementation before WRK item + plan + explicit WRK approval.
- No user-review acceptance unless the completed HTML was opened in the default browser.
- No stage-5 completion unless the interactive question-and-decision loop is
  captured in the plan evidence (including explicit tough-question outcomes).
- No stage-5 completion unless test/eval proposals were derived from available
  resource/document intelligence and reviewed with user disposition.
- No stage-5 completion unless `user-review-plan-draft.yaml` (or equivalent)
  captures tough questions, challenged assumptions, tradeoffs, and user test/eval
  additions from resource/document intelligence.
- No user-review completion (stages 5/7/17) unless the Gate-Pass Stage Status
  section was reviewed with the user (table + summary) and gaps were called out.
- No user-review acceptance unless relevant review artifacts are pushed to `origin`
  for distributed review (repo-local + remote visibility).
- No close without a per-WRK stage ledger in assets (`stage_evidence_ref`) covering stages 1-20.
- No close without gate evidence and `integrated_repo_tests` count in `[3,5]`.
- No archive when queue validation fails or merge/sync evidence is missing.
