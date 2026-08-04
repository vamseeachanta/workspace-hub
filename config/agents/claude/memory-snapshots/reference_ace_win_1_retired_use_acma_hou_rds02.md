---
name: reference_ace_win_1_retired_use_mkt-a_hou_rds02
description: "ace-win-1 is RETIRED (owner, 2026-08-04); the licensed/Windows lane is now mkt-a-hou-rds02 — but SSH from ace-linux-1 is NOT yet provisioned"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 3b006eae-10ef-4664-8b7a-316d95790cce
  modified: 2026-08-04T06:31:42.273Z
---

**Owner directive 2026-08-04: `ace-win-1` is retired. Use `mkt-a-hou-rds02`.**

Any plan, issue, or `machine:licensed-win-1` label naming `ace-win-1` should be read as
pointing at `mkt-a-hou-rds02` until the labels are migrated.

## Access is NOT yet working — this is the gap

`mkt-a-hou-rds02` = tailnet **100.93.182.24**, Windows, owner `vamsee.achanta@`.

Verified 2026-08-04 from ace-linux-1:

```
ssh mkt-a-hou-rds02 → vamsee@mkt-a-hou-rds02: Permission denied (publickey,keyboard-interactive)
```

- No `~/.ssh/config` Host entry
- No `known_hosts` record
- No script under `workspace-hub/scripts` or `digitalmodel/scripts` references the name

So this host has **never** been driven over SSH from ace-linux-1. Tailscale SSH does not
cover it — Tailscale SSH is Linux/macOS only, so a Windows target needs real OpenSSH auth
(key installed in the Windows user's `authorized_keys`, or the admin variant at
`C:\ProgramData\ssh\administrators_authorized_keys`). Local user is probably not `vamsee`;
domain is **mkt-a-INC** (see [[reference_ws014_access_and_2026_07_13_wedge]]).

**Needs a user action to provision.** An agent cannot install its own key on a box it
cannot log into.

## What this blocks

The environment the retired ace-win-1 carried — repo at `/d/ws/digitalmodel` on `main`,
interpreter `/d/ws/digitalmodel/.venv/Scripts/python.exe`, numpy 1.26.4 / scipy 1.15.3 /
pytest 8.4.2, sibling `assetutilities` at `/d/ws/assetutilities`, worktree convention
`/d/ws/_worktrees/<name>` — is **not** known to exist on mkt-a-hou-rds02. Assume it must be
built out, not inherited.

Concretely blocked today: digitalmodel [#1633]'s closeout acceptance criterion, which
demands a full-suite node-ID run on the Windows host with
`.venv/Scripts/python.exe -m pytest tests/ -q --no-header -p no:cacheprovider --capture=no`
compared node-ID by node-ID against a baseline captured in the same worktree at the branch
point. Implementation work itself is pure-Python and unblocked; only the closeout run needs
this host.

Other Windows boxes on the tailnet, for contrast: `acma-ws014` (offline 2d as of
2026-08-04), `lng-alt163` (offline 15d).

See [[reference_ace_win_1_equality_evidence_stale]],
[[reference_ace_win_1_headless_verification_via_heartbeat]],
[[feedback_machine_identity_is_logical_alias_565]].
