# Queue Migration To Labels

Issue: [#3999](https://github.com/vamseeachanta/workspace-hub/issues/3999)

The active queue is GitHub labels only. Local `.claude/work-queue/` and
`.planning/` files remain historical evidence, GSD planning state, or archived
records; they are not intake, routing, dispatch, approval, or completion truth.

## Active Label Axes

| Axis | Purpose |
|---|---|
| `dispatch:*` | Queue state. `dispatch:ready` is the intake queue. |
| `lane:*` | Planned execution lane, for example `lane:codex` or `lane:claude`. |
| `ai:*` | Provider override consumed by dispatch routing. |
| `decision:*` | Owner decision category for triage and PR labelling. |

Table 1. Queue state is carried by issue labels, not local markdown queue files.

## Retired Readers And Writers

| Retired reader/writer | Previous behavior | Replacement |
|---|---|---|
| `scripts/ace wrk list/show` | Read `.claude/work-queue/pending/*.md`. | Reads live GitHub issues with `dispatch:ready`; `show` accepts an issue number. |
| `scripts/strategic/strategic_score.py` default mode | Read `.claude/work-queue/pending/*.md`. | Reads live GitHub issues with `dispatch:ready` and scores their `lane:*`, `ai:*`, `decision:*`, `cat:*`, `domain:*`, and `priority:*` labels. `--dir` remains a fixture-only legacy path. |
| `scripts/strategic/strategic_classify.py` | Looked up `WRK-*` files in `.claude/work-queue/{pending,archived}`. | Reads a GitHub issue by number and normalizes labels for classification. |
| `scripts/memory/compact-memory.py --work-queue-root` | Used local done-WRK files as stale-memory evidence. | The option is compatibility-only; local WRK files no longer evict bullets. |
| `scripts/memory/eval-memory-quality.py --work-queue-root` | Reported done-WRK percentages from local archive files. | Metric remains for schema compatibility and reports `0.0`; labels are queue truth. |
| `.claude/work-queue/scripts/generate-index.py` | Generated `.claude/work-queue/INDEX.md` from local buckets. | Retired no-op; use `notes/agent-work-queue.md` from `scripts/refresh-agent-work-queue.py`. |
| `scripts/refresh-agent-work-queue.py` | Generated a queue from `agent:*` and `priority:*` labels. | Generates from `dispatch:ready` x `lane:*`; preserves the label-axis model used by the label PRs. |
| `scripts/operations/compliance/{audit_wrk_location,normalize_work_queue_metadata,validate_work_queue_schema}.sh` | Audited or mutated local WRK markdown. | Retired no-op compatibility entry points. |
| `scripts/session/{refresh-context,repo-map-context,data-intelligence-context}.sh` and `scripts/session/subagent-checkpoint.py` local auto-detect paths | Read or wrote active WRK files for context handoff. | Retired local auto-detect/state writes; callers must use issue labels or explicit non-queue inputs. |
| `scripts/planning/ensemble-plan.sh` | Read and wrote local WRK plan frontmatter. | Retired no-op; issue plans live in GitHub/docs plan surfaces. |
| `scripts/cron/update_portfolio_signals.py` L2 counts | Counted recent local WRK archive files. | Local archive count is retired and reports zero; provider signals continue independently. |
| `scripts/cron/comprehensive-learning-nightly.sh` release-scan auto-commit | Staged new `.claude/work-queue` files. | Stages release-scan state only; no local queue files. |
| `.planning/plan-approved/*` as queue/approval trigger | Local marker files were treated as execution readiness by older gates. | Readiness is represented by GitHub labels and task authority; new files under `.planning/` are blocked by `scripts/enforcement/check-retired-queue-paths.py` except archived historical records. |
| `scripts/ai/provider-dispatch-loop.py` | Required both `status:plan-approved` and an `approval_marker` field. | Uses `status:plan-approved`; retired markers are ignored. |
| `scripts/telegram_dispatch/policy.py` | Blocked implementation dispatch without `.planning/plan-approved/<issue>.md`. | Uses `status:plan-approved` plus readiness and lease checks. |
| `scripts/operations/linux-cron-issue-orchestrator.py` | Required `--plan-marker-dir` marker files. | Keeps `--plan-marker-dir` as ignored compatibility input; dispatch readiness is label-based. |
| `scripts/ai/approve-provider-plan.py` | Wrote quarantine markers and promoted them into `.planning/plan-approved/`. | Posts the approval comment, transitions GitHub labels, refreshes queue data, and writes no approval marker. |
| `.github/workflows/enforcement-gate.yml` marker-label-parity job | Validated newly added approval markers against GitHub labels. | Removed because new marker files are rejected by the retired-path guard. |
| `scripts/ai/build-orca-kanban.py` | Split `status:plan-approved` issues into ready vs marker-drift lanes. | Treats `status:plan-approved` as ready; local markers are ignored. |
| `scripts/data/document-index/phase-f-gap-wrk-generator.py` | Wrote generated local WRK files under `.claude/work-queue/pending/`. | Non-dry-run local writes fail closed; `--dry-run` previews GitHub issue candidates. |

Table 2. Local queue readers either read labels now or are retired.

## Existing Item Mapping

| Existing local signal | Label mapping |
|---|---|
| `.claude/work-queue/pending/<WRK>.md` | Open GitHub issue with `dispatch:ready` and the applicable `lane:*` / `decision:*` labels. |
| `.claude/work-queue/working/<WRK>.md` | GitHub issue with `dispatch:active` when that state label exists; otherwise current execution is represented by a dispatch claim record plus issue labels. |
| `.claude/work-queue/done/<WRK>.md` | GitHub issue with `dispatch:done` after reconcile support creates that label; historical local files remain archive evidence only. |
| `.planning/plan-approved/<issue>.md` | No new marker file. The issue's owner-visible labels and comments carry approval/decision context. |
| `.planning/archive/**` or `.claude/work-queue/_archive/**` | Historical evidence; not queue input. |

Table 3. Migration preserves historical files and moves live routing to labels.

New files under `.claude/work-queue/` or `.planning/` are rejected unless they
land under an archive directory. This keeps historical content readable without
reintroducing local queues.

The bulk migration/archive script for moving existing live local records into
`_archive/2026-10-legacy-queue/` is deferred from this part-1 PR. Until that
script lands, historical files stay in place and active tooling must ignore
them.
