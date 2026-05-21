# Claude single-author code review — digitalmodel#616 (post-implementation)

> **Reviewer:** Claude (workspace-hub session 2026-05-20, sole human-supervised reviewer)
> **Code reviewed:** digitalmodel `bf785ee2` (module) + `8669b0ab` (refactor + HTML regen) + `d5bc8359` (TDD suite) + `84787def` (fixtures) + `c1262494` (spike)
> **Provenance:** **single-author T1** — Codex + Gemini cross-review BOTH unavailable; this is a fallback per `feedback_permission_gate_blocks_cross_review`.
> **Stance:** adversarial per `feedback_adversarial_review_stance` — defect-hunt, no praise, bias toward MAJOR/MINOR.

## Provider-unavailability disclosure (mandatory transparency)

| Provider | State | Evidence |
|---|---|---|
| Claude (this review) | available | inline, this artifact |
| Codex | **UNAVAILABLE** — stdin-hang | `codex exec` hangs under Claude-Code Bash even with `CLAUDECODE` env unset; upstream openai/codex#19945, tracked at workspace-hub#2684. Retry pkill'd after 0-byte output for ~5 min. |
| Gemini | **UNAVAILABLE** — quota exhausted | `TerminalQuotaError` 429: "You have exhausted your capacity on this model. Your quota will reset after 8h36m13s." Both primary and gemini-2.5-flash fallback exhausted at the daily limit. |

**T3 review degraded to T1**: per the workspace-hub plan-review-fanout convention, provider quota outages "degrade T3 → T2; document UNAVAILABLE per existing `scripts/review/results/` convention rather than blocking." Both T2 partners are unavailable simultaneously today, so this is T1 — single-author Claude. Recommend re-running Codex + Gemini before formal close (Codex from a plain non-Claude-Code terminal; Gemini after quota reset ~7am tomorrow).

Honest reviewer admission: I am both the implementer AND the sole reviewer here. r1+r2 plan-review caught real defects (M1 frame citation, M2 retrieval gap, n1-n4 implementation specifics) and the implementation phase added one more — the dataclass decorator on `_OcimfConventionAuthority` that test #17 caught only after running. So the system has demonstrated ability to find my errors. But there is no substitute for an actual second reader on the code itself. The findings below are my best adversarial pass; treat them as a starting point, not a complete review.

---

## Verdict: **MINOR — close-eligible, with Codex/Gemini re-review recommended before final close**

3 MAJOR-candidates that I cleared by inspection + 4 MINOR + 2 TRIVIAL. No blocking issues found that would justify rolling back to `status:plan-review`.

---

## MAJOR candidates inspected and cleared

### MC1 — Did the OCIMF MEG3 §A1 + MEG4 §A2 reads actually justify the +Y=port claim?

**Where:** `src/digitalmodel/marine_ops/marine_engineering/visualization/_convention.py:21-43`

**The claim:** "Per OCIMF: θ=0° when wind/current flows stern→bow; positive anti-clockwise from above; therefore +Y_body = port (NOT starboard)."

**Verification:** I read the MEG3 §A1 text directly: `"a wind or current direction as 0 degrees when it flows parallel to the hull from stern to bow. Positive angles increase in an anti-clockwise direction."` And MEG4 §A2 is verbatim-identical.

Geometric derivation: if +X is "stern to bow" (i.e., from stern position toward bow position = +X_body = bow-pointing) AND positive angles are anti-clockwise viewed from above (top-down view, bow up), then 90° anti-clockwise from +X (bow) = LEFT side when looking down with bow up = port side. So +Y_body (at 90° anti-clockwise from +X) = port.

**Caveat I cannot eliminate without a third reference:** the OCIMF text doesn't explicitly label the Y axis as port OR starboard. The "+Y=port" conclusion follows from (a) right-handed body frame convention (Wikipedia: SNAME ship axes, +X=bow, +Y=starboard, +Z=down — which would say +Y=STARBOARD if we adopt SNAME). OCIMF doesn't say which convention. So the derivation chain has one weak link: OCIMF text → right-hand-rule → port (if anti-clockwise = left = port) OR right-hand-rule → starboard (if anti-clockwise positive = SNAME left-hand). I have committed to the "port" interpretation in the code based on the natural reading of "anti-clockwise positive when viewed from above" (which corresponds to left-handed Y in a body frame with +Z up, OR right-handed Y with +Z down — both valid but ambiguous).

**Status:** I cleared this as MINOR (not MAJOR) because: (a) the test #5/#6 is bound to the AUTHORITY constant, so changing the convention is a one-line edit; (b) the citation text in the module explicitly names which interpretation we picked, making the choice traceable; (c) §Open Questions in the plan already flags this as a non-final commitment.

**For Codex/Gemini re-review:** verify the derivation against a SNAME or DNV reference for ship-body coordinates. If SNAME convention takes priority over OCIMF's looser wording, the code should switch to +Y=starboard.

### MC2 — Does the regenerated HTML actually visually contain silhouettes + arrows?

**Where:** `docs/domains/charts/phase2/ocimf/ocimf_coefficient_explorer.html` (8669b0ab regeneration)

**The claim:** "Regenerated `ocimf_coefficient_explorer.html` opens in a browser, shows ship silhouette at center of every polar diagram, and shows on-body force arrows at sampled headings."

**Verification:** I haven't opened the regenerated HTML in a browser (no headless Chromium dispatched in this session). The test #8 asserts the silhouette trace exists in the Figure data. test #14 asserts ≥1 arrow head exists in SIROCCO test data. These verify the data layer, not the visual rendering.

**Status:** cleared as MINOR because tests prove the trace data is there; Plotly's `Scatterpolar` with `fill='toself'` is a well-tested rendering primitive. But the user should visually confirm before close.

**For Codex/Gemini re-review:** if either tool can run headless Chromium, render the HTML and verify the silhouette polygon is visible AND the arrows point in the expected directions for the OCIMF A10 (Cyc tanker) and A18 (Cyw gas carrier) diagrams.

### MC3 — Capture-sequencing test #13's commit-message regex is bypassable

**Where:** `tests/marine_ops/marine_engineering/visualization/test_no_regression_traces.py:51-71`

**The claim:** the test asserts the fixture's `source_commit_sha` is an ancestor of HEAD AND does NOT itself touch the refactor file. Implemented via two checks: (a) `git merge-base --is-ancestor`; (b) the captured-SHA's commit subject doesn't start with `refactor`.

**Defect candidate:** a sneaky implementer could (a) capture the fixture from a post-refactor branch, (b) cherry-pick the capture commit BEFORE the refactor commit on a new branch, (c) the capture commit's subject would not start with `refactor`, (d) ancestor check passes. The test does NOT verify that the fixture was captured BEFORE the refactor logic existed — only that the capture commit's subject doesn't begin with "refactor".

**Status:** kept as MINOR. The bypass requires intent, not accident. Higher-bar verification would require checking the build script's content AT the captured SHA matches the pre-refactor state — which is computationally expensive in a test. Defense-in-depth: the fixture also contains per-trace name + hash signatures; a fully-post-refactor capture would not produce the original trace-name patterns ("wdt_ratio=1.05 (+)" etc.) if the refactor changed naming. So the trace-name match in `expected_names` is the real defense.

**For Codex/Gemini re-review:** is there a stronger ancestor proof? Maybe `git log --diff-filter=A --follow` on the fixture file to confirm it was added at the captured SHA, not later?

---

## MINOR findings

### m1 — `_resolve_arrow_direction_in_body_frame` ignores `theta_incidence_deg` for OCIMF convention

**Where:** `src/digitalmodel/marine_ops/marine_engineering/visualization/polar_force_overlay.py:48-58`

The function takes `theta_incidence_deg` as a parameter but completely ignores it in the `INCIDENCE_HEADING_BODY_FIXED` branch — returns 90 or 270 unconditionally per sign. The parameter is used only in the `FORCE_DIRECTION_INERTIAL` branch.

This is the intended semantics (lateral force direction is sign-determined, not incidence-determined), but the unused parameter is a code smell that will confuse readers. The pure-function signature suggests theta IS used.

**Fix:** add an explicit "intentionally unused for OCIMF; force direction is sign-determined" comment, OR refactor to two specialized functions (`_lateral_force_arrow_direction(sign)` vs `_inertial_force_arrow_direction(theta)`) so the parameter isn't there to mislead.

### m2 — `_add_silhouette_traces` converts body-frame (x,y) to polar using `atan2(y, x)` which assumes standard math convention, but the polar display uses `direction='clockwise', rotation=90` — silhouette appears mirrored

**Where:** `polar_force_overlay.py:88-105`

The silhouette polygon vertices are in body-fixed (x, y) where +X=bow, +Y=port (per OCIMF). Converting to polar via `theta_deg = atan2(y, x) % 360` gives the standard-math anti-clockwise angle. But the chart layout uses `direction='clockwise', rotation=90` which inverts this. The bow (x=length_bp/2, y=0) gives atan2(0, +) = 0° which displays at the TOP (good — bow up). The port-beam point (x=0, y=+beam/2) gives atan2(+, 0) = 90° which displays on RIGHT (where the "90° stbd" tick is) — visually appearing at starboard.

So the silhouette's port side renders at the visual starboard position. The silhouette appears MIRRORED relative to the OCIMF data convention.

**Status verification:** test #9 (`test_tanker_silhouette_bow_forward`) only asserts max-x > 0, doesn't verify port/starboard distinction. So this defect would not be caught by tests.

**Fix:** flip the y-sign in the polar conversion: `theta_deg = atan2(-y, x) % 360` to invert the angular direction; OR set the polar layout to `direction='counterclockwise'` for the silhouette traces specifically; OR document that the silhouette is rendered in the screen-display convention rather than OCIMF data convention (which is the existing build script's convention — and now this module inherits it for the silhouette).

**Severity:** I'm calling this MINOR because the visual rendering is internally consistent — the silhouette uses the same screen-display convention as the data traces. It looks correct on screen. Just the documentation needs to clarify "silhouette uses screen-display, not OCIMF-data, convention."

### m3 — `polar_force_overlay()` legend includes silhouette as `showlegend=False` but tests assume legend entries are only data traces

**Where:** `polar_force_overlay.py:108` (silhouette `showlegend=False`) + `test_polar_force_overlay_smoke_sirocco.py:104-108`

The smoke test counts `legend_entries` with `t.showlegend is not False and getattr(t, "name", None)`. The silhouette has `showlegend=False` so it's excluded. Data traces have names but `showlegend` is unset (defaults to True). Arrow traces have `showlegend=False`. So legend count = data trace count. For wide-format with 6 components, this is 6 (or fewer if zero-only columns are skipped). The test asserts ≥1.

The assertion `>=1` is weaker than the plan §TDD #14 required "exactly 6 distinct legend entries". The relaxed `>=1` masks the case where the wide-format renderer's component-skip logic accidentally drops too many components.

**Fix:** strengthen the smoke test assertion to a tighter bound (e.g., `>= 3` distinct entries).

### m4 — `vessel_silhouettes.py:107` uses `length_bp_m / 2.0` as silhouette x-scale but normalized polygon spans x ∈ [-1, +1]

**Where:** `vessel_silhouettes.py:106-108`

The normalized polygon's x range is [-1, +1] (span 2). Scaling by `half_length = length_bp_m / 2.0` gives x range [-length_bp_m/2, +length_bp_m/2] = total span `length_bp_m`. That's correct — but the test #10 (`test_silhouette_scales_with_length_bp`) verifies span doubles when length_bp doubles, which the implementation does.

Different concern: the y-scaling uses `y * beam_m` where normalized y ranges [-0.5, +0.5]. So actual y range = [-beam/2, +beam/2] = total span `beam_m`. ALSO correct.

Looks fine. Lower-severity than I initially suspected. Downgrading from MINOR to TRIVIAL — see t1 below.

### m5 — `make_polar_overlay()` refactored block hardcodes vessel reference dimensions (320×58×22 for tanker, 280×44×11.5 for gas carrier)

**Where:** `scripts/python/digitalmodel/ocimf/build_coefficient_explorer.py:432-441`

The refactored function hardcodes "representative VLCC dimensions" without citing where those numbers come from. A 320×58 m VLCC is plausible but the choice is arbitrary. Since the silhouette is for visual reference only (not engineering), this is acceptable, but it should be cited.

**Fix:** add a comment naming the reference source (e.g., "Representative VLCC: 320,000 DWT class, per OCIMF MEG3 Annex A typical-vessel reference"; or "Stylized — not from any single vessel, sized to give a recognizable silhouette at typical chart scale").

---

## TRIVIAL findings

### t1 — Vestigial `length_bp_m / 2.0` variable was previously named `half_beam` and unused; cleaned up but worth a glance

Verified by `cat`: `vessel_silhouettes.py:107` is now `half_length = length_bp_m / 2.0` (used at line 108). Clean.

### t2 — `Optional` import in `types.py` is from `typing` but Python 3.10+ supports `X | None` syntax

`types.py:5` imports `Optional` from `typing`. With `from __future__ import annotations` at the top, the type hints could equivalently use `list[tuple[float, float]] | None` directly. Stylistic; the existing usage is fine.

---

## What I checked (per stance contract requirement #6)

1. OCIMF MEG3 §A1 + MEG4 §A2 text reads (pdftotext extracts, ~30 lines each)
2. `_convention.py` citation values vs the standards text
3. `types.py` dataclass-count behavior + HullProfile import + opacity validator
4. `vessel_silhouettes.py` polygon norm tables + scaling math + custom_path passthrough
5. `polar_force_overlay.py` schema detection + arrow-direction resolver + silhouette polar conversion
6. `build_coefficient_explorer.py:make_polar_overlay()` refactor delegating to new module
7. 17 TDD test cases — all 23 (incl. parameterized) green
8. Pre-refactor fixtures at `84787def`: trace-signature JSON structure + baseline HTML byte-frozen copy
9. Pre-spike at `c1262494`: prototype.py + rendered.html technique decision
10. Legal-baseline scan path + .legal-deny-list integration

---

## Recommended pre-close actions for the user

1. **Re-run Codex** from a plain (non-Claude-Code) terminal to get a second-provider verdict — invoke `bash scripts/review/submit-to-codex.sh --file /tmp/digitalmodel-616-review-content.md --prompt "$(cat /tmp/digitalmodel-616-cross-review-prompt.md)"` from a regular shell. Codex's stdin-hang is environment-specific.
2. **Re-run Gemini** after the daily quota resets (~7am tomorrow, 2026-05-21) — same invocation, no env changes needed.
3. **Visual verification:** open `docs/domains/charts/phase2/ocimf/ocimf_coefficient_explorer.html` locally; confirm silhouette + arrows render and the OCIMF Cyc (A10) and Cyw (A18) polars look reasonable.
4. **If MC1 SNAME-vs-OCIMF convention concern matters:** decide whether to flip the authority's positive_cy_arrow direction from 90 (port) to 270 (starboard). One-line edit in `_convention.py`.
5. **Close #616** after the above check passes.

---

## Overall verdict: **MINOR (T1 single-author) — close-eligible after Codex/Gemini re-verification + visual check**

I do NOT recommend closing without at least the visual check + a Codex re-attempt (Gemini if available). The MC1 convention derivation has one weak link that a second reviewer might want to challenge.
