# Pull/poll dispatch for no-SSH hosts (WF3 #3000)

`workstation-dispatch.sh` (F3) delivers work by **SSH push**. The hosts `ace-win-1`, `ace-win-2`,
`macbook-portable` and `gali-linux-compute-1` are `ssh: null` — they cannot be pushed to. WF3 adds the
**pull** complement: such a host claims and runs work itself, arbitrated by the F3 git-ref lease so two
hosts polling the same source never run the same item.

## How it works

`scripts/operations/dispatch_pull.py`:

1. Resolves this host's registry id (`resolve_machine_id`, alias-aware — the real Windows name
   `mkt-a-ANSYS05` resolves to `ace-win-1`).
2. `git fetch` of the `refs/heads/dispatch-lease/*` namespace (so the lease CAS sees other hosts' claims).
3. Reads the routed-card list `.claude/dispatch/<machine>.yaml` (cards with `dispatch_status: ready`).
4. For each card, **`claim_run`** acquires a fenced git-ref lease keyed by the card id
   (`dispatch_lease.acquire`; a crashed holder's expired lease is recovered by `reclaim`), runs the
   executor, fence-checks with `verify_token`, then records completion. **There is no release** — the
   lease lapses via TTL; completion is recorded on the item.
5. `git push` of the lease namespace.

The lease guarantees **no double-run**: if `ace-win-1` holds a card's lease, `ace-win-2` polling the
same list gets `skipped_held`. The fence (`verify_token` before completion) ensures a holder that was
superseded mid-run cannot falsely mark the item done.

## Running it on a no-SSH host (Git Bash)

```bash
python -m pip install --user pyyaml          # uv is not installed on the Windows hosts
# dry-run (claims nothing destructive — prints what it would dispatch):
python scripts/operations/dispatch_pull.py --machine ace-win-1
# real run (wire a real executor — see integration below):
python scripts/operations/dispatch_pull.py --machine ace-win-1 --apply
```

Scheduling the poll is **WF2** (#2815, Windows Task Scheduler); on Linux no-SSH hosts (gali) use cron.

## Trigger: Telegram via deckhand (long-term control surface)

Per the epic decision, the durable trigger is **Telegram via deckhand** (WF4 / #2742 + the venue
contract): an operator announces work in the venue; the no-SSH host's poll claims the lease-arbitrated
item. The poll cadence + the deckhand announcement are the two ways a host learns there is work; the
lease is the safety net that makes either safe to run on multiple hosts.

## Integration (opt-in — not wired by default)

`--apply` currently uses a safe dry-run executor. To do real work, supply an executor that runs the
card (e.g. `claude`/`codex` on the GitHub issue) or that feeds the existing solver queue. The live
solver pull (`scripts/solver/process-queue.py`, client SLA) is intentionally **unchanged**; it can
adopt the same lease by wrapping `process_job` in `claim_run` keyed by the job name, so `ace-win-1`
and `ace-win-2` could both poll `queue/pending` without double-running — a follow-up, behind its own
review.

## Robustness cases

The same agent runs on `macbook-portable` (darwin) and `gali-linux-compute-1` (linux, `ssh:null`) —
only the scheduler differs. The lease arbitration and pure `claim_run` core are OS-agnostic.
