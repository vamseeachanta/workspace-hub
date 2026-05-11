---
name: llm-wiki V18 corpus-freeze
description: V18 corpus-freeze declared 2026-05-10 (iter-60); 335 pages; cron-only mode; V19 audit 2026-06-09; pending URL decisions queued for V19 application
type: project
originSessionId: 0bbe01ec-b9f9-43e1-9c62-edf7ad841eba
---
V18 corpus-freeze declared 2026-05-10 06:50 UTC at iter-60 of llm-wiki (vamseeachanta/llm-wiki). 38-iter active development complete (iter-22 → iter-59). 4-of-4 quality-closure criteria CLOSED:

- Orphans = 0
- Unidir-bridges = 0 (34 bidirectional)
- Frontmatter = 100%
- Link-integrity = 100.000%

Final state: 335 pages (eng-stds 220 + lng-projects 30 + maritime-law 84 + engineering 1) + 20 audit files (V1-V18 + W251-W253 reports + SESSION-ARC retrospective).

**Why:** corpus quality stable; further substrate-fill is marginal-completionism. Project shifts to cron-only mode for drift detection.

**How to apply:**

1. **V19 audit calendared 2026-06-09** (~30 days from freeze). Drift-check on bridge-symmetry, frontmatter, link-integrity, orphan count, page count. V19 only — not a new development iter.

2. **Drift-tolerance bands** (any breach triggers V19 audit response): link-integrity <99%, orphans >3, bridges <30, frontmatter <95%, page-count drift >10%.

3. **Pending URL decisions, queued for V19 application** (recorded 2026-05-10 from W266 reviewer judgment calls):
   - `hague-visby` public_url → **CMI (comitemaritime.org)** — drafter > depositary for doctrinal cite
   - `opa-90` public_url → **Cornell LII (law.cornell.edu)** — statute text > agency-portal implementation context
   - `api-std-625` public_url → **API official (api.org)** — paywalled product page; publisher-of-record provenance
   - `sigtto-mooring-equipment` public_url → **SIGTTO (sigtto.org)** — paywalled product page; publisher-of-record provenance

   Pattern across all four: publisher-of-record over secondary distributor. Heuristic preserved for future standards-citation decisions.

4. **V18 anti-recommendations binding future agent activity** (10 rules, do not violate without explicit user signal):
   1. No scope creep beyond user-signaled work
   2. No ad-hoc active-iter reopening (cron-mode only)
   3. No marginal completionism
   4. No W227 marine-insurance resurrection without explicit user signal
   5. No skill-artifact recommit without source-change
   6. No new-domain pivot absent downstream-traffic justification
   7. No 27th+ cross-wiki bridge (saturated at 26-34 depending on count method)
   8. No 4th-wiki creation
   9. No depth-pilot expansion past 30-page wave
   10. No substrate-fill past iter-58 closure

5. **W227 retired doctrinal arcs** (deferred 2026-05-10, no signal yet):
   - Marine-insurance arc: MIA-1906 + ITC-Hulls + IHC-2003 + IG pooling + 7 sub-doctrines, ~1-iter, 15 cross-wiki bridges into maritime-law projected
   - Offshore-decommissioning arc: OSPAR 98/3 + IMO A.672(16) + BSEE 30 CFR 250 + DNV-OS-F211, ~1.5-iter

6. **Methodology codified as workspace-hub skill**: `.claude/skills/coordination/oss-wiki-development-arc/` (7 files, ~702L) — committed in workspace-hub `6caba5fc9` (provenance commit `e489288b0`). Projects 3-4× compression on future wiki-spinouts (12-15 iters vs 38).

7. **Last commit on llm-wiki main**: `23f3251d` "🎉 CORPUS-FREEZE-DECLARED iter 60 — V18 + portability fix + session retrospective" (pushed to vamseeachanta/llm-wiki).

8. **Key resume-context files**:
   - Session retrospective: `wikis/_audit/SESSION-ARC-iter22-iter59-RETROSPECTIVE.md` (260L)
   - Corpus-freeze declaration: `wikis/_audit/iter-60-W267-cross-wiki-audit-v18-CORPUS-FREEZE.md` (259L)
   - W227 doctrinal-arc seed brief: `wikis/_audit/iter-49-W227-doctrinal-arc-seed-brief.md` (177L)
