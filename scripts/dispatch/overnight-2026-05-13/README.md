# Overnight dispatch — 2026-05-13 wave

> **Plan:** plan-tonight (#2702 routing audit), 13-parallel tomorrow (5 Claude + 8 Hermes→Codex).
> **Source:** [#2695](https://github.com/vamseeachanta/workspace-hub/issues/2695) catalog + brain/hands D7 model.
> **Revision 2026-05-13 21:55:** [#2696](https://github.com/vamseeachanta/workspace-hub/issues/2696) was scoped down + closed (binary upgrade already landed). Tonight's session now plans [#2702](https://github.com/vamseeachanta/workspace-hub/issues/2702) (the empirical routing audit residue). Hermes lane expanded 5→8 (added H6/H7/H8) per user request for efficient Codex quota burn.

## Tonight (single session)

Run the **planning** workflow on [#2702](https://github.com/vamseeachanta/workspace-hub/issues/2702) (empirical `delegate_task` round-trip + Anthropic base/overage check). Single terminal, autonomous. Produces a draft plan + `status:plan-review` on #2702 — does NOT implement (issue is not plan-approved).

```
./00-tonight-issue-2702-routing-audit.sh
```

In the morning, review the draft plan; if good, label #2702 `status:plan-approved` and drop the marker. The H6–H8 lanes do NOT depend on tonight's session completing — they run /goal on already-approved issues. Tonight is concurrent with tomorrow's dispatch only via the routing-layer audit's downstream value (validates whether the 8 Hermes→Codex lanes are landing on the quota pools we think they are).

## Tomorrow (13 parallel sessions)

Open 13 terminals (or 13 tmux/screen panes). One script per terminal.

### Claude lane — Anthropic Max base quota (5 sessions)

| Script | Issue | Tag | Plan |
|---|---|---|---|
| `C1-issue-2533.sh` | repo-portfolio mission/objective | planning-heavy | ✅ |
| `C2-issue-2563.sh` | Telegram for Hermes mobile control | execution-heavy | ✅ |
| `C3-issue-2403.sh` | doc-intel embeddings spike | bidirectional | ✅ |
| `C4-issue-2402.sh` | doc-intel embeddings index | bidirectional | ✅ (depends on C3) |
| `C5-issue-2665.sh` | kanban provider-credit dashboard | bidirectional | ✅ |

**C3 → C4 ordering:** launch C3 first; launch C4 ~30 min later so C3's model selection lands before C4 reads it. OR launch both and accept C4 may need a re-run after C3 commits.

### Hermes lane — Codex via Hermes routing (8 sessions)

| Script | Issue | Tag | Plan | Notes |
|---|---|---|---|---|
| `H1-issue-2269.sh` | openfoam ESI v2312 baseline | execution-heavy | ✅ | digitalmodel; repo-isolated |
| `H2-issue-2112.sh` | SubseaIQ equipment counts backfill | execution-heavy | ⚠️ no plan | /goal will plan from scratch |
| `H3-issue-2055.sh` | subsea cost benchmarking | bidirectional | ⚠️ no plan | depends on H2 |
| `H4-issue-2152.sh` | reporting golden fixture corpus | execution-heavy | ⚠️ no plan | workspace-hub `scripts/review/` |
| `H5-issue-2657.sh` | Hermes llm-wiki path drift | bidirectional | ✅ | overlaps with [#2696](https://github.com/vamseeachanta/workspace-hub/issues/2696) (now closed) — refresh pre-launch check |
| `H6-issue-2694.sh` | catenary cross-domain dup cleanup epic | bidirectional | ✅ | **picklist pick #1**; refactor work fits Codex |
| `H7-issue-2628.sh` | digitalmodel domain-divided CI architecture | bidirectional | ✅ | digitalmodel; repo-isolated; replaces maxfail-masking |
| `H8-issue-1583.sh` | Hermes config parity via repo templates | execution-heavy | ⚠️ no plan | /goal plans first; stops at `status:plan-review` |

## Pre-launch checklist (run before opening 13 terminals)

```bash
# 1. Verify Hermes is at v0.13.0 (already true as of 2026-05-13 — sanity check only)
hermes --version  # expect ≥ v0.13.0

# 2. Verify all 13 issues are still at status:plan-approved
#    (#1583 is acceptable without status:plan-approved IF H8 stops at plan-review per its script)
for n in 2533 2563 2403 2402 2665 2269 2112 2055 2152 2657 2694 2628 1583; do
  echo -n "#$n: "
  gh issue view $n --repo vamseeachanta/workspace-hub --json labels --jq '[.labels[].name | select(test("status:"))] | join(",")'
done

# 3. Verify no WIP labels in flight on any target issue
gh issue list --repo vamseeachanta/workspace-hub --label wip --state open --limit 20

# 4. Check git status across affected repos
for r in /mnt/local-analysis/workspace-hub /mnt/local-analysis/digitalmodel; do
  echo "=== $r ==="; cd "$r" && git status --short
done

# 5. Verify markers still present (informational — label-is-the-gate per current convention;
#    many status:plan-approved issues lack markers, see #2695 bootstrap-comment finding)
for n in 2533 2563 2403 2402 2665 2269 2112 2055 2152 2657 2694 2628 1583; do
  test -f /mnt/local-analysis/workspace-hub/.planning/plan-approved/${n}.md && echo "$n OK" || echo "$n MISSING_MARKER"
done
```

## Mid-run monitoring

Each session logs to `logs/overnight-2026-05-14/{C1..C5,H1..H8}-issue-NNNN.log`. Tail any of them. If a session hangs >2 hours, check for:
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

Risks accepted (rev 2026-05-13 21:55):
- Hermes v0.13.0 is verified-installed; routing-layer behavioral claims (Anthropic base vs. overage; `delegate_task` round-trip) are **not yet empirically validated** — tonight's [#2702](https://github.com/vamseeachanta/workspace-hub/issues/2702) plan will frame that audit. Tomorrow's 8 Hermes→Codex lanes run on the *assumption* the routing model holds; if [#2702](https://github.com/vamseeachanta/workspace-hub/issues/2702) later disproves it, the picklist's quota-pool math needs revision.
- 5 candidates (H2/H3/H4 no-plan, H5 overlap with closed [#2696](https://github.com/vamseeachanta/workspace-hub/issues/2696), H8 no-plan) are higher risk; user has accepted the trade-off. H8 is explicitly instructed to STOP at `status:plan-review` rather than auto-progress.
- 13-parallel exceeds the catalog's 5-pick weekly cap **and** the prior 10-cap user-authorization; this is an explicit expansion to drain Codex quota efficiently. Tag breakdown of the 8 Hermes→Codex lanes: 6 execution-heavy (H1, H2, H4, H6, H7, H8) + 2 bidirectional (H3, H5).
- Resource limit on ace-linux-1: 3 claude processes already running pre-dispatch (PIDs 2875867 / 3032699 / 3185440); 13 more is unprecedented. Watch RAM. If swap engages, kill the lowest-priority lane (likely H3 — depends on H2's output anyway).

Per `feedback_never_offer_to_self_label_plan_approved`: no implementing agent (including me, including overnight sessions) sets `status:plan-approved` for itself. All gates are user-set.
