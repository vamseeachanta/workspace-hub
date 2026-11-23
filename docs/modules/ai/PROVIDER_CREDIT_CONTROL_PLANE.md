# Provider-credit control plane (#2665)

The provider-credit control plane keeps Claude/Codex/Gemini fed with safe work
while preserving the user-in-loop plan-approval gate. It is implemented as
four cooperating scripts plus a regression-test suite, all wired into the
existing cron refresh.

## Why this exists

The plan for #2665 documents the operational gap that motivated the work:
weekly utilization for Claude/Codex/Gemini was running well under target
(0.6% / 2.6% / 0.0% in W20), the execution-ready queue for Gemini was empty
while the planning/recon/review backlog was full, and there was no auditable
approval transaction binding "the user clicked Approve" to "implementation
can dispatch".

The control plane solves this without bypassing the plan-first governance
documented in [`docs/plans/README.md`](../../plans/README.md):

- Implementation dispatch ONLY pulls from `status:plan-approved` cards that
  also have a `.planning/plan-approved/<issue>.md` marker.
- Planning/recon/review dispatch runs whenever execution-ready is empty so
  provider credits aren't burnt idling.
- The approval transaction is idempotent, audited, and recoverable; agents
  can run `--dry-run` but never `--mode real` themselves.

## Components

| File | Role |
|---|---|
| `scripts/ai/provider-kanban.py` | Generates `config/ai-tools/provider-kanban.json` + `docs/reports/provider-kanban-dashboard.{md,html}` from `provider-work-queue.json`, `provider-routing-scorecard.json`, and `continuous-planning-pipeline` classification primitives. Static HTML is safe (no `<script>`, no `fetch()`, no secrets). |
| `scripts/ai/provider-kanban-server.py` | Local loopback HTTP server (default `127.0.0.1:7665`). Generates an ephemeral CSRF token at startup, injects it into the served dashboard, and accepts `POST /approve` only with matching token + explicit `user_identity` + `i_understand=yes`. Invokes the approval CLI on behalf of the user. |
| `scripts/ai/approve-provider-plan.py` | Idempotent approval transaction CLI. Per-issue `flock` at `.planning/approval-transactions/<N>.lock`, transaction journal, prepared comment body-file, quarantine marker, label transition, queue refresh, post-mutation verification, atomic marker promotion, and `--resume <txid>` recovery without duplicate side effects. |
| `scripts/ai/provider-dispatch-loop.py` | Safe pull-loop dispatcher with single-writer lease ledger at `logs/ai-provider-dispatch/leases.jsonl`. ace-linux-1 is the configured leader; ace-linux-2 is worker-only unless explicitly promoted. #2519 coexistence preflight aborts if a competing dispatcher uses a different lease contract. |
| `scripts/cron/provider-utilization-refresh.sh` | Existing cron entrypoint; #2665 added one line invoking `provider-kanban.py` plus three fail-closed checks. |
| `scripts/enforcement/require-plan-approval.sh` | Existing pre-commit gate; #2665 added `--require-issue <N>` strict-issue mode. |

## Operating model: weekly credit consumption

```
1. cron refresh runs every N minutes:
     query-quota.sh --refresh
     credit-utilization-tracker.py
     provider-routing-scorecard.py
     provider-work-queue.py        ← emits full_candidates (#2665)
     provider-autolabel.py
     provider-kanban.py            ← regenerates dashboard

2. User opens the static dashboard (read-only):
     open docs/reports/provider-kanban-dashboard.html
     # Approval buttons are visibly DISABLED
     # CLI fallback commands shown in the page

3. To approve a plan, run the local server:
     uv run --no-project python scripts/ai/provider-kanban-server.py
     # Opens 127.0.0.1:7665; ephemeral CSRF token printed to console
     # User clicks Approve in the browser
     # Server POSTs to its own /approve endpoint
     # /approve invokes approve-provider-plan.execute_transaction
     # Marker lands at .planning/plan-approved/<N>.md only after verification

4. Provider-dispatch-loop pulls from execution_ready and planning fallback:
     uv run --no-project python scripts/ai/provider-dispatch-loop.py
     # Runs on ace-linux-1; refuses non-leader hosts unless --promotion-token
     # Creates leases; launches provider work; tracks runs.jsonl
     # Falls back to planning/recon/review when execution_ready is empty

5. Morning QA packet aggregates the run/lease ledger:
     uv run --no-project python scripts/ai/provider-dispatch-loop.py --morning-qa
     # Writes docs/reports/provider-dispatch-morning-qa.md
     # Surfaces completed / running / stale / failed leases + user actions
```

## Approval transaction states

Every approval transaction progresses through phases recorded in
`.planning/approval-transactions/<issue>-<txid>.json`:

| Phase | Meaning | Mutating? |
|---|---|---|
| `preflight` | Live issue fetched, validated, plan + reviews resolved. | No |
| `journal_written` | Transaction record persisted to disk. | No (disk only) |
| `comment_prepared` | Comment body-file written under the tx dir. | No (disk only) |
| `quarantine_written` | Marker written to `.planning/approval-transactions/`. NOT under `plan-approved/`. | No (disk only) |
| `comment_posted` | `gh issue comment --body-file <prepared>` succeeded. | Yes |
| `labels_transitioned` | `status:plan-review` removed, `status:plan-approved` added. | Yes |
| `queue_refreshed` | `provider-work-queue.py` re-ran. | No (regenerates artifact) |
| `verified` | Re-fetched issue confirms label transition + idempotency-keyed comment present. | No |
| `promoted` | Quarantine marker atomically `os.replace()`-ed to `.planning/plan-approved/<N>.md`. | Yes |
| `complete` | Final journal entry; transaction is closed. | No |

### Failure modes & recovery

If anything fails between `comment_posted` and `promoted`, the transaction
journal records the last successful phase and the quarantine marker survives
in `.planning/approval-transactions/`. To recover:

```sh
uv run --no-project python scripts/ai/approve-provider-plan.py \
  --issue <N> --mode real \
  --user-identity <you> --approval-source 'cli' \
  --resume <txid>
```

Resume picks up at the next pending phase using a `phase_order` gate, so:
- No duplicate comment is posted (idempotency check against the original
  comment's idempotency_key embedded in its body).
- No duplicate label flip (re-applying the same label transition is a no-op).
- No duplicate marker promotion (only one final marker can exist).

## Lease ledger & dispatch

Each dispatched lease at `logs/ai-provider-dispatch/leases.jsonl` carries:

| Field | Notes |
|---|---|
| `lease_id` | `L-<issue>-<provider>-<unix_ts>` |
| `issue_number` | The work item |
| `provider` | claude / codex / gemini |
| `machine` | ace-linux-1 / ace-linux-2 / ... |
| `mode` | implementation / planning / recon / review |
| `parent_issue` | `#2519` (Hermes orchestration parent) |
| `idempotency_key` | `<issue>:<provider>:<machine>` |
| `state` | active / completed / stale / failed |
| `created_at` | UTC ISO timestamp |
| `ttl_seconds` | Default 10800 (3h) |
| `expires_at` | created_at + ttl |
| `expected_artifact` | The plan or output path the run should produce |

The ledger is append-only. `expire_stale_leases()` derives stale state from
TTL expiry at read time without mutating prior records — the audit trail
is preserved.

## Single-writer enforcement

- **ace-linux-1** holds the canonical leader role via `flock` on
  `logs/ai-provider-dispatch/leader.lock`. While it holds the lock, no other
  dispatcher can acquire it.
- **ace-linux-2** is worker-only by default. `acquire_leader_lock()` refuses
  to lock unless `promotion_token` is set in the dispatcher config.
- **Promotion handoff** is explicit: the operator must (a) stop the leader's
  dispatch loop so its `flock` releases, then (b) start the promoted machine
  with `--promotion-token <opaque>`. The `flock` itself guarantees
  one-writer-at-a-time across the handoff window — there is no split-brain
  state where both machines accept lease writes.
- **Coexistence preflight** (`#2519`) reads
  `logs/ai-provider-dispatch/competing-dispatcher.marker` and aborts
  fail-closed if it points at a different `leader_lock_path` than the
  current config's. This prevents an independent dispatcher (with its own
  lease ledger contract) from racing the leader-owned one.

## Acceptance criteria mapping

| Plan acceptance criterion | Implementation |
|---|---|
| `provider-work-queue.py` emits both `top_issues` and full candidates | `scripts/ai/provider-work-queue.py:155` (`full_candidates: items`) |
| Report wording: `status:plan-approved`, not `agent:*` | `scripts/ai/provider-work-queue.py:182` |
| Kanban generates JSON + MD + HTML from durable artifacts | `scripts/ai/provider-kanban.py` |
| Hover from durable data, no LLM-only summaries | `provider-kanban.build_hover_summary()` |
| Static HTML disabled buttons + copy/paste commands | `provider-kanban.render_html()` |
| Approval CLI: --dry-run, audited real mode, --resume | `scripts/ai/approve-provider-plan.py` |
| Dispatcher implementation requires both label AND marker | `provider-dispatch-loop.select_execution_ready()` |
| Planning/recon/review fallback when no execution-ready work | `provider-dispatch-loop.select_planning_fallback()` |
| Single-writer lease ledger, ace-linux-1 leader, #2519 preflight | `provider-dispatch-loop.coexistence_preflight + acquire_leader_lock` |
| Morning QA packet | `provider-dispatch-loop.generate_morning_qa()` |
| Provider refresh cron integrates Kanban gen + fail-closed checks | `scripts/cron/provider-utilization-refresh.sh:30,49-51` |

## Testing

Run the full acceptance suite:

```sh
uv run --no-project python -m pytest \
  tests/ai/test_provider_kanban.py \
  tests/ai/test_provider_kanban_server.py \
  tests/ai/test_approve_provider_plan.py \
  tests/ai/test_provider_dispatch_loop.py \
  tests/analysis/test_provider_work_queue.py \
  tests/analysis/test_continuous_planning_pipeline.py \
  tests/enforcement/test_require_plan_approval.py \
  -v
```

All tests use injectable runners or in-process httpd; no test touches the
live `gh` CLI or the real `.planning/plan-approved/` directory.

## Related issues

- [#2665](https://github.com/vamseeachanta/workspace-hub/issues/2665) — this control plane (this doc)
- [#2519](https://github.com/vamseeachanta/workspace-hub/issues/2519) — parent Hermes orchestration; dispatch coexistence contract
- [#1838](https://github.com/vamseeachanta/workspace-hub/issues/1838) — AI credit governance / horses-for-courses routing
