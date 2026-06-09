# Session entry prompt — epic #2998 Windows / no-SSH ecosystem rollout

> Paste the fenced block below into a fresh Claude Code session (run from `/mnt/local-analysis/workspace-hub`).
> Continuation of epic #2967 (Linux backbone, DELIVERED + live-converged) → #2998 (Windows/no-SSH).
> Full durable detail: auto-memory `project_machine_consistency_dynamic_workflows_2967.md`.

```
You are continuing a multi-machine harness project in workspace-hub (vamseeachanta/workspace-hub).
Work from /mnt/local-analysis/workspace-hub on ace-linux-1.

## MISSION
Build out epic #2998 — extend the (already-delivered, Linux-live) "consistent experience via
dynamic workflows" backbone to the Windows / no-SSH machine ecosystem.

## PREFLIGHT (run first, in order)
1. Read the full project memory:
   ~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/project_machine_consistency_dynamic_workflows_2967.md
2. git fetch origin main --quiet   (the working tree is on a parallel session's branch — do NOT
   switch/branch-surgery it; treat it as read-only-via-refs)
3. gh issue view 2998   (the Windows epic) and its children: 3001 WF0, 2999 WF1, 3000 WF3,
   plus existing-mapped 2815 WF2, 2742 WF4, 2816/2852 WF5.
4. Read docs/session-handoffs/2026-06-09-epic-2967-consistent-experience-delivered.md (on main).

## STATE (what's already true)
- Epic #2967 (Linux) DELIVERED + live-converged on ace-linux-1 + ace-linux-2: F1 deny-list applied,
  F2 role-managed crontabs (external/local crons preserved), F3 dispatch+provider-routing wired,
  F4 venue contract, F5 equality matrix building in prod. All F1–F5 + epic CLOSED.
- Epic #2998 (Windows/no-SSH) created, DECISIONS LOCKED:
  1. Rename licensed-win-1/2 -> ace-win-1/2 in registry; old names -> hostname_aliases (resolution).
  2. Dispatch = PULL/POLL agent (not Tailscale-SSH); long-term control surface = Telegram via
     deckhand (no-SSH host pulls/claims lease-arbitrated work through the deckhand venue — WF3<->WF4).
  3. Scope INCLUDES macbook-portable (darwin) + gali-linux-compute-1 (linux, ssh:null) as
     robustness cases.

## RECOMMENDED ORDER
A. WF0 registry rename (licensed-win-1/2 -> ace-win-1/2 + alias map + reference sweep) — prerequisite.
B. WF1 #2999 — role-overlay reconciler on Windows (python not uv, %USERPROFILE%\.claude,
   windows _base since crontab/systemctl deny rules are Linux-only). Lowest-risk; mirrors a1/a2.
C. WF3 #3000 — pull/poll dispatch for no-SSH hosts, reusing the transport-agnostic lease cores
   (scripts/operations/dispatch_lease.py + git_ref_lease.py); trigger via deckhand venue.

## HARD CONSTRAINTS / GOTCHAS (learned this project — honor them)
- Hard gates: Issue -> Plan (docs/plans/_template-issue-plan.md) -> adversarial review (Codex, both
  plan+code stages) -> USER APPROVES (status:plan-approved; NEVER self-approve) -> implement (TDD).
- /mnt/local-analysis is FUSE/ntfs-3g-slow: `git status` times out, worktree checkout infeasible.
  LAND CHANGES VIA THE GITHUB API (gh api git/blobs|trees|commits|refs) on a branch, then `gh pr create`.
- The a1 control-plane tree is shared/dirty + on another session's branch — never checkout/branch it.
- The F1 deny-list is now enforced against the agent on a1/a2: `Bash(crontab:*)`, `Bash(python3 -c:*)`,
  etc. are denied. Cutover tools write crontab via Python subprocess INTERNALLY (allowed); verify via
  cron-audit.py, not literal `crontab -l`. On Windows there's no SSH from Linux — run on-host.
- Cleanup discipline: restore ONLY files you edited, by exact name; never blanket `git checkout`/`rm -rf`
  (reverts background-automation files / deletes tracked tests). Verify `git status --porcelain -- <paths>`.
- Codex delegation: `codex exec --skip-git-repo-check -s read-only "$(cat prompt)" < /dev/null` disowned;
  use for independent review, NOT heavy authoring (CPU-starved here).
- Parallel subagents: give each a DISTINCT new file; pre-stage shared read-only deps once; reconcile
  anything touching canonical files yourself; verify their test claims by running tests yourself.
- Windows lease: keep refs/heads/* (GitHub push compat) stored as a commit (JSON-in-message over empty
  tree); update-ref old-value = atomic CAS; parent each lease commit so CAS always advances. Reconciler
  + lease cores are pure-Python so they port; only scheduler (Task Scheduler vs cron) + dispatch-reach differ.

## OPEN ITEMS NOT IN THIS EPIC (don't lose)
- deckhand#179: venue send-path in the deckhand repo (live client SLA; gated; VENUE_LEASE_ENABLED flag).
- roles_authoritative: 8 dual-read cron conflicts on a1/a2 (legacy machines: pins beat role-match) —
  user policy decision whether roles should win.

Start with A (WF0 registry rename) unless the user redirects. Plan it, get approval, land via API.
```
