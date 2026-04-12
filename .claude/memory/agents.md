# Agent Workflow Facts

> Git-tracked. Applies to all AI agents working in this repo on any machine.
> Refreshed by `scripts/memory/bridge-hermes-claude.sh` — edit the template,
> not the generated file.

<!-- BRIDGE:START — do not edit below this line, managed by bridge script -->

## Synced from Hermes Memory (2026-04-10)

### Environment Facts

- `claude auth login` — self-serve via browser tools. NEVER use API key auth (ANTHROPIC_API_KEY) without explicit user permission — subscription mode only.
- DEFAULT MODEL (2026-04-09): openai-codex / gpt-5.4 via https://chatgpt.com/backend-api/codex. smart_model_routing disabled. quick/research/data use gpt-5.4-mini, code/review use gpt-5.4, batch uses gpt-5.2. fallback_model disabled/empty. Gemini and Copilot are explicit-use only; never automatic fallback/default.
- workspace-hub contains Claude orchestrator session logs at logs/orchestrator/claude/session_*.jsonl, useful for session corpus and prompt-pattern analysis.
- 2026-04-09: Hermes smart_model_routing with cheap_model=gemini caused short queries to bypass explicit Codex intent and fail on Gemini 429 free-tier quota; config changed to disable smart_model_routing and route quick/research/data/batch commands to openai-codex instead of gemini/copilot.
- Non-interactive Claude Code overnight runs may stall or become read-only unless permissions are preconfigured. For unattended execution, prefer stdin redirection (`< /dev/null`) and enable write permissions via `.claude/settings*.json` or `--dangerously-skip-permissions` only with explicit user approval. *stale: 2026-04-11*
- Gmail access is configured via Gmail API OAuth for all three accounts using ~/.gmail-ace/credentials.json, ~/.gmail-personal/credentials.json, ~/.gmail-skestates/credentials.json plus shared ~/.gmail-mcp/oauth-env.json. Himalaya config currently covers ace and personal only.
- In workspace-hub shell, `gsd` is not currently available as a PATH executable (`gsd --help` => command not found); use the documented planning workflow/templates directly unless the slash-command runtime is present.
- digitalmodel repo has a working local virtualenv at /mnt/local-analysis/workspace-hub/digitalmodel/.venv. When `uv run pytest` fails due to pyproject dependency resolution conflict (`assetutilities` vs `deepdiff`), use `PYTHONPATH=src ./.venv/bin/python -m pytest ...` from the digitalmodel repo to run tests against the installed environment.

### User Profile

- Context parity mandate: corrections in one agent sync to ALL others. Zero waste across all AI subscriptions ($269/mo total).
- Overnight batch execution: 3 self-contained prompts, zero git contention, no user interaction, git contention avoidance map always included.
- Adversarial review at BOTH stages: plan review AND code/artifact review. All agents: Claude, Codex, Gemini.
- Vamsee: P.E., 23yr exp. ACE Engineer consulting. $120K/yr retainer. OrcaFlex/mooring/riser/FEA/cathodic/API 579/Python. GTM: offshore 10-50 engineers.
- Prefers choices/options to be numbered or lettered for easy selection.
- Prefers preserving Codex credits for interactive/daytime work; for overnight parallel batches, favor Claude-only execution when feasible.
- For overnight Claude work, pace usage across the available window instead of front-loading it; prefer staged all-night execution.


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
| Claude Max | $200/mo | Primary; Claude Code CLI |
| Codex / OpenAI #1 | $20/mo | Cross-review, overnight batch |
| Codex / OpenAI #2 | $20/mo | Parallel overnight runs |
| Gemini Google AI Pro | $19.99/mo | Cross-review; needs `--yolo` flag |
| **Total** | **$269/mo** | Maximize all — no unused slots |

Context parity = compute parity. Zero waste everywhere.

## Workflow Rules

- **Overnight batch**: 3 self-contained prompts, one per terminal, zero git contention.
  Always include a git contention avoidance map.
- **Adversarial review**: BOTH stages — plan review AND code/artifact review.
  Minimum: Claude + Codex + Gemini all review.
- **Context parity**: Corrections made in one agent must propagate to all others.
- **No local task IDs**: Use GitHub issues directly (`gh issue list`).
- **Issue comments**: Always post a summary comment on every implemented GitHub issue.
- **Parallel work check**: Scan for in-flight sessions before starting GSD work.

## GSD Workflow

GSD is the sole workflow system since 2026-03-25.
- Plans live in `.planning/` within each repo
- Long-duration plans live in `docs/plans/` *verified: 2026-04-11*
- Use `/gsd:*` commands for task management

## Skill System (Hermes)

Hermes maintains 691+ skills at `~/.hermes/skills/` on ace-linux-1. *stale: 2026-04-12*
On non-Hermes machines, consult `.claude/skills/` in this repo for equivalent procedures.

## ACE Engineer GTM Context

- `aceengineer-strategy/` — private nested repo with full GTM strategy *verified: 2026-04-12*
- 20+ prospects identified; ICP: offshore firms 10-50 engineers
- Demo reports: `digitalmodel/examples/demos/gtm/` (5 demos, `report_template.py`)
- Job market scanner: `scripts/gtm/job-market-scanner.py` (runs Monday cron)
