# Issue #1525 review decision

Date: 2026-04-21
Issue: `#1525` — Define canonical repo control-plane contract across workspace ecosystem
Decision basis: adversarial review waves 1–9 across Claude, Codex, and Gemini

## Outcome

Do not continue tightening `#1525` as a single approval packet.

Reason:
- repeated Claude/Codex MAJOR findings are no longer about the core mission-contract idea
- the remaining blockers are governance/evidence/validator-contract bookkeeping concerns
- Gemini repeatedly reports the plan is effectively implementation-ready in substance
- additional iteration on the same single packet is now yielding diminishing returns and creating self-referential governance churn

## Recommendation

Split the work into two bounded packets:

### Packet A — canonical workspace-hub mission contract
Purpose:
- establish the normative mission and role contract only
- keep scope primarily document reconciliation

Proposed scope:
- `docs/standards/WORKSPACE_HUB_MISSION_CONTRACT.md`
- `README.md`
- `docs/README.md`
- `docs/BUSINESS_BRAIN.md`
- `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md`
- generic cross-link in `docs/standards/CONTROL_PLANE_CONTRACT.md`

Keep but simplify:
- canonical role map
- non-goals
- glossary
- llm-wiki neutrality phrase
- Wave-1 deferral of `worldenergydata`

Remove from Packet A:
- advanced validator implementation details
- exhaustive review-wave bookkeeping in the plan body
- AGENTS blob pin as approval blocker
- CI follow-up detail as an implementation acceptance gate

Acceptance focus:
- contract content is correct
- docs are aligned
- cross-link is present
- no premature #2398 decision

### Packet B — validator and governance enforcement
Purpose:
- implement deterministic validator/test harness/CI follow-up after Packet A is approved

Proposed scope:
- `scripts/validation/check_workspace_hub_mission_contract.py`
- `tests/validation/test_workspace_hub_mission_contract.py`
- CI follow-up issue filing and/or CI hook integration
- stronger bookkeeping / evidence rules if still needed

Acceptance focus:
- parser semantics are precise and tested
- fixture coverage exists for CRLF/NFC/fences/paragraph wrapping
- AGENTS unchanged check is reproducible
- CI path is explicit

## Why split is now better than more tightening

1. The architectural/mission decision is already stable.
2. The remaining MAJOR findings are mostly about enforcement mechanics, not business/portfolio intent.
3. Splitting reduces review surface and should let Packet A become approval-ready quickly.
4. Packet B can then be reviewed as a tooling/governance issue with clearer testable boundaries.

## Practical next step

Treat current `#1525` plan as source material for two new local drafts:
1. mission-contract plan
2. validator/enforcement follow-up plan

Do not surface the current monolithic `#1525` draft for user approval.
