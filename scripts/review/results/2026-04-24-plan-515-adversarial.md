# Adversarial Review — Plan for Issue #515

## Verdict
`MINOR`

## Defect Checklist

- **Scope drift** — Path-common scope (claim-boundary doc + registry + reconciliation test) is tightly aligned with Gaps #1/#2/#8 from intel. Approach A explicitly widens to OQ-1..OQ-4 resolution, but that expansion is presented as a user tradeoff (not silently claimed). However, acceptance criterion "OQ-2: measured Groups gap for at least one pipeline + one riser model, recorded in registry `known_diffs`" (line 255) adds *measurement work* for #519's charter without citing a test in the TDD list — subtle drift into #519 even in Approach A. **MINOR drift.**

- **Evidence gaps** — Multiple count/type discrepancies inherited-or-introduced relative to ground truth (the source code itself):
  - Plan line 16 says `_SKIP_GENERAL_KEYS` contains **34** view/display keys. Actual file (`generic_builder.py:115-149`) contains **22** keys (regex-verified: `awk 'NR>=115 && NR<=149' ... | grep -oE '^\s*"[A-Za-z]+"' | wc -l` → 22). The intel file (line 11) also says 34; the plan propagates the error without independently verifying. TDD acceptance `test_skip_general_keys_documented_in_taxonomy` says "all 34 keys present in taxonomy; 0 unlisted" (line 219) — the number 34 is baked into test success criteria, so this drift will cause the test to fail or be silently amended.
  - Plan line 21 and pseudocode line 97 describe `Significance` as an `Enum` (`class Significance(Enum)` / "Significance enum"). Actual code (`semantic_validate.py:101-108`) defines it as a plain class with string constants: `class Significance: MATCH = "match" ...` — **not** `Enum`. This affects any plan-implied consumer treating it as `Significance.MATCH` with `.value` semantics.
  - Plan line 17 cites `environment_builder.py:49-159` as covering `_DEFAULTS`, `_SAFE_RAW_OVERLAY_KEYS`, and `_WIND_SPEED_DORMANT`. Actual: `_WIND_SPEED_DORMANT` is at line **160** (outside the range). Minor.
  - Plan intel claim of `_DEFAULTS` holding "21" values — unverified by this review beyond line start confirmation. Plan acceptance criterion line 234 repeats "21" verbatim; if the count is off by the same magnitude as `_SKIP_GENERAL_KEYS`, the licensed-win-1 test will reference a wrong cardinality.

- **TDD completeness** — Path-common acceptance AC "`SEMANTIC_EQUIVALENCE_CLAIM_BOUNDARY.md` exists and enumerates (a) per-family claim level, (b) legitimate claims, (c) forbidden claims, (d) enforcement" has no test asserting its internal structure (only a cross-link test for #2476). "Plan and outputs do NOT re-invent SEMANTIC_DIFF_TAXONOMY.md" AC has no test. Approach-A AC "OQ-2: measured Groups gap for one pipeline + one riser" has no TDD entry. **MINOR — three ACs unmapped.**

- **Missing edge cases** —
  - What happens if a taxonomy parser encounters a key listed twice (e.g., under both C3 and COSMETIC)? `test_allowed_diff_props_superset_of_skip_general` does not specify precedence.
  - `_WIND_SPEED_DORMANT = {"Full field"}` is a single-element set of a *wind-type value*, not a property name. The reconciliation test (`test_wind_speed_dormant_classified`) treats it as though its members are property keys ("`_WIND_SPEED_DORMANT` entries appear under Environment/C3 in taxonomy") — category mismatch. This will either fail or force artificial taxonomy entries.
  - Pseudocode `values_equal(True, 'Yes')` assumes case-sensitive `'Yes'`. OrcaFlex emits exactly `Yes`/`No` via `OrcaFlexDumper`, but user-edited specs may contain `yes`/`true`/`YES`. Plan does not specify whether `values_equal('yes', True)` should also match. Silent decision.
  - Registry schema (`MODEL_CLAIM_REGISTRY.yaml`) lacks a version/schema-version field. Future additions will break `test_model_claim_registry_schema_valid` with no migration path.

- **Coupling risk** — Approach A modifies `semantic_validate.py:357` (`values_equal`) which is called from at least 9 call sites (lines 402, 443, 477, 587, 728, 825, 845, 980). Plan flags the risk (line 315) and asks adversarial review to force a back-compat story, but provides none itself. Acceptance criteria do not require re-running 2454/2455/2456/2457 proofs — this is self-acknowledged hole. Approach A proposes modifying `environment_builder.py` for OQ-1 (`VerticalWindVariationFactor`) but tests cite `generator output on a01` only — one-model evidence for a cross-family generator change.

- **Past-tense drift** — None found. All proposed artifacts are future-tense ("Create", "this plan creates"). Gap-proof section uses past tense appropriately for the intel-pod reconnaissance that already happened ("→ missing → confirms"). Clean.

- **Self-labeling** — None. No claim of `status:plan-approved`. Line 300 explicitly says "Decision required from user before Wave 3 review." Clean.

- **Plan-vs-intel contradiction** — Plan faithfully reproduces intel's claims including intel's own unverified numbers (34 skip keys, 21 defaults, 20 unmapped sections, Significance=Enum). Plan cites one additional doc (`2026-04-01-orcawave-orcaflex-intensive-plan.md`) not in intel, but it is a pre-existing plan and plausibly applies. No new source claims. However: plan's pseudocode introduces `class Significance(Enum)` in triple-backticks (line 97) — the intel says "Significance enum" (lower-case, colloquial), the plan escalates to a type-claim (`Enum` as base class) that is demonstrably wrong. This is plan-level invention beyond intel.

- **Complexity mismatch** — T2 is defensible for Approach B (3 files, no source changes). For Approach A the plan itself admits "T2-high (potentially T3 if all four OQs close in one pass)" and fences explicit promotion (line 330). That transparency is correct, but the TDD list and AC table do not label which rows are A-only clearly until after the file — someone reading only Files-to-Change may still misjudge scope.

- **#515-specific existing-taxonomy tradeoff** — ✅ Clean. Line 286 explicitly presents Approach A vs B, preserves the fact that `SEMANTIC_DIFF_TAXONOMY.md` already exists under `#517 (parent: #515)`, lists pros/cons/complexity for each, and states "Decision required from user before Wave 3 review." Planner recommendation (line 300) is expressed as conditional on user preference, not silent. This is the plan's strongest section.

## Specific Defects Found

1. **Line 16** — Plan claims `_SKIP_GENERAL_KEYS` has 34 keys. Actual count is 22 (verified by regex on `generic_builder.py:115-149`). (a) Plan Resource Intel line 16 + TDD line 219 + Gap Proof. (b) Wrong cardinality; `test_skip_general_keys_documented_in_taxonomy` will assert the wrong count, and the claim-boundary doc will enumerate 12 phantom skip keys that don't exist. (c) Re-count the set before implementation; update both plan and test to the actual count.

2. **Lines 21, 97-98** — Plan asserts `Significance` is an Enum (`class Significance(Enum)`). Actual: plain class with string-constant attributes. (a) Resource Intel line 21; pseudocode block line 97. (b) Any code that imports `from enum import Enum` to type-hint against `Significance` will fail; `Significance.MATCH.value` access pattern won't work. (c) Correct to "class with string constants" or reify the class as a real Enum as a separate in-scope task.

3. **Line 17** — Cites `environment_builder.py:49-159` as covering `_WIND_SPEED_DORMANT`. Actual file line for `_WIND_SPEED_DORMANT` = 160. (a) Resource Intel line 17. (b) Off-by-one citation; reader can't jump to line. (c) Change to `:49-165` or cite `_WIND_SPEED_DORMANT` separately at `:160`.

4. **Pseudocode line 147 / TDD line 222** — `_WIND_SPEED_DORMANT = {"Full field"}` is a *wind-type value* (what `WindType` is set to for dormancy check), not a set of property names. Treating it as property keys that must appear in Environment/C3 taxonomy is a category error; this test cannot succeed as written. (a) TDD line 222 `test_wind_speed_dormant_classified`. (b) Reconciliation logic conflates different kinds of set membership. (c) Rewrite: assert `_WIND_SPEED_DORMANT` values correspond to documented dormancy states in taxonomy's Environment section, not to property-name buckets.

5. **AC line 255 (Approach A)** — "OQ-2: measured Groups gap for at least one pipeline + one riser model, recorded in registry `known_diffs`". No corresponding TDD entry. (a) Acceptance Criteria Approach-A-only. (b) Orphan AC with no test. (c) Add `test_groups_gap_measured` or move OQ-2 into Approach B's deferred list.

6. **AC line 234** — "each of the 21 `_DEFAULTS` matches OrcFxAPI-exported blank-model default". Count "21" inherited from intel without independent verification. If the same kind of count drift as defect #1 applies, the test name encodes a wrong cardinality. (a) TDD line 234. (b) Unverified numeric specifier. (c) Re-count `_DEFAULTS` before baking "21" into test.

7. **Risk line 315 acknowledges `semantic_validate.py` coupling but AC does not enforce back-compat** — plan flags the risk that `values_equal` changes may re-classify prior test verdicts (2454/2455/2456/2457) but provides no AC requiring those proofs to re-run. (a) Risks section line 315 vs AC lines 242-262. (b) Self-acknowledged hole; Approach A could silently reverse approved proofs. (c) Add AC "All prior per-family proofs re-run post-`values_equal` change; deltas reviewed."

8. **Pseudocode values_equal assumes bool/str case-canonical `Yes`/`No`** — no handling for `yes`/`true`/`YES`/`Y` or whitespace variants; also doesn't specify what happens for `values_equal(True, 'yes')`. (a) Pseudocode lines 176-182. (b) Under-specified contract. (c) Document normalization rule: exact string `'Yes'`/`'No'` only, or explicit case-insensitive with a whitelist.

9. **Registry schema lacks versioning** — `MODEL_CLAIM_REGISTRY.yaml` (line 155) has no `schema_version` or equivalent. (a) Pseudocode line 155. (b) Future schema evolution will break `test_model_claim_registry_schema_valid` with no migration path. (c) Add top-level `version: 1` and assert it.

10. **AC "do NOT re-invent SEMANTIC_DIFF_TAXONOMY.md" is unenforced** — acceptance line 246 states the plan must not re-invent taxonomy, but no test prevents it. (a) Path-common AC bullet 5. (b) Reviewer-enforced only, not machine-enforced. (c) Add script/CI check that SEMANTIC_DIFF_TAXONOMY.md is unchanged (Approach B) or only header-augmented (Approach A).

## Verdict Justification

`MINOR` — not `MAJOR`:
- The existing-taxonomy tradeoff is **presented to the user**, not silently picked (line 286, explicit Approach A/B with pros/cons/complexity; strongest section of the plan). This is the single most load-bearing #515-specific criterion and it passes.
- No past-tense drift, no self-labeling, no scope-drift beyond Approach A's acknowledged expansion.
- TDD covers most of Path-common acceptance; three AC rows are unmapped (Groups gap measurement, claim-boundary doc structure, no-reinvention constraint).

Not `APPROVE`:
- **Numeric/type citations are demonstrably wrong**: `_SKIP_GENERAL_KEYS` count (34 → actual 22), `Significance` as `Enum` (plain class), `_WIND_SPEED_DORMANT` line citation (159 → 160), `_WIND_SPEED_DORMANT` treated as property-name set when it's a wind-type value set. These aren't "hallucinated file paths" at the promote-to-MAJOR threshold (paths and line ranges mostly resolve), but they are **hallucinated quantities and types** baked into TDD acceptance criteria. The TDD list will produce wrong-count assertions as written.
- Back-compat story for `values_equal` modification (Approach A) is self-acknowledged but unenforced by any AC.

Defects are fixable without re-architecture (re-count, re-word, add 3 ACs, fix one test design error) — therefore `MINOR`.
