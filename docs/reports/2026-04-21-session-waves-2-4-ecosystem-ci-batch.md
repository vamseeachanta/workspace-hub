# Session Report — 2026-04-21 Ecosystem CI Batch: Waves 2-4

**Parent meta-issue:** #2424 (6-of-7 ecosystem repos red)
**Session:** 2026-04-21 — agent-team-driven multi-wave planning + adversarial review
**Scope:** 6 handoff child issues of #2424 → 2 approved, 4 revised-but-not-yet-approval-ready
**Status at exit:** mid-batch — Wave 4 re-review complete on 3 of 4 plan-review items; 1 (#2442) stuck in agent early-exit loop

---

## 1. Final state per issue

| Issue | Title | Label | Plan file | Approval marker | Review artifacts |
|---|---|---|---|---|---|
| #2433 | worldenergydata-ci | `status:plan-approved` | `docs/plans/2026-04-21-issue-2433-worldenergydata-ci.md` | `.planning/plan-approved/2433.md` | Wave-2 artifacts `scripts/review/results/20260421T155659Z-*2433*` |
| #2437 | workspace-hub-prune | `status:plan-approved` | `docs/plans/2026-04-21-issue-2437-workspace-hub-prune.md` | `.planning/plan-approved/2437.md` | Wave-2 artifacts `scripts/review/results/20260421T155649Z-*2437*` |
| #2441 | digitalmodel-pylife-dep | `status:plan-review` | `docs/plans/2026-04-21-issue-2441-digitalmodel-pylife-dep.md` | — | Wave 2 + Wave 4 (`-r2.md`) — aggregate MAJOR |
| #2442 | assethold-python-tests (HIGH) | `status:plan-review` | `docs/plans/2026-04-21-issue-2442-assethold-python-tests.md` | — | Wave 2 complete; **Wave 4 INCOMPLETE (agent early-exit ×2)** |
| #2443 | achantas-data-markdown-lint | `status:plan-review` | `docs/plans/2026-04-21-issue-2443-achantas-data-markdown-lint.md` | — | Wave 2 + Wave 4 (`-r2.md`) — aggregate MAJOR |
| #2444 | aceengineer-admin-ci | `status:plan-review` | `docs/plans/2026-04-21-issue-2444-aceengineer-admin-ci.md` | — | Wave 2 + Wave 4 (`-r2.md`) — aggregate MAJOR |

---

## 2. Wave progression

| Wave | Shape | Commit | Outcome |
|---|---|---|---|
| **1 — Planning drafts** | 6 parallel agents | (auto-sync `3b09fc067`) | 2 refined, 4 drafted; all 6 GH comments posted |
| **1.5 — Consolidation** | Serial orchestrator | `8093303a2` | Markers + README rows + label advances for #2433/#2437; rollbacks for #2441/#2442/#2443/#2444 |
| **2 — Adversarial review** | 4 parallel agents | — | #2442 needed retry; all 4 aggregate MAJOR |
| **3 — Plan revisions** | 4 parallel agents | `fe5f216e5` (#2442) + `bf2222da2` (others) | All 4 agents reported HIGH confidence for Wave 4 |
| **4 — Re-review** | 4 parallel agents | — | 3 returned MAJOR (Wave 3 regressions found); #2442 early-exit again |

---

## 3. Wave 4 verdicts (3 completed)

### #2441 digitalmodel-pylife-dep
- Claude APPROVE (5-item issues-found checklist)
- Codex MAJOR
- Gemini MAJOR
- **Aggregate: MAJOR**
- New blockers introduced by Wave 3:
  1. `coverage.json` chicken-and-egg in `digitalmodel/quality_gates.yaml` — blocks "first run green" claim
  2. Regression baseline scoped only to `fatigue/` subtree rather than full test tree
  3. Local `pytest -m "not solver"` diverges from actual CI command
  4. Plan body's §Adversarial Review Summary section documents only one wave

### #2443 achantas-data-markdown-lint
- Claude MAJOR
- Codex MAJOR
- Gemini MINOR (improved from MAJOR)
- **Aggregate: MAJOR**
- New blockers introduced by Wave 3:
  1. TDD step-2 floor-assertion has `{"default": false}` bypass gap (convergent 3/3)
  2. Internal contradiction: Acceptance Criteria forbids whole-host lychee exclusions; Risks section authorizes them
  3. `json5` import undeclared (not stdlib)

### #2444 aceengineer-admin-ci
- Claude APPROVE
- Codex MAJOR
- Gemini MAJOR (with one hallucinated finding, correctly filtered)
- **Aggregate: MAJOR**
- New blockers introduced by Wave 3:
  1. `aceengineer-admin/.gitignore:36` gitignores `uv.lock`, but Wave 3 adopted `uv sync --frozen` throughout — will fail on fresh CI runner
  2. Trigger-path contract inconsistent across Deliverable vs Spec vs AC (uv.lock in/out)
  3. CLI import target contradiction — Gaps says `aceengineer_admin.cli`, Files-to-Change says `aceengineer_admin.automation.cli`
  4. TDD hard-gate waiver unjustified
- Plus Claude's 3 minor residuals: stale `aceengineer_automation*` in `pyproject.toml:64,76`; ambiguous `test_config.py` rewrite target; non-deterministic "2 min lint" AC

### #2442 assethold-python-tests (HIGH)
- **Wave 4 did not complete.** Both agent dispatches terminated early with identical phrase: "Still running. Let me wait for notifications. The monitor will emit events as output files get populated."
- Deterministic failure — same behaviour on 2 separate agent invocations against this specific plan
- No `-r2.md` artifacts produced
- Wave 2 artifacts do exist (3/3 MAJOR)
- Wave 3 revision was committed by auto-sync (`fe5f216e5`) and includes the 7 applied fixes

---

## 4. Wave 3 regression pattern — ecosystem-level finding

The aggregate verdict pattern across 3 Wave 4 reviews reveals a systematic weakness in the Wave 3 revision process: **revision agents adopted fix mechanisms without independently verifying repo-state preconditions**.

Examples:
- **#2444 `--frozen`** — Wave 3 agent canonicalized `uv sync --frozen` as the install path; did not check whether `uv.lock` is committed (it isn't)
- **#2441 coverage.json** — Wave 3 agent left `quality_gates.yaml` generator sequence unchanged; did not verify `coverage.json` exists before the gate reads it
- **#2443 floor-assertion** — Wave 3 agent added a rule-enabled-check script; did not verify the check works under `{"default": false}` config pattern

In each case, the Wave 3 agent's fix matched the Wave 2 finding description, but the fix's implementation had unverified preconditions that Wave 4 caught.

**Recommendation for future revision-agent prompts:** require inline `ls`/`grep`/`cat` evidence citation for every state-dependent assumption the fix relies on. Not "we use `uv.lock`" — "we use `uv.lock` — `git ls-files aceengineer-admin/uv.lock` returns <verified output>."

---

## 5. #2442 early-exit phenomenon

Two agent dispatches against #2442 (Wave 2 retry + Wave 4 initial) terminated early with verbatim-identical phrasing. Pattern:

- Agent launches the 3 provider scripts (Claude, Codex, Gemini)
- Within ~2-3 minutes, agent returns with message containing "Still running. Let me wait for notifications. The monitor will emit events as output files get populated."
- No artifact files materialized
- Other plans (#2441, #2443, #2444) completed successfully with identical prompts modulo plan-specific content

Hypotheses:
1. The #2442 plan (largest at 324 lines) produces script stdout verbose enough to confuse the agent's "is it done?" heuristic
2. The agent has a recurring hallucination about a "monitor" mechanism for notification
3. Something in the `submit-to-codex.sh` or `submit-to-gemini.sh` interaction with the larger plan file hangs or produces unusual output

Remediation options for next session:
- **Inline approach**: run the 3 provider scripts from orchestrator Bash directly (~10-15 min blocked turn, deterministic)
- **Different prompt architecture**: agent dispatches scripts via a wrapper that `echo "DONE"` on completion, agent polls via tight-loop filesystem check
- **Chunk the plan**: split #2442 into smaller sections and review each; then synthesize

---

## 6. Hand-off — next session paths (options, not directives)

### For the overall batch
- **Path A — Full Wave 5** on all 4 remaining plans. Risk: Wave 3 → Wave 5 could introduce new regressions like Wave 3 did. Mitigation: tighter verification contracts in Wave 5 prompts.
- **Path B — Partial Wave 5**. Plans closest to APPROVE (#2443: 2 items; #2444: 4 items) get tight revision. #2441 + #2442 need scope re-assessment first.
- **Path C — Approve-with-known-risks on #2444**. Claude APPROVE'd it; MAJOR stems from single `uv.lock` issue. User accepts risk, adds marker, advances label. Focus Wave 5 on the other 3.
- **Path D — Pause and reassess batch composition**. If convergence is hard for similar-shape plans, batching may have been the wrong grouping.

### For #2442 specifically
- **Path E — Inline Wave 4** via orchestrator Bash (deterministic, 10-15 min)
- **Path F — Different-shape agent dispatch** (chunked plan or polling wrapper)
- **Path G — Manual Codex/Gemini invocation** by user via CLI, skip the agent layer entirely

---

## 7. Key artifacts reference

| Type | Location |
|---|---|
| All 6 plan files | `docs/plans/2026-04-21-issue-24{33,37,41,42,43,44}-*.md` |
| Approval markers (Cat A only) | `.planning/plan-approved/24{33,37}.md` |
| Wave 2 review artifacts | `scripts/review/results/2026-04-21-plan-24{33,37,41,42,43,44}-*.md` (without `-r2`) |
| Wave 4 review artifacts | `scripts/review/results/2026-04-21-plan-24{41,43,44}-*-r2.md` (missing #2442) |
| README index | `docs/plans/README.md` lines 268-273 |

### Consolidation commits (pushed to origin/main)
- `8093303a2` — Wave-1 consolidation (approvals for #2433/#2437, rollbacks for others)
- `fe5f216e5` — Wave-3 #2442 (auto-sync)
- `bf2222da2` — Wave-2 cross-review + Wave-3 revisions (#2441/#2443/#2444 + all Wave 2 artifacts)

### GitHub comments posted this session
- #2433: Wave-1 plan summary, Wave-1.5 user-approval note
- #2437: Wave-1 plan summary, Wave-1.5 user-approval note
- #2441: Wave-1, Wave-1.5 governance rollback, Wave 2 verdicts, Wave 4 verdicts
- #2442: Wave-1, Wave-1.5 governance rollback, Wave 2 retry verdicts
- #2443: Wave-1, Wave-1.5 governance rollback, Wave 2 verdicts, Wave 4 verdicts
- #2444: Wave-1, Wave-1.5 governance rollback, Wave 2 verdicts, Wave 4 verdicts

---

## 8. User-in-loop gates that remain active

Per planning skill `issue-planning-mode` + memory `feedback_never_offer_to_self_label_plan_approved`, all state transitions on `status:plan-approved` require user authorization. Future session should:

- Not pre-authorize label advancement in handoff-prompt language to downstream agents
- Surface plan state via tables + CLI suggestions, not "I approved" language
- Keep the user-in-loop gate load-bearing across session boundaries
