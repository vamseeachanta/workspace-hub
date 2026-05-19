# workspace-hub setup documentation

Per-machine bootstrap and ongoing audit for the workspace-hub fleet.
Issue: [#2751](https://github.com/vamseeachanta/workspace-hub/issues/2751) (build) · [#2753](https://github.com/vamseeachanta/workspace-hub/issues/2753) (operational tracker).

## Quick start

Fresh machine, single command after `git clone`:

```bash
bash scripts/setup/new-machine-setup.sh
```

This runs the 14-step bootstrap. On Windows native PowerShell, use `pwsh scripts/setup/new-machine-setup.ps1` instead (Phase 5 of #2751, lands after this doc).

## Index of guides

| Document | When to read it |
|---|---|
| [FRESH_MACHINE_SETUP.md](FRESH_MACHINE_SETUP.md) | First time on a new machine. Walks through clone → bootstrap → auth → verify. Contains the canonical **4×22 harness-parity coverage table** showing what gets installed at each stage. |
| [EXISTING_MACHINE_AUDIT.md](EXISTING_MACHINE_AUDIT.md) | You suspect a machine has drifted from canonical state. Walks through the audit flow + targeted repair commands. |
| [PROVIDER_AUTH_GUIDE.md](PROVIDER_AUTH_GUIDE.md) | Per-provider authentication for Claude, Codex, GitHub, Gemini, Hermes. Token rotation. What's auto-handled vs manual. |
| [MACHINE_REGISTRY.md](MACHINE_REGISTRY.md) | How the control-plane (`ace-linux-1`) reads per-machine status from `config/machine-baselines/` and aggregates the fleet drift report. |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Known issues: NTFS dirty volumes, sparse-checkout overlays, Codex stdin hang, parallel-session git conflicts, sudo prompts during auto-install. |

## How the pieces fit

```
┌─────────────────────────────────────────────────────────────────────┐
│  scripts/setup/new-machine-setup.sh  (14 steps, idempotent)         │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ Steps 1-8b: existing infra (submodules, hooks, CLI configs,   │  │
│  │             shell, npm, codex pin, cron, SSH, env, tmux)      │  │
│  │ Step 9   : AI-provider harness   ── bootstrap-machine.sh      │  │
│  │ Step 10  : Auto-install CLIs      ── lib/install-provider-clis│  │
│  │ Step 11  : Auth orchestration     ── lib/orchestrate-auth     │  │
│  │ Step 12  : Hermes config render   ── lib/instantiate-hermes-* │  │
│  │ Step 13  : Emit machine-status    ── lib/emit-machine-status  │  │
│  │ Step 14  : Verify all checks pass ── scripts/setup/verify-*   │  │
│  └───────────────────────────────────────────────────────────────┘  │
│         ↓                                                            │
│  config/machine-baselines/<token>.{md,yaml}  (per-machine, tracked) │
│         ↓                                                            │
│  scripts/setup/aggregate-machine-status.sh  (control-plane reads)   │
│         ↓                                                            │
│  docs/reports/fleet-harness-status.md  (22-dim × N-machine matrix)  │
└─────────────────────────────────────────────────────────────────────┘
```

## Operational tracker

After running setup on a new machine, post the contents of `config/machine-baselines/<token>.md` as a comment on **operational tracker [#2753](https://github.com/vamseeachanta/workspace-hub/issues/2753)**. That issue is evergreen — one comment per machine, time-ordered. It's the audit log of every bootstrap event across the fleet.

## Cross-references

- **Plan**: [`docs/plans/2026-05-19-issue-2751-cross-platform-harness-setup.md`](../plans/2026-05-19-issue-2751-cross-platform-harness-setup.md)
- **Build issue**: [#2751](https://github.com/vamseeachanta/workspace-hub/issues/2751) — `status:plan-approved` 2026-05-19, implementation in progress (this doc set)
- **Operational tracker**: [#2753](https://github.com/vamseeachanta/workspace-hub/issues/2753) — evergreen
- **Review artifacts**:
  - [`scripts/review/results/2026-05-19-plan-2751-claude.md`](../../scripts/review/results/2026-05-19-plan-2751-claude.md) (r1 MAJOR, all 12 findings absorbed)
  - [`scripts/review/results/2026-05-19-plan-2751-codex.md`](../../scripts/review/results/2026-05-19-plan-2751-codex.md) (r2 MAJOR, all 8 findings absorbed)
