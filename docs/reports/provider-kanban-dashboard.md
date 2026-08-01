# Provider-credit Kanban dashboard

Generated: 2026-07-31T09:21:31Z
Mode: static (read-only)

## How to approve

Static dashboard mode renders disabled approval controls. To actually approve a plan,
run the local approval server:

```sh
uv run --no-project python scripts/ai/provider-kanban-server.py --port 7665
# then open http://127.0.0.1:7665 and click Approve
```

Or invoke the CLI directly with explicit user identity (TTY required without a token):

```sh
uv run --no-project python scripts/ai/approve-provider-plan.py \
  --issue <N> --mode dry-run    # validate planned transaction
uv run --no-project python scripts/ai/approve-provider-plan.py \
  --issue <N> --mode real \
  --user-identity <email> --approval-source 'cli' --confirmation-token <tty>
```

## Lane: plan_review (0)

- (empty)

## Lane: execution_ready (0)

- (empty)

## Lane: running_leased (0)

- (empty)

## Lane: qa_closeout (0)

- (empty)

## Lane: planning_feedstock (200)

| # | Title | Provider | Machine | Approval ready | Blockers |
|---|---|---|---|---|---|
| #3728 | CI: stale command-identity inventory red-lights every PR, including docs-only ones | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3724 | bug(equality): 4 of 5 matrix rows are stale and render identically to fresh ones | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3723 | ops(fleet): derive fleet-ssh-hosts.yml reachability from the generated matrix, not a hand-maintained list | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3721 | ops(ace-win-2): install OpenSSH Server — host is up and answering, only the service is missing | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3717 | Context budget: harness config is 3.6% of the window — the cost is tool output (17%), not CLAUDE.md | agy | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3714 | CI: strict-scan / authority fails on every branch — missing AUTH_ENVELOPE secret | codex | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3712 | infra: no CI check is merge-blocking on main — every 'required gate' enforceability argument is currently false | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; reviews not clean: missing_review; static dashboard: real approval requires provider-kanban-server.py |
| #3711 | bug(cron): build-cron-identity-inventory.py is host-dependent and silently emits a wrong inventory off Linux | claude | — (blocked:no_provider_capable_workstation) | ✗ | reviews not clean: missing_review; static dashboard: real approval requires provider-kanban-server.py |
| #3709 | bug(cron): plan_cutover silently drops managed-block lines instead of blocking on them — audit and apply path disagree | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; reviews not clean: missing_review; static dashboard: real approval requires provider-kanban-server.py |
| #3708 | bug(cron): no safe crontab re-apply path — audit fail-closed on 47 uncataloged lines and setup-cron --replace disabled | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; reviews not clean: missing_review; static dashboard: real approval requires provider-kanban-server.py |
| #3707 | bug(cron): daily-cleanup has never disposed of anything — 4 independent defects, and its only scheduler died 2026-06-16 | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; reviews not clean: missing_review; static dashboard: real approval requires provider-kanban-server.py |
| #3706 | infra: Git LFS budget exhausted account-wide, blocking binary-heavy repos from version-controlling assets | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3705 | bug(sync): repository_sync auto-commits to protected main branches, stranding commits that can never be pushed | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3704 | bug(equality): reconcile-ecosystem.sh scans stale refs without fetching, so "0 actions" is not evidence of health | codex | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3703 | bug(equality): reconcile-ecosystem.sh fails open to an empty equality plan when uv is off the non-interactive PATH | codex | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3702 | bug(equality): equality-matrix-cron writes generated artifacts into the tracked tree, creating a self-sustaining STALE-CHECKOUT deadlock | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; already has status:plan-approved; reviews not clean: missing_review |
| #3698 | PR gate is baseline-red: two enforcement checks fail on every PR, plus an undeclared test dep | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3696 | chore(machines): 6 unpushed commits stranded in secondary working copies on ace-linux-2 (incl. one clone with no remote) | codex | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3695 | chore(llm-wiki): resolve two empty client-wiki stubs — llm-wiki-seanation and llm-wiki-hd | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3694 | chore(repo): reconcile llm-wiki-mkt-a → llm-wiki-acma rename across 62 files (2 scripts + 2 configs are live) | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3693 | Compliance alert: W31 — 0% (critical) | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3671 | INITIATIVE: Repo structure, test health & governance | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3670 | INITIATIVE: Fleet operations — machine readiness, cross-platform parity & security | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3669 | INITIATIVE: AI platform — provider parity, routing, memory & gateway | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3668 | [Epic] Promote packages up the maturity ladder to PRODUCTION | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3667 | [Epic] One implementation per capability: consolidate duplicates behind explicit seams | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3666 | [Epic] Architecture and readiness reporting runs itself | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3665 | [Epic] Shared dev toolchain works in every checkout: worktrees, portable paths, one packaging standard | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3664 | [Epic] Regression coverage for ecosystem-sync and harness mutation helpers | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3663 | [Epic] Test-health telemetry: trends, baselines and enforced budgets | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3662 | [Epic] Every repo clean, synced, and free of stray branches | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3661 | [Epic] Smoke coverage for licensed and platform-specific engineering tooling | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3660 | [Epic] Delete dead weight: stale code, orphan modules, and multi-GB git history | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3659 | [Epic] Coverage uplift for untested engineering and calculation code | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3658 | [Epic] Return red test suites to green (digitalmodel, worldenergydata, skills) | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3657 | [Epic] Wind down secondary repos: extract the value, then archive | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3656 | [Epic] Pre-push and merge gates: deterministic, passable, bypass-proof | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3655 | [Epic] The operator can see and steer the harness without opening a terminal | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3654 | [Epic] Get commit-review compliance out of critical and stop the weekly alert stream | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3653 | [Epic] The weekly review reports something a human can act on | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3652 | [Epic] Harness automation never destroys live work or unverified evidence | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3651 | [Epic] Identical harness behaviour on every machine and every provider lane | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3650 | [Epic] A session's state and learnings survive the session and the machine | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3649 | [Epic] One trustworthy answer to "is this plan approved?" across labels, markers and plan docs | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3648 | [Epic] Cross-review enforcement: reliable, blocking, provider-agnostic | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3647 | [Epic] Every scheduled task installs, runs, and surfaces its own failures | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3646 | [Epic] Every tier-1 repo has the same anatomy and a current mission statement | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3645 | [Epic] One-command harness bootstrap + unattended update lifecycle on every machine | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3644 | [Epic] Clear node bring-up debt — ace-linux-2 and gpu-claw to the known-good fleet baseline | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3643 | [Epic] Machine readiness matrix — evidence bundles on every platform + weekly licensed-tool review | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3642 | [Epic] Weekly review publication pipeline: validated, reproducible artifacts | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3641 | [Epic] Harness tooling is hardened against hostile and malformed input | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3640 | [Epic] Secret and legal scanning fails closed with positive controls | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3639 | [Epic] Every workstation is reachable only over hardened, registry-driven Tailscale SSH | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3638 | [Epic] Make ecosystem intelligence findable and provably fresh (entry points, accessibility registry, staleness) | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3637 | [Epic] Public repositories are hardened and contributor interactions have a standing playbook | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3636 | [Epic] Enforce knowledge promotion: ledger, audit trail, and boundary guardrails for L3 wiki content | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3635 | [Epic] Every open issue routes to exactly one domain, board and machine | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3634 | [Epic] Promote the named O&G standards backlog into the wiki on a corrected, citable catalog | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3633 | [Epic] Plan-approval evidence is fail-closed and machine-verifiable | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3632 | [Epic] llm-wiki ingest pipeline: complete source coverage, idempotent runs, tested retrieval | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3631 | [Epic] Every harness script and scheduled task runs identically on Windows, macOS and Linux | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3630 | [Epic] Adopting a new model or harness update is a verified, reversible operation | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3629 | [Epic] Weekly ecosystem review publishes reproducible, promotable artifacts | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3628 | [Epic] Security hardening for AI agent workflows and credential exposure | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3627 | [Epic] One consistent agent harness configuration on every machine | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3626 | [Epic] Hermes gateway & the self-hosted / free provider tier | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3625 | [Epic] Skill & prompt corpus — measure real usage, remove model-degrading scaffolding | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3624 | [Epic] Close the email-as-queue loop — extract, act, delete, reactivate on reply | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3623 | [Epic] Cross-provider review fanout produces trustworthy, complete evidence | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3622 | [Epic] Every issue leaves a standard durable trail — plan, retention, closure promotion, published artifact | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3621 | [Epic] Durable agent memory — canonical, fresh and lossless across every provider | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3620 | [Epic] Make workflow compliance consequential — a gate behind the metric, not a weekly alert nobody acts on | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3619 | [Epic] Trustworthy autonomous dispatch — approval, plan-review and handoff contracts an owner can act on without re-deriving | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3618 | [Epic] Model routing & AI credit governance — right model for the work, no surprise exhaustion | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3617 | [Epic] Retire the WRK work-queue — one work-tracking system, migration debris cleared | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3616 | [Epic] Provider parity — Claude, Codex and agy are interchangeable first-class workers | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3615 | [Epic] Make workspace-hub's own operational skills and pre-push guards trustworthy | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3614 | [Epic] Close eight named domain-skill coverage gaps | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3613 | [Epic] Finish the agent/command to SKILL.md migration and stop the gap reopening (#1721) | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3612 | [Epic] One canonical copy per skill, non-zero domain coverage in every tier-1 repo | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3611 | [Epic] Make the SKILL.md authoring contract machine-checkable and bring the corpus into conformance | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3609 | INITIATIVE: Personal & family operations | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3608 | INITIATIVE: CAD/CAM & manufacturing capability | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3607 | INITIATIVE: Brand, public surfaces & go-to-market | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3606 | INITIATIVE: Harness runtime, workflow & skills | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3605 | INITIATIVE: ACMA & client delivery | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3604 | INITIATIVE: Knowledge ingestion & the llm-wiki corpus | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3603 | INITIATIVE: Deckhand & Open Deck platform | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3602 | INITIATIVE: World Energy Field Explorer & asset data spine | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3601 | INITIATIVE: Engineering compute & solver trust | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3600 | fix(harness): R-MODEL-DRIFT validates only openai_primary — no claude_* key is checked by any nightly gate | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3598 | feat(equality): add HF-token health row to the machine equivalence matrix | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3596 | Compliance alert: W30 — 18% (critical) | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3595 | ace-win-2 on-box: schema-5 equality re-collect verification + hermes home init + revive licensed-runs queue heartbeat (#3592 follow-up) | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3594 | chore(registry): gpu-claw entry stale after 2026-07-22 relocation+onboarding — notes say clone pending / uv NOT installed; both now false | codex | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3592 | equality matrix: reclassify harness/scheduler/memory rows — uniform vote mis-grades per-role differences + Windows placeholder data poisons majority | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; already has status:plan-approved; reviews not clean: major_review,missing_review |
| #3589 | EPIC: family phone-media extraction & archive ecosystem | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3588 | phone-media: evaluate self-hosted family photo browser (Immich / PhotoPrism) | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3587 | phone-media: choose the ongoing incremental sync lane | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3586 | phone-media: off-site backup capacity plan + periodic rclone check cron | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3585 | phone-media: EXIF-date organizer + cross-phone dedupe | codex | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3584 | phone-media: USB-pull remaining family phones into the archive | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3582 | equality-matrix-cron.sh on Windows collects via bash and publishes degraded compute/provider evidence | claude | — (blocked:no_provider_capable_workstation) | ✗ | reviews not clean: missing_review; static dashboard: real approval requires provider-kanban-server.py |
| #3580 | chore(harness): gemini CLI uninstall decision after agy soak (#3573) | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3579 | chore(readiness): rename equality/parity provider row gemini→agy (cross-machine snapshot schema migration) | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3578 | fix(review): submit-to-codex.sh hangs — codex exec exit 124 'Reading additional input from stdin' despite #3294 mitigation | claude | — (blocked:no_provider_capable_workstation) | ✗ | reviews not clean: missing_review; static dashboard: real approval requires provider-kanban-server.py |
| #3577 | fix(harness): repo-wide exec-bit audit — NTFS-FUSE working copy commits scripts as 100644 | codex | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3573 | feat(ai-orchestration): replace gemini with agy as the third worker/reviewer provider ecosystem-wide | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; already has status:plan-approved; no canonical plan file |
| #3572 | Harden agent workflows for idempotent external mutations and receipt-bound review degradation | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3571 | equality/reconcile tooling gaps on ace-win-1: junction-following restore wiped canonical skills; Windows host-identity + flock gaps | codex | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; already has status:plan-approved; reviews not clean: missing_review |
| #3568 | epic(agent-ux): cross-machine input interaction parity | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; already has status:plan-approved; no canonical plan file |
| #3567 | feat(machine-equivalence): add interaction-UX evidence and pet-peeve predicates | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3566 | fix(agent-ux): make keyboard and context-menu text paste equivalent in Codex CLI | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; already has status:plan-approved; reviews not clean: missing_review,unavailable_review |
| #3565 | feat(agent-ux): align Linux Codex dictation hotkey with Windows Win+H | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3564 | bug(ci): legal rule authority receives empty AUTH_ENVELOPE on PRs | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3562 | Audit MSYS conversion of slash-prefixed native-command tokens | codex | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3561 | Repair and split workspace connection menu dispatch | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3560 | fix(review): isolate in-progress provider sinks and fail closed on empty final artifacts | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3559 | feat(field-explorer): immutable Hugging Face field/well HTML drill-down program [C11] | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3558 | fix(memory): prevent shared KNOWLEDGE rules from being omitted by provider slice cap | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3557 | bug(equality): reconcile marks dirty STALE-CHECKOUT auto-safe but apply cannot clean or make progress | codex | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3555 | feat(agent-ux): pilot persistent goals and native Codex statusline across machines | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3554 | bug(equality): Windows publish-equality misclassifies missing flock as contention and reports success | codex | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; already has status:plan-approved; reviews not clean: major_review,missing_review,unavailable_review |
| #3552 | security: make Gitleaks configuration fail closed with default rules and positive control | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3551 | ops(dev-primary): roll out and verify Tailscale plus hardened OpenSSH | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3550 | ops(dev-secondary): roll out and verify Tailscale plus hardened OpenSSH | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3549 | feat(ops): registry-driven Linux connection helpers with TDD | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; already has status:plan-approved; reviews not clean: missing_review |
| #3547 | feat(ops): secure remote Linux access architecture and staged rollout | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3545 | Plan bounded same-account Claude Remote Control pilot on Windows | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3544 | security(legal): correct and operationalize Phase A authority activation | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; already has status:plan-approved; reviews not clean: missing_review,unavailable_review |
| #3542 | audit(config): reject duplicate YAML keys and ambiguous scalar types | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3541 | test(enforcement): assert exact schemas for equivalent bypass fields | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3539 | Refactor oversized equality modules and make Windows collector tests hermetic | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3538 | Evolve calculation citation contract for amendment and exact-source identity | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3537 | [WRK] Make plan-review fanout artifacts atomic and revision-stamped | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3536 | CLI boundaries: prevent argparse from echoing rejected caller-controlled tokens | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3534 | secure(main): require latest-base checks and block unchecked direct pushes | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3533 | Make standards registries edition, amendment, access, and rights aware | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3532 | fix(memory): reserve cross-provider runtime budget for operational feedback | codex | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; already has status:plan-approved; reviews not clean: major_review,missing_review |
| #3527 | fix(scheduler): reconcile identity inventory after merge-base race | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; already has status:plan-approved; reviews not clean: missing_review,unavailable_review |
| #3526 | feat(windows): daily report-only ecosystem reconciliation audit | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3525 | [WRK] Investigate safe remote Claude job dispatch to ace-win-2 | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; already has status:plan-approved; reviews not clean: major_review,missing_review |
| #3524 | [WRK] bug(workstations): RDP microphone input not negotiated from ace-win-2 to ace-win-1 | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; already has status:plan-approved; reviews not clean: missing_review |
| #3523 | bug(enforcement): plan-approval gate rejects valid markers when sparse checkout omits STATE.md | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3522 | security(legal): migrate sensitive deny-list values out of public repository history | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; already has status:plan-approved; reviews not clean: missing_review |
| #3521 | Legal scanner: support explicit NUL-safe staged-blob pathsets | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3518 | fix(scheduler): keep setup-cron wrapper attestation pin synchronized | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; already has status:plan-approved; no canonical plan file |
| #3516 | bug(equivalence): ref blobs keyed by role — same-role boxes (ace-win-1/2) will clobber each other; role detection hardcoded to 2 hosts (gpu-claw published as unknown.json) | codex | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; already has status:plan-approved; no canonical plan file |
| #3513 | bug(harness): Windows soul installer reports LINK for ordinary file and accumulates backups | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3511 | bug(equivalence): Windows sentinel emits empty unknown fingerprint and corrupts mktree filenames | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; already has status:plan-approved; reviews not clean: missing_review,unavailable_review |
| #3506 | ops(ace-win-2): equivalence fingerprint ABSENT — sentinel not publishing from ace-win-2 (flagged by #3502 monitoring) | codex | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3505 | ops(ace-win-1): equivalence fingerprint ABSENT — sentinel not publishing from ace-win-1 (flagged by #3502 monitoring) | codex | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3500 | bug(pre-push): equivalence-state publish loops full tier-1 suite forever — remote ref never created, every push gated as new-branch RUN_ALL (sub-case of #3198) | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; already has status:plan-approved; no canonical plan file |
| #3499 | Zero-touch repo hygiene on all headless nodes (generalized ff-sync watchdog + fleet health in equality matrix) | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3498 | Machine-ecosystem map: roles, data-source access, services — admin-tier extension of the equality matrix | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3497 | EPIC: Fleet dispatch ecosystem — ace-linux-1 single dispatch surface; all other machines headless | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3495 | test(enforcement): make hash-pinned semantic mutation tests exercise refreshed pins | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3494 | design(capabilities): reconcile existing per-repo GitHub Pages capabilities pages with the HF-backed aceengineer.com surface [C10] | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3491 | chore(solver-queue): reconcile legacy solver-queue issues (#2641/#1586/#2524) with the live deckhand licensed-run lane [dm#1553 H] | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3490 | fix(onboarding): surface cron preview failure during new-machine dry-run | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; already has status:plan-approved; reviews not clean: missing_review,unavailable_review |
| #3485 | epic: Live HF-backed capability surfaces on aceengineer.com — self-perpetuating algorithm showcase | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3482 | design(repo-health): safe worktree lifecycle with leases and recoverable quarantine | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; already has status:plan-approved; no canonical plan file |
| #3480 | Land generic HF-dataset publisher: scripts/hf/save_results_to_hf.py (+ --card-note gate disclosures + tests) | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; already has status:plan-approved; no canonical plan file |
| #3479 | fix(harness-update): propagate or explicitly surface cron reconciliation failure | codex | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3478 | refactor(windows): add semantic ownership and recovery to scheduled-task installers | codex | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3477 | fix(scheduler): make kanban loader timer transactional across systemd-user and cron | codex | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3476 | refactor(cron): migrate three legacy marker installers to transactional reconciliation | codex | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3472 | feat(operations): add pressure-aware daily OS maintenance cleanup | codex | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; already has status:plan-approved; no canonical plan file |
| #3467 | Build an independent retained-input bootstrap for structured cross-provider review evidence | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3464 | Harden descriptor-bound Git and filesystem enforcement primitives | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3462 | Fix Windows plan-review fanout argument overflow and auth diagnostics | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3461 | bug(validation): make staged evidence handshakes resumable and snapshot-closed | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3460 | bug(hooks): post-commit learning hook fails from sparse linked worktrees | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3459 | bug(enforcement): check-no-abs-paths fails before scanning in sparse checkouts | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3458 | bug(cleanup): make archive manifests safe for tabs, newlines, and arbitrary names | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3457 | fix(worktrees): fail closed on an absent sparse-worktree index | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3456 | security(local-analysis): make parent runtime-config permissions enforceable on fuseblk | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3455 | bug(workstations): reconcile ace-win-1 with the live RDS-002 mapping | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3454 | chore(local-analysis): publish sanitized interactive cleanup ledger and prune stale local permission residue | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3453 | bug(cleanup): daily cleanup assumes nested repos and purges unverified staged evidence by age | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3451 | Legal sanity scan: make empty diff-only runs explicit and fail-closed when evidence is required | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3450 | fix(workflow-manifest): distinguish nested-worktree resolution failures from registry drift | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3448 | chore(ecosystem): audit repository detection for linked worktree compatibility | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3447 | Add cross-format CLI behavior parity tests for option-bearing commands | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3446 | Audit bounded JSON parsers for uncaught depth and resource exceptions | claude | — (blocked:no_provider_capable_workstation) | ✗ | reviews not clean: missing_review; static dashboard: real approval requires provider-kanban-server.py |
| #3445 | Require status and readiness checks to validate the same source contract as execution | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3444 | infra: route Python environments off fuseblk worktrees | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3443 | governance(legal): define repo-posture scanner profiles and replace private-repo scan skips | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3442 | Track Codex CLI 0.144 stdin regression in cross-review harness | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3440 | Harden generated HTML against JSON script-tag breakout | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; already has status:plan-approved; no canonical plan file |
| #3439 | Audit descriptor-relative readers for FIFO blocking before fstat | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3438 | Require complete module provenance in installed-wheel smoke tests | claude | — (blocked:no_provider_capable_workstation) | ✗ | reviews not clean: missing_review; static dashboard: real approval requires provider-kanban-server.py |
| #3437 | standard: require SHA-pinned cross-repository plan evidence | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3436 | bug: make new-branch pre-push checks worktree-aware | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3435 | bug: make hook installation worktree-aware | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3434 | feature: algorithm-scoped cross-run insights and decision briefs | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; no canonical plan file; review evidence not clean |
| #3433 | feature: per-repository Hugging Face projection and staged promotion | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; already has status:plan-approved; reviews not clean: missing_review |
| #3432 | standard: algorithm-specific metric definition and observation contract | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; already has status:plan-approved; reviews not clean: missing_review |
| #3431 | standard: curated output and rolling algorithm report contract | claude | — (blocked:no_provider_capable_workstation) | ✗ | missing status:plan-review label; already has status:plan-approved; reviews not clean: missing_review |

## Lane: blocked (0)

- (empty)

