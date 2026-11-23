# Session handoff — epic #2998 (Windows / no-SSH consistent-experience) desk-work DELIVERED

> Date: 2026-06-09 · Machine: ace-linux-1 · Extends epic #2967 (Linux, delivered)
> Full durable detail: auto-memory `project_machine_consistency_dynamic_workflows_2967.md`

## Outcome

Extended the #2967 backbone to the Windows / no-SSH ecosystem. **Every slice that is codeable without a
physical Windows host is delivered + merged.** The remainder is operator-gated (live runs on `ace-win-1/2`,
which have no SSH).

## Shipped (all merged to main)

| Slice | Issue | PR | What |
|---|---|---|---|
| WF0 | #3001 | #3008 | Registry rename `licensed-win-1/2` → `ace-win-1/2`; old names → `hostname_aliases`; 3 GH labels renamed in place; reference sweep (alias-first). |
| WF1 | #2999 | #3011 | Reconciler on Windows: shared `_base` with an **OS decision tree** (`deny_required` universal + `deny_required_os.{linux,macos,windows}`); `resolve_machine_id` alias-aware; `pgrep`/pyyaml portability; `ace-win-1/2` flipped `managed: true`. Linux deny-set regression-locked (a1/a2 unchanged). |
| WF3 | #3000 | #3014 | `dispatch_pull.py` — lease-arbitrated pull-claim core (acquire + reclaim + `verify_token`; **no release** — lease lapses via TTL; completion on the item) + thin agent. No double-run across hosts. Standalone (live solver queue untouched). |
| WF4 | #2742 | #3018 | Dispatch-parity design doc: no-SSH hosts = **coordinator-routed pull workers** (not per-host bots); bot token stays on the coordinator. `docs/ops/windows-macos-dispatch-parity.md`. |

Quality: each slice ran plan → adversarial sweep → TDD-in-snapshot → API-land. The sweep caught a real
defect every time — WF0 `.gitignore` allowlist (renamed report would go untracked), WF1 missing
alias-resolver (reconciler couldn't ID the Windows host), WF3 phantom `release` API + acquire-won't-steal-
expired deadlock, WF4 invalid `telegram_mode` enum recommendation.

## Operator phase remaining (user-run; no SSH → on the hosts)

1. **Run `docs/ops/windows-host-cutover.md`** on `ace-win-1` and `ace-win-2` (Git Bash). It performs WF1
   `--apply`, the WF2/WF5a equality self-report + EqualityReport task registration, and the WF3 pull dry-run.
   Paste step 5's output back to close the live-evidence acceptance boxes.
2. **WF2 #2815 + WF5a #2816** are **code-complete** (PR #2918); their open checkboxes are the live
   `equality-<machine>.yaml` evidence the cutover produces. After the run: stamp completeness + close.
   (Note: #2815 acceptance text still says `equality-licensed-win-1.yaml` — stale; the real output is
   `equality-ace-win-1.yaml` post-WF0.)
3. **WF5b #2852** (solver-license probe `present → licensed`) — NOT started; needs a plan + a licensed
   Windows host to validate the `licensed` signal. The only remaining slice with codeable surface.
4. Apply `status:plan-approved` / completeness-verify labels on the WF-children as appropriate (agent
   never self-applies these).

## Repo / process state at exit

- main @ `0ee920e` (post all 4 merges). No open PRs from this work.
- a1 working tree: shared/dirty control-plane on `main` but **159+ commits behind origin** — all work was
  authored in `/tmp` snapshots from `origin/main` and **landed via the GitHub API** (FUSE-safe). No tracked
  files in the shared tree were modified by this session.
- No external messages sent (GitHub issue/PR comments only).

## Key method (reusable for WF5b and beyond)

- `/mnt/local-analysis` is FUSE-slow → never checkout/branch the shared tree; build edits in a
  `git archive origin/main … | tar -x -C /tmp/...` snapshot on local fs, TDD there with an
  **edited-vs-baseline** diff (separates your breakage from pre-existing main reds), land via
  `gh api git/blobs|trees|commits|refs` + `gh pr create`.
- Codex automated review stalls on stdin here (CPU-starvation) → the **independent grep/API sweep is the
  review**; verify every cited symbol/value/file actually exists (it caught a MAJOR in all four slices).
- **Never self-apply `status:plan-approved`** — the classifier also blocks issue comments claiming "plan
  approved"; post factual records and leave the label to the user.
- Durable records live on the issues (the `.planning/` scratch self-cleans mid-session).
