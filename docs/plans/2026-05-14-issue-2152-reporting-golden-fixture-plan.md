# Issue #2152 Plan: Reporting Golden Fixture Corpus + Validator Coverage

Issue: https://github.com/vamseeachanta/workspace-hub/issues/2152
Catalog route: `/goal` Tier 1 #10 — test suite hardening [execution-heavy]
Mode: PLAN ONLY
Target branch/worktree: `dispatch/h4-2152` in `/tmp/wh-h4`

## Resource Intelligence Summary

### Sources checked

1. `/goal` invocation contract
   - Source: `.claude/rules/goal-invocation.md`
   - Finding: `/goal` work must fetch the catalog issue and latest comments before use.
   - Applied decision: catalog issue #2695 and latest comments were checked before this plan; current issue maps to Tier 1 #10 because fixture corpus and validator tests are test-suite hardening.

2. GitHub issue #2152 and comments
   - Source: live `gh issue view 2152 --repo vamseeachanta/workspace-hub`
   - Finding: #2152 is open and requests valid/invalid weekly-review run-artifact fixtures, expected validator outcomes, fixture README, and CI test usage.
   - Finding: labels include `status:blocked`, `agent:codex`, and `status:plan-approved`.
   - Finding: prior comments explicitly preserved the blocker: #2139/#2146/#2147 remain open and canonical schema/validator files are absent, so implementing fixtures now would invent the contract.

3. Foundation issue state
   - Source: live `gh issue view` for #2139, #2146, #2147, #2151, #2153, #2154.
   - Finding: #2139, #2146, and #2147 are still open.
   - Finding: #2151 is closed and may provide related readiness/status-vocabulary precedent, but it does not replace the weekly-review artifact schema/validator contract.
   - Decision: #2152 execution must begin with dependency revalidation and must stop if #2139/#2146/#2147 are still not landed.

4. Local repository evidence in `/tmp/wh-h4`
   - Source: file existence checks.
   - Missing: `docs/modules/ai/weekly-review-artifact.schema.yaml`, `scripts/analysis/validate_weekly_review_artifact.py`, `tests/analysis/test_weekly_review_artifact_fixtures.py`, `tests/fixtures/weekly-review-artifacts`.
   - Exists: `.planning/plan-approved/2152.md`, `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md`, `scripts/dispatch/overnight-2026-05-13/H4-issue-2152.sh`.
   - Decision: plan can be written, but fixture implementation remains gated on canonical schema/validator presence.

5. Existing planning/context docs
   - Source: `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` lines 174-184.
   - Finding: #2139, #2146, #2147, #2152, #2153, and #2154 are part of the weekly reporting artifact issue chain.
   - Source: `docs/plans/2026-04-10-top3-issue-assessment-dossiers.md` lines 62-98.
   - Finding: #2152 owned paths are expected to be `tests/analysis/`, `tests/fixtures/`, and `docs/modules/ai/`; blockers include #2146/#2147 and absent local fixture/validator surfaces.
   - Source: `docs/plans/2026-04-10-single-terminal-claude-agent-team-prompts-2150-2159.md` lines 205-234.
   - Finding: #2152 should execute as fixtures-and-tests work, avoiding product-code changes unless a tiny validator fix is necessary.

### Gaps / blockers

- Canonical weekly-review artifact schema is absent locally.
- Validator CLI is absent locally.
- Foundation issues #2139, #2146, and #2147 remain open at planning time.
- Any fixture body, expected validator error code, or CI assertion written before those foundations land would be speculative.

### Plan decision

Create a plan that is implementation-ready after dependencies land, but explicitly blocks execution if the canonical schema/validator contract is still absent. This preserves #2152 as approved planning while avoiding invented behavior.

## Objective

Add a golden fixture corpus and validator-focused coverage for weekly ecosystem review run artifacts once #2139/#2146/#2147 provide the canonical schema and validator contract.

The eventual implementation should make validator, renderer, history-index, and publication work safer by providing stable examples for healthy, degraded, multi-machine, and invalid weekly-review runs.

## Scope

In scope after dependency gate passes:

- Add valid weekly-review run artifact fixtures:
  - minimal valid run
  - full valid run
  - degraded-valid run
  - multi-machine valid run
- Add invalid weekly-review run artifact fixtures:
  - missing required key
  - bad enum/status value
  - bad timestamp/date format
  - malformed section/type
  - invalid issue reference format, if covered by the schema/validator
  - unsupported or incompatible schema version, if covered by #2146/#2147
- Define expected validator outcomes for every fixture.
- Add fixture README documenting naming, refresh, provenance, and intended-failure rules.
- Add tests wiring fixtures into validator coverage.
- Add CI test usage only through existing validator/test patterns from #2147.

Out of scope:

- Defining the weekly-review artifact schema from scratch.
- Creating or replacing the validator CLI.
- Inventing validator error-code taxonomy.
- Implementing renderer/history/publication behavior for #2153/#2154/#2159.
- Broad product-code refactors.
- Any changes outside the fixture/test/docs surfaces unless the landed validator exposes a tiny compatibility bug directly blocking fixture tests.

## Dependency Gate Before Implementation

Before writing any fixture or test, the executor must re-run these checks from a fresh, synced worktree:

1. Verify issue state:
   - `gh issue view 2139 2146 2147 2152 --repo vamseeachanta/workspace-hub` or equivalent per-issue calls.
   - Confirm #2139/#2146/#2147 are closed or their deliverables are present on `main` with accepted follow-up state.
2. Verify local contract files exist, using actual landed paths if names changed:
   - schema/spec file for weekly-review run artifact
   - validator CLI/module
   - validator test helper or CI entrypoint
3. Verify #2152 approval state remains valid:
   - live label/status still includes `status:plan-approved`, or user explicitly reconfirms.
4. If the dependency gate fails:
   - do not implement fixtures.
   - refresh blocker evidence in a narrow planning/blocker artifact or issue comment.
   - stop with exact missing files/issues.

## Proposed File Layout

Exact names should follow the landed #2146/#2147 conventions. If no contrary convention exists, use:

```text
tests/fixtures/weekly-review-artifacts/
  README.md
  valid/
    minimal.yaml
    full.yaml
    degraded.yaml
    multi-machine.yaml
  invalid/
    missing-required-key.yaml
    bad-enum.yaml
    bad-timestamp.yaml
    malformed-section.yaml
    bad-issue-reference.yaml          # only if schema validates issue refs
    incompatible-schema-version.yaml  # only if version policy validates this
  expected/
    valid.yaml                        # fixture -> expected success metadata
    invalid.yaml                      # fixture -> expected failure reason/code/path

tests/analysis/test_weekly_review_artifact_fixtures.py
```

If #2146/#2147 define JSON instead of YAML, mirror that format. Do not mix formats without a schema-backed reason.

## Implementation Plan After Gate Passes

### Phase 0 — Revalidate contract and paths

- Read the landed weekly-review schema/spec and validator docs.
- Identify required fields, optional fields, enum values, timestamp rules, issue-reference rules, compatibility/versioning rules, and degraded-valid semantics.
- Identify the validator invocation API:
  - Python function, CLI command, pytest helper, or CI script.
- Record the exact fixture root and test module names before adding files.

### Phase 1 — RED tests for corpus discovery and valid fixtures

Write failing tests first:

- `test_valid_minimal_fixture_matches_schema_contract`
- `test_valid_full_fixture_matches_schema_contract`
- `test_valid_degraded_fixture_matches_schema_contract`
- `test_valid_multi_machine_fixture_matches_schema_contract`
- `test_fixture_expected_outcome_manifest_covers_all_fixture_files`

Expected RED state:

- Tests fail because fixtures/expected outcome manifests do not exist yet, not because the validator cannot be imported. If the validator cannot be imported, stop and route back to #2147.

### Phase 2 — Add compact valid fixtures

Add compact fixtures that exercise schema coverage without becoming brittle data dumps.

Valid fixture intent:

- `minimal`: smallest artifact that passes required schema fields.
- `full`: representative populated artifact covering metadata, readiness, routing/settings, freshness, accessibility, findings, and follow-on issue refs.
- `degraded`: valid artifact with degraded status/findings, stale or partial evidence, and explicit reason fields allowed by schema.
- `multi-machine`: valid artifact representing at least two machine/evidence entries and any aggregation fields required by schema.

### Phase 3 — RED tests for invalid fixtures

Add failing tests that assert invalid fixtures fail for exactly the intended reason:

- `test_invalid_missing_required_key_reports_expected_error`
- `test_invalid_bad_enum_reports_expected_error`
- `test_invalid_bad_timestamp_reports_expected_error`
- `test_invalid_malformed_section_reports_expected_error`
- Optional schema-backed cases:
  - `test_invalid_bad_issue_reference_reports_expected_error`
  - `test_invalid_incompatible_schema_version_reports_expected_error`

Assertions should check stable validator output fields, not fragile full-message text unless #2147 makes the full message part of the contract.

### Phase 4 — Add invalid fixtures and expected outcomes

For each invalid fixture:

- Keep only one intentional violation per file.
- Preserve all other required fields as valid.
- Map fixture to expected exit code / error code / JSON pointer or path / concise human message.
- If the validator emits multiple errors, assert the intended primary error is present and no unrelated errors are introduced by fixture sloppiness.

### Phase 5 — Fixture README and refresh policy

Add `tests/fixtures/weekly-review-artifacts/README.md` covering:

- fixture purpose and consumers
- valid vs invalid directory meaning
- naming convention
- one-intended-failure rule for invalid fixtures
- schema-version update process
- how to refresh expected outcomes
- provenance/sanitization rule: no secrets, credentials, host-specific tokens, or private raw paths beyond intentionally documented examples
- commands to run fixture tests

### Phase 6 — CI/test wiring

Wire only to the existing validator/test infrastructure from #2147.

Preferred command:

```bash
uv run pytest tests/analysis/test_weekly_review_artifact_fixtures.py -q
```

If the repo already has a reporting/analysis CI group, add the test to that group instead of creating a new CI workflow. Avoid broad CI churn.

## Testing Strategy

Minimum local checks after implementation:

```bash
uv run pytest tests/analysis/test_weekly_review_artifact_fixtures.py -q
uv run pytest tests/analysis -k "weekly and (fixture or validator)" -q
```

If validator CLI exists:

```bash
uv run python scripts/analysis/validate_weekly_review_artifact.py --help
uv run python scripts/analysis/validate_weekly_review_artifact.py tests/fixtures/weekly-review-artifacts/valid/minimal.yaml
```

If #2147 provides a different CLI/module path, use that path instead.

Quality assertions:

- Every fixture is covered by expected outcomes.
- Every expected outcome references an existing fixture.
- Valid fixtures pass validator checks.
- Invalid fixtures fail for the intended reason only.
- Tests are deterministic and do not require live GitHub/network access.
- No fixture contains secrets or machine-private credentials.

## Documentation Updates

Required:

- `tests/fixtures/weekly-review-artifacts/README.md`.

Optional, only if useful and consistent with landed docs:

- Add a short pointer from the weekly review artifact schema/spec doc to the fixture corpus.
- Add a short validator usage example if #2147 docs do not already cover fixture validation.

## Adversarial Review Plan

No adversarial review was run as part of this plan-only drafting.

Required review route before implementation closure:

- Codex T1 review: fixture/test completeness, intended-failure isolation, CI wiring, and no speculative schema behavior.
- Claude T2 review: workflow gate compliance, blocker truthfulness, docs clarity, and downstream compatibility with #2153/#2154.

Review criteria:

- APPROVE only if fixtures are schema-backed and validator-backed.
- MAJOR if any fixture/test invents fields, enums, validator output, or CI behavior not established by #2146/#2147.
- MAJOR if invalid fixtures contain multiple accidental failures.
- MAJOR if implementation proceeds while #2139/#2146/#2147 deliverables are still absent.

## Risks and Open Questions

- Risk: #2146/#2147 may land under different file names than prior blocker comments expected.
  - Mitigation: dependency gate should search/read actual landed paths before deciding blocked.
- Risk: validator output may not have stable machine-readable error codes.
  - Mitigation: assert against the most stable contract #2147 provides; if none exists, route a small #2147 follow-up before freezing expected outcomes.
- Risk: fixtures become too large and brittle.
  - Mitigation: keep valid fixtures compact and purpose-specific; avoid raw production artifact dumps.
- Risk: degraded-valid semantics remain ambiguous.
  - Mitigation: only create degraded-valid fixture after schema explicitly defines degraded/stale/partial evidence fields.
- Open question: YAML vs JSON fixture format.
  - Resolution source: #2146 schema/spec.
- Open question: expected outcomes as sidecar YAML/JSON vs Python parametrization.
  - Recommendation: prefer sidecar manifest if validator output is stable; use Python parametrization only if repo tests already follow that pattern.

## Done Criteria

Planning done when:

- This plan exists at `docs/plans/2026-05-14-issue-2152-reporting-golden-fixture-plan.md`.
- Plan preserves the #2139/#2146/#2147 blocker and forbids speculative fixture implementation.
- Plan identifies concrete owned paths, tests, fixture classes, expected outcomes, docs, and CI checks.

Implementation done later when:

- Dependency gate passes against live issue state and local files.
- Fixture corpus exists and follows the landed schema/validator contract.
- Expected validator outcomes cover all fixtures.
- Fixture README documents naming, refresh, provenance, and intended-failure rules.
- Validator fixture tests pass locally and in CI.
- Adversarial reviews complete without unresolved MAJOR findings.
- GitHub issue #2152 receives evidence and is closed only after transactional commit/push/clean-state verification.

## Checklist

- [x] `/goal` rule fetched.
- [x] Catalog issue #2695 and latest comments fetched.
- [x] Catalog route mapped to Tier 1 #10 test suite hardening.
- [x] Isolated worktree `/tmp/wh-h4` created on branch `dispatch/h4-2152`.
- [x] #2152 live issue state checked.
- [x] Foundation issues #2139/#2146/#2147 checked and found open at planning time.
- [x] Local schema/validator/fixture paths checked and found absent at planning time.
- [x] Plan written.
- [ ] Adversarial plan review run.
- [ ] User approval or approval-state reconciliation after review.
- [ ] Implementation started after dependency gate passes.

## Complexity Classification

Execution-heavy test suite hardening.

Rationale:

- Primary deliverables are fixtures, tests, expected validator outcomes, and CI usage.
- Complexity is driven by dependency sequencing and correctness of negative test cases, not broad architecture.
- Work should be Codex-friendly after schema/validator foundations land, with Claude review for gate compliance and blocker truthfulness.
