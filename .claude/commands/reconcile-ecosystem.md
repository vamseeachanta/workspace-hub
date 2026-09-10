---
name: reconcile-ecosystem
description: "Bring THIS computer back to ecosystem + machine-equality equivalence in one keystroke. Detects repo-hygiene drift (dirty trees, behind/ahead, merged-safe-pattern branches, stale worktrees/stashes) across sibling repos AND maps every non-OK equality-matrix verdict for this machine to its fix. Report-first; destructive actions are guard-gated and opt-in (never discards dirty work; ff-only; deny-by-default worktree guard; dev-primary destructive-locked)."
argument-hint: "[--apply] [--stash-dirty] [--equality] [--json] (no args = read-only report)"
allowed-tools: Read, Bash, Edit, Glob, Grep, Agent
---

## Reconcile: This Machine → Ecosystem Equivalence

Drive `scripts/readiness/reconcile-ecosystem.sh` (repo-root relative) under the
`ecosystem-equivalence-reconcile` skill (the playbook + safety boundary live there).
**Default is read-only** — print the plan and stop unless the user passed action flags.

### 0. Parse `$ARGUMENTS`

| Flag | Default | Meaning |
|---|---|---|
| *(none)* | report-only | Detect drift + equality gaps, print the classified plan, change nothing. |
| `--apply` | off | Execute only the **AUTO-SAFE** subset (ff-only pulls, etc.). |
| `--stash-dirty` | off | With `--apply`: stash dirty trees (recoverable) instead of surfacing them. **Never discards.** |
| `--equality` | off | With `--apply`: after hygiene, re-collect this box's equality report and rebuild the matrix. |
| `--json` | off | Emit the machine-readable plan (no actions). |

If flags look absent/exploratory, treat as the read-only report.

### 1. Resolve context

!`WS="$(git rev-parse --show-toplevel 2>/dev/null || echo /mnt/local-analysis/workspace-hub)"; echo "WS=$WS"; H="$(hostname | tr '[:upper:]' '[:lower:]')"; case "$H" in ace-linux-1*) M=dev-primary;; ace-linux-2*) M=dev-secondary;; *macbook*) M=macbook-portable;; ace-win-1*) M=ace-win-1;; ace-win-2*) M=ace-win-2;; *) M="$H";; esac; echo "machine=$M"`

This machine reconciles **its own** equality column. On `dev-primary` the driver auto-locks
destructive disposal (`DESTRUCTIVE_OK=0`) — it owns the daily-cleanup cron + intentional worktrees.

### 2. Safety boundary (load-bearing — do not bypass)

The driver inherits the deny-by-default guard (`scripts/lib/worktree_guard.py`, #3143). It **never**:
discards dirty work · deletes an unmerged/current/checked-out branch · removes a worktree it
can't prove it owns · does anything but fast-forward on remotes. Every action is pre-classified
`AUTO-SAFE` / `NEEDS-APPROVAL` / `OPERATOR-ONLY`; only AUTO-SAFE auto-runs under `--apply`.

### 3. Execute

1. Run the driver from `$WS` with the parsed flags:
   - report: `bash scripts/readiness/reconcile-ecosystem.sh`
   - apply: `bash scripts/readiness/reconcile-ecosystem.sh --apply [--stash-dirty] [--equality]`
   - json:  `bash scripts/readiness/reconcile-ecosystem.sh --json`
2. **Present** the plan grouped by class. For `--apply`, report exactly what ran and what was held.
3. **Surface `NEEDS-APPROVAL`** items for the user — each prints its exact command. Do not run them
   automatically. For at-scale branch/worktree disposal on the primary, prefer the guarded cron
   (`scripts/cron/daily-cleanup.sh --dry-run` then live) over ad-hoc deletion.
4. For `OPERATOR-ONLY` (Windows licence probe, hardware, remote host), name the off-box action.
5. If `--equality` ran, note that the matrix was rebuilt; per [[machine-equality-matrix-live-link]] a
   push is needed to refresh the live link. A divergence that survives a clean re-collect is a **real**
   config drift, not a stale-report artifact — fix the config, don't just re-collect again.

### 4. Gate exemption

This is operational automation, not issue implementation — it does **NOT** route through the
Issue→Plan→Approve→Implement gate. The driver's own guards + the user's review of NEEDS-APPROVAL
items are the control points. (If a finding spawns separate tracked work, that work re-enters the gate.)

---
**Examples**
- `/reconcile-ecosystem` — read-only: what needs fixing on this box right now
- `/reconcile-ecosystem --apply` — run the safe subset (ff-pulls clean repos, etc.)
- `/reconcile-ecosystem --apply --stash-dirty` — also stash (recoverable) dirty trees, then re-pull
- `/reconcile-ecosystem --apply --equality` — reconcile, then refresh this machine's equality column
- `/reconcile-ecosystem --json` — machine-readable plan for CI/dispatch
