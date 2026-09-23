> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-31
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_rig_selector_capability_depth.md

---
name: feedback-rig-selector-capability-depth
description: "Owner direction on rig-selector evolution — onshore/offshore first filter, then equipment-level capability fields (cranes, generation, MPD) that define rig facilities"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 7619de1a-15ec-4e54-a4fc-1bece965f3e0
---

Owner direction (2026-07-13) on the Drilling Rig Selector (wed #991 / aceengineer.com):

1. **Onshore rigs belong in the same selector** — the FIRST filter is onshore vs
   offshore, then the rest of the choices cascade.
2. **PDF links are the floor, not the product** — expand extraction so insights come
   from the data itself. The facility-defining fields that "make a big difference":
   **crane capacity, moonpool sizes, rig generation, MPD presence** (managed
   pressure drilling — "very important"), and similar equipment-level capabilities.
   These define what work a rig can actually host.
3. Add more technical capabilities over time — this is an evolving surface, not a
   one-shot page.

**Why:** rig selection isn't just hull dimensions; the equipment spread (cranes for
deck ops, MPD for narrow-margin wells, dual-activity derricks, quarters) decides
whether a rig fits a program.

**How to apply:** when extending the spec parser/schema, prioritize equipment fields
over more hull numbers; surface every new field as a selector filter; keep
onshore/offshore as the top-level split. [[reference-vessel-fleet-data-locations]]
