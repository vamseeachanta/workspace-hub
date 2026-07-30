> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-30
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_document_discovered_data_sources_as_issues.md

---
name: feedback_document_discovered_data_sources_as_issues
description: "Owner directive 2026-07-06: any data source discovered during research gets documented immediately as a GitHub data issue for future ingestion"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 4aef446e-8ae6-4fa4-8a87-b5d9afe883d1
---

While researching/working, whenever we come across data sources we don't yet ingest, document them **immediately as GitHub data issues** so they can be picked up in the future — don't let them evaporate with the session.

**Why:** research sessions surface valuable source URLs/artifacts as side-effects (e.g., the BOEM FieldReserves family found while planning wed #847). Without a durable GitHub record they must be re-discovered. Issues are the ecosystem's actionable queue; memory files are not dispatchable.

**How to apply:** file one issue per source *family* (not per file) in the owning repo, labeled `cat:data` + `domain:ingest`, with a table: source | URL (verified live, with date) | what it gives | candidate consumer. Reference the issue that triggered the discovery. Pilot: [wed #855](https://github.com/vamseeachanta/worldenergydata/issues/855) (BOEM FldMoPro / Hist / mastprod / appendix B / annual vintage pages, found during [[project_completion_dc_reconciliation_wo_article]] #847 planning).
