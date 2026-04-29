# Agent Workflow Facts

> Git-tracked. Applies to all AI agents working in this repo on any machine.
> Refreshed by `scripts/memory/bridge-hermes-claude.sh` — edit the template,
> not the generated file.

<!-- BRIDGE:START — do not edit below this line, managed by bridge script -->

## Synced from Hermes Memory (2026-04-29)

### Environment Facts

- `claude auth login` — self-serve via browser tools. NEVER use API key auth (ANTHROPIC_API_KEY) without explicit user permission — subscription mode only.
- Repo mission conventions: OGManufacturing code should centralize in digitalmodel while repo holds manufacturing/domain context and outputs reusable by other clients/teams; acma-projects is ACMA naval-architecture client project data/GTM delivery; doris is Doris engineering-consulting client project data; frontierdeepwater is startup project data and AceEngineer has 5% stake.
- ace-linux-2 has a GIS timelapse Python environment at /mnt/local-analysis/ace2-gis-timelapse/.venv with earthengine-api, geemap, rasterio, imageio, pillow, geopandas, shapely, folium, matplotlib, contextily, requests, numpy, and pandas installed; setup report/logs are under /mnt/local-analysis/ace2-worker-reports/ and /mnt/local-analysis/ace2-worker-logs/ for workspace-hub issue #2538.
- Repo mission conventions: investments is private short-lived triage for investment/deal files; all useful data must migrate to assethold or achantasdata with no information loss, manifest/provenance preserved, and repo retired within 3 months if possible.
- Repo mission conventions: rock-oil-field is active triage only; sanity-check all files, migrate useful code/data/analysis to Tier-1 repos (digitalmodel/assetutilities/worldenergydata as appropriate), preserve no-loss manifest, then archive/retire if possible.
- Repo mission conventions: sabithaandkrishnaestates supports investment/admin finance/tax/entity records; saipem is installation-contractor info extraction then archive/retire; sd-work is Sabitha Deepthimahanti bio/pharmacy docs only on request; seanation is client info extraction then archive.
- Business Brain: one confirmed paid Codex/OpenAI account ($200/mo); Hermes on ace-linux-1 is the primary AI-agent control surface for approvals/decisions/GitHub mutations and continuous lane reconciliation; ace-linux-2 is overflow worker capacity after repo/tool/auth checks. GTM loop should continually convert signals + repo evidence into engineering-bounded client-ready material. licensed-win-1 initially gets OrcaFlex/AQWA after readiness.

### User Profile

- User requires zero-waste AI spend; ace-linux-1 is Hermes control plane, ace-linux-2 overflow needs repo/tool/auth checks before delegation.
- Prefers numbered/lettered choices, tables where appropriate, one-by-one task execution, and clickable GitHub issue/PR links for #NNNN references.
- Vamsee: P.E., 23yr exp. ACE Engineer consulting. $120K/yr retainer. OrcaFlex/mooring/riser/FEA/cathodic/API 579/Python. GTM: offshore 10-50 engineers. Wants continuous autonomous GitHub throughput with adversarial plan/code reviews by Claude/Codex/Gemini; prefers Claude-only staged pacing overnight and preserving Codex for interactive/daytime work. User approves sensible direct execution; GitHub latest status:* wins, proactive follow-ups, quick safety audits, parallel work, and direct plan-approved transitions/local markers when explicitly approving batches. Post-reboot priority: salvage current work, then research/restart ongoing work, then set off future work.
- For session exits, user wants future GitHub issues created as needed, state documented in a handoff artifact, and verification performed rather than only a conversational summary.


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

- **ace-linux-1 control surface**: keep user approvals, launch decisions, GitHub mutations, and cross-lane reconciliation on `ace-linux-1` unless explicit failover is chosen.
- **Overnight batch**: 3 self-contained prompts, one per terminal, zero git contention.
  Always include a git contention avoidance map.
- **Long-running lanes**: prefer named `tmux` sessions or Hermes-tracked background processes with logs under `logs/night-runs/` and prompt packs under `docs/plans/overnight-prompts/`.
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
- GTM control rule: continuous AI work should convert external signals, repo engineering work, and approved issue outputs into client-ready material, but keep engineering evidence boundaries explicit.
- Control-surface rule: `ace-linux-1` remains the approval and reconciliation surface while `ace-linux-1` / `ace-linux-2` long-running lanes keep planning, execution, review, and GTM packaging moving in the background.
