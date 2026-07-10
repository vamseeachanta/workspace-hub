# Plan for [#3415](https://github.com/vamseeachanta/workspace-hub/issues/3415): validate the broker workflow and lock a federal-acreage-aware pilot

> **Status:** plan-review
> **Complexity:** T2
> **Date:** 2026-07-09
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3415
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** r1 `scripts/review/results/2026-07-09-plan-3415-r1-{claude,codex,gemini}.md` | r2 unavailable records `scripts/review/results/2026-07-09-plan-3415-r2-unavailable-{claude,codex,gemini}.md` | r2 fallback `scripts/review/results/2026-07-09-plan-3415-r2b-{claude,codex}.md` | r3 main-session resolution `scripts/review/results/2026-07-09-plan-3415-r3-main.md`

---

## Resource Intelligence Summary

### Existing repo code

- Current control-plane scope lives in parent [#3414](https://github.com/vamseeachanta/workspace-hub/issues/3414) and children [#3416](https://github.com/vamseeachanta/workspace-hub/issues/3416)-[#3423](https://github.com/vamseeachanta/workspace-hub/issues/3423). The tree separates private-repo boundaries, security, intake, evidence, QA, export, public-source integration, and training so this issue will remain a research/decision slice.
- No Landman Project Desk application exists in `workspace-hub`; this issue will not create one. The downstream application work will consume the pilot contract produced here.
- [worldenergydata issue 924](https://github.com/vamseeachanta/worldenergydata/issues/924) and [landman.py at the pinned planning commit](https://github.com/vamseeachanta/worldenergydata/blob/0c5393b18590cf787b3eb020a7d418f3f36fb0f7/packages/worldenergydata-landman/src/worldenergydata/landman/landman.py) show that the current default provider path advertises `county_records` but imports a missing module. The pilot report will classify this source path as unproven until that issue is implemented.
- [county_reference.py at the pinned planning commit](https://github.com/vamseeachanta/worldenergydata/blob/0c5393b18590cf787b3eb020a7d418f3f36fb0f7/packages/worldenergydata-landman/src/worldenergydata/landman/providers/county_reference.py) covers seven states. Its Colorado rows are Weld, Adams, and Arapahoe; it has no Rio Blanco or Garfield row. Those rows are reference data, not title evidence or verified automation coverage.

### Standards

Not applicable. This issue will produce a workflow and pilot decision, not an engineering calculation. Legal-description, lease, and title facts will remain source evidence requiring human review; the report will not produce legal advice or a title opinion.

### LLM Wiki pages consulted

- [llm-wiki PR 745](https://github.com/vamseeachanta/llm-wiki/pull/745), [source note at review head](https://github.com/vamseeachanta/llm-wiki/blob/cf0e2b2ddccd456edba753f6052b34d08c3564b5/wikis/trends-and-strategies/wiki/sources/coe-2026-landman-demand-collide.md) - records the Collide post as a practitioner signal rather than verified labor-market data. It supports an intake -> decomposition -> assignment -> evidence -> exception -> QA -> packet workflow and a one-jurisdiction MVP.

### Documents consulted

- [#3415](https://github.com/vamseeachanta/workspace-hub/issues/3415) - requires a broker/project-manager workflow, a TX/OK/CO comparison, an explicit federal/mixed/private acreage decision, one county cluster, one project class, and measurable success criteria.
- [#3414](https://github.com/vamseeachanta/workspace-hub/issues/3414) - requires public-safe fixtures and a strict distinction between federal lease evidence and county title evidence.
- [worldenergydata issue 909](https://github.com/vamseeachanta/worldenergydata/issues/909), [issue 913](https://github.com/vamseeachanta/worldenergydata/issues/913), [issue 914](https://github.com/vamseeachanta/worldenergydata/issues/914), [issue 915](https://github.com/vamseeachanta/worldenergydata/issues/915), [issue 924](https://github.com/vamseeachanta/worldenergydata/issues/924), and [issue 925](https://github.com/vamseeachanta/worldenergydata/issues/925) - separate source inventory, raw BLM acquisition, county feasibility, state joins, executable provider routing, and federal-acreage output. This plan will not duplicate those implementations.
- [BLM MLRS public reports](https://reports.blm.gov/reports/MLRS) - exposes public case-recordation reports, oil-and-gas lease reports, serial-register pages, and legal-land-description reports. BLM states that MLRS replaces LR2000 and has Privacy Act redactions.
- [BLM national MLRS oil-and-gas lease layer](https://gis.blm.gov/nlsdb/rest/services/HUB/BLM_Natl_MLRS_Oil_and_Gas_Leases/FeatureServer/0) - exposes queryable polygon features with case identifiers, disposition, case acres, dates, administrative/geographic state, source, and quality fields. It is lease/case evidence, not complete ownership/title evidence.
- [BLM Colorado lease sales](https://www.blm.gov/programs/energy-and-minerals/oil-and-gas/leasing/regional-lease-sales/colorado) - records active 2026 leasing; the June 16 sale leased 147 parcels totaling 134,173 acres. This supports testing a federal-aware Colorado workflow without treating sale totals as pilot acreage.
- [Midland County Clerk](https://www.co.midland.tx.us/27/County-Government) and [Reeves County Clerk](https://www.reevescounty.org/departments/county-clerk) - identify the official Texas recording offices; Reeves explicitly exposes online land records and real-property recording. These are access-path evidence, not title conclusions.
- [Grady County Clerk](https://www.gradycountyok.com/195/County-Clerk) and [Canadian County Land Records](https://canadiancounty.org/885/Land-Record-Searches) - identify official Oklahoma deed, mortgage, and oil-and-gas lease records. Grady notes that online fees can apply; Canadian requires a login for images, so both limitations will remain explicit score inputs.
- [Rio Blanco County Recorder](https://www.rbc.us/181/Recorder) - states that records are public and free to inspect, indexed by grantor/grantee rather than tract, and that the office does not perform searches. This is a useful explicit human-in-the-loop county/title constraint.
- [Garfield County Recording Department](https://www.garfieldcountyco.gov/clerk-recorder/recording-department/) - exposes an official index back to 1883, notes that images are not in the index, and states that the county does not perform title searches. Garfield will therefore have its own evidence row rather than inheriting Rio Blanco readiness.
- Drive-index query `landman federal acreage title broker` returned 20 irrelevant CAD title-block matches. No relevant drive file was found; `master_document_index` was unreachable, and two indexes were stale.

### Gaps identified

- No durable artifact maps the broker workflow from intake through reviewed packet delivery.
- No tested, mode-neutral scorecard compares Texas, Oklahoma, and Colorado on public-source readiness, county/title feasibility, fixture reproducibility, broker value, and delivery/exception learning.
- No owner-approved pilot contract fixes the jurisdiction, county cluster, acreage mode, project class, primary persona, exclusions, and success measures.
- County pages establish official access paths but do not prove that a reproducible, public-safe fixture can be assembled without a paid portal or account. That will remain a hard-gate input rather than an assumed fact.
- No interview or outreach authorization exists. This issue will prepare a question set and authorization checkpoint but will not contact anyone.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-07-09T22:38:10-05:00 via `gh issue view`):

- [#3415](https://github.com/vamseeachanta/workspace-hub/issues/3415) - OPEN, `status:needs-plan`, `lane:claude` - broker workflow and pilot validation.
- [#3414](https://github.com/vamseeachanta/workspace-hub/issues/3414) - OPEN, `status:needs-plan`, `lane:claude` - parent application epic.
- [#3416](https://github.com/vamseeachanta/workspace-hub/issues/3416)-[#3423](https://github.com/vamseeachanta/workspace-hub/issues/3423) - OPEN, each with exactly one lane and `status:needs-plan`.
- `worldenergydata` [issue 913](https://github.com/vamseeachanta/worldenergydata/issues/913), [issue 914](https://github.com/vamseeachanta/worldenergydata/issues/914), [issue 924](https://github.com/vamseeachanta/worldenergydata/issues/924), and [issue 925](https://github.com/vamseeachanta/worldenergydata/issues/925) - OPEN and not implemented.

**Federal evidence** (queried 2026-07-09T23:15:20-05:00):

```text
$ for state in TX OK CO; do curl .../query where="GEO_STATE='$state'" returnCountOnly=true; done
TX {"count":4527}
OK {"count":5474}
CO {"count":33271}
```

These are mapped feature counts, not unique leases or acreage. They are directional only and inherit MLRS geometry/quality limitations.

**Drive-index evidence** (2026-07-10T03:42:17Z):

```text
$ DRIVE_SEARCH_NO_METRICS=1 uv run python scripts/data/drive-index-search/search.py \
    "landman federal acreage title broker" --json --limit 20 --caller plan-resource-intel
exit 0; 20 results; all irrelevant CAD "Title Block" token matches
coverage gap: master_document_index unreachable
stale: og_standards_inventory, master_document_index
```

**File state** at planning time:

- EXISTS in [llm-wiki PR 745](https://github.com/vamseeachanta/llm-wiki/pull/745): linked Collide landman-demand source note at review head `cf0e2b2`.
- EXISTS and inspected: `scripts/legal/legal-sanity-scan.sh`, `scripts/workflow/completeness_score.py`, and `scripts/workflow/render_completeness_html.py`. The score module is a pure Python API rather than a CLI; the plan therefore names `classify`, `score_evidence`, and `write_html` explicitly.
- MISSING (this issue will create): `docs/reports/landman/2026-07-09-pilot-decision.yaml`.
- MISSING (this issue will create): `docs/reports/landman/2026-07-09-pilot-decision.html`.
- MISSING (this issue will create): `tests/docs/test_landman_pilot_decision.py`.

**Reproduction proof:** N/A - this is a research/governance issue with no alleged runtime failure. Runtime defects are isolated in [worldenergydata issue 924](https://github.com/vamseeachanta/worldenergydata/issues/924).

Coverage includes the issue tree, llm-wiki source note, six WED issues, three official BLM surfaces, six official county surfaces, pinned repository code, and the drive index.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-09-issue-3415-landman-pilot-validation.md` |
| Evidence and score inputs | `docs/reports/landman/2026-07-09-pilot-evidence.yaml` |
| Decision builder | `scripts/research/build_landman_pilot_decision.py` |
| Machine-readable decision | `docs/reports/landman/2026-07-09-pilot-decision.yaml` |
| Human decision report | `docs/reports/landman/2026-07-09-pilot-decision.html` |
| Contract tests | `tests/docs/test_landman_pilot_decision.py` |
| Completeness report | `docs/reports/<completion-date>-3415-completeness.html` |
| Plan review - r1 | `scripts/review/results/2026-07-09-plan-3415-r1-{claude,codex,gemini}.md` |
| Plan review - r2 fallback | `scripts/review/results/2026-07-09-plan-3415-r2b-{claude,codex}.md` |
| Plan review - r3 resolution | `scripts/review/results/2026-07-09-plan-3415-r3-main.md` |

The `2026-07-09` decision filenames will identify the frozen planning/evidence snapshot, not the eventual implementation date. The completeness artifact alone will use its actual generation date at closeout.

---

## Deliverable

A tested evidence YAML, decision builder, machine-readable decision, and matching HTML report will map the broker/project-manager workflow, compare Texas/Oklahoma/Colorado, and select the highest-scoring candidate that passes every declared hard gate. The selection will lock one jurisdiction/county cluster, federal/mixed/private acreage mode, project class, primary persona, exclusions, and measurable downstream success criteria.

Texas, Oklahoma, and Colorado will enter the same score and hard-gate contract; no leading jurisdiction, county, or acreage mode will be encoded in tests or constants. If no candidate passes all hard gates, eligible leaders tie, or sensitivity changes the winner, the output will be `owner_decision_required` with ranked alternatives and no implicit selection.

---

## Considered Approaches

| Approach | Benefit | Cost / reason not preferred |
|---|---|---|
| Colorado mixed federal/private (leading hypothesis) | Exercises BLM/MLRS, state regulator evidence, split-source exceptions, and human county/title work in one broker-relevant slice | More exception handling; Rio Blanco is manual/grantor-grantee indexed and Garfield lacks county-specific feasibility evidence |
| Texas private-only | Fastest path because Texas regulator data and county references are most mature locally | Defers the federal-acreage differentiator and risks validating only the easiest data surface |
| Colorado federal-only | Simplifies source acquisition around BLM/MLRS | Does not validate the county/title boundary or the broker's mixed-acreage coordination problem |

---

## Declared Decision Contract

The hand-authored evidence YAML will enumerate exactly three candidate clusters, each with exactly two named counties: Texas Permian (`Midland`, `Reeves`), Oklahoma SCOOP/STACK (`Grady`, `Canadian`), and Colorado Piceance (`Rio Blanco`, `Garfield`). Every county will have its own official-source, access, fee/account, index, image, observed-at, confidence, and limitation fields. A cluster will need at least one ready primary county; the second county may be conditional but will never inherit the primary county's readiness.

Eligible candidates will be scored from 0-5 on each criterion and normalized to 100 points. Every score will cite one or more evidence-row IDs. `unknown` will remain unknown and will make the candidate ineligible rather than being converted to zero. The score anchors will be identical for every criterion:

| Score | Evidence anchor |
|---:|---|
| 0 | Official evidence contradicts readiness or pilot fit |
| 1 | Conceptual relevance only; no verified access or reproducible evidence |
| 2 | Official source is accessible but material limitations remain untested or manual |
| 3 | Access and pilot relevance are verified with disclosed limitations |
| 4 | Verified and reproducible with a public-safe fixture path |
| 5 | Verified, reproducible, and fully fits the declared broker workflow and pilot boundary |

| Criterion | Weight |
|---|---:|
| Broker workflow value | 25 |
| Public-source readiness for the candidate's declared acreage mode | 25 |
| County/title feasibility | 20 |
| Public-safe fixture reproducibility | 15 |
| Delivery and exception-learning value | 15 |
| **Total** | **100** |

Federal/mixed/private acreage mode will be a declared decision dimension and hard-gate input, not a second federal bonus. Federal or mixed candidates will require BLM/MLRS readiness evidence; private-only candidates will require an explicit `federal_deferred` decision and will not be penalized for omitting a BLM result. Every candidate will still keep federal, regulator, and county/title conclusions separate.

Each raw score will be `sum(Decimal(score) / Decimal(5) * Decimal(weight))`. Ranking will use the exact unquantized `Decimal`; display will use two decimal places with `ROUND_HALF_UP`. Only exact raw-score equality will count as a tie. A deterministic sensitivity matrix will evaluate every ordered criterion pair by adding five weight points to one criterion and subtracting five from the other, preserving a total of 100. Any eligible-winner change across those variants will require an owner decision rather than being hidden by the base weights.

A candidate will be eligible only when it has complete sourced evidence for all five criteria; an explicit federal/mixed/private mode; a public-safe fixture path that does not require paid portal use or account creation; one ready primary county with its own official evidence row; a two-county cluster with no inherited readiness; separate federal, regulator, and county/title conclusions; and a research-assistance/no-title-opinion boundary. The highest eligible raw score will win only when the sensitivity matrix preserves that winner.

Zero eligible candidates will emit `owner_decision_required` and require evidence remediation; hard gates cannot be waived. A tie or sensitivity flip will emit `owner_decision_required` and stop until the owner records `chosen_candidate`, `actor`, UTC `decided_at`, and `rationale` in the evidence YAML. The builder will compute the score-input hash from all decision inputs while excluding the owner-decision block, accept only an eligible ranked alternative whose record cites that hash, and regenerate a `selected` result. No completeness scoring or issue closeout will proceed while the result is not `selected`.

The evidence YAML will carry a frozen RFC 3339 UTC `decision_timestamp`. Generation will not read wall-clock time. YAML and HTML will use UTF-8, LF newlines, a final newline, sorted mapping keys, fixed criterion/candidate ordering, decimal strings quantized to two places with `ROUND_HALF_UP`, locale-independent formatting, and a fixed renderer version. `--check` will compare exact bytes.

---

## Pseudocode

```text
function build_candidate_scorecard(source_ledger, declared_weights):
    require exact clusters TX=[Midland,Reeves], OK=[Grady,Canadian],
        CO=[Rio Blanco,Garfield] and one official row per county
    define mode-neutral weights and shared 0-5 evidence anchors
    require one evidence row and one limitation row per criterion per candidate
    reject claims without source URL, observed timestamp, access state, and confidence
    reject bool/unknown scores and scores without cited evidence-row IDs
    calculate exact Decimal weighted scores and paired +/-5 sensitivity variants
    return candidates, weights, raw/display scores, sensitivity, hard gates, unresolved gates

function select_pilot(scorecard):
    filter to candidates with a public-safe fixture and no paid/account dependency
    require one ready primary and exactly one named secondary county per cluster
    require separate federal, state-regulator, and county/title evidence decisions;
        require BLM evidence only for federal/mixed modes and federal_deferred for private-only
    rank eligible candidates by exact raw Decimal score
    if no candidate qualifies, emit owner_decision_required with remediation and no waiver
    if eligible leaders tie or sensitivity changes the winner, emit owner_decision_required
        with ranked alternatives and no selected pilot
    if owner decision is required, validate actor/time/rationale/chosen eligible candidate
        and score-input hash before allowing selected
    otherwise return the highest eligible jurisdiction, cluster, acreage mode,
        project class, persona, rationale, and rejected alternatives

function define_broker_workflow(selection):
    emit intake, AOI/tract decomposition, work planning, assignment, evidence capture,
        exception handling, QA/signoff, and packet delivery stages
    define stage inputs, outputs, owner, evidence requirements, and stop conditions
    distinguish broker, landman, trainee, title examiner, and underwriter responsibilities
    attach measurable downstream pilot success criteria and explicit legal limitations

function publish_decision(selection, workflow, source_ledger, output_paths, check=false):
    read decision_timestamp from the hand-authored evidence input; never read wall clock
    generate canonical decision YAML using fixed order, Decimal formatting, UTF-8/LF,
        renderer version, sorted mapping keys, and final newline
    render a readable HTML decision report from the same decision object
    include source ledger, scorecard, rejected alternatives, risks, and no-outreach state
    if check, compare generated bytes with committed outputs and fail on drift
    return both output paths or a nonzero check result
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `tests/docs/test_landman_pilot_decision.py` | TDD contract for scoring, eligibility, owner-decision fallback, provenance, HTML/YAML parity, and no-outreach/legal boundaries |
| Create | `docs/reports/landman/2026-07-09-pilot-evidence.yaml` | Hand-authored TX/OK/CO evidence rows, frozen decision timestamp, limitations, hard-gate inputs, scoring weights, and any owner decision record |
| Create | `scripts/research/build_landman_pilot_decision.py` | Validate evidence, compute selection without a preselected winner, render both outputs, and support `--check` |
| Create | `docs/reports/landman/2026-07-09-pilot-decision.yaml` | Generated machine-readable scorecard, workflow, selection/decision state, success criteria, and source ledger |
| Create | `docs/reports/landman/2026-07-09-pilot-decision.html` | Human-facing decision report, default rich-artifact format |
| Create | `docs/reports/<completion-date>-3415-completeness.html` | Required closeout completeness evidence; generated only after implementation/review evidence exists |
| Update | `docs/plans/README.md` | Keep the plan index synchronized with live issue state |

No application repository, application schema, provider implementation, source downloader, or private-data artifact will be created in this issue.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_decision_schema_and_version` | YAML has a stable top-level contract | decision YAML | schema version, generated/observed timestamps, decision status |
| `test_exact_candidate_clusters_and_counties` | Required comparison is not narrowed after the fact | candidate/county rows | exactly TX Midland/Reeves, OK Grady/Canadian, CO Rio Blanco/Garfield |
| `test_score_anchors_weights_decimal_and_evidence` | Scoring is neutral and reproducible | weights, scores, evidence rows | shared 0-5 anchors; weights total 100; exact Decimal formula; two-place display; every score sourced |
| `test_paired_weight_sensitivity_preserves_total` | Weight fragility is visible | base weights | all ordered +/-5 variants total 100 and are emitted |
| `test_selection_matches_highest_eligible_score` | Tests do not preselect a jurisdiction | synthetic candidates with different winners | selected candidate follows scores and gates |
| `test_no_eligible_candidate_requires_owner_decision` | Hard-gate failure cannot auto-select a fallback | all candidates ineligible | `owner_decision_required`, no selection, ranked alternatives |
| `test_tied_leaders_require_owner_decision` | Tie handling remains human-in-loop | equal eligible leaders | `owner_decision_required`, no selection |
| `test_sensitive_winner_requires_owner_decision` | Base weights cannot conceal a winner flip | sensitivity variant changes winner | `owner_decision_required`, no selection |
| `test_owner_decision_is_bound_and_cannot_waive_gates` | Human resolution is auditable and bounded | tie/sensitivity/no-eligible cases | eligible choice + actor/time/rationale/hash may resolve tie; no-eligible remains blocked |
| `test_selected_pilot_is_complete` | A successful decision is actionable | generated selection block | jurisdiction, cluster, acreage mode, project class, primary persona, rationale |
| `test_ready_counties_require_specific_evidence` | Readiness cannot be inherited | county rows with/without required fields | one ready primary required; conditional secondary disclosed; every county has its own row |
| `test_workflow_has_eight_ordered_stages` | Full broker lifecycle is represented | workflow stages | intake through packet delivery in canonical order |
| `test_persona_boundaries_are_distinct` | Broker needs are not conflated with execution/review roles | persona rows | five named personas with non-overlapping responsibilities |
| `test_federal_and_title_evidence_are_separate` | Federal lease evidence never implies ownership/title completeness | evidence classes | distinct BLM, regulator, county/title classes and limitation |
| `test_success_measures_are_machine_checkable` | Downstream pilot has measurable gates | success criteria | provenance coverage, evidence classes, exception, signoff, no-title-opinion gates |
| `test_success_measures_follow_selected_acreage_mode` | Private-only and federal/mixed winners have coherent evidence gates | synthetic selected modes | regulator + county always; BLM for federal/mixed; `federal_deferred` for private-only |
| `test_builder_check_detects_html_or_yaml_drift` | Acceptance-time anti-drift check fails closed | generated vs edited outputs | `--check` nonzero on either mismatch |
| `test_generation_is_byte_deterministic` | Wall clock, locale, key order, and newline cannot drift outputs | fixed evidence timestamp rendered twice | byte-identical YAML/HTML with fixed order/Decimal/LF/final newline |
| `test_html_matches_yaml_decision` | Both generated outputs share one decision object | YAML + HTML | same state/selection, scores, workflow, risks, and source links |
| `test_outreach_remains_not_authorized` | No interview/contact side effect is implied | authorization block | `not_authorized`, no interviewee/contact records |
| `test_public_safe_and_legal_boundaries` | No private/client identifiers or automated legal conclusion appears | both artifacts | public-safe fixture rule and research-assistance/no-title-opinion disclaimer |

---

## Acceptance Criteria

- [ ] Tests will be written first and fail because the builder/evidence/YAML/HTML artifacts do not yet exist.
- [ ] `uv run pytest tests/docs/test_landman_pilot_decision.py -v` will pass.
- [ ] `uv run python scripts/research/build_landman_pilot_decision.py --check` will confirm the committed YAML and HTML match regenerated bytes. This is an acceptance-time Level-2 check; this issue will not add a new repo-wide CI workflow.
- [ ] Evidence YAML will compare exactly Texas, Oklahoma, and Colorado using declared weights, claim-level provenance, and explicit unknown values.
- [ ] Candidate clusters will be exactly Texas Midland/Reeves, Oklahoma Grady/Canadian, and Colorado Rio Blanco/Garfield; every county will have a separate official-source/access/limitation row, and no county will inherit another county's readiness.
- [ ] Scores will use the shared 0-5 evidence anchors, exact Decimal formula, two-place `ROUND_HALF_UP` display, exact-raw-score ties, and the complete paired +/-5 sensitivity matrix.
- [ ] The builder will select the highest-scoring eligible candidate; no test or constant will require Colorado, Texas, or Oklahoma to win.
- [ ] If no candidate passes every hard gate, eligible leaders tie, or sensitivity changes the winner, YAML and HTML will emit `owner_decision_required`, contain no selected pilot, and show ranked alternatives plus failed gates or sensitivity evidence.
- [ ] A tie/sensitivity decision will remain stopped until an owner record names an eligible choice, actor, UTC decision time, rationale, and matching score-input hash; hard-gate failures will never be owner-waived.
- [ ] The evidence timestamp and renderer version will be inputs; generation will not read wall clock, and two runs will produce byte-identical UTF-8/LF/final-newline outputs with fixed ordering and decimal formatting.
- [ ] The winning candidate will carry one project class and broker/project manager as the primary persona; alternatives may propose different project classes but must use the same scoring contract.
- [ ] The workflow will cover intake -> tract/AOI decomposition -> task plan -> assignment -> evidence -> exceptions -> QA/signoff -> packet.
- [ ] Downstream success will always require one winning-jurisdiction regulator item, one winning-primary-county title/manual-or-unavailable exception, 100% provenance-or-unavailable coverage, and versioned reviewer signoff. Federal/mixed winners will additionally require BLM/MLRS evidence; private-only winners will require a documented `federal_deferred` decision instead.
- [ ] Federal feature counts will be labeled as directional mapped-feature counts, never acreage or unique-lease totals.
- [ ] County/title gaps will remain separate from federal and state-regulator evidence; the report will include a no-title-opinion/no-legal-advice limitation.
- [ ] Interviews, outreach, account creation, paid portals, and representation of A&CE will remain `not_authorized` and unperformed.
- [ ] `bash scripts/legal/legal-sanity-scan.sh` will pass for all committed artifacts.
- [ ] Final code/artifact adversarial review will route to Claude, Codex, and Gemini by default; any unavailable provider will have an explicit artifact, and at least two usable reviews will be required.
- [ ] The issue will carry `gate:completeness` before entering plan review. Closeout will compute changed files from the approved-plan base through implementation HEAD and call `classify(changed_files, {})`; it must return `evidence` because this issue may not change a mapped package. The immutable `score_evidence(..., issue_number=3415)` manifest will total 100: focused tests 25, source ledger/decision contract 20, byte-exact generated YAML/HTML check 15, final `selected` state 15, legal scan 10, and resolved plan-review plus usable no-MAJOR code-review evidence 15. Every item must be met, `result.passed` must be true, and `write_html(result.to_dict(), 3415, ...)` will render the completion-date report. The exact record will be persisted to issue metadata/body before the agent stops for owner-applied `status:completeness-verified`; the agent will never apply that owner-only label.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR (fallback r2) | Parameterize success by winner/mode; add TX/OK official sources; freeze deterministic bytes; operationalize completeness; define tie/date/review contracts |
| Codex | MAJOR (fallback r2) | Remove federal double-weighting; anchor/formalize scoring and sensitivity; stop on owner decisions; define two-county clusters; make completeness executable |
| Gemini | UNAVAILABLE (r1/r2) | No noninteractive Gemini credential was configured; contributed no review signal |
| Main session | RESOLVED (r3) | Patched every r2 finding inline under the required r3 loop-break rule; no additional provider dispatch was performed |

**Overall result:** r2 returned MAJOR and blocked advancement. The r3 main-session resolution will record every finding against the revised text and local checks. The issue may move to `status:plan-review` only after that artifact, the plan, and the index are committed/pushed and the evidence comment exists. Implementation will remain blocked pending explicit user approval.

R3 resolutions:

- Replaced the federal double bonus with five mode-neutral criteria, shared evidence anchors, an exact Decimal formula, raw-score tie rule, and paired-weight sensitivity tests.
- Fixed three explicit two-county clusters and cited official Midland, Reeves, Grady, Canadian, Rio Blanco, and Garfield sources without treating access evidence as title evidence.
- Parameterized success by the selected jurisdiction and acreage mode; BLM evidence is required only for federal/mixed winners, while private-only winners require `federal_deferred`.
- Made `owner_decision_required` a hard stop with a bound owner record for tie/sensitivity cases and no waiver for zero-eligible cases.
- Froze timestamp, renderer, ordering, decimal, encoding, and newline rules so byte-exact `--check` is meaningful.
- Named the existing completeness APIs, immutable 100-point evidence manifest, persistence step, and owner-only close gate.

---

## Risks and Open Questions

- **Risk:** MLRS polygons and counts can omit or imperfectly geocode cases. The decision will treat geometry as evidence with quality metadata, not as complete acreage truth.
- **Risk:** Mixed federal/private acreage can involve split estate and overlapping interests. The pilot will expose uncertainty and county/title gaps rather than infer ownership.
- **Risk:** Current local state-data maturity may favor one jurisdiction. Mode-neutral weights and the complete paired-weight sensitivity matrix will expose rather than conceal that influence.
- **Risk:** Rio Blanco records are not tract-indexed and the recorder does not perform searches. That manual constraint is intentional pilot evidence, not a promise of automated county research.
- **Risk:** Official county pages prove recording/access surfaces, not fixture reproducibility or a title chain. Every county will remain independently conditional until its access and fixture hard gates pass; [worldenergydata issue 914](https://github.com/vamseeachanta/worldenergydata/issues/914) will own deeper portal feasibility.
- **Risk:** BLM acquisition, provider routing, and acreage computation are not implemented. The pilot contract will name [worldenergydata issue 913](https://github.com/vamseeachanta/worldenergydata/issues/913), [issue 924](https://github.com/vamseeachanta/worldenergydata/issues/924), and [issue 925](https://github.com/vamseeachanta/worldenergydata/issues/925) as dependencies rather than simulate readiness.
- **Approval decision:** Approving this plan will authorize the evidence schema, weights, hard gates, and deterministic selection method. It will not pre-approve a jurisdiction, interviews, or outreach; ties and no-eligible-candidate outcomes will return to the owner.

---

## Complexity: T2

**T2** - the issue will create a bounded decision builder, evidence input, two generated decision artifacts, and a structural/provenance test suite. It will consume cross-repository evidence and define a downstream pilot contract without implementing the application or data pipelines.
