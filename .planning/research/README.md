# Nightly GSD Research

Automated research artifacts produced by `scripts/cron/gsd-researcher-nightly.sh`.

## Schedule

Runs daily at **01:35 UTC** via system cron. Logs: `logs/research/<date>.log`.

## Domain Rotation

| Day       | Domain             | Focus                                             |
|-----------|--------------------|----------------------------------------------------|
| Mon / Thu | `standards`        | API, DNV, ABS, ISO — offshore/subsea standards     |
| Tue / Fri | `python-ecosystem` | uv, dependencies, CVEs, packaging PEPs             |
| Wed / Sat | `ai-tooling`       | Claude Code, GSD, MCP, Codex/Gemini CLI            |
| Sun       | `synthesis`        | Weekly cross-domain summary with ranked insights    |

## Output Format

Each artifact is `<date>-<domain>.md` with three sections:

1. **Key Findings** — 3-5 bullets with source references
2. **Relevance to Project** — how each finding maps to a specific package or workflow
3. **Recommended Actions** — checklist: promote to PROJECT.md, create GitHub issue, or ignore

## Review Process

1. **Daily (optional):** Skim the latest artifact for urgent findings (CVEs, breaking changes).
2. **Weekly (Sunday synthesis):** Read the `*-synthesis.md` file — it ranks the week's findings by impact and flags the top 3 for promotion.
3. **Act on recommendations:**
   - **Promote to PROJECT.md** — add finding to the relevant section (Engineering Domains, Tech Stack, Constraints).
   - **Create GitHub issue** — use the recommended title from the action item; label `research-finding`.
   - **Ignore** — no action needed; the reasoning is documented in the artifact.
4. **Prune:** Delete artifacts older than 90 days. The weekly synthesis preserves the important bits.

## Manual Run

```bash
# Dry run (shows domain, context length, output path — no API call)
bash scripts/cron/gsd-researcher-nightly.sh --dry-run

# Full run
bash scripts/cron/gsd-researcher-nightly.sh
```
