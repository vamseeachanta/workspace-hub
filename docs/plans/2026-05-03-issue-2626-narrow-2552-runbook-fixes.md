# Plan for #2626: Narrow #2552 external-contributor runbook tests + scenario 3

> **Status:** plan-review
> **Complexity:** T1
> **Date:** 2026-05-03
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2626
> **Parent:** [#2552](https://github.com/vamseeachanta/workspace-hub/issues/2552) (status:plan-approved 2026-05-03; runbook content approved despite 4-day Tier-D persistent-MAJOR — architectural defects deferred here)
> **Review artifacts:** scripts/review/results/2026-05-03-plan-2626-claude.md (pending) | gemini.md (pending). Codex SKIPPED per #2479 unless version-pin lands first.

---

## Resource Intelligence Summary

### Existing repo code

- Found: `docs/plans/2026-04-29-issue-2552-external-contributor-runbook.md` — parent runbook plan, approved 2026-05-03 with persistent MAJOR defects deferred (this issue).
- Found: `.planning/plan-approved/2552.md` — local approval marker noting the deferral rationale.
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
| Test (revised) | `tests/security/test_runbook_external_contributor.py` | Create — positive-presence assertions only |
| Runbook scenario-3 patch | `docs/security/external-contributor-runbook.md` (within #2552 scope) | Modify in #2552 implementation slice; this plan defines the fix shape |
| Ingestion-vector doc | `docs/security/external-contributor-ingestion-vector.md` | Create |
| Plan-approved marker | `.planning/plan-approved/2626.md` | Create on user approval |

---

## Deliverable

A revised test contract + scenario-3 architectural decision + ingestion-vector procedure that resolves the 4 architectural defects from the #2552 Tier-D persistent-MAJOR pattern, without retroactively unapproving #2552 or duplicating its runbook content.

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

# 4. Verify plan-internal consistency
#   - HTML-comment metadata aligned with surrounding tables
#   - Acceptance criteria implementable from AC text alone
```

---

## Files to Change

| File | Action | Why |
|---|---|---|
| `docs/plans/2026-05-03-issue-2626-narrow-2552-runbook-fixes.md` | Create (this file) | Canonical plan |
| `tests/security/test_runbook_external_contributor.py` | Create | Implements revised test contract — positive-presence only |
| `docs/security/external-contributor-ingestion-vector.md` | Create | Defines ingestion under `collaborators_only` lockdown |
| `docs/security/external-contributor-runbook.md` | Modify (in #2552 slice) | Drop scenario-3 interaction-limit-lift suggestion |

---

## TDD Test List

| ID | Test | Trigger | Pass criterion |
|---|---|---|---|
| t01 | `test_runbook_references_triggering_issues` | runbook MD doesn't reference #2401 / #2546 / #2550 | all 3 issue refs present |
| t02 | `test_ingestion_vector_doc_exists` | the new doc isn't created | file exists at expected path with required sections |
| t03 | `test_scenario_3_no_interaction_limit_lift` | runbook MD contains banned phrase like "lift the interaction limit" | no match (negative search on a fixed string is OK; positive on names is NOT) |
| t04 | `test_runbook_no_pii_hardcoded` | test file contains email addresses or `@username` patterns | grep returns empty |

---

## Acceptance Criteria

- [ ] Plan committed to `docs/plans/`
- [ ] Cross-review wave: Claude r1 + Gemini r1 (Codex skipped per #2479 unless pinned). All return MINOR or APPROVE.
- [ ] On approval: `status:plan-approved` label + `.planning/plan-approved/2626.md` marker
- [ ] Implementation slice creates the 3 new files + the runbook patch
- [ ] All 4 TDD tests pass
- [ ] No regression on the runbook content already approved via #2552

---

## Risks

| Risk | Mitigation |
|---|---|
| Per-user allowlist is asked for as a future scenario | Out of scope for this plan; document as follow-up |
| Email ingestion vector requires inbox monitoring discipline | Document as operator responsibility; not enforced by this plan |
| Runbook patch creates merge conflict with concurrent #2552 implementation | Sequence: approve+implement #2626 first, then resume #2552 implementation slice with the patched scenario-3 |

---

## Adversarial Review Summary

| Round | Provider | Verdict | Notes |
|---|---|---|---|
| r1 | (pending) | (pending) | Cross-review will run after this plan lands |

**Status**: plan-review (rev-1, fresh). Awaiting Claude + Gemini cross-review.
