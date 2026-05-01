---
agent: adversarial-review-B-gemini
date: 2026-05-01
stance: cross-author defect hunt
upstream_status: env_failure_recovered_via_fallback_model
---

# Adversarial Cross-Review B (Gemini) — 2026-05-01 GTM Bundle

## Provenance

| Field | Value |
|---|---|
| Reviewer | Gemini CLI (Google) |
| Reviewer role | Cross-author defect-hunt (reviewer-B) |
| Author (reviewer-A) | Claude main session (this same workspace) |
| Gemini CLI version | `0.40.1` |
| Primary model attempted | `gemini-3.1-pro-preview` |
| Primary model outcome | **Failed** — RESOURCE_EXHAUSTED (HTTP 429, MODEL_CAPACITY_EXHAUSTED) followed by 5-minute timeout (exit 124) |
| Fallback model used | `gemini-2.5-flash` (via `-m gemini-2.5-flash`) |
| Fallback outcome | **Success** — exit 0, 66s wall time |
| Command (first attempt) | `GEMINI_CLI_TRUST_WORKSPACE=true timeout 300 gemini -p "$(cat /tmp/gemini-review-brief-2026-05-01.md)"` |
| Command (fallback) | `GEMINI_CLI_TRUST_WORKSPACE=true timeout 240 gemini -m gemini-2.5-flash -p "$(cat /tmp/gemini-review-brief-2026-05-01.md)"` |
| Brief size | 10,179 chars / 112 lines |
| Response size | 3,191 chars |
| Response duration | 66s (fallback) |
| Brief artifact | `/tmp/gemini-review-brief-2026-05-01.md` |
| Raw response artifact | `/tmp/gemini-response-2026-05-01-flash.txt` |
| Failed primary stderr | `/tmp/gemini-response-2026-05-01.stderr` (6,601 bytes — preserved as failure-mode evidence) |

### Upstream environment notes

- The `GEMINI_CLI_TRUST_WORKSPACE=true` envvar from `feedback_gemini_trust_env_blocks_reviews.md` was set on both attempts; the failure mode here was **upstream capacity exhaustion**, not the trust-env issue.
- The wrapper at `scripts/review/submit-to-gemini.sh` has a built-in fallback to `gemini-2.5-flash` for exactly this RESOURCE_EXHAUSTED case (lines 219-272), but it forces JSON-only output and was not used here because this review needed free-form Markdown findings rather than the structured-review JSON contract.
- After the model returned, Gemini also attempted to call `read_file` on three `aceengineer-website/content/...` paths and `run_shell_command`. All four tool calls failed (paths under sparse-checkout ignore patterns; `run_shell_command` not registered in this Gemini config). This is the `feedback_gemini_sandbox_overlay_blindness.md` pattern recurring — Gemini cannot directly read the website-repo source files in this sandbox. Findings in this artifact rely on Gemini reasoning over the brief plus my local validation passes.

---

## 1. Gemini's verdict — verbatim

```markdown
**Verdict:** MAJOR — Multiple significant internal contradictions and inconsistencies were found across the bundle's claims and artifacts, particularly concerning demo capabilities and descriptions.

**Findings:**

- **MAJOR, Category 1 & 6:** The `vessel-contractor-matrix-2026-05-01.md` (Section §2 Niche Coverage Gaps) states "FOWT" has "No demo", yet the `README.md` under "Live URLs" lists "FOWT mooring screening" as an "Audience brief" and issue #2561 claims a "FOWT mooring screening worked example" is live. This internal contradiction impacts the "Audience C" email template's claim that a demo can be re-run parametrically, suggesting an over-claim if the FOWT mooring screening is not a re-runnable demo.
- **MAJOR, Category 1:** The "Demo legend" in `vessel-contractor-matrix-2026-05-01.md` claims "D5=deepwater rigid-jumper installation (300 cases)", while the `README.md` email template for Audience A describes the same demo as having "81 tests". This is a direct numerical contradiction in the claimed scope or effort for Demo 5, potentially misleading prospects about the depth of analysis.
- **MAJOR, Category 2 & 6:** The `docs/gtm/sendable-bundles/2026-05-01/README.md` under "Live URLs" lists only "Five overnight parametric demos", excluding the "mooring demo" (`demos/mooring.html`) that was shipped as "GTM Demo 6" per issue #2115. This inconsistency means the README does not accurately represent all shipped demos and contradicts the "Audience C" claim of linking "five demos" when six were shipped.
- **MINOR, Category 3:** The `vessel-contractor-matrix-2026-05-01.md` lists "Gulf Offshore (Bourbon-related historical brand)" for row 14, despite Section §3 "Evidence Quality Notes" stating that the "Gulf Offshore" brand is historical and its status is uncertain. The shipped matrix should reflect the current, verified entity or explicitly state the uncertainty in the main matrix entry, as the existing entry carries a known, unmitigated factual weakness.
- **NIT, Category 3:** The `vessel-contractor-matrix-2026-05-01.md` for row 12 is titled "Cal Dive / Helix Energy Solutions", but Section §3 "Evidence Quality Notes" recommends to "Reword matrix row title to 'Helix Energy Solutions (Q-class fleet)' before send". While the current entry acknowledges the rebrand, the suggested re-wording indicates a minor, unaddressed stylistic inconsistency within the bundle.
- **MINOR, Category 4:** The `docs/gtm/triage-2026-05-01.md` lists "jumper-installation flesh-out" as "✅ skipped", citing the page being "table-heavy with substantive Ballymore manifold content". However, the "Reality reconciliation" section of the same document previously noted `jumper-installation.html` as "suspiciously thin (251 words vs. 994–1886 for peers) — likely under-developed". Skipping this task leaves a potentially underdeveloped demo page in the bundle, which could detract from its overall quality.

**Sharpest finding:** The direct contradiction in the claimed number of cases/tests for Demo 5 ("300 cases" in the matrix vs. "81 tests" in the README email template) would most likely confuse a prospect evaluating the depth of ACE's capabilities.
```

---

## 2. Findings, structured

| # | Severity | Category | Artifact | Finding (compressed) |
|---|---|---|---|---|
| F1 | MAJOR | 1, 6 | matrix §2 + README + #2561 | "FOWT — No demo" in matrix §2 contradicts the FOWT mooring-screening worked example shipped under #2561; impacts Audience C "re-run parametrically" promise |
| F2 | MAJOR | 1 | matrix legend + README Audience A | Demo 5: matrix claims "300 cases", live D5 page + README email say "27 OrcaFlex sections, 81 tests" — numeric contradiction |
| F3 | MAJOR | 2, 6 | bundle README | README's "Live URLs" section lists 5 demos, omits Demo 06 (mooring) shipped Wave 5 under #2115; "Five overnight engineering demos" subject line and Audience C body undercount the actual bundle |
| F4 | MINOR | 3 | matrix row 14 | "Gulf Offshore (Bourbon-related historical brand)" — §3 flags entity status as uncertain post-2019 admin, but row title/body carry the historical brand without correction |
| F5 | NIT | 3 | matrix row 12 | "Cal Dive / Helix" row title not yet rewritten to "Helix Energy Solutions (Q-class fleet)" per §3's own recommendation |
| F6 | MINOR | 4 | triage ledger | "✅ skipped" justification for jumper-installation flesh-out is internally inconsistent with the same document's "suspiciously thin" reality-reconciliation observation |

Counts: **MAJOR=3, MINOR=2, NIT=1.**

---

## 3. My validation pass

### F1 — FOWT "No demo" contradiction

**Verdict: false positive (Gemini conflated terminology).**

Local verification:
- Matrix §2 row reads: `**11 FOWT** (Available) ... No demo ... OC4-DeepCwind 1-pager` → it explicitly classifies the FOWT *demo* gap (D1–D5 only ship the existing 5 OrcaFlex/parametric demos)
- README "Audience briefs" section lists `FOWT mooring screening → fowt-mooring-screening.html` as a *brief*, not a demo
- The page itself (https://www.aceengineer.com/outreach/fowt-mooring-screening.html, 200 OK) is positioned as a "worked example" with a "Where this stops" section explicitly disowning IEC coverage

So matrix §2 is correct ("no shipped FOWT *demo* in the D1-D5 sense") and the README is correct ("audience brief, not demo"). The two terms are not contradictory — they're different artifact types. **The Audience C email's "we'll re-run it parametrically on your data inside 48 hours" promise is scoped to the demos (D1-D5), not the FOWT brief, so the over-claim Gemini posited does not actually appear in the email text.**

Marking F1 as **NOT VALIDATED** — Gemini-side terminology conflation. However, it does surface a documentation hygiene point: the README could make the "demo vs brief" distinction more explicit so a reader doesn't make the same conflation Gemini did.

### F2 — Demo 5 case-count contradiction

**Verdict: VALIDATED, real defect.**

Local verification:
- Matrix legend (line 23): `> D5=deepwater rigid-jumper installation (300)`
- README Audience A email (line 54): `Subsea jumper lift (Ballymore manifold-to-PLET, 27 OrcaFlex sections, 81 tests)`
- Live D5 page `https://www.aceengineer.com/demos/jumper-installation.html` (curl-checked):
  - `<img alt="...Ballymore manifold-to-PLET, 27 OrcaFlex sections, 81 validated tests"`
  - `Live walkthrough — ... 81/81 tests passing`
  - `Validated against Jumper_Input_Ballymore_Manifold-PLET V2.xlsx — all 81 tests pass`
  - **The page never mentions "300 cases"**.

The matrix's "300" appears to be either a planning-phase target that wasn't realized, or a different unit (parametric sweep cases vs. validated tests). Either way it is **unsupported by the live demo content** and contradicts the README the same matrix is shipped alongside. A prospect comparing matrix-legend numbers against the demo page itself will see the gap. **This is a real ship defect.**

### F3 — README undercounts demos

**Verdict: VALIDATED, real defect.**

Local verification:
- Bundle README §"Live URLs" / "Five overnight parametric demos" enumerates Demos 1-5 only (lines 24-29)
- Bundle README "the 5 demos" copy in line 14
- README Audience C subject line: "Five overnight engineering demos" (line 88)
- README Audience C body: "It links five demos (freespan/VIV screening, multi-code wall thickness, mudmat installation, shallow-water pipelay, subsea jumper lift)" (line 94)
- Triage ledger Wave 5 row: `#2115 mooring demo (Demo 06) | ✅ shipped | aceengineer-website f5186ca | /demos/mooring.html — content-only`
- Live mooring.html → 200 OK, present in `/demos/` gallery as Demo 06

So Demo 06 (mooring) is shipped, in the gallery, and linked from the outreach hub — but the **client-sendable bundle README** that drives all 3 audience email templates says "five demos". Audience B's "wind-developer" email is the most exposed: it pitches FOWT but doesn't link the mooring demo, which is the one demo most directly relevant to FOWT prospects. **This is a real defect that hurts the FOWT outreach.**

### F4 — Gulf Offshore row carries known-stale brand

**Verdict: VALIDATED as MINOR.**

Local verification: matrix row 14 is `Gulf Offshore (Bourbon-related historical brand)`, evidence URL `https://www.bourbon-online.com/en/our-fleet`. §3 row 14 explicitly says "consider re-classing to Bourbon or dropping if entity is dormant". Gemini correctly notes the row was shipped without acting on its own §3 advisory. Real but low-stakes.

### F5 — Cal Dive title vs. recommended rewording

**Verdict: VALIDATED as NIT.**

Same shape as F4: §3 recommends rewording row 12 to "Helix Energy Solutions (Q-class fleet)" before send; row 12 is currently "Cal Dive / Helix Energy Solutions". Cosmetic but Gemini caught the gap between own-recommendation and own-title.

### F6 — Triage ledger "skipped" inconsistency

**Verdict: VALIDATED as MINOR.**

Local verification:
- Triage ledger lines 24-26 (reality reconciliation): "`jumper-installation.html` is suspiciously thin (251 words vs. 994–1886 for peers) — likely under-developed"
- Triage ledger Wave 1 row: "jumper-installation flesh-out | ✅ skipped | – | 251-word count was misleading — page is table-heavy with substantive Ballymore manifold content; uniform GIF + CTA addition was sufficient"

The two statements aren't strictly contradictory (an early-pass observation can be revised on closer inspection), but the "✅ skipped" justification is a single-author re-judgment without cross-check evidence. Gemini's flag is fair — the document records both views without adjudicating. Useful for tightening future triage ledgers; not blocking for the bundle.

### Validation summary

| Finding | Validated locally? |
|---|---|
| F1 (FOWT no-demo contradiction) | **No** — terminology conflation, false positive |
| F2 (D5: 300 vs 81) | **Yes** — real, ship-defect |
| F3 (5 demos vs 6 shipped) | **Yes** — real, ship-defect, especially for FOWT audience |
| F4 (Gulf Offshore stale) | Yes (MINOR) |
| F5 (Cal Dive title) | Yes (NIT) |
| F6 (triage skipped justification) | Yes (MINOR) |

**Validation hits: 5/6. False positives: 1/6 (F1).**

---

## 4. Cross-author signal

Per `feedback_codex_sustained_major_loop.md`, when a single reviewer cycles MAJOR repeatedly while others say MINOR, that's a consensus-vs-minority decision point, not auto-correct. Here Gemini is reviewer-B in single-pass mode against the author (reviewer-A = main session). With Codex unavailable today (upstream regression #2479), there is no third lens.

The two validated MAJOR findings (F2, F3) are concrete and reproducible from the shipped artifacts themselves — they are not dependent on Gemini's reasoning or sandbox visibility. They survive the false-positive filter and should be treated as real issues to fix before the bundle goes to a real prospect.

The user (reviewer-of-reviewers) sees:
- 2 validated MAJOR findings worth acting on (D5 case-count, Demo 06 missing from bundle)
- 1 false-positive MAJOR (FOWT terminology conflation)
- 3 lower-severity findings consistent with the bundle's own §3 self-flags (so the bundle was honest about its own evidence weaknesses; the residue is between draft and ship)

This is a **MAJOR verdict that does not auto-cycle** — single pass, action items concrete, no need for further Gemini round.

---

## 5. Recommendations (if user chooses to act)

1. **F2 — Reconcile D5 case count**: change matrix legend from "D5=deepwater rigid-jumper installation (300)" to match the live page, e.g., "D5=deepwater rigid-jumper installation (Ballymore, 81 validated tests across 27 OrcaFlex sections)".
2. **F3 — Add Demo 06 to bundle README**: insert the mooring demo into the "Five overnight parametric demos" list (rename to "Six overnight parametric demos"), and add a Demo 06 link to the Audience B (FOWT) email body where it is most demo-relevant.
3. **F4, F5** — apply the §3 self-recommended rewordings to rows 12 and 14 before the matrix is referenced in any prospect-facing send.
4. **F6** — future triage ledgers should record an explicit reconciliation when an early observation is later revised, not leave both views in the document.
5. **F1** — consider adding a one-line "demos vs. briefs" terminology gloss to the bundle README so future readers (human or LLM reviewer) don't make the same conflation Gemini did.

These are author-side fixes; no source changes were made by this review agent (write-only on the workspace).
