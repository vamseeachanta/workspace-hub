# Codex-under-Claude execution route — pilot report (#2804)

**Date:** 2026-05-26 · **Host:** ace-linux-1 (Ubuntu 24.04.4 LTS) · **codex-cli:** 0.133.0 · **Status:** route validated; codified for reuse

## Problem
Running OpenAI Codex as a delegated sub-agent *nested inside Claude Code* failed: every Codex shell/tool call died at `bwrap: loopback: Failed RTM_NEWADDR` / `bwrap: setting up uid map: Permission denied`. This blocked the original #2802 delegation (Codex returned `Blocked before implementation`, `touchedFiles: []`).

## Root cause
Ubuntu 24.04 sets `kernel.apparmor_restrict_unprivileged_userns=1`, blocking unprivileged user-namespace creation that `bwrap` (Codex's sandbox) requires. We run in the host's **initial** user namespace (`/proc/self/uid_map = 0 0 4294967295`), so the blocker is the host AppArmor policy — **not** a Claude userns sandbox. `strace -f -e execve` proved Codex execs the **system `/usr/bin/bwrap`** (not its vendored copy) as its outer sandbox.

## Fix (one-time, persists across reboots; no runtime sudo)
1. AppArmor profile `scripts/install/codex-bwrap.aa` → `/etc/apparmor.d/codex-bwrap`, granting `userns` to `/usr/bin/bwrap`. Installed via `scripts/install/setup-codex-sandbox.sh --accept-userns-lpe-risk`.
2. `~/.codex/config.toml` → `[sandbox_workspace_write] network_access = true` (bwrap shares host net, skipping the `--unshare-net` loopback step; Codex needs network for gh/git).

## Validation evidence (full output verified)
| Channel | Command | File write |
|---|---|---|
| `/usr/bin/bwrap --unshare-user … echo` | `SYSTEM_BWRAP_USERNS_OK` | — |
| `codex exec` (workspace-write + network) | `git rev-parse` → `fix/2795-…` | `.codex-exec-probe.txt` = `VALIDATED-EXEC` |
| Broker `codex-companion.mjs task --write` | exit 0 | `.codex-broker-probe.txt` = `BROKER-OK` |
| Codex r2 review (broker, autonomous) | — | wrote its own 12 KB review artifact |

## Route going forward
Claude orchestrates via the broker (`codex-companion.mjs task --write --background`); Codex executes autonomously (own shell/tests/writes/patches). Cross-provider review unchanged (Claude + Codex + Gemini). Degraded fallback for hosts without the setup: brain/hands (Codex generates text, Claude executes) — see #2804 history.

## Security tradeoff (user-accepted 2026-05-26)
The grant targets the system `/usr/bin/bwrap`, shared by VSCode/Firefox/Flatpak — so all bwrap consumers regain unprivileged userns, not Codex alone (Codex offers no bwrap-path override). Narrower than the blanket sysctl (all binaries); broader than codex-only (impossible). Unprivileged userns is a kernel-LPE primitive; the user reviewed and chose to keep the profile over rollback. Reversible via `scripts/install/teardown-codex-sandbox.sh`.

## Lessons (also in memory `feedback_codex_sandbox_write_blocked`)
- Profile the binary Codex *actually execs* (`strace`), not the one `find` surfaces — first attempt targeted the unused vendored bwrap.
- Don't claim "validated" from absence-of-error in a filtered view; confirm the actual stdout + that the file landed.
- The broker only avoids bwrap for runtime boot, not per-command execution — corrected the 2026-05-26 orchestrator handoff.

## First real-world pilot
#2802 (kanban reconciler) — executed via this route under its own issue/PR/ACs (referenced, not part of #2804's acceptance).
