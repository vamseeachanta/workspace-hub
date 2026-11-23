# Session Handoff — Cradle-to-Grave Engineering Flywheel (2026-04-25 → 2026-04-26)

> **Date:** 2026-04-26
> **Session shape:** Brainstorm → 14-issue tree creation → 4 P0 plans (3 approved + executed, 1 in v2 plan-review on isolated branch) → 2 incidental quality fixes → memory entries
> **Parent epic:** [aceengineer-strategy #1](https://github.com/vamseeachanta/aceengineer-strategy/issues/1)
> **Branch state at exit:** `main` HEAD = `89b5808309`; isolated feature branch `flywheel/aces-5-v2-patch` HEAD = `b3b079ef2` on origin

---

## What Got Built

### Issues (aceengineer-strategy)

14-issue tree (epic + 13 children):

| # | Priority | Status at exit | Title |
|---|---|---|---|
| 1 | epic | scoping | [Epic] Cradle-to-Grave Engineering Flywheel — Strategic Initiative |
| 2 | P0 | **plan-approved** + executed | Wedge confirmation: Approach C + mooring vertical |
| 3 | P0 | **plan-approved** + partial-execution (anchor accounts pending) | ICP confirmation: Operators as primary |
| 4 | P0 | **plan-approved** + Phase 1 executed | Standards LLM-wiki industrialization |
| 5 | P1 | **plan-review** (v2 on isolated branch) | Public mooring quick-screen calculator |
| 6 | P1 | scoping | Public failure-case browser |
| 7 | P2 | scoping | Mooring failure intelligence integration product |
| 8 | P2 | scoping | Mooring parametric atlas API |
| 9 | P2 | scoping | Pricing & licensing model |
| 10 | P2 | scoping | Flywheel portfolio management |
| 11 | P3 | scoping | Anchor pilot client + telemetry-sharing |
| 12 | P3 | scoping | Real-time mooring monitoring copilot |
| 13 | P3 | scoping | Feedback-loop pipeline + public log |
| 14 | P4 | scoping | Replication harness (post-mooring) |

### Artifacts on `main`

- **Plans:** `docs/plans/2026-04-25-aces-{2,3,4}-*.md` and v1 of `docs/plans/2026-04-26-aces-5-*.md`
- **Adversarial reviews:** `scripts/review/results/2026-04-25-plan-aces-{2,3,4}-claude.md` + `2026-04-26-plan-aces-5-claude.md`
- **Approval markers:** `.planning/plan-approved/aces-{2,3,4}.md` (revision-bound per `project_issue_2460_approval_binding.md`)
- **Decision artifacts:** `docs/governance/flywheel-{wedge,icp}-decision.md` + `offshore-marine-standards-canonical-home.md`
- **Design spec + decision panel:** `docs/governance/2026-04-25-cradle-to-grave-engineering-flywheel-design.md` + `2026-04-25-flywheel-p0-decision-panel.md`
- **Plans index:** `docs/plans/README.md` lines 320–323

### Artifacts on `flywheel/aces-5-v2-patch` branch (NOT yet merged)

- v2 plan content for aces-#5 (5 MAJOR + 4 MINOR review findings resolved)
- `fix(quality)`: PEP-723 metadata in `scripts/quality/check_config_drift.py` (commit `c73f54c64`)
- `fix(quality)`: drop `python` prefix in `scripts/quality/check-all.sh` so uv reads PEP-723 (commit `b3b079ef2`)

Compare: https://github.com/vamseeachanta/workspace-hub/compare/main...flywheel/aces-5-v2-patch

### Memory entries written

- `feedback_superpowers_specs_gitignored.md` — brainstorming skill default `docs/superpowers/specs/` is gitignored; use `docs/governance/` instead
- `project_wiki_standards_path_decision.md` — amended (was stale: described #2471 as general substrate; actually CSA-only; aces-#4 now scopes general)

---

## Locked Decisions (for future sessions)

1. **Operating motto:** *the flywheel must continue.* Loop velocity > revenue maximization.
2. **Public-by-default policy:** all artifacts default-public; client opt-out allowed; free-by-client-preference acceptable. **NOT closed-data subscription.**
3. **Open-core revenue model:** revenue from integration + SLA + advisory + real-time copilot. Data is not the moat — the loop is.
4. **Wedge:** Approach C (closed-loop on one vertical end-to-end) on mooring. 18-month time horizon. Soft rollback gate with explicit procedure.
5. **Primary ICP:** Operators (Shell/Equinor/Petrobras/ExxonMobil/ADNOC tier). Anchor accounts pending user input.
6. **Standards canonical home:** `knowledge/wikis/marine-engineering/wiki/standards/<publisher>/<code-id>/`. Phase 2 (populate DNV-OS-E301 + API RP 2SK) requires outside counsel + source-text fixtures + Gemini cross-review.
7. **License-class enum** for standards pages: `summary-only-with-citation` (default for copyrighted) | `cc-by-publishable` | `public-domain-quoted` | `private-derived`.

---

## Open Items (blocking next-session work)

1. **aces-#3 anchor accounts** — user must reply to issue #3 with 3–5 named operators. Sole blocker for #11 execution.
2. **aces-#5 plan-approval** — at `status:plan-review` on isolated branch; user reviews, merges (or cherry-picks `ca7810ad8`), flips label.
3. **aces-#4 Phase 2 prerequisites** — outside-counsel engagement + source-text fixtures provisioned + (optional) Gemini cross-review.

---

## Two Painful Pattern Discoveries (Useful for Next Session)

1. **Hermes "remove unrelated files" cleanup loop.** When Hermes is processing a specific issue (#2488 in this session), it aggressively cleans `main` of files it considers unrelated. My v2 patches landed and were reverted three times before isolation via worktree+branch worked. **Defense:** for non-trivial multi-commit work, use a worktree on a feature branch from the start. Memory reinforces existing entries in `feedback_check_parallel_work.md`, `feedback_isolated_clone_dispatch_race.md`, `feedback_merge_race_silent_revert.md`.
2. **Pre-push hook PEP-723 invocation bug.** `uv run --no-project python <script>` ignores PEP-723 metadata (uv treats `python` as the entry point); fix is `uv run --no-project <script>`. The two `fix(quality)` commits on the branch resolve this; once they merge, `GIT_PRE_PUSH_SKIP=1` (audited bypass) becomes unnecessary for hook-blocked branches.

---

## How to Resume Next Session

```bash
# 1. Check Hermes status (don't commit if active)
pgrep -af "git (rebase|stash push|commit|merge|reset|checkout)" | grep -v grep || echo "(Hermes quiet)"

# 2. Read this handoff for context
cat docs/handoffs/session-2026-04-26-flywheel-cradle-to-grave-exit.md

# 3. Check approval queue
gh issue list --repo vamseeachanta/aceengineer-strategy --label "status:plan-review"
gh issue list --repo vamseeachanta/aceengineer-strategy --label "status:plan-approved"

# 4. If anchor accounts arrived (aces-#3), execute #11 plan-draft
# 5. If aces-#5 merged, plan #6 (failure-case browser) — same calculator pattern
# 6. If standards Phase-2 prerequisites met, execute aces-#4 Phase 2

# 7. Worktree cleanup (if branch is merged or abandoned)
git worktree remove /tmp/flywheel-aces-5-worktree
```

---

## Key URLs

- **Epic:** https://github.com/vamseeachanta/aceengineer-strategy/issues/1
- **Decision panel (single-pass approval surface):** [`docs/governance/2026-04-25-flywheel-p0-decision-panel.md`](../governance/2026-04-25-flywheel-p0-decision-panel.md)
- **Design spec:** [`docs/governance/2026-04-25-cradle-to-grave-engineering-flywheel-design.md`](../governance/2026-04-25-cradle-to-grave-engineering-flywheel-design.md)
- **aces-#5 v2 branch:** https://github.com/vamseeachanta/workspace-hub/tree/flywheel/aces-5-v2-patch
- **Scheduled 24h reminder routine:** `trig_01Nx6xzCx8hEmU2QnnWwEuwV` (one-shot; will fire next ~06:45 AM CT and likely auto-disable post-run)
