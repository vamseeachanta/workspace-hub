---
title: GTM Bundle Hand-off — 2026-05-01 → next session
date: 2026-05-01
status: ready-to-resume
context-budget-at-handoff: 78% used / 35% remaining
---

# GTM Bundle Hand-off

This document is the durable resume-point for the 2026-05-01 GTM bundle work. The current session reached 78% context; rather than push to limits, here is everything needed to pick up cleanly in a fresh session.

## Tasks for next session

User has approved the following:

1. **Drop the P.E. claim** (Adv-C2 F2 user decision: option 3)
2. **Handle the round-2 MINOR/NIT batch** (6 items, all defined below)
3. **Make the work durable** (this doc + commit each fix individually)

---

## Task 1 — Drop the P.E.-Stamped claim

**Decision (user, 2026-05-01):** option 3 — drop the "P.E.-Stamped" claim entirely from the brochure. No license number to cite, no defensible soften-form chosen.

**Files to edit:** `aceengineer-website/content/outreach/vessel-contractor-brochure.html`

**Locations of the claim:**

| Line | Element | Current text | Edit |
|---|---|---|---|
| 5 | `<meta name="description">` | "...heavy-lift, pipelay, PLSV, FOWT. Overnight screening, **P.E.-stamped**, 48hr custom runs." | Remove "P.E.-stamped, " — keep "Overnight screening, 48hr custom runs." |
| 9 | `<meta property="og:description">` | "Parametric installation screening overnight. **P.E.-stamped**, code-compliant, contractor-ready." | Remove "P.E.-stamped, " — keep "Parametric installation screening overnight. Code-compliant, contractor-ready." |
| H1 (visible body) | `<h1>` | "Installation Screening, Overnight. **P.E.-Stamped, Code-Ready.**" | Replace with: "Installation Screening, Overnight. Code-Ready, Audit-Traceable." |

**Verification after edit:**
```bash
cd /mnt/local-analysis/workspace-hub/aceengineer-website
grep -c "P.E.\|p\.e\." content/outreach/vessel-contractor-brochure.html
# expected: 0
npm run build && npm test
# expected: 52 pages, 146/146 tests pass
```

**Verification on live site (post-deploy):**
```bash
curl -sL https://www.aceengineer.com/outreach/vessel-contractor-brochure.html | grep -ci "p\.e\."
# expected: 0
```

**Companion edit — sanity-review log:** mark Section C.4 (P.E.-stamp authority) as **N/A — claim dropped**, not pending. Path: `docs/gtm/outreach/sanity-review-log.md`. Update line 41 to add ` → resolved 2026-05-01: claim dropped from brochure (commit <SHA>). Item now N/A.` after the existing checklist text.

**Commit message template:**
```
fix(gtm): drop P.E.-Stamped claim from brochure (Adv-C2 F2 resolution)

Adv-C2 F2 flagged the brochure's prominent "P.E.-Stamped, Code-Ready"
claim as exposed: no license number, state, or stamp authority cited
anywhere in the bundle. In some jurisdictions this is unauthorized-
practice risk if not backed.

User decision (2026-05-01): drop the claim. No license to cite,
no defensible soften wording chosen.

- meta description: "...P.E.-stamped, 48hr custom runs" → "...48hr custom runs"
- og:description: "P.E.-stamped, code-compliant, contractor-ready" → "Code-compliant, contractor-ready"
- H1: "Installation Screening, Overnight. P.E.-Stamped, Code-Ready." → "Installation Screening, Overnight. Code-Ready, Audit-Traceable."

Sanity-review log Section C.4 updated to mark the item N/A (claim dropped)
rather than pending.

Build: 52 pages built clean.
Tests: 146/146 pass.
```

---

## Task 2 — Round-2 MINOR/NIT batch

Six items, each independently shippable. **Recommend one commit per item** for clean rollback if any goes sideways.

### 2a. Adv-A2 m2 — Otto Candies cited specs are PNG-only on cited URL

**File:** `docs/gtm/outreach/vessel-contractor-matrix-2026-05-01.md` §3 evidence-quality table

**Current state:** Row 17 narrative cites specific specs (340' DP2, 250-MT AHC crane, 24'×24' moonpool) but the cited URL `https://ottocandies.com/fleets/m-v-sub-sea-imr/` returns 1.7 KB of nav/scaffolding — the specs are inside a PNG image (`Sub-Sea-Vessel.png`), not in raw HTML text.

**Edit:** add a §3 row noting that Row 17 evidence URL confirms vessel-in-fleet only; specs are sourced from spec-sheet PNG / internal records.

**Insert in §3 evidence-quality table** (around line 130, after the existing Row 17 RESOLVED entry):

```markdown
| 17 | Otto Candies | Cited specs (340' DP2, 250-MT AHC crane, 24'×24' moonpool) are sourced from the per-vessel spec-sheet PNG (`Sub-Sea-Vessel.png`) and internal vessel database; raw HTML on `https://ottocandies.com/fleets/m-v-sub-sea-imr/` confirms vessel-in-fleet only, not the specific spec numbers. | Acceptable for prospect-research scope; if a prospect challenges a specific spec value, refer to the public PNG spec-sheet rather than re-citing the URL as text-grade evidence. |
```

### 2b. Adv-A2 m3 / Adv-C2 F6 — §3a Subsea7 description operationally inverted

**File:** same matrix file, §3a row 1 (Subsea7).

**Current text (line ~151):**
```
| 1 | Subsea7 | JS challenge across `subsea7.com` host (vessel datasheet PDFs also blocked) | VALID — works in browsers; no clean alternative |
```

**Reality (verified 2026-05-01):**
- `curl -sI https://www.subsea7.com/en/our-business/assets.html` (default UA) → **HTTP 200**, 51 KB body, contains borealis/seven/J-lay/fleet keywords
- `curl -sI -A "Chrome/126" ...` → **HTTP 404** with JS-challenge cookie
- The WAF is **inverted** — UA-targeted at known-browser UAs, not at default-UA probes.

**Edit:** replace the §3a row 1 description with:
```markdown
| 1 | Subsea7 | UA-targeted JS challenge on Chrome/Edge UAs only; default-UA probes get 200 + content; vessel datasheet PDFs may behave differently | VALID — works in real browsers (note: probe sweeps that use a Chrome UA will see this row as broken; default-UA `curl` succeeds) |
```

### 2c. Adv-A2 n1 — Demo 6 vs Demo 06 inconsistency

**Files:** four surfaces use different forms.

| Surface | Current form | File:line |
|---|---|---|
| Demos gallery card badge | "DEMO 06" | `aceengineer-website/content/demos/index.html:449` (approx) |
| Demos gallery comparison subtitle | "Demo 06 (mooring) is a template" | `aceengineer-website/content/demos/index.html:473` (approx) |
| Outreach hub card | "Demo 6 · station-keeping (template)" | `aceengineer-website/content/outreach/index.html:200` (approx) |
| Bundle README | "(Demo 6, illustrative until project run)" | `docs/gtm/sendable-bundles/2026-05-01/README.md:30` |

**Recommendation:** standardize on **"Demo 6"** (no leading zero) — matches the other 5 demos which are written without leading zeros throughout the bundle.

**Edits (sed):**
```bash
cd /mnt/local-analysis/workspace-hub/aceengineer-website
sed -i 's|DEMO 06|DEMO 6|g; s|Demo 06|Demo 6|g' content/demos/index.html
```

### 2d. Adv-A2 n2 — demo-links.test.js docstring incomplete

**File:** `aceengineer-website/tests/js/demo-links.test.js:4-9`

**Current text:** module docstring says "the 6 demo detail pages (freespan, wall-thickness, mudmat, pipelay, jumper-installation)" — enumerates 5 but says "6". The mooring slug is missing.

**Edit:** add `mooring` to the parenthetical:
```javascript
/**
 * Demo gallery link-check tests.
 *
 * Verifies the 6 demo detail pages (freespan, wall-thickness, mudmat, pipelay,
 * jumper-installation, mooring) are wired into the gallery at /demos/index.html
 * ...
 */
```

Plus line 7 currently says "for the four chart pages" — that's still correct since CHART_SLUGS = 4 demos that have Plotly. No change needed there.

### 2e. Adv-C2 F7 — Send-tracker template rows visually fragile

**File:** `docs/gtm/outreach/send-tracker.md:42-48`

**Current state:** template rows for Heerema (row 6) and Equinor (row 25) look like real send-log entries except for the date `2026-05-XX`. A future maintainer scanning the file may not notice the placeholder.

**Recommendation:** wrap the template rows in an HTML comment fence so they are visually unmistakable:

```markdown
<!-- TEMPLATE — DO NOT TREAT AS HISTORY. Remove these example rows when real outbound begins. -->

| Date sent | Matrix row # | Audience track | Subject line variant | Pages sent | Demo links sent | PDF attached | Followup +3d | Followup +7d | Response | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| `<<DATE>>` | 6 (Heerema) | A | "Parametric installation engineering, overnight" | hub, vc-brochure | demo-jumper, demo-mudmat | yes | scheduled | scheduled | none | in-cadence |
| `<<DATE>>` | 25 (Equinor) | C | "Six engineering demos — sendable directly" | hub | demo-pipelay | no | scheduled | scheduled | none | in-cadence |

<!-- END TEMPLATE -->
```

Replace the existing line 41-48 block with the fenced version above.

### 2f. Adv-C2 F9 — Adv-D verdict scope overclaim

**File:** `docs/sessions/2026-05-01-gtm-review-D-link-check-v2.md` line 39 (approx)

**Current text:** "**Verdict: CLEAN** — every URL in the post-remediation bundle ecosystem resolves on the live site."

**Issue:** the v2 sweep covered 20 URLs — all internal `aceengineer.com`. The matrix's 26 contractor URLs (the load-bearing trust artifact) were NOT re-probed. "Bundle ecosystem" reads as inclusive but is actually bundle-internal-only.

**Recommendation:** reword the verdict to make scope explicit:

```markdown
**Verdict: CLEAN (bundle-internal scope)** — every URL referenced in the post-remediation bundle's *aceengineer.com* surface resolves on the live site (20 URLs probed). The matrix's 26 contractor URLs were repaired in commit `83e8b46b1` and spot-verified during repair, but were NOT included in this regression sweep. Sanity-review log Section B.1 still requires a human-browser HTTP-200 check of those 26 URLs before tier-1 outbound.
```

---

## Task 3 — Make the work durable

The round-2 review reports written by the Adv-A2/B2/C2 agents were **not persisted to disk**. Their findings live only in agent return-messages plus this hand-off doc. Three durability options for the next session:

### Option A — Re-dispatch with verify-write contracts (recommended)

Re-dispatch the 3 missing review reports with explicit:
1. Required output path (already in the prompt)
2. **Final verification step**: agent must `ls -la <output_path>` and include the byte count in its summary; `git ls-files <output_path>` to confirm tracked
3. Main session checks the file exists before accepting the agent's verdict

Cost: ~3 parallel agents, ~5-10 min each.

### Option B — Reconstruct from agent return messages

Each agent's last message in this session has its 6-line summary. The detailed findings are in chat history but not in commitable files. A scribe agent could reconstruct synthesized review files from the chat transcript.

Cost: ~1 agent + scribe pass.

### Option C — Skip the report files; document only via this hand-off

Accept that the round-2 reviews live only in commit messages + this hand-off. Less durable but lower cost. The remediation work is captured; the review-step audit trail is partial.

**My recommendation: Option A** — durability is the explicit user goal, and Option B/C undermine the "show your work" stance that made the adversarial reviews valuable.

---

## Resume sequence (suggested order)

```bash
# 1. Verify state
cd /mnt/local-analysis/workspace-hub
git fetch origin
git log --oneline origin/main -10  # confirm 9d283d6d7 (round-2 remediation) is at top
cat docs/sessions/2026-05-01-gtm-bundle-handoff.md  # this doc

# 2. Drop P.E. claim (Task 1) — single commit
# follow the file edits above; commit; push

# 3. MINOR/NIT batch (Task 2) — 6 commits, in this order:
# 2a Otto specs note → 2b Subsea7 §3a reword → 2c Demo 6 standardize
# → 2d test docstring → 2e send-tracker template fence → 2f Adv-D verdict scope

# 4. Re-dispatch missing review reports (Task 3, Option A)

# 5. Final regression sweep — Adv-D3 over both bundle-internal AND 26 matrix URLs
```

## Quick-reference state at hand-off

**Live URLs (last verified 2026-05-01):**
- Outreach hub: <https://www.aceengineer.com/outreach/> (HTTP 200)
- Vessel-contractor brochure: <https://www.aceengineer.com/outreach/vessel-contractor-brochure.html>
- FOWT mooring: <https://www.aceengineer.com/outreach/fowt-mooring-screening.html>
- Demos gallery: <https://www.aceengineer.com/demos/>
- 6 demo pages: freespan, wall-thickness, mudmat, pipelay, jumper-installation, mooring
- 6 methodology pages: compound-engineering, enforcement, multi-agent-parity, orchestrator-worker, compliance-dashboard, cross-review
- Capability summary PDF: <https://www.aceengineer.com/assets/capability-summary-v1.pdf> (SHA256 sidecar in sync as of `2e97fca`)

**Sanity-review log verdict** (current row): **FLAG** until B.1 (human-browser 26-URL check) + C.4 (P.E. claim) + matrix-26 probe gap close. Task 1 above closes C.4 directly; B.1 + matrix-26 probe stay as human-driven gates.

**GitHub issues (all closed):** #2422, #2554, #2556, #2561, #2562, #2030, #2115, #2577, #2578.

**No P0 deliverable defects open.** All remaining items are gate-honesty + minor-polish.
