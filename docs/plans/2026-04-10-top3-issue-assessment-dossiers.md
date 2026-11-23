# Top 3 Issue Assessment Dossiers

Date: 2026-04-10
Repo: `vamseeachanta/workspace-hub`
Mode: delegated read-only Claude assessment
Issues assessed: `#2151`, `#2152`, `#2155`

## Live approval status

Current live GitHub state during assessment:
- open issues with `status:plan-approved`: `0`

That means all three issues are currently blocked for implementation and are suitable only for:
- approval-check runs
- dossier generation
- planning refinement

---

## Issue #2151
`feat(operations): define per-machine readiness evidence bundle schema and status vocabulary`

Assessment
- Approval: not approved
- Status: not done
- Confidence: high

Likely owned paths
- `docs/modules/ai/`
- `scripts/analysis/`
- `tests/analysis/`
- `tests/fixtures/`

Likely blockers / dependencies
- hard blocker: no `status:plan-approved`
- parent/dependency pressure:
  - `#2089`
  - `#2134`
  - `#2135`
- interface pressure from downstream consumers:
  - `#2148`
  - `#2150`
  - `#2152`
- related schema/validator chain:
  - `#2146`
  - `#2147`
- overlap risk with existing readiness output surfaces such as `scripts/readiness/nightly-readiness.sh`

Exact first failing tests after approval
- `uv run pytest tests/analysis -k "schema or readiness" -q`
- then likely:
  - `uv run pytest tests/analysis/test_readiness_evidence_bundle_schema.py -q`

Adversarial notes
- keep this issue schema-only
- do not absorb writer logic from `#2148` or `#2150`
- define explicit enum/timestamp/provenance rules
- align with existing workstation registry semantics

---

## Issue #2152
`test(reporting): add golden fixture corpus for weekly review run artifacts and validator coverage`

Assessment
- Approval: not approved
- Status: not done
- Confidence: high

Likely owned paths
- `tests/analysis/`
- `tests/fixtures/`
- `docs/modules/ai/`

Likely blockers / dependencies
- hard blocker: no `status:plan-approved`
- strong parent dependencies still open:
  - `#2146` schema spec
  - `#2147` validator CLI + CI checks
- downstream coupling pressure:
  - `#2153`
  - `#2154`
- no existing weekly-review fixture corpus found locally
- no weekly-review validator CLI found locally

Exact first failing tests after approval
- `uv run pytest tests/analysis -k "fixture or validator or weekly" -q`
- then likely:
  - `uv run pytest tests/analysis/test_weekly_review_artifact_fixtures.py::test_valid_minimal_fixture_matches_schema_contract -q`
  - `uv run pytest tests/analysis/test_weekly_review_artifact_fixtures.py::test_invalid_missing_required_key_reports_expected_error -q`
  - `uv run pytest tests/analysis/test_weekly_review_artifact_fixtures.py::test_invalid_bad_enum_reports_expected_error -q`
  - `uv run pytest tests/analysis/test_weekly_review_artifact_fixtures.py::test_invalid_bad_timestamp_reports_expected_error -q`

Adversarial notes
- do not invent validator behavior before reading `#2146` / `#2147`
- keep fixtures compact
- ensure invalid fixtures fail for the intended reason only

---

## Issue #2155
`feat(knowledge): build shared machine/path resolver library for session lookup and registry consumers`

Assessment
- Approval: not approved
- Status: not done
- Confidence: high

Likely owned paths
- `src/`
- `scripts/lib/`
- `scripts/operations/`
- `scripts/analysis/`
- `tests/workstations/`
- `tests/analysis/`
- `config/workstations/`

Most likely first integration targets
- `scripts/analysis/provider_session_ecosystem_audit.py`
- `scripts/analysis/claude_session_ecosystem_audit.py`

Likely blockers / dependencies
- hard blocker: no `status:plan-approved`
- canonical module location decision still needed
- alias/path policy still incomplete for future scope
- current unknown-host fallback behavior is inconsistent across scripts
- Windows path handling remains fragmented
- downstream consumers likely include:
  - `#2149`
  - `#2161`
  - `#2162`
  - `#2167`

Exact first failing tests after approval
- `uv run pytest tests/workstations/test_machine_path_resolver.py -q`
- then regression anchors:
  - `uv run pytest tests/analysis/test_provider_session_ecosystem_audit.py tests/analysis/test_claude_session_ecosystem_audit.py -q`
  - `uv run pytest tests/workstations/test_registry.py tests/workstations/test_dispatch.py -q`

Adversarial notes
- choose one canonical implementation, likely in `src/`
- keep shell wrappers thin
- define unknown-host behavior explicitly
- fixture-test Windows normalization rather than relying on heuristics

---

## Recommended next operator actions

1. Approve in order:
   - `#2151`
   - `#2152`
   - `#2155`

2. After approval, execute in order:
   - `#2151` schema/status vocabulary
   - `#2152` fixture corpus
   - `#2155` resolver extraction

3. Keep later issues gated behind these foundations:
   - `#2150`
   - `#2157`
   - `#2158`
   - `#2153`
   - `#2154`
   - `#2159`

## Recommended immediate use

Use `docs/plans/2026-04-10-single-terminal-claude-agent-team-prompts-2150-2159.md` in approval-check / dossier mode now.
After label approval is added, rerun the relevant prompt in implementation mode.
