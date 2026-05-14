# Plan for #2665: provider-credit approval dashboard and dispatch gates

> **Status:** plan-approved; user approved #2665 via GitHub label on 2026-05-12, local approval marker recorded at `.planning/plan-approved/2665.md`
> **Complexity:** T3
> **Date:** 2026-05-12
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2665
> **Review artifacts:** scripts/review/results/2026-05-12-plan-2665-claude.md | scripts/review/results/2026-05-12-plan-2665-codex.md | scripts/review/results/2026-05-12-plan-2665-gemini.md | scripts/review/results/2026-05-12-plan-2665-disagreement.md | scripts/review/results/2026-05-12-plan-2665-focused-review-a.md | scripts/review/results/2026-05-12-plan-2665-focused-review-b.md | scripts/review/results/2026-05-12-plan-2665-final-synthesis.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/cron/provider-utilization-refresh.sh` already refreshes quota snapshots and regenerates provider utilization, routing scorecard, provider work queue, and provider autolabel artifacts. This is the correct refresh entrypoint to extend rather than creating a separate scheduler.
- Found: `scripts/ai/provider-work-queue.py` already builds provider queues from live GitHub issues and the routing scorecard, but it emits only `top_issues: items[:8]` per provider. #2665 will extend it to emit a non-truncated `all_issues`/`full_candidates` provider field and will have `provider-kanban.py` consume that shared artifact instead of duplicating provider-routing logic.
- Found: `scripts/enforcement/require-plan-approval.sh` already recognizes `.planning/plan-approved/*.md` as approval evidence for implementation commits, but the evidence check is broad/recent-marker oriented rather than issue-specific. #2665 will add an issue-specific strict path (`--require-issue <NNN>` / staged-file issue inference where feasible) and regression tests so a marker for one issue cannot satisfy another issue’s implementation gate. In strict mode, missing or ambiguous issue inference must fail closed and must never fall back to broad/recent-marker evidence.
- Found: `scripts/operations/workstation-status.sh` and `scripts/operations/workstation-dispatch.sh` provide a starting workstation registry/probe/dispatch layer. This issue should consume/extend those artifacts rather than inventing an unrelated machine routing model.
- Found: `scripts/ai/continuous-planning-pipeline.py` already provides plan discovery, review discovery, review cleanliness checks, marker quality checks, approval-candidate/execution-ready lane classification, and dispatch/review lanes. #2665 must reuse or import its plan/review/marker/lane classification primitives, or explicitly wrap its JSON output, rather than creating a second divergent readiness classifier.
- Gap: no implementation currently provides the provider-credit Kanban dashboard UX, local approval endpoint, approval transaction writer, cross-provider lease/run ledger, provider-credit dispatch pull loop, or morning QA packet generator.

### Standards
| Standard | Status | Source |
|---|---|---|
| Workspace issue-planning gate | active | `docs/plans/README.md` lines 15-27, 105-116 |
| Control-plane provider adapter contract | active | `docs/standards/CONTROL_PLANE_CONTRACT.md` lines 18-35 |
| AI review routing policy | active | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` lines 11-27 |
| Hard-stop policy | active but older/narrower than current AGENTS.md memory | `docs/standards/HARD-STOP-POLICY.md`; `AGENTS.md` and `docs/plans/README.md` are stricter for current work |

### LLM Wiki pages consulted
- N/A — this is harness / AI orchestration work, not engineering domain content promotion.

### Documents consulted
- Issue #2665 — requests a Kanban approval/control surface to reduce wasted provider credits while preserving user approval gates.
- Issue #1838 — establishes the parent provider-credit governance problem: Claude absorbs most work, Gemini/Codex capacity is underused, and routing needs a cross-provider matrix.
- Issue #2519 — establishes Hermes-led provider + workstation dispatch as parent orchestration work, including provider telemetry reconciliation, workstation readiness, dispatch ledger, and plan-approved gate.
- `docs/reports/provider-utilization-weekly.md` — current week utilization is materially under target: Claude 0.6%, Codex 2.6%, Gemini 0.0%, with all three underutilization alerts.
- `docs/reports/provider-routing-scorecard.md` — current recommended provider order is `gemini, codex, claude`; Codex/Gemini are highest priority, Claude is high priority but should be reserved for synthesis/review.
- `docs/reports/provider-work-queue.md` — current queue has execution-ready candidates for Claude and Codex but none for Gemini, proving the missing feedstock/approval/dispatch loop rather than lack of backlog.
- `docs/BUSINESS_BRAIN.md` — hard rule: harness throughput is primary; provider credits should be consumed by keeping plan prep, review, approved execution, and reconciliation lanes fed.

### Gaps identified
- No durable Kanban-lane JSON schema exists for issue cards with lane, approval readiness, hover summary, provider route, machine route, lease state, and validation state.
- No static/served HTML dashboard exists that renders provider utilization, issue lanes, hover summaries, and approval controls from durable artifacts.
- No approval CLI or local approval endpoint exists to validate live GitHub issue state, canonical plan file, latest review artifacts, explicit user approval intent, per-issue approval transaction lock, quarantine marker, per-issue approval marker atomic promotion, label transition, GitHub comment body-file, queue refresh, and idempotent resume as one auditable transaction with defined recovery states.
- No single-writer dispatcher lease ledger exists to prevent double-dispatch of the same issue to Claude/Codex/Gemini across ace-linux-1/ace-linux-2.
- No continuous-provider loop exists that safely runs planning/recon/review when execution-ready work is empty, then dispatches implementation only from `status:plan-approved`.
- No morning QA packet exists to summarize completed/running/blocked provider work with tests, changed files, artifacts, and recommended user actions.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-12T12:23:22Z via `gh issue view`):
- `#2665` — OPEN — `feat(kanban): provider-credit approval dashboard and dispatch gates`; labels: `enhancement`, `priority:high`, `cat:ai-orchestration`, `cat:harness`, `domain:agent-cost-tracking`.
- `#1838` — OPEN — `AI credit utilization governance — horses-for-courses routing with Gemini as first-class provider`.
- `#2519` — OPEN — `feat(hermes): orchestrate AI provider usage and workstation dispatch`.

**File existence** (verified 2026-05-12T12:26:43Z):
- EXISTS: `docs/reports/provider-utilization-weekly.md`
- EXISTS: `docs/reports/provider-routing-scorecard.md`
- EXISTS: `docs/reports/provider-work-queue.md`
- EXISTS: `scripts/cron/provider-utilization-refresh.sh`
- EXISTS: `scripts/ai/provider-work-queue.py`
- EXISTS: `docs/plans/README.md`
- EXISTS: `docs/standards/CONTROL_PLANE_CONTRACT.md`
- EXISTS: `docs/standards/AI_REVIEW_ROUTING_POLICY.md`
- EXISTS: `scripts/enforcement/require-plan-approval.sh`
- MISSING (new — this plan creates): `scripts/ai/provider-kanban.py`
- MISSING (new — this plan creates): `scripts/ai/provider-kanban-server.py`
- MISSING (new — this plan creates): `scripts/ai/approve-provider-plan.py`
- MISSING (new — this plan creates): `scripts/ai/provider-dispatch-loop.py`
- MISSING (new — this plan creates): `tests/ai/test_provider_kanban.py`
- MISSING (new — this plan creates): `tests/ai/test_provider_kanban_server.py`
- MISSING (new — this plan creates): `tests/ai/test_approve_provider_plan.py`
- MISSING (new — this plan creates): `tests/ai/test_provider_dispatch_loop.py`

**Line excerpts**:

`docs/reports/provider-utilization-weekly.md`:
```text
9|## 2026-W20 (current)
13|| claude | 8 | 247 | 0.6% | activity_vs_recent_peak | n/a | quota unavailable from unavailable; using activity fallback |
14|| codex | 51 | 1952 | 2.6% | quota | 2.6% | week_messages/weekly_limit from history.jsonl |
15|| gemini | 1 | 1 | 0.0% | activity_vs_recent_peak | 0.0% | today_messages/daily_limit from estimated; using activity fallback |
81|## Current-week underutilization alerts
83|- claude at 0.6% (activity_vs_recent_peak)
84|- codex at 2.6% (quota)
85|- gemini at 0.0% (activity_vs_recent_peak)
```

`docs/reports/provider-routing-scorecard.md`:
```text
5|Recommended provider order: gemini, codex, claude
50|### Preferred work
51|- bounded implementation
52|- test writing and repair
53|- mechanical cleanup/refactors
76|### Preferred work
77|- batched research/recon
78|- risk enumeration
79|- competitor/standards scans
```

`docs/reports/provider-work-queue.md`:
```text
7|Execution-ready means the issue already carries `status:plan-approved` or an explicit agent label.
12|- Execution-ready candidates: 7
29|- Execution-ready candidates: 5
46|- Execution-ready candidates: 0
```

`scripts/cron/provider-utilization-refresh.sh`:
```text
21|  bash scripts/ai/assessment/query-quota.sh --refresh --log
22|  uv run --no-project python scripts/ai/credit-utilization-tracker.py \
26|  uv run --no-project python scripts/ai/provider-routing-scorecard.py
27|  uv run --no-project python scripts/ai/provider-work-queue.py
28|  uv run --no-project python scripts/ai/provider-autolabel.py
```

`scripts/ai/provider-work-queue.py`:
```text
63|def has_plan_approved(issue: dict[str, Any]) -> bool:
64|    return "status:plan-approved" in label_names(issue)
80|def suggested_provider(issue: dict[str, Any]) -> tuple[str, str]:
89|    if any(term in haystack for term in STRATEGY_TERMS):
90|        return "claude", "strategy/workflow/architecture language"
91|    if any(term in haystack for term in IMPLEMENT_TERMS):
92|        return "codex", "implementation/test/fix language"
93|    if any(term in haystack for term in RESEARCH_TERMS):
94|        return "gemini", "research/triage/audit language"
```

`docs/plans/README.md`:
```text
15|## The Workflow (Step by Step)
21|4. ADVERSARIAL REVIEW — Route to 2+ AI providers; revise if MAJOR verdict
22|5. POST TO GITHUB   — Comment plan on issue, label status:plan-review
23|6. HARD STOP        — Wait for user approval (never self-approve)
24|7. USER APPROVES    — Swap label to status:plan-approved
105|### Step 5: Post and Label
107|1. Post the completed plan as a GitHub issue comment
108|2. Apply label: `gh issue edit NNN --add-label "status:plan-review"`
109|3. **STOP** — do NOT write any implementation code
111|### Step 6: User Approval
113|The user (never the implementing agent) approves the plan:
114|- `gh issue edit NNN --remove-label "status:plan-review" --add-label "status:plan-approved"`
115|- Creates marker: `.planning/plan-approved/NNN.md`
```

**Gap proofs**:
```text
$ rg -i "Approve Plan|kanban.*dashboard|provider-credit approval|approval dashboard" scripts docs tests config --glob '*.py'
<no output>
```
This confirms no Python approval/dashboard implementation currently exists.

**Reproduction proofs**:
- N/A — issue #2665 is a new harness/control-plane feature request, not a runtime failure report.

**Distinct source count:** 11 (issue #2665, parent issues #1838/#2519, provider reports, queue generator, refresh script, planning guide, review policy, control-plane contract, enforcement script, BUSINESS_BRAIN).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-12-issue-2665-provider-credit-approval-dashboard-dispatch-gates.md` |
| Tests — Kanban artifact | `tests/ai/test_provider_kanban.py` |
| Tests — local approval server | `tests/ai/test_provider_kanban_server.py` |
| Tests — approval transaction | `tests/ai/test_approve_provider_plan.py` |
| Tests — dispatch/lease loop | `tests/ai/test_provider_dispatch_loop.py` |
| Implementation — Kanban/dashboard generator | `scripts/ai/provider-kanban.py` |
| Implementation — local approval server | `scripts/ai/provider-kanban-server.py` |
| Implementation — approval transaction CLI | `scripts/ai/approve-provider-plan.py` |
| Implementation — continuous pull dispatcher | `scripts/ai/provider-dispatch-loop.py` |
| Implementation — refresh integration | `scripts/cron/provider-utilization-refresh.sh` |
| Generated JSON | `config/ai-tools/provider-kanban.json` |
| Generated HTML | `docs/reports/provider-kanban-dashboard.html` |
| Generated Markdown | `docs/reports/provider-kanban-dashboard.md` |
| Dispatch lease ledger | `logs/ai-provider-dispatch/leases.jsonl` |
| Dispatch run ledger | `logs/ai-provider-dispatch/runs.jsonl` |
| Morning QA packet | `docs/reports/provider-dispatch-morning-qa.md` |
| Approval markers | `.planning/plan-approved/<issue>.md` |
| Plan review — Claude | `scripts/review/results/2026-05-12-plan-2665-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-12-plan-2665-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-12-plan-2665-gemini.md` |

---

## Deliverable

A repo-tracked provider-credit control plane that renders a Kanban HTML dashboard with hover summaries and gated approval buttons, validates/records plan approvals through an explicit human-operated local endpoint/CLI transaction, and runs a safe single-writer provider pull loop that keeps Claude/Codex/Gemini fed without bypassing plan-first governance.

---

## Operating Model: stop wasting weekly provider usage

The fix is not “make agents run continuously” in an open-ended way. The practical operating model is a governed pull system:

```text
refresh telemetry
  -> refresh full Kanban/provider queue from live issues, plans, reviews, workstation status
  -> serve dashboard locally for human approval actions
  -> if plan-approved implementation exists: dispatch bounded execution with single-writer lease
  -> else if plan-review candidates exist: surface approval cards and review gaps
  -> else: spend credits on planning/recon/adversarial review feedstock
  -> monitor leases and collect artifacts
  -> produce morning QA packet
  -> refill queue
```

Usage targets for this issue’s implemented workflow:
- By Wednesday noon each week: any provider under 25% reported utilization must receive planning/recon/review packets unless blocked by quota/auth/tool failure.
- By Friday noon: any provider under 60% reported utilization must receive additional safe work packets, with Codex prioritized for bounded TDD/refactor/test repair and Gemini for batched research/recon/review.
- Last 24 hours before reset: consume remaining provider headroom on non-mutating recon/review/plan-hardening if no approved implementation queue exists.

Hard boundaries:
- Implementation dispatch only from `status:plan-approved` plus `.planning/plan-approved/<issue>.md` marker.
- User approval is never performed by cron, provider workers, Hermes autonomous dispatch, or a generic delegated person. Real approval mode requires the user’s explicit action through `provider-kanban-server.py` or an explicit CLI invocation with user identity/confirmation artifact; agents may run only `--dry-run` and may post approval requests for the user. Local UI mechanics are only a transport for the user action, not broader approval authority.
- Planning/recon/review packets may run without implementation approval because they are non-mutating feedstock work.
- The dispatcher has one lease-writing leader on ace-linux-1 by default. ace-linux-2 is worker-only: it may execute jobs only after ace-linux-1/Hermes leader creates a lease and assignment. ace-linux-2 must not originate dispatch, write leases, or launch implementation work unless an explicit single-writer promotion handoff disables ace-linux-1 lease writes first.
- #2665 extends parent #2519: Hermes remains the orchestration authority, while this issue adds the Kanban approval surface, issue-specific approval transaction, shared lease ledger contract, and safe pull-loop implementation. Before writing leases or launching implementation, the loop must run a #2519 coexistence preflight: detect any active Hermes/provider dispatcher, verify it shares the same ace-linux-1 leader lock and lease ledger contract, and abort fail-closed if another independent lease writer is active. Independent competing lease writers are forbidden.

---

## Pseudocode

```text
function build_provider_kanban(inputs):
    load provider-utilization-weekly.json, provider-routing-scorecard.json, provider-work-queue.json metadata
    require provider-work-queue.json to expose full non-truncated provider candidates (`all_issues` / `full_candidates`)
    if full candidates are unavailable, fail with migration error instead of silently using top_issues[:8]
    load workstation-status --json plus workstation registry/dispatch capabilities
    discover canonical plan path from docs/plans index and filename convention
    discover latest review artifacts for each issue plan
    classify each issue into lane: planning_feedstock, plan_review, execution_ready, running_leased, qa_closeout, blocked
    compute approval_ready only if live issue open, plan exists, latest reviews acceptable, no MAJOR/FAIL/UNAVAILABLE pending, no stale plan-review drift
    compute hover summary from durable title, labels, plan summary, risks, validation, provider route, machine route; do not use transient LLM-only summaries
    write config/ai-tools/provider-kanban.json
    render docs/reports/provider-kanban-dashboard.md and provider-kanban-dashboard.html
    in static HTML mode, render disabled approval buttons and copy/paste dry-run commands only
    when served by provider-kanban-server.py, enable buttons only after loopback CSRF/session metadata is injected
```

```text
function approve_provider_plan(issue_number, dry_run, user_identity, approval_source, confirmation_token):
    fetch live GitHub issue JSON for issue_number
    fail unless issue is OPEN and has status:plan-review
    fail unless user_identity and approval_source identify explicit user approval intent
    fail real mode unless invoked by local approval server or explicit TTY/user confirmation; provider workers and cron may only dry-run
    acquire per-issue approval lock .planning/approval-transactions/<issue_number>.lock before any mutating step
    re-fetch live GitHub issue JSON after acquiring the lock
    fail if another active transaction exists for issue_number unless --resume <txid> is supplied
    resolve canonical docs/plans file and verify it exists in the working tree
    parse latest review artifacts for plan issue and fail on MAJOR, FAIL, UNAVAILABLE, or pending latest required review
    prepare approval comment file on disk and transaction journal entry before mutation
    if dry_run:
        emit planned transaction JSON and exit without marker/label/comment writes
    write pending transaction journal .planning/approval-transactions/<issue_number>-<txid>.json
    write quarantine marker .planning/approval-transactions/<issue_number>-<txid>.marker.pending.md (not under plan-approved)
    gh issue comment issue_number --body-file <prepared_comment_path>
    gh issue edit issue_number --remove-label status:plan-review --add-label status:plan-approved
    run provider-utilization refresh or provider-work-queue refresh
    verify live labels, comment presence/idempotency key, and regenerated queue
    atomically promote quarantine marker to .planning/plan-approved/<issue_number>.md only after verification succeeds
    verify final marker content and issue-specific plan gate result
    on partial failure, keep marker quarantined, write recovery state to .planning/approval-transactions/<issue_number>-<txid>.json, and require --resume <txid> to complete pending actions without duplicate comments/labels
    emit transaction JSON with all changed artifacts and recovery status
```

```text
function provider_dispatch_loop(mode, max_jobs, provider_filter):
    assert #2519 coexistence preflight passes and no competing dispatcher is active
    assert ace-linux-1/Hermes leader owns the single lease-writer role via local flock and leader-state file
    reject lease writes and dispatch origination on ace-linux-2 unless explicit promotion handoff disables ace-linux-1 writes first
    refresh provider telemetry, full Kanban JSON, and workstation-status JSON
    load active leases and expire stale leases after TTL with explicit state
    if execution_ready lane has candidates:
        choose highest priority candidates by provider headroom, issue priority, machine readiness, stale age
            create atomic lease record keyed by issue/provider with machine, idempotency key, expected artifact, expiry, and parent #2519 dispatch relation
        launch provider-specific prompt/command in approved worktree or emit prompt packet for worker execution
        if selected machine is non-leader, send leader-created assignment; non-leader never originates dispatch
    else:
        choose non-mutating planning/recon/review packets to create feedstock
        create lease marked planning_only/recon_only/review_only
    monitor run outputs and update logs/ai-provider-dispatch/runs.jsonl
    enforce Wednesday/Friday/reset-window utilization policies when selecting planning/recon/review fallback packets
    generate morning QA summary with completed/running/blocked/tests/artifacts/recommended actions
```

```text
function render_hover_card(issue_card):
    show issue number/title/url
    show labels/status/lane/provider/machine
    show one-paragraph plan summary if plan exists, otherwise issue summary
    show risk/unknowns from plan or default risk classifier
    show tests/validation from plan TDD table or required next action
    show approval blockers or enabled Approve Plan button
```

```text
function provider_utilization_refresh_cron():
    run quota/utilization, routing scorecard, provider-work-queue, provider-autolabel
    run provider-kanban.py
    fail closed unless all existing provider outputs exist
    fail closed unless config/ai-tools/provider-kanban.json exists
    fail closed unless docs/reports/provider-kanban-dashboard.md exists
    fail closed unless docs/reports/provider-kanban-dashboard.html exists
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/ai/provider-kanban.py` | Build provider Kanban JSON plus static Markdown/HTML dashboard from existing provider, full live issue, review, workstation artifacts, and `continuous-planning-pipeline.py` plan/review/marker/lane primitives. |
| Create | `scripts/ai/provider-kanban-server.py` | Local loopback approval server that serves the dashboard with ephemeral CSRF token and calls the approval CLI only after explicit user action. |
| Modify | `scripts/ai/continuous-planning-pipeline.py` | Expose or document reusable plan/review/marker/lane classification primitives if current function boundaries are not directly consumable by `provider-kanban.py`; avoid duplicate readiness logic. |
| Create | `scripts/ai/approve-provider-plan.py` | Idempotent approval CLI used by the local dashboard endpoint and manual user invocation; dry-run is allowed for agents, real mode requires explicit user identity/confirmation, per-issue lock, and recovery journal. |
| Create | `scripts/ai/provider-dispatch-loop.py` | Safe ace-linux-1/Hermes-leader pull-loop dispatcher that launches only plan-approved implementation and otherwise launches planning/recon/review feedstock; ace-linux-2 is worker-only unless promoted through explicit single-writer handoff. |
| Modify | `scripts/ai/provider-work-queue.py` | Emit full non-truncated provider candidate lists for downstream Kanban/dispatcher consumers and correct report wording so execution-ready means `status:plan-approved` only. |
| Modify | `scripts/enforcement/require-plan-approval.sh` | Add issue-specific strict approval checking so `.planning/plan-approved/<other-issue>.md` cannot satisfy unrelated implementation commits. |
| Modify | `scripts/cron/provider-utilization-refresh.sh` | Add Kanban/dashboard generation after provider queue generation plus explicit fail-closed checks for all three Kanban outputs. |
| Create | `tests/ai/test_provider_kanban.py` | TDD coverage for full-candidate lane classification, hover summaries, approval gating, machine-route inclusion, and HTML rendering. |
| Create | `tests/ai/test_provider_kanban_server.py` | TDD coverage for local-only endpoint binding, CSRF token enforcement, no secret emission in static reports, and refusal without explicit user approval intent. |
| Create | `tests/ai/test_approve_provider_plan.py` | TDD coverage for live-state validation, user-confirmation/auth boundary, dry-run vs real mutation, recovery journal, body-file comment generation, and idempotent retry using fixtures/mocks; no network calls in unit tests. |
| Create | `tests/ai/test_provider_dispatch_loop.py` | TDD coverage for lease/idempotency behavior, flock leader lock, ace-linux-2 write refusal unless promoted, and planning-only fallback. |
| Modify | `tests/analysis/test_provider_work_queue.py` | Regression coverage for full candidate emission and corrected execution-ready report wording using the existing provider-work-queue test location. |
| Modify | `tests/analysis/test_continuous_planning_pipeline.py` | Regression coverage that existing plan/review/marker/lane classification primitives remain stable for provider Kanban reuse. |
| Modify/Create | `tests/enforcement/test_require_plan_approval.py` | Regression coverage for issue-specific marker matching and rejection of unrelated approval markers. |
| Create | `tests/fixtures/ai/provider_kanban/issues.json` | Fixture issue set with more than 8 candidates per provider to prove the dashboard is not truncated by `top_issues`. |
| Create | `tests/fixtures/ai/provider_kanban/plans/` | Minimal canonical plan files for approval-ready and blocked examples. |
| Create | `tests/fixtures/ai/provider_kanban/reviews/` | APPROVE, MINOR, MAJOR, UNAVAILABLE, and pending review examples. |
| Create | `tests/fixtures/ai/provider_kanban/workstations.json` | Reachable, offline, missing-auth, and stale-repo machine examples. |
| Create | `docs/reports/provider-kanban-dashboard.html` | Generated user approval dashboard with hover cards. Static file renders visible disabled approval buttons plus copy/paste dry-run/approval commands; real button wiring is injected only when served by `provider-kanban-server.py` on loopback with ephemeral token. |
| Create | `docs/reports/provider-kanban-dashboard.md` | Generated text fallback for CLI/non-browser review with explicit copy/paste dry-run and approval commands. |
| Create | `config/ai-tools/provider-kanban.json` | Machine-readable Kanban state consumed by dashboard and dispatcher. |
| Create | `docs/modules/ai/PROVIDER_CREDIT_CONTROL_PLANE.md` | User docs for weekly credit consumption, local approval server, approval transaction recovery, dispatch loop, leader lock, parent #2519 relationship, and failure modes. |
| Update | `docs/plans/README.md` | Add this canonical plan to the plan index. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_kanban_groups_issues_by_lane_provider_and_machine` | Issues are assigned to planning, plan-review, execution-ready, running, QA, and blocked lanes from labels/reviews/leases/machine readiness. | Fixture issue set with mixed labels, workstation states, and lease records. | Deterministic lane counts and provider/machine grouping. |
| `test_continuous_planning_pipeline_exports_reusable_readiness_primitives` | Provider Kanban consumes existing plan/review/marker/lane classification instead of maintaining divergent readiness logic. | Fixture issues/plans/reviews/markers run through continuous-planning-pipeline primitive or JSON wrapper. | Kanban lane/review readiness matches continuous-planning-pipeline output for shared fields. |
| `test_provider_work_queue_emits_full_candidates_and_top_issues` | Queue generator preserves readable `top_issues` while exposing non-truncated downstream candidates. | Fixture with 12 candidates for one provider. | JSON contains all 12 in full candidate field and 8 in `top_issues`. |
| `test_provider_work_queue_report_says_plan_approved_only` | Generated report wording cannot imply `agent:*` labels are execution approval. | Queue fixture with agent label but no `status:plan-approved`. | Markdown states execution-ready requires `status:plan-approved`; item is not ready. |
| `test_kanban_uses_full_issue_candidate_set_not_top_issues_truncation` | Dashboard cannot silently omit backlog because provider-work-queue readable view emits only top 8. | Fixture with 12 approval candidates for one provider and a queue artifact with full candidates plus 8 top issues. | Kanban JSON contains all 12 candidates or explicitly reports skipped candidates with reason. |
| `test_hover_summary_includes_plan_risk_tests_and_route` | Hover card content is sourced from durable issue/plan/review/workstation data. | Issue with plan sections, review artifacts, and workstation route. | Summary includes title, labels, plan summary, risks, tests, provider route, machine readiness. |
| `test_approve_button_disabled_when_reviews_missing_or_major` | UI state never enables approval if latest valid review is missing, MAJOR, FAIL, UNAVAILABLE, or pending. | Fixture plan-review issues with review variations. | `approval_ready=false` plus blocker reasons. |
| `test_approve_button_enabled_only_for_open_plan_review_issue_with_plan_and_clean_reviews` | Approval readiness requires live issue open, canonical plan path, acceptable reviews, and served-localhost explicit-user-action mode. | Fixture issue with `status:plan-review`, plan file, APPROVE/MINOR reviews, local server metadata and user-action metadata. | `approval_ready=true` and button/action metadata present. |
| `test_render_static_html_contains_no_secrets_and_no_external_mutation_by_default` | Dashboard is safe static output; mutation occurs through local loopback endpoint or CLI, not hidden JS/secrets. | Generated HTML fixture. | No tokens/env secrets; approval command is explicit/auditable; buttons disabled outside served localhost mode. |
| `test_local_approval_endpoint_requires_loopback_csrf_and_user_intent` | HTML button can perform a real approval transaction only through the local approval server. | Served dashboard request with/without token/user intent. | POST without token/user intent fails; valid POST calls approval CLI dry-run/real path as configured. |
| `test_approve_provider_plan_dry_run_reports_exact_transaction` | Approval CLI dry-run validates all preconditions and emits planned label/comment/marker/refresh actions. | Mocked GitHub issue JSON and fixture reviews. | JSON transaction with no marker/label/comment mutation beyond temp output. |
| `test_approve_provider_plan_real_mode_requires_user_confirmation` | Agents/cron/delegated processes cannot self-approve by invoking real mode silently. | Non-TTY/no user confirmation invocation. | Non-zero exit; no marker/label/comment writes. |
| `test_approve_provider_plan_writes_comment_body_file_before_mutation` | `gh issue comment --body-file` always receives an existing prepared file. | Approved fixture issue. | Comment body file exists before mocked `gh issue comment` call. |
| `test_approve_provider_plan_serializes_concurrent_approvals_per_issue` | Two real-mode approval attempts cannot duplicate side effects. | Two concurrent invocations for one issue. | Exactly one transaction mutates; second exits as duplicate/in-progress or resumes safely. |
| `test_approve_provider_plan_resume_race_is_serialized` | Resume and approve cannot race into duplicate comments/markers. | Active recovery journal plus concurrent resume/approve. | Per-issue lock serializes operations and idempotency key prevents duplicate comment. |
| `test_approve_provider_plan_promotes_marker_only_after_verification` | Real approval never exposes `.planning/plan-approved/<issue>.md` until comment, label, queue refresh, and verification succeed. | Approved fixture issue with mocked successful mutations. | Pending marker is promoted atomically only after verification; final marker includes required fields. |
| `test_approve_provider_plan_rejects_stale_closed_or_unlabeled_issue` | Live-state drift blocks approval. | Closed issue or issue without `status:plan-review`. | Non-zero exit and no marker/label/comment writes. |
| `test_approve_provider_plan_partial_failure_keeps_marker_quarantined` | Label/comment/refresh failures cannot create broad approval evidence. | Mocked `gh` failure after comment or label step. | Recovery JSON records phase; pending marker remains outside `.planning/plan-approved/`; no final marker exists. |
| `test_approve_provider_plan_resume_completes_pending_actions_without_duplicates` | Idempotent resume completes remaining mutations without duplicate comments or label churn. | Recovery journal with completed comment and pending label/refresh/marker promotion. | Resume verifies existing comment by idempotency key, updates missing label, refreshes queue, promotes marker once. |
| `test_dispatch_loop_never_launches_implementation_without_approval_marker` | Dispatcher refuses implementation for issues lacking label or marker. | Queue item without marker. | No implementation launch; blocker logged. |
| `test_require_plan_approval_rejects_unrelated_issue_marker_in_strict_issue_mode` | Existing broad pre-commit approval evidence cannot be satisfied by another issue marker. | Staged implementation mapped to issue A, marker only for issue B. | Strict issue mode fails closed. |
| `test_require_plan_approval_strict_mode_fails_when_issue_mapping_ambiguous` | Strict issue-specific gate never falls back to broad recent approval evidence. | Staged implementation with no inferable issue and no `--require-issue`. | Non-zero exit; diagnostic asks for explicit issue. |
| `test_dispatch_loop_refuses_lease_write_without_leader_lock` | ace-linux-2 or concurrent processes cannot double-write leases unless promoted. | Dispatcher invoked without flock leader lock or on ace-linux-2 without promotion. | No lease write; blocked reason emitted. |
| `test_dispatch_loop_aborts_when_competing_dispatcher_detected` | #2519 coexistence preflight prevents independent lease writers. | Active dispatcher marker/process not sharing the lease contract. | Loop exits fail-closed before lease write or launch. |
| `test_non_leader_node_cannot_originate_dispatch` | ace-linux-2 worker-only role cannot launch implementation without leader-created assignment. | Non-leader sees execution-ready item but no leader lease. | No launch; blocked reason emitted. |
| `test_dispatch_loop_single_writer_promotion_disables_previous_leader` | ace-linux-2 promotion requires explicit handoff and disables ace-linux-1 lease writes. | Promotion token/flag plus active ace-linux-1 state. | Promotion succeeds only after old leader marked inactive; no split-brain. |
| `test_dispatch_loop_blocks_unready_machine_routes` | Machine readiness gates provider assignment. | Offline/missing-auth/stale-repo workstation fixtures. | Candidate is blocked or rerouted; no lease to unready machine. |
| `test_dispatch_loop_falls_back_to_planning_recon_review_when_no_execution_ready_work` | Provider credits are still used safely when implementation queue is empty. | Queue with no `status:plan-approved` items. | Planning/recon/review prompt packet selected. |
| `test_dispatch_loop_uses_lease_idempotency_to_prevent_double_dispatch` | Same issue/provider/machine cannot be leased twice while active. | Active lease ledger record. | Second dispatch skipped with duplicate reason. |
| `test_dispatch_loop_applies_wednesday_friday_reset_usage_policy` | Time-based utilization policy changes fallback work selection. | Frozen dates/utilization below thresholds. | Correct planning/recon/review packet selected and policy reason logged. |
| `test_morning_qa_packet_summarizes_completed_running_blocked_and_user_actions` | Daily QA report is actionable. | Fixture run ledger with completed/running/blocked jobs. | Markdown report with tests/artifacts/next actions. |

---

## Acceptance Criteria

- [x] `uv run pytest tests/ai/test_provider_kanban.py tests/ai/test_provider_kanban_server.py tests/ai/test_approve_provider_plan.py tests/ai/test_provider_dispatch_loop.py tests/analysis/test_provider_work_queue.py tests/analysis/test_continuous_planning_pipeline.py tests/enforcement/test_require_plan_approval.py -v` passes. (63/63 green, 5.02s — verified 2026-05-13)
- [x] `scripts/ai/provider-work-queue.py` emits both readable `top_issues` and full downstream candidate lists, and its Markdown report states execution-ready requires `status:plan-approved` rather than `agent:*` labels. (commit `6bd81302f`)
- [x] `scripts/ai/provider-kanban.py` generates `config/ai-tools/provider-kanban.json`, `docs/reports/provider-kanban-dashboard.md`, and `docs/reports/provider-kanban-dashboard.html` from existing provider artifacts, full non-truncated issue data, and `continuous-planning-pipeline.py` plan/review/marker/lane readiness primitives. (commit `067c1d263`)
- [x] Dashboard renders provider utilization, issue lane, provider route, machine route, machine readiness state, approval readiness, and approval blockers. (commit `067c1d263`)
- [x] Every issue card has a hover summary sourced from durable issue/plan/review/workstation data; transient LLM-only summaries are explicitly forbidden for approval readiness. (`provider-kanban.build_hover_summary()`)
- [x] Static HTML renders disabled approval buttons plus explicit copy/paste dry-run/approval commands; real Approve action is enabled only when served from local loopback server and all approval prerequisites pass: live open issue, canonical plan exists, clean latest reviews, explicit user approval intent, issue-specific marker path ready, current `status:plan-review` label, and per-issue approval lock acquired. (`provider-kanban.render_html` + `provider-kanban-server.py`; commits `067c1d263`, `1a0f41c71`)
- [x] Approval CLI supports `--dry-run` and auditable/idempotent real mode: per-issue transaction lock, prepared body-file, quarantine marker, GitHub comment, label transition, queue refresh, post-mutation verification, atomic marker promotion, and `--resume <txid>` recovery without duplicate comments/labels. Final promoted marker includes issue number, canonical plan path, txid, user approval source, review artifact paths/fingerprints, verification timestamp, and idempotency key. (commit `01c1f8cc7`)
- [x] Dispatcher implementation mode only pulls from execution-ready lane with `status:plan-approved` and `.planning/plan-approved/<issue>.md` marker. (`provider-dispatch-loop.select_execution_ready`; commit `2d4ee3434`)
- [x] Dispatcher planning/recon/review mode can consume provider credits safely when no approved implementation work exists. (`provider-dispatch-loop.select_planning_fallback`; commit `2d4ee3434`)
- [x] Running jobs have provider, machine, issue, lease id, idempotency key, TTL, expected artifact, parent #2519 relation, and status in a single-writer lease ledger; lease writes are centralized through ace-linux-1/Hermes leader using local `flock` and #2519 coexistence preflight, ace-linux-2 is worker-only, and any promotion requires explicit single-writer handoff that disables the prior leader before new lease writes. (`provider-dispatch-loop.Lease + acquire_leader_lock + coexistence_preflight`; commit `2d4ee3434`)
- [x] Morning QA packet summarizes completed/running/blocked work, tests, changed files, artifacts, and recommended user action. (`provider-dispatch-loop.generate_morning_qa`; tests + changed_files surface when launcher reports them in run_ledger outcome dicts)
- [x] Provider refresh cron integrates Kanban/dashboard generation and includes exact fail-closed checks: `[[ -f "${REPO_ROOT}/config/ai-tools/provider-kanban.json" ]]`, `[[ -f "${REPO_ROOT}/docs/reports/provider-kanban-dashboard.md" ]]`, and `[[ -f "${REPO_ROOT}/docs/reports/provider-kanban-dashboard.html" ]]`. (commit `69a759d5c`)
- [x] User approval has moved #2665 to `status:plan-approved`; local approval marker recorded at `.planning/plan-approved/2665.md`.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Initial Claude | MAJOR | Required explicit failure/recovery semantics for approval transaction, issue-specific gate boundary, relationship to #2519, single-writer leases, and a clear static-vs-server approval architecture. |
| Initial Codex | MAJOR | Required real approval-button architecture, anti-self-approval/user-approval boundary, full issue candidate source instead of `top_issues[:8]`, machine readiness inputs/tests, and correction of a queue-text/code mismatch. |
| Initial Gemini | MAJOR | Valid findings called out missing time-policy logic, invalid `--body-file` pseudocode, undefined variable use, underspecified fixtures, and later reuse of existing `continuous-planning-pipeline.py`. |
| Fresh focused reviewer A | APPROVE | Verified prior MAJORs resolved: user approval, per-issue locks, single-writer leases, #2519 preflight, strict fail-closed inference, continuous-planning-pipeline reuse, corrected test paths, and complete acceptance command. |
| Fresh focused reviewer B | MAJOR → resolved in this revision | Found stale status/user-approval wording and missing explicit continuous-planning-pipeline file/TDD entries; this revision removes the stale wording and adds the file/test entries. |

**Overall result:** prior MAJOR findings have been incorporated. The plan was posted for user approval review and is now approved for implementation: the user reported #2665 approved via GitHub label, and `.planning/plan-approved/2665.md` records the local approval evidence. Implementation remains constrained to the approved TDD scope above.

Revisions made based on review:
- Chose the approval architecture: static report remains read-only; real HTML button works only through `scripts/ai/provider-kanban-server.py` on localhost with ephemeral token and explicit user intent.
- Added user-confirmation/auth boundary: agents and cron may only dry-run; real approval requires explicit user action through the local approval server or explicit CLI user confirmation.
- Replaced transaction-safety claims with idempotent audited transaction semantics including prepared comment body-file, quarantine marker, post-mutation verification, atomic marker promotion, recovery journal, and resume without duplicate mutations.
- Added full issue candidate source requirement by modifying `provider-work-queue.py`; dashboard must consume non-truncated full candidates and must not use `top_issues[:8]` as its only source.
- Added workstation readiness artifacts/tests and a local `flock` single-writer lease model tied to parent #2519; #2665 extends #2519 and does not create a competing independent dispatcher.
- Added time-based utilization policy tests and cron fail-closed artifact list.
- Renamed planned scripts to kebab-case to match existing repo script naming.
- Scoped the `agent:*` execution-ready wording fix into `scripts/ai/provider-work-queue.py` and existing `tests/analysis/test_provider_work_queue.py`; agent labels remain routing hints only.
- Added explicit reuse/integration with `scripts/ai/continuous-planning-pipeline.py` readiness primitives and existing continuous-planning-pipeline tests.
- Replaced generic delegated-person approval authority with explicit user approval semantics.
- Added per-issue approval transaction locking and concurrent approve/resume race tests.
- Strengthened dispatcher lease model to ace-linux-1/Hermes-leader single-writer, #2519 coexistence preflight, worker-only ace-linux-2 behavior, and explicit promotion handoff.
- Added fail-closed strict issue inference behavior to the plan and tests.

---

## Risks and Open Questions

- **Risk:** The issue asks for an HTML button, but committed static HTML cannot safely mutate GitHub state. This plan therefore uses a local loopback approval server (`scripts/ai/provider-kanban-server.py`) for the real button and keeps the committed HTML safe/read-only by default. No secrets or durable tokens may be embedded in `docs/reports/provider-kanban-dashboard.html`.
- **Risk:** Current provider telemetry is weak for Claude/Gemini and partly activity-based. Routing should use it directionally and record basis/confidence, not treat percentages as billing-grade truth. Wednesday/Friday/reset thresholds are dispatch-selection policy when the loop runs; ensuring scheduler cadence beyond existing cron integration is a follow-up monitor unless implemented in this issue’s refresh checks.
- **Risk:** Existing `provider-work-queue.py` code sets `execution_ready` only from `status:plan-approved`, but generated report wording implies explicit `agent:*` labels are enough. This issue fixes that wording and keeps implementation dispatch requiring plan-approved label plus issue-specific marker.
- **Risk:** Continuous dispatch can create cleanup debt if jobs are launched without leases, expected artifacts, and closeout responsibilities. The lease ledger and morning QA packet are non-optional.
- **Risk:** Dashboard summaries could become stale after issue edits. Approval CLI must revalidate live issue/plan/review state at click time and ignore stale rendered readiness.
- **Decision:** First implementation includes a local loopback approval server because issue #2665 explicitly requires a real approval button. Committed static HTML renders visible disabled approval controls plus copy/paste dry-run/approval commands; real buttons are enabled only when served by `provider-kanban-server.py` with ephemeral CSRF/session metadata. Static CLI-only mode remains a safe fallback, not the primary UX.
- **Decision:** `agent:*` labels are routing hints only for implementation dispatch; execution-ready requires `status:plan-approved` plus marker.

---

## Complexity: T3

**T3** — multi-artifact harness/control-plane work touching provider telemetry, GitHub issue state, approval governance, static HTML reporting, dispatch leases, and continuous multi-provider operation. It requires TDD, transaction boundaries, and adversarial plan review before implementation.
