# Plan for aceengineer-strategy #3: ICP Confirmation — Primary Buyer Segment for Paid Integration Tier

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-04-25
> **Issue:** https://github.com/vamseeachanta/aceengineer-strategy/issues/3
> **Parent epic:** https://github.com/vamseeachanta/aceengineer-strategy/issues/1
> **Review artifacts:** scripts/review/results/2026-04-25-plan-aces-3-claude.md (pending)

---

## Resource Intelligence Summary

### Existing repo code

- Not directly applicable — this is a strategy decision, not an implementation. AceEngineer existing consulting client list (in `aceengineer-admin/` or `aceengineer-strategy/` private repo) is the most relevant input but not under code-review here.
- Found: `aceengineer-website/` exists; current public positioning is general-purpose engineering consulting, not vertical-segment-specific. Future ICP-aligned messaging in #5 (calculator) and #6 (browser) will inherit the decision from this plan.

### Standards

Not applicable.

### LLM Wiki pages consulted

Not applicable for ICP decision.

### Documents consulted

- aceengineer-strategy issue #1 (epic body) — revenue model section now reframed as open-core: subscription tier $15K–$30K/seat/yr for **paid integration surface** (API + SLA + integration support), institutional tier $50K–$200K/yr for embedded copilot + custom calibrations.
- aceengineer-strategy issue #3 (this issue's body) — buyer-options matrix with A/B/C/D candidates and per-segment economics estimates.
- aceengineer-strategy issue #2 (wedge plan) — locks mooring vertical, which constrains ICP suitability (operators with FPSO/spread-mooring assets are most natural fit).
- SemiAnalysis case study (their primary ICPs: investors + chip-industry strategists + AI lab CTOs) — comparable model fetched 2026-04-25.
- Workspace-hub memory `project_field_dev_economics.md`, `project_field_dev_arch_patterns.md` — adjacent verticals with different ICP fits (financial buyers / EPC bid teams more relevant for those).

### Gaps identified

- No existing AceEngineer client-segmentation document captures explicit ICP for a flywheel offering.
- Named anchor accounts not yet enumerated (depends on user input — issue #3 explicitly lists this as open question).
- Public-by-default policy interaction with each ICP not yet documented (operators are most sensitive to data publication; financial buyers are most permissive).

### Evidence (embedded verification)

**Issue states** (verified 2026-04-25):
- aceengineer-strategy `#3` — OPEN — "[P0] ICP confirmation: primary buyer segment for paid integration tier"
- aceengineer-strategy `#1` — OPEN (epic)

**File existence:**
- MISSING (this plan creates): `docs/governance/flywheel-icp-decision.md`

**Source count:** 5 distinct sources above.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-25-aces-3-flywheel-icp.md` |
| Decision artifact | `docs/governance/flywheel-icp-decision.md` |
| Plan review — Claude | `scripts/review/results/2026-04-25-plan-aces-3-claude.md` |
| Plan review — Codex | DEFERRED (codex-cli upstream broken) |
| Plan review — Gemini | DEFERRED (strategy doc) |

---

## Deliverable

A decision artifact at `docs/governance/flywheel-icp-decision.md` that locks the primary ICP for the v1 paid integration tier (#7, #8), names 3–5 anchor target accounts, defines graduation criteria for adding a second ICP, and documents how the public-by-default policy interacts with the chosen ICP's procurement and information-sharing norms.

---

## Pseudocode

T1 — trivial; see Files to Change.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/governance/flywheel-icp-decision.md` | Locks primary ICP, names target accounts, defines public-by-default interaction |
| Update | `docs/plans/README.md` | Add row for this plan |

---

## Decision Content (to be written into `flywheel-icp-decision.md`)

1. **Primary ICP (locked by user):** _user selects from issue #3 options A/B/C/D or "start with two"_
2. **Rationale:** why this segment first — economic, procurement-cycle, mooring-vertical-fit, public-by-default-fit
3. **Named anchor accounts (3–5):** _user provides_
4. **Public-by-default × ICP procurement-norms interaction (pre-enumerated guidance per F1 review patch).** Pick the row matching the locked ICP and refine:

| ICP | Default-publish acceptability | Competitive-sensitivity vectors | Per-engagement opt-out scope |
|---|---|---|---|
| A — Operators | Acceptable for atlas + anonymized failure entries | Metocean conditions revealing asset location; incident proximity to peer assets | Per-asset opt-out clause (mandatory) + per-incident review |
| B — EPCs | Acceptable | Bid-win details; project-scope IP; competitive cost benchmarks | Per-project opt-out (default 24-month embargo on identifiable details) |
| C — Class societies / insurers | Strongly acceptable (their business is information-sharing) | Investigation-active embargo (during open inquiry) | Investigation-status flag with auto-publish at closure |
| D — Financial buyers | Fully acceptable | Pre-deal MNPI windows | Quiet-period flag with auto-clear at deal close |

5. **Paid-tier value drivers for this ICP:** specific to the segment's workflow integration needs (e.g., for operators: integration with IRM/asset-management systems; for EPCs: bid-team standards crosswalk + benchmark exports; for class societies: incident-corpus exports + standards-delta tracking; for financial buyers: aggregate dashboards + screening models)
6. **Sales motion:** typical contact path (engineering manager → integrity head → CFO; or bid-team lead → engineering director → procurement), expected cycle length, dollar-value range
7. **Graduation criteria for adding a second ICP:** trigger conditions (e.g., "after 3 paying anchor accounts in primary ICP, or after vertical-2 launch")

---

## TDD / Validation Checks

| Check | What it verifies |
|---|---|
| `flywheel-icp-decision.md` exists at agreed path | File presence |
| Section 1 (locked ICP) is filled (not placeholder) | Decision actually made |
| Section 3 lists ≥3 named target accounts | Concreteness |
| Section 5 lists at least 3 paid-tier value drivers specific to chosen ICP | Differentiation from public substrate |
| Cross-reference grep: dependent issues #7, #8, #9, #11 cite this artifact | Bidirectional linkage |

---

## Pre-Execution Gate (per F2 review patch)

This plan **cannot execute** until the user replies to aceengineer-strategy issue #3 with both:
1. Primary-ICP selection (one of A / B / C / D, or "start with two: X + Y").
2. ≥3 named anchor accounts for the chosen ICP.

Plan-approval is *separate from* execution-readiness. The user may approve the plan *structure* via `status:plan-approved` while the user-input items are still pending; execution still blocks on the pre-execution gate above. This separation is intentional — it lets the user pre-bless the plan structure before the named-account discussion.

## Acceptance Criteria

- [ ] `docs/governance/flywheel-icp-decision.md` created and committed
- [ ] Pre-execution gate satisfied: user has selected primary ICP and provided named anchor accounts (per the gate above)
- [ ] Public-by-default × ICP-procurement-norms interaction explicitly documented for this ICP (using the pre-enumerated table as starting point, refined to chosen ICP)
- [ ] `docs/plans/README.md` updated
- [ ] aceengineer-strategy issue #3 closure comment cites artifact path
- [ ] Cross-references in #7, #8, #9, #11 updated to `§Cross-links` sections

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (self-r3) | MINOR | F1 (per-ICP procurement-norms × public-by-default interaction pre-enumerated — fixed inline as §Decision Content #4 table), F2 (pre-execution gate added separating plan-approval from execution-readiness — fixed inline). See `scripts/review/results/2026-04-25-plan-aces-3-claude.md`. |
| Codex | UNAVAILABLE | codex-cli 0.124.0 upstream regression; #2479 filed; deferred. |
| Gemini | DEFERRED | Plan content is user-decision-pending; cross-provider review adds limited value until decisions land. Recommend Gemini re-review post-user-input. |

**Overall result:** PASS (Claude MINOR, all findings patched inline).

Revisions made based on review:
- §Decision Content #4: pre-enumerated table for A/B/C/D × public-by-default interaction added.
- New §Pre-Execution Gate: explicit separation of plan-approval (structure) from execution-readiness (user-input-dependent).
- §Acceptance Criteria: gate moved out, criteria refined to reference table.

---

## Risks and Open Questions

- **Risk:** locking single ICP too early may miss a faster-converting adjacent segment. Mitigation: explicit graduation criteria for adding ICP-2, reviewed at portfolio cadence (#10).
- **Risk:** public-by-default policy may clash with operator information-sharing norms. Mitigation: client-opt-out clause from #9 must be ICP-aware; default-publish for anonymized findings, opt-out for entries that would reveal asset identity.
- **Open:** the user must select from A/B/C/D options in issue #3 body and name anchor accounts. This plan cannot be implemented until that selection lands.

---

## Complexity: T1

T1 — single decision-artifact file. The decision content depends on user input; once provided, the artifact is short and the cross-reference updates are mechanical.
