# Agent Workflow Facts

> Git-tracked. Applies to all AI agents working in this repo on any machine.
> Refreshed by `scripts/memory/bridge-hermes-claude.sh` — edit the template,
> not the generated file.

<!-- BRIDGE:START — do not edit below this line, managed by bridge script -->

## Synced from Hermes Memory (2026-04-28)

### Environment Facts

- `claude auth login` — self-serve via browser tools. NEVER use API key auth (ANTHROPIC_API_KEY) without explicit user permission — subscription mode only.
- DEFAULT MODEL (2026-04-25): openai-codex/gpt-5.5 via chatgpt backend; smart_model_routing disabled. ace-linux-2 needs login shell (`bash -lc`) for Hermes/Codex PATH. Codex CLI 0.125 may hang at `Reading additional input from stdin...`; Hermes pattern: terminal(background=true) then `process close`.
- workspace-hub contains Claude orchestrator session logs at logs/orchestrator/claude/session_*.jsonl, useful for session corpus and prompt-pattern analysis.
- Hermes smart_model_routing is disabled in workspace-hub because cheap-model Gemini routing bypassed explicit Codex intent and hit Gemini 429 quota.
- Non-interactive Claude Code overnight runs may stall or become read-only unless permissions are preconfigured. For unattended execution, prefer stdin redirection (`< /dev/null`) and enable write permissions via `.claude/settings*.json` or `--dangerously-skip-permissions` only with explicit user approval.
- Gmail access is configured via Gmail API OAuth for all three accounts using ~/.gmail-ace/credentials.json, ~/.gmail-personal/credentials.json, ~/.gmail-skestates/credentials.json plus shared ~/.gmail-mcp/oauth-env.json. Himalaya config currently covers ace and personal only.
- digitalmodel repo has a working local virtualenv at /mnt/local-analysis/workspace-hub/digitalmodel/.venv. When `uv run pytest` fails due to pyproject dependency resolution conflict (`assetutilities` vs `deepdiff`), use `PYTHONPATH=src ./.venv/bin/python -m pytest ...` from the digitalmodel repo to run tests against the installed environment.
- In workspace-hub, scripts/enforcement/require-plan-approval.sh only recognizes .planning/plan-approved/*.md markers newer than .planning/STATE.md; a stale marker can block commits even when the GitHub issue is already status:plan-approved.
- Elements ingest /mnt/ace mapping: qgis → digitalmodel; Woodfibre 31522 → acma-projects; casa_grande_77017 → assethold; staging uses `_from_elements` without dates; client_projects is a real repo bucket, not a misc category.

### User Profile

- User requires zero-waste AI spend; ace-linux-1 is Hermes control plane, ace-linux-2 overflow needs repo/tool/auth checks before delegation.
- User wants continuous autonomous GitHub throughput: keep issues planned, adversarially reviewed, and user-approved so overnight planning/implementation can run and next-day review/QA has ready artifacts.
- Adversarial review at BOTH stages: plan review AND code/artifact review. All agents: Claude, Codex, Gemini.
- Vamsee: P.E., 23yr exp. ACE Engineer consulting. $120K/yr retainer. OrcaFlex/mooring/riser/FEA/cathodic/API 579/Python. GTM: offshore 10-50 engineers.
- Prefers numbered/lettered choices and clickable GitHub issue/PR links for #NNNN references.
- For overnight batches, prefers Claude-only staged pacing and preserving Codex for interactive/daytime work.
- User wants all reviews to be adversarial reviews by default for maximum productivity and impact.
- User approves sensible direct execution. GitHub: latest status:* wins, proactive follow-ups, quick safety audits, parallel work, and direct plan-approved transitions/local markers when explicitly approving batches. Travel-planning issues should include realistic seasonal photos plus destination/stay links and scenery caveats.
- Post-reboot recovery priority: salvage current work first, research/restart ongoing work second, set off future work last.


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
