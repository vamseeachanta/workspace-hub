# Claude r2 adversarial re-review — digitalmodel OCIMF polar+vessel+force-vector plan (revised)

> **Reviewer:** Claude (workspace-hub session, single-author r2; follow-on to r1)
> **Plan reviewed:** `docs/governance/2026-05-20-digitalmodel-plan-draft-ocimf-polar-vessel-force-overlay.md` (revised; 38.8 KB / 332 lines, up from 25.1 KB / 240 lines)
> **r1 artifact:** `scripts/review/results/2026-05-20-plan-draft-digitalmodel-ocimf-polar-vessel-force-overlay-claude-r1.md`
> **Date:** 2026-05-20
> **Stance:** adversarial; verify each r1 finding's revision actually addresses the defect rather than paraphrasing it; hunt for new defects introduced during revision.

---

## Verdict: **MINOR — surface to user as approval-eligible with 4 new minor findings to optionally tighten**

r1 MAJOR closure: **confirmed**. Both M1 and M2 received structural revisions, not cosmetic paraphrases. The six MINOR findings received targeted §Files-to-Change rows and §Acceptance enforcement bullets.

Four new MINOR findings emerged from the revisions themselves. None blocks approval; each is a tightening opportunity the implementing agent should either fix during plan-review or carry into implementation as a TODO.

---

## r1 closure verification

### M1 closure — VERIFIED

The revised plan:

- Replaces `returns 90.0` / `returns 270.0` literal assertions in §TDD #5/#6 with property assertions that derive the expected value from a citation-bound authority constant.
- Adds `IMPLEMENTATION GATE` language in `_resolve_arrow_direction_in_body_frame`'s docstring forbidding test value-pinning before the OCIMF Annex A citation lands.
- Adds independent cross-check TDD #16 (180°-invariant under sign flip) — catches asymmetric mapping bugs even if the authority constant is wrong by an offset.
- Adds enforcement bullet in §Acceptance: "OCIMF MEG3/MEG4 Annex A convention citation is present in `polar_force_overlay.py` docstring and in the `OCIMF_CONVENTION_AUTHORITY` constant; tests #5/#6 derive their expected value from that authority, not from inline literals."

**The closure is structural** — the plan can no longer pass with a directionally wrong test silently codifying the bug. Reviewer would catch missing citation.

### M2 closure — VERIFIED

The revised plan:

- Expands §RIS Existing repo code with 4 hull/vessel-related entries: `profile_schema.py` (HullProfile/HullStation/HullType), `models.py` (vessel-property models), `orcawave/vessel_database.py`, `hydrodynamics/diffraction/input_schemas.py`, plus the hull_library helpers.
- Records an explicit Decision: reuse `HullProfile` + introduce thin `VesselSilhouetteSpec` wrapper; rejects the competing-`VesselGeometry` anti-pattern.
- Updates §Pseudocode: `VesselGeometry` dataclass replaced with `VesselSilhouetteSpec(hull_profile: HullProfile, silhouette_kind, custom_path, opacity)`.
- Adds §Files-to-Change row for `types.py` housing the new spec.
- Adds TDD #17 static-analysis check forbidding competing geometry dataclasses (field-name discriminator).
- Adds §Risks Open row for HullProfile field-set confirmation gate.

**The closure is structural and load-bearing on tests #17 + acceptance criterion.**

### MINOR closures

| Finding | Closure | Verified |
|---|---|---|
| m1 (fixture-capture step) | §Files-to-Change adds `fixtures/ocimf_explorer_pre_refactor_trace_signature.json` + capture-sequencing paragraph + `source_commit_sha` field requirement | ✓ structural |
| m2 (SIROCCO smoke weakness) | §TDD #14 expanded from 1 assertion to 5 sub-conditions: returns Figure, 6 legend entries, ≥3 distinct arrow directions, no warnings, non-empty layout | ✓ each sub-condition is independently falsifiable |
| m3 (legal-scan hardcoded patterns) | §TDD #15 rewritten to invoke `scripts/legal/legal-sanity-scan.sh` OR consume `.legal-deny-list.yaml` patterns programmatically | ✓ |
| m4 (missing before-snapshot file) | §Files-to-Change adds `fixtures/ocimf_explorer_baseline.html` byte-frozen baseline row | ✓ |
| m5 (citation contract applicability) | §Risks Open carries a three-part decision (a) module emits no Citation; (b) Figure `layout.meta` carries provenance for downstream consumers; (c) silhouettes are conventional. §Acceptance enforces (b). | ✓ decision is recorded and falsifiable |
| m6 (Plotly arrow pre-spike) | §Risks rewritten to require pre-spike artifact attached to issue before approval; §Acceptance enforces | ✓ but see r2 finding n4 |

---

## NEW MINOR findings introduced by the revision

### n1 — `OCIMF_CONVENTION_AUTHORITY` constant referenced in §TDD #5/#6 but its location and shape are not specified in §Files-to-Change

**Where:** §TDD row 5 ("Test scaffold: `expected_direction = OCIMF_CONVENTION_AUTHORITY.positive_cy_arrow_at_starboard_incidence()`"); §Files-to-Change does not list the file housing this constant; §Pseudocode does not import it.

**Why MINOR:** the implementing agent has to invent the authority constant's location and API surface, which means two implementers will produce two incompatible designs. Not load-bearing on correctness (the citation gate still applies), but it is a missing decision row.

**Fix:** add a §Files-to-Change row specifying that the authority constant lives in a `_convention.py` module under `marine_engineering/visualization/` (or imported from a more global citation registry once one exists), and name at minimum the methods/attributes the constant must expose.

### n2 — Capture-sequencing rule lacks an enforceable verification step

**Where:** §Files-to-Change "Capture sequencing" paragraph.

**The defect:** the paragraph instructs the implementing agent to land the capture-commit before the refactor-commit and to record the pre-refactor `source_commit_sha` in the fixture JSON. But there is no commit hook, CI check, or test that verifies the SHA actually predates the refactor. A speed-running implementer could (deliberately or accidentally) regenerate the fixture from a post-refactor state, defeating the regression test #13.

**Fix:** add a verification step — either (a) a test in #13 that runs `git log --follow scripts/python/digitalmodel/ocimf/build_coefficient_explorer.py` and asserts the fixture's `source_commit_sha` predates any commit touching the refactor target lines, or (b) a documented reviewer-check in §Acceptance: "reviewer verifies fixture JSON's `source_commit_sha` predates the refactor commit by inspecting `git log`."

### n3 — TDD #17 forbids competing-dataclass fields by literal name, not by semantic overlap

**Where:** §TDD row 17 ("no `@dataclass` declares fields named `loa_m`, `beam_m`, or `draft_m`").

**The defect:** the static-analysis check uses three literal field names. A sneaky (or merely inconsistent) implementer could use `length_overall_m`, `loaM`, `vessel_loa`, `LOA`, or any variant and bypass the check while still creating the duplicate-data anti-pattern. The test catches the laziest form of the bug but not the harder forms.

**Fix:** widen the check — either (a) read the actual field set of `HullProfile` at test time and forbid any dataclass field in the visualization module whose semantic intent overlaps (heuristic: lowercase normalize + token compare against HullProfile's field set), or (b) restrict the check to declare that `VesselSilhouetteSpec` is the ONLY dataclass in the new module and any other dataclass is forbidden. Option (b) is the simpler enforceable rule.

### n4 — §Acceptance "spike artifact attached to digitalmodel issue as a comment" is GitHub-only; should be repo-tracked

**Where:** §Acceptance "r1 m6 enforcement: Plotly arrow technique pre-spike artifact (≤30 LOC prototype + rendered output) is attached to the digitalmodel issue as a comment."

**The defect:** GitHub comments can be edited, deleted, or hidden behind discussion-mode toggles. A repo-tracked spike under `digitalmodel/docs/spikes/2026-05-20-plotly-polar-arrow-technique/` survives audit and can be referenced by commit SHA. GH-only attachment leaves the audit trail brittle.

**Fix:** require the spike artifact to be committed under `digitalmodel/docs/spikes/` (or similar repo path) with the issue comment serving as a *link* to the committed artifact, not the artifact itself. Update §Acceptance bullet accordingly.

---

## Items the r2 review did NOT find defective despite hunting

- The `_resolve_arrow_direction_in_body_frame` provisional mapping (`return 90.0 if ... else 270.0`) is acceptable in §Pseudocode because the §Acceptance enforcement bullet AND the IMPLEMENTATION GATE docstring redirect the binding to the citation authority. The literal values in pseudocode are illustrative; the test-binding is via the authority.
- The increased TDD row count (15 → 17) is acceptable; #16 and #17 are independent property assertions adding cross-check value rather than busywork.
- The plan still uses future tense correctly throughout (per `feedback_plan_past_tense_artifact_claims`).
- The 38.8 KB / 332-line size is in line with comparable T3 plans in the index (the workspace-hub#2768 epic plan is 22.8 KB; #2758/#2754/#2755 are similar magnitude).

---

## Overall result: r2 = MINOR (approval-eligible after surfacing to user)

The plan is structurally sound. r1 MAJORs are closed. r2 MINORs are tightening opportunities the implementing agent should address during plan-review, but they do not block surfacing to user for approval.

**Recommended next steps in order:**

1. Surface r2 findings to user (this artifact + summary).
2. User decides: (a) fix the 4 r2 MINORs inline and proceed to issue creation, (b) accept as-is and proceed to issue creation with the MINORs noted as plan-review TODO items, (c) request external provider review (Codex + Gemini) first.
3. If (a) or (b): user creates digitalmodel issue from the issue-draft, transcribes plan to `digitalmodel/docs/plans/2026-05-20-issue-<NNN>-...`, applies `status:plan-review` label.
4. If (c): dispatch Codex + Gemini in parallel against the revised plan.
5. After cross-provider review (whether before or after issue creation), reconcile findings into final revision.
6. **Only then**: user-in-loop approval → `status:plan-approved` → `.planning/plan-approved/<NNN>.md` → implementation.

**Per `feedback_r3_inline_loop_break_pattern`:** I am NOT running a Claude r3 inline. Two inline rounds is the cap. External cross-provider review is the right next adversarial gate if the user wants further hardening; otherwise the plan is approval-eligible at user's discretion.

**Per `feedback_never_offer_to_self_label_plan_approved`:** this artifact does not pre-authorize anything. User remains the sole approval authority.
