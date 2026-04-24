# Adversarial Review — Plan #486 (Subsea Connectors & Jumpers, API 17R)

**Reviewer stance:** Adversarial / defect-hunter. Charitable reading suspended.
**Plan under review:** `docs/plans/2026-04-24-issue-486-subsea-connectors-jumpers-api17r.md`
**Intel:** `/tmp/orca-batch-2026-04-24/intel-486.md`
**Issue JSON:** `/tmp/orca-batch-2026-04-24/issue-486.json`
**Date:** 2026-04-24

---

## Verdict

**MINOR** — plan is fundamentally sound on the high-stakes axes (hard-gate ledger call, dual-path delivery, greenfield verification, no hallucinated 17R clause citations), but contains a cluster of specification defects that must be tightened before implementation. No APPROVE because several Acceptance Criteria and TDD entries are unfalsifiable or phrased so loosely that "done" is a matter of interpretation, and Path-A/Path-B convergence is not cleanly preserved through the Files-to-Change list.

---

## #486-Specific Hard-Gate Checklist

| # | Hard-gate question | Result | Evidence |
|---|---|---|---|
| H1 | API 17R ledger gap surfaced as MANDATORY user gate? | **PASS** | Risks §[TRADEOFF FOR USER] lines 291-298 explicitly states "This is a hard gate, not a design choice. User must pick one of two paths" and "Neither the Planner nor downstream implementers may self-select this path. User decides during plan-approval." Standards table (line 34) marks 17R "load-bearing blocker". |
| H2 | Both Path A (procure 17R) and Path B (pivot to 17B/17J/17K/F101/F105/B31.8) presented? | **PASS** | Risks §[TRADEOFF FOR USER] lines 294-296 both options enumerated with pros/cons; Deliverable §lines 144-146 restates both; Acceptance Criteria has distinct Path-A-only and Path-B-only blocks (lines 255-268). |
| H3 | Deliverable and AC written CONDITIONALLY against both paths so user can pick without re-planning? | **PARTIAL PASS** | Shared + Path-A-only + Path-B-only AC blocks exist, but Files-to-Change table (lines 192-217) does NOT mark which rows are Path-A-conditional vs. Path-B-conditional vs. shared — see Defect D2. |
| H4 | Plan AVOIDS hallucinated "per API 17R clause X" citations? | **PASS** | No specific 17R clause numbers appear in plan body. Only uses of "17R" are (a) titling, (b) hard-gate discussion, (c) Path-A-only AC saying "cite specific API 17R clause numbers ... for its design decisions" which is conditional on procurement. The phrase "or API 17B §" in pseudocode line 171 is ambiguous placeholder but does not assert specific clauses. |
| H5 | Greenfield claim verified against intel? | **PASS** | Plan §"Existing repo code" line 21: "No `connectors/` subdir exists"; §"File existence" line 89 "EXISTS: `digitalmodel/src/digitalmodel/subsea/`" + line 95 "MISSING (new — this plan creates): `digitalmodel/src/digitalmodel/subsea/connectors/__init__.py`"; §"Gap proofs" line 115: `ls digitalmodel/src/digitalmodel/subsea/connectors/ 2>&1 → "No such file or directory"`. Intel corroborates at intel line 17 ("no `connectors/` subdir"). |

**All 5 hard gates PASS (H3 with qualification).** No fabricated 17R clauses; the ledger gap is correctly escalated to user-in-loop rather than hidden. This is a significant positive versus the baseline failure modes for standards-gap plans.

---

## Full Defect Checklist (adversarial-stance pass)

| Axis | Status | Notes |
|---|---|---|
| Hallucinated evidence | CLEAN | No unverifiable file paths. All "EXISTS:" claims corroborated by intel. |
| Hallucinated standards citations | CLEAN | See H4. |
| Past-tense artifact drift | CLEAN | Plan consistently uses future tense for unwritten files ("MISSING (new — this plan creates)"); no "implemented" / "added" verbs for unwritten work. |
| Self-approval / pre-authorization language | CLEAN | Line 298 explicitly forbids self-selection by planner or downstream agents. |
| Greenfield verification | CLEAN | See H5. |
| Ledger gap surfaced | CLEAN | See H1. |
| Acceptance Criteria falsifiability | **DEFECTS** | See D1, D3, D5, D7. |
| Files-to-Change path-conditionality | **DEFECT** | See D2. |
| Test list numerical-reference grounding | **DEFECT** | See D4. |
| Cross-issue coordination concreteness | **DEFECT** | See D6. |
| Cross-repo placement risk | CLEAN (noted) | Risks line 335 addresses; every Create row in Files-to-Change uses `digitalmodel/` prefix. |
| T3 complexity justification | ACCEPTABLE | Line 345-353 defensible, though borderline — see D8. |
| Scope-creep tradeoffs flagged | CLEAN | Four distinct `[TRADEOFF FOR USER]` blocks. |
| Collision risk with #2455 | CLEAN | Test `test_no_collision_with_2455` asserts no writes into `jumper_hybrid/`. |
| `ConnectorProperties` naming collision | CLEAN (deferred) | Risks line 332 + Files-to-Change "Modify (coordination)" row handles. |

---

## Specific Defects

### D1 — AC "OrcaFlex export artifact validates against the existing schema" is unfalsifiable as stated (MINOR)

**Location:** AC shared block, line 250: "OrcaFlex export artifact validates against the existing `solvers/orcaflex/modular_generator` schema".

**Problem:** The `modular_generator` does not have a documented public schema referenced here. The plan cites no schema file path, no validator function name. A tester asked "did this AC pass?" has no binary check to run. The adjacent test `test_orcaflex_export_emits_valid_spec` (line 235) says "spec validates against existing generator schema" — same ambiguity.

**Fix required:** Specify the validator. Either (a) a concrete validator function (e.g., `modular_generator.validate_spec(spec) -> bool`), or (b) a JSON schema file path, or (c) a round-trip contract ("emitted spec loads into `modular_generator` without raising and produces an OrcaFlex .yml matching `jumper_hybrid/base/jumper_base.yml` key-set"). Without this, "validates" is interpretive.

**Severity:** MINOR — fixable pre-implementation by one line of specification.

### D2 — Files-to-Change does not mark rows Path-A vs. Path-B vs. shared (MINOR)

**Location:** Files to Change table, lines 192-217.

**Problem:** H3 hard gate requires user to pick without re-planning. Shared / Path-A-only / Path-B-only AC blocks exist (lines 246-268), but the Files-to-Change table mixes them with no annotation except for two rows ("Modify (Path A only, later)" on line 210 and the wiki rows on 215-216 which are parenthetically "(under Path B — ledgered-adjacents basis)"). The 7 core source files (lines 194-200) are presumably shared but this is not declared.

Specifically: if the user picks Path B, the plan must not later surprise the implementer with "oh, and you now need a new wiki entry under knowledge/wikis/marine-engineering/wiki/concepts/" that was not in the commitment.

**Fix required:** Add a column "Path" with values `Shared` / `Path A only` / `Path B only` to the Files-to-Change table. Make explicit which of the 7 Create rows are unconditional.

**Severity:** MINOR — does not block implementation once user chooses, but breaks the "no re-planning" guarantee if not fixed.

### D3 — "Module docstrings cite specific API 17R clause numbers" (Path A AC) admits hallucination if implementer can't access procured PDF (MAJOR risk, MINOR now)

**Location:** AC Path-A-only, line 257: "Every module docstring cites specific API 17R clause numbers for its design decisions".

**Problem:** Even under Path A (user procures 17R), the plan does not require the implementer to have read-verified citations against the procured PDF. The AC as written can be trivially satisfied by a plausible-sounding citation ("per API 17R § 6.2.3") that nobody verifies. This converts the hard-gate win (H4) into a deferred hallucination risk at implementation time.

**Fix required:** Tighten the Path-A AC: "Every cited clause number is verified against the ingested PDF; a `standards-citation-audit.md` artifact lists {clause, page, quoted text} pairs reviewed during implementation." This makes the citation falsifiable at review time.

**Severity:** MINOR at plan stage; would become MAJOR at implementation stage if left as-is.

### D4 — TDD reference-value tests cite standards without clause/example pointers (MINOR)

**Location:** TDD table, lines 229-232:
- `test_bending_analysis_stress_matches_DNV_OS_F101`: "rigid-pipe bending stress matches DNV-OS-F101 § reference" — § is literal placeholder with no section number.
- `test_thermal_expansion_fixed_fixed_axial_load`: "matches ASME B31.8 closed-form" — which closed-form? which worked example?

**Problem:** A reference-value test needs a specific reference value. `σ = M·c/I` and `F = A·E·α·ΔT` are first-principles formulas, not standards-specific — they're in any strength-of-materials textbook. If the AC is to match DNV-OS-F101 or ASME B31.8, the specific section (e.g., DNV-OS-F101 §5.4.3 or B31.8 §832) must be cited so the implementer can ground the numerical reference.

**Fix required:** Either (a) pin the specific standards section + worked example, or (b) downgrade wording from "matches DNV-OS-F101" to "matches classical beam theory closed-form" to remove false standards attribution.

**Severity:** MINOR — honest in intent, but sloppy at specification level and could produce the same "citation drift" pattern D3 warns about.

### D5 — AC "`ConnectorProperties` naming coordination ... resolved (either re-export or explicit namespace note)" leaves decision to implementer (MINOR)

**Location:** AC shared block, line 251.

**Problem:** "Either re-export OR explicit namespace note" is a live design decision that the plan defers to implementation time. Both options have different downstream consequences for #475 (test expansion) and for the public API of the new module. A plan that lets implementers choose between these is a plan that can't be reviewed until after implementation.

**Fix required:** Make the call now. Intel line 86 recommends "pin an import direction". Pick one: new `subsea.connectors.connector_design.Connector` is a distinct class (explicit namespace note); `jumper_lift.ConnectorProperties` stays installation-specific. Document this decision in the plan, don't defer.

**Severity:** MINOR — can be decided in plan revision or at approval time.

### D6 — "Coordinate with #475" appears twice without a concrete coordination mechanism (MINOR)

**Location:** Lines 211, 251, 332.

**Problem:** Three separate "coordinate with #475" mentions, zero specification of what coordination means. Is it a PR comment cross-link? A pre-implementation sync? A shared branch? An explicit ordering (#486 waits for #475, or vice versa)? As written, the plan leaves this to ambient agent behavior.

**Fix required:** Specify the mechanism. Suggestion: "Before landing any file that redefines or re-exports `ConnectorProperties`, comment on #475 with proposed change and wait for #475 author's ack. If #475 is already merged, rebase onto its final form." Or declare an ordering: "#486 depends on #475 completion."

**Severity:** MINOR — but a known pattern (intel risk #2) that's been a failure mode in adjacent issues; worth tightening.

### D7 — "Fatigue integration API not yet specified" is flagged as a risk but not resolved or deferred properly (MINOR)

**Location:** Risks line 337: "Fatigue integration API not yet specified. `fatigue/hotspot_stress.py` API is internal. Mitigation: Phase 3 opens with a brief API-design note appended to this plan as an amendment (or referenced from `fatigue_bridge.py` docstring); no behavior change to `fatigue/` module itself."

**Problem:** Phase 3 implementation will block on API design. The mitigation is "append an amendment or docstring note" — which is doing design work inside implementation, not surfacing it as a user-visible gate. Per Acceptance Criteria line 249, the AC is "bridge imports `digitalmodel.fatigue.rainflow`, `damage`, `hotspot_stress`" — that's a syntactic AC (did you import it?) not a semantic one (does the integration produce correct stress histories?).

**Fix required:** Either (a) do the API-design note now in this plan (one paragraph) so Phase 3 is executable, or (b) declare Phase 3 itself gated on a follow-up micro-plan that specifies the fatigue-bridge API contract.

**Severity:** MINOR — deferrable, but risks T3 scope blowout if left.

### D8 — T3 justification rests partly on the hard-gate that may resolve to Path B (scope reduction) (MINOR)

**Location:** Complexity §, lines 345-353; particularly line 347 ("Missing standard reference ... is a project-level gate").

**Problem:** If user picks Path B, the "project-level gate" dissolves immediately at approval, reducing T3 complexity pressure. The plan acknowledges line 353 that "a pure data-catalog slice ... would still be T2" — suggesting T3 is driven by the 7-file, 16-test, multi-standards-basis scope regardless of path choice. But the gate justification is duplicative with the scope justification. An adversarial reviewer would call this "padding T3".

**Fix required:** Either (a) accept T3 remains on pure scope grounds (7 new modules + 16 tests + numerical references + cross-module coupling) and drop the gate line from the justification, or (b) note that T3 remains T3 under Path B but could be T2 under Path-B-minimum-scope (catalog + connector_design only).

**Severity:** MINOR — not a blocker, but rigor of complexity argument could be tightened.

### D9 — Pseudocode for `connector_design.py` elides the core 17R content under both paths (MINOR)

**Location:** Pseudocode, lines 161-166.

**Problem:** `verify_preload()` pseudocode refers to "seal compression window" and "make-up torque residual" — these are the exact subsea-specific content that the Path-B tradeoff block (line 296) warns "will reference best-available general piping + vendor data only" because 17R proper owns those clauses. Yet the pseudocode commits to computing them. Under Path B, what are the numerical reference values? Where do the seal-compression and make-up-torque formulas come from when API 17R is unavailable?

**Fix required:** Under Path B, the AC/pseudocode must explicitly state that `verify_preload()` returns a conservative envelope check based on first-principles (hub-face area × seal-compression limit) with a docstring noting "Subsea-connector-specific design clauses live in API 17R; this function uses vendor-data fallback X/Y/Z for Path B scope". Otherwise the module ships with a function that claims to verify preload per unspecified standard.

**Severity:** MINOR at plan stage, MAJOR at implementation stage if unresolved.

### D10 — "`test_worked_example_tree_to_manifold`" bundles 6 independent assertions into one test (MINOR)

**Location:** TDD table, line 237.

**Problem:** Test asserts "catalog entry + preload PASS + bending PASS + thermal PASS + damage < 0.1/yr + OrcaFlex spec emitted" — six criteria. If one fails, the whole test fails and diagnosing is harder. Also "damage < 0.1/yr" is a threshold pulled from thin air with no standards basis.

**Fix required:** Split into per-AC assertions, or structure as separate parametrized test cases. Justify the `0.1/yr` threshold (is it 10-year design life? DNV fatigue safety factor?) or remove the specific number.

**Severity:** MINOR.

---

## Justification

The plan is better than the typical plan for this class of issue. It correctly identifies the API 17R ledger gap as a project-level user gate rather than papering over it with fabricated clause citations — this is the failure mode that would have produced the worst outcome (hallucinated-standards implementation), and the plan avoids it cleanly. The dual-path structure is well-conceived: the Shared/Path-A/Path-B AC split is the right shape, and the `[TRADEOFF FOR USER]` blocks correctly refuse to self-approve.

The defects are all in the second tier: falsifiability of ACs, path-conditionality completeness in Files-to-Change, concreteness of cross-issue coordination, and deferred design decisions that belong in the plan rather than in implementation. None are fatal; all are fixable with a revision pass of maybe 30-60 lines of plan edits.

The most important fix is D1+D4: making the numerical-reference and schema-validation ACs falsifiable at test-run time, because those are the ACs that determine whether implementation actually meets the issue's engineering substance versus just producing modules that import the right standards-flavored names. The second most important is D2 (Path annotation in Files-to-Change) because without it the "no re-planning required" guarantee breaks the moment user picks a path and the implementer finds an unannounced file in the commitment.

**Recommendation:** Plan-author revises to address D1-D6 at minimum. D7-D10 can be addressed in a second pass or accepted as known risks. After revision, re-review to confirm ACs are binary-checkable.

---

## Reviewer metadata

- Turns consumed: 4
- Hard-gate result: 5/5 PASS (H3 with qualification)
- Defect count: 10 (0 CRITICAL, 0 MAJOR-now, 10 MINOR; D3 + D9 have MAJOR-at-implementation potential)
- Verdict: **MINOR**
