# Golden-task baseline drift policy

Version: 1.0. Scope: synthetic offline corpus changes.
Format and scoring: [README.md](README.md).
Read budget: 8192 UTF-8 bytes; design basis: README, Design constants.

Baseline changes must preserve reproducible comparisons. A changed model response
alone is not evidence that the expected result should change.

## Revision history

| Revision | Date | Change and reason |
|---|---|---|
| Initial | 2026-10-25 | Define source-driven refresh and distinguish response drift from stale rules. |

## Classification

| Observation | Classification | Required action |
|---|---|---|
| Response changes, cited repository rule and task remain unchanged | Response drift | Keep the baseline; report failed groups and compare the raw structured responses. |
| Cited repository rule or task scope changes | Baseline staleness candidate | Inspect the changed rule and its authority; update the structured derivation only if justified. |
| Normalizer or rubric semantics change | Evaluation drift | Version the incompatible format and rerun all fixed examples before comparing results. |
| A complete task is unavailable because of truncation | Unavailable input | Preserve identity; request complete task material. Do not score a correctness result. |

The provider-owned versus repository-owned distinction follows
[Classify the Drift](../../../docs/standards/MODEL_RELEASE_UPGRADE_PLAYBOOK.md).
A provider improvement may satisfy the existing baseline without a refresh.
If the corpus itself is defective, correction is a repository-owned change;
do not mix provider configuration changes into that correction.

## Refresh transaction

- Retain the prior baseline in Git history and identify the prior revision in
  the change description. Do not silently overwrite an observation record or
  present synthetic results as live model results.
- Read the cited source at the recorded `rules_revision` and at the candidate
  revision. Record the changed requirement, source section and expected effect.
  A moved path or altered excerpt is a review trigger, not an automatic rewrite.
- Update affected `input.yaml`, `expected.yaml`, `meta.yaml` and class rubric
  consistently. Update `rules_revision` only after inspecting the cited rules.
  Keep the stable class/task identity unless the task's meaning changes.
- Re-derive independent test expectations and good/bad score sums from the
  cited rule and hand arithmetic. Never generate expected scores by running the
  evaluator under test. Preserve old examples where the semantics still apply.
- Run both focused suites using the README command. Resolve failures caused by
  the change and obtain the review required by
  [AI_REVIEW_ROUTING_POLICY.md](../../../docs/standards/AI_REVIEW_ROUTING_POLICY.md).
  The originating task authorizes implementation within its scope; a baseline,
  verdict or label does not independently authorize publication or deployment.
- Add a revision-history row stating what changed and why; preserve earlier
  rows. Record known limits and remaining review in the change description.

## Comparison record boundary

A future comparison must identify the corpus revision, format version,
normalization semantics, model identifier, complete-input status, budgets and
raw responses before interpreting a score delta. This corpus defines no storage
schema or runner behavior for those records. No automatic refresh, model calls,
live readiness threshold or production release decision is implemented here.

The lesson for later extensions is to pin response examples independently of the
baseline under test. Otherwise a weakened expected result can make its own
regression test pass without preserving the repository rule.
