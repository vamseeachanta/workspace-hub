# Adversarial review: plans #2569 / #2570 / #2571

## #2569 — MINOR

**Why:** The plan is close to review-ready as a documentation/source-pack issue, but governance and downstream-contract details need tightening before approval.

**Required revisions**
- Add an explicit **hard-stop / approval gate** section matching the repo pattern used in #2566/#2568: no implementation before review artifacts are published, issue is in `status:plan-review`, and user applies `status:plan-approved`.
- Make dependency handling explicit: **#2569 should not be blocked by #2568**. It may cite #2568 for context, but source-pack extraction is independently executable and should be framed as the prerequisite for #2570/#2571.
- Strengthen the downstream contract for benchmark uncertainty: require the YAML to distinguish `authoritative`, `narrative`, `derived`, and `unrecoverable/unknown` fields, and require nulls plus caveat text when the notes do not support a numeric benchmark.
- Clarify artifact ownership: keeping the durable source pack under `workspace-hub/docs/projects/acma/B1528/` is appropriate; say explicitly that this is the canonical cross-repo citation artifact for later `digitalmodel` work.
- Add a review-readiness criterion that exact remote source paths and any nonrecoverable workbook cell references must be recorded, so #2570/#2571 do not silently promote uncertain values to facts.

## #2570 — MAJOR

**Why:** The engineering scope is plausible, but the plan is not governance-ready because prerequisites, approval gates, artifact placement, and deliverable boundaries are still ambiguous.

**Required revisions**
- Add an explicit **hard-stop / approval gate** section like #2566/#2568. Right now the plan is missing the standard “review-only until approved” control.
- Make **#2569 an explicit blocker**, not just a cited prerequisite. The plan should state that implementation cannot finalize packaged inputs or benchmark/regression claims until the source pack lands and provides canonical values/citations.
- Correct dependency handling for **#2566**: treat it as a **follow-up quality-validation issue, not an implementation prerequisite**. Current wording risks implying approval/validation status carries execution authority for #2570.
- Resolve artifact placement before approval. The plan currently leaves open whether output belongs only in `digitalmodel` or also in `workspace-hub`. That is not review-ready. Required resolution:
  - canonical generated artifacts and executable code in `digitalmodel`
  - cross-project planning/review/source-pack references in `workspace-hub`
  - do **not** make checked-in repo deliverables depend on `digitalmodel/outputs/.../*.html` unless the plan explicitly states whether those HTML files are committed, ignored, or produced only in runtime/manifests.
- Tighten interactive-chart deliverability. “Generate and reference” is too vague for a review gate. Specify whether the durable doc is:
  - markdown linking to generated HTML artifact paths,
  - a reproducible command that regenerates Plotly HTML,
  - and what happens in non-GitHub-renderable contexts.
- Benchmark-source uncertainty is under-specified. Static yaw regression should be against workbook-derived values from #2569, while any breakaway-note comparison must be clearly labeled non-authoritative unless the source pack normalizes it quantitatively.
- Add an acceptance criterion that report text must identify which outputs are **reference regression**, which are **model outputs**, and which are **illustrative sweeps**, so consumers do not mistake the report for validated maneuver prediction.

## #2571 — MAJOR

**Why:** This plan has the highest workflow/governance risk. It depends on unsettled upstream work, mixes model layers, and does not yet have a review-safe dependency and uncertainty story.

**Required revisions**
- Add an explicit **hard-stop / approval gate** section matching #2566/#2568.
- Make dependency order explicit and blocking:
  - **#2569 must complete first** for benchmark/source normalization.
  - **#2570 should complete first** unless #2571 fully duplicates and freezes its own B1528 geometry/source contract.
  - **#2568 is a methodological prerequisite** unless this plan fully restates and owns the first-order Nomoto estimator boundary and tests. As written, it depends on #2568 conceptually but does not state whether #2568 approval/completion is required.
- Resolve the model-boundary ambiguity called out by the plan itself: the current design risks **double-counting** by combining a Nomoto `K/T` model with direct rudder-force/yaw-moment feedback. Before approval, the plan must choose one of these and state the other is excluded, or define clearly separated model variants and outputs.
- Tighten benchmark-source uncertainty handling. The acceptance criteria should require a **source-gap mode** when SIROCCO notes are narrative/non-numeric, with no benchmark overlay fabricated from sparse prose.
- Resolve artifact placement exactly as for #2570. `digitalmodel/outputs/b1528_sirocco/time_trace_report.html` is not, by itself, a governance-ready durable artifact location unless commit/runtime expectations are stated.
- Tighten interactive deliverability requirements: specify reproducible generation command, expected manifest/provenance links, and how report consumers reach the HTML output from the durable markdown doc.
- Add a plan-review readiness criterion that time-trace outputs are **descriptive preliminary simulations only**, not incident reconstruction, and that no calibration to SIROCCO notes occurs unless the calibrated parameters and evidence source are explicitly documented in #2569 artifacts.

## Cross-issue workflow assessment
- **Best candidate for near-term approval:** #2569 after minor revisions.
- **Not ready for approval:** #2570 and #2571.
- **Dependency chain should be explicit in the plans/issues:** `#2569 -> #2570 -> #2571`, with `#2568` as methodological prerequisite for `#2571`, and `#2566` as post-implementation validation/hardening rather than execution authority.
- The biggest governance gap across all three drafts is missing or inconsistent **approval-gate language**. #2566/#2568 already establish the expected pattern; #2569/#2570/#2571 should match it before plan approval.
