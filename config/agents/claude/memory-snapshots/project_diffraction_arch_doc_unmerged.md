---
name: project_diffraction_arch_doc_unmerged
description: digitalmodel diffraction-domain architecture doc referenced by epic
metadata: 
  node_type: memory
  type: project
  originSessionId: d885c1e2-a484-4586-bc98-b319e83f6d3e
---

The epic #622 / #623 / #624 handoff points to `docs/domains/orcawave/DIFFRACTION_DOMAIN_ARCHITECTURE.html` as the architecture spec, but that file is **not on `main`** — it 404s. It was committed in `6d01048c` on branch `docs/orcawave-domain-architecture-and-scorecard` (also `origin/...`), never merged.

**How to apply:** to read it, `git show 6d01048c:docs/domains/orcawave/DIFFRACTION_DOMAIN_ARCHITECTURE.html`. §4 prescribes the `AssumptionRecord` shape (field/value/source/basis/reference/confidence); §5 lists the reference-data feeds (hull_library, rao_database, L00–L06 example sets, wamit_reference_loader) consulted in priority order exact→estimate→default. The companion `2026-05-27-issue-completeness-scorecard.html` is on the same commit. Relates to [[project_analysis_domain_objective]].
