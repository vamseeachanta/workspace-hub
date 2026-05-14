# Overnight dispatch — 2026-05-13 wave

> **Plan:** stabilize first (tonight), then 10-parallel (tomorrow).
> **Source:** [#2695](https://github.com/vamseeachanta/workspace-hub/issues/2695) catalog + brain/hands D7 model.

## Tonight (single session)

Run [#2696](https://github.com/vamseeachanta/workspace-hub/issues/2696) Hermes v0.4.0 → v0.13.0 upgrade audit so tomorrow's Hermes lane has verified routing. Single terminal, autonomous.

```
./00-tonight-hermes-upgrade-2696.sh
```

In the morning, verify: `hermes --version` returns ≥ v0.13.0, AND `hermes skill list | grep -i "claude-code\|codex"` shows bundled-skill routing capability. If either fails, the Hermes lane tomorrow falls back to direct Codex CLI calls (still works; loses the routing intelligence).

## Tomorrow (10 parallel sessions)

Open 10 terminals (or 10 tmux/screen panes). One script per terminal.

### Claude lane — Anthropic Max base quota (5 sessions)

| Script | Issue | Tag | Plan |
|---|---|---|---|
| `C1-issue-2533.sh` | repo-portfolio mission/objective | planning-heavy | ✅ |
| `C2-issue-2563.sh` | Telegram for Hermes mobile control | execution-heavy | ✅ |
| `C3-issue-2403.sh` | doc-intel embeddings spike | bidirectional | ✅ |
| `C4-issue-2402.sh` | doc-intel embeddings index | bidirectional | ✅ (depends on C3) |
| `C5-issue-2665.sh` | kanban provider-credit dashboard | bidirectional | ✅ |

**C3 → C4 ordering:** launch C3 first; launch C4 ~30 min later so C3's model selection lands before C4 reads it. OR launch both and accept C4 may need a re-run after C3 commits.

### Hermes lane — Codex via Hermes routing (5 sessions)

| Script | Issue | Tag | Plan | Notes |
|---|---|---|---|---|
| `H1-issue-2269.sh` | openfoam ESI v2312 baseline | execution-heavy | ✅ | digitalmodel; repo-isolated |
| `H2-issue-2112.sh` | SubseaIQ equipment counts backfill | execution-heavy | ⚠️ no plan | /goal will plan from scratch |
| `H3-issue-2055.sh` | subsea cost benchmarking | bidirectional | ⚠️ no plan | depends on H2 |
| `H4-issue-2152.sh` | reporting golden fixture corpus | execution-heavy | ⚠️ no plan | workspace-hub `scripts/review/` |
| `H5-issue-2657.sh` | Hermes llm-wiki path drift | bidirectional | ✅ | overlaps with [#2696](https://github.com/vamseeachanta/workspace-hub/issues/2696) — may need defer |

## Pre-launch checklist (run before opening 10 terminals)

```bash
# 1. Verify Hermes upgrade landed (from tonight)
hermes --version  # expect ≥ v0.13.0

# 2. Verify all 10 issues are still at status:plan-approved
for n in 2533 2563 2403 2402 2665 2269 2112 2055 2152 2657; do
  echo -n "#$n: "
  gh issue view $n --repo vamseeachanta/workspace-hub --json labels --jq '[.labels[].name | select(test("status:"))] | join(",")'
done

# 3. Verify no WIP labels in flight on any target issue
gh issue list --repo vamseeachanta/workspace-hub --label wip --state open --limit 20

# 4. Check git status across affected repos
for r in /mnt/local-analysis/workspace-hub /mnt/local-analysis/digitalmodel; do
  echo "=== $r ==="; cd "$r" && git status --short
done

# 5. Verify markers still present
for n in 2533 2563 2403 2402 2665 2269 2112 2055 2152 2657; do
  test -f /mnt/local-analysis/workspace-hub/.planning/plan-approved/${n}.md && echo "$n OK" || echo "$n MISSING_MARKER"
done
```

## Mid-run monitoring

Each session logs to `logs/overnight-2026-05-14/{C1..C5,H1..H5}-issue-NNNN.log`. Tail any of them. If a session hangs >2 hours, check for:
- Permission prompts (use `--dangerously-skip-permissions` or `bypassPermissions` flag at launch)
- Git lock contention (`feedback_git_status_lock_storm` — zombie `git status` processes from sibling sessions)
- Hermes preflight conflicts (`feedback_hermes_active_preflight_check` — Hermes cleanup loops on main can revert commits)

## Morning triage

In the AM, run:

```bash
./morning-triage.sh  # (not pre-staged; user composes based on overnight outcomes)
```

Or manually: for each session script, check the log tail + the issue's most-recent comment for progress reports. Each script is instructed to post a progress comment every ~30 min.

## Risk acceptance

User chose "Stabilize first" + "Pre-stage launch commands". Risks accepted:
- Hermes v0.13.0 routing layer is unverified until tonight's audit completes (mitigation: tonight)
- 4 candidates (H2/H3/H4 no-plan + H5 overlap) are higher risk; user has accepted the trade-off
- 10-parallel exceeds the catalog's 5-pick weekly cap — user has explicitly authorized

Per `feedback_never_offer_to_self_label_plan_approved`: no implementing agent (including me, including overnight sessions) sets `status:plan-approved` for itself. All gates are user-set.
