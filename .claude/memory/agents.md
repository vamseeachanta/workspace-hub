# Agent Workflow Facts

> Git-tracked. Applies to all AI agents working in this repo on any machine.
> Refreshed by `scripts/memory/bridge-hermes-claude.sh` — edit the template,
> not the generated file.

<!-- BRIDGE:START — do not edit below this line, managed by bridge script -->

## Synced from Hermes Memory (2026-05-17)

### Environment Facts

- `claude auth login` — self-serve via browser tools. NEVER use API key auth (ANTHROPIC_API_KEY) without explicit user permission — subscription mode only.
- Workspace-hub tier-1 ecosystem scope includes eight repos: workspace-hub, digitalmodel, assetutilities, worldenergydata, llm-wiki, assethold, aceengineer-website, and aceengineer-strategy; user values general, per-repo, per-domain, execution-ready, approval-drift, and planning-needed boards for sequential review/refinement before multiagent execution.
- User prefers workspace-hub repo-sync/closeout reports to show referenced GitHub issues as clickable hyperlinks grounded via live `gh issue view`, not just issue numbers.
- workspace-hub/comprehensive-learning now has references/exit-handoff-closeout.md: concrete checklist for “document and prepare to exit” closeout (write docs/session-handoffs handoff, commit/push it, prove clean/synced repos, report no-external-action status).
- For GTM/prospect work, aceengineer-strategy is the repository of record for specific named prospects/contacts; generic reusable plans, collateral, and implementation work should live in the appropriate other tier-1 repos rather than storing person-specific details there.
- For repeated judge/checklist continuation prompts, user values fresh evidence artifacts/crosswalks, precise inventory/status reconciliation, and explicit blocked-stop decisions over relaunching implicit continuation work across human/governance/scope gates.
- Hermes runtime SOUL.md for this workspace is repo-backed: canonical file `/mnt/local-analysis/workspace-hub/config/agents/hermes/SOUL.md`, with `~/.hermes/SOUL.md` symlinked to it.
- CTV operability assets in digitalmodel are reference material for future vessel-operability ecosystem work; SeaOps is treated as a competitor, so use those assets for research and repo documentation only unless the user explicitly approves GTM/project reuse.
- ace-linux-2 is reachable by SSH from ace-linux-1 and has OpenFOAM ESI v2312 installed: wrapper `/usr/bin/openfoam2312`, bashrc `/usr/lib/openfoam/openfoam2312/etc/bashrc`, `WM_PROJECT_DIR=/usr/lib/openfoam/openfoam2312`, `WM_PROJECT_VERSION=v2312`.

### User Profile

- User requires zero-waste AI spend: consume weekly provider credits on useful approved work; prefers Tier-1 Kanban boards with provider/machine routing, decision lanes, hover summaries, and approve actions. In marine/offshore force reviews, user expects individual components and resultants compared side-by-side using existing basecase assumptions.
- User expects strict workflow compliance: meaningful work needs proper gates and adversarial review even for docs/reports/skills/non-code. Closeout must be transactional in-window: push to origin, branch/worktree disposition, clean-state proof or explicit evidence-preserving blocker; stale files/branches/worktrees after closure are workflow failures. “Document and prepare to exit” means a committed/pushed docs/session-handoffs report with repo states, dirty exceptions, no-external-action status, and next steps. Approval requests should be compact with GitHub links, current gate/status, exact recommended action, and what happens next. User wants llm-wiki maintained on a weekly freshness cadence for code-development leverage.
- When execution is interrupted by context/tool-call limits, user expects a concise, truthful handoff: current task state, verified evidence, blockers, exact next commands, and an explicit non-closeout if gates are incomplete.


<!-- BRIDGE:END -->

---

## User

Vamsee Achanta — Professional Engineer (P.E.), 23 years experience.
Runs ACE Engineer consulting (aceengineer.com).
Target: $120K/yr retainers, 3-5 clients = $360-600K ARR.
GTM: offshore engineering firms with 10-50 engineers.
Core expertise: OrcaFlex, mooring/riser, FEA, cathodic protection, API 579, Python automation.

## AI Subscriptions

| Agent | Cost | Notes |
|-------|------|-------|
| Claude Max | $200/mo max | Primary planning/orchestration subscription; Claude Code CLI |
| Gemini Google AI Pro | $20/mo | Research/recon and cross-review |
| Codex / OpenAI | Verify authenticated paid account(s) before load planning | Do not assume parallel paid seats without machine/auth evidence |

Context parity = compute parity. Zero waste everywhere.

## Workflow Rules

- **ace-linux-1 control surface**: keep user approvals, launch decisions, GitHub mutations, and cross-lane reconciliation on `ace-linux-1` unless explicit failover is chosen.
- **Overnight batch**: 3 self-contained prompts, one per terminal, zero git contention.
  Always include a git contention avoidance map.
- **Long-running lanes**: prefer named `tmux` sessions or Hermes-tracked background processes with logs under `logs/night-runs/` and prompt packs under `docs/plans/overnight-prompts/`.
- **Adversarial review**: BOTH stages — plan review AND code/artifact review.
  Minimum: Claude + Codex + Gemini all review.
- **Context parity**: Corrections made in one agent must propagate to all others.
- **GTM issue routing**: with GTM messages in view, convert each signal by updating an existing GitHub issue, reopening an existing issue, or opening a new one.
- **Code-readiness loop**: strengthen code with methodologies, standards, tests, and review artifacts before claiming delivery readiness.
- **Legal promotion gate**: before promoting raw-data-derived material into public `llm-wiki` pages or other artifacts, preserve engineering evidence boundaries and run legal sanity review/scan.
- **Autonomous gate evolution**: hard gates remain in force until metrics prove agent rigor is consistently safe; over time, shift routine plan/review/execution/verification cycles from user-managed approval to evidence-threshold approval so the owner focuses on ideas, GTM throughput, and customer/prospect artifacts.
- **No local task IDs**: Use GitHub issues directly (`gh issue list`).
- **Issue comments**: Always post a summary comment on every implemented GitHub issue.
- **Parallel work check**: Scan for in-flight sessions before starting GSD work.

## GSD Workflow

GSD is the sole workflow system since 2026-03-25.
- Plans live in `.planning/` within each repo
- Long-duration plans live in `docs/plans/`
- Use `/gsd:*` commands for task management

## Skill System (Hermes)

Hermes maintains 691+ skills at `~/.hermes/skills/` on ace-linux-1.
On non-Hermes machines, consult `.claude/skills/` in this repo for equivalent procedures.


### Harness Throughput Rule

Provider credits are not the current bottleneck. The harness must prioritize preparing plans, running adversarial reviews, executing approved work, and reconciling results so weekly provider limits do not reset unused. Latest user-provided headroom showed Claude weekly capacity still substantial (All models 38% used; Sonnet 7% used) and Codex weekly capacity mostly unused (89% overall remaining; GPT-5.3-Codex-Spark 100% remaining). Preserve enough emergency/approval capacity, but otherwise keep useful lanes fed; the owner can tolerate up to ~2 days of depleted credits near reset if durable work was produced.

### GTM → Knowledge → Code Readiness

GTM messages should update/reopen/create GitHub issues. Raw data and public data sources may feed `llm-wiki` with provenance, data, codes/standards references, and methodology, but public-facing pages/artifacts require legal sanity checks, sanitization, and explicit evidence boundaries. Code readiness comes from converting those methods into tests, fixtures, acceptance criteria, and bounded implementation plans.

### Weekly GTM Target Rule

Establish weekly GTM targets interactively with the owner, then turn them into bounded GitHub issues and agent-executable packets. Current/next seed: week of April 1 should produce vessel capability charts plus a strong brochure sent to all researched vessel contractors; agents should handle contractor research, list hygiene, capability-chart/brochure preparation, evidence-backed claims, and outbound/send tracking. This week should also include a review of the owner's full work pattern to suggest productivity hacks: audit recent sessions, GitHub throughput, GTM artifacts, handoffs, repeated friction points, and tool/provider bottlenecks, then propose changes that reduce owner orchestration time and increase GTM/artifact flow.

## ACE Engineer GTM Context

- `aceengineer-strategy/` — private nested repo with full GTM strategy
- 20+ prospects identified; ICP: offshore firms 10-50 engineers
- Demo reports: `digitalmodel/examples/demos/gtm/` (5 demos, `report_template.py`)
- Job market scanner: `scripts/gtm/job-market-scanner.py` (runs Monday cron)
- GTM control rule: continuous AI work should convert external signals, repo engineering work, and approved issue outputs into client-ready material, but keep engineering evidence boundaries explicit.
- Public-promotion rule: raw data may feed internal code/wiki preparation, but public `llm-wiki` and artifacts must carry provenance plus data/code/standards/methodology separation and pass legal sanity checks.
- Control-surface rule: `ace-linux-1` remains the approval and reconciliation surface while `ace-linux-1` / `ace-linux-2` long-running lanes keep planning, execution, review, and GTM packaging moving in the background.
