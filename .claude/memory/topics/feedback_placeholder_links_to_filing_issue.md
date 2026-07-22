> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-22
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_placeholder_links_to_filing_issue.md

---
name: feedback_placeholder_links_to_filing_issue
description: "For missing/incomplete data in a UI feature, render a VISIBLE placeholder that links to a filed gh issue describing the work needed — don't silently omit"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b5f8ff27-c366-49c4-8c3b-a8550b73610e
---

**2026-07-11 (Vamsee, during #951 landman planning):** "For the P&A or any other feature,
keep placeholder and show actions required via gh issue so we can round up the work nicely
so we can get help from anybody who can help us."

**Why:** silent omission (the honesty default until now) hides the gap; a visible placeholder
that links to a grabbable issue turns each data gap into rounded-up, delegable work anyone can
pick up. The live UI itself becomes a worklist surface.

**How to apply:** when a feature's data is thin/absent (e.g. BSEE lease status/dates/working
interest not in committed data; well-plugging P&A not attributable per field):
1. Build the feature with what data DOES exist.
2. For each missing attribute, render a **visible placeholder cell** ("— pending <X> ingest")
   — NOT an omitted row/field.
3. File a `cat:data` (or appropriate) gh issue documenting the ACTIONS REQUIRED to fill it
   (source URL if known, join path, consumer), per [[feedback_document_discovered_data_sources_as_issues]].
4. **Link the placeholder to that issue** so a viewer/contributor can grab the work.

Extends the honesty discipline: not only "don't over-claim" but also "don't hide the gap —
publish it as grabbable work." Complements [[feedback_unique_live_links_traffic_credibility]]
(every gap = a front door to its filling-issue). First applied: #951 landman lease panel
(status/dates/WI placeholders → filing issue) + retroactive well-P&A ingest issue for #949.
