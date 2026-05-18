# Exit Handoff — Telegram/Hermes multi-machine connectivity review

- **Timestamp:** 2026-05-18T17:51:21Z / 2026-05-18T12:51:21-05:00
- **Host:** ace-linux-1
- **Repo:** `/mnt/local-analysis/workspace-hub`
- **Branch:** `main`
- **Purpose:** durable closeout after reviewing whether all available machines can be connected through Telegram + Hermes Agent, and what work remains to enable safe connection.

## Current answer

No: the available machines are **not yet fully dispatch-connectable** through Telegram + Hermes Agent.

Current supported posture is staged:

1. `ace-linux-1` / `dev-primary`: intended coordinator, but not currently dispatchable until local Telegram env/allowlist and clean-state gates pass.
2. `ace-linux-2` / `dev-secondary`: intended first Linux worker, but not dispatchable until host-local readiness evidence is generated and shared with the coordinator.
3. `licensed-win-1`, `licensed-win-2`, `macbook-portable`: status-only/manual surfaces; do not dispatch unattended work until Windows/macOS parity is separately planned and approved.
4. `gali-linux-compute-1`: not onboarded; missing workspace root / repo / Hermes setup.

## Live readiness evidence captured

Command run from `/mnt/local-analysis/workspace-hub`:

```bash
scripts/readiness/telegram-hermes-readiness.sh
```

Result summary:

| Host ID | Hostname | Telegram/Hermes posture | Status | Dispatchable | Blocking work |
|---|---|---|---|---:|---|
| `dev-primary` | `ace-linux-1` | coordinator | fail | no | configure `TELEGRAM_ALLOWED_USERS`; configure `TELEGRAM_BOT_TOKEN`; clean/sync workspace before dispatch |
| `dev-secondary` | `ace-linux-2` | worker | fail | no | generate host-local readiness evidence; provide evidence to coordinator via `--evidence-dir` |
| `licensed-win-1` | `licensed-win-1` | desktop-status-only | status-only | no | keep manual/status-only until Windows dispatch parity plan is approved |
| `licensed-win-2` | `licensed-win-2` | desktop-status-only | status-only | no | keep manual/status-only until Windows dispatch parity plan is approved |
| `macbook-portable` | `Vamsees-MacBook-Air` | desktop/status-only | status-only | no | keep manual/status-only until macOS dispatch parity plan is approved |
| `gali-linux-compute-1` | `shoerack` | disabled | not-onboarded | no | configure workspace root, repo sync, Hermes install, reachability, and local readiness |

Important nuance: `dev-primary` was dirty during the readiness probe because this exit/skill-closeout had local documentation/skill edits in progress. After closeout, rerun readiness from a clean checkout; the remaining expected coordinator blockers should be the missing local Telegram token/allowlist env values unless local secrets already exist outside this shell.

## Durable artifacts / issues

Primary runbook and contract:

- `docs/ops/telegram-hermes-multimachine-control-plane.md`

Related GitHub issues:

- Parent: [#2737](https://github.com/vamseeachanta/workspace-hub/issues/2737) — `feat(hermes): enable Telegram/Hermes control-surface dispatch across approved machines`; currently open / `status:needs-plan`.
- Approved coordinator implementation: [#2738](https://github.com/vamseeachanta/workspace-hub/issues/2738) — `feat(hermes): harden ace-linux-1 Telegram gateway as dispatch coordinator`; currently open / `status:plan-approved`.
- Approved Linux worker implementation: [#2739](https://github.com/vamseeachanta/workspace-hub/issues/2739) — `feat(hermes): promote ace-linux-2 as first Telegram/Hermes dispatch worker`; currently open / `status:plan-approved`.
- Readiness gates: [#2740](https://github.com/vamseeachanta/workspace-hub/issues/2740) — `feat(hermes): formalize multi-host dispatch readiness evidence and registry gates`; currently closed after readiness-gate work landed.
- Smoke/canary follow-up: [#2741](https://github.com/vamseeachanta/workspace-hub/issues/2741) — `test(hermes): validate Telegram dispatch smoke tests and destructive-action canary`; currently open / `status:needs-plan`.
- Cross-platform parity: [#2742](https://github.com/vamseeachanta/workspace-hub/issues/2742) — `plan(hermes): Windows and macOS Telegram/Hermes dispatch parity path`; currently open / `status:needs-plan`.

## Work required to enable connection

Minimum safe enablement path:

1. **Harden `ace-linux-1` coordinator** under #2738:
   - Put `TELEGRAM_BOT_TOKEN` and `TELEGRAM_ALLOWED_USERS` only in the local Hermes secret/env store.
   - Ensure `GATEWAY_ALLOW_ALL_USERS` is false/unset.
   - Install/verify gateway/systemd environment loading and restart/drain behavior.
   - Keep workspace-hub clean/synced before dispatch attempts.
2. **Promote `ace-linux-2` as first worker** under #2739:
   - Sync workspace-hub to a revision containing the readiness script/runbook.
   - Verify Hermes CLI/gateway install and safe approval posture on ace-linux-2.
   - Configure local env-name contract without committing secrets.
   - Generate host-local readiness evidence and expose it to the coordinator readiness check.
3. **Validate command safety** under #2741:
   - `/status` smoke test.
   - `/dispatch` fail-closed tests for missing approval, dirty worktree, missing local marker, and unsupported host.
   - Destructive-action canary proving Telegram cannot bypass approval gates.
4. **Plan Windows/macOS parity** under #2742:
   - Keep Windows/macOS status-only until parity plan proves local Hermes/gateway setup, execution safety, rollback, and secrets posture.
5. **Onboard `gali-linux-compute-1` only if still desired**:
   - Add workspace root, repo sync, Hermes install, network reachability, and host-local evidence.

## Repo-state proof before this handoff commit

```text
git status --porcelain=v1 --branch
## main...origin/main
 M .claude/skills/github/github-issues/SKILL.md
 M .claude/skills/workspace-hub-learned/git-operation-serialization-preflight/SKILL.md
?? .claude/skills/workspace-hub-learned/git-operation-serialization-preflight/references/post-commit-hook-metadata.md
```

```text
git rev-parse HEAD
12c61ebd4af88152a2f47c9c0794a7c02d70466e

git rev-parse origin/main
12c61ebd4af88152a2f47c9c0794a7c02d70466e

git rev-list --left-right --count HEAD...origin/main
0	0

git ls-remote origin refs/heads/main
12c61ebd4af88152a2f47c9c0794a7c02d70466e	refs/heads/main
```

Dirty-state classification before this handoff commit:

- `.claude/skills/github/github-issues/SKILL.md`: durable skill hardening to require remote/local closeout proof for issue work that commits artifacts.
- `.claude/skills/workspace-hub-learned/git-operation-serialization-preflight/SKILL.md`: durable learned skill hardening for post-commit hook/tooling metadata dirt.
- `.claude/skills/workspace-hub-learned/git-operation-serialization-preflight/references/post-commit-hook-metadata.md`: supporting reference for the learned skill.

## Worktree disposition

`git worktree list --porcelain` reported:

- `/mnt/local-analysis/workspace-hub`: main checkout, active closeout target.
- `/tmp/wh-h4`: branch `dispatch/h4-2152`, `HEAD a18c5ef868716f3657aa64d721f9636942a11c36`; preserved, not removed.

## External-action status

No external send/action was performed during this closeout. No Telegram/Hermes remote-machine command was triggered. The readiness script inspected registry/config/local state only.

## Restart checklist

1. Fetch current state: `git fetch origin main && git status --porcelain=v1 --branch`.
2. Rerun readiness from clean checkout: `scripts/readiness/telegram-hermes-readiness.sh`.
3. If enabling the MVP, execute #2738 first, then #2739, then #2741 smoke/canary validation.
4. Do not dispatch unattended work to Windows/macOS until #2742 is planned, reviewed, approved, implemented, and validated.

## Final proof placeholder

This handoff must be committed and pushed, then final live proof should be reported in the chat response after re-fetching origin.
