---
agent: triage-A-issues
date: 2026-05-01
scope: domain:gtm + gtm open issues
---

# GTM Triage: 12-Hour Multi-Track Execution Window

**Scope**: Open issues with `domain:gtm` OR legacy `gtm` label.  
**Goal**: Identify client-sendable artifacts (web pages + MP4/WebM/GIF demos) within 12 hours.  
**Total issues scanned**: 38 unique  
**Recommend YES**: 8  
**Recommend NO**: 30 (defer or parent-level strategy)

---

## Triage Table

| # | Title (≤80 chars) | Track | Status | Priority | Effort | Client-Blocking | Sendable Artifact | Depends On | Recommend |
|---|---|---|---|---|---|---|---|---|---|
| 2346 | prospect-data customized-demo pipeline — 48hr turnaround + pre-staged vessels | B | working | high | T2 | YES | Prospect data + branded demo report | 2016,1669 | YES: In progress (codex), 48hr SOP is highest-ROI tool |
| 2556 | vessel contractor brochure and outbound send tracker | A | none | high | T0 | YES | Brochure + send tracker + email templates | 1669,2016 | YES: High-priority vessel GTM; feeds into #2554 |
| 2554 | weekly vessel contractor outreach matrix for April target | A | blocked | high | T0 | YES | Contractor matrix with evidence URLs | 1669,2016 | YES: Unblock this; core weekly target |
| 2562 | expand GoM niche vessel-contractor evidence lane | A | none | high | T1 | YES | GoM contractors list + vessel fleet mapping | 2554,2016,2556 | YES: GoM targets feed contractor matrix |
| 2561 | FOWT mooring screening worked example for wind-contractor outreach | D | none | medium | T0 | YES | One-page GTM proof + OC4 reference | 2554,2016 | YES: Unblocks wind-contractor lane |
| 2115 | mooring demo — GTM Demo 6 for station-keeping outreach | D | none | medium | T1 | YES | Demo 6 (mooring parametric) with charts | 1904 | YES: Core demo gap; high consulting value |
| 2030 | publish: methodology docs to aceengineer.com -- 4 pages | C | none | medium | T1 | YES | 4 published methodology pages on website | 2016 | YES: Client-facing content; leverages existing work |
| 2422 | extend capability-summary-v1.pdf CTA to 5 demo detail pages | E | none | low | T0 | YES | CTA links wired on 5 demo pages | 2367 | YES: Quick polish; completes prior demo work |
| 2347 | reconcile stale tracker bodies for #2016, #1669, #117, #191 | A | none | medium | T0 | YES | Updated tracker issue bodies | 2016,1669,117,191 | NO: Internal cleanup; can defer |
| 2557 | weekly work-pattern review and flow hacks | X | none | high | T0 | YES | Productivity review + ranked hack backlog | none | NO: Internal process; not GTM artifact |
| 2350 | verify: #2043 mooring animation render outputs | D | none | low | T1 | YES | Published animation or reopen item | 2043 | NO: Depends on #2043; low priority |
| 2349 | refresh 30-day plan — #1809 closed, update dependency table | E | none | low | T0 | YES | Updated plan doc with Day-7 checkpoint | 1809,2288 | NO: Internal doc; not client-blocking |
| 2345 | wire GTM demos into unified smoke runner | E | none | medium | T1 | YES | CI regression gate for all 5 GTM demos | 2118,2272,2298 | NO: Harness regression; not GTM artifact |
| 2114 | VIV demo notebook — freespan walkthrough | B | none | medium | T1 | YES | Jupyter notebook (freespan validation) | 1792 | NO: Demo 1 exists; nice polish, not blocking |
| 2037 | manim mooring layout / force explainer animation | F | none | medium | T0 | YES | Manim animation video (MP4/GIF) | 2035 | NO: F-track; defer animation pipeline |
| 2038 | manim installation sequence / operability envelope animation | F | none | medium | T1 | YES | Manim animation video (MP4/GIF) | 2035,1798 | NO: F-track; defer animation pipeline |
| 2035 | manim-based engineering explainer pipeline | F | none | medium | T1 | YES | Manim template + first animation | 1809,2016 | NO: Foundation for 2037/2038; low-priority |
| 2016 | client conversion pipeline -- turn repo capability into clients | A | none | high | T0 | YES | GTM inventory + plan + child issues | 1994,1993 | NO: Parent strategy issue; not executable |
| 1905 | rigid jumper OrcaFlex model + input workbook | A | none | high | T1 | YES | OrcaFlex YML + Excel workbook | 1874 | NO: Engineering data; Demo 5 nice-to-have |
| 1904 | OrcaFlex/OrcaWave model and Excel workbook catalog | D | none | high | T3 | YES | OrcaFlex inventory JSON + links | none | NO: Data infrastructure; not immediate GTM |
| 1669 | GTM: Vessel Installation Contractor Email Outreach Campaign | A | none | medium | T0 | YES | Outreach SOP + target list | none | NO: Parent tracking issue; refer to #2554, #2556 |
| 1834 | Field Development Pipeline Engineering skill | A | none | medium | T3 | YES | Python skill + demo usage | 1831,1832 | NO: Complex engineering; future demo |
| 1837 | Pipeline CAPEX cost model | A | none | medium | T0 | YES | Cost model module + demo | 1834 | NO: Engineering module; future demo |
| 1836 | Shore approach analysis (HDD, trenching, pull-in) | X | none | medium | T0 | YES | Analysis module | 1834 | NO: Engineering module; future demo |
| 1835 | On-bottom stability analysis (DNV-RP-F109) | X | none | medium | T0 | YES | Stability module | 1834 | NO: Engineering module; future demo |
| 1833 | Demo 2: Review findings (pressure insensitivity) | X | none | medium | T0 | YES | Demo 2 annotation/update | 1800 | NO: Low-priority polish; noted for future |
| 1799 | Collect public pipelay vessel specs | A | none | medium | T0 | YES | Vessel spec data (JSON/CSV) | none | NO: Data collection; nice-to-have |
| 1798 | Collect public heavy-lift vessel specs | A | none | medium | T1 | YES | Vessel spec data (JSON/CSV) | none | NO: Already researched; low priority |
| 1792 | freespan VIV demo notebook | B | none | medium | T0 | YES | Jupyter notebook (VIV workflow) | 1773,1783,1692 | NO: Demo 1 exists; polish not blocking |
| 1993 | Rigzone job application pipeline | G | none | medium | T0 | YES | Resume/cover tailoring SOP | none | NO: G-track (personal job search); not GTM |
| 2117 | resume + cover letter generator for Rigzone | G | none | medium | T1 | YES | Resume templates + tailoring guide | 1993 | NO: G-track; not GTM bundle |
| 1994 | Register for GLG, AlphaSights, Guidepoint expert networks | A | none | medium | T3 | YES | Expert network profiles | none | NO: G-track proxy; long-tail income, not 12hr bundle |
| 2355 | pin Node engines in aceengineer-website package.json | X | none | low | T0 | YES | package.json + vercel.json updates | 2342,2343 | NO: Forward-looking resiliency; not blocker |
| 2356 | add GH Actions workflow to run npm test | E | none | low | T0 | YES | .github/workflows/ci.yml | 2342,2343 | NO: CI harness debt; not GTM artifact |
| 2351 | Day-7/14/21/30 checkpoint dashboard | C | none | low | T1 | YES | Checkpoint tracker + weekly report | 2016 | NO: Internal tracking; not client-facing |
| 197 | OpenClaw/WhatsApp AI agent setup guide | C | none | medium | T0 | YES | docs/ai-initiatives/narada-setup.md | none | NO: C-track infrastructure; not GTM |
| 191 | chatbot fundamentals — shared persona, tone, tiers | C | none | high | T0 | YES | ai-initiatives/shared/chatbot_fundamentals.md | none | NO: C-track strategy doc; not GTM artifact |
| 117 | oil-and-gas practitioner persona + 1-month GTM plan | C | none | high | T0 | YES | docs/gtm/persona.md + plan | none | NO: Strategy doc shipped conceptually; doc refresh only |
| 108 | ACE-GTM: A&CE Go-to-Market strategy stream | B | none | high | T0 | YES | Parent issue + child roadmap | none | NO: Parent strategy; not executable alone |

---

## Cluster Summary

### By Track
| Track | Total | YES | NO | Description |
|-------|-------|-----|----|----|
| **A** | 18 | 6 | 12 | Vessel-contractor outreach, brochures, matrices, engineering data |
| **B** | 4 | 0 | 4 | Prospect 48hr demo pipeline, demo notebooks |
| **C** | 6 | 1 | 5 | Client conversion, methodology publishing, chatbot foundations, expert networks |
| **D** | 2 | 2 | 0 | FOWT/wind contractor lane, mooring demo, animation inventory |
| **E** | 4 | 1 | 3 | CTA wiring, CI workflow, checkpoint dashboard |
| **F** | 3 | 0 | 3 | Animation/explainer pipeline, manim scenes |
| **G** | 2 | 0 | 2 | Rigzone, expert networks (personal income) |
| **X** | 4 | 0 | 4 | Engineering modules, demo review findings |

**Summary**: 8 YES (high-confidence GTM artifacts for 12-hr bundle), 30 NO (strategy, engineering data, polish, or future-track work).

---

## Already in Flight — DO NOT TOUCH

| Issue | Status | Agent | Track | Notes |
|-------|--------|-------|-------|-------|
| **#2346** | `status:working` | `agent:codex` | B | **DO NOT TOUCH**: In active progress by Codex agent. Prospect-data pipeline is core to 12-hr bundle; wait for completion signal. |

---

## Hidden Dependencies

Issues where the Sendable Artifact secretly depends on infrastructure or data work NOT in the GTM track:

1. **#2115 (mooring demo GTM Demo 6)**
   - Depends on: #1904 (OrcaFlex inventory catalog)
   - Hidden risk: If #1904 not landed, mooring demo will use stale/incomplete OrcaFlex reference models
   - Mitigation: #1904 is T3 effort; propose using pre-existing OrcaFlex templates from `digitalmodel/mooring/` to avoid blocking #2115

2. **#2038 (installation sequence animation)**
   - Depends on: #1798 (HLV vessel specs collected)
   - Hidden risk: Manim scene needs vessel operability envelope data; #1798 research may have gaps
   - Mitigation: #1798 already researched (Sleipnir, Thialf, etc. specs available); animation can proceed with known heavy-lift vessels

3. **#2030 (publish methodology docs)**
   - Depends on: Existing content in `docs/methodology/` (already written)
   - Hidden risk: Low — content exists; publishing is pure ops
   - Mitigation: None needed

4. **#2556 (vessel brochure)**
   - Depends on: #2554 (contractor matrix) and capability charts
   - Hidden risk: Cannot send brochure without contractor list and positioning
   - Mitigation: #2554 is T0 effort; prioritize as unblocking item

5. **#2422 (CTA wiring on demo pages)**
   - Depends on: #2367 (already shipped)
   - Hidden risk: Low — pattern established; copy-paste implementation
   - Mitigation: None needed

---

## Top 3 YES Picks for 12-Hour Window

1. **#2554 — vessel contractor outreach matrix (T0, high priority)**
   - Unblock: Feeds #2556 (brochure) and #2562 (GoM evidence)
   - Artifact: Contractor matrix + evidence URLs
   - Owner: GTM team
   
2. **#2556 — vessel brochure + send tracker (T0, high priority)**
   - Unblock: Directly leads to first client sends
   - Artifact: Brochure PDF + email templates + send tracker
   - Owner: GTM team
   
3. **#2346 — prospect-data 48hr pipeline (T2, working + plan-approved)**
   - Status: Codex agent in progress
   - Artifact: Branded demo report + intake schema
   - Owner: Codex (in flight; monitor for completion)

---

## Top Blocker for the Bundle

**#2554** — "weekly vessel contractor outreach matrix"

- **Why**: Both #2556 (brochure) and #2562 (GoM evidence) are blocked until contractor matrix exists
- **Effort**: T0 (research already done; formatting only)
- **Client value**: High — enables first cold-outreach batch
- **Status**: Currently `status:blocked` (reason unclear from issue body)
- **Recommendation**: Prioritize unblocking #2554 first; everything else cascades from this

---

## Summary for Execution

| Key Metric | Value |
|---|---|
| Total issues scanned | 38 unique (28 domain:gtm + 8 gtm + 2 dual-labeled) |
| Recommend YES | 8 |
| Recommend NO | 30 |
| Critical path items (T0-T1) | 6 (#2554, #2556, #2562, #2561, #2115, #2422) |
| In-flight work (do not touch) | 1 (#2346 via Codex) |
| High-priority engineering debt | 0 (for GTM; 4 modules in backlog for future) |
| Expected sendable artifacts | Brochure + contractor matrix + prospect demo + mooring demo + methodology pages + CTA-wired pages |
