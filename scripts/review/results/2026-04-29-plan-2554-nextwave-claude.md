## Verdict
MINOR

## Retrieval
- Read `docs/plans/2026-04-29-issue-2554-vessel-contractor-outreach-matrix.md` lines 1-214 (entire plan).
- Read `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md` lines 1-80 (boundary decision + first 3 targets) and ran `grep -nE "^#+ Target " ...` over the full file.
- Verified file-existence claims in plan §"Evidence (embedded verification)" via `ls digitalmodel/examples/demos/gtm/`, `wc -l docs/gtm/outreach-candidate-briefs-2026-04-28.md`, `ls scripts/legal/`.
- Verified live issue state via `gh issue view 2554/2556` — both OPEN, label set as plan asserts.
- Counted actual scaffold targets and High-priority entries via `grep -c` (22 targets, 10 High-priority entries).
- Read `scripts/review/plan-review-fanout.sh` lines 1-205 to confirm AC #5's expected artifact path shape.
- Cross-checked plan's "Test List" §155-167 grep patterns against the rendered scaffold heading shape.

## Findings

1. **Test List row 1 grep pattern is off-by-one separator.** Plan §155 row 1 specifies `grep -c "^### Target — " docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md` to verify "count_targets ≥ 20". The scaffold actually renders headings as `### Target 1 — Subsea7`, `### Target 2 — TechnipFMC (Subsea)`, etc. — there is a target *number* between the word "Target" and the em-dash. The plan's literal `grep` pattern returns **0**, not 22. The check is supposed to be falsifiable; as written, it falsifies the artifact rather than the data. Patch is one character (`"^### Target [0-9]" `or `"^### Target "`).

2. **Internal inconsistency on High-priority count: 9 vs 10.** Scaffold line 376 ("Targets in `outreach_priority: High`: 9") and the lane summary at `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2554-summary.md` both state **9** High-priority targets, naming "Subsea7, TechnipFMC, Saipem, McDermott, Allseas, Heerema, Boskalis, DOF Group, Sapura Energy, Helix". That list contains **10** names. Direct grep `^- \*\*outreach_priority\.\*\* \*\*High\*\*` over the scaffold returns **10** matches. Either the count is wrong or one of the named contractors is not actually flagged High in the row body. This will surface as a discrepancy in any downstream automation that joins the matrix to brochure-send routing.

3. **Acceptance criterion #5 is unmet by any review wave that lacks both Codex and Gemini.** Plan §177 states: *"Adversarial review artifacts exist for Claude + at least one of Codex/Gemini at scripts/review/results/2026-04-29-plan-2554-*.md."* The current next-wave run produced Claude self-review only; both Codex and Gemini are UNAVAILABLE this wave (see sibling artifacts). Per the literal AC, the plan cannot be promoted to `status:plan-review` on this wave. The plan should either (a) wait for a permitted lane to drive a Codex or Gemini run, or (b) loosen AC #5 to admit a documented UNAVAILABLE provenance fallback, mirroring the `aces-2`/`aces-3`/`aces-4` precedent already cited in §225.

4. **Pseudocode evidence-URL gate is satisfied in letter but not in spirit.** Plan §107 pseudocode: `validate evidence_urls is non-empty before promoting High priority`. Every High-priority row in the scaffold carries at least one URL — but every URL is a corporate-domain root (`https://www.subsea7.com/`, `https://www.technipfmc.com/`, etc.), not a deep-link to a fleet/project page that actually substantiates the pain-point hypothesis. The scaffold's own URL-handling note (§41) explicitly defers deep-link verification to "matrix-fill execution work that follows plan approval". This means the High-priority gate is currently passing on URLs that prove only that the contractor exists — not that the named pain-point is grounded. Either the gate should require deep-link evidence (consistent with the brief contract that descends from `outreach-candidate-briefs-2026-04-28.md`), or the AC should be split: "non-empty URL at plan-review" vs "deep-link evidence at plan-approved".

5. **No traceability from `pain_point_hypothesis` to a citable public source.** Each scaffold target carries a pain-point hypothesis (e.g., for Subsea7: "Deepwater installation contractors face decision-cost pressure on go/no-go for marginal sea-states across the lift envelope…"). These hypotheses are bounded by the plan's "public-evidence-bounded — never invented" rule (§120), but the scaffold does not attach an evidence URL or repo path to each hypothesis. A reader cannot tell which hypotheses are cross-walked from a public source vs. inferred from the demo set vs. drawn from operator memory. Recommend adding a `pain_point_evidence:` slot per row, even if v1 ships with `inferred-from-demo-coverage` placeholders for most rows.

## Blockers

- Finding 3 (AC #5 unmet without Codex/Gemini evidence) blocks `status:plan-review` promotion of #2554 by the plan's own contract. This is the controlling blocker for this wave. Findings 1, 2, 4, 5 are MINOR and can be patched alongside the AC reconciliation.

## Notes

- This artifact was produced by the **Claude main session** acting as an adversarial reviewer (planning-only lane; no permission to drive `scripts/review/plan-review-fanout.sh`). It is NOT a clean-room headless `claude -p` run. The reviewer was the same agent that also drafted the next-wave summary; reviewer independence is therefore weaker than a separate CLI invocation. Treat findings as a self-audit, not a true cross-author review.
- Codex and Gemini artifacts for this wave (`2026-04-29-plan-2554-nextwave-codex.md` / `-gemini.md`) are written as UNAVAILABLE per the canonical fanout-script shape and reflect (a) lane permission restriction + (b) known upstream regressions per `feedback_codex_cli_0_124_upstream_regression.md` and `feedback_gemini_sandbox_overlay_blindness.md`.
