> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-09
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_codex_sandbox_write_blocked.md

---
name: Codex sandbox under Claude — bwrap nesting fix (AppArmor + network_access)
description: Codex's bwrap sandbox fails nested under Claude (Ubuntu 24.04 AppArmor blocks unprivileged userns); FIXED via a surgical AppArmor profile granting userns to /usr/bin/bwrap + config.toml network_access=true. Both codex exec and the broker then run fully.
type: feedback
originSessionId: 9b439b61-1bc0-4c85-b9a9-727564b48494
---
**RESOLVED 2026-05-26 (#2804).** Codex CAN run shell + write files nested under Claude Code on ace-linux-1. The old "sandbox blocks all writes, capture inline only" workaround is SUPERSEDED.

**Root cause:** Ubuntu 24.04 sets `kernel.apparmor_restrict_unprivileged_userns=1`, which blocks `bwrap` from creating the user/network namespaces its sandbox needs. We run in the host's initial userns (NOT a Claude userns sandbox — `/proc/self/uid_map` = `0 0 4294967295`), so the blocker is the host AppArmor policy, not Claude. Two distinct bwrap stages fail: net-ns loopback (`RTM_NEWADDR`) and user-ns (`uid map: Permission denied`).

**The fix (one-time, persists across reboots; runtime needs NO sudo):**
1. AppArmor profile `/etc/apparmor.d/codex-bwrap` granting `userns` to `/usr/bin/bwrap` (the SYSTEM bwrap — Codex execs `/usr/bin/bwrap` at runtime as its outer sandbox, NOT its vendored copy; verified by `strace -f -e execve`). `flags=(unconfined)` + `userns,`. Load: `sudo apparmor_parser -r -W /etc/apparmor.d/codex-bwrap`.
2. `~/.codex/config.toml` → `[sandbox_workspace_write]` `network_access = true` (makes bwrap share host net, skipping the `--unshare-net` loopback step that fails nested; Codex needs network for gh/git anyway).

**Verified:** both `codex exec -c sandbox_mode=workspace-write -c sandbox_workspace_write.network_access=true` AND the plugin broker (`codex-companion.mjs task --write`) run shell commands AND write files in the workspace. The broker hardcodes `workspace-write` (`codex-companion.mjs:460`) and reads network_access from config.toml.

**Lessons that bit this session:**
- Profile the binary Codex ACTUALLY execs (`/usr/bin/bwrap`), not the vendored one the `find` surfaced — `strace` is ground truth.
- Don't claim "validated" from a filtered grep showing no error; confirm the actual stdout/file landed. (Claimed codex exec worked on absence-of-error, then full output showed `uid map` failure.)
- See also [[feedback_codex_needs_pushed_artifact]] (read-side, still relevant for GitHub-connector reads), [[feedback_codex_sustained_major_loop]].

**Security tradeoff (user-accepted 2026-05-26):** the profile targets the SYSTEM `/usr/bin/bwrap`, which is shared by VSCode/Firefox/Flatpak (`apt-cache rdepends bubblewrap`) — so the `userns` grant is NOT codex-only; all bwrap consumers regain unprivileged userns. Codex offers no bwrap-path override, so a truly codex-only AppArmor scope is impossible. User chose to KEEP this (narrower than the blanket sysctl, reversible) over rollback. Spectrum: codex-only (impossible) < bwrap-profile (chosen) < blanket sysctl (all binaries).

**Fallback if the profile path breaks** (e.g., npm relocates Codex): blanket `sudo sysctl -w kernel.apparmor_restrict_unprivileged_userns=0` (+ /etc/sysctl.d drop-in) — weaker (host-wide) but guaranteed.

---
_Historical (pre-fix, #2342 2026-04-17/19):_ Codex sandbox blocked `apply_patch`/shell-writes with `bwrap: loopback: Failed RTM_NEWADDR`; workaround was capturing findings in return text and writing `scripts/review/results/*-codex.md` from the main session. Still usable as a degraded mode if AppArmor can't be changed.
