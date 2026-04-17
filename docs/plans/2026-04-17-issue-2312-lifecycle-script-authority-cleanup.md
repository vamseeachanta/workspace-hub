# Plan for #2312: Lifecycle-script authority cleanup

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2312
> **Review artifacts:** scripts/review/results/2026-04-17-plan-2312-claude.md | scripts/review/results/2026-04-17-plan-2312-codex.md | scripts/review/results/2026-04-17-plan-2312-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `.planning/templates/stage-evidence-template.yaml` — still contains deleted lifecycle-script evidence targets for the final stages: `scripts/work-queue/close-item.sh` and `scripts/work-queue/archive-item.sh`.
- Found: `docs/work-queue-workflow.md` — already states the canonical flow is GitHub issue -> `.planning/` -> implementation -> cross-review -> close issue, and explicitly says not to invoke legacy local closure helpers as live workflow steps.
- Found: `notes/agent-work-queue.md` — current queue summary is generated from GitHub labels and explicitly states GitHub issues are the source of truth, refreshed via `scripts/refresh-agent-work-queue.py` / `.sh`.
- Found: `tests/helpers/stale_reference_docs.py` — already bans deleted lifecycle-script references (`close-item.sh`, `whats-next.sh`, `archive-item.sh`, `claim-item.sh`) in strict stale-reference scans.
- Gap: there is no targeted regression test for lifecycle-script references in current templates/routing docs that are not yet eligible for the full strict stale-reference suite because they still contain other legacy compatibility paths.
- Gap: the stage-evidence template still encodes a deleted-script worldview for close/archive evidence, so current workflow guidance is internally inconsistent even though top-level docs already describe the GitHub/.planning model correctly.

### Standards
| Standard | Status | Source |
|---|---|---|
| Not applicable | n/a | Documentation / workflow-governance issue; no engineering standard governs the cleanup |

### LLM Wiki pages consulted
- No relevant wiki pages — issue scope is repo workflow governance, not domain knowledge.

### Documents consulted
- Issue #2312 — defines the target stale-read cluster (216 mapped Claude reads) and identifies the desired authority surfaces.
- `docs/reports/provider-session-ecosystem-audit.md` — latest audit confirms the lifecycle cluster as `close-item.sh` (94), `archive-item.sh` (62), and `claim-item.sh` (60), with redirect guidance already pointing to `scripts/refresh-agent-work-queue.py`, `scripts/refresh-agent-work-queue.sh`, `notes/agent-work-queue.md`, `.planning/`, and GitHub issues.
- `docs/ops/legacy-claude-reference-map.md` — canonical redirect map for deleted lifecycle scripts and the current queue-authority surfaces.
- Issue #1717 — broader policy/docs contradiction issue for GitHub issues vs legacy work-queue guidance.
- Issue #2213 — broader stale-reference test expansion issue for live docs.
- Issue #2214 — broader architecture/legacy redirect split issue.

### Gaps identified
- No canonical replacement evidence paths have been defined yet for the final close/archive stages in `.planning/templates/stage-evidence-template.yaml`.
- No targeted test currently protects current templates/routing docs from reintroducing deleted lifecycle-script references while still allowing intentional historical surfaces to exist.
- The issue needs a bounded rule for how legacy analytical tests/fixtures that intentionally mention deleted lifecycle scripts should be treated relative to current user-facing templates and docs.

<!-- Verification: count distinct sources above (across all sub-sections).
     Minimum 3 required (issue body + 2 others). Current count: 7 -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-17-issue-2312-lifecycle-script-authority-cleanup.md` |
| Current workflow doc | `docs/work-queue-workflow.md` |
| Queue authority note | `notes/agent-work-queue.md` |
| Legacy redirect map | `docs/ops/legacy-claude-reference-map.md` |
| Template to patch | `.planning/templates/stage-evidence-template.yaml` |
| Targeted lifecycle-reference regression test | `tests/docs/test_lifecycle_script_reference_cleanup.py` |
| Shared stale-reference helper updates (if needed) | `tests/helpers/stale_reference_docs.py` |
| Review artifact — Claude | `scripts/review/results/2026-04-17-plan-2312-claude.md` |
| Review artifact — Codex | `scripts/review/results/2026-04-17-plan-2312-codex.md` |
| Review artifact — Gemini | `scripts/review/results/2026-04-17-plan-2312-gemini.md` |

---

## Deliverable

A consistent current-workflow documentation/template contract in which lifecycle completion stages point to GitHub issue + `.planning` + queue-refresh authority surfaces instead of deleted local lifecycle scripts, backed by targeted regression tests.

---

## Pseudocode

```text
identify current templates/docs that still mention close-item/archive-item/claim-item scripts
for each current workflow surface:
    decide whether the reference is current guidance, historical evidence, or analytical fixture
for current guidance files:
    replace deleted lifecycle-script refs with canonical GitHub/.planning/refresh-agent-work-queue evidence targets
create a targeted regression test that scans current workflow templates/docs for lifecycle-script refs
exclude intentional historical maps and analytical fixture files from the targeted current-surface rule
run targeted docs tests
refresh provider-session audit after cleanup and link the result back to the issue
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `.planning/templates/stage-evidence-template.yaml` | replace deleted close/archive lifecycle-script evidence refs with current canonical evidence targets |
| Modify | `docs/work-queue-workflow.md` | tighten wording if needed so current completion/closure evidence paths match the template changes |
| Modify | `notes/agent-work-queue.md` | document/anchor queue-refresh authority if the template needs a stable evidence target reference |
| Create | `tests/docs/test_lifecycle_script_reference_cleanup.py` | targeted regression test for deleted lifecycle-script refs in current docs/templates |
| Modify | `tests/helpers/stale_reference_docs.py` | expose reusable lifecycle-script-specific helper/patterns if needed |
| Update | `docs/plans/README.md` | add this plan to index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_stage_evidence_template_no_longer_uses_deleted_close_archive_scripts` | the canonical stage-evidence template no longer encodes `close-item.sh` or `archive-item.sh` as live evidence targets | `.planning/templates/stage-evidence-template.yaml` | zero deleted lifecycle-script matches |
| `test_current_workflow_docs_use_github_planning_refresh_authority_not_deleted_lifecycle_scripts` | current workflow docs/templates point to GitHub/.planning/refresh helpers instead of deleted lifecycle scripts | curated current-file list | zero deleted lifecycle-script matches and required replacement anchors present |
| `test_legacy_reference_map_retains_redirects_for_lifecycle_scripts` | intentional legacy map still preserves the discoverable redirects for historical references | `docs/ops/legacy-claude-reference-map.md` | redirect block present |
| `test_analytical_fixture_files_are_not_treated_as_current_workflow_docs` | legacy analytical test fixtures can remain historical data without weakening current-doc protection | selected fixture file list | targeted test ignores or separately classifies them |

---

## Acceptance Criteria

- [ ] `.planning/templates/stage-evidence-template.yaml` stops referencing deleted lifecycle scripts as current close/archive evidence
- [ ] Current workflow docs/templates describe GitHub issues + `.planning` + refresh helpers as the authoritative completion flow
- [ ] A targeted regression test fails if deleted lifecycle scripts (`close-item.sh`, `archive-item.sh`, `claim-item.sh`) reappear in protected current docs/templates
- [ ] Intentional historical/reference surfaces remain discoverable without being mistaken for current workflow guidance
- [ ] Targeted docs test suite passes via `uv run pytest tests/docs/test_lifecycle_script_reference_cleanup.py tests/docs/test_banned_stale_references.py tests/docs/test_legacy_reference_allowlist.py -q`
- [ ] Post-implementation audit refresh is run and linked from the issue

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MINOR | Main approach is sound, but the plan leaves the close/archive replacement contract unresolved and does not fully classify adjacent current surfaces. |
| Codex | MAJOR | The central replacement evidence contract is still undecided; proposed doc edits are not evidence-tight; audit-refresh success criteria are not measurable. |
| Gemini | MINOR | Good direction, but the replacement target should be proposed up front and the targeted test must explicitly include hidden agent/rule surfaces. |

**Overall result:** FAIL (re-draft required before approval readiness)

Revisions required based on review:
- Define the exact authoritative replacement for the `Close` and `Archive` evidence values in `.planning/templates/stage-evidence-template.yaml`.
- Remove unsupported “modify if needed” doc targets unless a concrete stale lifecycle-script hit is evidenced in those files.
- Make the regression strategy explicit: exact protected surface set (including hidden agent/rule directories if in scope), and whether this issue adds a bespoke test or extends existing stale-reference infrastructure.
- Add validation that replacement evidence targets are real/approved anchors rather than placeholder paths.
- Tighten or demote the audit-refresh acceptance criterion unless it includes a concrete success condition tied to this cleanup.

---

## Risks and Open Questions

- **Risk:** The stage-evidence template still contains broader legacy work-queue paths beyond the lifecycle scripts, so the new regression test must stay tightly scoped or it will fail for unrelated historical-compatibility reasons.
- **Risk:** Choosing replacement evidence targets for Close/Archive may require a small contract decision rather than a simple path substitution.
- **Open:** What should the canonical issue-specific evidence path be for the final close/archive stages — GitHub issue URL/comment reference, a `.planning/verified/` artifact, or a queue-refresh artifact reference?
- **Open:** Should `claim-item.sh` be handled in the same bounded issue if no current live template/doc hit is found, or should the issue only patch the surfaces actually present today and leave `claim-item.sh` covered by the regression test?

---

## Complexity: T2

**T2** — bounded multi-file documentation/template/testing cleanup with one unresolved evidence-contract decision for the close/archive stages, but no architecture-scale implementation or domain-standard dependency.
