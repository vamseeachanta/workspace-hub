---
agent: adversarial-review-C-silent-failures
date: 2026-05-01
stance: silent-failure hunt (assume claims overshoot reality)
verdict: MAJOR
---

# Adversarial review C — silent-failure hunt of 2026-05-01 GTM bundle

## 1. Verdict & top concern

**Verdict: MAJOR.**

**Sharpest finding:** the vessel-contractor matrix's "Public Evidence (URL)" column is the load-bearing trust artifact for the entire matrix — it's what makes the matrix defensible as "company-level prioritized target list with public-source evidence" per the #2554 acceptance criteria. **14 of the 26 evidence URLs do not resolve (404) or are blocked (403/000)**. Only ~7 of 26 return a clean HTTP 200 with the claimed vessel content findable via grep. The matrix's own §3 "Evidence Quality Notes" flags 6 rows as needing pre-send verification — **but the live URL-resolution failure rate is 14/26, more than double what §3 self-discloses.** The closing comment on #2554 ticks the acceptance-criteria box "[x] Each target has public evidence" with a categorical claim, and the bundle README forwards the matrix as the "internal target list" without flagging this. A prospect ops review against any of the 14 broken URLs would surface immediately.

**Tier-2 concerns:**
- **#2556 acceptance criteria silently dropped two of four items** — "Send tracker exists" and "Legal/evidence sanity review is complete before public/client-facing distribution" are not addressed in the closing comment. No tracker artifact exists in the repo.
- **Triage ledger row 11 ("claude-in-chrome quality-proof capture ⚠️ partial") contradicts the bundle README** — ledger says "8-frame tour GIF generated (1.1 MB) but landed outside this sandbox"; bundle README says "9-page tour, 270 frames, 828 KB GIF" with files committed in `proof/`. Both can't be true; the bundle README matches reality.
- **`record-tour.sh` swallows Chrome errors via `2>/dev/null`** — pipeline does not validate that all 9 PNGs were captured before encoding. A 502/DNS failure produces a missing or 0-byte frame that ffmpeg silently skips, the script still exits 0, and the operator sees no signal.

---

## 2. Silent-failure findings

### F1 — vessel-contractor matrix evidence URLs: 14/26 broken
**File:** `docs/gtm/outreach/vessel-contractor-matrix-2026-05-01.md` rows 1–26
**Severity: HIGH**

Live `curl -sIL` results (2026-05-01):

| # | Company | URL status |
|---|---|---|
| 1 | Subsea7 | **404** subsea7.com/en/our-fleet.html |
| 2 | TechnipFMC | 403 (likely WAF, may resolve in browser) |
| 3 | Saipem | 403 (WAF) |
| 4 | McDermott | **404** mcdermott.com/What-We-Do/Subsea-and-Floating-Facilities |
| 5 | Allseas | **404** allseas.com/equipment/ |
| 6 | Heerema | 200 (verified Sleipnir + Thialf in page meta) |
| 7 | DOF Group | **404** dof.com/en/our-fleet |
| 8 | Solstad | 200 (but `Normand Maximus`/`Normand Vision` not findable on returned HTML) |
| 9 | Boskalis | 200 (Bokalift confirmed) |
| 10 | DEME | **404** deme-group.com/fleet |
| 11 | Seaway7 | 200 |
| 12 | Helix | **404** helixesg.com/our-fleet/ |
| 13 | DeepOcean | **404** deepoceangroup.com/fleet/ |
| 14 | Bourbon/Gulf Offshore | **000** (DNS or TLS failure on bourbon-online.com) |
| 15 | Hornbeck | **000** (TLS/DNS failure) |
| 16 | Edison Chouest | **404** chouest.com/our-business/edison-chouest-offshore/ |
| 17 | Otto Candies | 200 (Ross Candies confirmed; Kelly Ann Candies not findable in the returned page) |
| 18 | Tidewater | **404** tdw.com/our-fleet/ |
| 19 | Cadeler | 455 (unusual code; not 200) |
| 20 | Jan De Nul | 200 |
| 21 | Van Oord | **404** vanoord.com/en/equipment/ |
| 22 | Cheniere | **404** cheniere.com/operations |
| 23 | Venture Global | **404** ventureglobal.com/our-projects/ |
| 24 | Woodside | 403 (WAF) |
| 25 | Equinor | 200 |
| 26 | Aker Solutions | 200 |

**Tally:** 8 clean 200s, 4 WAF-protected (defensible — likely render in a browser), 14 hard 404/000 failures.

The matrix §5 row "[x] Each target has public evidence" is the load-bearing claim that Closes #2554. **More than half of the URLs cited as evidence do not point at a live page.** Worse, §3 "Evidence Quality Notes" flags only 6 specific rows for pre-send verification — leaving 8 additional broken URLs entirely unflagged. The matrix's tone says "Public Evidence (URL)" as a definitive column header, not "candidate URL pending verification" — the disclaimer in §3 is operationally invisible against the row-by-row table appearance.

**Reality:** these URL paths look like they were composed by guess-pattern (`/en/our-fleet`, `/our-fleet/`, `/fleet/`) without per-URL fetching. The matrix needs row-by-row URL replacement before it can be sent or used as a contact-research surface.

---

### F2 — #2556 closing comment drops 2 of 4 acceptance criteria
**File:** triage-2026-05-01.md row "#2556 brochure ✅ shipped" + bundle README provenance row
**Severity: HIGH**

#2556 issue body acceptance criteria:
1. [x] Brochure has an evidence-bounded value proposition and vessel capability visuals → **shipped (brochure live, demo_comparison_matrix.gif embedded)**
2. [x] Outreach copy is personalized by contractor tier/segment → **arguably shipped (3-audience email templates in bundle README)**
3. **[ ] Send tracker exists and distinguishes public artifact paths from private contact details** — **NOT addressed in closing comment; no tracker artifact found via `find docs/gtm -name '*tracker*' -o -name '*send-log*' -o -name '*outbound*'`**
4. **[ ] Legal/evidence sanity review is complete before public/client-facing distribution** — **NOT addressed in closing comment**

The triage ledger Wave 2 row "#2556 brochure ✅ shipped" with sendable artifact "vessel-contractor-brochure.html (213 lines, 418 words) + tracker stub" mentions a "tracker stub" but no tracker file exists. Agent A's triage explicitly defined the #2556 sendable artifact as "Brochure + send tracker + email templates" — two of three are missing or weak (tracker entirely missing; email templates re-located to bundle README rather than committed as a templates artifact under #2556's scope).

**This is an issue-closure overclaim.** The closing comment lists the brochure URL and build/test green and says "Closing." — without disclosing that 2 of 4 acceptance criteria are unmet.

---

### F3 — Triage ledger row 11 contradicts bundle README on proof artifact
**File:** docs/gtm/triage-2026-05-01.md:88 vs docs/gtm/sendable-bundles/2026-05-01/README.md:117–124
**Severity: MEDIUM**

Triage ledger says: `⚠️ partial — 8-frame tour GIF generated (1.1 MB) but Chrome download landed outside this sandbox per feedback_lane_result_path_outside_sandbox.md; the live URLs themselves are the proof`

Bundle README says: `proof/2026-05-01-gtm-bundle-tour.gif — 900×506, 270 frames, 828 KB` and the file is in fact present at that path with size 827773 bytes. There are 9 PNG frames in `proof/frames/` not 8.

The ledger's narrative ("landed outside the sandbox; live URLs are the proof") was true earlier in the session for the claude-in-chrome capture path but is now contradicted by the ffmpeg-encoded tour that was successfully built in-bundle. The ledger row was never updated to reflect that the second proof attempt succeeded.

A reader of the ledger will believe no in-bundle proof exists. A reader of the bundle README will believe one does. Both claims are made by the same session, and the bundle README matches reality.

---

### F4 — `record-tour.sh` silently passes through Chrome failures
**File:** docs/gtm/sendable-bundles/2026-05-01/proof/record-tour.sh:35–48
**Severity: MEDIUM**

```bash
google-chrome \
  --headless=new ... \
  --virtual-time-budget=8000 \
  --screenshot="${out}" \
  "${url}" 2>/dev/null
```

`set -euo pipefail` is set at line 7, which is necessary but not sufficient for this pipeline:

1. **`2>/dev/null`** silences chrome stderr — net errors, DNS failures, blocked-by-CSP, render-deadline exhaustion are all invisible. With `pipefail`, the chrome exit code IS checked, but Chromium has documented patterns where `--virtual-time-budget` exhaustion writes a partial or empty PNG and exits 0.
2. **No size validation** on the resulting PNG. An empty (0-byte) or partial PNG silently flows into the concat list at line 56.
3. **No assertion** that `$(ls "${FRAMES_DIR}"/*.png | wc -l)` equals 9 (the URL count). If chrome failed on URL 4, the script still encodes a 8-frame tour and exits 0 without warning.
4. **Line 60 `last=$(ls ... | tail -1)`** — if the directory is empty, `last` is the empty string, and the printf at line 61 generates a line `file ''` that ffmpeg will reject with a vague error. Operator sees ffmpeg complaint, not the real cause (no Chrome captures).
5. **ffmpeg invocations** also `-loglevel error` — encoding errors that don't fail hard are suppressed.

A network drop mid-run produces a tour that's missing pages. Reproducibility is broken without anyone being told.

**Recommendation:** after the loop, assert `[[ $(ls "${FRAMES_DIR}"/*.png | wc -l) -eq ${#URLS[@]} ]] || { echo "ERROR: expected ${#URLS[@]} frames"; exit 1; }`. Add `[[ -s "${out}" ]] || { echo "ERROR: empty PNG for $url"; exit 1; }` inside the loop. Drop the `2>/dev/null` on chrome (or write stderr to a log file in the workdir).

---

### F5 — FOWT screening page: stiffness numbers stated with disclaimer-as-fig-leaf
**File:** content/outreach/fowt-mooring-screening.html lines 149 (live)
**Severity: MEDIUM**

The page states:
> "Indicative magnitudes for the OC4 catenary are k_xx ≈ k_yy ≈ 70–90 kN/m and k_yaw on the order of 1.0×10^8 N·m/rad — *screening-only, replace with project values*."

The disclaimer is technically present, but the structure ("are 70–90 kN/m" — declarative copula, not "would be" or "for illustrative purposes are reported as") frames the numbers as if they characterise the OC4 catenary. The em-tagged "screening-only" lives at the **end** of the sentence after the numbers have already been read.

A wind-developer engineer who scans this page (the email template explicitly invites prospects who "want to see the kind of deliverable we'd hand back") will pattern-match on the numbers and may take them as ACE's calibration of the OC4 platform. They are not — they are illustrative ranges intended only to demonstrate the screening **shape**.

**This is the disclaimer-neutralised-by-prose pattern.** The fix is either (a) replace the values with explicit ellipses ("k_xx in the order of [project value], typical OC4-class screening band"), or (b) move the screening-only flag to the front of the sentence ("Illustrative-only k_xx for the OC4 catenary fall in the 70–90 kN/m band when seeded with public-reference values").

---

### F6 — Audience B email implies done capability, page is a worked-example template
**File:** docs/gtm/sendable-bundles/2026-05-01/README.md:71 (audience B email body)
**Severity: MEDIUM**

Email text: *"I run AceEngineer; we do pre-FEED and early-FEED mooring screening for floating offshore wind."*

Live page (fowt-mooring-screening.html): *"This worked example shows the **shape** of an ACE FOWT mooring screening deliverable... [k_xx] screening-only, replace with project values."*

The email framing **"we do"** asserts a current production capability. The page is a worked example with public OC4-DeepCwind values, no client case-study, no past-engagement evidence, no named partner ("handed off to OpenFAST / WEIS partners" — no partner is named on any ACE page).

A wind-developer prospect who clicks through and asks "great — what client did you screen this for?" gets a credibility hit. The email's done-tense framing exceeds what the linked page actually shows. Defensible escape hatch: ACE leadership (Vamsee Achanta) has done equivalent O&G mooring screening work, and the page's "Engagement model" section honestly says "A real engagement starts with a 1-hour intake" — which implies the demonstrated artifact is not a past engagement. But the email's "we do" framing leans toward "we have done this for clients," which the page does not support.

---

### F7 — Brochure asserts "23 years of subsea/installation engineering" without source
**File:** content/outreach/vessel-contractor-brochure.html (live)
**Severity: NIT**

Brochure says: *"We codified 23 years of subsea/installation engineering into parametric tools..."*

Vamsee Achanta's career chronology is not on the page, in the brochure copy, or in the bundle. A prospect doing diligence on a 1-person shop's "23 years" claim has no public attestation surface. The number is plausible but unanchored. Either link to a LinkedIn / about page, or soften to "two decades of subsea/installation engineering."

---

### F8 — Matrix §5 acceptance "[x] Follow-up issues are created" is technically false
**File:** docs/gtm/outreach/vessel-contractor-matrix-2026-05-01.md:197–200
**Severity: MEDIUM**

Matrix §5 row 4: `[x] Follow-up issues are created for high-value missing data rather than burying blockers → §2 Niche Coverage Gaps + §3 Evidence Quality Notes capture the follow-up shape; existing #1835/#1836/#1837 already cover the on-bottom stability / shore-approach / pipeline-CAPEX module gaps.`

The acceptance criterion says "Follow-up **issues** are created" — i.e., new GitHub issues. The matrix self-justification claims that:
- §2 (Niche Coverage Gaps) and §3 (Evidence Quality Notes) "capture the follow-up shape" — these are in-document tables, not GitHub issues
- #1835 / #1836 / #1837 are pre-existing issues for engineering modules, not for the 6 evidence-quality rows the matrix itself identified

**No new GitHub issue was filed for the 6 evidence-upgrade rows in §3, nor for any of the §2 niche-gaps that don't already have an open issue.** The closing comment on #2554 propagates the same `[x]` checkmark.

This is the #2030/#2115 closing-comment-glosses-criterion pattern. The work product is acceptable; the acceptance check is wrong.

---

### F9 — Solstad evidence URL resolves but doesn't contain the cited vessels
**File:** docs/gtm/outreach/vessel-contractor-matrix-2026-05-01.md:39 (row 8)
**Severity: NIT**

Matrix says: *"Normand Maximus (DP3 pipelay/construction), Normand Vision — light construction and IMR fleet"* with evidence URL `https://www.solstad.com/our-fleet/`.

`curl -sL https://www.solstad.com/our-fleet/ | grep -i "normand maximus\|normand vision"` returns zero matches. The page may render those names via JS (the site is heavy SPA), but the matrix's "smell test" claim that the evidence URL supports the named vessels is not directly verifiable from raw HTML. Pre-send verification per §3's general principle is needed for this row even though §3 didn't flag it.

Otto Candies row similar: page confirms Ross Candies but Kelly Ann Candies is not findable on raw HTML — a prospect who follows the link looking for Kelly Ann gets a soft credibility ding.

---

## 3. Cross-claim contradictions

| Doc A | Claim | Doc B | Counter-claim | Reality |
|---|---|---|---|---|
| triage-2026-05-01.md:88 | "8-frame tour GIF generated (1.1 MB) but landed outside this sandbox" | sendable-bundles/2026-05-01/README.md:120–121 | "9-page tour, 270 frames, 828 KB GIF" in `proof/` | Bundle README correct; ledger row stale |
| triage-2026-05-01.md:81 | "#2556 shipped — content/outreach/vessel-contractor-brochure.html (213 lines, 418 words)" + "tracker stub" | sendable-bundles/2026-05-01/README.md:132 (provenance) | "Vessel-contractor brochure" only — no tracker | Tracker doesn't exist; ledger overclaims |
| Audience B email README.md:71 | "we do pre-FEED and early-FEED mooring screening for floating offshore wind" | fowt-mooring-screening.html | "shape of an ACE FOWT mooring screening deliverable" with all illustrative values | Email overstates relative to page |
| matrix legend line 23–24 | "D5=deepwater rigid-jumper installation (300)" | jumper-installation.html (live) | Page shows "81/81 tests" + "27 OrcaFlex sections", no "300" anywhere | The "300 cases" number is from the GIF storyboard / brochure GIF, not the demo page; defensible only via the GIF visual |

---

## 4. Live-evidence misses

### Live URL resolution against the bundle (clean)
All 12 URLs in the bundle README's "Live URLs" section return HTTP 200:
- outreach hub, vessel-brochure, FOWT screening, 5 demos, mooring demo, capability PDF, demos gallery, both methodology pages.

### Live URL resolution against the matrix (broken)
14/26 URLs hard-fail (404 or 000); 4 are 403/455 (WAF). Detail in F1 above.

### Page-content support for email-template claims
| Email claim | Page reality | Verdict |
|---|---|---|
| "Subsea jumper lift (Ballymore manifold-to-PLET, 27 OrcaFlex sections, 81 tests)" | jumper-installation.html: meta-alt confirms Ballymore, KPI shows "27 OrcaFlex sections" + "81/81 tests" | **PASS** |
| "Deepwater mudmat installation (180 parametric cases, DNV H103 coupled)" | mudmat.html: subtitle "180 parametric cases", body "DNV-RP-H103 (2011)" | **PASS** |
| "Shallow water pipelay (sag-bend tension sensitivity, sea-state envelope)" | pipelay.html: 1886 body words, includes pipelay sag-bend tables | **PASS** |
| "we do pre-FEED and early-FEED mooring screening for FOWT" | fowt-mooring-screening.html: explicit "worked example" + "shape" framing, no past-client evidence | **OVERCLAIM** (F6) |

---

## 5. Issue-closure honesty audit

| Issue | Verdict | Evidence |
|---|---|---|
| **#2422** | **PASS** | Closing comment matches commit `20f5e59`: 5 demo pages each have GIF + CTA. Live `curl` of all 5 pages confirms `<img src="../assets/img/demos/demo_0X_*.gif">` and PDF CTA anchor. Build claim "46 pages built clean, 144/144 tests pass" matches the commit message. Honest closure. |
| **#2554** | **OVERCLAIMED (soft)** | Acceptance criterion 4 ("Follow-up issues are created") is checked `[x]` but no GitHub issues were opened for the 6 evidence-quality rows §3 identifies. (See F8.) Acceptance criterion 2 ("public evidence... reason for outreach fit") is checked `[x]` but 14/26 URLs are hard-broken. (See F1.) The work shipped is real (26 ranked rows with structured columns) but two acceptance boxes are ticked harder than the artifact supports. |
| **#2556** | **OVERCLAIMED** | Closing comment ships the brochure landing page and stops. Acceptance criterion 3 (send tracker) is unmet — no tracker artifact in repo. Acceptance criterion 4 (legal/evidence sanity review) is not addressed in the closing comment. (See F2.) |
| **#2561** | **PASS** (with F5 caveat) | Closing comment honestly says "All numeric values flagged as illustrative public-reference." Live page does carry the illustrative caveat per row in the parameter table. The disclaimer is grammatically end-tailed in the prose paragraph (F5) but technically present. |
| **#2562** | **PASS** | Closing comment routes GoM expansion to matrix §4 (4 GoM rows). Matrix §4 source-reconciliation table indeed identifies 4 from #2562. Hornbeck/Chouest/Otto Candies/Tidewater all carry GoM regional flag. Acceptance criteria are direct match. (Hornbeck and Chouest URLs are broken per F1 — that's a matrix problem, not a closing-comment overclaim.) |
| **#2030** | **PASS** | Closing comment: 4 prior pages via `3d21b8e` + 2 new via `f5186ca` = 6 of 6 (excluding internal-only knowledge-to-website-pipeline as designed). Live URLs verified for all 6. New pages (compliance-dashboard, cross-review) have meta description + Google Analytics G-K31E51DQ47 + Contact CTA + capability-summary CTA. All 4 acceptance bullets from issue body are objectively supported. Honest closure. |
| **#2115** | **PASS (transparent under-deliver)** | Closing comment directly says: "Scope decision: content-only this window. No new GIF was generated (would require a fresh OrcaFlex parametric run, ~3-4 hr). The same illustrative-public-values pattern shipped successfully on the FOWT page." Live page uses `demo_comparison_matrix.gif` placeholder (not a mooring-specific GIF) and badge reads "Demo template — awaiting project values." This is the correct pattern: under-deliver explicitly rather than wallpaper. The triage ledger's row "#2115 mooring demo — content-only (illustrative values, screening-tier boundary, real parametric run per-prospect via 48hr SOP)" matches the closing comment. **Honest closure**. |

**Summary:** 5 of 7 closures pass; 2 overclaim (#2554 soft, #2556 explicit).

---

## 6. What I checked and found clean

- **File commit references** in triage ledger and bundle README all resolve. `git show 434afb7c1`, `20f5e59`, `a79b462`, `f3b0914`, `e069d11`, `f5186ca` all exist with matching content.
- **Bundle README live URLs** — all 12 referenced URLs return HTTP 200.
- **Sitemap entries** — all 6 new URLs (mooring demo, outreach hub, brochure, FOWT page, 2 methodology pages) are in the live sitemap.xml.
- **Methodology pages** — both new pages (compliance-dashboard, cross-review) have meta description, Google Analytics G-K31E51DQ47, contact CTA, and capability-summary PDF download anchor. #2030 acceptance criteria objectively met.
- **Mooring demo page (#2115)** — every numeric value is wrapped in "illustrative" language; case-badge says "Demo template — awaiting project values"; "Where this stops" boundary section is comprehensive. Closing comment honestly discloses the content-only scope.
- **Demo case counts referenced in emails** — 81 tests, 180 cases, 60 cases all match the live demo pages.
- **Provenance commit verification** — every SHA in the bundle README provenance table actually exists on its repo's main and contains the changes claimed.
- **`set -euo pipefail`** is set in `record-tour.sh`. (Necessary but not sufficient — see F4.)

---

## 7. Recommended fixes (prioritised)

1. **Block-level: do not send the matrix-as-prospect-evidence to anyone until the 14 broken URLs are repaired** — open an issue against `vessel-contractor-matrix-2026-05-01.md` with row-by-row URL-pass requirement before send. Half-broken evidence is worse than no evidence.
2. **Reopen #2556** or open a follow-up "send-tracker artifact + legal/evidence sanity review" issue. The acceptance check is unmet.
3. **Reopen the matrix §5 follow-up checkbox** — convert §3 evidence-upgrade row 5 to actual GitHub issues, or reword the acceptance bullet to "follow-up shape captured in §2/§3 of this document" so the document is self-consistent.
4. **Fix triage ledger row 11** — update from "8-frame ⚠️ partial" to a row that reflects the in-bundle ffmpeg tour (9 frames, 828 KB GIF, 906 KB MP4).
5. **Patch `record-tour.sh`** — assert frame count after the loop, drop `2>/dev/null` on chrome (or redirect to a workdir log file), validate non-empty PNGs.
6. **Reword the FOWT-screening k-value sentence** — move "screening-only" to the front of the sentence so the disclaimer is read before the numbers.
7. **Reword Audience B email** — replace "we do pre-FEED and early-FEED mooring screening" with "we built the OC4-DeepCwind worked example to demonstrate ACE's screening-tier shape; ready to run on your project inputs" — match the page's framing.
