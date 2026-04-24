# Adversarial Review — Plan for Issue #279 (r2)

**Reviewer stance:** adversarial / defect-hunter
**Review date:** 2026-04-24
**Plan under review:** `docs/plans/2026-04-24-issue-279-orcaflex-reporting-standardization.md` (r2 revision)
**Prior artifacts consulted:**
- `scripts/review/results/2026-04-24-plan-279-adversarial.md` (r1 adversarial — 3 MAJOR + 5 MINOR, authoritative defect list)
- `scripts/review/results/2026-04-24-plan-279-claude.md` (r1 2nd-pass Claude — MAJOR, 12 findings / 7 blockers)
- `/tmp/orca-batch-2026-04-24/intel-279.md` (pod intel)
- `/tmp/orca-batch-2026-04-24/issue-279-body.txt` (issue spec v1.13)

**Live-code verification:** `ls`/`grep` against `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/` and `docs/` on 2026-04-24.

---

## Verdict

**MINOR** — all r1 MAJOR defects RESOLVED, but r2 introduces 1 new MAJOR-adjacent evidence-gap (degraded to MINOR because it doesn't block implementation) and 3 non-critical consistency issues. Plan is approvable after a quick revision pass on the items listed below.

---

## Prior-Defect Resolution Audit

### r1 adversarial review (3 MAJOR + 5 MINOR)

| r1 defect | Status in r2 | Evidence |
|---|---|---|
| **MAJOR-1** — `docs/modules/` → `docs/domains/` rename-risk ignored | **RESOLVED** | r2 adds § Docs Path Binding (Rename-Risk Lock) at lines 151–165 binding `$EXAMPLES_DIR` variable with explicit resolution protocol; Risk bullet at line 403; AC line 371 predicates path on resolution; 32 grep hits in r2 for `docs/modules\|docs/domains\|EXAMPLES_DIR` vs. 0 in r1. |
| **MAJOR-2** — Spec-mandated golden HTML examples missing | **RESOLVED** | r2 Artifact Map lines 195–197 add 2 golden HTML files + README; Files to Change lines 321–323 add 3 rows; Acceptance Criterion line 370 requires ≥2 golden reports parseable via `html.parser.HTMLParser`; TDD rows `test_golden_riser_html_committed` and `test_golden_mooring_html_committed` at lines 351–352. |
| **MAJOR-3** — Fabricated `test_boundary_conditions_wired_in_aggregator` | **RESOLVED** | Verified by grep: `grep -c "test_boundary_conditions_wired\|test_boundary_conditions" r2-plan` returns 1, and the only remaining hit is in § Revision Notes documenting the removal. The fabricated test is GONE from the TDD Test List (lines 335–356); Gap #8 was removed (gaps list at lines 95–107 no longer contains a `boundary_conditions` wiring-audit row); aggregator Files-to-Change row at line 309 now reads "wire vessel extractor into `_safe_extract` chain" (no wiring-audit clause). |
| **MINOR-1** — Dispatch pseudocode vs. live if/elif | **RESOLVED** | r2 Pseudocode lines 257–270 explicitly commits to **APPEND `elif`**, NOT dict rewrite; AC line 365 requires diff-review confirming append-elif; added `test_dispatch_ladder_parity` (line 336). |
| **MINOR-2** — `from_dict()` not elevated to AC | **RESOLVED** | AC line 369 adds dedicated checkbox; TDD row `test_from_dict_all_models_offline` parameterised over all 11 models (line 343); Files to Change line 318. |
| **MINOR-3** — Source-count footnote wrong | **RESOLVED** | Line 147: source count now "9 distinct sources" and enumerates each. Honest count. |
| **MINOR-4** — SRI-pin guard scope | **RESOLVED** | Pseudocode lines 280–288 extends scope to include BOTH version drift AND SRI-hash drift (recompute `sha384(curl ...)` vs. declared constant); AC line 373 requires both synthetic checks; TDD rows `test_sri_pin_script_detects_version_drift` and `test_sri_pin_script_detects_hash_drift`. |
| **MINOR-5** — Codex-iter-14 / Gemini NO_OUTPUT x14 lineage ungated | **RESOLVED** | AC line 377 wires re-cross-review into acceptance with explicit Gemini NO_OUTPUT fallback ("≥ 2 attempts with stderr capture → proceed on Claude+Codex consensus"); Artifact Map line 203 states "fallback: NO_OUTPUT tolerated with stderr capture". |

### r1 2nd-pass Claude review (12 findings / 7 blockers)

| r1-Claude finding | Status in r2 | Evidence |
|---|---|---|
| **Finding 1** — Dispatch refactor ambiguity | **RESOLVED** | See MINOR-1 above. |
| **Finding 2** — FPSO snapshot silent regression | **RESOLVED** | r2 adds dedicated § FPSO Snapshot Re-baseline Protocol (lines 168–177) with A/B/C commit protocol; AC line 366; TDD row `test_fpso_rebaselined_with_vessel_renderer` (line 350); Risk bullet at line 404. |
| **Finding 3** — Gap #8 false | **RESOLVED** | See MAJOR-3. Evidence: `aggregator.py:24` import + `aggregator.py:68` call confirmed; Gap removed from r2. |
| **Finding 4** — Vessel-as-primary vs. subcomponent divergence | **RESOLVED** | r2 Pseudocode lines 245–254 adds `VesselExtract.to_other_structures_dict()` adapter; Risk bullet line 405; TDD row `test_vessel_to_other_structures_dict_consistent` (line 342). |
| **Finding 5** — `fixtures/` dir doesn't exist | **RESOLVED** | Files to Change line 316 breaks out `fixture_helpers.py` refactor as its own row; AC line 368 requires the refactor + migration; Risk bullet line 406. |
| **Finding 6** — Extractor count 7 vs 8 | **RESOLVED** | r2 line 60: "8 files (not 7)" with full enumeration. Verified via `ls`: 8 non-`__init__` files present. |
| **Finding 7** — `css.py` omitted | **RESOLVED** | r2 line 56 adds `css.py` (213 lines) to inventory. |
| **Finding 8** — `test_report_generator.py:112` already tests dispatch | **RESOLVED** | Files to Change line 312 now reads "**Extend** `test_report_generator.py`" (NOT a new file); TDD row "(in `test_report_generator.py`)" notation at line 335. |
| **Finding 9** — 17 modules for 16 sections | **PARTIAL** | r2 line 41 "clarified: utils.py is the 17th, not a section — 16 sections + 1 utils". But r2 line 58 enumerates **18 names** (header, executive_summary, model_overview, geometry, materials, boundary_conditions, mesh, other_structures, loads, analysis_setup, results_static, results_dynamic, results_extreme, design_checks, fatigue, summary, appendices, utils) and says "(17 files total)". Count-of-names (18) contradicts stated count-of-files (17). See New Defect #2 below. |
| **Finding 10** — TRADEOFF-gated acceptance | **RESOLVED** | r2 lines 413–417 lock defaults (Legacy=A Deprecate, Vessel=A Minimum-viable, structure_types=A Remove); AC lines 374–375 reference defaults with override provision. |
| **Finding 11** — Gemini NO_OUTPUT indefinite-block | **RESOLVED** | See MINOR-5. |
| **Finding 12** — Deprecation comment self-contradicts | **RESOLVED** | r2 Pseudocode lines 290–298 aligned; header now just "Legacy deprecation (aligned — no self-contradiction)"; warning body says "will be removed in v<N+2>"; AC line 374 wording matches. |

### Summary of prior-defect resolution

- **r1 adversarial MAJOR (3):** 3 RESOLVED, 0 PARTIAL, 0 UNRESOLVED.
- **r1 adversarial MINOR (5):** 5 RESOLVED, 0 PARTIAL, 0 UNRESOLVED.
- **r1 Claude blockers (7):** 7 RESOLVED, 0 PARTIAL, 0 UNRESOLVED.
- **r1 Claude cleanups (5):** 4 RESOLVED, 1 PARTIAL (Finding 9 section-count).
- **Total:** 19 RESOLVED / 1 PARTIAL / 0 UNRESOLVED.

All r1 MAJOR defects are RESOLVED (not PARTIAL). Per the verdict rules, baseline verdict is APPROVE if no new MAJOR defects are introduced. New defects are in the next section.

---

## New Defects (introduced by r2)

### NEW-1 — Plan text contradicts live filesystem: `docs/domains/` DOES exist (r2 twice claims it does not)

**Severity:** MINOR (evidence gap; does not invalidate the path-binding protocol, which remains sound)

r2 claims in two places:

- Line 19 (MAJOR-1 resolution row): *"`docs/modules/orcaflex/` does NOT currently exist; `docs/domains/` does NOT currently exist."*
- Line 64 (Resource Intelligence): *"`docs/modules/` EXISTS but has NO `orcaflex/` subdirectory; `docs/domains/` does NOT exist."*
- Line 126 (File existence bullet): *"MISSING: `docs/domains/` — directory does not exist"*
- Line 143 (Gap proofs): *"`ls docs/domains 2>&1` → 'No such file or directory'"*

**Live verification 2026-04-24:**
```
$ ls -la /mnt/local-analysis/workspace-hub/docs/domains
drwxrwxrwx 1 vamsee vamsee     0 Mar 31 06:06 .
-rwxrwxrwx 1 vamsee vamsee     0 Mar 31 06:06 .gitkeep
```

`docs/domains/` **exists** as an empty directory with a `.gitkeep` sentinel. It was seeded 2026-03-31 (before r1 and r2). The r2 claim contradicts the repo state it asserts via `ls` citation.

**Why MINOR, not MAJOR:** the rename-risk protocol in § Docs Path Binding is still sound — `$EXAMPLES_DIR` is bound per resolution decision. The existence of a `.gitkeep`-only directory doesn't change the rename-decision question (empty placeholder ≠ migration happening). But: (a) the plan cites falsified `ls` output as evidence, which degrades the Evidence (embedded verification) block's credibility; (b) the `.gitkeep` suggests someone already started the migration skeleton, which makes the rename-decision question more urgent than r2 portrays; (c) it contradicts the memory feedback item `feedback_codex_needs_pushed_artifact` style discipline ("verify evidence locally").

**Suggested fix:** update r2 lines 19, 64, 126, 143 to read `docs/domains/` EXISTS (empty, only `.gitkeep`) and add one sentence to § Docs Path Binding noting the empty-skeleton seeding may indicate a rename-in-progress — treat as a signal to ask the user before implementer starts.

### NEW-2 — Section-count enumeration contradicts stated file count (PARTIAL-carry from r1-Claude Finding 9)

**Severity:** MINOR

r2 line 58 enumerates section_builders names:
> `header, executive_summary, model_overview, geometry, materials, boundary_conditions, mesh, other_structures, loads, analysis_setup, results_static, results_dynamic, results_extreme, design_checks, fatigue, summary, appendices, utils`

That's **18 names**. But the same sentence says "(17 files total)" and line 41 says "16 sections + 1 utils" = 17. `ls section_builders/*.py` confirms 19 entries including `__init__.py` — so **18 non-`__init__` files = 17 section modules + utils.py + one extra**. The extra is `appendices.py` or a naming overlap; the 16-section canonical layout likely does NOT include `header` (it's chrome) OR `appendices` (often chrome). r2 doesn't resolve which one is excluded from the canonical 16.

This was r1-Claude Finding 9; r2 Revision Notes line 41 claims it was resolved but the enumeration still contradicts itself.

**Suggested fix:** either (a) say explicitly "18 files in section_builders/ = 16 canonical sections + `utils.py` (XSS helper) + `header.py` (chrome frame, not a section)" OR (b) restate the canonical-section count to match the file count.

### NEW-3 — r2 review-artifact path collides with r1 review path

**Severity:** MINOR

Plan Artifact Map line 201:
> `Plan review — Claude (r2) | scripts/review/results/2026-04-24-plan-279-claude.md (r1 exists; r2 re-review required)`

This reuses the r1 filename for r2. The r2 Claude reviewer will either (a) overwrite the r1 artifact (destroying history), or (b) refuse to write, or (c) pick a `-r2-` suffix unilaterally. This review is being written to `2026-04-24-plan-279-r2-adversarial.md` (per the dispatcher prompt) — so an `-r2-` prefix convention is already in use for the adversarial lane. r2 plan should name all r2 artifacts with the same convention (e.g., `2026-04-24-plan-279-r2-claude.md`) to avoid the collision.

**Suggested fix:** update Artifact Map lines 201–203 to use the `-r2-` filename prefix for all r2 provider reviews.

### NEW-4 — Revision Notes and TDD list disagree on one renamed test

**Severity:** MINOR (cosmetic)

Revision Notes line 21 (MAJOR-3 resolution) says the replacement test is *"dispatch-map vs. renderer-registry parity test"*. The actual TDD row at line 336 is `test_dispatch_ladder_parity` — "ladder", not "map"/"registry". The plan has committed to append-elif (MINOR-1 fix), so "ladder" is the right name. But the Revision Notes terminology ("dispatch-map vs. renderer-registry") is a vestigial artefact from the refactor-to-dict option that MINOR-1 explicitly rejected.

**Suggested fix:** reword line 21 to "dispatch-ladder parity test" or "dispatch ↔ renderer-class-registry parity test" (matching line 106's gap description).

### Scope drift check: **none**

r2's new content (§ Docs Path Binding, § FPSO Snapshot Re-baseline Protocol, `to_other_structures_dict`, golden HTML rows, `test_dispatch_ladder_parity`, `test_from_dict_all_models_offline`) is defect-driven — each is traceable to a specific r1 finding. No new features were smuggled in. Complexity re-evaluation from T2 → T2-large is justified in Complexity section (lines 427–435). No scope drift.

### Newly-fabricated claims: **NEW-1 only**

Greps for function names, file paths, line numbers in r2 that could be hallucinated:

- `aggregator.py:24` / `aggregator.py:68` — **verified** via grep.
- `report_generator.py:60-74` if/elif, `PLOTLY_JS_VERSION = "2.26.0"`, `PLOTLY_JS_SRI` declared — consistent with r1 verification, no contradicting grep.
- `models/other_structures.py:20` `vessels: List[dict]` — consistent with r1 verification.
- `builder.py:31` `#0d6efd` — consistent with r1 verification.
- `test_fpso_fixture_snapshot.py:13-25` — consistent with r1 verification.
- `test_report_generator.py:112` — consistent with r1 verification.
- Renderer count 5 + base.py — verified via `ls`.
- Extractor count 8 non-`__init__` — verified via `ls`.
- Models count 11 non-`__init__` — verified via `ls`.
- section_builders count "17" — contradicted by `ls` (18 non-`__init__` files) — see NEW-2.
- `docs/domains/` existence — contradicted by `ls` — see NEW-1.

Two of ~12 verifiable claims are wrong. Worse ratio than r1 (which had zero verified fabrications in the inventory), but both misses are at the edges (directory-existence probe, count cross-check), not core logic.

### Consistency with `$EXAMPLES_DIR`: mostly consistent

All golden-HTML references use `$EXAMPLES_DIR` (Artifact Map, Files to Change, TDD, AC). One minor nit: AC line 371 reads *"$EXAMPLES_DIR resolved against current docs/modules/ vs docs/domains/ rename decision at implementation start"* — this is correctly deferred. § Docs Path Binding step 1 option (c) says "If unresolved, block on the rename-tracking issue (user names it at approval) rather than race." Good — the unresolved case has an explicit blocker. No consistency-drift.

---

## Defect Checklist (standard)

| # | Check | Status |
|---|---|---|
| 1 | Scope drift | PASS |
| 2 | Evidence gaps (hallucinated paths / numbers / types) | FAIL × 2 — NEW-1 (docs/domains exists), NEW-2 (section count) |
| 3 | TDD completeness | PASS — fabricated test removed, replacements grounded |
| 4 | Missing edge cases | PASS — FPSO re-baseline, `to_other_structures_dict`, Gemini fallback, SRI hash drift all covered |
| 5 | Coupling risk | PASS — append-elif preserves per-branch kwargs surface |
| 6 | Past-tense drift | PASS — all AC items in imperative/future tense; Revision Notes use past tense only for "Added X" / "Removed Y" which is appropriate for a revision log |
| 7 | Self-labeling | PASS — no `status:plan-approved` claim in plan body; AC line 377 correctly gates on pre-approval reviews; line 421 correctly leaves rename-tracking-issue name as user-open item |
| 8 | Plan-vs-intel contradiction | PASS — intel (`/tmp/orca-batch-2026-04-24/intel-279.md`) aligns with r2's "delta = vessel + fixtures + cleanup" framing |
| 9 | Complexity mismatch | PASS — T2→T2-large re-evaluation justified by expanded deliverable surface (golden HTML + FPSO re-baseline + fixtures refactor + 11-model from_dict) |

---

## Specific Defects Found

1. **(NEW-1, MINOR)** Lines 19, 64, 126, 143 — falsified `ls` evidence re. `docs/domains/` existence.
   - **Fix:** update to "`docs/domains/` EXISTS (empty, `.gitkeep` only, seeded 2026-03-31)"; add one sentence flagging the `.gitkeep` as a possible migration-in-progress signal the implementer should clarify with the user at resolution time.

2. **(NEW-2, MINOR)** Line 58 — 18 enumerated names vs. "17 files total" vs. `ls` showing 18 non-`__init__` `.py` files.
   - **Fix:** pick one: either restate "18 files = 16 canonical sections + `utils.py` + `header.py` (chrome)" with explicit chrome-vs-section assignment, or correct the count to match `ls` output.

3. **(NEW-3, MINOR)** Lines 201–203 — r2 review artifacts reuse r1 filename paths.
   - **Fix:** rename r2 artifacts to `2026-04-24-plan-279-r2-{claude,codex,gemini}.md` to match the adversarial-lane naming convention this review is using.

4. **(NEW-4, MINOR / cosmetic)** Line 21 — "dispatch-map vs. renderer-registry parity test" terminology contradicts the MINOR-1 resolution (which committed to append-elif, NOT dict/registry).
   - **Fix:** reword to "dispatch-ladder parity test" to match line 336 TDD row and line 106 gap description.

5. **(Carry-forward partial, MINOR)** r2 Revision Notes line 41 claims Finding 9 "clarified" but the actual inventory at line 58 still contains the enumerate-vs-count contradiction. Revision Notes overclaim the fix.
   - **Fix:** same as NEW-2; when applied, update Revision Notes Finding 9 row to reflect the real fix.

---

## Verdict Justification

**Baseline:** 19/20 prior findings RESOLVED, 1/20 PARTIAL (Finding 9 carried into NEW-2), 0 UNRESOLVED. All 3 r1 MAJOR defects RESOLVED — per verdict rules, APPROVE is on the table.

**Why MINOR, not APPROVE:**
- NEW-1 is a falsified-evidence item (the plan twice asserts `ls docs/domains` returns "No such file or directory" — it does not). Even though the path-binding protocol is unaffected, the plan presents wrong `ls` output as verified evidence. That's exactly the class of defect the user's memory (`feedback_codex_needs_pushed_artifact`, `feedback_commit_attestation_narrow_scope`) calls out as load-bearing trust.
- NEW-2 is a carried-forward partial that the Revision Notes overclaim as resolved.
- NEW-3 will cause artifact collision when the r2 Claude reviewer runs — operationally avoidable.
- NEW-4 is cosmetic but indicative of edit-hygiene gaps (leftover dict/registry terminology after a refactor-to-append decision).

**Why not MAJOR:**
- No r1 MAJOR defect is PARTIAL or UNRESOLVED.
- NEW-1 doesn't invalidate the resolution protocol — $EXAMPLES_DIR binding still works for any rename-decision outcome. The falsified-evidence nit is about evidence quality, not plan soundness.
- NEW-2, NEW-3, NEW-4 are all revisable in a single 10-minute edit pass.

**Recommended revision:** fix NEW-1 through NEW-4 (all small edits, no structural change) and re-dispatch for an r3 sweep, OR accept MINOR with user-at-approval-time acknowledgement of the four items above.

---

## Forbidden-behaviour self-check

- No charitable re-reading; every defect cites a file + line OR a grep/ls result run locally.
- No scope invented beyond the r1 defect list and the standard checklist.
- Verdict is `MINOR`, not `APPROVE`, because of NEW-1's falsified `ls` evidence — not rhetorical.
- Not claiming "approved for implementation"; user retains approval authority.
- Did not modify the plan, did not commit, did not push, did not touch forbidden plan directories.
