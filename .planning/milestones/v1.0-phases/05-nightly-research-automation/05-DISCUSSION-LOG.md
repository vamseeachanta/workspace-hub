# Phase 5: Nightly Research Automation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-29
**Phase:** 05-nightly-research-automation
**Areas discussed:** Research domains & coverage, Insight actioning workflow, Reliability & monitoring, Research depth & quality

---

## Research Domains & Coverage

### Domain expansion

| Option | Description | Selected |
|--------|-------------|----------|
| Add competitor/market domain | Track Sesam, SACS, Flexcom, OrcaFlex, ANSYS updates — feature gaps, pricing, new capabilities | ✓ |
| Add client-vertical domain | Offshore/subsea industry news: projects, regulatory, decommissioning trends | |
| Current 3 domains are enough | Standards, python-ecosystem, ai-tooling cover the technical base | |

**User's choice:** Add competitor/market domain
**Notes:** Focused on competing software tools, directly informs digitalmodel roadmap.

### Schedule rotation

| Option | Description | Selected |
|--------|-------------|----------|
| One domain per weekday + synthesis | Mon=standards, Tue=python, Wed=ai-tooling, Thu=competitor, Fri=synthesis. Sat/Sun off | ✓ |
| Keep 7-day rotation, spread evenly | Each domain ~2x/week, synthesis Sunday | |
| You decide | Let Claude pick | |

**User's choice:** One domain per weekday + synthesis
**Notes:** Weekday-only reduces API cost; each domain gets dedicated focus day.

### Competitor domain focus

| Option | Description | Selected |
|--------|-------------|----------|
| Competing software tools | Track Sesam, SACS, OrcaFlex, Flexcom, ANSYS updates, feature gaps, pricing | ✓ |
| Broader market + tools | Software tools + industry trends, new projects, decommissioning wave, floating wind | |
| Industry news only | Project announcements, regulatory changes, contract awards | |

**User's choice:** Competing software tools
**Notes:** Direct product intelligence focus.

---

## Insight Actioning Workflow

### Promotion mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| Manual weekly review | Review Friday synthesis, pick insights for PROJECT.md or GitHub issues | ✓ |
| Semi-automated triage | Auto-create draft GitHub issues labeled 'research-finding', approve weekly | |
| Fully automated | High-confidence findings auto-promote without review | |

**User's choice:** Manual weekly review
**Notes:** Low automation, high signal. Matches existing README workflow.

### UAT acceptance bar

| Option | Description | Selected |
|--------|-------------|----------|
| Promoted to PROJECT.md or GitHub issue | Insight added to PROJECT.md or becomes tracked issue. Concrete, verifiable | ✓ |
| Any documented decision | Even 'ignore with reason' counts — proves findings are reviewed | |
| Must change code or config | Strictest: must result in code/config change | |

**User's choice:** Promoted to PROJECT.md or GitHub issue
**Notes:** Concrete and verifiable bar.

### Synthesis format

| Option | Description | Selected |
|--------|-------------|----------|
| Structured action table | Table at top: Finding / Impact / Action / Status. Quick scan format | ✓ |
| Keep current format | Current 'Top 3 Insights' + checklist is sufficient | |
| You decide | Let Claude pick best format | |

**User's choice:** Structured action table
**Notes:** Easier to scan and track during weekly review.

---

## Reliability & Monitoring

### Health awareness

| Option | Description | Selected |
|--------|-------------|----------|
| Staleness alert | Notify if no artifact within 36 hours. Catches silent failures | ✓ |
| Weekly health summary | Sunday synthesis reports success rate | |
| Current notify.sh is enough | Failures already send notifications | |

**User's choice:** Staleness alert
**Notes:** 36-hour threshold catches silent failures like cron not running or machine down.

### Staleness check location

| Option | Description | Selected |
|--------|-------------|----------|
| Separate lightweight cron job | New script at different time (06:00). Detects when researcher itself doesn't run | ✓ |
| Embedded in researcher script | Check overdue domains at end of each run | |
| You decide | Let Claude pick | |

**User's choice:** Separate lightweight cron job
**Notes:** Separate job can catch cases where the researcher script itself stops running.

### Artifact retention

| Option | Description | Selected |
|--------|-------------|----------|
| 90-day auto-prune | Delete dailies > 90 days, keep synthesis longer | ✓ |
| Keep everything | Never delete, git history preserves | |
| 30-day prune for dailies, keep synthesis | More aggressive pruning | |

**User's choice:** 90-day auto-prune
**Notes:** Matches existing README recommendation. Synthesis files kept longer.

---

## Research Depth & Quality

### Web search

| Option | Description | Selected |
|--------|-------------|----------|
| Enable web search | Use --allowedTools WebSearch for real-time CVE advisories, release notes, standard updates | ✓ |
| Training knowledge only | Keep simple, avoid API costs and flaky web results | |
| Web search for some domains only | Standards + python-ecosystem only | |

**User's choice:** Enable web search
**Notes:** Critical for recency focus — research needs current information.

### Context richness

| Option | Description | Selected |
|--------|-------------|----------|
| Add prior research artifacts | Include last week's artifacts so model builds on prior findings, avoids repetition | ✓ |
| Add REQUIREMENTS.md + module-registry | More targeted gap analysis, heavier context | |
| Current context is sufficient | PROJECT.md + ROADMAP.md is enough direction | |

**User's choice:** Add prior research artifacts
**Notes:** Enables trend tracking and avoids redundant findings across runs.

### Model selection

| Option | Description | Selected |
|--------|-------------|----------|
| Haiku for dailies, Sonnet for synthesis | Cheaper daily scans, deeper synthesis analysis | ✓ |
| Same model for everything | Simpler, consistent quality | |
| Always use Sonnet | Higher quality across the board, small nightly cost | |

**User's choice:** Haiku for dailies, Sonnet for synthesis
**Notes:** Cost-effective tiering; synthesis needs deeper cross-domain reasoning.

### Output validation

| Option | Description | Selected |
|--------|-------------|----------|
| Basic structure validation | Check 3 required sections present, retry once if missing | ✓ |
| No validation | Trust model output, weekly review catches issues | |
| Full validation with URL checks | Structure + verify cited URLs are reachable | |

**User's choice:** Basic structure validation
**Notes:** Catches malformed outputs without over-engineering.

---

## Claude's Discretion

- Web search tool invocation mechanism
- Prior research context assembly strategy
- Staleness check script implementation details
- Pruning mechanism (cron entry vs script)
- Competitor/market prompt design

## Deferred Ideas

None — discussion stayed within phase scope.
