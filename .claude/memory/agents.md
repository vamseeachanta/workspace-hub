# Agent Workflow Facts

> Git-tracked. Applies to all AI agents working in this repo on any machine.
> Refreshed by `scripts/memory/bridge-hermes-claude.sh` — edit the template,
> not the generated file.

<!-- BRIDGE:START — do not edit below this line, managed by bridge script -->

## Synced from Hermes Memory (2026-04-05)

### Environment Facts

- AI: $269/mo. Claude Max $200, 2x Codex $20 each, Gemini Pro $20. Overnight: use Hermes subagents. Gemini needs --yolo.
- ace-linux-1: real workspace is /mnt/local-analysis/workspace-hub (git repo). ~/workspace-hub is sparse overlay — write to /tmp/ then move.
- Always `uv run` for Python — never `python3` or `pip`. On Windows (licensed-win-1) use `python`.
- digitalmodel/ is a separate git repo (gitignored). Commits must be from within digitalmodel/ dir, not workspace-hub root.
- Legal scan: .legal-deny-list.yaml (15 client patterns). MANDATORY for doc-intelligence and resource work. scripts/legal/legal-sanity-scan.sh. Catalogs (dde-*, conference-*) excluded.
- aceengineer-strategy/: GTM, $120K retainer target, 20+ prospects, scripts/gtm/job-market-scanner.py Mon cron. Aceengineer.com consulting, 23yr P.E. exp.
- Hermes: 5 external_dirs repos, 691 skills. Nightly cron: export+sync+drift. Key frontmatter: skills context:fork paths effort model hooks.
- OCR punted by user (#1643, #1772). Skip image-based PDFs in Phase B.

### User Profile

- Context parity mandate: corrections in one agent sync to ALL others. Zero waste across all AI subscriptions ($269/mo total).
- Overnight batch execution: 3 self-contained prompts, zero git contention, no user interaction, git contention avoidance map always included.
- Adversarial review at BOTH stages: plan review AND code/artifact review. All agents: Claude, Codex, Gemini.
- Vamsee: P.E., 23yr exp. ACE Engineer consulting. $120K/yr retainer. OrcaFlex/mooring/riser/FEA/cathodic/API 579/Python. GTM: offshore 10-50 engineers.


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
