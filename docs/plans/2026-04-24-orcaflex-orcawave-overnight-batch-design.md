# Overnight OrcaFlex/OrcaWave Planning Batch — Design

> **Status:** approved (main-session batch design; not an issue plan)
> **Location note:** lives in `docs/plans/` because `docs/superpowers/specs/` is gitignored in this repo; the `-batch-design` suffix distinguishes it from per-issue plans.
> **Date:** 2026-04-24
> **Session:** 2026-04-24 main session, pts/3 (PID 1807944)
> **Repo:** `vamseeachanta/digitalmodel`
> **Design authority:** User approved Option A + slate + deferral on 2026-04-24

---

## Goal

Run a write-only overnight batch of **10 parallel planning agents**, each producing a single adversarial-ready implementation plan for a distinct OrcaFlex/OrcaWave GitHub issue in `vamseeachanta/digitalmodel`. No code execution, no issue-label mutation beyond `status:plan-review`, no self-approval.

User reviews the 10 plans the next morning; approved plans enter the standard execute pipeline in a later session.

## Non-Goals

- **No implementation.** Agents cannot modify source files.
- **No self-approval.** Per `feedback_never_offer_to_self_label_plan_approved`, the `status:plan-approved` label remains user-gated across session boundaries.
- **No coupled-issue parallelism.** The semantic-equivalence cluster (#517/#518/#519) is deliberately deferred until #515's plan is approved, because they share the same YAML→strict pipeline and parallel planning would produce contradictory designs.
- **No cross-review fanout this batch.** Plan-review fanout (`scripts/review/plan-review-fanout.sh`) is already running on plan 2227 (PID 1902572); adding 10 more fanouts would saturate the provider quota. The agents produce drafts marked `status:draft`; the user decides whether to fanout-review each one after morning triage.

## Existing Conditions (verified 2026-04-24 ~03:48Z)

- **Repo scope**: only `vamseeachanta/digitalmodel` is in-bounds (no separate `orcaflex-*` repo).
- **Open OrcaFlex/OrcaWave-titled issues**: 58.
- **Issues with plan-status labels**: 4 at `status:pending` (#515, #517, #518, #519); 0 at `status:plan-review`; 0 at `status:plan-approved`.
- **In-flight parallel work on this workstation**:
  - PID 1895354 — isolated exec-clone running **issue #2311** in `/mnt/local-analysis/worktrees/ws-2311-exec`
  - PID 1902572 — plan-review fanout for **plan 2227** (CSA wiki)
  - PIDs 1807944, 1860162 — live `claude` sessions
  - PID 1813663 — `codex --yolo`
  - 4 agent worktree dirs under `.claude/worktrees/`

The 10 issues chosen for this batch **do not overlap** with #2311 or #2227; dispatch-time safety check will re-verify.

## Issue Slate (10, ordered by agent lane)

| Lane | # | Area | Body size | Why independent |
|------|---|------|-----------|-----------------|
| 1 | **#515** | OrcaFlex YAML semantic equivalence | 6.9 KB | Parent of the #517/#518/#519 cluster; planned alone. |
| 2 | **#282** | OrcaWave reporting standardization (WRK-130) | 5.6 KB | Disjoint subtree from #279. |
| 3 | **#279** | OrcaFlex reporting standardization (WRK-129) | 79 KB | Disjoint subtree from #282. Large body — agent should extract only relevant sections. |
| 4 | **#510** | Fix 20 pre-existing OrcaFlex test failures | 0.8 KB | Test-suite only. |
| 5 | **#500** | OrcaWave mesh preflight + auto-copy in runner | 1.7 KB | Runner-layer; distinct from config (#501). |
| 6 | **#501** | OrcaWave QTF + field points + irregular-freq | 1.9 KB | Config-schema; distinct from runner (#500). |
| 7 | **#504** | OrcaFlex buoys builder refactor (split 611-line file) | 0.8 KB | Single file, no cross-cutting. |
| 8 | **#503** | OrcaFlex/OrcaWave help ingestion (LLM-accessible) | 1.5 KB | Docs/knowledge pipeline, isolated. |
| 9 | **#511** | OrcaFlex campaign spec generation (parametric sweep) | 1.1 KB | Greenfield generator. |
| 10 | **#486** | Subsea connectors & jumpers module (API 17R) | 1.5 KB | Greenfield feature module. |

**Deferred on purpose (coupled to #515):** #517 (semantic-diff taxonomy), #518 (model-library regression tests), #519 (General/Environment/Groups fidelity). These three can be planned in the next batch once #515's approach is locked.

## Dispatch Mechanics

### 2-agent pod per issue, in 2 parallel waves (user-approved 2026-04-24)

Each of the 10 issues gets a **pod** = Explorer + Planner. Pods run as two waves:

- **Wave 1: 10 Explorers** (parallel) — each performs codebase recon for its assigned issue and writes intel to `/tmp/orca-batch-2026-04-24/intel-<N>.md`.
- **Wave 2: 10 Planners** (parallel) — each reads its pod's intel + issue body + template, and writes the final plan to `docs/plans/2026-04-24-issue-<N>-<slug>.md`.

This separation of concerns improves plan quality (Planner's entire context budget is available for synthesis rather than recon), and makes the batch partially resumable (if a Planner fails, we can retry it against the already-written intel without redoing recon).

### Write-only pattern (applies `feedback_parallel_agent_write_only_pattern`)

**Explorer agents:**

- Write **exactly one file**: `/tmp/orca-batch-2026-04-24/intel-<N>.md`
- Cannot commit, push, or touch `gh`
- Cannot modify source files, tests, configs, or any other file
- May READ anywhere in the repo; may NOT Write outside the intel path
- If an Explorer attempts a forbidden write, the main session skips that pod's Planner (no plan is produced without intel)

**Planner agents:**

- Write **exactly one file**: `docs/plans/2026-04-24-issue-<N>-<slug>.md`
- Cannot commit, push, or touch `gh`
- Cannot re-do codebase recon (intel file is the source of truth — Planner may only verify specific claims against source if confused)
- May READ the template, intel, issue JSON, and any file explicitly cited by the intel
- If a Planner tries to write outside its designated plan path, the main session kills it and flags the pod as failed in the morning report

### Main session serializes post-batch work

After all 10 Planners complete (or timeout), the main session:

1. Verifies each plan file exists and passes a self-review scan (placeholders, past-tense-artifact-claims, evidence count)
2. Commits all 10 plan files in a single atomic batch
3. Applies `status:plan-review` label to each issue (removing `status:pending` where present)
4. Posts a summary comment on each issue linking to the plan (per `feedback_gh_issue_comment`)
5. Writes a morning report at `docs/reports/2026-04-24-overnight-orcaflex-orcawave-planning-batch.md`

This avoids the git-lock races recorded in `feedback_multi_agent_commit_serialization`.

### Launch shape

- **Subagent type**: `general-purpose` for all 20 (both Explorers and Planners).
- **Model**: inherit (Opus 4.7, 1M context) — each agent's job is well-scoped; context headroom is comfortable.
- **Background**: `run_in_background: true` on all agents so the main session is notified as each completes, rather than blocking or polling.
- **Wave 1 launch**: a single message with 10 Explorer `Agent` tool calls in parallel.
- **Wave 2 launch**: after all 10 Explorers complete, a single message with 10 Planner `Agent` tool calls in parallel.
- **Timebox**: 25 turns each.
- **Session persistence requirement**: main session must remain active between the two waves to trigger wave 2. If the session dies, wave 2 can be resumed manually by re-invoking the planner dispatch against the already-written intel files.

### Explorer prompt skeleton

Each Explorer receives:

1. **Full issue context** pre-fetched to `/tmp/orca-batch-2026-04-24/issue-<N>.json`. Explorer reads this; does not re-fetch.
2. **Write target** (single absolute path): `/tmp/orca-batch-2026-04-24/intel-<N>.md`.
3. **Intel structure required**:
   - Relevant source files (with `src/…:line_range` refs) and what each does today
   - Existing tests that touch the area (with `tests/…` refs)
   - Related prior plans under `docs/plans/` (with findings)
   - Standards applicable (via `data/document-index/standards-transfer-ledger.yaml`) — engineering issues only
   - Wiki pages applicable (via `knowledge/wikis/**`) — engineering issues only
   - Gaps: what must be built from scratch (each gap is a testable claim)
   - Risks surfaced: files that are large/coupled/will need adversarial review
4. **Shared context allowlist (read-only):**
   - `docs/plans/2026-04-01-orcawave-orcaflex-intensive-plan.md` (existing infra map)
   - `src/digitalmodel/**`, `tests/**`, `docs/plans/**`, `knowledge/wikis/**`, `data/document-index/**`
5. **Hard forbidden list:**
   - `git commit`, `git push`, `gh *` (any), any Write outside the intel path
   - Touching `docs/plans/2026-04-17-issue-2311-*`, `docs/plans/2026-04-12-issue-2227-*` (in-flight elsewhere)
6. **Per-issue scope boundary** (one sentence per issue) to prevent Explorer drift into neighbors.

### Planner prompt skeleton

Each Planner receives:

1. **Intel file** at `/tmp/orca-batch-2026-04-24/intel-<N>.md` (its pod's Explorer output).
2. **Issue JSON** at `/tmp/orca-batch-2026-04-24/issue-<N>.json`.
3. **Plan template**: `docs/plans/_template-issue-plan.md` (all sections required, with the Resource Intelligence evidence contract from #2208).
4. **Write target** (single absolute path): `/mnt/local-analysis/workspace-hub/docs/plans/2026-04-24-issue-<N>-<slug>.md`.
5. **Hard forbidden list:**
   - `git commit`, `git push`, `gh *` (any), any Write outside the designated plan path
   - Re-doing codebase recon — Planner must use intel-sourced citations, not fresh grep
6. **Failure protocol**: if the intel has gaps, Planner writes the plan with explicit `[EVIDENCE GAP]` markers in the affected sections rather than inventing sources.
7. **Complexity tagging**: each plan labels itself T1/T2/T3 per template; user uses this for morning approval triage.

### Coordination with the live #2311 and plan-2227 work

- Re-run `ps -ef | grep -E "(claude|codex)"` immediately before dispatch to confirm those PIDs are still scoped to their current issues and have not expanded.
- Skip any issue that appears in `logs/orchestrator/hermes/` as currently in-flight (safety net — none of the 10 should hit this).

## Morning Report Contents

`docs/reports/2026-04-24-overnight-orcaflex-orcawave-planning-batch.md` will contain:

1. **Per-issue verdict table** (10 rows): plan path, complexity (T1/T2/T3), evidence-count, self-review flags, recommended approve/revise/hold.
2. **Cross-issue dependency notes**: any plan that references another (e.g., #500 ↔ #501 config surface, #279 ↔ #282 reporting primitives).
3. **Deferred-cluster readiness**: what #515's plan locks that now unblocks planning of #517/#518/#519.
4. **Failed lanes** (if any): cause, whether partial output is recoverable, recommended retry shape.
5. **Recommended user actions**: suggested order of review (cheap T1s first, heavy T3s last) — but explicitly **not** suggesting which to approve.

## Guardrails Specific to This Batch

- **In-flight exclusion re-check** immediately before dispatch.
- **Abort-on-drift policy**: kill agents that attempt forbidden writes, do not negotiate.
- **No self-approval gate**: main session verifies no plan file claims `status:plan-approved`.
- **Past-tense drift scan**: per `feedback_plan_past_tense_artifact_claims`, main session greps plans for "implemented", "added", "fixed" applied to proposed work — flag any hit in the morning report.
- **Memory-file protection**: agents may READ `.claude/memory/**` and `~/.claude/projects/.../memory/**` for context but cannot WRITE.

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Two agents cite contradictory facts about shared infra | Shared intensive-plan (2026-04-01) as single source of truth; evidence-count enforcement |
| Agent hallucinates a file path or function name | Evidence contract (#2208) requires `ls`-verified paths in Evidence block |
| Agent drift into coupled-cluster planning (#517/#518/#519) | Explicit "out-of-scope" sentence in #515's prompt listing those three by number |
| Git-lock contention with the live #2311 worktree | Agents are write-only, so no git mutation during the batch — contention is impossible |
| Morning report itself makes an approval recommendation | Explicit prompt rule forbidding approval verbs in the report (`feedback_never_offer_to_self_label_plan_approved`) |
| `gh issue` rate-limit when labeling 10 issues in serial | Serialize with `sleep 2` between `gh issue edit` calls |
| #279's 79 KB body blows agent context budget | Prompt instructs agent to use `jq` to extract only the Acceptance-Criteria + Current-State sections from the JSON |

## Acceptance Criteria for This Batch

- [ ] 10 intel files exist at `/tmp/orca-batch-2026-04-24/intel-<N>.md`.
- [ ] 10 plan files exist at the designated paths.
- [ ] Each plan has a non-empty Resource-Intelligence section with ≥3 sources and an Evidence block, sourced from its pod's intel file.
- [ ] No plan is self-labeled `status:plan-approved`.
- [ ] All 10 issues carry `status:plan-review` label after batch (or the label application failed cleanly with error captured in morning report).
- [ ] Each of the 10 issues has a summary comment posted linking to its plan.
- [ ] Morning report exists at `docs/reports/2026-04-24-overnight-orcaflex-orcawave-planning-batch.md`.
- [ ] No modifications to source code, tests, configs, memory files, `.claude/` files, or any path other than the 10 designated plans + the 1 morning report.

## What Happens After User Approval of This Spec

1. Main session dispatches all 10 agents in one parallel message.
2. Main session waits for background notifications.
3. As each agent completes, main session captures its output path and flags any error.
4. After the last agent finishes (or its timeout expires), main session runs the post-batch actions described above.
5. Main session surfaces a concise completion message with the morning report path and a reminder that nothing is `plan-approved` yet.

## Open Questions for User

None remaining; all three clarifying questions were answered in the approval turn (slate accepted, cluster deferral accepted, spec-first path accepted).
