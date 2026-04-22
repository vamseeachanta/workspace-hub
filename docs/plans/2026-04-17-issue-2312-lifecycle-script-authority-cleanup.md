# Plan for #2312: Lifecycle-script authority cleanup

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2312
> **Review artifacts:** scripts/review/results/2026-04-17-plan-2312-claude.md | scripts/review/results/2026-04-22-plan-2312-codex.md | scripts/review/results/2026-04-22-plan-2312-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `.planning/templates/stage-evidence-template.yaml` still encodes deleted lifecycle scripts in the only verified stale live-template hits for this issue: stage 19 uses `scripts/work-queue/close-item.sh` and stage 20 uses `scripts/work-queue/archive-item.sh`.
- Found: `tests/helpers/stale_reference_docs.py` already contains the lifecycle-script banned-pattern bank, so this issue can add a bounded docs regression test instead of inventing a new matcher.

### Attested evidence anchors used by this plan
- `docs/work-queue-workflow.md` exists and is the canonical current workflow reference for issue closeout/queue authority.
- `docs/ops/legacy-claude-reference-map.md` exists and is the canonical redirect map for deleted lifecycle scripts.
- `notes/agent-work-queue.md` exists and is the canonical queue-summary artifact referenced by the legacy redirect map.
- `docs/plans/README.md` exists and defines the retrieval/governance bundle relevant to this issue.
- `docs/standards/CONTROL_PLANE_CONTRACT.md` exists and is the governing control-plane contract for classifying adapters/rules.
- `config/agents/codex/state-snapshots/default.rules` exists and must be classified explicitly rather than silently ignored.
- `scripts/knowledge/tests/test-knowledge-scripts.sh` exists and must be classified explicitly rather than silently ignored.

### Standards / governance sources
| Source | Concrete finding |
|---|---|
| `docs/plans/README.md` | This plan touches both documentation and harness surfaces, so retrieval must include governance docs plus `CONTROL_PLANE_CONTRACT.md`, `config/agents/`, and `.claude/rules/`. |
| `docs/standards/CONTROL_PLANE_CONTRACT.md` | Provider adapters and rules are live control-plane surfaces; if lifecycle references appear there they must be classified explicitly rather than ignored. |
| `.claude/rules/` | No verified `close-item.sh`, `archive-item.sh`, or `claim-item.sh` hits exist today, so the directory can be treated as a zero-hit protected surface in the regression test. |
| `config/agents/codex/state-snapshots/default.rules` | Verified lifecycle references exist, but they are historical/provider-snapshot command records, not current workflow guidance; they belong in an explicit reference-only exclusion bucket for #2312. |
| `scripts/knowledge/tests/test-knowledge-scripts.sh` | Verified lifecycle references exist only as legacy-hook fixture/test scenarios; this is an analytical fixture surface, not live workflow guidance. |

### Documents consulted
- Issue #2312 — identifies the stale lifecycle-script authority cluster and the need to redirect agents to current GitHub / `.planning` / refresh-based surfaces.
- `docs/reports/provider-session-ecosystem-audit.md` — confirms the lifecycle cluster as `close-item.sh` (94), `archive-item.sh` (62), and `claim-item.sh` (60), so this issue should protect against reintroduction even where only close/archive are patched now.
- Issue #1717 — broader GitHub-vs-legacy work-queue contradiction context.
- Issue #2213 — broader stale-reference test-expansion context.
- Issue #2214 — broader historical redirect / live guidance separation context.

### Classification decisions locked by this plan
- Current guidance / protected surfaces for #2312: `.planning/templates/stage-evidence-template.yaml`, `.planning/templates/route-c-generic.md`, `.planning/templates/route-c-structural.md`, `.planning/templates/route-c-energy.md`, `.planning/templates/route-c-marine.md`, `docs/work-queue-workflow.md`, `docs/standards/CONTROL_PLANE_CONTRACT.md`, `.claude/rules/README.md`, `.claude/rules/patterns.md`, and `.claude/rules/coding-style.md`.
- Mixed generated authority surface: `notes/agent-work-queue.md` remains a valid authority anchor for archive/refresh guidance, but it is not suitable for whole-file banned-string scanning because issue titles in the generated queue can legitimately contain historical script names.
- Historical / reference surfaces intentionally allowed for now: `docs/ops/legacy-claude-reference-map.md`, `config/agents/codex/state-snapshots/default.rules`, `.planning/archive/**`, `.planning/architecture/**`.
- Fixture / analytical surfaces intentionally allowed for now: `scripts/knowledge/tests/test-knowledge-scripts.sh` and other tests whose purpose is to model legacy lifecycle behavior.
### Gaps identified
- The exact replacement contract for stages 19 and 20 has not yet been encoded in `.planning/templates/stage-evidence-template.yaml`.
- No existing targeted docs test protects the bounded current-surface set above while excluding historical/reference/fixture surfaces on purpose.
- The issue needs an explicit assertion that the replacement values are the approved anchors themselves, not merely “not the deleted scripts”.

<!-- Verification: count distinct sources above (issue + repo docs/files/issues). Minimum 3 required. Current count: 10+ distinct sources. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-17-issue-2312-lifecycle-script-authority-cleanup.md` |
| Template to patch | `.planning/templates/stage-evidence-template.yaml` |
| Current workflow authority doc | `docs/work-queue-workflow.md` |
| Legacy redirect authority doc | `docs/ops/legacy-claude-reference-map.md` |
| Queue refresh authority note | `notes/agent-work-queue.md` |
| Existing lifecycle banned-pattern helper | `tests/helpers/stale_reference_docs.py` |
| New bounded regression test | `tests/docs/test_lifecycle_script_reference_cleanup.py` |
| Historical/provider snapshot to classify, not patch | `config/agents/codex/state-snapshots/default.rules` |
| Fixture surface to classify, not patch | `scripts/knowledge/tests/test-knowledge-scripts.sh` |
| Review artifact — Claude | `scripts/review/results/2026-04-17-plan-2312-claude.md` |
| Review artifact — Codex | `scripts/review/results/2026-04-22-plan-2312-codex.md` |
| Review artifact — Gemini | `scripts/review/results/2026-04-22-plan-2312-gemini.md` |

---

## Deliverable

A draft-preserving cleanup in which `.planning/templates/stage-evidence-template.yaml` uses explicit current-workflow close/archive anchors, and a bounded docs regression test protects the verified current guidance surfaces from reintroducing `close-item.sh`, `archive-item.sh`, or `claim-item.sh` while leaving historical/reference/fixture surfaces intentionally classified and out of scope.

---

## Exact replacement contract

Patch `.planning/templates/stage-evidence-template.yaml` in place with these exact evidence values:

```yaml
  - order: 19
    stage: Close
    evidence: GitHub issue state and comments
  - order: 20
    stage: Archive
    evidence: notes/agent-work-queue.md
```

Authority rule for approval-stage review:
- This plan intentionally cites file existence plus governance-role alignment, not inline quoted content blocks, as its attested basis.
- During implementation review, the patch itself must prove the literal replacement strings above.
- This plan does not claim that `notes/agent-work-queue.md` is suitable for whole-file banned-string scanning; it claims only that it is the approved archive visibility anchor referenced by the legacy redirect map.

Why these are the approved replacements:
- `docs/work-queue-workflow.md` is the canonical current workflow reference for issue closeout/queue authority.
- `docs/ops/legacy-claude-reference-map.md` is the canonical redirect map for deleted lifecycle scripts.
- `notes/agent-work-queue.md` is the canonical queue-summary artifact referenced by that redirect map.

Bounded decision for `claim-item.sh` in #2312:
- No verified live current-guidance hit requires a patch in this issue.
- The new regression test will still ban `claim-item.sh` from the protected current-surface set so the issue reduces future stale-read risk without speculative code/doc edits.

---

## Pseudocode

```text
verify current live stale hits for close/archive in .planning/templates/stage-evidence-template.yaml
lock classification table:
    protected current guidance
    mixed generated authority surface
    historical/reference surfaces
    fixture/analytical surfaces
replace stage 19 evidence with exact literal "GitHub issue state and comments"
replace stage 20 evidence with exact literal "notes/agent-work-queue.md"
add bounded docs regression tests using existing lifecycle banned-pattern helper
in the new tests:
    test A scans only the fixed protected-surface set for close-item/archive-item/claim-item bans
    test B asserts the explicit exclusion bucket is exactly:
        docs/ops/legacy-claude-reference-map.md
        config/agents/codex/state-snapshots/default.rules
        scripts/knowledge/tests/test-knowledge-scripts.sh
        .planning/archive/**
        .planning/architecture/**
    test C asserts the exact replacement literals in stage-evidence-template.yaml
    test D asserts claim-item.sh remains banned in the protected-surface set
run the targeted docs tests and verify the protected-surface rule is falsifiable
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `.planning/templates/stage-evidence-template.yaml` | replace deleted stage-19/20 lifecycle-script evidence refs with the exact approved close/archive anchors above |
| Create | `tests/docs/test_lifecycle_script_reference_cleanup.py` | add a bounded regression test that asserts both the exact replacement contract and the protected current-surface ban on `close-item.sh`, `archive-item.sh`, and `claim-item.sh` |

No other file is planned for modification in #2312 unless a new verified stale current-guidance hit is discovered during implementation. `docs/work-queue-workflow.md`, `notes/agent-work-queue.md`, and `docs/plans/README.md` are evidence sources for the contract, not speculative edit targets.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_stage_evidence_template_uses_exact_current_close_archive_contract` | stage 19/20 in `.planning/templates/stage-evidence-template.yaml` use the approved literal replacements, not placeholders | `.planning/templates/stage-evidence-template.yaml` | stage 19 evidence is exactly `GitHub issue state and comments`; stage 20 evidence is exactly `notes/agent-work-queue.md` |
| `test_protected_current_guidance_surfaces_exclude_deleted_lifecycle_scripts` | deleted lifecycle scripts do not appear in the bounded protected current-surface set | exact file list: `.planning/templates/stage-evidence-template.yaml`, `.planning/templates/route-c-generic.md`, `.planning/templates/route-c-structural.md`, `.planning/templates/route-c-energy.md`, `.planning/templates/route-c-marine.md`, `docs/work-queue-workflow.md`, `docs/standards/CONTROL_PLANE_CONTRACT.md`, `.claude/rules/README.md`, `.claude/rules/patterns.md`, `.claude/rules/coding-style.md` | zero matches for `close-item.sh`, `archive-item.sh`, and `claim-item.sh` across those protected surfaces |
| `test_reference_and_fixture_exclusion_bucket_is_exact_and_explicit` | the exclusion bucket is explicit and cannot silently grow | exact exclusion set only: `docs/ops/legacy-claude-reference-map.md`, `config/agents/codex/state-snapshots/default.rules`, `scripts/knowledge/tests/test-knowledge-scripts.sh`, `.planning/archive/**`, `.planning/architecture/**` | test fails if a new path is relied on without updating the explicit exclusion contract |
| `test_claim_script_is_banned_in_protected_current_guidance_even_without_patch_targets` | `claim-item.sh` remains in regression scope even though #2312 does not patch a live current-guidance hit for it | same protected current-surface set as above | zero `claim-item.sh` matches |

Implementation note:
- Reuse `tests/helpers/stale_reference_docs.py` lifecycle-script patterns rather than duplicating the regex bank.
- Do not scan `notes/agent-work-queue.md` as a whole-file banned-reference target because generated issue titles can legitimately contain historical script names.

---

## Acceptance Criteria

- [ ] `.planning/templates/stage-evidence-template.yaml` stage 19 evidence is exactly `GitHub issue state and comments`
- [ ] `.planning/templates/stage-evidence-template.yaml` stage 20 evidence is exactly `notes/agent-work-queue.md`
- [ ] No speculative doc edits are performed beyond files with verified stale current-guidance hits
- [ ] A bounded regression test protects the exact current-guidance surface set: `.planning/templates/stage-evidence-template.yaml`, `.planning/templates/route-c-generic.md`, `.planning/templates/route-c-structural.md`, `.planning/templates/route-c-energy.md`, `.planning/templates/route-c-marine.md`, `docs/work-queue-workflow.md`, `docs/standards/CONTROL_PLANE_CONTRACT.md`, `.claude/rules/README.md`, `.claude/rules/patterns.md`, and `.claude/rules/coding-style.md`
- [ ] The regression suite uses a separate explicit exclusion-bucket assertion for `docs/ops/legacy-claude-reference-map.md`, `config/agents/codex/state-snapshots/default.rules`, `scripts/knowledge/tests/test-knowledge-scripts.sh`, `.planning/archive/**`, and `.planning/architecture/**`; those paths are classified, not silently skipped.
- [ ] `claim-item.sh` is included in the protected-surface regression ban even though this issue does not patch a current live `claim-item.sh` hit
- [ ] Targeted docs tests pass via `uv run pytest tests/docs/test_lifecycle_script_reference_cleanup.py tests/docs/test_banned_stale_references.py tests/docs/test_legacy_reference_allowlist.py -q`
- [ ] After fresh external re-review, the plan can advance toward `status:plan-review`; remaining in `draft` is not itself a success criterion.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MINOR | Approach was sound, but the previous draft left the close/archive replacement contract unresolved and did not fully classify adjacent surfaces. |
| Codex | MAJOR | Required an exact stage-19/20 replacement contract, harness-bundle retrieval, explicit current-vs-reference-vs-fixture classification, non-speculative file targets, and measurable/falsifiable test scope. |
| Gemini | MAJOR | Required the plan body itself to resolve the open replacement decision, remove speculative edits, and replace vague placeholder test inputs with exact protected/excluded surfaces. |

**Overall result from latest review round:** FAIL

This revision addresses the cited MAJOR findings by:
- locking the exact stage-19/20 replacement strings in the plan body;
- naming the harness/control-plane retrieval bundle and classifying `config/agents/codex/state-snapshots/default.rules` plus `scripts/knowledge/tests/test-knowledge-scripts.sh` explicitly;
- removing unsupported “modify if needed” file targets;
- defining a fixed protected-surface set and exclusion set for the new regression test;
- demoting audit refresh from pass/fail acceptance to post-implementation observation.

Because those review artifacts are still the latest recorded verdicts, the plan remains `draft` and needs fresh re-review rather than self-upgrading status.

---

## Risks and Open Questions

- **Risk:** `notes/agent-work-queue.md` is a mixed surface: authoritative header + generated issue-title payload. A naive whole-file banned-string test would create false positives from issue titles, so the test scope must stay on the fixed protected set above.
- **Risk:** Historical/provider snapshot files may continue to mention deleted lifecycle scripts for audit reproducibility; broad repo-wide bans would overreach beyond #2312.
- **Risk:** The stage-evidence template still contains broader legacy `.claude/work-queue` evidence paths; #2312 is intentionally bounded to lifecycle authority cleanup, not a full legacy evidence-contract rewrite.
- **Open question deferred, not blocking this issue:** whether mixed generated authority surfaces like `notes/agent-work-queue.md` should later gain line-scoped or section-scoped stale-reference checks. That is not required to approve this bounded cleanup.

---

## Complexity: T2

**T2** — bounded documentation/template/testing cleanup with a now-explicit replacement contract, a fixed and falsifiable protected-surface test scope, and explicit classification of current versus historical/reference/fixture surfaces; no architecture-scale implementation is required.
