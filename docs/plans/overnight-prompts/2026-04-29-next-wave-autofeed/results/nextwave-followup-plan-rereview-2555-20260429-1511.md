# Next-wave follow-up plan re-review — #2555 (vessel capability charts)

> **Wave.** ace-linux-1 next-wave autofeed worker; cold-context re-review of #2555 plan after the 14:46 patch lane.
> **Lane class.** plan-rereview (read-only; no plan edits, no GitHub mutations, no fanout dispatch, no source code).
> **Worker.** Claude main session, planning/research-scoped permissions only.
> **Date.** 2026-04-29 (timestamp suffix `20260429-1511`).
> **Wave prompt source.** Inline operator prompt with hard guardrails; not a saved overnight-prompt file.

---

## Executive verdict

**MINOR_PATCH_NEEDED.** Ready for user decision; not an approval recommendation.

The 14:46 patch lane resolved all five prior MINOR findings from `gtm-review-2554-2555.md` (the underlying Claude self-review at `scripts/review/results/2026-04-29-plan-2555-nextwave-claude.md`): (1) the TDD heading-depth grep pattern, (2) the cross-provider AC tightening, (3) the chart-rendering code-home naming, (4) the asset-directory mkdir gate, and (5) the standards-citation enforcement at plan-AC level. Verification was performed by direct read of the plan, the storyboard, and the upstream data files — not by trusting the patch report's attestations.

However, the patch's tightening introduced three new MINOR document-consistency drift findings, all stemming from the patch lane's deliberate scope narrowing to the plan file alone (storyboard, Risks section, sibling captions left uncorrected):

- **A.** Storyboard §223 still describes the now-rejected "permitted fallback" provider-review policy, contradicting the tightened plan AC §209.
- **B.** Plan Risks §260 still names "Claude + Gemini cross-coverage" as a Codex-blocked mitigation, contradicting the same tightened AC.
- **C.** Storyboard caption for **Chart C3** cites only DNV-RP-H103 and omits DNV-ST-N001 (which is inherited from C3's data input `csv_hlv_vessels.json`) with **no omission rationale recorded** — a direct violation of the new plan AC the patch itself just added.

None of these are MAJOR (no factual errors, no scope violations, no breaches of the autofeed wave's guardrails). All three are document-consistency repairs the next permitted patch lane should harmonize alongside any cross-provider fanout work. The plan correctly remains `draft` and `status:plan-review` is not applicable while the cross-provider live evidence remains absent.

---

## Live issue state

Verified read-only via `gh issue view 2555 --json state,labels,updatedAt` at 2026-04-29 (this lane's only `gh` invocation):

| Field | Value |
|---|---|
| State | `OPEN` |
| Labels | `priority:high`, `cat:business`, `cat:strategy`, `domain:gtm` |
| `updatedAt` | `2026-04-29T18:44:35Z` |
| `status:plan-review` present? | NO |
| `status:plan-approved` present? | NO |

`updatedAt` is identical to the value the 14:46 patch lane recorded, confirming no GitHub-side activity has occurred between the patch and this re-review.

---

## Prior findings re-check table

The five Claude MINOR findings were drawn from `scripts/review/results/2026-04-29-plan-2555-nextwave-claude.md` lines 14-24 and reproduced in `gtm-review-2554-2555.md` lines 81-86. Each finding's re-check below was performed by reading the cited line ranges of the current plan and storyboard files directly, not by accepting the patch report's status claims at face value.

| # | Original finding | Patch claim | Verified status | Evidence |
|---|---|---|---|---|
| 1 | TDD Test List row 1 grep `^## Chart C` is off-by-one heading depth (literal returns 0; storyboard charts are at depth 3, `### Chart C1..C4`) | "Already corrected by an earlier wave — plan reads `^### Chart C`" | **RESOLVED** | Plan line 188 reads `grep `^### Chart C` count in storyboard`. Storyboard headings `### Chart C1`, `### Chart C2`, `### Chart C3`, `### Chart C4` at lines 61, 96, 131, 166. Pattern + content match; check is now falsifiable as authored. |
| 2 | AC §209 (Claude + Codex + Gemini live) unmet without external-provider live evidence; older "permitted fallback" clause defeated user-in-loop intent | "Tightened — UNAVAILABLE no longer admissible for any provider" | **RESOLVED at AC level**, but see new finding A and B below for residual contradictions in storyboard and Risks section | Plan line 209 now reads "Cross-provider adversarial review evidence is recorded before any `status:plan-review` label is applied: required evidence is Claude **and** Codex **and** Gemini live verdicts (each APPROVE or MINOR). UNAVAILABLE provenance is NOT sufficient for any of the three providers". Direction is one-way restrictive (admits strictly fewer evidence configurations than the prior text). |
| 3 | Chart-rendering implementation home unspecified vs. "no `digitalmodel/` edits" rule | "Already named `scripts/gtm/render_brochure_charts.py` at plan lines 23, 49, 173, 212 + storyboard line 49" | **RESOLVED** | Plan line 23 (Resource Intelligence): "implementation home to a new follow-on wrapper script at `scripts/gtm/render_brochure_charts.py`". Plan line 173 (Files to Change): `Create (future implementation slice) \| scripts/gtm/render_brochure_charts.py`. Plan line 212 (Acceptance Criteria): "Future implementation home is explicitly `scripts/gtm/render_brochure_charts.py`". Storyboard line 49: "The future render entry point is a new wrapper script at `scripts/gtm/render_brochure_charts.py`. That wrapper may import `digitalmodel/examples/demos/gtm/report_template.py` helpers, but #2555 itself does not edit `digitalmodel/` source." Plan's "no `digitalmodel/` edits" rule and the rendering-home claim are now reconciled across both artifacts. |
| 4 | Brochure-asset target dir `docs/reports/gtm/assets/` mkdir gate not in pseudocode | "Pseudocode now has `assert exists(...)` + AC binding directory creation to follow-on slice" | **RESOLVED** | Plan line 159 (Pseudocode): `assert exists("docs/reports/gtm/assets/"), "asset-directory gate not met; create via follow-on slice"`. Plan line 213 (Acceptance Criteria): "Future implementation-slice plan creates `docs/reports/gtm/assets/` via `mkdir -p` as an explicit Files-to-Change row before any render call. Render aborts cleanly if the directory is missing... This planning artifact does NOT create the directory itself." Gate is now spelled at both pseudocode and AC layers. |
| 5 | C1 caption draft cites three of four inherited standards; API RP 1111 omitted without justification | "Storyboard line 82 already cites all four standards including API RP 1111 (Claude finding was based on a stale read); plan now adds AC enforcement of inherited-standards-completeness or omission rationale" | **RESOLVED for C1**, but new finding C below: C3 violates the same new AC | Storyboard line 82 (C1 caption): "Coloured cells show pass rate of cases meeting governing-load checks per DNV-RP-H103, DNV-ST-N001, DNV-ST-F101, and API RP 1111 where shallow-pipelay screening is involved." All four inherited standards cited; API RP 1111 carries scope-conditional language ("where shallow-pipelay screening is involved") that is acceptable defensible-claim phrasing because C1 covers three jobs (mudmat, jumper, shallow pipelay) with API RP 1111 inherited only for the third. Plan line 214 (new AC): "Every chart caption cites the full inherited-standards set from the upstream JSON `_references` arrays... If a standard is intentionally omitted... the storyboard chart entry must record the omission rationale inline; bare omission is not acceptable." Plan line 154 (new pseudocode assertion): `assert set(C.inherited_standards) <= set(caption.standards) | set(C.omission_rationale.keys())`. AC is binding for the storyboard, not just C1. |

All five prior findings are RESOLVED for the artifact site each finding originally cited. The patch lane's "verified-already-fixed" attestations for findings 1, 3, and 5 (C1) hold up against direct file inspection.

---

## New findings (introduced or exposed by the patch)

### Finding A — MINOR — Storyboard §223 contradicts tightened plan AC §209

**Where.** `docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md:223`.

**What.** The storyboard's Legal & Evidence Gate currently reads:

> Provider-review readiness for this storyboard follows the paired plan: preferred evidence is Claude + Codex + Gemini live verdicts; permitted fallback is Claude plus at least one additional live provider verdict, with any unavailable provider explicitly documented with timestamp and blocking reason in `scripts/review/results/2026-04-29-plan-2555-*.md`.

This is the **older** policy that the 14:46 patch lane explicitly rejected when it tightened plan AC §209 to "UNAVAILABLE provenance is NOT sufficient for any of the three providers". The two artifacts now disagree on whether a Claude + 1-live + 1-documented-unavailable configuration satisfies the cross-provider gate.

**Why this matters.** The storyboard is the canonical chart-pack spec that the sibling brochure-send issue #2556 will read. If a future agent reads the storyboard's permissive fallback first, it could promote the plan past `status:plan-review` on weaker evidence than the tightened plan AC requires. The plan AC is the binding gate — but maintaining a single source of truth across plan + storyboard avoids ambiguity at handoff time.

**Patch lane attribution.** This contradiction was created by the patch lane's deliberate guardrail-respecting decision to leave the storyboard untouched. The lane was correct to honor its read-only-on-non-plan-files boundary; the resulting drift is now a follow-on repair item.

**Suggested resolution.** The next permitted patch lane should rewrite storyboard §223 to mirror plan AC §209's "all three live, UNAVAILABLE not sufficient" language.

### Finding B — MINOR — Plan Risks §260 contradicts tightened plan AC §209

**Where.** `docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md:260`.

**What.** The Risks and Open Questions section retains the older Codex-blocked mitigation:

> Risk: Codex review-runner regression (per memory: codex-cli stdin-hang and sandbox-no-execution issues) may block adversarial review. Mitigation: wait for clean Codex evidence rather than self-approve; if blocked, document with same provenance pattern used in `aces-2`/`aces-3`/`aces-4` (Codex UNAVAILABLE annotated) and rely on Claude + Gemini cross-coverage.

The mitigation's last clause — "rely on Claude + Gemini cross-coverage" — assumes that Claude + Gemini suffices when Codex is blocked. AC §209 (tightened by the same patch) now requires all three live verdicts and explicitly rejects UNAVAILABLE provenance for any of the three. The Risks section and the AC contradict each other inside a single artifact.

**Why this matters.** Internal contradictions in a plan tend to be resolved in favor of whichever section a downstream reader hits first. If a permitted lane reads Risks §260 before AC §209, it may dispatch a Claude + Gemini-only fanout and consider the gate satisfied. The Risks-section text is also the most likely text to be quoted in any handoff comment to GitHub.

**Suggested resolution.** Rewrite the Risks §260 mitigation to: "Mitigation: wait for live Codex evidence before any status escalation; the tightened AC §209 does NOT admit a Codex-blocked fallback. If Codex CLI 0.124.0 stdin-hang persists, escalate to operator for downgrade per `feedback_codex_cli_0_124_upstream_regression.md` (#2479)." Keep the link to AC §209 explicit so future readers cannot read Risks in isolation.

### Finding C — MINOR — Storyboard C3 caption violates new plan AC §214

**Where.** `docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md:153` (Chart C3 caption draft).

**What.** Chart C3's data input is `digitalmodel/examples/demos/gtm/data/csv_hlv_vessels.json` (storyboard line 142). Per plan §28-32, that file's `_references` array inherits **DNV-RP-H103** and **DNV-ST-N001**. C3's caption draft (line 153) reads:

> Crane-utilisation margin at 1500 m water depth for the 50 / 100 / 200 te mudmat installation cases. Both vessel classes pass go/no-go, but margin matters: lower utilisation reduces sensitivity to weight growth, rigging revisions, and weather stand-by. Vessel crane curves are representative-class. Per DNV-RP-H103 dynamic amplification framework; full lift sensitivity requires project-specific RAO/sea-state inputs.

DNV-RP-H103 is cited; **DNV-ST-N001 is omitted with no omission rationale**. Plan AC §214 (added by the 14:46 patch) reads:

> Every chart caption cites the full inherited-standards set from the upstream JSON `_references` arrays (DNV-ST-F101, DNV-RP-H103, DNV-ST-N001, DNV-OS-H101 where applicable, API RP 1111 where shallow-pipelay screening is in scope). If a standard is intentionally omitted (e.g., scope-limited to deepwater-only or crane-lift-only jobs), the storyboard chart entry must record the omission rationale inline; bare omission is not acceptable.

C3's omission of DNV-ST-N001 without an omission rationale is a direct violation of the AC the patch itself just added.

**Why this matters.** The original Claude reviewer found a similar issue at C1 (which subsequent storyboard text resolved). The patch then turned the rule into a binding plan-level AC — but did not audit the rest of the storyboard against the new rule before adopting it. C3 is the most obvious miss; C2 and C4 were re-checked during this re-review and pass.

**Detail of re-check on each chart's caption:**

| Chart | Data inputs | Inherited standards | Caption cites | Rationale recorded? | Status |
|---|---|---|---|---|---|
| C1 | `vessel_comparison_matrix.json` (cross-demo, all four standards inherited transitively) | DNV-RP-H103, DNV-ST-N001, DNV-ST-F101, API RP 1111 | All four cited (line 82) | N/A — full coverage | OK |
| C2 | `pipelay_vessels.json` + `vessel_comparison_matrix.json` (PLV head-to-head subset) | DNV-ST-F101, API RP 1111 (pipelay-only inherited set) | DNV-ST-F101, API RP 1111 (line 118) | N/A — full coverage of pipelay-only inherited set | OK |
| C3 | `csv_hlv_vessels.json` + `structure_comparison_matrix.json` | DNV-RP-H103, DNV-ST-N001 | DNV-RP-H103 only (line 153) | **NO** | **VIOLATION of new AC §214** |
| C4 | `docs/gtm/capability-map.md` (no JSON `_references` arrays consumed) | (none from JSON) | "Per-discipline standards citations inherited from upstream" — generic | N/A — AC is scoped to "JSON `_references` arrays" which C4 does not consume | OK (boundary case) |

**Suggested resolution.** Either add DNV-ST-N001 to C3's caption ("Per DNV-RP-H103 dynamic amplification framework and DNV-ST-N001 marine-operations governing-load envelope") or add an omission_rationale subsection under C3 (e.g., "DNV-ST-N001 omitted from C3 caption: this chart is scoped to crane-utilisation margin under nominal operability, not the marine-operations envelope; DNV-ST-N001 governing checks were not exercised by the structure_comparison_matrix.json feed."). The fix lives in the storyboard, which the patch lane could not edit; the next permitted lane should bundle it with the Finding A storyboard repair.

---

## Boundary compliance

All hard guardrails from the operator prompt were respected by this re-review lane:

| Wave guardrail | Compliance |
|---|---|
| Workspace = `/mnt/local-analysis/workspace-hub` | OK — all reads local |
| `gh issue view 2555 --json state,labels,updatedAt` only (read-only) | OK — single read-only `gh` call; output recorded in §"Live issue state" |
| Did NOT run `gh issue edit/comment/close`, `gh pr *`, `scripts/review/plan-review-fanout.sh`, `codex`, or `gemini` | OK — none invoked |
| Did NOT apply `status:plan-approved` | OK — no GitHub label changes |
| Did NOT apply `status:plan-review` | OK — no GitHub label changes |
| Did NOT create or edit `.planning/plan-approved/*` markers | OK — no files touched in `.planning/plan-approved/` |
| Did NOT implement code | OK — no code changes |
| Did NOT edit the plan or any production/source/report artifact | OK — read-only on plan, storyboard, review artifacts, upstream data files |
| Did NOT send outreach or expose private contact details | OK — no outreach surface touched |
| Did NOT print or hardcode secrets | OK |
| Wrote exactly one primary result artifact at the specified path | OK — `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-rereview-2555-20260429-1511.md` |
| Did NOT overwrite other lanes' result files | OK — the 14:46 patch result file at `…/nextwave-followup-plan-patch-2555-20260429-1446.md` is untouched; the prior `gtm-review-2554-2555.md` is untouched; this lane writes only its own file |
| Phrased any approve-like outcome as ready for user decision (never as approval) | OK — verdict is `MINOR_PATCH_NEEDED` (not approve-like); the executive verdict explicitly says "Ready for user decision; not an approval recommendation." |

No durable memory writes were made by this lane.

---

## Lane classification

**COMPLETED_WITH_RESULT.**
