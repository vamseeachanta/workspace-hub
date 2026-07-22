> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-22
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_opportunity_data_to_aceengineer_strategy.md

---
name: feedback-opportunity-data-to-aceengineer-strategy
description: ALL opportunity data — full-time job applications AND consulting/BD leads — canonically lives in aceengineer-strategy (pipeline/); teamresumes keeps only the chronological application log + CV artifacts
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 6010c297-dfe1-4247-aa54-f3a21f1996f0
---

VA directive (2026-06-04, during Hanwha Ocean mooring applications): "all this data should go into aceengineer-strategy — whether it is fulltime job or more leads to get more work etc."

**Why:** Every job posting is simultaneously (a) a possible FT role and (b) a BD signal — a company staffing a discipline reveals a capability gap A&CE could fill as consulting/overflow work, plus toolchain/standards intelligence for future pitches. aceengineer-strategy/pipeline/ is the single funnel for both readings; splitting them across repos loses the lead.

**How to apply:** When capturing any job/opportunity:
1. Full capture → `aceengineer-strategy/pipeline/<company>-<role>-<date>.md` with an explicit FT-vs-lead classification table, fit notes, toolchain intel, and BD follow-through step (e.g., prospects.md entry).
2. `teamresumes/cv/va/applications-2026.md` gets the chronological log row + brief entry pointing at the canonical strategy file.
3. Update both on status change. Established pattern: Harbour Zama (2026-05-12) and Hanwha Ocean (2026-06-03) entries.

Related: [[project-hanwha-mooring-applications-pending]]
