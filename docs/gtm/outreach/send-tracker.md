---
title: GTM Outbound Send Tracker
date_initialized: 2026-05-01
audience: internal
---

# Outbound Send Tracker

Per-prospect send ledger for the 2026-05-01 GTM bundle and beyond. Public-side ledger only — keeps the matrix-row reference, what was sent, when, and whether a response was received. **PII (individual contact emails, decision-maker names, private routing) lives in the gitignored `private/` companion or external CRM; this file references matrix rows by number, not by person.**

This artifact closes acceptance criterion 3 of [#2556](https://github.com/vamseeachanta/workspace-hub/issues/2556) ("Send tracker exists and distinguishes public artifact paths from private contact details") via follow-up [#2577](https://github.com/vamseeachanta/workspace-hub/issues/2577).

## Per-outbound row schema

| Date sent | Matrix row # | Audience track | Subject line variant | Pages sent | Demo links sent | PDF attached | Followup +3d | Followup +7d | Response | Status |
|---|---|---|---|---|---|---|---|---|---|---|

**Column definitions:**
- **Date sent**: ISO 8601 date of first outbound (`YYYY-MM-DD`)
- **Matrix row #**: row number from `vessel-contractor-matrix-2026-05-01.md` (1–26). Use `EXT-<n>` for prospects outside the matrix.
- **Audience track**: A (vessel-contractor) / B (FOWT/wind) / C (generic operator) / D (LNG/marine-terminal) — must match a paste-and-send template in `sendable-bundles/2026-05-01/README.md` § Email-ready text.
- **Subject line variant**: short label of which subject was used (lets us A/B test over time)
- **Pages sent**: comma-separated short codes — `hub`, `vc-brochure`, `fowt`, `demo-mooring`, `demo-jumper`, etc.
- **Demo links sent**: same convention; how many demos went in this email
- **PDF attached**: yes / no — did the 1-page capability summary go as an attachment, or was it left as a download link?
- **Followup +3d / +7d**: yes / scheduled / skipped
- **Response**: none / auto-reply / personal / interested / declined
- **Status**: in-cadence / paused / converted / dead-end / blocked

## Pre-send checklist (per outbound)

Run this before clicking send on any of the matrix rows. Failing any item = do NOT send; remediate first.

- [ ] Matrix row's evidence URL returns HTTP 200 in a real browser today (not just at original commit time). Probe for known WAF/TLS-strict rows (Subsea7, McDermott, TechnipFMC, Saipem, Hornbeck, Cadeler, Woodside per matrix §3a) is the *human* clicking the link, not an HTTP probe.
- [ ] All demo links in the email body return HTTP 200 (`curl -sLo /dev/null -w "%{http_code}" <url>` per link).
- [ ] Capability-summary PDF attaches at full size (~315 KB; verify hash against `assets/capability-summary-v1.pdf.sha256`).
- [ ] Email body re-read once for the prospect's industry — every claim supported by the linked page (no done-tense overclaim against worked-example pages, especially FOWT).
- [ ] Subject line doesn't claim a number (e.g., "Six demos") that's wrong as of today.
- [ ] Sender footer carries `support@aceengineer.com` (not `info@`) — matches site-wide canonical.

## Template rows (illustrative; remove or replace as outreach begins)

| Date sent | Matrix row # | Audience track | Subject line variant | Pages sent | Demo links sent | PDF attached | Followup +3d | Followup +7d | Response | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-05-XX | 6 (Heerema) | A | "Parametric installation engineering, overnight" | hub, vc-brochure | demo-jumper, demo-mudmat | yes | scheduled | scheduled | none | in-cadence |
| 2026-05-XX | 25 (Equinor) | C | "Six engineering demos — sendable directly" | hub | demo-pipelay | no | scheduled | scheduled | none | in-cadence |

(remove these illustrative rows when real outbound begins)

## Open backlog (do not send until cleared)

Matrix rows that are documented as **not send-ready** until follow-up work lands. Pulling these into actual outbound without the noted upgrade is operationally dishonest.

- ~~**Row 14 Bourbon / Gulf Offshore** — narrative split deferred~~ → ✅ **RESOLVED 2026-05-01** in commit [`a29148192`]: Row 14 retitled "Bourbon Offshore (post-SPP)"; "Gulf Offshore" reference dropped (research confirmed GulfMark absorbed into Tidewater Row 18 since 2018-11-15). Matrix §3b documents.
- ~~**Row 17 Otto Candies** — Kelly Ann Candies sold to Aqueos~~ → ✅ **RESOLVED 2026-05-01** in commits [`a29148192`] (vessel substitution) + [`c435869b3`] (P2→P1 promotion): Sub-Sea Candies (340 ft DP2 MPSV, ex-Harvey Sub-Sea) replaces Kelly Ann; Otto Candies promoted to P1 to join the GoM P1 block (#15 + #16 + #17) per #2562. Matrix Row 17 + §1 sequence row 9 + §3b RESOLVED documents.
- WAF rows (1, 2, 3, 4, 15, 19, 24): URL works in real browsers but probe-fails. Pre-send rule = human reviewer clicks the link. Document the click date in a "last verified" annotation if you want to send the same row twice in a quarter.

## Aggregate metrics (filled in weekly)

| Week ending | Outbounds sent | Responses received | Conversions to call | Conversions to engagement | Notes |
|---|---|---|---|---|---|
| 2026-05-08 | 0 | 0 | 0 | 0 | Bundle shipped 2026-05-01; first outbounds pending review pass closure |

---

**Conventions:**
- This file is **append-only history** — never delete a row. If a status changes, update the Status column on the existing row.
- The `private/` companion (path: `~/.gtm-outreach-private/2026-05-01-contacts.md` or wherever you put PII) is **NOT** in git. Keep it that way.
