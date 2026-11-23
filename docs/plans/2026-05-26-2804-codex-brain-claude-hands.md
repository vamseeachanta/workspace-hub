# Plan for #2804: Codex-under-Claude execution route (Option 6 — AppArmor userns grant for system bwrap)

> **Status:** v3 (r3-inline of all findings) — awaiting user approval. Reviews: r1 REJECT 3/3 (Option 9), r2/r3 REJECT 3/3 (Option 6 v2). Direction accepted by all providers; this v3 folds in every execution + honesty fix inline (no 4th dispatch, per `feedback_r3_inline_loop_break_pattern` + budget).
> **Complexity:** T3 · **Date:** 2026-05-26 · **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2804 · **Client:** N/A · **Project:** N/A
> **Review artifacts:** scripts/review/results/2026-05-26-plan-2804-{claude,codex,gemini}.md (r1) + ...-r2-{claude,codex,gemini}.md (r2/r3)

## Finding → fix changelog (what changed since v2)

| Finding (round) | Fix in v3 |
|---|---|
| Security blast-radius oversold (r2/r3 BLOCKER) | §Security states the truth: grant covers ALL system-bwrap consumers (VSCode/Firefox/Flatpak), kernel-LPE tradeoff, no codex-only possible. User reviewed + accepted (kept profile over rollback/sysctl). |
| Hardcoded `/home/vamsee/` path (r2 BLOCKER) | Profile targets ONLY `/usr/bin/bwrap`; vendored-bwrap clause dropped (strace proved it's unused) → no abs-path, passes `check-no-abs-paths.sh`. |
| Scope coupling #2804↔#2802 (r1/r2/r3 BLOCKER) | #2804 acceptance = codify + **synthetic disposable-fixture smoke test** only. #2802 is a *referenced* pilot, NOT in #2804's ACs. |
| Installer unguarded privileged mutation (r2/r3 MAJOR) | Installer spec: `--check`/`--dry-run` default; explicit `--accept-userns-lpe-risk` to write; OS/AppArmor detection fail-fast on non-Ubuntu; refuse-overwrite unmanaged content (sentinel header); teardown script; logs `codex --version`. |
| `network_access=true` egress (r2/r3 MAJOR) | Documented threat model; kept (Codex needs gh/git) but called out as a distinct, separately-reversible setting with full-egress acknowledgement. |
| Worktree not isolated / dangerous fallback (r2/r3 BLOCKER) | Strict runbook; **abort if worktree can't be created — NO temp-index/dirty-main fallback** (Gemini r3). Named branch off recorded `origin/main` SHA; pre/post checks; honest "files isolated, global git/auth shared". |
| Provenance / Claude-erosion (r2 MAJOR) | Loop contract: Codex owns implementation patches; Claude only mechanical metadata; else run marked mixed-author + not a clean pilot. |
| TDD theater (r1/r2 MAJOR) | Commit-pinned TDD trace: failing test committed before impl; red run against pre-impl SHA; green after. |
| Past-tense / pre-approval host change (r2 MAJOR) | §"Already executed this session" labels it honestly + reversible; ACs are future-tense verifiable. |

## Decision

Supported Codex-under-Claude route = **Option 6**: AppArmor profile granting `userns` to `/usr/bin/bwrap` + `~/.codex/config.toml [sandbox_workspace_write] network_access=true`. Claude orchestrates via the broker (`codex-companion.mjs task --write --background`); Codex executes autonomously. Brain/hands (Option 9) retained only as a documented degraded fallback for hosts where the change is declined.

## Security (honest)

- The grant targets the **system `/usr/bin/bwrap`**, shared by VSCode, Firefox, Flatpak (`apt-cache rdepends bubblewrap`; `code`/`firefox`/`snapd` installed). So **all bwrap consumers** regain unprivileged-userns — NOT Codex alone. Codex hardcodes `/usr/bin/bwrap` with no override, so a codex-only scope is impossible.
- Tradeoff: unprivileged userns is a kernel-LPE primitive Ubuntu 24.04 restricts by default. This re-opens it for bwrap-invoking processes. **Narrower than** the blanket sysctl (all binaries); **broader than** codex-only (impossible). **User reviewed and chose to keep it** (2026-05-26) over rollback or sysctl. Fully reversible: `sudo apparmor_parser -R /etc/apparmor.d/codex-bwrap && sudo rm /etc/apparmor.d/codex-bwrap`.
- `flags=(unconfined)`: bwrap runs otherwise-unconfined under this profile (bwrap's own namespace/seccomp sandboxing is the boundary, not AppArmor). Documented, not hidden.

## Scope

**#2804 is DONE when (independent of #2802):**
1. AppArmor profile (de-hardcoded) + guarded installer + teardown committed under `scripts/install/`.
2. Codify: correct the 2026-05-26 orchestrator-handoff "broker = bwrap-free" claim; update codex-handoff template to broker + one-time-setup; memory updated (see §Already executed).
3. Pilot report `docs/reports/2026-05-26-codex-under-claude-pilot.md` recording the validation evidence + `codex --version`.
4. **Synthetic smoke test**: installer `--check` passes AND a broker `task --write` in a *disposable fixture dir* (not the repo) writes a probe file + runs a command — proving the route, owned entirely by #2804.

**#2802 is a separate issue** (its own TDD/PR/legal-scan/merge). It is referenced as the first real-world pilot but is NOT a #2804 acceptance gate.

Out of scope: #2802 Phase-2 nudge/GitHub App; blanket sysctl (fallback only); broker plugin-cache edits.

## Execution

**Install (guarded, user-authorized):** see §Already executed — done + validated. Installer committed so other machines reproduce *with* the guards.

**#2802 pilot (post-approval, separate issue) — worktree runbook:**
- Assert `/mnt/local-analysis/wt-2802` does not pre-exist (else inspect/remove explicitly). `WTBASE=$(git rev-parse origin/main)`; `git worktree add -b codex/2802-kanban-reconciler /mnt/local-analysis/wt-2802 "$WTBASE"`.
- **If worktree creation fails or stalls (5-min poll): ABORT the pilot and report.** Never run Codex in the dirty main repo.
- Record `git worktree list --porcelain`, `git -C <wt> rev-parse HEAD`, `status --short`, `branch --show-current`. Note honestly: this isolates *working-tree files* only; global git config, credentials, Codex auth, broker cache, and the remote branch namespace remain shared.
- Dispatch #2802 to Codex via broker `task --write --background --cd /mnt/local-analysis/wt-2802` with allowed/forbidden write paths in the prompt. **Codex owns all implementation patches**; Claude applies only mechanical metadata or marks the run mixed-author.
- TDD trace: Codex commits the failing test first; red run captured against that SHA; implement; green. Claude verifies the trace.
- Claude runs code-stage T3 review on the diff; findings relayed to Codex to fix. PR `Refs #2802`; **user merges**. `git worktree remove` after.

## Risks & mitigations

| # | Risk | Mitigation |
|---|---|---|
| R1 | Profile path breaks on codex/npm change | Targets stable `/usr/bin/bwrap`; installer `--check` detects drift; sysctl fallback documented |
| R2 | Worktree stalls | Abort pilot (NO dirty-main fallback); retry or escalate to user |
| R3 | TDD theater | Commit-pinned red→green trace, behavioral assertion, verified by Claude + reviewer |
| R4 | Codex full network egress (workspace-write) | Documented; required for gh/git; separately reversible; not bundled silently with userns fix |
| R5 | Host-security exposure (bwrap-wide userns) | User-accepted, documented, reversible; installer requires `--accept-userns-lpe-risk` + Ubuntu/AppArmor detection |
| R6 | Batch agent auto-runs privileged installer | Installer defaults to `--check`; refuses to write without explicit risk flag; no-ops on non-Ubuntu |
| R7 | Broker bypasses version guard | Log `codex --version` before each task; pin via `scripts/install/pin-codex.sh` on regression |

## Acceptance criteria (future-tense, #2804-scoped)

1. `scripts/install/codex-bwrap.aa` contains **no** absolute home paths (passes `check-no-abs-paths.sh`); targets only `/usr/bin/bwrap`.
2. `scripts/install/setup-codex-sandbox.sh` exists with `--check` (default, no mutation), `--dry-run`, explicit `--accept-userns-lpe-risk` to write, Ubuntu+AppArmor detection (fail-fast otherwise), sentinel-guarded refuse-overwrite; `scripts/install/teardown-codex-sandbox.sh` reverses it.
3. Orchestrator-handoff "broker = bwrap-free" claim corrected; codex-handoff template references broker + setup; memory updated.
4. Pilot report committed with validation evidence + `codex --version`.
5. Synthetic smoke test (broker writes probe in a disposable fixture dir) documented as reproducible.
6. No further privileged host change beyond the one-time, user-authorized step already made.

(#2802's own ACs — genuine TDD, dry-run, legal scan, T3 review, PR `Refs`, no self-merge — live on #2802, not here.)

## Already executed this session (pre-approval, reversible)

These were done during diagnosis with explicit user authorization, BEFORE this plan's approval; listed honestly:
- AppArmor profile installed at `/etc/apparmor.d/codex-bwrap` (user ran sudo; loaded; `aa-status` confirms). Reversible (see §Security).
- `~/.codex/config.toml` → `[sandbox_workspace_write] network_access=true` (Claude edit).
- Memory `feedback_codex_sandbox_write_blocked` updated with fix + tradeoff.
- Validation evidence captured (codex exec + broker both wrote probe files; strace identified `/usr/bin/bwrap`).
The committed installer will reproduce this *with* the v3 guards (which the manual steps lacked).
