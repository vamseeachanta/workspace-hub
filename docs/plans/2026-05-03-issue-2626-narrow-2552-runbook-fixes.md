# Plan for #2626: Narrow #2552 external-contributor runbook tests + scenario 3

> **Status:** plan-review (canonical artifact recovered 2026-05-04; fresh Codex/Gemini reviews returned MAJOR; not approval-ready until blockers below are patched and rerun)
> **Complexity:** T1
> **Date:** 2026-05-03
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2626
> **Parent:** [#2552](https://github.com/vamseeachanta/workspace-hub/issues/2552) (status:plan-approved 2026-05-03; runbook content approved despite 4-day Tier-D persistent-MAJOR — architectural defects deferred here)
> **Review artifacts:** `scripts/review/results/2026-05-04-plan-2626-{claude,codex,gemini,disagreement}.md`. Codex/Gemini returned MAJOR; Claude output was not substantive enough to count as approval evidence.

---

## Resource Intelligence Summary

### Existing repo code

- Found: `docs/plans/2026-04-29-issue-2552-external-contributor-runbook.md` — parent runbook plan, approved 2026-05-03 with persistent MAJOR defects deferred (this issue).
- Live GitHub labels show #2552 is `status:plan-approved`, but `.planning/plan-approved/2552.md` is **not** retrievable on `main`; this plan must not cite a local approval marker as evidence until that governance drift is reconciled separately.
- Found: `feedback_codex_sustained_major_loop.md` (memory) — precedent for resolving 3+ round MAJOR loops by surfacing user decisions, not auto-cycling.
- Gap: `tests/security/test_runbook_external_contributor.py` not yet created — must be authored under this plan or a follow-up implementation slice.
- Gap: no documented ingestion-vector procedure for when GitHub interactions are blocked by `collaborators_only` lockdown (per #2546).

### Standards
| Standard | Status | Source |
|---|---|---|
| n/a — security/policy plan; no calc constants | n/a | n/a |

### Documents consulted

- Issue body of #2626 — defines the 4 defects + resolution shapes (issue body is plan-grade content, this plan formalizes it as canonical artifact).
- 2026-04-30 Gemini review of #2552 (`scripts/review/results/2026-04-30-plan-2552-gemini.md`) — surfaced privacy-leak finding + lockdown-contradiction finding.
- 2026-04-30 Codex review of #2552 (`scripts/review/results/2026-04-30-plan-2552-codex-final.md`) — surfaced executable-spec contradictions.
- `.claude/skills/coordination/issue-planning-mode/SKILL.md` — defines the cross-review contract this plan must satisfy.

---

## Artifact Map

| Deliverable | Path | Action |
|---|---|---|
| This plan | `docs/plans/2026-05-03-issue-2626-narrow-2552-runbook-fixes.md` | Create |
| Plan index | `docs/plans/README.md` | Update with #2626 row and current non-approval-ready review status |
| Test (revised) | `tests/security/test_runbook_external_contributor.py` | Create — positive-presence assertions only |
| Runbook scenario-3 patch | `docs/security/external-contributor-runbook.md` (within #2552 scope) | Modify in #2552 implementation slice; this plan defines the fix shape |
| Ingestion-vector doc | `docs/security/external-contributor-ingestion-vector.md` | Create |
| Plan-approved marker | `.planning/plan-approved/2626.md` | Create on user approval |

---

## Deliverable

A revised test contract + scenario-3 architectural decision + ingestion-vector procedure that resolves the 4 architectural defects from the #2552 Tier-D persistent-MAJOR pattern, without retroactively unapproving #2552 or duplicating its runbook content. The four defects are: (1) privacy-leaking negative test shape, (2) missing contributor-ingestion vector while GitHub is locked down, (3) interaction-limit-lift contradiction in scenario 3, and (4) executable-spec/governance metadata drift between issue references, plan/index rows, and acceptance criteria.

---

## Pseudocode

```
# 1. Revise the proposed test (drop privacy-leak negation)
def test_runbook_references_triggering_issues():
    text = read("docs/security/external-contributor-runbook.md")
    for issue_num in ("#2401", "#2546", "#2550"):
        assert issue_num in text, f"runbook must reference {issue_num}"
    # explicitly NO negative-presence assertions on PII —
    # those would require hardcoding the prohibited names

# 2. Define ingestion vector (decision: email)
# Write docs/security/external-contributor-ingestion-vector.md:
#   - Primary: email to security@aceengineer.com
#   - Secondary: open a public issue from a designated AceEngineer account
#     after triage approval
#   - Lockdown contract: collaborators_only stays in force; ingestion
#     does NOT lift the GitHub interaction limit

# 3. Resolve scenario-3 contradiction (decision: drop scenario 3 from in-scope)
# Patch the runbook to:
#   - Remove the "temporary lift of interaction limit" suggestion
#   - Document that fork-and-PR workflow for non-collaborators is currently
#     OUT OF SCOPE; refer requesters to the email ingestion vector
#   - Note that a per-user allowlist mechanism (if needed in future) is
#     a separate plan, not this one

# 4. Verify executable-spec/governance consistency
#   - docs/plans/README.md row exists and states current MAJOR-blocked plan-review state
#   - HTML-comment metadata aligned with surrounding tables
#   - Acceptance criteria implementable from AC text alone
#   - no claim depends on a missing .planning/plan-approved/2552.md marker
```

---

## Files to Change

| File | Action | Why |
|---|---|---|
| `docs/plans/2026-05-03-issue-2626-narrow-2552-runbook-fixes.md` | Create (this file) | Canonical plan |
| `docs/plans/README.md` | Update | Required plan index row; must say current reviews are MAJOR-blocked, not approval-ready |
| `tests/security/test_runbook_external_contributor.py` | Create | Implements revised test contract — positive-presence only |
| `docs/security/external-contributor-ingestion-vector.md` | Create | Defines ingestion under `collaborators_only` lockdown |
| `docs/security/external-contributor-runbook.md` | Modify (in #2552 slice) | Drop scenario-3 interaction-limit-lift suggestion |

---

## TDD Test List

| ID | Test | Trigger | Pass criterion |
|---|---|---|---|
| t01 | `test_runbook_references_triggering_issues` | runbook MD doesn't reference #2401 / #2546 / #2550 | all 3 issue refs present |
| t02 | `test_ingestion_vector_doc_exists` | the new doc isn't created | file exists at expected path with required sections |
| t03 | `test_scenario_3_no_interaction_limit_lift` | runbook MD contains any prohibited lockdown-bypass pattern: `lift the interaction limit`, `temporary lift`, `temporarily lift`, `disable collaborators_only`, `turn off collaborators_only`, `allow non-collaborator PR`, or equivalent regex class documented in the test | no prohibited lockdown-bypass wording remains; the test must cover the exact phrase cited in #2626 plus at least the listed variants |
| t04 | `test_no_private_identity_literals_in_test_contract` | the test file embeds private names, email addresses, or personal `@username` patterns while trying to prove absence | grep/regex over `tests/security/test_runbook_external_contributor.py` returns empty for private-identity literals; runbook privacy assertions use structural/redacted fixtures, not hardcoded prohibited names |
| t05 | `test_2552_regression_contract_after_scenario_3_narrowing` | narrowing scenario 3 accidentally removes #2552's legitimate-contributor/request coverage | runbook still has a section for legitimate contributor requests, but directs non-collaborator/public-GitHub intake to the email ingestion vector without lifting `collaborators_only` |

---

## Acceptance Criteria

- [ ] Plan committed to `docs/plans/`
- [ ] Cross-review wave: at least two valid current provider artifacts return MINOR or APPROVE after these MAJOR findings are patched; any unavailable/skipped provider has a non-empty `UNAVAILABLE` artifact and is named in the approval request.
- [ ] On approval: `status:plan-approved` label + `.planning/plan-approved/2626.md` marker
- [ ] Implementation slice creates the required docs/tests and applies the runbook patch only after the #2552 runbook file exists; if #2552 has not yet created `docs/security/external-contributor-runbook.md`, #2626 is sequenced as a pre-merge amendment to the #2552 implementation slice rather than a standalone patch against a missing file.
- [ ] All 5 TDD tests pass
- [ ] No regression on the #2552 legitimate-contributor/request coverage: scenario 3 is narrowed to email/owner-triaged intake, not deleted without replacement.

---

## Risks

| Risk | Mitigation |
|---|---|
| Per-user allowlist is asked for as a future scenario | Out of scope for this plan; document as follow-up |
| Email ingestion vector requires inbox monitoring discipline | Document as operator responsibility; not enforced by this plan |
| Runbook file may not exist yet because #2552 is approved but not implemented | Sequence #2626 as a pre-merge amendment to the #2552 implementation: create the #2552 runbook per its approved plan, then apply the #2626 scenario-3 narrowing before merging/closing #2552. Do not attempt to patch a missing file as a standalone closeout. |

---

## Adversarial Review Summary

| Round | Provider | Verdict | Notes |
|---|---|---|---|
| r1 | Codex | MAJOR | 2026-05-04 review found canonical artifact/index drift, false `.planning/plan-approved/2552.md` claim, pending-review status overclaim, narrow scenario-3 test, and missing #2552 regression contract. This revision patches those findings; rerun required. |
| r1 | Gemini | MAJOR | 2026-05-04 review found the same missing marker claim, impossible runbook patch sequencing, missing fourth-defect resolution, and circular/privacy test wording. This revision patches those findings; rerun required. |

**Status**: plan-review, MAJOR-blocked. Do not request user approval until a fresh post-patch rerun returns no MAJOR findings.
