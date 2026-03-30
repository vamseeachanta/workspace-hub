# Phase 5: Nightly Research Automation - Context

**Gathered:** 2026-03-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Keep PROJECT.md and domain context enriched automatically via scheduled GSD researcher agents running nightly. Output to `.planning/research/` for periodic review. Domain-specific research: new standards, competitor tools, industry trends. UAT: nightly job running, research artifacts accumulating, at least one insight actioned.

</domain>

<decisions>
## Implementation Decisions

### Research Domains & Rotation
- **D-01:** Expand from 3 domains to 4: standards, python-ecosystem, ai-tooling, and **competitor/market** (focused on competing software tools: Sesam, SACS, OrcaFlex, Flexcom, ANSYS updates, feature gaps, pricing changes, new capabilities).
- **D-02:** Weekday-only schedule with one domain per day + synthesis: Mon=standards, Tue=python-ecosystem, Wed=ai-tooling, Thu=competitor/market, Fri=synthesis. Sat/Sun=off (no API cost on weekends).

### Insight Actioning Workflow
- **D-03:** Manual weekly review of the Friday synthesis report. User reviews, picks insights to promote to PROJECT.md or create GitHub issues.
- **D-04:** "Insight actioned" for UAT = promoted to PROJECT.md (updating context) OR becomes a tracked GitHub issue. Concrete, verifiable bar.
- **D-05:** Synthesis report includes a structured action table at the top: `| Finding | Impact | Action | Status |` for quick scan and triage.

### Reliability & Monitoring
- **D-06:** Staleness alert: if no new research artifact appears within 36 hours, trigger a notification via notify.sh. Catches silent failures (cron not running, machine down).
- **D-07:** Staleness check runs as a **separate lightweight cron job** (e.g., 06:00 UTC) — not embedded in the researcher script. This detects cases where the researcher script itself doesn't execute.
- **D-08:** 90-day auto-prune for daily research artifacts. Weekly synthesis files kept longer. Add a cron entry or integrate into existing retention logic.

### Research Depth & Quality
- **D-09:** Enable web search for all domains (`--allowedTools WebSearch` or equivalent). Critical for recency — CVE advisories, release notes, standard updates.
- **D-10:** Feed prior research artifacts (last week's outputs) as additional context so the model builds on prior findings, avoids repetition, and tracks evolving trends.
- **D-11:** Use Haiku for daily domain scans (cheaper, sufficient for scanning + summarizing). Use Sonnet for Friday synthesis (deeper cross-domain analysis).
- **D-12:** Basic structure validation after generation: check output has Key Findings, Relevance, and Recommended Actions sections. Reject and retry once if sections are missing. No URL verification.

### Claude's Discretion
- Exact web search tool invocation mechanism (depends on claude CLI capabilities at implementation time)
- How prior research artifacts are assembled into context (full text vs summaries)
- Staleness check script implementation details
- Pruning mechanism (cron entry vs script)
- Competitor/market prompt design (specific tool names to track, comparison angles)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing nightly researcher infrastructure
- `scripts/cron/gsd-researcher-nightly.sh` — Current researcher script with domain rotation, context assembly, error handling, notifications
- `.planning/research/README.md` — Documents rotation schedule, output format, review process, manual run instructions
- `config/scheduled-tasks/schedule-tasks.yaml` — Single source of truth for all scheduled tasks; contains `gsd-researcher` entry at 01:35 UTC

### Supporting scripts and config
- `scripts/cron/setup-cron.sh` — Installs crontab entries from schedule-tasks.yaml; auto-detects machine role
- `scripts/cron/crontab-template.sh` — Legacy reference for cron schedule (read-only, canonical source is schedule-tasks.yaml)
- `scripts/notify.sh` — Notification dispatch (used for failure alerts)
- `scripts/lib/workstation-lib.sh` — Workstation variant detection (full/contribute/contribute-minimal)

### Existing research artifacts (reference for format)
- `.planning/research/2026-03-26-standards.md` — Example daily artifact
- `.planning/research/2026-03-29-synthesis.md` — Example synthesis artifact

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/cron/gsd-researcher-nightly.sh` — Fully functional researcher script; needs modifications for 4-domain rotation, web search, model selection, validation, and richer context
- `scripts/notify.sh` — Notification dispatch already supports cron source with pass/fail
- `scripts/lib/workstation-lib.sh` — Machine role detection (researcher already uses `ws_is "full"` guard)
- `config/scheduled-tasks/schedule-tasks.yaml` — Declarative task registry; new staleness-check job goes here

### Established Patterns
- Domain rotation via `$DAY_NUM` case statement in the researcher script
- Context assembly by concatenating planning docs as `--- filename ---` delimited blocks
- Git commit + push after each artifact (best-effort, tolerates failures)
- Notification via `scripts/notify.sh cron <job-id> pass|fail "<message>"`
- Schedule declaration in YAML with `machines`, `requires`, `prefer`, `is_claude_task` fields

### Integration Points
- Crontab installed by `setup-cron.sh` reading `schedule-tasks.yaml`
- Research artifacts committed to `.planning/research/` and pushed to origin
- Researcher uses `claude` CLI (must be in PATH, checked with `command -v`)
- Failure notifications integrate with existing notify.sh infrastructure

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches within the decisions above.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 05-nightly-research-automation*
*Context gathered: 2026-03-29*
