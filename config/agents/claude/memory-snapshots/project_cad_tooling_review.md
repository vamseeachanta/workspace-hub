---
name: CAD tooling review (CadQuery family)
description: 3 GH issues paused pending doc/resource intelligence (#2205) review; resume #2327 first (unblocks #2329)
type: project
originSessionId: b3c0e8c5-8113-46c9-bba2-515f9426df88
---
**PAUSED** — 3 GH issues created and revised 2026-04-17 around CadQuery / code-first CAD, but user wants to tackle them **after** reviewing the document/resource intelligence operating model (#2205).

## Issues (all at `status:plan-review`-equivalent readiness — no label exists yet)

- **#2327** — digitalmodel: CadQuery spike for parametric offshore geometry generation
  - 4-hour time-box, H-link mooring shackle family (4 MBL variants), AQWA `QPPL DIFF` pipeline
  - Go/no-go: <30 min to first STEP, <60 s regen, 2-of-4 AQWA passes
- **#2328** — CAD-DEVELOPMENTS: comparison — CadQuery vs build123d vs ReplicAD vs Open(Python)SCAD
  - Code-first tools only; 3 parts × 5 axes; LLM codegen protocol specified; decider named (14-day default-to-status-quo)
- **#2329** — Engineering methodology: code-first vs GUI CAD for offshore parametric families
  - **Blocked by #2327 and #2328** — do not start until siblings produce evidence
  - Reframed: find N-threshold empirically; Level-1 micro-skill or Level-2 script (Level-0 prose rejected per `.claude/rules/patterns.md`)

## Origin

HN thread 2026-04-16: https://news.ycombinator.com/item?id=47772725 (180 points, CadQuery / Python parametric CAD).

## Wiki pages created (and auto-sync committed for engineering)

- ✅ `knowledge/wikis/engineering/wiki/entities/cadquery.md` (tracked, committed via `2fbf50f9c`)
- ✅ `knowledge/wikis/engineering/wiki/sources/2026-04-17-hn-cadquery.md` (tracked, committed)
- ✅ `knowledge/wikis/engineering/wiki/index.md` + `log.md` updates (tracked, committed)
- ⚠ `knowledge/wikis/marine-engineering/wiki/entities/cadquery.md` + index + log — **gitignored** per `.gitignore:490`. Machine-local only. If resuming on a different machine, re-create from the engineering entity (or fix the gitignore for marine-engineering).

## Why

User explicitly deferred: "We will tackle this after we review all our document/resource intelligence." The operating model (#2205) governs how LLM-wikis and Resource/Document Intelligence compose — conclusions from that review may change framing for #2329 (methodology enforcement) in particular.

## How to apply

When doc/resource intelligence review (#2205 and descendants) concludes:
1. Re-read #2327 revised body and confirm scope still valid
2. Run `/gsd:plan-phase` or the plan-template workflow for #2327 first (unblocks #2329 along with #2328)
3. Consider whether #2329's "Level-1 vs Level-2" enforcement choice needs updating based on whatever enforcement patterns the doc/resource intel review endorsed
4. Adversarial review comments already exist on all three issues — see issue 2327/2328/2329 `#issuecomment-*` for the critique that drove the current revised bodies
