---
title: GTM Sendable Bundle — 2026-05-01
date: 2026-05-01
audience: external (mailto-ready)
status: ready-to-send
---

# Client-Sendable Bundle — 2026-05-01

This bundle ties together the artifacts shipped in the 2026-05-01 GTM session into a sequence you can send directly to a prospect, without further authoring.

**The shareable URL** for any audience: <https://www.aceengineer.com/outreach/>

That single page links the two audience-specific briefs, the 6 demos, and the capability-summary PDF download. You can also send any of the deeper links below.

---

## Live URLs

### Audience briefs
- Vessel installation contractors → <https://www.aceengineer.com/outreach/vessel-contractor-brochure.html>
- FOWT mooring screening → <https://www.aceengineer.com/outreach/fowt-mooring-screening.html>

### Six engineering demos (5 overnight parametric runs + 1 template)
- DNV freespan / VIV (Demo 1) → <https://www.aceengineer.com/demos/freespan.html>
- Pipeline wall thickness multi-code (Demo 2) → <https://www.aceengineer.com/demos/wall-thickness.html>
- Deepwater mudmat installation (Demo 3) → <https://www.aceengineer.com/demos/mudmat.html>
- Shallow water pipelay (Demo 4) → <https://www.aceengineer.com/demos/pipelay.html>
- Subsea jumper lift — Ballymore worked example (Demo 5) → <https://www.aceengineer.com/demos/jumper-installation.html>
- Mooring & station-keeping screening template (Demo 6, illustrative until project run) → <https://www.aceengineer.com/demos/mooring.html>

### One-page summary (PDF, attachable)
- <https://www.aceengineer.com/assets/capability-summary-v1.pdf>

### Demo gallery (existing)
- <https://www.aceengineer.com/demos/>

---

## Email-ready text — by audience

Replace the `[name]` and `[company]` tokens; otherwise these are paste-and-send.

### Audience A — heavy-lift / pipelay / PLSV vessel contractor

**Subject:** Parametric installation engineering, overnight — for [company]'s installation team

Hello [name],

I run AceEngineer, an engineering-led parametric analysis shop for offshore installation work. I think the way [company] frames installation envelopes (vessel × sea state × structure geometry) is exactly what our overnight runs were built for.

A 1-screen overview, written for installation contractors, is here: <https://www.aceengineer.com/outreach/vessel-contractor-brochure.html>

If you want to see the kind of deliverable we'd hand back after a 48-hour run on your data, the relevant demos are:
- Subsea jumper lift (Ballymore manifold-to-PLET, 27 OrcaFlex sections, 81 tests): <https://www.aceengineer.com/demos/jumper-installation.html>
- Deepwater mudmat installation (180 parametric cases, DNV H103 coupled): <https://www.aceengineer.com/demos/mudmat.html>
- Shallow water pipelay (sag-bend tension sensitivity, sea-state envelope): <https://www.aceengineer.com/demos/pipelay.html>

Capability summary PDF (1 page, attachable): <https://www.aceengineer.com/assets/capability-summary-v1.pdf>

Happy to do a 30-minute call or run a parametric pass on a vessel + structure pair you pick.

— Vamsee Achanta
AceEngineer

### Audience B — wind-developer / FOWT-installation contractor

**Subject:** Pre-FEED mooring screening on OC4 — for [company]'s floating wind work

Hello [name],

I run AceEngineer; we built an OC4-DeepCwind worked example to show the shape of an ACE screening-tier FOWT mooring deliverable — concept ranking, quasi-static stiffness, frequency-domain response trends, installation and operability flags. Page values are illustrative public-reference; we run on your project inputs in 48 hours. We position screening-tier explicitly and hand off to OpenFAST / WEIS partners for full IEC coupled work — that boundary keeps the engagement honest.

The OC4-DeepCwind worked example: <https://www.aceengineer.com/outreach/fowt-mooring-screening.html>

The mooring-screening demo template (catenary / taut / hybrid concept comparison): <https://www.aceengineer.com/demos/mooring.html>

For technical-buyer context, the closest installation demos:
- Mudmat installation (180 parametric cases): <https://www.aceengineer.com/demos/mudmat.html>
- Subsea jumper lift (Ballymore worked example): <https://www.aceengineer.com/demos/jumper-installation.html>

Capability summary PDF: <https://www.aceengineer.com/assets/capability-summary-v1.pdf>

Worth a 30-minute call?

— Vamsee Achanta
AceEngineer

### Audience C — generic offshore operator / EPC

**Subject:** Six engineering demos — sendable directly

Hello [name],

We ship parametric installation engineering on overnight turnarounds. Easiest entry point is the outreach hub: <https://www.aceengineer.com/outreach/>

It links six demos (freespan/VIV screening, multi-code wall thickness, mudmat installation, shallow-water pipelay, subsea jumper lift, and a mooring-screening template), two audience briefs, and a 1-page capability summary.

Pick whichever demo is closest to your current question and we'll re-run it parametrically on your data inside 48 hours.

— Vamsee Achanta
AceEngineer

---

## Send sequencing

Recommended cadence per prospect:

| Day | Channel | Content | Why |
|---|---|---|---|
| 0 | Email | Brief link + 1 demo URL + PDF attachment | Show, don't tell — visual proof in 30 seconds of skim |
| 0 | LinkedIn | Connection request, no pitch | Soft surface; the email does the work |
| +3 | Email | Re-share with second demo URL relevant to their portfolio | Proof of breadth without re-pitching |
| +7 | Email | Offer to run a 48-hour parametric pass on a structure they pick | Concrete ask, low commitment |
| +14 | Pause | Move to nurture cadence | Quality outreach > volume |

---

## Visual proof of the live deliverable

A recorded 9-page tour of every shipped page is in `proof/`:
- [`proof/2026-05-01-gtm-bundle-tour.mp4`](proof/2026-05-01-gtm-bundle-tour.mp4) — 1280×720, 27 s, 906 KB (best for in-browser embedding)
- [`proof/2026-05-01-gtm-bundle-tour.gif`](proof/2026-05-01-gtm-bundle-tour.gif) — 900×506, 270 frames, 828 KB (best for email paste; survives Outlook)
- [`proof/record-tour.sh`](proof/record-tour.sh) — reproducible: re-run anytime with `bash record-tour.sh`

Each page is held for 3 seconds — readable at a glance without dragging the proof past 30 seconds total.

## Provenance

| Asset | Issue closed | Commit |
|---|---|---|
| Outreach hub `/outreach/` index | (this bundle) | aceengineer-website [`e069d11`](https://github.com/vamseeachanta/aceengineer-website/commit/e069d11) |
| 5 demo pages — embedded GIF + CTA | [#2422](https://github.com/vamseeachanta/workspace-hub/issues/2422) | aceengineer-website [`20f5e59`](https://github.com/vamseeachanta/aceengineer-website/commit/20f5e59) |
| Vessel-contractor brochure | [#2556](https://github.com/vamseeachanta/workspace-hub/issues/2556) | aceengineer-website [`a79b462`](https://github.com/vamseeachanta/aceengineer-website/commit/a79b462) |
| FOWT mooring screening worked example | [#2561](https://github.com/vamseeachanta/workspace-hub/issues/2561) | aceengineer-website [`f3b0914`](https://github.com/vamseeachanta/aceengineer-website/commit/f3b0914) |
| Vessel-contractor matrix (internal target list) | [#2554](https://github.com/vamseeachanta/workspace-hub/issues/2554) + [#2562](https://github.com/vamseeachanta/workspace-hub/issues/2562) | workspace-hub [`434afb7c1`](https://github.com/vamseeachanta/workspace-hub/commit/434afb7c1) |
| 2 methodology pages (compliance-dashboard, cross-review) + 6th demo (mooring template) + sitemap expansion | [#2030](https://github.com/vamseeachanta/workspace-hub/issues/2030) + [#2115](https://github.com/vamseeachanta/workspace-hub/issues/2115) | aceengineer-website [`f5186ca`](https://github.com/vamseeachanta/aceengineer-website/commit/f5186ca) |
| Adversarial-review P0 remediation (dead /contact link, Demo 6 hub card, sitemap drift, brochure case-count inflation, FOWT disclaimer-first) | (this commit) | aceengineer-website [`5f45587`](https://github.com/vamseeachanta/aceengineer-website/commit/5f45587) |
| MINOR/NIT batch (3-email standardize, mobile `.table-responsive`, "two decades" + LinkedIn, og:`&amp;`, justify-typo, 20-sections-elided, word-counts → read-time) | (this commit) | aceengineer-website [`b60722c`](https://github.com/vamseeachanta/aceengineer-website/commit/b60722c) |
| Demo 6 card image — replaced 5-demo composite GIF with mooring-specific PNG screenshot | (this commit) | aceengineer-website [`06f2f51`](https://github.com/vamseeachanta/aceengineer-website/commit/06f2f51) |
| Test docstrings updated for 6 demos | (this commit) | aceengineer-website [`3e89cc4`](https://github.com/vamseeachanta/aceengineer-website/commit/3e89cc4) |
| Round-2 review M1 + M2 (live `/demos/` gallery '1,292 cases' inflation; PDF SHA256 sidecar regenerated) | (this commit) | aceengineer-website [`2e97fca`](https://github.com/vamseeachanta/aceengineer-website/commit/2e97fca) |
| Matrix URL repair (12 cleanly + 7 WAFs documented + 2 narrative-edit follow-ups) | [#2578](https://github.com/vamseeachanta/workspace-hub/issues/2578) | workspace-hub [`83e8b46b1`](https://github.com/vamseeachanta/workspace-hub/commit/83e8b46b1) |
| Send-tracker + sanity-review-log artifacts (#2556 unmet acceptance) | [#2577](https://github.com/vamseeachanta/workspace-hub/issues/2577) | workspace-hub [`b5f85814e`](https://github.com/vamseeachanta/workspace-hub/commit/b5f85814e) |
| Matrix §3b narrative edits (Bourbon retitle + Sub-Sea Candies replacement) | (this commit) | workspace-hub [`a29148192`](https://github.com/vamseeachanta/workspace-hub/commit/a29148192) |
| Otto Candies P2 → P1 promotion (post-Harvey-Gulf 4-MPSV acquisition + 2026 Kelly Ann divestiture trigger; §1 priority sequence gains item 9) | (this commit) | workspace-hub [`c435869b3`](https://github.com/vamseeachanta/workspace-hub/commit/c435869b3) |

> **Caveat — known unmet acceptance criteria** (Adv-C F2 finding): #2556's acceptance criteria 3 (send-tracker artifact) and 4 (legal/evidence sanity review) were not addressed in the original closing commit. Tracked in follow-up [#2577](https://github.com/vamseeachanta/workspace-hub/issues/2577). The brochure itself ships as designed; the missing items are operational, not deliverable defects.
>
> **Caveat — matrix evidence URLs** (Adv-C F1 finding): of 26 contractor rows, 14 carried URLs returning HTTP 404/000 at review time. Tracked in follow-up [#2578](https://github.com/vamseeachanta/workspace-hub/issues/2578); URL repairs land in `vessel-contractor-matrix-url-repairs-2026-05-01.md` once the repair agent completes. Until that merges into the main matrix, treat individual evidence URLs as candidates rather than verified — **pre-send verification of any row you actually use is mandatory**.

Triage source: [`docs/gtm/triage-2026-05-01.md`](../../triage-2026-05-01.md)
