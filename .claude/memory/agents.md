# Agent Workflow Facts

> Git-tracked. Applies to all AI agents working in this repo on any machine.
> Refreshed by `scripts/memory/bridge-hermes-claude.sh` — edit the template,
> not the generated file.

<!-- BRIDGE:START — do not edit below this line, managed by bridge script -->

## Synced from Hermes Memory (2026-04-30)

### Environment Facts

- `claude auth login` — self-serve via browser tools. NEVER use API key auth (ANTHROPIC_API_KEY) without explicit user permission — subscription mode only.
- Business Brain: AI provider credits are no longer the bottleneck; harness/plan-prep/execution throughput is. Claude Max is $200/mo, Gemini is ~$20/mo, and weekly limits should be deliberately spent on useful planning/review/execution work even if credits run out for up to ~2 days before reset. Hermes on ace-linux-1 is the primary AI-agent control surface for approvals/decisions/GitHub mutations and continuous lane reconciliation; ace-linux-2 is overflow worker capacity after repo/tool/auth checks.
- Elements→/mnt/ace ingest conventions: canonical layout is /mnt/ace/<repo-name>/<domain>/; `client_projects` is a real repo bucket; Woodfibre uses repo bucket `acma-projects` (not `acma_projects`) with project code 31522; `qgis` is reusable digitalmodel workflow/data; `casa_grande_77017` belongs under `assethold`; staging folders use `_from_elements/` without dates.
- Telegram/Hermes mobile bot branding chosen: “AceEng Bot” with username “AceEngBot” preferred; fallback names include AceEngineerBot, AceEngAIBot, AceEngineerAIBot, AceOpsBot.
- Telegram/Hermes mobile bot actual username created: @AceEngineerBot / t.me/AceEngineerBot. Initial token was pasted into chat and should be treated as compromised; rotate via @BotFather before configuring Hermes.
- Codex is also on a USD $200 membership with roughly 85% usage left; quota reset time reported as April 5 at 12 PM.

### User Profile

- User requires zero-waste AI spend; ace-linux-1 is Hermes control plane, ace-linux-2 overflow needs repo/tool/auth checks before delegation.
- Prefers numbered/lettered choices, tables where helpful, one-by-one execution, clickable GitHub links for #NNNN. Vamsee: P.E., 23yr exp; ACE Engineer consulting; target $120K/yr retainers; domains OrcaFlex/mooring/riser/FEA/cathodic/API 579/Python; GTM offshore 10-50 engineers. Wants continuous autonomous GitHub throughput with Claude/Codex/Gemini adversarial plan/code reviews; GitHub latest status:* wins; direct execution, proactive follow-ups, safety audits, parallel work, and direct plan-approved transitions/local markers when explicitly approving batches. Hard gates should evolve into evidence-threshold gates once metrics prove safe, so user focuses on idea origination, GTM throughput, and customer/prospect artifacts. Weekly GTM targets should be set interactively then executed by agents. Session exits need GH evidence, handoff artifact, fresh-session copy/paste prompt, worktree verification, and next priorities.
- User prefers post-reboot recovery triage in this order: salvage current work first, research/restart ongoing work second, then set off future work.


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
- Plans live in `.planning/` within each repo *verified: 2026-05-02*
- Long-duration plans live in `docs/plans/`
- Use `/gsd:*` commands for task management

## Skill System (Hermes)

Hermes maintains 691+ skills at `~/.hermes/skills/` on ace-linux-1. *stale: 2026-05-02*
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
