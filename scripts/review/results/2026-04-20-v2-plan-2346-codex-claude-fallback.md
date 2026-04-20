# Adversarial review v2 — plan for #2346 (Claude — Codex fallback, sandbox-blocked)

**Reviewer:** Claude (Opus 4.7, 1M context) acting as Codex fallback per `feedback_codex_sandbox_no_execution.md`.
**Plan:** `docs/plans/2026-04-19-issue-2346-prospect-data-pipeline.md` @ `ee1b16440`
**Stance:** Codex-style — file-state verification over plan-text trust; defect-hunt over charitable read.
**Repo state verified:** HEAD = `2adf4ae89` on `main`; plan blob at `ee1b16440` (v3.1 commit).
**Inputs consulted:** round-1 Claude (`2026-04-20-plan-2346-claude.md`), round-1 Codex (`2026-04-20-plan-2346-codex.md`), round-2 Claude v3 (`2026-04-20-v2-plan-2346-claude.md`), drift memory `feedback_plan_past_tense_artifact_claims.md`, sandbox memory `feedback_codex_sandbox_no_execution.md`.

## Verdict: **APPROVE**

All 7 Codex round-1 MAJORs are discharged with verifiable evidence. All 3 Claude round-2 MINORs (D1/D2/D3) are applied at the lines claimed. Live `jsonschema.Draft7Validator.check_schema()` passes; behavioural accept/reject tests all match plan claims. Cross-repo claim is independently verified (aceengineer-website IS a separate git repo). Past-tense drift audit: clean. No blocking new defects found. Four non-blocking NITs flagged below for optional polish — none justify another round.

---

## Round 1 finding disposition (7 Codex MAJORs + 3 Claude MAJORs + 4 MINORs)

| # | Source | Round-1 finding | Plan file + line | v3/v3.1 disposition |
|---|---|---|---|---|
| 1 | Codex M1 | Q5 unsourced — "deferred to implementation" | lines 42-63 | **RESOLVED.** Source Pins table at 53-57 with concrete IDs: OTC-24523 (2013), OTC-25303 (2014), ISBN 978-0-12-812622-6 (Bai & Bai 2018), ISBN 978-1-5939-2378-7 (Palmer & King 2023), DNV-RP-H103 (Oct 2021), Allseas Lorelay/Subsea 7 Seven Borealis/TechnipFMC Deep Energy vendor spec URLs. Plus line 51 "MUST NOT leave any citation as a placeholder at merge time". |
| 2 | Codex M2 | Canonical vessel reproduction arbitrary | line 59 | **RESOLVED.** Explicit reviewer-reproducibility test: "reviewer MUST be able to open each cited document … and recompute at least LOA, beam, DP class, max water depth, and one representative crane/tensioner capacity." |
| 3 | Codex M3 | JSON-Schema is prose/pseudocode | lines 211-307 | **RESOLVED via execution.** Schema parses as JSON; `Draft7Validator.check_schema()` → **PASS** (live run). Behavioural: demo_01+vessel → REJECTED (2 errors, `False schema does not allow {...}`); demo_01 no-vessel → ACCEPTED; demo_03 no-vessel → REJECTED (`'vessel' is a required property`); demo_03+vessel → ACCEPTED. All four match plan claims at line 309. |
| 4 | Codex M4 | Dual delivery — no transaction model | lines 146-158 | **RESOLVED.** 7-step state machine with 4 terminal states (`DELIVERED`, `DELIVERED_EMAIL_ONLY`, `FAILED_EMAIL`, `UNPUBLISHED`), email-first sequencing, 3× exp-backoff (30s/2min/10min), delivery-log schema, compensating `unpublish_url()` action, and 5 TDD tests at line 158. |
| 5 | Codex M5 | Sidecar boundary undefined | lines 460-482 | **RESOLVED.** Path moved to `private-log/fallback-applied.json`, gitignored (line 514), schema committed at lines 464-480, two never-ships tests at lines 577-578 (`test_fallback_sidecar_never_in_email_attachment`, `...never_in_url_publish_set`). |
| 6 | Codex M6 | Canonical-fixture leakage uncontained | line 111, 579 | **RESOLVED.** Test-only sink `tests/fixtures/prospect-outputs/` (line 111) + gitignore + `test_canonical_fixture_output_path_isolation` at line 579. |
| 7 | Codex M7 | Revision record inconsistent ("4 vs 5 fallbacks") | line 14-15, 435 | **RESOLVED.** Revision row v2 reads "5 authorized fallbacks F1-F5"; v3.1 (D6 trivial) also fixed line 435 to "five authorized fallbacks (F1 refuse + F2-F5 fix-paths)". |
| 8 | Claude M1 | Gating hand-waved | lines 511-513, 585-586 | **RESOLVED.** `aceengineer-website/robots.txt` + `vercel.json` in Files-to-Change; acceptance `curl` at 623-624; tests 585-586. |
| 9 | Claude M2 | `not:{required}` doesn't forbid | lines 300-303 | **RESOLVED via execution.** `"properties": { "vessel": false }` verified live to reject stray-vessel payload — "False schema does not allow" error is the `properties.vessel: false` mechanism firing, not just the `not/required` path. Defense-in-depth is real, not performative. |
| 10 | Claude M3 | #2342/#2343 sequencing unanalyzed | lines 667-672 | **RESOLVED.** Two-path analysis (prefer-merge-after vs inline-self-contained fallback). |
| 11 | Claude m1 | Q5 citation deferral | see Codex M1 | **RESOLVED** (same fix). |
| 12 | Claude m2 | Fallback matrix under-specified | line 456 | **PARTIALLY RESOLVED.** Numerical-failure row still reads "F2 ALLOWED (if pre-auth AND root cause is vessel)" with no root-cause-detection protocol — v3.1 consciously DEFERRED (rev-history line 16 "D7 … require >1-line edits and are filed as post-implementation refinements"). Acceptable as deferred NIT; SOP Hour 6-24 covers engineer-judgment escalation. |
| 13 | Claude m3 | Sidecar schema absent | lines 464-480 | **RESOLVED.** |
| 14 | Claude m4 | gitignore coverage incomplete | line 514, 587-589 | **RESOLVED.** 4 patterns + 3 check-ignore tests. |

## Round 2 D1/D2/D3 disposition (v3.1 delta)

| Fix | Claimed line | Verified? |
|---|---|---|
| **D1** — Gating-mechanism table path reconciled to `/private/<hash>/<slug>.html` | line 136 | **VERIFIED.** Line 136 reads `/private/<sha256-hash-of-(prospect-id + salt + date)>/<slug>.html`; explicitly notes "Path prefix `/private/` matches the single top-level `Disallow` rule in `robots.txt` and the `X-Robots-Tag` header applied at line 511-515." Internal consistency holds across lines 136, 511-513, 516, 585-586, 623-624. No stray `/prospects/` left in gating context. |
| **D2** — Prose + schema enum reconciled so F1-F5 all log | lines 460, 473 | **VERIFIED.** Line 460 reads "all fallbacks F1-F5 will be logged"; line 473 enum reads `["F1", "F2", "F3", "F4", "F5"]` (F4 added). Matrix at 446-458 is consistent. |
| **D3** — Cross-repo deploy dependency subsection | lines 674-680 | **VERIFIED** and independently confirmed: `aceengineer-website/.git` exists as a distinct repo; `git ls-files | grep aceengineer-website` returns 0 in workspace-hub. Section explicitly names (a) two pushes required, (b) Vercel auto-rebuild on aceengineer-website push, (c) reclassification of 623-624 as post-deploy verification, (d) cross-repo rollback path. Not hand-waving. |
| **D6 trivial** — "four authorized fallbacks" → "five" | line 435 | **VERIFIED.** Line 435 reads "five authorized fallbacks (F1 refuse + F2-F5 fix-paths)". |
| **D4, D5, D7 deferred** per rev-history line 16 | n/a | Acknowledged deferral, rationale documented. Acceptable. |

## Past-tense drift audit (post-v3.1)

`grep -nE 'committed|vendored|now present|has been created|was created|is implemented|already exists'` → 11 hits. All analyzed:

| Line | Text (abbrev) | Verdict |
|---|---|---|
| 14-16 | Revision History "Integrated…", "Addressed…" | Past of revision-action, not implementation. PASS per memory. |
| 49 | "will be committed with … citations" | FUTURE. PASS. |
| 73 | "vendored Plotly" describing EXISTING #2342/#2343 plan artifacts | Describes another plan's prescribed work, not this plan's. Marginal but defensible — this is a Documents-consulted section, not a this-plan-prescribes section. ACCEPTABLE. |
| 77 | "must be committed to git before it is referenced" | FUTURE (imperative). PASS. |
| 101 | This plan "EXISTING (committed)" | TRUE — plan blob at `ee1b16440` verified. PASS. |
| 209 | "will be committed verbatim" | FUTURE. PASS. |
| 462 | "committed to `.gitignore`" (context: will be) | FUTURE in context. PASS. |
| 572 | "matches committed golden file byte-for-byte" | Test behavior at test-time, not plan-time state. PASS. |
| 629 | "Golden regression test committed with a canonical golden JSON output file" | Acceptance-checkbox describing future deliverable. Marginal but standard. ACCEPTABLE. |
| 660 | "golden regression test re-materializes and compares against committed golden output" | Future-state Mitigation description. PASS. |
| 661 | "Demo 1 fixture committed and test-covered" | Risk-mitigation of future Files-to-Change row. Marginal; ACCEPTABLE. |

Confirmed no implementation artifacts exist: `ls docs/gtm/intake/` → No such file; `ls digitalmodel/examples/demos/gtm/prospect_adapter.py` → No such file; `ls docs/gtm/deliveries-log.md` → No such file. Plan does NOT falsely claim any of these exist. **No drift.**

## Citation metadata completeness (v3 additions)

Per review instructions — no URL fetches; verify metadata sufficient for an independent reviewer to look up.

| Citation | Required metadata | Plan line 53-57 provides | Lookup verdict |
|---|---|---|---|
| Allseas Lorelay | vendor + model + URL | Allseas + Lorelay + allseas.com URL | Resolvable |
| Palmer & King | author + title + edition + year + ISBN | ALL present: Palmer & King, *Subsea Pipeline Engineering*, 3rd ed., 2023, ISBN 978-1-5939-2378-7 | Resolvable |
| Seven Borealis | vendor + model + URL | Subsea 7 + Seven Borealis + subsea7.com URL | Resolvable |
| OTC-24523 | OTC# + year + title | OTC-24523 (2013) "Installation of Subsea Structures Using Heavy-Lift CSVs" | Resolvable via OnePetro (number+year+title sufficient); author NOT pinned but OTC number is the canonical index key |
| Bai & Bai | author + title + edition + year + ISBN | ALL present: Bai & Bai, *Subsea Engineering Handbook*, 2nd ed., 2018, ISBN 978-0-12-812622-6 | Resolvable |
| Deep Energy | vendor + model + URL | TechnipFMC + Deep Energy + technipfmc.com URL | Resolvable |
| OTC-25303 | OTC# + year + title | OTC-25303 (2014) "Deepwater Reel-Lay PLSV Installation Experience" | Resolvable; same caveat |
| DNV-RP-H103 | ID + edition/year + section | DNV-RP-H103, Oct 2021 ed., §4 | Resolvable |
| API 17B/17J | ID + edition | NO edition/year pinned | **WEAK — NIT N2 below** |

**Verdict:** 8 of 9 sources fully resolvable. API 17B/17J is secondary (line 57 complement, not primary). Not a blocker.

## JSON Schema — live execution

```
CHECK_SCHEMA: PASS — schema is syntactically valid draft-07
demo_01 + stray vessel (EXPECT REJECT): REJECTED  errs=2
  - False schema does not allow {'shape': 'csv_hlv', ...}
demo_01 + no vessel (EXPECT ACCEPT): ACCEPTED  errs=0
demo_03 + no vessel (EXPECT REJECT): REJECTED  errs=1
  - 'vessel' is a required property
demo_03 + vessel (EXPECT ACCEPT): ACCEPTED  errs=0
```

All four behavioural expectations match the plan's claims at line 309 and acceptance criteria 605-606. The `False schema does not allow` error is the plan's `"properties": { "vessel": false }` construct actually firing — Claude round-1 M2 concern is conclusively addressed, not merely re-worded.

## /private/<hash> as security-by-obscurity

**Question:** acceptable for NDA-safe prospect delivery, or does it need real access control?

**Assessment:** **Acceptable at plan level, with caveats explicitly documented.**
- Line 136 labels the mechanism "Security-by-obscurity" explicitly — no hidden claim of cryptographic protection.
- Defense stack: (a) 256-bit hash is non-enumerable in practice; (b) `robots.txt` `Disallow: /private/`; (c) `X-Robots-Tag: noindex, nofollow` stops indexing; (d) NDA is the contractual layer; (e) email is authoritative channel (line 129) so URL is viewing-convenience not the trust boundary; (f) `purge_after_utc` auto-cleanup (cron is follow-up — risk documented at line 664).
- Residual risk correctly flagged at line 664: "prospect forwarding the hash URL to an unauthorized third party — not mitigable at plan level."
- Line 137-138 documents basic-auth (+$20/mo Vercel Pro) and signed-link as opt-in upgrades. Plan is NOT locking in obscurity as the ONLY option.

This is the correct level of rigor for the stated use case (NDA-bearing warm leads, not regulated PHI/PCI). If the user's risk tolerance later tightens, the opt-in upgrade paths are already documented.

## Cross-repo D3 — assessment

**Question:** does D3 clearly say which edits go to which repo, or is it hand-waving?

**Assessment:** **Not hand-waving.** Lines 674-680:
- Line 676 explicitly names `aceengineer-website/.git` as a distinct repo with separate remote (verified live: `git -C aceengineer-website rev-parse --show-toplevel` returns `/mnt/local-analysis/workspace-hub/aceengineer-website`, separate from workspace-hub).
- Line 677 names the two pushes required.
- Line 678 names Vercel auto-rebuild as the trigger, reclassifies 623-624 as post-deploy verification.
- Line 679 names rollback scope asymmetry.
- Line 680 prescribes SOP cross-repo deploy checklist.

This is the right level of specificity for a plan; operational details (exact push commands, deploy SLAs) belong in the SOP runbook — which is itself a deliverable of this plan.

## Dual-delivery state machine — assessment

**Question:** actual state machine with transitions, or prose? Terminal states defined?

**Assessment:** **Real state machine.** Lines 146-158:
- Terminal states enumerated: `DELIVERED`, `DELIVERED_EMAIL_ONLY`, `FAILED_EMAIL`, `UNPUBLISHED` (line 152, 156, delivery-log schema 157).
- Transitions: (a) email-first sequencing (150), (b) email-success + URL-success → `DELIVERED` (151), (c) email-failure → retry 3× → `FAILED_EMAIL` (152), (d) email-success + URL-fail → retry 3× → `DELIVERED_EMAIL_ONLY` (153), (e) late URL publish — allowed but no auto-email (154), (f) compensating `unpublish_url()` → `UNPUBLISHED` (155).
- Retry policy quantified: 30s/2min/10min exp-backoff.
- TDD tests cover each transition (line 158): 5 tests, one per transition.

**NIT — D4 from round-2 Claude v3.** v3.1 deferred the `DELIVERED_EMAIL_ONLY → DELIVERED` recovery transition. This means a late-day manual URL re-publish after exhausted retries creates an append-only row with no state-upgrade path. Plan acknowledges at rev-history line 16. Non-blocking because the deliveries-log schema (line 157) says "appended never mutated" and real-world late-publish is rare and SOP-driven. Filing as post-implementation refinement is defensible.

## New v3+v3.1 findings (hunt for new defects)

### N1 NIT — Fallback matrix row "demo 1/2 with stray vessel" (line 458) routes to F4 clarify; but schema rejects at intake before SOP dispatch

- **Evidence:** Line 458 matrix: `Demo 1/2 with stray vessel block | — | — | — | DEFAULT (F4 clarify) | —`. But line 576 test `test_e2e_demo_01_with_stray_vessel_rejected` promises the pipeline refuses at schema time (`< 5 s`). Implies fallback dispatch would never run for this failure — the schema rejection IS the SOP's "refuse" path, making the F4 label at line 458 dead.
- **Severity:** NIT. Either (a) relabel line 458's DEFAULT to F1 refuse (schema-refuses is the operational F1), or (b) add a sentence clarifying that "schema rejection" short-circuits the matrix for this row. Not blocking; the matrix is an "implementation crib" per line 445 so duplicating the refuse-by-schema row isn't incorrect.

### N2 NIT — API 17B/17J citation lacks edition pin

- **Evidence:** Line 57 cites "API 17B/17J" with no edition, year, or section — unlike DNV-RP-H103 which pins "Oct 2021 ed. §4". API 17B has multiple editions; a reviewer cannot recompute against an unspecified edition.
- **Severity:** NIT. Secondary citation for `plsv.yaml` only; the primary (TechnipFMC + OTC-25303) is adequate for LOA/beam/DP/reel capacity. Pin when implementation writes the YAML.

### N3 NIT — Deliveries-log schema (line 157) uses `state` field while later prose (line 460) adds "all fallbacks F1-F5 logged" to the markdown log without defining the log's column shape

- **Evidence:** Line 157 defines the JSON-row schema for the delivery log entry per prospect. Line 460 says "every fallback application must be logged in `docs/gtm/deliveries-log.md`" + the JSON sidecar (lines 464-480). But the markdown table column set in acceptance criterion 615 is `prospect_id | demo | delivered_utc | gated_url_hash | purge_after_utc | fallback_applied` — that's 6 columns, and DOES NOT include the state-machine states (`DELIVERED_EMAIL_ONLY` etc) from line 157 schema. Two logs (one markdown for humans, one JSON sidecar for audit) with slightly different shapes.
- **Severity:** NIT. Resolvable by reconciling the markdown table in acceptance line 615 to include a `state` column, or documenting that the markdown log is a human summary distinct from the machine audit. Either is fine; plan just doesn't call it out.

### N4 NIT — `additionalProperties: false` on `vessel` conflicts with `properties: { vessel: false }` forbidding mechanism under corner case

- **Evidence:** Line 232-234 (`vessel` object schema) sets `additionalProperties: false` AND `required: [shape, source]`. Line 301 (`allOf` branch for demos 1/2) overrides with `properties: { vessel: false }`. In JSON-Schema draft-07, a `properties.<key>: false` subschema does correctly forbid the key at that object-level — but the forbidding happens at the ROOT object, not the `vessel` object. The live test confirms correct behavior. NIT is documentational: a reader of the bare `vessel` subschema (lines 232-251) might not realize it is never evaluated when `target_demo in {demo_01, demo_02}` because the `allOf` at root forbids the property outright. A one-line comment in the schema JSON would aid reviewer comprehension.
- **Severity:** NIT. Behavior is correct (verified by live execution); only a clarity improvement.

## Claims verified (≥5)

1. **JSON Schema executability.** Extracted schema (lines 212-307), ran `json.loads()` → PASS; `Draft7Validator.check_schema()` → PASS; 4 behavioural tests all match plan claims. **Evidence:** live execution output above.
2. **Past-tense drift.** 11 grep hits on drift patterns; all confirmed FUTURE/EXISTING-referent or plan-self-reference. No false past-tense artifact claims. **Evidence:** grep output + `ls` checks (intake/, prospect_adapter.py, branded_report.py, deliveries-log.md all absent as plan says).
3. **Cross-repo claim.** `aceengineer-website/.git` is a distinct repo; `git ls-files | grep aceengineer-website` → 0 in workspace-hub. Current `aceengineer-website/robots.txt` has no `Disallow: /private/` (only a commented-out placeholder); `vercel.json` has no `X-Robots-Tag`. Plan correctly prescribes these as modifications AND acknowledges cross-repo nature at lines 674-680. **Evidence:** bash output.
4. **D1 path consistency.** Line 136 reads `/private/<sha256-hash-of-(prospect-id + salt + date)>/<slug>.html` — aligned with Files-to-Change at lines 511-513, `Note` at 516, tests 585-586, acceptance 623-624. No stray `/prospects/` in gating context. **Evidence:** `sed -n '132,145p'` output.
5. **D2 enum reconciliation.** Line 460 prose reads "all fallbacks F1-F5 will be logged"; line 473 enum is `["F1", "F2", "F3", "F4", "F5"]`; matrix at 446-458 consistent.
6. **Citations resolvability.** 8 of 9 sources have lookup-sufficient metadata (OTC# + year + title, ISBN + author + edition, vendor + model + URL). API 17B/17J lacks edition — filed as NIT N2.
7. **State machine completeness.** 4 terminal states defined, retry policy quantified (30s/2min/10min), 5 TDD tests at line 158 one-per-transition. Compensating action present. D4 recovery-transition deferred with rationale.
8. **D3 cross-repo rigor.** 5 concrete sub-points (distinct repo, two pushes, Vercel rebuild trigger, rollback asymmetry, SOP checklist) vs hand-wave.

## Summary

Plan v3.1 passes Codex-grade verification. All 10 round-1 MAJORs have verifiable fixes at cited lines; the two most technically demanding — Codex M3 (executable schema) and Claude M2 (`vessel: false` actually forbidding) — confirmed by live `jsonschema.Draft7Validator` execution with behavioural accept/reject matching claims exactly. Round-2 D1/D2/D3 applied correctly. Cross-repo D3 is independently verified against the actual filesystem (aceengineer-website IS a distinct git repo; current robots.txt/vercel.json lack the prescribed entries as the plan states). Past-tense drift audit: clean. Citation metadata meets lookup-resolvability bar on 8 of 9 sources. Security-by-obscurity for `/private/<hash>` is explicitly labeled and bracketed by correct defenses (NDA + robots + X-Robots-Tag + purge) with documented upgrade paths. Four NITs (N1-N4) are doc-polish only, not blockers. Verdict: **APPROVE**; proceed to implementation.
