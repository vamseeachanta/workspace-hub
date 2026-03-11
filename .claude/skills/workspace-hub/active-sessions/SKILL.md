---
name: active-sessions
description: >
  Surface all WRK items with active session locks on this workstation — claimed and unclaimed.
  Use when: session-start pre-work audit, investigating cross-session collision, answering
  "what's running right now?", or any session discovery context.
  Runs scripts/work-queue/active-sessions.sh and presents output.
version: 1.0.0
category: workspace-hub
type: skill
trigger: manual
related_scripts: [scripts/work-queue/active-sessions.sh]
reuse_in: [session-start, whats-next, claim-item]
---

# Active Sessions

Scans all `assets/WRK-NNN/evidence/session-lock.yaml` files and classifies each lock
by queue location and lock age. Reports claimed (working/) vs unclaimed (pending/) items
that have a recent session lock.

## Usage

```bash
bash scripts/work-queue/active-sessions.sh
bash scripts/work-queue/active-sessions.sh --unclaimed-only
bash scripts/work-queue/active-sessions.sh --json
```

## Output Format

Each active session row:

```
WRK-ID         STATUS     AGE     HOSTNAME             LOCKED_AT
WRK-1097       unclaimed  12min   ace-linux-1          2026-03-10T06:00:00Z
WRK-1085       claimed    45min   ace-linux-1          2026-03-10T05:27:00Z
```

| Column | Meaning |
|--------|---------|
| WRK-ID | Work item identifier |
| STATUS | `claimed` (in working/) or `unclaimed` (in pending/) |
| AGE | Minutes since locked_at |
| HOSTNAME | Machine that wrote the lock |
| LOCKED_AT | UTC timestamp from session-lock.yaml |

## Flags

```
--json            Output as JSON array for scripting
--unclaimed-only  Show only items in pending/ with active locks
```

## Liveness Heuristic (v1)

Liveness is determined by lock age only: `locked_at` within the last 2 hours (7200s).

The `session_pid` field is NOT used for liveness checking. The PID belongs to
`start_stage.py` — a short-lived script that exits immediately after writing the lock.
`kill -0 <pid>` will always return "dead" regardless of whether a session is actually
active. Age-only is the documented v1 approach.

## Claimed vs Unclaimed

Canonical source of truth is the queue folder location:

- `working/WRK-NNN.md` exists → **claimed**
- `pending/WRK-NNN.md` exists → **unclaimed** (session started but claim-item.sh not run)

The `status:` field inside session-lock.yaml is NOT used (known bug: duplicate keys
in some lock files written by earlier versions of claim-item.sh).

## Notes

- Stale locks (age >= 2h) are silently skipped and do not appear in output.
- For full queue priority view, use `bash scripts/work-queue/whats-next.sh` which also
  shows the ⚠ IN-PROGRESS UNCLAIMED section.
- If unclaimed items appear, investigate before starting the same WRK in another session.
