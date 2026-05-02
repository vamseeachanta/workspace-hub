---
title: GTM Bundle Legal & Evidence Sanity Review Log
date_initialized: 2026-05-01
audience: internal
---

# Legal & Evidence Sanity Review Log

Pre-send sanity-review checklist + log for the 2026-05-01 GTM bundle. This artifact closes acceptance criterion 4 of [#2556](https://github.com/vamseeachanta/workspace-hub/issues/2556) ("Legal/evidence sanity review is complete before public/client-facing distribution") via follow-up [#2577](https://github.com/vamseeachanta/workspace-hub/issues/2577).

The bundle does NOT enter outbound rotation until the most recent log entry below records a CLEAR sign-off. Re-run this checklist whenever any of the following changes:
- Brochure copy changes
- Capability-summary PDF rev bumps
- A new demo or methodology page joins the gallery
- Matrix evidence URLs change
- A regulatory or compliance change in the user's practice surface

## Checklist

Each item is binary CLEAR / FLAG. A FLAG blocks the bundle from outbound use until the noted remediation lands.

### A. Capability-claim accuracy

- [ ] Every capability claim in the brochure (`vessel-contractor-brochure.html`) is supported by either the live demo pages OR a footnoted public source. No vague "we are leaders in X" without a link or a measurable metric.
- [ ] FOWT page (`fowt-mooring-screening.html`) carries the explicit screening-tier scope boundary; nothing in the prose hints at IEC certification, full-coupled time-domain, or geotechnical anchor design as deliverables.
- [ ] Mooring demo (`demos/mooring.html`) is uniformly tagged as a template with illustrative values; no narrative paragraph refers to the values without the "screening-only" disclaimer leading the sentence.
- [ ] Methodology pages (compound-engineering, enforcement, multi-agent-parity, orchestrator-worker, compliance-dashboard, cross-review) describe ACE's process at a level a prospect can verify against the public website + commit history. No claims about clients ACE doesn't have permission to name.

### B. Evidence-URL hygiene

- [ ] Every URL in the matrix that's slated for actual outbound this week has been HTTP-200 verified by a human reviewer in a real browser (not an automated probe). WAF-protected rows in §3a are subject to this rule too.
- [ ] No URL points at a paywall, login wall, or expired CDN that wasn't documented as such in matrix §3.
- [ ] No URL contains tracking-token query params (utm_*, fbclid, gclid) that would leak metadata about the sender.
- [ ] The capability-summary PDF link path is current (`assets/capability-summary-v1.pdf` — `v1` rev tag is intentional; replace if a `v2` ships).

### C. Brand & assertion safety

- [ ] No competitor brand names used pejoratively. (Rule: factual segment context OK — "Subsea7 fleet of pipelay vessels" — but no "ACE is faster than Subsea7 because…")
- [ ] No client name used without explicit prior written permission.
- [ ] No vessel/equipment image used that we don't own + don't have license for. The composite GIF (`demo_comparison_matrix.gif`) is internally generated; the demo-page GIFs are screen-recordings of ACE's own software runs.
- [ ] Anything that looks like a P.E. stamp or seal is real and current — including any implied certification language in the brochure (the brochure currently uses "P.E.-Stamped, Code-Ready" — verify the stamp authority and stamp date).

### D. PII & data governance

- [ ] No prospect names, emails, phone numbers, or LinkedIn URLs in any git-tracked file under `docs/gtm/outreach/`.
- [ ] Vessel-contractor matrix's "Contact Discovery" column is status-only ("decision-maker named", "company researched only") — no actual person data.
- [ ] Send tracker (`send-tracker.md`) references rows by matrix row number, not by person.
- [ ] Bundle README's email templates use placeholder tokens (`[name]`, `[company]`) — never check in a populated copy.

### E. Regulatory / contractual

- [ ] Brochure pricing claims (if any) match `docs/gtm/capability-map.md` — last anchored 2026-04-22.
- [ ] Engagement-model section's "48-hour parametric run" promise is a real operational commitment ACE can defend in case of a delivery slip; otherwise replace with "best-effort" framing.
- [ ] Any standard cited (DNV, API, ISO, ASME) is current rev. Standards rotate every 3–7 years; recheck before each major outbound batch.

### F. Cross-document consistency

- [ ] "AceEngineer" capitalization is consistent across all client-facing pages (no "aceEngineer" / "ACE Engineer" mid-sentence drift).
- [ ] Demo case-counts in email templates match the live demo pages exactly (Adv-C catch: "Demo 5 = 81 tests" not "300 cases"; "992 + Ballymore worked example" not "1,292 parametric cases").
- [ ] Outreach hub demo grid count matches the bundle README "Live URLs" count matches the sitemap (Adv-A catch: bundle had 5/6/12 mismatch pre-fix).

## Sign-off log

Append a row each time the bundle is reviewed. CLEAR means OK to outbound; FLAG means blocked with named remediation.

| Date | Reviewer | Bundle revision | Verdict | Flagged items + remediation | Cleared on |
|---|---|---|---|---|---|
| 2026-05-01 | adversarial-review-pass (Adv-A + Adv-B + Adv-C + Adv-D) | aceengineer-website [`5f45587`] + workspace-hub [`35209622b`] | FLAG | (a) #2577 send-tracker missing → this artifact, ✅; (b) #2578 14 broken matrix URLs → repaired in `83e8b46b1`, ✅; (c) §3b narrative-edit rows pending → in flight as of 2026-05-01 | pending §3b |
| 2026-05-01 | (post-MINOR/NIT batch) | aceengineer-website [`b60722c`, `06f2f51`, `3e89cc4`] + workspace-hub [`83e8b46b1`, `3ccb238ad`] | FLAG | §3b narrative items still open (Bourbon split, Otto Candies vessel substitution) | pending |
| TBD | human reviewer | (next bundle revision) | (CLEAR / FLAG) | (any remaining flags + their resolution path) | (date) |

## Cadence

- **Per-outbound check:** the per-outbound checklist in `send-tracker.md` is the operational gate; it does not replace this sanity-review log but provides the row-by-row verification.
- **Per-bundle-rev check:** any commit that changes capability claims, demo case-counts, scope boundaries, or pricing triggers a fresh row in the Sign-off log above. The bundle is not send-eligible until that row records CLEAR.
- **Quarterly recheck:** standards rotate; redo Section E in full each quarter even if nothing else changed.

---

**Note on self-review:** the 2026-05-01 review pass that surfaced this artifact's need was Claude-driven (Adv-A + Adv-B + Adv-C + Adv-D). For high-stakes outbound (e.g., a tier-1 enterprise prospect), pair this checklist with a fresh adversarial-review pass — the cross-author validation catches what one author misses.
