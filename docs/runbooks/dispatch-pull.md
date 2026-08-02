# Runbook: continuous pull dispatch (`dispatch-pull`)

> **Machine:** `dev-primary` (ace-linux-1) · **Task:** `dispatch-pull` in
> [`config/scheduled-tasks/schedule-tasks.yaml`](../../config/scheduled-tasks/schedule-tasks.yaml)
> **Cadence:** `7 */6 * * *` — 00:07 / 06:07 / 12:07 / 18:07 UTC
> **Issues:** [#3000](https://github.com/vamseeachanta/workspace-hub/issues/3000) (pull dispatch),
> [#3773](https://github.com/vamseeachanta/workspace-hub/issues/3773) (the unattended rails)

Every 6 hours, `scripts/cron/dispatch-pull-cron.sh` runs
`scripts/operations/dispatch_pull.py`. That loop reads the cards marked
`dispatch_status: ready` in `.claude/dispatch/dev-primary.yaml`, claims each one
under a git-ref lease so no other host runs it concurrently, and hands it to
`scripts/dispatch/drain.py`, which executes the bound command and writes a
dispatch record.

**As shipped it is inert.** It runs in dry-run — it claims nothing, executes
nothing, and writes nothing but a log. Two separate things have to be true before
it does real work, and they are covered in *Starting it* below.

---

## Reading this first: what is and is not automatic

| | |
|---|---|
| Automatic | *when* the loop runs, *which* cards it considers, *which* host wins a contested card, *how many* cards one run may execute |
| Deliberate, per issue, by a human | *what* a card actually runs (`.claude/dispatch/commands.yaml`) |
| Deliberate, per machine, by a human | whether the loop may write at all (the two gates) |

An issue nobody has bound is an issue nobody has authorised to run unattended.
That is the whole reason the queue can hold 1,344 cards and the loop can be armed
without anything happening.

---

## Starting it

### 1. Both gates

`dispatch_pull` refuses `--apply` unless `DISPATCH_APPLY_ENABLED=1` is also set,
and `drain.py` refuses to write for the same reason. Two gates, two names, on
purpose: one flag must not be able to satisfy both.

For the scheduled lane, arming lives in a **machine-local file that is not in the
repo**, so a fresh checkout on a new box never starts dispatching by itself:

```bash
mkdir -p ~/.workspace-hub
cat > ~/.workspace-hub/dispatch-pull.env <<'EOF'
DISPATCH_PULL_APPLY=1        # the wrapper adds --apply
DISPATCH_APPLY_ENABLED=1     # drain.py / reconcile.py write gate
EOF
chmod 600 ~/.workspace-hub/dispatch-pull.env
```

Setting only one is refused, by name, before anything is claimed:

```
$ DISPATCH_PULL_APPLY=1 DISPATCH_PULL_ENV_FILE=/dev/null bash scripts/cron/dispatch-pull-cron.sh
dispatch-pull-cron: DISPATCH_PULL_APPLY=1 without DISPATCH_APPLY_ENABLED=1
dispatch-pull-cron: set BOTH in /dev/null — nothing claimed.        # exit 2
```

Optional knobs in the same file: `DISPATCH_PULL_MACHINE`,
`DISPATCH_PULL_MAX_CARDS`, `DISPATCH_PULL_DELAY`. Unset means the module's own
defaults (5 cards per run, 30 s between hand-offs).

### 2. Install the cron line

The catalog is the source of truth; never edit `crontab -e` directly. Preview
first — the dry run prints the reconciled crontab and changes nothing:

```bash
bash scripts/cron/setup-cron.sh --dry-run --machine dev-primary   # preview
bash scripts/cron/setup-cron.sh          --machine dev-primary    # apply
```

The line it installs is:

```
7 */6 * * * mkdir -p .../logs/dispatch-pull && PATH=$HOME/.local/bin:$PATH; cd ... && bash scripts/cron/dispatch-pull-cron.sh
```

### 3. Run it by hand

Same wrapper, same gates, same singleton lock. Without the arming file this is a
dry run and is safe to run any time:

```bash
bash scripts/cron/dispatch-pull-cron.sh
tail -20 logs/dispatch-pull/cron-$(date -u +%F).log
```

The wrapper's own stdout goes to your terminal; the loop's stdout goes to that
dated log, because `cron_runtime.py` owns the child's output.

### Runs never overlap

The task declares `runtime.singleton: true`, so the wrapper execs
`scripts/cron/cron_runtime.py run`, which takes an exclusive `flock` on
`.claude/state/cron-runtime/dispatch-pull/runtime.lock`. A tick that arrives
while the previous run is still going **exits 75 and starts nothing**:

```bash
uv run --script scripts/cron/cron_runtime.py inspect \
  --schedule-file config/scheduled-tasks/schedule-tasks.yaml \
  --workspace "$PWD" --task-id dispatch-pull --format tsv
```

`completed_success` / `completed_failure` = idle. `active_within_budget` = a run
is in flight. `overlap` = a tick was refused while one was in flight — not fatal,
but if you see it routinely the cadence no longer matches how long runs take.
`excessive_runtime` = a run has passed `runtime.max_seconds` (18,600 s).

---

## Stopping it

### The kill switch

```bash
touch .claude/dispatch/PAUSE      # stop
rm .claude/dispatch/PAUSE         # resume
```

Presence of the file is the entire protocol. `drain.py` checks it immediately
before the claim and exits **3**; `dispatch_pull` treats exit 3 as
`FleetPaused`, records the one card as `paused`, and **breaks out of the loop**
rather than walking the rest of the queue recording failures the operator caused.

Two things it does **not** do:

* **It does not stop what is already running.** `scripts/dispatch/run.sh` detaches
  payloads with `setsid nohup`, precisely so that killing a wrapper loop cannot
  orphan them. A payload dispatched before you created `PAUSE` keeps going, holds
  whatever seat it holds, and finishes normally. See *Stopping a payload* below.
* **It is not visible from a dry run.** A dry run returns `planned` before
  reaching the kill switch, since it was never going to claim anything. Do not
  read a dry run's exit 0 as "PAUSE is not working."

### Stopping a payload that is already running

Detached payloads are reachable only through the runner's state directory,
`~/.local/state/workspace-hub/dispatch/<job-id>/`, which holds `child.pid`,
`stdout.log`, `stderr.log` and `status.kv`.

```bash
bash scripts/dispatch/run.sh list
# {"ok":true,"action":"list","count":2,"jobs":[{"job_id":"drain-20260802T023313Z-5bdc00",
#  "issue_ref":"vamseeachanta/deckhand#33","state":"finished","exit_code":0}, ...]}

bash scripts/dispatch/run.sh status --job-id drain-20260802T023313Z-5bdc00
bash scripts/dispatch/run.sh logs   --job-id drain-20260802T023313Z-5bdc00 --tail 50
bash scripts/dispatch/run.sh cancel --job-id drain-20260802T023313Z-5bdc00
```

`cancel` sends `SIGTERM` to the pid in `child.pid` and reports whether it
actually signalled (`"signalled":true|false`) — cancelling an already-finished
job is a normal no-op, not an error, and it never rewrites the recorded outcome.

The full stop is therefore two steps, in this order: `touch PAUSE` to stop new
claims, then `run.sh list` + `run.sh cancel` for anything still in flight.

---

## Binding work

`.claude/dispatch/commands.yaml` maps an issue to the command that issue runs.
**This file does not exist yet**, which is why an armed loop over 1,344 cards
still executes nothing: every card is refused as `no_command`.

```yaml
# .claude/dispatch/commands.yaml
commands:
  vamseeachanta/workspace-hub#3757: >-
    uv run --with pyyaml python scripts/dispatch/reconcile.py --report
  vamseeachanta/digitalmodel#1640: >-
    bash scripts/testing/run-domain-tests.sh orcaflex
```

Rules the loader enforces at **load** time, before anything runs:

* keys must be `owner/repo#N` — a key that could never match a card is an error,
  not a silent no-op, because a typo and a deliberate omission would otherwise
  look identical;
* a value must be a non-empty string. An empty command is not an empty payload:
  the runner would execute nothing, exit 0, and the drain would record a clean
  completion for work that never happened;
* a missing file is **not** an error. It means nothing is bound, and the loop says
  so once per card.

**Why this is manual.** Three designs were available and the module took the
third (`dispatch_pull.py`, "card → command binding"):

1. a `command:` field on the card — destroyed on the next `dispatch.py --write`,
   which rebuilds `.claude/dispatch/<machine>.yaml` wholesale from `route.py`;
2. a per-domain or per-provider template — `domain` is a routing axis, not a
   statement about what the work *is*; one template would fire the same command
   at hundreds of unrelated issues and produce a record for each;
3. an explicit per-issue map kept outside the generated queue — survives
   regeneration, reviewable in a diff, and writing an entry is a deliberate human
   act, which is where the plan-approval gate already lives.

Cards are also skipped as `wip_capped` when the router did not mark them
`wip_eligible`. A *missing* flag counts as capped: an absent field is not
permission.

---

## What to read in the morning

### 1. Did anything actually work?

```bash
uv run --with pyyaml python scripts/dispatch/chain.py \
  --repo vamseeachanta/workspace-hub --records .claude/dispatch/records
```

Two axes, deliberately not merged. The **stage** block says how far cards got
(`queued` → `executing` → `executed`); the **OUTCOMES** block says whether the
work succeeded, from `records.is_success` (`done` *and* `returncode == 0`).
Before that second axis existed, a night that failed every card printed the same
report as a night that completed every card.

Read `UNATTESTED` as its own verdict: the payload is recorded `done` but nobody
observed an exit code, so nobody knows. It is neither a success nor a clean
failure. `not measured here` on `result`/`published` is likewise not a zero —
those need a join this tool does not do.

### 2. What did last night's run do?

The run log is a dated JSONL under `logs/dispatch-pull/` — local only,
`.gitignore`d, so nothing an issue reference could leak reaches this public repo.

```bash
tail -n1 logs/dispatch-pull/$(date -u +%F).jsonl                     # the run_summary line
grep '"status": "failed"' logs/dispatch-pull/$(date -u +%F).jsonl || echo "no failures"
grep -o '"status": "[a-z_]*"' logs/dispatch-pull/$(date -u +%F).jsonl | sort | uniq -c
```

A summary line looks like:

```json
{"apply": false, "counts": {"no_command": 3, "wip_capped": 1341}, "delay_s": 30.0,
 "event": "run_summary", "fetch_rc": 0, "machine": "dev-primary", "max_cards": 5,
 "push_rc": 0, "ready": 1344, "run_id": "df67d02ee2da", "total": 1344, "ts": ...}
```

Statuses are distinct on purpose — they need different actions from you:

| status | meaning | your move |
|---|---|---|
| `ran` | executed and the fence still held; marked done | nothing |
| `failed` | `drain.py` exited nonzero; **not** marked done, stays claimable | read the job's `stderr.log` |
| `paused` | `.claude/dispatch/PAUSE` exists; the run stopped here | remove the sentinel when ready |
| `no_command` | nothing bound in `commands.yaml` | bind it, or leave it — this is the standing state |
| `wip_capped` | the router did not mark the card `wip_eligible` | routing question, not a dispatch one |
| `run_capped` | past this run's `--max-cards` ceiling; never dropped | it will be reconsidered next run |
| `skipped_held` | another host holds a fresh lease | nothing |
| `lost_fence` | superseded mid-run; **not** marked done | expect a re-run |

`fetch_rc` / `push_rc` are in the summary because a failed lease sync leaves this
host's claims invisible to the fleet — the [#3772](https://github.com/vamseeachanta/workspace-hub/issues/3772)
failure mode, and otherwise indistinguishable from a quiet night.

The loop exits nonzero **only** for a card that genuinely failed. `no_command` is
a standing configuration gap across the backlog; alarming on it every poll would
train you to ignore the exit code that reports a real break.

### 3. Was the run refused before it started?

`logs/dispatch-pull/cron-<date>.log` holds the wrapper's own output — dry-run
notice, gate refusals, and the loop's stdout.

---

## Known ceilings

* **`ttl_minutes` (90 by default) is a hard ceiling on a payload.** Nothing beats
  the record's heartbeat while a child runs, so a payload that outlived its TTL
  would have its record expire underneath it, `reconcile.settle` would return the
  issue to `ready`, and the next `prepare` would reclaim it — two payloads, one
  issue. `drain.py` refuses at startup when the longest wait (`--timeout`,
  default 3600 s) is `>=` the TTL, rather than relying on the coincidence that
  3600 < 5400. Raising `--timeout` means raising `--ttl-minutes` with it.
* **`wip_caps.per_machine` is the only cap enforced at claim time** —
  `dev-primary: 3` in `.claude/memory/kanban/routing-rules.yaml`. It counts
  *concurrent live claims* on this machine from every source, so an interactive
  session holding three claims will make the loop's cards refuse.
* **`wip_caps.per_provider` and `budget_pools.*.max_concurrent` bind nowhere at
  claim time.** `route.py` reads them when it proposes an assignment; nothing
  re-checks them when a card is actually claimed. Treat `claude: 4`,
  `gemini: 1`, `codex_pool.max_concurrent: 3` as routing hints, not as
  enforcement.
* **`--max-cards` is a ceiling, not a switch.** There is no value meaning
  "unbounded"; `0` runs none and negatives are rejected. Five cards is ten
  commits pushed to `main` per run, which is what an operator can review in a
  morning.
* **There is no retry loop.** A card that failed stays claimable and is picked up
  by a later run, bounded by that run's own ceiling.

---

## Coexisting with the other crons on this checkout

Two other tasks write this same working tree. Neither fights `dispatch-pull`, but
know why:

* **`git-lock-reaper` (`*/5`)** deletes `.git/index.lock` only when it is both
  older than 10 minutes **and** has no live `git` process. A commit made by
  `drain.py` satisfies neither condition, so it can never be race-reaped.
* **`return-to-main-guard` (`*/30`)** restores the checkout to `main` when it is
  parked off-branch and idle. It refuses to act while a git operation is live or
  staged changes exist, and `drain.py` commits and pushes each card rather than
  leaving long-lived unstaged churn for the guard to stash. The guard's goal —
  the checkout sitting on `main` — is also what this loop wants.

The `:07` minute is chosen to clear the crowded slots: `:00` (`repository-sync`,
`return-to-main-guard`, `git-lock-reaper`), `:11` (`harness-install-doctor`),
`:17` (`equivalence-sentinel`), `:30` (`return-to-main-guard`), `:47`
(`session-curation`), `:50` (`equality-matrix-refresh`).

---

## Changing the schedule

Editing `config/scheduled-tasks/schedule-tasks.yaml` stales the Scheduler
Mutation Surface Guard, because the task catalog is one of the governed inputs to
the identity digest. After any edit, in this order:

```bash
uv run python scripts/cron/build-cron-identity-inventory.py          # regenerate
# copy the new "input_digest" into resolved_dispositions[0].source_digest
#   in config/scheduled-tasks/mutation-surfaces.yaml, with a note saying WHY the
#   #3475 disposition still holds. Never touch resolved_on or pull_request —
#   they are pinned in scheduler_mutation_contract.py:310.
git add -- config/scheduled-tasks/ docs/reports/
uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py \
  --render-html docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html
git add -- docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html
```

Then all four checks CI runs (`.github/workflows/enforcement-gate.yml`):

```bash
uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py
uv run python scripts/cron/build-cron-identity-inventory.py --check
uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py \
  --check-html docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html
uv run python scripts/cron/validate-schedule.py
```

`check-scheduler-mutation-surfaces.py` reads the **git index**, not the working
tree (`check-scheduler-mutation-surfaces.py:88`). Stage your changes first or it
will report the state you had before you edited anything.
