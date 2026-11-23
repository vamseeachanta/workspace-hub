# Nightly GSD Research

Automated research artifacts produced by `scripts/cron/gsd-researcher-nightly.sh`.

## Schedule

Runs weekdays at **01:35 UTC** via system cron. No runs on Saturday/Sunday. Logs: `logs/research/<date>.log`.

## Domain Rotation

| Day | Domain | Model | Focus |
|-----|--------|-------|-------|
| Mon | `standards` | Haiku | API, DNV, ABS, ISO -- offshore/subsea standards |
| Tue | `python-ecosystem` | Haiku | uv, dependencies, CVEs, packaging PEPs |
| Wed | `ai-tooling` | Haiku | Claude Code, GSD, MCP, Codex/Gemini CLI |
| Thu | `competitor-market` | Haiku | Sesam, SACS, OrcaFlex, Flexcom, ANSYS updates |
| Fri | `synthesis` | Sonnet | Weekly cross-domain summary with action table |
| Sat/Sun | -- | -- | Off (no API cost) |

## Output Format

Each daily artifact is `<date>-<domain>.md` with three required sections:

1. **Key Findings** -- 3-5 bullets with source references
2. **Relevance to Project** -- how each finding maps to a specific package or workflow
3. **Recommended Actions** -- checklist: promote to PROJECT.md, create GitHub issue, or ignore

Output is validated after generation. Missing sections trigger one automatic retry.

### Synthesis Format (Friday)

The Friday synthesis includes an **Action Table** at the top for quick triage:

| Finding | Impact | Action | Status |
|---------|--------|--------|--------|
| [finding] | High/Medium/Low | Promote / Issue / Monitor / Ignore | Pending |

Followed by Top 3 Insights, Cross-Domain Connections, and Detailed Action Items.

## Context Feeding

Each research run receives:
- `PROJECT.md` and `ROADMAP.md` as project context
- Last 7 days of prior research artifacts (all domains) to avoid repetition and track trends

## Review Process

1. **Weekly (Friday synthesis):** Read the `*-synthesis.md` file. Scan the Action Table for high-impact findings. (D-03)
2. **Act on recommendations:** (D-04)
   - **Promote to PROJECT.md** -- add finding to the relevant section (Engineering Domains, Tech Stack, Constraints)
   - **Create GitHub issue** -- use the recommended title from the action item; label `research-finding`
   - **Monitor** -- no action now; watch for developments next week
   - **Ignore** -- documented reasoning in the artifact
3. An insight is "actioned" when it is either promoted to PROJECT.md or tracked as a GitHub issue.

## Staleness Monitoring

A separate staleness check (`scripts/cron/research-staleness-check.sh`) runs daily at **06:00 UTC**. It alerts via `notify.sh` if no research artifact has been created within **60 hours**.

The 60-hour threshold (rather than 36h) accounts for the weekday-only schedule: Friday's artifact at 01:35 UTC is ~52 hours old by Monday 06:00 UTC.

## Artifact Retention

- **Daily artifacts** (`*-standards.md`, `*-python-ecosystem.md`, etc.): pruned after **90 days**
- **Synthesis artifacts** (`*-synthesis.md`): pruned after **365 days**

Pruning runs automatically at the end of each researcher execution.

## Manual Run

```bash
# Dry run (shows domain, model, budget, tools, context length -- no API call)
bash scripts/cron/gsd-researcher-nightly.sh --dry-run

# Full run
bash scripts/cron/gsd-researcher-nightly.sh

# Staleness check dry run
bash scripts/cron/research-staleness-check.sh --dry-run
```

## Cost Estimate

- **Daily scans (Haiku, 4x/week):** ~$1-3/month
- **Weekly synthesis (Sonnet, 1x/week):** ~$2-6/month
- **Total:** ~$3-9/month (guarded by `--max-budget-usd` per call)
