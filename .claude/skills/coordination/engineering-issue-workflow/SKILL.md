---
name: engineering-issue-workflow
description: Engineering-specific discovery, qualification, implementation and verification for calculation, standards, solver and data-pipeline issues. Generic planning and authority follow the shared lifecycle.
metadata:
  category: coordination
  triggers:
    - When a GitHub issue with cat:engineering, cat:engineering-calculations, cat:engineering-methodology, or cat:data-pipeline is mentioned or assigned
    - When the user asks to implement any engineering calculation, offshore standard, metocean, OrcaFlex, or data-pipeline work
    - When any commit touches digitalmodel/, worldenergydata/, or assetutilities/
  version: 1.3.0
---

# Engineering Issue Workflow

## Shared lifecycle and ownership

Use `config/agents/SHARED_SOUL.md`, `docs/standards/HARD-STOP-POLICY.md` and
`.claude/skills/coordination/issue-planning-mode/SKILL.md` in workspace-hub for
planning, authorization, review and closeout. This skill adds engineering checks;
it does not duplicate the plan template or introduce another approval ceremony.

Classify actual effects, including engineering-basis changes. Proceed only within
independently established authority; substantial current plans and consequential
engineering actions require matching approval. Do not repeat approval for unchanged
scope or treat local markers, labels, handoffs or reviewer verdicts as authority.
The implementing agent never self-labels `status:plan-approved`.

Resolve each owning checkout from explicit context or verified workspace mapping.
`digitalmodel`, `worldenergydata` and `assetutilities` may be separate Git roots,
not nested folders. Run tests and Git operations in the verified owner; do not
commit another repository's outputs from the workspace-hub root. Check parallel
claims and serialize shared integration through the shared lifecycle.

## Engineering resource intelligence

- Locate existing implementations, constants, fixtures and predecessor workflows
  before designing another calculation. Use available search tools in the owner.
- Consult hub `data/document-index/standards-transfer-ledger.yaml` and
  `data/document-index/online-resource-registry.yaml`, then the applicable owner
  catalogs/manifests. Use indexed, bounded drive lookup for relevant source documents.
- Verify source access, edition, clause, units, extraction status and intended-use
  readiness. A registry status, portal entry or summary is not formula authority.
  Read current metadata and coverage gaps rather than assuming historical counts,
  field completeness or mounted-drive availability.
- Apply `docs/architecture/agent-data-handling-contract.md` and the calc-citation
  contract to source-qualified inputs and standards-derived constants. Preserve
  source rights, raw-evidence retention and licensed-original exclusions.
- If the user requests raw context preservation before coding, establish the
  authorized owner and retention route first. Preserve verified source references,
  source pages, concept anchors and extraction/comparison summaries as permitted;
  record anchors in the plan and issue within posting authority. Do not copy raw
  licensed/private payloads into a wiki merely because the old workflow did so.

## Engineering plan and implementation checks

Read [engineering calculation hardening](references/engineering-calculation-plan-hardening.md)
for relevant calculation plans and again before closeout. Its domain checks apply
within the shared scope/authority contract; historical examples do not expand work.

- State governing cases, assumptions, excluded physics and applicable criteria.
  Distinguish equal/opposite quantities; define force-line lever arms geometrically.
- Pin axes and physical sign conventions consistently in code, YAML, documentation
  and tests. Include absolute sign, identity, reversal and zero cases, not only
  symmetric/scaling tests that mirror the implementation.
- Name exact output artifacts, manifests, provenance/citation sidecars and charts.
  Honor YAML-configured names and chart subsets; reject empty sweeps before writers.
- Preserve public import/package-data behavior outside pytest path injection.
  Include upstream helper, wrapper and predecessor regression slices when reused,
  including OrcaFlex wrappers and solver/YAML integration paths when affected.
- Preserve subprocess environments; use robust module imports for monkeypatching.
  Distinguish assumptions from standards-derived inputs in provenance tests.

## TDD, validation and review

Write and run the failing tests before implementation; implement the bounded change,
then confirm the tests pass. Use the owning repository's supported `uv run` commands.
Run affected helper/wrapper regressions, relevant solver/artifact smoke checks and
required repository validation. Select additional tests by dependency coverage and
unresolved risk; do not repeatedly run an unchanged suite without new evidence.
Confirm test collection and counts are meaningful: runner failure or zero collected
tests is not success. Inspect failures instead of reporting an empty run as green.

Apply shared plan/code adversarial-review routing. Supply the current plan, exact
diff, test results, governing criteria and source limitations. Record actual provider
availability; never count unavailable review as passing. Resolve blocking findings
and bounded actionable defects, then rerun affected checks. Keep review artifacts
under `scripts/review/results/` with revision/context evidence; inspect current
records rather than infer that all work since a historical date is unreviewed.

## Continuation and closeout

Continue within verified scope while useful progress remains. If dependencies,
engineering assumptions, authority or acceptance criteria are unresolved, report the
specific blocker and preserve resumable evidence. Tool-call counts alone do not
require another permission request; observed loops or repeated failures require
reassessment under the existing session controls.

Verify the result against the governing case and current plan; distinguish tested
behavior from unverified solver/source coverage. Run the shared completeness and
cleanup checks, retain named residue and issue follow-ups, and commit/push/comment
or close only within applicable authority. Implementation approval does not grant
publication or other consequential action approval.

A hook's source presence does not prove installed enforcement. Report observed
consumer mismatches; do not disable hooks, set bypass flags or fabricate markers.
This skill neither installs provider profiles nor changes live enforcement.

Historical implementation references (verify current status):
[workflow consumers](https://github.com/vamseeachanta/workspace-hub/issues/1876),
[index metadata](https://github.com/vamseeachanta/workspace-hub/issues/1878),
[source-file readiness](https://github.com/vamseeachanta/workspace-hub/issues/2309).
