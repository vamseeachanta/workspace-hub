# Session exit handoff — 2026-05-16 (paths A + B parallel)

Session ran **Path A** (PE Phase 5 plan + epic creation) and **Path B** (reservoir-engineering Wave 1 founding) in parallel on `vamseeachanta/llm-wiki`.

## Outcomes

| Path | What landed | Commit |
|---|---|---|
| B | `wikis/reservoir-engineering/` founded (Wave 1: CLAUDE.md + 4 wiki/ scaffold files + 2 concept pages = 577 lines / 6 files) | [`4e5d7af6`](https://github.com/vamseeachanta/llm-wiki/commit/4e5d7af6) |
| A | Phase 5 plan + Claude r1 review (288 + 178 lines) | [`1a59ca0d`](https://github.com/vamseeachanta/llm-wiki/commit/1a59ca0d) |
| A | GitHub epic [#92](https://github.com/vamseeachanta/llm-wiki/issues/92) created with `status:plan-review` + r1 summary comment posted | — |
| B | [#40](https://github.com/vamseeachanta/llm-wiki/issues/40) Wave 1 summary comment posted; issue stays OPEN through 5-wave delivery | — |

PE wiki: still **75 pages** (Phase 5 plan is approval-gated; no concept pages landed). RE wiki: **3 pages** (Wave 1 founding scaffold).

llm-wiki main: [`1a59ca0d`](https://github.com/vamseeachanta/llm-wiki/commit/1a59ca0d) on origin/main, clean.

## Open user-decision gate (HARD)

**Phase 5 plan [#92](https://github.com/vamseeachanta/llm-wiki/issues/92) is `status:plan-review`.** Do NOT execute the 3 sub-issues until user explicit-approves the plan and label flips to `status:plan-approved` AND `.planning/plan-approved/92.md` marker is written. Per [[feedback_never_offer_to_self_label_plan_approved]] — user-in-loop gate is load-bearing.

The r1 review surfaces 8 MINOR + 1 MAJOR finding. The MAJOR is the calc-citation half-activation defect (plan currently punts on whether allocation-factor / measurement-uncertainty / allowable-rate formulas activate the sidecar contract or stay doc-only). User-decision needed at approval time — recommend explicit commitment in plan body before approval.

Optional T2 escalation: if MAJOR-1 user-decision warrants cross-provider validation, dispatch Codex r2 via `codex exec` (per [[feedback_codex_needs_pushed_artifact]] — pushed artifact is at [`docs/plans/2026-05-16-issue-92-pe-phase-5-production-accounting-regulatory-handover.md`](https://github.com/vamseeachanta/llm-wiki/blob/main/docs/plans/2026-05-16-issue-92-pe-phase-5-production-accounting-regulatory-handover.md), reachable by Codex GitHub connector).

## Open follow-ups (deferable)

### #40 reservoir-engineering — Waves 2-5 remaining
Each remaining wave needs its own sub-task issue + adversarial review pass. Per the CLAUDE.md 5-wave strategy:
- **Wave 2** — corpus manifest `docs/research/reservoir-engineering-corpus.md` (license-triaged candidates; ≥30 high-quality OR ≥50 mixed)
- **Wave 3** — concept pages: gamma-ray-log-interpretation + dip-azimuth + formation-tops
- **Wave 4** — methodology pages: geosteering-workflow + log-correlation
- **Wave 5** — standards pages: API RP 40 + CWLS LAS 2.0 + SEG-Y Rev 2 + SPWLA references

**Standards-revision verification gap**: Wave 5 standards pages were drafted with `revision: "verify-at-publish-time"` placeholder per founding-session discipline. Before Wave 5 lands, run a fact-verification subagent on:
- API RP 40 current edition (commonly cited 2nd edition 1998 / reaffirmed — verify)
- SPWLA formation-evaluation references (per-publication granularity needed)
- CWLS LAS specifications (2.0 + 3.0 published — canonical citation convention check)
- SEG-Y Rev 2 vs Rev 2.1 current canonical reference

Mirrors Phase 4 [#87](https://github.com/vamseeachanta/llm-wiki/issues/87) MINOR-2 / MINOR-3 fact-verification pattern.

### Phase 5 [#92](https://github.com/vamseeachanta/llm-wiki/issues/92) — POST-APPROVAL execution path
After user approves: create 3 sub-issues serially (per [[feedback_parallel_gh_issue_create_reverses_numbers]] — `&` parallel creates reverse-arrival numbering):
1. `research+ingest(production-engineering): production accounting + measurement — allocation factors + well-test reconciliation + GOR/water-cut tracking + custody-transfer overview + flow-measurement uncertainty`
2. `research+ingest(production-engineering): regulatory reporting — production-allowable rates + state production reporting (TX RRC W-1H/W-2/P-4) + federal production reporting (BSEE 30 CFR 250) + FracFocus chemical disclosure + gas-flaring rules`
3. `research+ingest(production-engineering): surface-handover + data integration — surface-handover-boundary router + manifold-tie-in + choke-skid-and-separator-inlet + production-SCADA-architecture + production-data-historian-patterns`

Dispatch pattern: **Two-batch** per [[feedback_parallel_subagent_shared_target_manifest_deferral]] proven across 3 epics now. Batch 1 = Sub-1 + Sub-2 parallel (disjoint topic surfaces). Batch 2 = Sub-3 solo (heaviest cross-link surface).

Pre-execution hooks (carried from r1 MINORs):
- Run standards-revision fact-verification for API MPMS Ch 20 parts + 30 CFR 250 eCFR date + ISA-95 part revisions
- Surface SCADA vendor-IP deny-list addition to `test_production_chemistry_deny_list.py` (extends Phase 4 production-chemistry-IP pattern to proprietary tag schemas / OPC-UA address-space naming / historian-archive formats)
- Decide explicitly at approval-time on calc-citation activation (the MAJOR-1 surface)

### Meta-work from prior handoffs still deferable
- `test_production_chemistry_deny_list.py` per Phase 4 #87 Codex MAJOR-1 — discipline maintained at content-time but test file not yet created (small PR opportunity)
- Memory pruning: `feedback_parallel_subagent_shared_target_manifest_deferral` could be updated to formalize "2-batch parallel + solo trailing" pattern (currently says ">2 = sequential", proven across 3 epics + this session that it's "2-batch + solo")
- Phase 4 retrospective extract: 3 epics in 1 session validates the pattern at scale; could extract as a workspace-hub-learned skill

## Workspace state at exit

- llm-wiki main: [`1a59ca0d`](https://github.com/vamseeachanta/llm-wiki/commit/1a59ca0d) on origin, clean
- workspace-hub main: was at [`bc61311ad`](https://github.com/vamseeachanta/workspace-hub/commit/bc61311ad) at session start; this handoff commit is the only added work
- Sibling clone `/mnt/local-analysis/llm-wiki` remains 1-ahead/5-behind (untracked rag-benchmark work on [#78](https://github.com/vamseeachanta/llm-wiki/issues/78)) — parallel session, NOT this session's concern; flagged for the #78 worker

## Discipline notes worth re-reading next session

- **Path B's calc-citation contract escape link** (caught at content-time): `permeability.md` originally linked to `../../../../.claude/rules/calc-citation-contract.md` which escapes the llm-wiki repo. Fixed inline before commit. Reinforces a general rule: in `wikis/*/` content, agent-context-tooling files (`.claude/rules/`, feedback memories) should be paraphrased inline or omitted, never path-linked across repo boundaries.
- **Path A's MAJOR-1 self-aware finding**: the subagent caught the plan literally quoting "don't punt to ambiguous middle" then punting. Validates `feedback_adversarial_review_stance` — adversarial framing surfaces contradictions that charitable reading misses.
- **CWD inheritance**: bash session inherited `/mnt/local-analysis/workspace-hub/llm-wiki` cwd from an earlier tool call; commits landed in llm-wiki correctly but the surface was non-obvious. The `git -C <path>` form (or post-hoc `pwd` check) is the defense.

## Next-session first-step recommendation

Ask user: "Approve Phase 5 [#92](https://github.com/vamseeachanta/llm-wiki/issues/92) plan (with MAJOR-1 calc-citation decision), escalate to Codex r2, or focus on #40 Wave 2 (corpus manifest)?"

The three branches are mutually exclusive for the next session's primary work:
1. **Phase 5 approval + execution** → user picks calc-citation posture, label flips to `plan-approved`, marker written, execute 3 sub-issues via two-batch
2. **Phase 5 cross-review** → Codex r2 dispatch (~10-15 min) before final approval decision
3. **#40 Wave 2** → corpus manifest is a self-contained deliverable, doesn't depend on Phase 5 approval; fact-verification for Wave 5 standards can happen in parallel as a small follow-up

Don't auto-pick. Don't self-approve Phase 5 plan. Do not invoke `gh issue create` for Phase 5 sub-issues until `status:plan-approved` is set.
