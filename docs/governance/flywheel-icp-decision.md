# Flywheel ICP Decision — Operators (Primary, v1 Paid Integration Tier)

> **Status:** LOCKED for primary ICP; **PENDING for named anchor accounts** (see §3)
> **Date:** 2026-04-26
> **Authority:** User-approved via aceengineer-strategy [#3](https://github.com/vamseeachanta/aceengineer-strategy/issues/3) `status:plan-approved` (label flipped 2026-04-26) + decision-panel acceptance with explicit deferral on row 4. Local approval marker: `.planning/plan-approved/aces-3.md` (revision-bound to plan SHA `7af80b652`).
> **Plan:** [`docs/plans/2026-04-25-aces-3-flywheel-icp.md`](../plans/2026-04-25-aces-3-flywheel-icp.md)
> **Parent epic:** [aceengineer-strategy #1](https://github.com/vamseeachanta/aceengineer-strategy/issues/1)

---

## 1. Primary ICP (Locked)

**A — Operators** (oil/gas operators with FPSO and spread-mooring assets: Shell, Equinor, Petrobras, ExxonMobil, ADNOC, BP, Chevron, TotalEnergies, ENI, and equivalent peers).

## 2. Rationale

- **Mooring-vertical fit:** operators own the FPSO/spread-mooring assets that the [`flywheel-wedge-decision.md`](./flywheel-wedge-decision.md) wedge targets. EPCs (B) build for operators; class societies (C) regulate operators; financial buyers (D) finance operators. The operator segment is the source of telemetry that closes layers 6 + 7 of the flywheel.
- **Telemetry feedback loop:** the integrity-team workflow at an operator is where mooring failures, line tensions, and anomaly signals originate. The anchor pilot ([aces-#11](https://github.com/vamseeachanta/aceengineer-strategy/issues/11)) must be an operator for the loop to close on real measured data. EPCs see snapshots; operators see continuous time-series.
- **Dollar value:** operators support the institutional pricing tier ($30K–$60K/seat/yr per [aces-#9](https://github.com/vamseeachanta/aceengineer-strategy/issues/9)) — single-asset operators less so, multi-asset majors comfortably.
- **Public-by-default fit:** operators have explicit asset-identity sensitivity (revealed asset location, incident proximity to peer assets) which the per-asset opt-out clause specifically addresses (per the §4 table below). Public-by-default does not mean "publish everything about the asset"; it means "publish the technical learning, anonymize the operator-and-asset identity unless they explicitly want logo credit." Operators accept this framing more readily than they accept "private exclusive data" — because they don't want to fund a competitor's database.

EPCs (B) deferred to ICP-2 (see §7 graduation): faster procurement but data flow is bid-snapshot, not continuous. Class societies and financial buyers similarly deferred — addressable but downstream.

## 3. Named Anchor Accounts — PENDING USER INPUT

⚠️ **This section is the only blocker for full execution of [aces-#11](https://github.com/vamseeachanta/aceengineer-strategy/issues/11) (anchor pilot client).** The plan-structure approval allows this artifact to lock §1, §2, §4–§7. The named accounts below are *candidate suggestions* based on industry-typical mooring-asset operator profiles, **not** locked decisions.

**Candidates (user to confirm or replace):**

| # | Operator | Why a candidate | Deal-shape note |
|---|---|---|---|
| 1 | _______ | strongest existing AceEngineer relationship | warmest path |
| 2 | _______ | second-strongest existing relationship | secondary warm path |
| 3 | _______ | third existing relationship | tertiary warm path |
| 4 | _______ | strategic stretch — industry leader whose endorsement compounds inbound | logo value |
| 5 | _______ | optional second strategic stretch | logo value |

**Industry-default fallback set if user has no specific preferences** (purely generic — replace with actual relationships before outreach):
- Shell (FPSO operator, North Sea + GoM + Brazil + Gulf of Mexico portfolio)
- Equinor (FPSO + spar operator, North Sea + Brazil)
- Petrobras (FPSO operator, largest pre-salt portfolio)
- ExxonMobil (Guyana FPSO + global)
- ADNOC (offshore + emerging FPSO program)

**Action required:** user replies in the next session with 3–5 named operators (preferring existing-relationship over fallback list). On reply, this section locks and [aces-#11](https://github.com/vamseeachanta/aceengineer-strategy/issues/11) execution unblocks.

## 4. Public-by-Default × Operator Procurement-Norms Interaction

| Topic | Default-publish | Per-asset opt-out triggers | Mitigation |
|---|---|---|---|
| Anonymized failure entries (#6 corpus) | ✅ Yes | Asset proximity to peer assets reveals operator-asset combo via inference | Strip metocean fingerprint to ±50nm; jurisdiction-only; date-quarter-only |
| Atlas outputs (#8 atlas dump) | ✅ Yes | None — atlas is parametric, no asset-level data | n/a |
| Failure case w/ logo credit | ✅ Yes (with explicit operator consent) | Active investigation; legal hold; ongoing claim | Investigation-status flag with auto-publish at closure |
| Real-time copilot insights (#12) | ✅ Yes (anonymized findings) | Currency of telemetry (live data is competitive intelligence) | Public release lags ≥1 quarter; entries published in feedback-loop log #13 |
| Calibration deltas to atlas | ✅ Yes | None — atlas already public | n/a |
| Standards-interpretation refinements | ✅ Yes | None — refinements benefit industry | Public to standards-wiki canonical home |

**Per-asset opt-out clause** (mandatory in [aces-#11](https://github.com/vamseeachanta/aceengineer-strategy/issues/11) telemetry agreement template): operator may exclude any specific asset from publication for any duration, no justification required. Default is "all assets in scope unless explicitly excluded." Renewal-review at each MSA renewal.

## 5. Paid-Tier Value Drivers for Operators

These are what we charge for; data alone is public per epic [#1](https://github.com/vamseeachanta/aceengineer-strategy/issues/1) policy.

1. **Integration into IRM / asset-management systems** — direct API into the operator's existing integrity workflow (Maximo, SAP IH, Cireson, AVEVA APM). Saves the operator's integrity team from rebuilding ingestion every time we ship.
2. **SLA-backed query API** — sub-second response, 99.5% uptime, named support response time.
3. **Custom calibration runs** — operator-specific environmental conditions, asset class, line configuration baked into a per-customer atlas slice.
4. **Embedded engineering hours** — senior AceEngineer engineer in the operator's working channel for the first 90 days of #12 copilot deployment.
5. **Standards-update propagation** — when DNV/API revises a clause, paid customers get the calibration delta in their atlas slice within the SLA window; public substrate gets the change in the next quarterly cycle.
6. **Multi-asset rollout playbook** — established procedure to extend from pilot asset to portfolio rollout without bespoke project work each time.

**Anti-pattern (we will not gate):** raw atlas outputs, individual failure entries (except client-opt-out), standards-wiki page contents, screening calculator usage. These are public substrate per epic #1; gating them violates the open-core revenue model.

## 6. Sales Motion

**Typical contact path (operator):** AceEngineer engineering manager → operator's mooring-integrity lead → integrity head → CFO/procurement.

**Cycle length:** 6–9 months from first contact to executed MSA. Pilot/free-tier conversions (per epic [#1](https://github.com/vamseeachanta/aceengineer-strategy/issues/1) freemium-eligibility) compress to 3–4 months.

**Dollar-value range:** $30K–$60K/seat/yr for the integration tier ([aces-#7](https://github.com/vamseeachanta/aceengineer-strategy/issues/7)); $80K–$200K/yr for institutional API access + custom calibrations ([aces-#8](https://github.com/vamseeachanta/aceengineer-strategy/issues/8)); $200K–$1M project-based for the embedded copilot deployment ([aces-#12](https://github.com/vamseeachanta/aceengineer-strategy/issues/12)).

**Anchor-pilot terms** (per [aces-#11](https://github.com/vamseeachanta/aceengineer-strategy/issues/11) plan): founding-customer pricing locked for 5 years if signed in 2026; default-publish telemetry agreement with per-asset opt-out clause.

## 7. Graduation Criteria for Adding ICP-2

ICP-2 (most likely B — EPCs / subsea contractors) becomes a planning candidate when **at least two** of:
- 3 paying operator anchor accounts under MSA, OR
- vertical-2 (riser or field-dev econ) launches per [aces-#14](https://github.com/vamseeachanta/aceengineer-strategy/issues/14), OR
- inbound from EPCs reaches a sustained ≥5 qualified inquiries/quarter (suggesting market pull).

Until then, EPC engagement is opportunistic (we accept inbound, we don't actively target).

---

## Open Items After Anchor Accounts Land

Once user supplies anchor accounts in §3, [aces-#11](https://github.com/vamseeachanta/aceengineer-strategy/issues/11) (anchor pilot client) execution can begin. That issue's deliverables include the telemetry-sharing agreement template and the engagement-economics doc, which build on this artifact's §4 and §6.
