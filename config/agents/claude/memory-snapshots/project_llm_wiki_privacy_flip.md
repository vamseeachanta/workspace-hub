---
name: llm-wiki-privacy-flip
description: vamseeachanta/llm-wiki flipped public→private 2026-05-20; codes/standards data + client work now lives at full fidelity inside the private repo
metadata: 
  node_type: memory
  type: project
  originSessionId: 301086a5-63fe-4d73-a934-dd43ff2f9c0d
---

`vamseeachanta/llm-wiki` is **PRIVATE** as of 2026-05-20 21:30 CT. The 2026-05-05 public spinout decision (#2398 override) was reversed by the user to close the licensing window for vendor-licensed codes and standards content (OCIMF MEG3/MEG4 Annex A pilot).

**Why:** the public posture forced per-page `extraction_policy: metadata-only` + `raw_copy_allowed: false` + `## Boundary` patterns on every standards page, blocking the full-fidelity ingest the user wanted for client work. Going private removes the public-redistribution risk and lets verbatim convention text, digitized coefficient tables, and figure-derived content all sit in the repo. User framing: "get clients and go with full flow."

**How to apply:**
- All codes/standards data (OCIMF, API, DNV, ABS, IACS UR, ASCE, ASME, ISO, BS EN, SOLAS, MARPOL) routes to private llm-wiki per [[codes-standards-data-in-private-wiki]]
- Client project names (B1528, SIROCCO, acma-projects) no longer require abstraction inside llm-wiki — the abstraction gate (Skill D) only applies when promoting to a public surface, and there is no public llm-wiki anymore
- Cross-repo references from workspace-hub/digitalmodel to llm-wiki will 404 for unauthenticated readers; intentional, by design
- `digitalmodel`-pip-install users get `CitationResolutionError` for citation lookups unless they configure `LLM_WIKI_PATH` to a local clone; intentional gating
- Forks/stars at flip time: 0 each; no external dependents to coordinate
- The two now-private commits with public history: `9b3481c9` (OCIMF MEG3/MEG4 standards resolver pages, 2026-05-20 14:22) and `ac6fb7a1` (naval-architecture OCIMF methodology pages, 2026-05-20 18:30). The pre-flip license (MIT + CC-BY-4.0) survives on cloned copies; going-forward content is sealed.

**Supersedes:**
- [[project_llm_wiki_spunout]] — full supersede; public spinout is reversed
- [[project_llm_wiki_strategic_role]] — partial supersede; "public + legally-sanitized" thesis replaced by "private + full-fidelity"
- [[project_llm_wiki_external_post_ingest_workflow]] — workflow continues but landing target is now private; no public-share reciprocity for ingested LinkedIn/blog content

**Related:**
- Routing rule: `.claude/rules/codes-standards-data-routing.md`
- Calc-citation contract unchanged: `.claude/rules/calc-citation-contract.md`
- Source PDFs continue to live at `/mnt/ace/acma-codes/<code>/` (canonical) per [[offrepo_intel_routing]]
