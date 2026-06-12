### Verdict: MAJOR

### Summary
A well-scoped, heavily-reviewed Phase A contract-surfaces plan with strong TDD coverage, an exhaustive schema occurrence-disposition table, and clean deferral of enforcement to #3013. One fail-closed gap (ungated public input_residency) and a few under-specifications should be resolved before r6 approval; the rest is minor.

### Issues Found
- [P2] Fail-closed gap: line 195 adds `public_federal_wiki` to execution-manifest `input_residency` (line 55) as 'vocabulary symmetry only, not a guard predicate.' Output residency is guarded (lines 162/179) but a public INPUT residency value is introduced with neither a guard nor a consumer-blocking note — a potential private-to-public input-laundering vector left unaddressed in a fail-closed system. No test covers ungated public input_residency.
- [P3] `publication_sequence` is under-specified: `test_publication_sequence_is_machine_readable` asserts 'required keys and strictly increasing order,' but the plan never defines the order key or the per-stage key schema, so the test is unverifiable against an unspecified contract.
- [P3] Public-safe policy is double-represented (per-value `public_safe` flag AND `public_safe_source_publication_classes`/`public_safe_license_terms_classes` lists), relying on a consistency test rather than a single source of truth; this is the kind of dual-write the externalize-config discipline usually collapses to one representation.
- [P3] `test_config_defines_exact_enum_values` hardcodes the plan's exact enum values into a contract test, making any future additive enum change require a coordinated test edit; acceptable as a deliberate contract lock but worth noting as brittleness.
- [P3] Minor narrative inconsistency: line 15 says 'after r1-r8 adversarial review' (the prior omnibus) while the Adversarial Review Summary scopes this plan to an independent r1-r5; a reader could conflate the two histories.

### Suggestions
- Either add a guard (or an explicit consumer-blocking note + test) for public_federal_wiki used as execution-manifest input_residency, or state in the plan why input residency needs no guard and defer it to #3013 with the same prose-note treatment given to output residency.
- Specify the publication_sequence stage record shape in the plan (e.g., `stage_id`, `order: int`, `target_residency`, `target_wiki`) so `test_publication_sequence_is_machine_readable` tests a defined contract rather than an implied one.
- Consider single-sourcing public-safe membership (derive the policy lists from per-value flags at load time, or vice versa) so the consistency test guards an invariant rather than reconciling two hand-maintained representations.
- Reconcile the line-15 'r1-r8' phrasing to clearly attribute it to the prior omnibus plan, distinct from this Phase A r1-r5 sequence, to avoid review-history confusion at r6.

### Questions for Author
- Why is public_federal_wiki safe to admit as an execution-manifest input_residency without a guard? What prevents a manifest from declaring a private source while marking input_residency public_federal_wiki to bypass downstream egress checks once #3013 enforcement lands?
- What is the concrete record schema for each publication_sequence stage, and how is 'strictly increasing order' encoded (explicit integer key vs. list position)?
- After the const-to-enum guard broadening, has the JSON Schema if/then mechanics been validated so that public_federal_wiki triggers the identical promotion-gate `then` block as public_llm_wiki (i.e., the enum match in the `if` predicate fires correctly for both values)?
- Given Gemini has returned NO_OUTPUT across all five rounds, is the T2 (Claude+Codex) coverage acceptable to the owner for a plan that introduces a new public-data egress route, or should a third provider be attempted at r6 before approval?
