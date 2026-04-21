# Packet B Plan — workspace-hub mission-contract validator and governance enforcement

> Status: draft
> Date: 2026-04-21
> Source context: split extracted from issue `#1525`
> Depends on: Packet A approval for canonical mission contract content

---

## Goal

Implement a deterministic validator, test harness, and CI/governance follow-up for the approved workspace-hub mission contract after Packet A lands.

## Why this packet exists

The repeated MAJOR findings on the original monolithic `#1525` plan were concentrated in tooling/enforcement concerns:
- parser semantics
- regex/forbidden phrase enforcement
- fenced-code handling
- AGENTS invariance checks
- evidence/bookkeeping expectations
- CI integration follow-up

This packet isolates that enforcement work from the mission-contract content decision.

---

## In scope

Tooling and governance only:
- `scripts/validation/check_workspace_hub_mission_contract.py`
- `tests/validation/test_workspace_hub_mission_contract.py`
- fixture-based tests for normalization / fencing / role contradictions
- reproducible `AGENTS.md` unchanged rule
- refinement/finalization of `.planning/quick/issue-1525-followup-ci-validator.md`
- optional filing of the CI follow-up issue after approval

---

## Out of scope

Do not redefine mission content here.
Do not renegotiate:
- role map
- non-goals
- glossary
- llm-wiki neutrality text
- Wave-2 `worldenergydata` defer note

Those come from Packet A.

---

## Deliverable

A deterministic validator plus test suite that enforces the approved workspace-hub mission contract and a ready-to-file CI follow-up issue for automated enforcement.

---

## Files to change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/validation/check_workspace_hub_mission_contract.py` | contract validator |
| Create | `tests/validation/test_workspace_hub_mission_contract.py` | red/green test harness |
| Create or modify | `tests/validation/fixtures/...` | parser/normalization fixtures |
| Modify | `.planning/quick/issue-1525-followup-ci-validator.md` | finalize CI follow-up issue draft |

---

## Required validator semantics

The validator should implement and the tests should prove:
- case-sensitive matching for canonical required statements
- CRLF → LF normalization
- Unicode NFC normalization
- trailing-whitespace trimming
- paragraph line-wrap normalization
- triple-backtick fenced-code exclusion for required / forbidden / semantic checks
- whole-line matching for required non-goal bullets
- exact glossary-section structure checks
- semantic role-claim contradiction checks using explicit regex catalog
- `AGENTS.md` unchanged check using a reproducible baseline strategy

---

## Required fixture coverage

Packet B should explicitly include fixtures/tests for:
1. CRLF normalization
2. Unicode punctuation / NFC normalization
3. wrapped paragraph required-phrase detection
4. forbidden phrase inside fenced code block should not fail
5. forbidden phrase outside fenced code block should fail
6. non-goal bullet marker normalization
7. glossary structure validation
8. semantic contradiction detection for wrong repo-role assignment
9. `GSD is the control plane` legacy phrase rejection
10. `AGENTS.md` unchanged baseline behavior

---

## TDD sequence

1. write failing tests in `tests/validation/test_workspace_hub_mission_contract.py`
2. add fixtures covering normalization/fencing/contradictions
3. run:
   - `uv run pytest tests/validation/test_workspace_hub_mission_contract.py -q`
4. confirm failures
5. implement `scripts/validation/check_workspace_hub_mission_contract.py`
6. rerun until green
7. smoke-test validator directly from CLI

Suggested direct validator contract:
- success exit code = 0
- contract violation exit code = non-zero
- clear stderr/stdout explaining failing rule

---

## Acceptance criteria

- `scripts/validation/check_workspace_hub_mission_contract.py` exists
- `tests/validation/test_workspace_hub_mission_contract.py` exists
- fixture coverage exists for normalization, fencing, contradiction, and AGENTS invariance cases
- `uv run pytest tests/validation/test_workspace_hub_mission_contract.py -q` passes
- validator can also be run directly from the command line with a stable exit code contract
- `.planning/quick/issue-1525-followup-ci-validator.md` includes:
  - validator path
  - test path
  - pytest command
  - intended CI hook/job
- if desired by the user, the CI follow-up issue can then be filed from the refined draft

---

## Suggested review standard for Packet B

This packet should be reviewed primarily for:
1. determinism of parser semantics
2. sufficiency of fixture coverage
3. reproducibility of AGENTS invariance rule
4. clarity of validator CLI behavior
5. suitability of CI follow-up details

---

## Relationship to Packet A

Packet B must consume the approved Packet A contract as source of truth.
If Packet A wording changes, Packet B should be updated to match before implementation begins.