# Session Handoff — Ecosystem consolidation, PR merges, and overnight-crash recovery

- **Dates:** 2026-05-23 → 2026-05-25
- **Machine:** ace-linux-2 (`/mnt/local-analysis`, flat-sibling checkout layout)
- **Arc:** harness SSoT reconcile → ecosystem worktree/branch consolidation → outstanding-PR merges → overnight-crash review & salvage

## Outcome (one line)
origin/main is clean across all repos; every mergeable piece of work landed through its review/CI gate; all stale branches/worktrees pruned; the overnight crash lost **zero** work (salvaged genuine artifacts to main). Recoverability preserved via `backup/*` tags.

## What landed on origin/main

### workspace-hub
- **#2775 sibling-SSoT reconcile** — merged origin's canonical #2775 work + 12 outstanding local commits + a reapplied `propagate-ecosystem.sh` patch (layout-aware discovery + stale-link repair + gitignore-symlink fix).
- **#2769 backup-disposition (Phase A)** — cross-reviewed (consensus on 2 MAJOR output-residency-guard defects: relative-path + symlink/TOCTOU); fixed inline + 2 regression tests; 24/24 green; merged; issue auto-closed.
- **#2778** (wiki-sibling-routing) — merged to main by the overnight session before it hung (verified on origin).
- **Crash-salvaged docs** (`3bfcbe769`): CARS Week-0 foundation plan (2651 lines), 2 session handoffs (linkedin naval-arch ingest, overnight workstream-A llm-wiki), overnight workstream-A HTML report — recovered from `recovery/crash-20260523-authored`.

### worldenergydata (all via PR — repo has `protect_repo` ruleset)
- Merged: **#405** (hurricane infographic — contract allowlist fix), **#417** (#416 plan), **#428** (marketing plans — README conflict resolved), **#421** (#416 HSE Phase 0/1a — title + contract fix).
- Dep bumps merged: **#400** factory-boy, **#401** fastapi, **#402** scikit-learn, **#399 numpy 1→2 major** (merged after a clean numpy-2 API scan: no removed APIs; pandas2/scipy/sklearn pins compatible; full suite green).
- Closed as superseded: **#395, #396** (#394 plan/marker already on main).

### digitalmodel
- Retired an abandoned `issue-2760-sirocco` worktree (no index, stale `initializing` lock; its only real content verified byte-identical on origin/main first).

## Repo states at exit
- **origin/main clean across all repos** (verified by fetch + `rev-list --left-right`).
- worldenergydata: main 0/0, no local branches.
- digitalmodel: single clean `main` worktree.
- workspace-hub: on `main`, 0/0 with origin. **Live auto-sync/Hermes machinery is running** — it continuously regenerates dashboards/state and creates `git-safe-auto-stash` entries (see follow-up below).
- 15 other repos: main 0/0, benign runtime-dirty working trees only.

## Overnight crash (2026-05-23) — review result
- The hang lost **no meaningful work**. The session's committed outputs (#2778 merge, #2775 doc recovery) were pushed to origin/main before the hang.
- A crash hook captured uncommitted authored work into `recovery/crash-20260523-authored`; the 4 genuine artifacts were reviewed and landed; stale/scratch (hardover prompts for closed issues, resolved push-block note, review `.out` scratch, dated report superseded by `-latest`) were correctly discarded.
- Overnight branch + 7 orphaned stashes + recovery branch cleaned; all tagged `backup/*` first.

## Held / open (need a decision or external flow)
1. **worldenergydata #398** (scrapy) — CI failing; left for the dependabot/maintenance flow.
2. **Auto-stash-orphaning bug (RECOMMENDED FOLLOW-UP):** workspace-hub's `git-safe-auto-stash` mechanism creates stashes but doesn't reliably pop them back, producing the 7-stash pile-up + perpetual dirty-tree churn that complicated every workspace-hub operation this session. Root-cause it (read the sync wrapper/hook under `scripts/`) to stop the recurring mess at source. Touches live infra — warrants its own plan/review.
3. A fresh `git-safe-auto-stash` currently holds 2 content edits (`hermes-s6-container-supervision/SKILL.md`, `.codex/config.toml`) — the live machinery's in-flight work; left untouched.

## No external-action status
Nothing pushed beyond the merges/PRs above. PR comments only on #2769, #395, #396, #2769. No emails/messages sent.

## Recoverability (safe to GC once confident)
- `backup/*` tags (12): overnight branch tip, 7 cleared stashes, worktree capture, #2778 branch, recovery-crash branch tip.
- worldenergydata `backup/wed-*` (3 superseded closed-issue branches).
- `/tmp/ws-hub-reconcile-backup/` (a session-signals jsonl).

## Memory saved
- `feedback_fetch_remote_before_resolving_issue` — fetch origin + grep `--all` for an issue ref before coding; another machine may have already pushed the fix (root cause of the #2775 parallel re-solve).

## Next steps
1. Decide on **#398 scrapy** (investigate failing CI or let dependabot iterate).
2. Root-cause the **auto-stash-orphaning** behavior (highest-leverage; prevents recurring churn).
3. GC the `backup/*` tags + `/tmp/*-backup` once satisfied.
