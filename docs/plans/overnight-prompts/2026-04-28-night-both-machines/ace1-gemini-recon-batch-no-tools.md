# A2 — Gemini no-tool recon prompt

You are Gemini. Do not use tools. Do not call shell commands. Do not read or write files. Produce one markdown report only from the embedded issue context below. The shell wrapper will capture your stdout into the log/result file.

For each issue, provide: current-state summary, gaps/blockers, recommended next status/labels, exact next implementation prompt for tomorrow, and verification commands. End with a ranked summary by next-action readiness and AI-credit value.


## Issue #2295: WRK: 2025 TX franchise No Tax Due + PIR — SKEstates and AceEngineer
URL: https://github.com/vamseeachanta/workspace-hub/issues/2295
Labels: enhancement, priority:high, cat:personal-finance, domain:tax-preparation
Updated: 2026-04-16T02:54:39Z

### Body excerpt

## Summary
File Texas franchise tax No Tax Due Reports + Public Information Reports (PIR) for both C-Corps via Texas Comptroller Webfile.

## Entities

### SKEstates Inc (Sabitha and Krishna Estates Inc.)
- **Webfile:** XT036957
- **EIN:** 39-2384131
- **SOS:** 1484581040004
- **First filing** (incorporated 2025-05-27)
- **Revenue:** $50,085.60 (well below $2.47M threshold)
- **Data file:** `sabithaandkrishnaestates/taxes/2025/tx-franchise-tax-filing-data.yaml`

### AceEngineer Inc (Achanta AceEngineer Inc)
- **EIN:** 46-2870262
- **Incorporated:** 2013-05-24 (TX)
- **Revenue:** $361,410 (below $2.47M threshold)
- **Data file:** needs creation — model on SKEstates YAML

## Filing Requirements (both entities)
1. **No Tax Due Report** — certify revenue < $2,470,000
2. **Public Information Report (PIR)** — update officer/director/agent info
3. Both reports REQUIRED even though $0 tax owed

## Key Dates
- **Due:** May 15, 2026 (not affected by federal extensions)
- **Late penalty:** $50/report ($100 total per entity)

## Acceptance Criteria
- [ ] SKEstates No Tax Due Report filed via Webfile
- [ ] SKEstates PIR filed via Webfile
- [ ] AceEngineer No Tax Due Report filed via Webfile
- [ ] AceEngineer PIR filed via Webfile
- [ ] Confirmation numbers saved to `taxes/2025/filed/`
- [ ] Human approval before each submission

## Handover Prompt
See `sabithaandkrishnaestates/taxes/2025/tx-franchise-handover-prompt.md`

### Recent comments excerpts


## Issue #2501: chore(planning): #2105 governance-lock — handoff vs live-state discrepancy
URL: https://github.com/vamseeachanta/workspace-hub/issues/2501
Labels: priority:medium, cat:documentation, cat:harness
Updated: 2026-04-26T17:57:48Z

### Body excerpt

## Context

The 2026-04-26 morning handoff stated [#2105](https://github.com/vamseeachanta/workspace-hub/issues/2105) (governance-lock) needs a v5 plan revision before [#2483](https://github.com/vamseeachanta/workspace-hub/issues/2483) and [#2484](https://github.com/vamseeachanta/workspace-hub/issues/2484) can unblock. However, live-state inspection shows:

- [#2105](https://github.com/vamseeachanta/workspace-hub/issues/2105) state: OPEN
- Labels: `enhancement,priority:medium,cat:documentation,cat:harness,status:plan-approved`
- Most-recent comment (2026-04-24T16:56:37Z): linked children #2483 (matrix population) + #2484 (scanner extension)

The `status:plan-approved` label is already present.

## Question

Is [#2105](https://github.com/vamseeachanta/workspace-hub/issues/2105) actually ready to execute (handoff is stale), or is v5 needed to address something the v4 approval missed (handoff is right, label is premature)?

## Action

User clarification needed:
- If ready: schedule exec routine for [#2105](https://github.com/vamseeachanta/workspace-hub/issues/2105), then unblock #2483/#2484.
- If v5 needed: open a v5 planning session.

## Surfaced

2026-04-26 from autonomous-wave session — flagged in `/tmp/handoff-2026-04-26-session-close.md`.

### Recent comments excerpts


## Issue #2254: fix(provider-telemetry): improve Claude and Gemini quota observability for exact weekly targeting
URL: https://github.com/vamseeachanta/workspace-hub/issues/2254
Labels: bug, priority:high, cat:harness, domain:agent-cost-tracking
Updated: 2026-04-26T21:54:49Z

### Body excerpt

## Summary
Improve Claude and Gemini quota observability so provider utilization can support exact weekly targeting instead of falling back to directional activity heuristics.

## Why
The current routing/control-plane stack is useful, but quota observability is still the limiting factor for precise weekly credit optimization:
- Claude quota is still frequently `source: unavailable`
- Gemini quota is still `source: estimated`
- utilization reports therefore fall back to activity-vs-recent-peak for two key providers

This means the system can route work intelligently, but cannot yet guarantee near-100% weekly usage with high confidence.

## Scope
- identify stronger live data sources for Claude weekly headroom
- identify stronger live data sources for Gemini usage/headroom
- wire improved sources into query-quota / latest quota artifacts
- preserve current fallback behavior when better telemetry is unavailable
- update reports to distinguish exact vs estimated weekly targeting confidence

## Deliverables
- improved quota-source extraction or parsing for Claude/Gemini
- updated quota snapshot artifacts
- utilization report notes showing confidence level per provider
- tests for the new telemetry paths and fallback behavior

## Related
- Parent provider-utilization strategy: #1838
- Weekly provider review context: #2089
- Existing quota/cache hygiene issues: #2108, #2109

## Acceptance criteria
- [ ] Claude quota source is stronger than `unavailable` in the normal healthy path
- [ ] Gemini usage source is stronger than `estimated` in the normal healthy path
- [ ] utilization reports can distinguish exact vs heuristic routing confidence
- [ ] fallback behavior remains safe when direct telemetry is unavailable


### Recent comments excerpts

Comment by vamseeachanta at 2026-04-26T21:54:49Z

Plan drafted: `docs/plans/2026-04-26-issue-2254-claude-gemini-quota-observability.md` (commit `7aa5ffe05`).

Per-provider fallback hierarchy:
- **Claude**: Admin-API → OAuth-cache → stats-cache → ccusage → unavailable
- **Gemini**: CLI `quota --json` → `state.json` → tmp-filecount → unavailable

Schema additions: `confidence_level` per agent (`exact|heuristic|estimated|absent`) + top-level `overall_targeting_confidence` in routing scorecard. Console scraping ruled out of scope. 19 TDD tests covering telemetry-available path, telemetry-unavailable fallback, mixed-confidence aggregation, regression guard, schema round-trip, and rate-limit self-throttling.

**Two user-policy questions surfaced for plan-review**:
1. Should `confidence_level: absent` block routing recommendations? (default proposed: annotate-only)
2. Where should `ANTHROPIC_ADMIN_KEY` live? (default proposed: env-only with `~/.config/workspace-hub/ai-secrets.env` autoload)

Status: `draft`. Awaiting human review before `status:plan-review`.


## Issue #2519: feat(hermes): orchestrate AI provider usage and workstation dispatch
URL: https://github.com/vamseeachanta/workspace-hub/issues/2519
Labels: enhancement, cat:ai-orchestration, cat:harness, priority:critical, domain:ai-orchestration, domain:workstations, domain:agent-cost-tracking
Updated: 2026-04-27T18:57:43Z

### Body excerpt

## Summary
Build and mature a Hermes-led orchestration flow that coordinates:

1. AI provider/model usage across Claude, Codex, Gemini, and future providers.
2. Work dispatch across network-accessible workstations, starting with `ace-linux-1` and `ace-linux-2` over VPN.
3. Queue/label/telemetry feedback so urgent expiring credits are consumed intentionally without breaking plan-first governance.

## Why now
- User priority on 2026-04-27: Codex credit is expiring in ~24 hours with ~50% remaining per user-visible subscription state; use it aggressively for bounded work before expiry.
- Existing workspace telemetry reports Codex as a high-priority execution lane (`docs/reports/provider-work-queue.md`), but this needs to be tied to workstation availability and Hermes orchestration decisions.
- Workstation priority is explicit: first `ace-linux-1`, then `ace-linux-2`, both VPN-accessible.

## Current evidence / anchors
- `docs/BUSINESS_BRAIN.md` lists `ace-linux-1` as primary Linux dev for daily AI work / Claude-Codex sessions, and `ace-linux-2` as secondary Linux dev for parallel AI work / overflow.
- `docs/BUSINESS_BRAIN.md` lists provider roles: Claude as default orchestrator, Codex as coding worker/adversarial reviewer, Gemini as narrow large-context research/review lane.
- `docs/reports/provider-work-queue.md` generated 2026-04-27 recommends provider order `gemini, codex, claude`, with Codex routing priority `highest` and several execution-ready Codex candidates.
- Live `scripts/ai/assessment/query-quota.sh --refresh --json` currently reports Codex from `history.jsonl`; this may conflict with user-visible expiring-credit state, so the plan must explicitly reconcile provider telemetry sources before trusting automation.

## Desired mature flow
Hermes should operate as the control-plane/orchestrator that can:

1. Refresh provider usage / quota telemetry and classify confidence per provider.
2. Inventory workstation availability, VPN reachability, repo sync health, and tool readiness for `ace-linux-1` and `ace-linux-2`.
3. Combine provider urgency + workstation readiness + issue status labels into a ranked dispatch plan.
4. Prefer Codex for the next 24 hours for bounded implementation, tests, cleanup, and mechanical issue execution where plans are already approved.
5. Preserve Claude for orchestration, plan synthesis, and adversarial review; preserve Gemini for batched research/recon where it fits.
6. Emit a reviewable dispatch ledger showing: issue, provider, workstation, reason, quota basis, safety gate, and expected validation.
7. Avoid unapproved implementation: only dispatch execution to issues with `status:plan-approved`, unless the dispatch task is planning/review-only.
8. Support manual override by the user before large batches or cross-machine operations.

## Initial scope proposal
This issue should first produce a canonical plan for a minimum viable orchestration flow, then proceed after approval.

In-scope candidates:
- Control-plane design for provider + workstation dispatch.
- Codex-expiry emergency routing playbook for the next 24 hours.
- Workstation readiness probes for `ace-linux-1` and `ace-linux-2`.
- Provider telemetry source-of-truth reconciliation.
- Dispatch ledger schema and operator-facing review packet.
- GitHub label/queue integration using existing `agent:*`, `machine:*`, `status:*`, `priority:*`, `cat:*`, and `domain:*` labels.

Out of scope unless split into child issues:
- Full distributed scheduler implementation across all machines.
- Secret distribution or credential synchronization beyond documented checks.
- Broad provider billing/account automation.
- Running unapproved repo mutations outside the plan-approved gate.

## Immediate Codex-expiry handling requirement
The plan should identify an immediate safe action path for the next 24 hours:

1. Refresh or reconcile Codex usage telemetry against the user-visible subscription state.
2. List `status:plan-approved` issues that are good Codex candidates.
3. Map the top candidates to `ace-linux-1` / `ace-linux-2` based on repo/worktree readiness.
4. Generate self-contained Codex prompts or Hermes/Codex launch commands.
5. Require final user approval before launching any long-running batch.

## Acceptance criteria
- A canonical plan artifact exists under `docs/plans/YYYY-MM-DD-issue-NNN-<slug>.md`.
- The plan includes resource intelligence from repo docs, provider utilization reports, label taxonomy, and workstation readiness evidence.
- The plan explicitly reconciles conflicting Codex usage telemetry sources.
- The plan defines the minimum viable dispatch ledger fields.
- The plan defines how `ace-linux-1` and `ace-linux-2` readiness is probed before assigning work.
- The plan defines routing rules for Claude / Codex / Gemini and explains the temporary Codex-first priority due to expiring credit.
- The plan identifies immediate plan-approved Codex work candidates or states why none are safe.
- Adversarial plan review is completed before the issue moves to `status:plan-review`.
- No implementation or cross-workstation dispatch starts until explicit user approval moves the issue to `status:plan-approved`.

## Suggested labels
- `enhancement`
- `priority:critical`
- `cat:ai-orchestration`
- `cat:harness`
- `domain:ai-orchestration`
- `domain:workstations`
- `domain:agent-cost-tracking`

## Related issues / context
- #2504 — dispatch-ledger trust contract and lease lifecycle writer.
- #2506 — Lane E implementation handoff readiness.
- #2408 — model-release readiness contract and upgrade playbook.
- #2301 — openai-codex transport/challenge recovery.

## Governance note
This is a planning-first issue. Implementation and cross-machine execution must follow the workspace gate:
Issue → resource intelligence → plan → adversarial review → `status:plan-review` → user approval → `status:plan-approved` → implementation/dispatch.


### Recent comments excerpts

Comment by vamseeachanta at 2026-04-27T17:43:50Z

Correction to the `ace-linux-2` readiness finding:

I re-checked using a login shell. The earlier probe used non-login SSH, which missed user-level paths.

Verified on `ace-linux-2` with `bash -lc`:

```text
hermes: /home/vamsee/.local/bin/hermes
Hermes Agent v0.11.0 (2026.4.23)
Hermes model: {'default': 'gpt-5.5', 'provider': 'openai-codex', 'base_url': 'https://chatgpt.com/backend-api/codex'}

codex: /home/vamsee/.npm-global/bin/codex
codex-cli 0.123.0
Codex auth files: ~/.codex/auth.json and ~/.codex/config.toml exist
```

Updated report artifact:
- `docs/reports/2026-04-27-issue-2519-ace-linux-2-readiness-probe.md`

Revised delegation implication:
- `ace-linux-2` is repo-ready and **Hermes/Codex-runtime-ready when launched through a login shell**.
- Dispatch commands should use `ssh ace-linux-2 'bash -lc ...'` or otherwise source the user environment so `/home/vamsee/.local/bin` and `/home/vamsee/.npm-global/bin` are on `PATH`.
- For the immediate Codex-expiry objective, `ace-linux-2` can be considered a Codex worker after a lightweight preflight confirms Hermes default model remains `openai-codex / gpt-5.5`.
- Remaining caveat: `gh auth status` is still invalid on `ace-linux-2`, so GitHub mutation authority should stay on `ace-linux-1` unless/until GH auth is repaired there.


Comment by vamseeachanta at 2026-04-27T17:45:59Z

GH auth re-check on `ace-linux-2` complete.

Result: **GH is still not authenticated / token invalid** on `ace-linux-2`, even in a login shell.

Evidence:

```text
HOST=ace-linux-2
GH_PATH=/usr/bin/gh
gh version 2.90.0 (2026-04-16)

gh auth status:
  X Failed to log in to github.com account vamseeachanta (default)
  - The token in default is invalid.

gh api user:
  Requires authentication (HTTP 401)
```

Created follow-up blocker/check issue:
- #2520 — fix(workstations): repair and gate ace-linux-2 GitHub auth before delegation
- https://github.com/vamseeachanta/workspace-hub/issues/2520

Operational impact for #2519:
- `ace-linux-2` remains usable for Hermes/Codex local execution when launched with `bash -lc`.
- `ace-linux-1` should retain GitHub mutation authority until #2520 is resolved.
- The #2519 plan should treat #2520 as a pre-delegation gate for any workflow where `ace-linux-2` must comment, label, create PRs, push, or close issues directly.


Comment by vamseeachanta at 2026-04-27T17:53:14Z

## Handoff documented for parallel Hermes terminal

Prepared and pushed a docs-only handoff for the next Hermes terminal/session to generate continuous + parallel work prompts across `ace-linux-1` and `ace-linux-2`:

- Handoff doc: `docs/plans/2026-04-27-issue-2519-hermes-workstation-orchestration-handoff.md`
- Commit: `d5ee02cef`

Key handoff points captured:

- `ace-linux-1` remains primary control plane and GitHub mutation authority.
- `ace-linux-2` is first overflow/Codex worker and must be launched through login shell: `ssh ace-linux-2 'bash -lc "<command>"'`.
- `ace-linux-2` Hermes/Codex are available through login shell with `openai-codex / gpt-5.5`.
- `ace-linux-2` `gh` auth remains invalid, tracked separately in #2520; do not use it for GitHub mutation until repaired.
- Codex credit expiry urgency is captured as the top provider priority.
- The next terminal's deliverable is an operator-ready prompt pack under `docs/plans/`, with separate prompts for `ace-linux-1` control plane, `ace-linux-2` worker, and optional monitor/reconciler.

No long-running workers were launched from this session.

Comment by vamseeachanta at 2026-04-27T18:45:13Z

Committed and merged the continuous machine prompt pack plus refreshed provider queue artifacts to main. Commit: 3e136a524. Prompt files: docs/plans/machine-prompts/2026-04-27/README.md, ace-linux-1-continuous-parallel-work-prompt.md, ace-linux-2-continuous-parallel-work-prompt.md. Local main and origin/main both verify at 3e136a524. Remaining local dirt is only .claude/state/session-signals/2026-04-27.jsonl, intentionally not committed.

Comment by vamseeachanta at 2026-04-27T18:57:43Z

## Future issues created for #2519 maturation

Created three follow-up issues to mature the Hermes workstation/provider orchestration flow beyond the current two-machine prompt pack:

1. #2523 — https://github.com/vamseeachanta/workspace-hub/issues/2523
   - Reusable Hermes workstation preflight readiness checker.

2. #2524 — https://github.com/vamseeachanta/workspace-hub/issues/2524
   - Machine-aware dispatch ledger and reconciler.

3. #2525 — https://github.com/vamseeachanta/workspace-hub/issues/2525
   - Codex expiring-credit burn-down controller.

Documented the follow-up tree here:

- `docs/plans/2026-04-27-issue-2519-future-issue-handoff.md`

Operational note remains unchanged: until #2520 is fixed, `ace-linux-1` should own GitHub mutations and `ace-linux-2` should execute only through login-shell-backed Hermes/Codex lanes with local result artifacts.



## Issue #2520: fix(workstations): repair and gate ace-linux-2 GitHub auth before delegation
URL: https://github.com/vamseeachanta/workspace-hub/issues/2520
Labels: bug, cat:ai-orchestration, cat:harness, priority:critical, domain:ai-orchestration, domain:workstations, domain:agent-cost-tracking
Updated: 2026-04-27T17:45:28Z

### Body excerpt

## Summary
`ace-linux-2` currently has Hermes/Codex available in a login shell, but GitHub CLI auth is still invalid. Before delegating end-to-end issue execution to `ace-linux-2`, repair GH auth or constrain that workstation to local execution while `ace-linux-1` owns GitHub mutations.

## Evidence
Checked from `ace-linux-1` using login shell on `ace-linux-2`:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=8 ace-linux-2 'bash -lc '\''set +e; command -v gh; gh --version | head -3; gh auth status; gh api user --jq "{login:.login,id:.id}"'\'''
```

Observed:

```text
GH_PATH=/usr/bin/gh
gh version 2.90.0 (2026-04-16)

github.com
  X Failed to log in to github.com account vamseeachanta (default)
  - Active account: true
  - The token in default is invalid.
  - To re-authenticate, run: gh auth login -h github.com

GH_API_VIEWER
{
  "message": "Requires authentication",
  "documentation_url": "https://docs.github.com/rest",
  "status": "401"
}
gh: Requires authentication (HTTP 401)
```

## Why this matters
For #2519, `ace-linux-2` is intended as a high-priority overflow/Codex worker. It can run Hermes/Codex with `bash -lc`, but invalid GH auth blocks safe autonomous GitHub operations:

- issue comments
- label changes
- PR creation/review
- pushing through `gh` workflows
- closeout evidence posting

## Scope
Create or formalize a pre-delegation check script/runbook that validates `ace-linux-2` before launching workers.

Minimum checks:

1. SSH reachability via BatchMode.
2. Login-shell PATH includes Hermes/Codex:
   - `/home/vamsee/.local/bin/hermes`
   - `/home/vamsee/.npm-global/bin/codex`
3. Hermes model config confirms:
   - provider: `openai-codex`
   - model: `gpt-5.5`
4. Codex CLI exists and can report version.
5. GH auth is valid:
   - `gh auth status`
   - `gh api user --jq .login`
6. Canonical repo root exists:
   - `/mnt/local-analysis/workspace-hub`
7. Target tier-1 repo status is clean or has an approved dirty-state exception.
8. Engineering software smoke test, if the work packet requires a domain tool.

## Acceptance criteria
- A documented command or script exists to run the pre-delegation checks from `ace-linux-1` against `ace-linux-2`.
- The check clearly reports PASS/FAIL per capability: host, repo, Hermes, Codex, GH, engineering tools.
- #2519 can reference this as the mandatory gate before dispatching Codex/Hermes work to `ace-linux-2`.
- GH auth on `ace-linux-2` is either repaired and verified, or #2519 explicitly records that `ace-linux-1` retains GitHub mutation authority while `ace-linux-2` performs local execution only.

## Related
- Parent/control-plane issue: #2519
- Readiness probe artifact: `docs/reports/2026-04-27-issue-2519-ace-linux-2-readiness-probe.md`


### Recent comments excerpts
