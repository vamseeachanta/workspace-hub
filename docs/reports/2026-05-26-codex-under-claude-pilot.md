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

## Isolated dispatch — clone vs worktree (#2822)
**This section runs ON TOP OF the base route above.** It does not replace the userns grant + `network_access`; those remain prerequisites (without them Codex cannot run at all). It only covers *where* Codex writes when you want isolation from the live checkout.

**Why isolation is non-trivial.** Codex `sandbox_mode = workspace-write` grants write to **one contiguous root**. A git **worktree** deliberately splits its state: the working tree is at the worktree path, but its `.git` is a *gitlink file* pointing to `<main-repo>/.git/worktrees/<name>`, and shared objects/refs live in the main `.git` — all **outside** the worktree root. The sandbox mounts those read-only, so file writes succeed but `git commit` fails `index.lock: Read-only file system` (discovered live in the #2802 pilot, PR #2820).

### Recommended: a write-isolated local clone (only `--cwd` needed)
Prepare a self-contained clone whose `.git` lives *inside* the dispatch root, then point the broker at it:

```bash
scripts/install/codex-dispatch-prep.sh --prepare <branch>      # default: git clone --no-hardlinks (write-isolated)
# emits the exact broker invocation, e.g.:
node <broker> task   --cwd <clone> --write --background --prompt-file /abs/path/to/prompt.md
node <broker> status --cwd <clone>                              # status/result need --cwd too (jobs keyed by toplevel)
node <broker> result --cwd <clone> <JOB_ID>
scripts/install/codex-dispatch-prep.sh --cleanup <clone>        # guarded rm -rf when done
```

- **Default is `git clone --no-hardlinks`, not `--local`.** `--local` *hardlinks* object files, so the clone's `.git/objects/<x>` shares an **inode** with the source — a write-capable sandbox could corrupt the source repo's objects. `--no-hardlinks` copies objects (distinct inodes = true isolation). Reproduced: `--local` clone object inode == source; `--no-hardlinks` inode differs. Cost: a one-time object-store copy (~228 MB for workspace-hub), reclaimed on cleanup; works on any filesystem.
- **`--allow-hardlinks` (→ `git clone --local`) is opt-in for READ-ONLY dispatch only** (immutable shared objects can't be corrupted by reads). It's cheaper but **must not** be used for write dispatch. `--local` also cannot cross filesystems (`Invalid cross-device link`); the helper falls back to `--no-hardlinks` automatically.
- The helper re-points the clone's `origin` at the GitHub URL so Codex can push, then `git fetch origin` + `checkout -b <branch> origin/main` so the branch bases on true remote `main`. **Push auth** uses your ambient git credential helper (global `~/.gitconfig`) — on a fresh host, run `gh auth login` / configure credentials first.
- Cleanup is fail-closed: it refuses any path that isn't a sentinel-marked (`.git/codex-dispatch-managed`), `*-cxc-*`-named git toplevel under the dispatch root (never `/`, `$HOME`, or the source repo).

### Fallback: a literal worktree + writable-roots grant (NOT recommended)
Only if you must dispatch into an existing worktree, **all three** of the following are required, or it blocks silently — each on a different layer (memory `feedback_codex_worktree_sandbox_three_layer`):
1. **`--cwd <worktree>` on the broker `task`** — not a `cd` in the prompt, and *not* `--cd` (not a flag; it leaks into the prompt). The broker derives the sandbox root from cwd via `git rev-parse --show-toplevel`.
2. **`[sandbox_workspace_write].writable_roots = ["<main-repo>/.git"]` in `~/.codex/config.toml`** — so worktree commits can write the gitlinked metadata + shared object/ref db. *Blast-radius:* the entire shared `.git` (all branches/objects/refs) becomes writable to the sandbox.
3. **Restart the broker's shared `serve`/app-server after editing config** — it reads `config.toml` once at spawn; a live edit is a silent no-op until the per-workspace `/tmp/cxc-*` session is killed and respawned.

Also: broker jobs are namespaced by workspace root, so `status`/`result` for a worktree-rooted job need `--cwd <worktree>` too. The clone route avoids all three layers and the shared-`.git`-writable blast radius — prefer it.

## Security tradeoff (user-accepted 2026-05-26)
The grant targets the system `/usr/bin/bwrap`, shared by VSCode/Firefox/Flatpak — so all bwrap consumers regain unprivileged userns, not Codex alone (Codex offers no bwrap-path override). Narrower than the blanket sysctl (all binaries); broader than codex-only (impossible). Unprivileged userns is a kernel-LPE primitive; the user reviewed and chose to keep the profile over rollback. Reversible via `scripts/install/teardown-codex-sandbox.sh`.

## Lessons (also in memory `feedback_codex_sandbox_write_blocked`)
- Profile the binary Codex *actually execs* (`strace`), not the one `find` surfaces — first attempt targeted the unused vendored bwrap.
- Don't claim "validated" from absence-of-error in a filtered view; confirm the actual stdout + that the file landed.
- The broker only avoids bwrap for runtime boot, not per-command execution — corrected the 2026-05-26 orchestrator handoff.
- **A hardlinked clone is not write-isolation for a write-capable sandbox (#2822).** `git clone --local` shares object *inodes* with the source; a sandbox with write access to the clone can corrupt the source repo's objects. "Self-contained" (no external `alternates`) ≠ "write-isolated" (distinct inodes). Default to `--no-hardlinks` for any write-capable clone dispatch; reserve `--local` for read-only. Generalizes beyond Codex to any sandbox+clone pattern.

## First real-world pilot
#2802 (kanban reconciler) — executed via this route under its own issue/PR/ACs (referenced, not part of #2804's acceptance).

## Fleet rollout coverage (#2813)

The route is a **per-machine, user-authorized** install (the userns grant is a kernel-LPE-surface decision — no batch/fleet auto-run). Roster enumerated **empirically from `config/workstations/registry.yaml`** (6 machines — not assumed; the registry lists two beyond the four initially in mind, per the "verify coverage empirically" rule). Status as of 2026-05-26:

| Machine | OS / role | Status | Evidence / reason |
|---|---|---|---|
| **ace-linux-1** | linux | **FUNCTIONAL** (route live); reconcile to installer-managed pending user sudo | `setup-codex-sandbox.sh --check` → profile present + `network_access: true`; broker ran live Codex `task` jobs (#2822 reviews); codex-cli 0.134.0. Profile applied out-of-band during the #2804 pilot (`managed-by-us: no`); reconcile to the committed installer (sentinel-stamped, teardown-able) is a user-authorized sudo step (see runbook). |
| **ace-linux-2** | linux (SSH-reachable per registry) | **PENDING** (per-machine) | Not yet onboarded; install runs during a session on ace-linux-2 (runbook below). User chose runbook-only over an SSH-driven install (#2813 Q2). |
| **shoerack** | linux, gpu-compute | **PENDING — not yet configured** | `workspace_root: null`, `ssh: null` (access TBD) in the registry. The route *applies* (Linux) once the machine has a workspace-hub checkout and is reachable + Codex-under-Claude is wanted; until then nothing to install. |
| **Vamsees-MacBook-Air** | **macOS**, portable-dev | **N/A** | macOS has no AppArmor/bwrap — the #2804 userns blocker does not exist; installer fail-fasts. Codex's macOS sandbox is a different model (out of #2804 scope). |
| **licensed-win-1** | windows (`ssh: null`, GUI-only) | **N/A** | The #2804 AppArmor/userns fix is Linux-only; installer fail-fasts on non-Ubuntu/no-AppArmor. Windows-native Codex-under-Claude (if wanted) is a separate, out-of-scope question. |
| **licensed-win-2** | windows (`ssh: null`, GUI-only) | **N/A** | Same as licensed-win-1. |

`#2813` stays a tracking item until the two Linux PENDINGs (ace-linux-2, shoerack) resolve (installed or confirmed not-wanted).

### Per-machine runbook (Ubuntu, run on the target machine)

One-time, user-authorized. The installer grants userns to `/usr/bin/bwrap` but **does not write `~/.codex/config.toml`** — the `network_access` edit is a separate explicit step (the installer only prints a reminder):

```bash
cd <workspace-hub> && git pull
bash scripts/install/setup-codex-sandbox.sh --check               # report state (no mutation; fail-fasts on non-Ubuntu → N/A)
bash scripts/install/setup-codex-sandbox.sh --accept-userns-lpe-risk   # one-time sudo; persists across reboots
# REQUIRED separate step — the installer does NOT write config:
grep -q 'network_access = true' ~/.codex/config.toml || printf '\n[sandbox_workspace_write]\nnetwork_access = true\n' >> ~/.codex/config.toml
bash scripts/install/setup-codex-sandbox.sh --check               # expect: managed-by-us: yes, network_access: true
# functional smoke: a broker `task --write` exits 0
bash scripts/setup/lib/emit-machine-status.sh                     # refresh this machine's baseline + post to tracker #2753
```
Reverse with `scripts/install/teardown-codex-sandbox.sh`. For an isolated write-dispatch checkout on the machine, use `scripts/install/codex-dispatch-prep.sh` (#2822).
