# WRK-1301: /work Queue Enhancement Research Brief

> Research date: 2026-03-17 | Source: get-shit-done + CLI PM tool landscape + current /work audit

## 1. Get-Shit-Done (GSD) — Key Takeaways

**What it is:** A meta-prompting/context-engineering framework wrapping AI coding agents (Claude Code, Gemini CLI, Codex). 32K+ stars, MIT license, Node.js. Core problem: context rot during long LLM sessions.

### Features Worth Adopting

| GSD Feature | Our Equivalent | Gap |
|---|---|---|
| **Wave-based parallel execution** — dependency DAG groups plans into waves; independent plans run in parallel subagents | `parallel-work-policy` skill (manual) | No automated wave grouping or file-ownership conflict detection |
| **State.md persistent tracking** — YAML frontmatter synced on every update; survives context resets | `checkpoint.yaml` per WRK | We checkpoint at session boundaries, not continuously |
| **Context monitor hook** — warns at 35%/25% remaining context, directs agent to pause properly | None | No context budget awareness in our lifecycle |
| **Progress command** — completion %, recent work, decisions, blockers, smart routing to next action | `whats-next.sh` (partial) | No single-WRK progress view with decision/blocker history |
| **Pause/resume with handoff doc** — `continue-here.md` captures exact state for next session | `checkpoint.yaml` (similar) | Our checkpoint lacks prose context summary for cold-start |
| **Goal-backward verification** — verifies observable outcomes, not activity completion | Stage 12 TDD + Stage 14 gate evidence | Our verification is test-centric; no user-perspective outcome checks |
| **Model profile system** — quality/balanced/budget profiles control model per agent role | `task_classifier.sh` (WRK-5002 pending) | No profile presets; routing is per-WRK not per-role |
| **Atomic commits per task** — each task gets its own conventional commit, independently revertable | Our convention is per-WRK commit | More granular commit strategy within a WRK could aid bisect |
| **Note capture** — zero-friction `/gsd:note` for ideas outside current scope | `create-spinoff-wrk.sh` (heavier) | No lightweight scratch capture; spinoff requires full WRK metadata |

### Features We Already Do Better

| Feature | GSD | Our System |
|---|---|---|
| **Lifecycle depth** | 4 stages (Discuss→Plan→Execute→Verify) | 20 stages with explicit gate evidence |
| **Cross-provider review** | Single-agent verification | Multi-provider (Claude+Codex+Gemini) with Codex hard gate |
| **Machine partitioning** | Not addressed | Machine-range WRK IDs, workstation assignment |
| **Feature decomposition** | Milestones→Phases→Plans | Feature WRK→Child WRKs with dependency tracking |
| **Evidence packaging** | Markdown-based state | YAML evidence per stage with schema validation |
| **Legal compliance** | Not addressed | Deny-list scanning integrated into workflow |

## 2. CLI PM Tool Landscape — Best Features

### High Relevance for Our System

| Feature | Best Tool | How It Would Help |
|---|---|---|
| **Urgency scoring algorithm** | Taskwarrior | Auto-surface highest-priority WRK. Weighted: due proximity (+12), blocking count (+8), priority (+6), age (+2), blocked penalty (-5) |
| **Git-native storage + agent JSON mode** | Beads | Our YAML files are already git-native; adding structured JSON query output for agents would help |
| **Per-directory context auto-switch** | dstask + direnv | Auto-set active WRK when `cd`-ing into a repo — natural for multi-repo |
| **Dependency graph visualization** | ascii-dag, PHART | Terminal DAG view of `blocked_by` relationships across WRKs |
| **Time tracking integration** | Timewarrior | Estimation calibration: predicted vs actual per complexity route |
| **PageRank prioritization** | Beads | Graph-theoretic priority based on transitive blocking relationships |
| **Recurring tasks** | Taskwarrior | Weekly syncs, monthly audits — currently manual or cron-adjacent |

### Medium Relevance

| Feature | Description |
|---|---|
| **Burndown/velocity charts** | ASCII charts of WRK completion rate over time windows |
| **NLP task capture** | LLM-powered `/work add` that extracts category, priority, repos, dependencies from natural language |
| **Session persistence browser** | Browse/search past session contexts (beyond checkpoint.yaml) |
| **Estimation vs actual tracking** | Per-WRK estimated effort field + actual time, with calibration reports |

## 3. Current /work System — Gaps Identified

### Automation Gaps (Scripts Missing)

| Gap | Impact | Proposed Fix | Complexity |
|---|---|---|---|
| **Auto-unblock** — no script watches for blocking WRK completion | Stale blocked/ items; manual moves | `auto-unblock.sh` cron/hook: when WRK archives, scan blocked/ for `blocked_by` matches | Simple |
| **Feature auto-close** — no trigger when all children archived | Manual feature closure | `feature-auto-close-hook.sh` in `on-complete-hook.sh` | Simple |
| **Route auto-classify** — no `assign-routes.sh` | Manual complexity decision at Stage 3 | Heuristic: word count + repo count + file count → route suggestion | Medium |
| **Legal scan in lifecycle** — not wired into Stage 19/20 | Can archive without legal scan | Add legal scan check to `close-item.sh` | Simple |
| **Ghost pending sweep** — `scan-ghost-pending.sh` not automated | Stale items accumulate | Wire into session-start or weekly cron | Simple |

### Feature Gaps (New Capabilities)

| Gap | Impact | Proposed Enhancement | Complexity |
|---|---|---|---|
| **Urgency scoring** | Manual prioritization; `whats-next.sh` uses simple sort | Weighted score: priority×6 + age×2 + blocking_count×8 + blocked×(-5) + due_proximity×12 | Medium |
| **Context budget monitor** | Context rot in long sessions | Hook that checks token usage and warns at thresholds | Medium |
| **Lightweight note capture** | No scratch pad; everything needs full WRK | `/work note <text>` → append to `.claude/work-queue/notes.yaml` | Simple |
| **Decision/blocker log per WRK** | Decisions scattered in chat, lost across sessions | `decisions:` and `blockers:` arrays in checkpoint.yaml | Simple |
| **Single-WRK progress view** | No `/work progress WRK-NNN` showing stage, decisions, time spent | Script reading evidence + checkpoint + frontmatter | Medium |
| **Dependency DAG visualization** | `blocked_by` field exists but no visual | `dep-graph.sh` using ascii-dag or simple indented tree | Medium |
| **Recurring WRK templates** | Weekly/monthly tasks manually created | `recurring-wrk.yaml` config + cron job | Medium |
| **Estimation tracking** | No effort prediction or calibration | `estimated_hours:` field + actual from timestamps + calibration report | Medium |
| **Wave-based parallel grouping** | Parallel work possible but not automated | Script analyzing `blocked_by` graph → wave assignment → parallel hints | Complex |

## 4. Proposed Enhancement WRKs

### Priority 1 — Quick Wins (Route A, Simple)

| # | Title | Description |
|---|---|---|
| 1 | Auto-unblock on archive | `on-complete-hook.sh` scans blocked/ for `blocked_by` matches; moves to pending/ |
| 2 | Feature auto-close check | Add `feature-close-check.sh` call to archive hook |
| 3 | Legal scan gate in close | Add `legal-sanity-scan.sh` check to `close-item.sh` |
| 4 | Ghost pending sweep in session-start | Wire `scan-ghost-pending.sh` into session-start Step 2 |
| 5 | Lightweight note capture | `/work note` → append to `notes.yaml`; `/work notes` → list |

### Priority 2 — Medium Enhancements (Route B)

| # | Title | Description |
|---|---|---|
| 6 | Urgency scoring for whats-next | Weighted algorithm replacing simple sort in `whats-next.sh` |
| 7 | Single-WRK progress command | `/work progress WRK-NNN` → stage, decisions, blockers, time, evidence status |
| 8 | Route auto-classification | Heuristic script for Stage 3 triage: suggest route based on description/scope |
| 9 | Decision/blocker log | Add `decisions:` and `blockers:` to checkpoint schema |
| 10 | Dependency DAG visualization | `dep-graph.sh` rendering `blocked_by` relationships as ASCII tree |

### Priority 3 — Strategic Enhancements (Route B/C)

| # | Title | Description |
|---|---|---|
| 11 | Context budget monitor hook | Warn at 35%/25% context remaining; suggest checkpoint |
| 12 | Recurring WRK templates | Config-driven recurring task creation (weekly syncs, monthly audits) |
| 13 | Estimation vs actual tracking | `estimated_hours:` field + calibration report per complexity route |
| 14 | Wave-based parallel execution | Dependency graph analysis → wave grouping → parallel execution hints |
| 15 | NLP-enhanced task capture | LLM extracts category, priority, repos, dependencies from natural language `/work add` |

## 5. Platform Cannibalization Assessment

> Which of our custom features will Claude Code absorb natively, making our implementation redundant?

### Already Redundant or Imminently So

These Claude Code primitives exist today (some as deferred tools shipping now). Our custom versions add workflow value on top, but the plumbing underneath is being replaced.

| Our Feature | Claude Code Native | Impact |
|---|---|---|
| **WRK item CRUD** (create, status, list, update) | `TaskCreate`, `TaskUpdate`, `TaskList`, `TaskGet` | Native task primitives will replace our markdown-file-based WRK CRUD. Our frontmatter schema is richer, but the basic operations are product features now. |
| **Planning gates** (Stage 4-7 plan approval) | `EnterPlanMode` / `ExitPlanMode` | Native plan-before-code. Our multi-stage review is richer but the concept is built-in. |
| **Session checkpoint/resume** | `--continue`, `--resume` flags | Session continuity is native. Our `checkpoint.yaml` carries more structured state (decisions, blockers, entry_reads) but the primitive is absorbed. |
| **Worktree isolation** (parallel execution) | `EnterWorktree` / `ExitWorktree` | Agent-level git worktree support is native. Our wave-based parallelism would use this underneath. |
| **Agent dispatch** (`scripts/agents/*.sh`) | `Agent` tool, `TeamCreate`, `SendMessage` | Multi-agent coordination with named agents, message passing, background execution. Our shell wrappers become unnecessary. |
| **Lightweight note capture** (#5) | Native task system | A `/work note` feature would just be `TaskCreate` with a "note" tag. Don't build this. |

### Likely Absorbed Within 6-12 Months

| Our Feature | Why It's Coming | Recommended Action |
|---|---|---|
| **Recurring WRK templates** (#12) | `CronCreate`, `CronDelete`, `CronList` are deferred tools. Scheduling is clearly on the roadmap. | Don't build. Wait for native crons. |
| **Dependency tracking** (`blocked_by`, auto-unblock) (#1, #10) | Task system will inevitably add dependencies. Every PM tool does. Linear CLI already has this. | Build auto-unblock (#1) as a simple script now — it's cheap. But don't invest in DAG visualization (#10) — that's coming natively. |
| **NLP task capture** (#15) | Claude Code already parses natural language. Structured task extraction from conversation is trivial to add. | Don't build. Already happens implicitly when the agent calls `TaskCreate`. |
| **Progress/velocity reporting** (#7) | Once tasks exist natively, dashboards follow. GitHub Copilot Workspace already shows progress. | Build a thin `/work progress` script now for immediate value, but expect it to be replaced. |
| **Session persistence browser** | `--resume` already browses sessions. Will get richer with search, filtering, project-scoping. | Don't build. |
| **Context budget monitor** (#11) | `PreCompact` hook exists. Native context health signals are the obvious next product step. | Build as a hook now — it's 20 lines of shell. Cheap to discard when native version ships. |
| **Checkpoint with structured state** (#9) | Session persistence will get richer — decisions, blockers, context summary are natural extensions of `--resume`. | Add `decisions:` and `blockers:` to checkpoint.yaml now for immediate value. Low cost to maintain. |

### Safe to Build — Our Moat (Won't Be Absorbed)

These are domain-specific workflow features. Claude Code builds **primitives**; these are **policies** and **process IP** that run on top of primitives.

| Our Feature | Why It's Safe | Proposed Enhancement |
|---|---|---|
| **20-stage lifecycle with evidence gates** | Too domain-specific. No product ships a 20-stage engineering workflow. This is our process, not a platform feature. | Continue investing. Core competitive advantage. |
| **Urgency scoring** (#6) | Taskwarrior-style weighted scoring with *our* coefficients. Generic priority != our priority. Platform will offer basic priority; we need custom weighting. | **Build this.** High-value, script-only, permanent. |
| **Complexity routing** (Route A/B/C) (#8) | Our calibrated judgment about what needs planning vs. what doesn't. Platform might offer something generic, but ours is tuned to our work. | **Build this.** `assign-routes.sh` with our heuristics. |
| **Cross-provider review** (Codex hard gate) | Anthropic won't build "use Codex to review Claude's work." The pattern of multi-pass review with fresh context maps to Agent teams, but the *policy* is ours. | Continue investing. |
| **Legal compliance scanning** | Deny-list, client reference prevention — our business risk, not a platform feature. | Already built. Maintain. Wire into close (#3). |
| **Gate evidence verification** (`verify-gate-evidence.py`) | Our quality contracts. Script-enforced stage exit criteria. | Continue investing. |
| **Feature WRK decomposition** (parent/child) | Opinionated epic → child breakdown with our naming/scope rules. | Continue investing. |
| **Cost attribution per WRK** | Per-task token economics. Platform shows usage but not per-task attribution. | Already built. Maintain. |
| **Wave-based parallel execution** (#14) | Orchestration *logic* on top of native teams. The wave grouping algorithm and file-ownership conflict detection are ours. | **Build this.** Uses native `Agent`/`TeamCreate` underneath but the wave logic is permanent. |
| **Auto-unblock on archive** (#1) | Lifecycle hook specific to our queue structure. | **Build this.** Cheap, permanent, script-only. |
| **Feature auto-close** (#2) | Our parent/child lifecycle policy. | **Build this.** Cheap, permanent. |
| **Ghost pending sweep** (#4) | Our queue hygiene policy. | **Build this.** Cheap, permanent. |
| **Legal scan gate in close** (#3) | Our compliance policy. | **Build this.** Cheap, permanent. |
| **Estimation tracking** (#13) | Per-route calibration with our complexity tiers. | Build when needed. Medium value. |
| **O*NET tagging / observed-exposure** | Labor economics research. Deeply domain-specific. | Continue investing. |
| **Machine-partitioned ID ranges** | Multi-workstation coordination specific to our setup. | Already built. Maintain. |

### Revised Investment Priority

Based on cannibalization risk, re-ordered from the original proposal:

| Priority | # | Enhancement | Rationale |
|---|---|---|---|
| **BUILD NOW** | 1 | Auto-unblock on archive | Cheap, permanent, lifecycle hook |
| **BUILD NOW** | 2 | Feature auto-close | Cheap, permanent, lifecycle hook |
| **BUILD NOW** | 3 | Legal scan in close | Cheap, permanent, compliance policy |
| **BUILD NOW** | 4 | Ghost pending sweep | Cheap, permanent, queue hygiene |
| **BUILD NOW** | 6 | Urgency scoring | High-value, our coefficients, permanent moat |
| **BUILD NOW** | 8 | Route auto-classify | Our heuristics, permanent moat |
| **BUILD CHEAP** | 9 | Decision/blocker log | Low-cost schema addition; may be superseded but useful now |
| **BUILD CHEAP** | 11 | Context budget monitor | 20-line hook; discard when native ships |
| **BUILD CHEAP** | 7 | Single-WRK progress | Thin script; expect replacement but useful today |
| **BUILD LATER** | 14 | Wave-based parallel execution | High-value moat but complex; wait for native teams to stabilize |
| **BUILD LATER** | 13 | Estimation tracking | Medium value; no urgency |
| **DON'T BUILD** | 5 | Note capture | Native `TaskCreate` covers this |
| **DON'T BUILD** | 10 | Dependency DAG viz | Native task dependencies coming |
| **DON'T BUILD** | 12 | Recurring templates | Native `CronCreate` coming |
| **DON'T BUILD** | 15 | NLP task capture | Native LLM parsing already does this |

## 6. Architecture Principle

All enhancements should follow the existing pattern: **scripts over LLM overhead**. Each feature should be a deterministic script called from the lifecycle, not LLM prose reasoning. The urgency scoring, auto-unblock, and wave grouping are all script-first by nature.

**Platform migration strategy:** As Claude Code primitives mature, migrate plumbing (task CRUD, session resume, agent dispatch) to native tools. Keep workflow orchestration (lifecycle stages, gate contracts, routing policies, compliance checks) as our scripts/skills layer on top. The primitives change; the policies persist.

GSD's key insight — thin orchestrator / fat agent with context isolation — aligns with our existing orchestrator pattern. Their wave-based parallelism is the most technically interesting feature we lack, and it's firmly in "our moat" territory since it's orchestration logic, not a platform primitive.
