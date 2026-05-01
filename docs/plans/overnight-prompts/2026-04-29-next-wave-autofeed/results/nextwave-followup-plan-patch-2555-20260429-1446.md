# Next-wave follow-up plan patch — #2555 (vessel capability charts)

> **Wave.** ace-linux-1 next-wave autofeed worker; planning-only follow-up to `gtm-review-2554-2555.md`.
> **Lane class.** plan-patch (not approval, not GitHub mutation, not cross-provider fanout).
> **Worker.** Claude main session, planning/research-scoped permissions only.
> **Date.** 2026-04-29 (timestamp suffix `20260429-1446`).
> **Wave prompt source.** Inline operator prompt with hard guardrails; not a saved overnight-prompt file.

---

## Live issue state (verified 2026-04-29 read-only via `gh issue view 2555 --json state,labels,updatedAt`)

| Field | Value |
|---|---|
| State | `OPEN` |
| Labels | `priority:high`, `cat:business`, `cat:strategy`, `domain:gtm` |
| `updatedAt` | `2026-04-29T18:44:35Z` |
| `status:plan-review` present? | NO |
| `status:plan-approved` present? | NO |

No GitHub mutation was performed by this lane. The live state read above is the only `gh` invocation this wave executed against issue #2555.

---

## Files changed (this wave)

| Path | Change |
|---|---|
| `docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md` | (a) Pseudocode block updated to add the standards-citation-completeness assertion and the `assert exists("docs/reports/gtm/assets/")` mkdir gate. (b) Cross-provider AC tightened to require **all three** providers' live verdicts (UNAVAILABLE no longer admissible). (c) Two new acceptance criteria added: asset-directory creation gate + caption-completeness/omission-rationale rule. (d) Adversarial Review Summary "Remaining tasks" first bullet rewritten to require *both* live Codex and live Gemini. (e) New "Next-wave patch (2026-04-29)" block appended to the Revisions list documenting this lane's patches and what was *not* done. |

No other files were touched. The storyboard at `docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md` was NOT edited (per wave guardrail #4). The Claude/Codex/Gemini review artifacts were NOT edited.

---

## Finding-by-finding resolution

The five Claude MINOR findings (per `scripts/review/results/2026-04-29-plan-2555-nextwave-claude.md` lines 14-24) and their post-patch state:

| # | Claude finding | Pre-wave state | Action this wave | Post-wave state |
|---|---|---|---|---|
| 1 | TDD Test List row 1 grep `^## Chart C` is off-by-one heading depth (literal returns 0; should be `^### Chart C`) | Already corrected by an earlier wave — plan line 188 reads `grep `^### Chart C` count in storyboard` | NONE — verified the prior fix is intact | RESOLVED (already-fixed; verified) |
| 2 | AC #5 (Claude + Codex + Gemini) unmet without Codex+Gemini live evidence | Plan line 209 admitted a "permitted fallback" where Claude + 1 live + 1 UNAVAILABLE-documented could satisfy the AC; this defeated the user-in-loop gate intent | TIGHTENED — replaced the AC text so all three providers' live verdicts are required and UNAVAILABLE provenance is explicitly NOT sufficient for any of the three | RESOLVED (tightened) |
| 3 | Chart-rendering implementation home unspecified vs. "no `digitalmodel/` edits" rule | Already resolved in earlier wave — `scripts/gtm/render_brochure_charts.py` named at lines 23, 49, 173, 212 of plan and storyboard line 49 | NONE — verified the prior fix is intact and consistent across plan + storyboard | RESOLVED (already-fixed; verified) |
| 4 | Brochure-asset target dir `docs/reports/gtm/assets/` mkdir gate not in pseudocode | Pseudocode referenced `asset_home="docs/reports/gtm/assets/"` but had no `assert exists(...)` or mkdir step | ADDED — pseudocode now has `assert exists("docs/reports/gtm/assets/"), "asset-directory gate not met; create via follow-on slice"` plus an explanatory comment that directory creation belongs to the follow-on implementation-slice plan, not this artifact. New AC added binding this gate at plan-AC level. | RESOLVED (gate added) |
| 5 | C1 caption omits API RP 1111 despite shallow-S-lay job inheriting it | Storyboard line 82 already cites all four standards including API RP 1111 (the Claude finding was based on a stale read of the storyboard); plan-AC had no enforcement language for the inherited-standards-completeness rule | ADDED at plan-level only (storyboard not edited per guardrail) — pseudocode now asserts `set(C.inherited_standards) <= set(caption.standards) | set(C.omission_rationale.keys())`. New AC added requiring captions to cite the full inherited-standards set or record an omission rationale inline. | RESOLVED (plan-level enforcement; storyboard unchanged) |

**Positive verification (recorded as evidence by Claude reviewer, not a finding):** Storyboard headline-number "Shallow Water Barge: 100% pass rate across 30 cases" matches `digitalmodel/examples/demos/gtm/results/vessel_comparison_matrix.json` exactly (`pass_rate_pct: 100.0`, `cases_pass: 30`, `cases_total: 30`). This patch wave did not re-verify; relies on the prior-wave attestation.

---

## Remaining blockers (post-patch)

| Blocker | Why it remains | What unblocks it | Owner |
|---|---|---|---|
| Cross-provider AC unmet — no live Codex verdict | Codex (next-wave) artifact is UNAVAILABLE; tightened AC explicitly rejects UNAVAILABLE provenance | A permitted lane on a host with codex-cli ≥ 0.123.0 verified working runs `bash scripts/review/plan-review-fanout.sh docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md --providers=codex --output-dir=scripts/review/results`. Canonical artifact lands at `scripts/review/results/2026-04-29-plan-2555-codex.md` (no `-nextwave` suffix). | A permitted-execution lane (this wave was planning/research-scoped) |
| Cross-provider AC unmet — no live Gemini verdict | Gemini (next-wave) artifact is UNAVAILABLE; tightened AC explicitly rejects UNAVAILABLE provenance | A permitted lane runs `bash scripts/review/plan-review-fanout.sh docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md --providers=gemini --output-dir=scripts/review/results` with `GEMINI_CLI_TRUST_WORKSPACE=true` (per memory `feedback_gemini_trust_env_blocks_reviews.md`). | A permitted-execution lane |
| `status:plan-review` cannot be applied | Per-plan AC contract (now strict) and per durable rule `feedback_never_offer_to_self_label_plan_approved.md` | Both Codex and Gemini live artifacts arriving with APPROVE or MINOR verdicts AND a permitted lane patching the Adversarial Review Summary table to record them | The above two providers + a permitted patch lane |
| `status:plan-approved` cannot be applied by any lane | User gate is load-bearing across session boundaries (`feedback_never_offer_to_self_label_plan_approved.md`) | User explicitly approves after seeing the canonical-fanout artifacts | User only |
| Codex CLI 0.124.0 stdin-hang regression | Per memory `feedback_codex_cli_0_124_upstream_regression.md` (#2479) — host-level dependency for the Codex provider | Downgrade to 0.123.0 OR upstream patch; permitted lane verifies the version pin before dispatch | Operator / host config |

Sibling lanes #2556 (brochure-send) and #2557 (productivity review) stay paused until #2555 (and #2554) reach `status:plan-approved`.

---

## Boundary compliance

| Wave guardrail | Compliance |
|---|---|
| Workspace = `/mnt/local-analysis/workspace-hub`; no ace-linux-2 dispatch | OK — all work local; no remote invocation |
| Planning/review/synthesis only; no production-code changes outside the named plan file | OK — only `docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md` edited (planning artifact); no edits to `digitalmodel/`, `assethold/`, `worldenergydata/`, `frontierdeepwater/`, `ai-orchestrator-template/`, or any subrepo |
| No outreach drafted/sent | OK — no outreach drafts touched, no recruiter/contractor email, no external publishing |
| No private contact details exposed; no secrets printed | OK — no contact-detail or secret content in this artifact |
| No GitHub mutations: no `gh issue edit/comment/close`, no `gh pr ...` | OK — only `gh issue view --json state,labels,updatedAt` (read-only) executed |
| No `status:plan-review` applied | OK — label not changed; tightened AC explicitly forbids self-promotion |
| No `status:plan-approved` applied | OK — label not changed; user-in-loop gate preserved |
| No `.planning/plan-approved/*` markers created/edited | OK — no files touched under `.planning/plan-approved/` |
| No `scripts/review/plan-review-fanout.sh`, `codex`, `gemini`, or mutating Hermes commands run | OK — none invoked; permission scope of this lane prevents fanout dispatch |
| No edits to `digitalmodel/`, `assethold/`, `worldenergydata/`, `frontierdeepwater/`, `ai-orchestrator-template/` | OK — verified by edit set |
| Storyboard / report files NOT edited | OK — storyboard at `docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md` was read but not modified; finding 5's enforcement was added at plan-AC level only |
| Result artifact written to the exact specified path | OK — `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2555-20260429-1446.md` |
| Single primary result artifact | OK — one file written by this lane |

No durable memory writes were made by this wave (consistent with the parent autofeed wave's contract and `feedback_never_offer_to_self_label_plan_approved.md`'s implicit "do not encode self-approve workarounds in memory"). All relevant memory entries cited in the patched plan and this artifact were already present pre-wave.

---

## Patch-quality self-check

- **Edit-safety per `.claude/rules/coding-style.md`:** every edit was a targeted single-site replacement with the surrounding context preserved; no bulk find-replace; the three edits were applied sequentially with file re-reads where the harness required; no duplicate definitions or deleted-adjacent-content errors observed. Plan structure (sections, tables, code fence) preserved end-to-end.
- **Finding 1 + 3 + 5 already-resolved attestations:** verified at the line numbers cited above against the file state read at the start of this wave; no relitigation of a prior wave's fixes.
- **Tightening direction:** the AC change is one-way restrictive (admits strictly fewer evidence configurations than before). It cannot accidentally promote the plan past the user-in-loop gate. This is consistent with the memory-recorded preference for never offering to self-label `status:plan-approved`.
- **Pseudocode additions are advisory (planning-only):** the `assert exists(...)` and `assert set(...) <= ...` lines are part of the storyboard's chart-derivation contract, not executable code. The follow-on implementation-slice plan must translate them into concrete checks (likely `pathlib.Path(...).is_dir()` and a frozenset comparison in `scripts/gtm/render_brochure_charts.py`).

---

## Lane classification

**COMPLETED_WITH_RESULT.**

All five Claude MINOR findings are now either (a) verified-already-fixed by a prior wave or (b) addressed in this patch wave via low-risk plan-file edits. The cross-provider AC has been tightened in line with the wave prompt's preferred resolution. Two new acceptance criteria were added (asset-directory gate + caption-citation-completeness rule). No GitHub mutations occurred. No production code paths were touched. The plan remains `draft`; `status:plan-review` and `status:plan-approved` were not applied. The next safe lane is a permitted execution lane that drives `scripts/review/plan-review-fanout.sh` for both `codex` and `gemini` providers and lands the canonical artifacts at `scripts/review/results/2026-04-29-plan-2555-{codex,gemini}.md`, after which a separate permitted lane can patch the Adversarial Review Summary table and apply `status:plan-review` for user review.
