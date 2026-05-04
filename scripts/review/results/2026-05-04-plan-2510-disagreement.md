# Disagreement report — plan #2510 (2026-05-04)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | MINOR |
| codex | MAJOR |
| gemini | UNKNOWN |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

- **[MINOR] r14 P2 finding 5 (with_metadata sidecar) not patched — §GDS Round-Trip Contract does not specify `write_gds(with_metadata=...)` invocation.**
-    Location: §GDS Round-Trip Contract (lines 186–194) and §Pseudocode `write_exchange_artifact` (lines 217–223).
-    Evidence: r14 finding 5 identified that GDSFactory 9.40.2's `Component.write_gds` has a hidden `with_metadata=True` default that can emit a YAML sidecar alongside the GDS. The plan patches the 3 P1 findings from r14 but leaves P2 finding 5 unaddressed — the `write_gds` invocation in pseudocode line 222 says only "write chip_package_demo.gds" without specifying `with_metadata=False`. An implementer could produce unenumerated sidecar files that break the manifest invariant or determinism tests.
-    Risk: low-to-medium. The sidecar may not appear for simple geometries (per r14 probe), but the plan's own determinism contract (line 396: "do not serialize wall-clock timestamps into checked-in metadata") and manifest contract (only explicitly enumerated artifacts) become ambiguous without pinning this parameter.
- **[MINOR] r14 P3 finding 8 (geometry_summary.csv column schema) not patched — CSV determinism is unfalsifiable.**
-    Location: §Determinism Contract line 395, §TDD `test_outputs_are_deterministic_across_runs` line 274.
-    Evidence: the plan says "geometry_summary.csv must contain only deterministic geometry rows/columns" but never enumerates the column names, types, or sort key. The determinism test relies on byte-identical output across two runs, which requires a frozen column schema, yet the plan leaves this to implementer discretion. Two compliant implementations could produce structurally different CSVs that both pass in isolation but fail if anyone regenerates from a different starting point.
-    Risk: low. Within a single implementation the byte-equality test will enforce consistency, but the plan's falsifiability standard (which it explicitly names as a goal) is not met for this artifact.
- **[MINOR] r14 P2 finding 6 (kfactory stderr noise on second-run) not patched — `test_outputs_are_deterministic_across_runs` may be flaky.**
-    Location: §TDD test `test_outputs_are_deterministic_across_runs` (line 274), §Determinism Contract (lines 390–401).
-    Evidence: r14 found that kfactory logs `ERROR | Name conflict in kfactory.kcell::name` to stderr when the same component name is constructed twice in one process (PDK cell registry persists). The two-run test defined in the TDD list compares outputs in "two temp dirs" but does not specify whether this means two subprocesses or two calls in one pytest session. If in-process, the test hits cell-registry noise. The plan does not mandate a subprocess isolation strategy or logger silencing.
-    Risk: low-to-medium. An implementer is likely to discover this empirically, but the plan should have anticipated it since the r14 review explicitly flagged it.
- **[MINOR] Current 2026-05-04 canonical review artifacts are 0 bytes — plan header says "r15 adversarial review pending" but the r15 fanout has already run and produced empty/failed results.**
-    Location: plan header line 3 ("r15 adversarial review pending") vs filesystem `scripts/review/results/2026-05-04-plan-2510-{claude,codex,gemini}.md` (all 0 bytes).
-    Evidence: the three canonical artifacts dated 2026-05-04 (today) are all 0 bytes. The plan's own §Pre-Approval Review Artifact Checklist (lines 382–386) says "canonical unsuffixed files must not be 0 bytes after the review command completes; transient 0-byte placeholders … must be replaced by provider output or a non-empty `UNAVAILABLE` artifact before committing or requesting approval." The current state violates this checklist — and this review itself is the r15 evidence being produced to replace one of those empty files.
-    Risk: process-hygiene only. This is not a plan-content defect but a state-drift between the plan's traceability claims and the actual filesystem. The plan should acknowledge that its canonical artifacts are currently in an intermediate state awaiting this review wave's completion.
- **[MINOR] Plan header (line 3) says `plan-review` but r14 finding 4 noted the GitHub label is `status:plan-approved` — label-vs-plan drift persists unresolved.**
-    Location: plan header line 3 vs GitHub label (per r14 retrieval, `gh issue view 2510 --json labels` returned `status:plan-approved`).
-    Evidence: r14 P2 finding 4 identified this drift and recommended relabeling. The plan's r14 patch notes (line 362) mention extending forbidden-phrase tests and adding PDK activation but do not mention resolving the label drift. The label may have been fixed since r14 was written (I cannot verify live GitHub state), but the plan body does not record the resolution.
-    Risk: low. This is a process artifact, not a technical implementation blocker.
- **[MINOR] Forbidden-phrase test exemption mechanism is ambiguous between two mutually exclusive strategies.**
-    Location: §TDD line 277, last paragraph of the test description.
-    Evidence: the test description says the canonical limitation sentence "must be exempted by being inside a known-disclaimer block that the test allowlists, **or** rephrased so that none of the bare tokens appear at all." It then gives example wording `not a foundry or PDK signoff flow and not evidence for manufacturing release` which itself contains the bare tokens `signoff` and `manufacturing release` (both in the forbidden list). The plan doesn't specify which strategy the implementer should use or provide a concrete allowlist-block marker syntax. An implementer choosing the "rephrase" path must avoid the example wording, while one choosing the "allowlist" path needs a marker format (e.g., `<!-- disclaimer-begin -->`) that is never specified.
-    Risk: medium. This directly affects whether the test as written can pass with any real disclaimer text. The implementer will need to make a design decision that the plan punts on. However, the two options are clearly stated and an implementer can resolve this at implementation time without plan revision.

### codex

- `docs/plans/README.md` is stale relative to the plan it indexes. The #2510 row still says `r13 MAJOR findings patched, r8-r13 archived, r14 review pending after push`, while the plan header says `r14 MAJOR findings patched ... r15 adversarial review pending`. The plan’s own §Files to Change requires updating `docs/plans/README.md`, and §Review Routing and Traceability Policy depends on committed canonical plan/index state before approval routing. This state drift can send reviewers to the wrong wave and is not approval-gate clean.
- §GDS Round-Trip Contract and §Determinism Contract still do not pin the full `Component.write_gds(...)` invocation, including `with_metadata` and `no_empty_cells`. r14 finding 5 specifically identified that the recorded probe hides the determinism-relevant `with_metadata=True` default. The current plan only says to pass `save_options` with `gds2_write_timestamps=False`; it does not require `with_metadata=False` or a test that no unmanifested GDSFactory sidecar files appear in `--output`. This leaves a manifest-completeness hole for generated artifacts.
- §Determinism Contract says `test_outputs_are_deterministic_across_runs` satisfies the two-run byte-diff probe, but the plan still does not address r14 finding 6: kfactory can emit `Name conflict ...` errors to stderr when constructing the same component name twice in one process. The plan gives no requirement to reset the PDK/cell registry, create unique deterministic cell scopes, or assert clean stderr on the second run. That makes the same-process determinism test under-specified and potentially flaky.
- §Determinism Contract says `geometry_summary.csv` must contain deterministic rows/columns, but no required CSV schema or row-sort key is specified. The TDD row `test_cli_regenerates_artifacts_manifest_and_report` only checks that the CSV exists. This leaves the CSV contract too loose for a checked-in deterministic artifact: two incompatible column sets could both satisfy the plan.

### gemini

(no findings unique to this provider)

