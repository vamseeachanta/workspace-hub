# Session handoff - 2026-10-12 - Linux workstation CLI install consolidation

Scope: the Codex and agy (Antigravity) CLI installs of one user account on a Linux
workstation were inventoried, de-duplicated and brought to the latest published
release. State probed 2026-10-12 16:40 UTC. Execution owner: none; the work is
complete and no process is running.

## Result

| CLI | Before | After | Comparator | Disposition |
|---|---|---|---|---|
| Codex | npm global Codex package 0.162.1, plus snap `codex` 0.114.0 (rev 34) | npm global 0.162.1 only | package-manager `latest` dist-tag = 0.162.1 | Single install, at latest |
| agy | `~/.local/bin/agy` 1.2.9 | `~/.local/bin/agy` 1.3.3 | `agy update` reports "already on the latest version" | Single install, at latest |

## Actions taken

- Codex: no upgrade was required; the npm install already matched `latest`. The snap package
  was removed by the owner with `sudo snap remove --purge codex`; `--purge` also removed the
  per-user snap data directory `~/snap/codex`. `snap list codex` now returns
  "no matching snaps installed".
- `/usr/local/bin/codex` is retained. It is a root-owned symlink to the same npm install, not
  a second copy.
- agy: upgraded in place with `agy update` (1.2.9 to 1.3.3). No `agy` process was running at
  the time. The updater left a 217 MB backup of the previous binary
  (`~/.local/bin/agy.<timestamp>.old`); it was deleted after 1.3.3 was confirmed to run. No
  local rollback copy of 1.2.9 remains.
- No `antigravity` or `gemini` binary is on `PATH`, and no npm, snap or dpkg package exists
  for either.

## Findings for the fleet

- The removed snap `codex` was published by a publisher other than the vendor. It is
  recommended that other machines be checked with `snap list codex` and that the snap
  not be used as a Codex install route. Coverage on other machines is not established; only
  a Linux workstation was enumerated.
- The snap sat later on `PATH` than the npm install, so `codex` already resolved to 0.162.1.
  Any caller that invoked `/snap/bin/codex` by absolute path would have run 0.114.0; no such
  caller was searched for, and none is known.
- `agy update` leaves a full-size `.old` binary beside the new one on every upgrade. It is
  recommended that it be removed once the new version is verified.

## Not touched

- A second user account on the Linux workstation runs its own Codex 0.162.1 app-server daemon
  from its own `~/.codex`; it was observed in the process list and left unchanged.
- A separate agent CLI npm install (2.1.296) was observed, not assessed.
- As of 2026-10-12, the Linux workstation workspace-hub checkout was 67 commits behind
  `origin/main` with pre-existing local modifications, including a machine-equality state file
  for that workstation and the machine-equality-matrix reports. These predate the session and
  were not altered; the original handoff was committed from `origin/main` without changing that
  working tree.

## External actions

None beyond the package registry and updater downloads, and the push of the original handoff.

## Next session

No carry-forward work. Optional: run the same inventory (`type -a codex agy`,
`snap list codex`, `npm ls -g --depth=0`, and the tool's version query) on the remaining
fleet machines. Treat any update as a separate step requiring authorization.
