## Verdict
MINOR

## Retrieval
- Read `docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md` lines 1-235 (entire plan).
- Read `docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md` lines 1-80 (Source-Data Surface + Output-Format Manifest + Chart C1).
- Verified data-input claims via `ls digitalmodel/examples/demos/gtm/data/` and `ls digitalmodel/examples/demos/gtm/results/` — `pipelay_vessels.json`, `csv_hlv_vessels.json`, `vessel_comparison_matrix.json`, `structure_comparison_matrix.json` all present.
- Verified Demo 4 chart precedent via `ls digitalmodel/examples/demos/gtm/output/` — `demo_04_shallow_pipelay_report.html` exists.
- Verified live issue state via `gh issue view 2555/2556` — both OPEN, label set as plan asserts.
- Counted actual storyboard chart concepts via `grep -nE "^#+ Chart C"` — 4 charts, all at heading depth 3 (`### Chart C1..C4`).
- Cross-checked storyboard headline-number claim against `vessel_comparison_matrix.json` via `jq '.vessels[] | select(.name | test("Shallow"; "i"))'` — Shallow Water Barge `pass_rate_pct: 100.0, cases_pass: 30, cases_total: 30` confirmed exactly as the storyboard caption claims.
- Read `scripts/review/plan-review-fanout.sh` lines 1-205 to confirm AC #5 expected artifact path shape.

## Findings

1. **TDD Test List grep pattern is off-by-one heading depth.** Plan §172 row 1 specifies `chart_count_ge_3 | grep ^## Chart C count in storyboard`. The storyboard renders chart concepts at heading depth 3 (`### Chart C1`, `### Chart C2`, …), not depth 2. The plan's literal `grep` returns **0**, not 4. The check is supposed to be falsifiable; as written it falsifies the artifact rather than the data. Patch: change `^## Chart C` to `^### Chart C` (or `^#+ Chart C`). Same defect class as #2554 plan §155 row 1 — both plans share an automatable-check authoring miss.

2. **Acceptance criterion #5 (cross-provider review) is unmet by any wave that lacks Codex and Gemini live evidence.** Plan §197: *"Cross-provider adversarial review run (Claude + Codex + Gemini) before any `status:plan-review` label is applied. Until then, status remains `draft`."* The current next-wave run produced Claude self-review only (sibling Codex/Gemini artifacts UNAVAILABLE per documented lane-permission and upstream-regression risks). Per the literal AC, the plan cannot be promoted to `status:plan-review` on this wave. No revision required — the plan must wait for a permitted lane to drive a Codex or Gemini run, or AC #5 must be revised to admit a documented UNAVAILABLE provenance fallback.

3. **Chart-rendering implementation home is unspecified, in tension with the "no `digitalmodel/` edits" rule.** Plan §165 declares `digitalmodel/examples/demos/gtm/**` *out of scope* for this plan's lifecycle ("NO edits"). Storyboard §145 pseudocode says `figure = render(C.style, inputs, headline)  # Plotly or matplotlib via report_template.py`. The named module lives at `digitalmodel/examples/demos/gtm/report_template.py`. Two interpretations: (a) chart rendering *imports* `report_template.py` from a new entry-point that lives outside `digitalmodel/` — the plan should name that entry-point path; or (b) chart rendering edits `report_template.py` to add brochure-grade export — which contradicts the "NO edits" rule. The follow-on plan-approved slice cannot start until this ambiguity is resolved.

4. **Brochure-asset target directory `docs/reports/gtm/assets/` does not yet exist and the plan does not enumerate the mkdir gate.** Storyboard §47 states "brochure assets live under `docs/reports/gtm/assets/` once rendered." `ls docs/reports/gtm/` shows only the storyboard + the sibling #2554 scaffold; `assets/` is missing. Not blocking for this draft plan, but the follow-on implementation slice should include directory creation in its Files-to-Change.

5. **Standards-citation contract not extended to chart captions.** Plan §28-32 inherits standards citations (DNV-ST-F101, DNV-RP-H103, DNV-ST-N001, API RP 1111) from the upstream JSON `_references` arrays. Storyboard caption draft for C1 cites three of those four (`DNV-RP-H103, DNV-ST-N001, DNV-ST-F101`) but omits API RP 1111 even though shallow-water S-lay screening (one of the three jobs in the heatmap) inherits that standard. Either the caption should add API RP 1111 or the storyboard should explain why it is intentionally omitted (e.g., scope-limited to deepwater jobs). This is a defensibility-of-claims issue surfaced by the calc-citation contract spirit, even though that contract is not formally binding for GTM artifacts.

## Blockers

- Finding 2 (AC #5 unmet without Codex+Gemini evidence) blocks `status:plan-review` promotion of #2555 by the plan's own contract. Findings 1, 3, 4, 5 are MINOR and can be patched alongside the AC reconciliation.

## Notes

- This artifact was produced by the **Claude main session** acting as an adversarial reviewer (planning-only lane; no permission to drive `scripts/review/plan-review-fanout.sh`). It is NOT a clean-room headless `claude -p` run. Reviewer independence is therefore weaker than a true cross-author CLI invocation. Treat findings as a self-audit, not a true cross-author review.
- One positive verification worth noting (not a finding): the storyboard's headline-number claim "Shallow Water Barge: 100% pass rate across 30 cases for 8-24 in pipe at 7-30 m water depth" is grounded in `digitalmodel/examples/demos/gtm/results/vessel_comparison_matrix.json` (vessel name match, pass_rate_pct = 100.0, cases_total = 30). The pipe-size and water-depth range portions of the claim were not verified this wave; deep verification belongs in the follow-on plan-approved slice.
- Codex and Gemini artifacts for this wave (`2026-04-29-plan-2555-nextwave-codex.md` / `-gemini.md`) are written as UNAVAILABLE per the canonical fanout-script shape.
