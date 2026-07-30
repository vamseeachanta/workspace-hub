# Plan for #3566: Keyboard/context-menu text paste equivalence

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-07-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3566
> **Client:** N/A
> **Lane:** lane:claude

## Resource Intelligence Summary

- Issue #3566 requires HITL confirmation of `Ctrl+Insert` versus `Shift+Insert`, route ownership, canonical-draft comparison, and no accidental submit.
- `scripts/readiness/check-ux-consistency.sh` is prose-only; it records no structured route, digest, or submission evidence.
- `scripts/readiness/collect-equality.sh` and `build-equality-matrix.py` provide the existing matrix pipeline but no paste predicate.
- Parent plan #3568 and sibling #3567 require semantic interaction predicates, privacy-safe evidence, and independent child gates.
- `scripts/readiness/harness-config.yaml` has five active machines plus two unreachable entries; GUI evidence must not be assumed for headless/unavailable roles.
- Drive index search (`plan-resource-intel`, 2026-07-17) returned no relevant UX/equivalence documents.

### Gaps identified
- No deterministic fixture or collector distinguishes keyboard paste from bracketed context-menu paste.
- No versioned canonicalization contract or separate input/canonical-draft digests exists.
- No HITL artifact records duplicate insertion, accidental submit, or Unicode/tab/newline preservation without retaining raw clipboard text.

### Reproduction proofs
The issue's live Ubuntu evidence identifies GNOME Terminal paste as `Ctrl+Shift+V`, right-click as terminal-owned bracketed paste, and no current Codex `Ctrl+Insert` text-paste binding. HITL must run the synthetic sentinel through plain Bash and Codex composer before implementation.

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-17-issue-3566-paste-equivalence.md` |
| Tests | `tests/readiness/test_collect_interaction_ux.py`, `tests/readiness/test_build_equality_matrix.py` |
| Implementation | `scripts/readiness/collect-interaction-ux.sh`, `scripts/readiness/build-equality-matrix.py` |
| Review artifacts | `scripts/review/results/2026-07-17-plan-3566-*` |

## Deliverable

A versioned, privacy-safe paste-equivalence evidence producer and matrix predicate proving keyboard and context-menu paste yield one identical canonical Codex draft without auto-submit.

## Pseudocode

```text
capture_paste_probe(route, sentinel):
    validate route is keyboard or context_menu
    capture input digest without storing sentinel text
    inject through the selected terminal/Codex seam
    capture canonical draft digest and safety flags
    return route, digests, canonicalization_version, flags

grade_paste_equivalence(probes):
    require both routes and matching canonical digests
    require exactly-one insertion and explicit-submit behavior
    require Unicode/tab/newline fixture coverage
    emit PASS, FAIL, or MISSING-EVIDENCE with remediation issue
```

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/readiness/collect-interaction-ux.sh` | Capture structured, redacted HITL paste evidence |
| Create | `tests/readiness/test_collect_interaction_ux.py` | TDD fixtures for both event paths and safety flags |
| Modify | `scripts/readiness/build-equality-matrix.py` | Grade paste predicate and render remediation |
| Modify | `tests/readiness/test_build_equality_matrix.py` | Verify verdict precedence and missing/headless evidence |
| Update | `docs/plans/README.md` | Index this plan |

## TDD Test List

| Test name | What it verifies | Expected output |
|---|---|---|
| `test_fixture_captures_both_routes` | keyboard and context-menu routes are distinct inputs | two records |
| `test_canonical_digest_matches` | equivalent routes compare canonical drafts | `PASS` |
| `test_route_mismatch_is_fail` | route-specific normalization is visible | `FAIL` |
| `test_multiline_unicode_tab_fixture` | sentinel classes are preserved | matching digest |
| `test_no_auto_submit_or_duplicate` | safety predicates hold | explicit-submit, count=1 |
| `test_missing_gui_evidence` | unavailable GUI is not assumed equivalent | `MISSING-EVIDENCE` |
| `test_headless_role_is_bounded` | headless machine is bounded | `EXPECTED-DIVERGENCE` |

## Acceptance Criteria

- [ ] HITL confirms `Ctrl+Insert` versus `Shift+Insert` before remapping.
- [ ] RED fixture distinguishes plain-terminal ownership from Codex composer ownership.
- [ ] Input and canonical-draft digests are separate; raw sentinel/transcript text is never persisted.
- [ ] Both routes match for single-line, multiline, Unicode, tab, and trailing-newline fixtures.
- [ ] No duplicate insertion or accidental submit occurs.
- [ ] Canonicalization is pinned to installed Codex and probe versions.
- [ ] Unavailable GUI is `MISSING-EVIDENCE`; headless roles are bounded `EXPECTED-DIVERGENCE`.
- [ ] Adversarial review artifacts exist before posting for user approval.

## Adversarial Review Summary

Pending review.

## Risks and Open Questions

- GUI/HITL capture cannot run from headless cron; capture and ingestion must be separate.
- Literal chord comparison would incorrectly mark Windows/Linux semantic parity as divergent.
- Confirm whether the accepted gesture is literally `Ctrl+Insert` or conventional `Shift+Insert`.
