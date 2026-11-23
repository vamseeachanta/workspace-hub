# Entry handoff — SOUL ecosystem follow-up (post-#2719/2446/2411/2722)

Date: 2026-05-16
Predecessor: [`2026-05-16-issue-2719-cross-provider-soul-exit.md`](2026-05-16-issue-2719-cross-provider-soul-exit.md) (this file is the entry pickup for that exit)
Scope: 4 OPEN workspace-hub issues + 3 OPEN sibling-repo PRs awaiting your action across 4 different repos.

---

## Suggested prompt (paste into fresh Claude session)

```
Pick up the SOUL ecosystem follow-up work from the 2026-05-16 session. The
prior session landed:
- workspace-hub#2719 (cross-provider SOUL.md unification, 7 phases, 8 commits)
- workspace-hub#2446 closing-criteria (5/5 satisfied)
- workspace-hub#2411 inventory (4/4 acceptance, 7-repo audit)
- 3 sibling-repo merge-conflict-fix PRs (worldenergydata#415,
  aceengineer-website#15, assethold#51) — all awaiting merge
- 3 new feedback memories (codex_bootstrap_untracked_sed_origin,
  reviewer_dispatch_refetch_live_body, regression_test_broader_than_issue_scope)
- workspace-hub#2722 NEW pre-commit-hook umbrella for merge-conflict
  prevention (status:needs-plan)

Read the exit handoff at `docs/session-handoffs/2026-05-16-issue-2719-
cross-provider-soul-exit.md` for full session state. Then run the
preflight commands below to verify current state. Then triage what to
do next based on the queue.
```

---

## Preflight commands (next session should run before acting)

```bash
# 1. Verify session-critical commits still on origin/main
cd /mnt/local-analysis/workspace-hub
for sha in 354774856 a798e31b8 00e0793f4 965c124f0 1c5c11eb7 bc280bd43 \
           bbaaa4554 9fa7dd490 1e916204a; do
  git merge-base --is-ancestor $sha origin/main 2>/dev/null \
    && echo "✓ $sha" || echo "✗ $sha MISSING"
done

# 2. Verify the new pytest enforcement still passes
uv run python -m pytest tests/enforcement/test_agent_bootstrap_surfaces_receive_constraints.py -o "addopts="
# Expect: 40 passed

# 3. Check drift on built SOUL runtime artifacts
bash scripts/enforcement/check-soul-runtime-drift.sh
# Expect: All SOUL runtime artifacts up to date.

# 4. Verify live runtime symlinks intact
for f in ~/.hermes/SOUL.md ~/.codex/AGENTS.md; do
  echo "$f → $(readlink "$f" 2>/dev/null || echo NOT-A-SYMLINK)"
done

# 5. Check status of all open issues + PRs from prior session
gh issue view 2719 --repo vamseeachanta/workspace-hub --json state,labels
gh issue view 2446 --repo vamseeachanta/workspace-hub --json state,labels
gh issue view 2411 --repo vamseeachanta/workspace-hub --json state,labels
gh issue view 2722 --repo vamseeachanta/workspace-hub --json state,labels
gh pr   view 415  --repo vamseeachanta/worldenergydata  --json state
gh pr   view 15   --repo vamseeachanta/aceengineer-website --json state
gh pr   view 51   --repo vamseeachanta/assethold --json state
```

## State of play

### OPEN — workspace-hub side

| Issue | Why open | Action |
|---|---|---|
| [#2719](https://github.com/vamseeachanta/workspace-hub/issues/2719) | All 7 phases delivered; user-applied close pending | close if no review needed |
| [#2446](https://github.com/vamseeachanta/workspace-hub/issues/2446) | 5/5 acceptance criteria satisfied via #2719 | close if no review needed |
| [#2411](https://github.com/vamseeachanta/workspace-hub/issues/2411) | 4/4 acceptance via 7-repo inventory comment | close if no review needed |
| [#2722](https://github.com/vamseeachanta/workspace-hub/issues/2722) | NEW; pre-commit hook umbrella; `status:needs-plan` | plan + adversarial review + execute |

### OPEN — sibling repos

| PR | Repo | What | Branch |
|---|---|---|---|
| [#415](https://github.com/vamseeachanta/worldenergydata/pull/415) | worldenergydata | merge-conflict fix in `.claude/docs/agents.md` | `fix/414-agents-md-merge-conflict` |
| [#15](https://github.com/vamseeachanta/aceengineer-website/pull/15) | aceengineer-website | merge-conflict fix in 2 blog files | `fix/14-blog-merge-conflict` |
| [#51](https://github.com/vamseeachanta/assethold/pull/51) | assethold | merge-conflict fix in `.claude/settings.json` (merge-both) | `fix/50-settings-merge-conflict` |

All 3 PRs blocked on `main` branch protection (ruleset, not classic). Either user-applied merge OR admin-via-ruleset-API toggle (pattern: [worldenergydata#413](https://github.com/vamseeachanta/worldenergydata/pull/413) precedent).

### Local-vs-origin divergence (workspace-hub)

At session exit (2026-05-16 ~15:30Z), local `main` was **8 ahead / 3 behind** origin/main due to concurrent multi-session writes during this session. Critical commits all on origin. Local commit `bc61311ad` (exit-handoff extension) preserved in reflog only — not pushed. Auto-sync should reconcile organically; if not, next session can `git pull --rebase --autostash` from clean working tree.

**Verification before any new commit**: run preflight command #1 above. If any `✗ MISSING`, do NOT proceed — investigate via reflog first (`feedback_reflog_as_ground_truth`).

## Recommended priority queue (ordered)

### Tier 1 — quick close-outs (user-applied, low risk)

1. **Close [#2446](https://github.com/vamseeachanta/workspace-hub/issues/2446)** — all 5 acceptance criteria satisfied via #2719 commits. One-line `gh issue close 2446 --comment "Closed via #2719 Phase 2a + Phase 7; all 5/5 criteria satisfied."`
2. **Close [#2411](https://github.com/vamseeachanta/workspace-hub/issues/2411)** — 7-repo inventory comment at [issuecomment-4467824635](https://github.com/vamseeachanta/workspace-hub/issues/2411#issuecomment-4467824635) satisfies all 4 ACs.
3. **Close [#2719](https://github.com/vamseeachanta/workspace-hub/issues/2719)** — all 7 phases complete, audit posted, Gemini-stale-input crosswalk documented. Optional: rerun Gemini r2 against live body BEFORE close if T3 closure needed for audit (cost: 1 Gemini quota cycle; benefit: convergent-verdict on as-built state, not stale input).

### Tier 2 — sibling-repo merges (user-applied OR admin-bypass)

4. **Merge [worldenergydata#415](https://github.com/vamseeachanta/worldenergydata/pull/415)** — landed first, simplest fix
5. **Merge [aceengineer-website#15](https://github.com/vamseeachanta/aceengineer-website/pull/15)** — public-facing blog site; resolves 120 markers across 2 files
6. **Merge [assethold#51](https://github.com/vamseeachanta/assethold/pull/51)** — restores broken JSON settings

For each: same admin-via-ruleset-API toggle pattern used on [worldenergydata#413](https://github.com/vamseeachanta/worldenergydata/pull/413) (2026-05-15) if you want to skip review-cycle.

### Tier 3 — new plannable work

7. **Plan + execute [#2722](https://github.com/vamseeachanta/workspace-hub/issues/2722)** — pre-commit-hook propagation across tier-1 repos. T2 complexity. Issue body includes draft implementation outline + edge cases. Next session: plan → `status:plan-review` → user approves → TDD-first execute.

### Tier 4 — deferred / optional

8. **Per-repo adapter-parity rollout** — 5 sibling repos still PARTIAL per [#2411 inventory](https://github.com/vamseeachanta/workspace-hub/issues/2411#issuecomment-4467824635). Could be bundled umbrella OR 5 per-repo issues. Awaiting user direction on scope.
9. **Cross-machine bootstrap dry-run on `ace-linux-2`** — empirically validates Phase 4 `install-soul-runtime.sh` cross-machine claim. Per `feedback_cross_machine_execution`, user-driven on the target machine (not SSH'd from main).
10. **Codex CLI 0.130 stdin-hang regression follow-up** — [#2715](https://github.com/vamseeachanta/workspace-hub/issues/2715) is still open; `feedback_codex_cli_0_124_upstream_regression` updated 2026-05-16.

## Gates to respect

- **Never self-apply `status:plan-approved`** (`feedback_never_offer_to_self_label_plan_approved`) — user gates all approvals
- **Pathspec-form commits** (`git commit -m "..." -- <file>`) — auto-sync writes constantly; never `git add -A` or sweep
- **Refetch live issue body before every review dispatch** (`feedback_reviewer_dispatch_refetch_live_body`) — don't reuse cached `/tmp/<prompt>.txt`
- **Cross-provider review T3 default** for non-trivial work (`feedback_always_adversarial_review_scale_depth`) — Claude r1 + Codex r2 + Gemini r2
- **Verify before recommending from memory** (auto-memory rules) — memory facts may be stale; check current state for file paths, flags, signs

## Key reference artifacts

- **Exit handoff (full session state)**: [`docs/session-handoffs/2026-05-16-issue-2719-cross-provider-soul-exit.md`](2026-05-16-issue-2719-cross-provider-soul-exit.md)
- **#2411 7-repo audit inventory**: [issuecomment-4467824635](https://github.com/vamseeachanta/workspace-hub/issues/2411#issuecomment-4467824635)
- **#2719 r3 reshape body**: [issue body](https://github.com/vamseeachanta/workspace-hub/issues/2719)
- **#2719 Phase 1 Discovery resolution**: [issuecomment-4464316028](https://github.com/vamseeachanta/workspace-hub/issues/2719#issuecomment-4464316028)
- **#2719 Gemini r2 stale-input crosswalk**: [issuecomment-4466874488](https://github.com/vamseeachanta/workspace-hub/issues/2719#issuecomment-4466874488)
- **#2722 pre-commit hook umbrella**: [issue body](https://github.com/vamseeachanta/workspace-hub/issues/2722)

## Memory artifacts written this session

- `feedback_codex_bootstrap_untracked_sed_origin.md`
- `feedback_reviewer_dispatch_refetch_live_body.md`
- `feedback_regression_test_broader_than_issue_scope.md`

All in `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/` and indexed in `MEMORY.md` (auto-memory store; not repo-tracked).

## What success looks like for the next session

Minimal scope: close the 3 ready-to-close issues + merge the 3 ready PRs (user-applied actions; ~10 minutes of GH UI work + auto-sync reconciliation).

Full scope: + plan + adversarial review + execute [#2722](https://github.com/vamseeachanta/workspace-hub/issues/2722) (estimated 30-60 minutes for T2 implementation + reviews).

Stretch scope: + initiate adapter-parity rollout per Tier 4 item 8 (multi-session work; just file the umbrella issue this round).
