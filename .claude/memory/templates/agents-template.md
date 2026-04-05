# Agent Workflow Facts

> Git-tracked. Applies to all AI agents working in this repo on any machine.
> Refreshed by `scripts/memory/bridge-hermes-claude.sh` — edit the template,
> not the generated file.

<!-- BRIDGE:START — do not edit below this line, managed by bridge script -->
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
- Long-duration plans live in `docs/plans/`
- Use `/gsd:*` commands for task management

## Skill System (Hermes)

Hermes maintains 691+ skills at `~/.hermes/skills/` on ace-linux-1.
On non-Hermes machines, consult `.claude/skills/` in this repo for equivalent procedures.

## ACE Engineer GTM Context

- `aceengineer-strategy/` — private nested repo with full GTM strategy
- 20+ prospects identified; ICP: offshore firms 10-50 engineers
- Demo reports: `digitalmodel/examples/demos/gtm/` (5 demos, `report_template.py`)
- Job market scanner: `scripts/gtm/job-market-scanner.py` (runs Monday cron)
