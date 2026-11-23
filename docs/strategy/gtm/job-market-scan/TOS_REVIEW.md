# GTM Job Market Scanner — ToS / robots.txt Review & Owner Sign-off

> **Governance artifact** for the scanner at `scripts/gtm/job-market-scanner.py`.
> Required by #1707 and prescribed by the #2348 plan v3 (`docs/plans/2026-04-19-issue-2348-scanner-tos-triage.md`).
> Owner: **Vamsee Achanta**, business owner of ACE Engineer.
> Approval mechanism: per-source `Owner approved: YYYY-MM-DD` line below, effective
> through plan approval commit `5438fd4ed` (`.planning/plan-approved/2348.md`).

## Purpose

This document governs which job-board sources the scanner may fetch and under what
conditions. It:

1. Records per-source ToS observations and robots.txt disposition.
2. Captures the engineer-proposed decision (what the scanner would do by default).
3. Captures the **owner-signed decision** (what the scanner is authorized to do).
4. For any source whose robots.txt disallows us but the owner wants retained,
   records an explicit `Owner override:` block that the scanner parses at import time.
5. Lists removed dead sources in an appendix (Q9).
6. Carries the owner-authored cease-and-desist runbook (U4).

**Removing an `Owner override:` block from this file revokes the override** —
the scanner re-parses the doc at every import and will fall back to fail-closed
robots.txt enforcement for that source.

## Mitigations in force (all sources)

- **Rate limiting** per `SOURCE_RATE_LIMITS` (2–4s between requests).
- **Source allowlist** — only `{indeed, linkedin, career_page, example-board}` are scraped.
- **Domain allowlist** per source via `SOURCE_ALLOWED_DOMAINS`.
- **robots.txt enforced** via `urllib.robotparser` inside `safe_request()`; unreachable = DENY.
- **Retry-After respected** + exponential backoff on 429/503 (`safe_request` retry loop).
- **Forged Chrome User-Agent** — the scanner does NOT impersonate a signed-in user;
  no authentication credentials are sent; no CAPTCHAs are bypassed.
- **Public-only pages** — no login walls breached, no paywall content scraped.

---

## Source: linkedin

- **Live source?** Yes. Highest-volume source in the 2026-04-13 scan (584 of 738 results).
- **ToS URL:** https://www.linkedin.com/legal/user-agreement — §8.2 restricts automated
  access; known enforcement posture (hiQ Labs v. LinkedIn remand, 2022; CFAA theories).
- **robots.txt disposition:** expected **DISALLOW** for generic User-Agents on
  `/jobs/search/` per LinkedIn's published robots policy. Verify at each scan via
  `_get_robots_parser("www.linkedin.com")`.
- **Engineer-proposed decision:** if strict robots enforcement is applied with no
  override, LinkedIn is effectively excluded from the weekly scan; recommend either
  (a) owner override documented below, or (b) migrate to LinkedIn Talent Solutions
  API (paywalled; out of scope for v3).
- **Owner-signed decision (Q11 KEEP):** retain LinkedIn for now. Owner has evaluated
  the legal risk landscape (CFAA/ToS exposure; post-hiQ remand environment) and
  accepts it. Revisit if cease-and-desist received.

### Owner override: LinkedIn robots.txt

Owner override: LinkedIn's robots.txt disallows scraping for our User-Agent on
`/jobs/search/` and related paths. Owner has reviewed the legal landscape, including
LinkedIn's post-hiQ enforcement posture and the CFAA implications of scraping
public pages, and accepts the residual risk to preserve weekly coverage of
LinkedIn-posted engineering roles. This override applies only to the `linkedin`
source; it does not extend to any other source. **Removing this entire block in
a future PR automatically revokes the override**, at which point the scanner's
fail-closed robots enforcement will exclude LinkedIn from the weekly run until
either the override is re-signed or the scanner migrates to an API path.

Effective: 2026-04-21. Revocable at any time via PR removing this block.

Owner approved: 2026-04-21
Owner: Vamsee Achanta (business owner, ACE Engineer)

---

## Source: indeed

- **Live source?** Yes. 112 of 738 results in the 2026-04-13 scan.
- **ToS URL:** https://www.indeed.com/legal — Cookies & Privacy + Terms of Service;
  §8 addresses automated access. Indeed has historically been less aggressive than
  LinkedIn in enforcement, but does maintain the legal right to block scraping.
- **robots.txt disposition:** `https://www.indeed.com/robots.txt` typically allows
  `/jobs` with `Disallow:` entries restricted to `/m/`, `/*/viewjob`, and similar
  paths the scanner does not visit. Verify at each scan.
- **Engineer-proposed decision:** keep; robots likely permits `/jobs?q=...` queries.
  If robots tightens to DENY in a future scan, fail-closed removes Indeed from the
  run automatically — no code change required.
- **Owner-signed decision:** retain Indeed under fail-closed robots enforcement.
  No override block; if robots denies in the future, Indeed is removed from the
  weekly run until robots or decision changes.

Owner approved: 2026-04-21
Owner: Vamsee Achanta (business owner, ACE Engineer)

---

## Source: career_page

- **Live source?** Yes. ~42 results in the 2026-04-13 scan across ~30 company
  career pages defined in `COMPANY_CAREER_URLS`.
- **ToS URL:** per-company; the scanner visits only the public career landing
  pages. Companies listed are target consulting prospects, not competitors.
- **robots.txt disposition:** varies per company. Enforced per-domain via the
  cache in `_get_robots_parser`. A site that disallows is silently skipped
  (with a `[WARN]` log line).
- **Engineer-proposed decision:** keep; fail-closed is acceptable because the
  scanner tolerates zero results from any single career page.
- **Owner-signed decision:** retain under fail-closed robots enforcement.
  Individual career pages that block the scanner are dropped from that week's run;
  this is acceptable signal loss given the broader dataset.

Owner approved: 2026-04-21
Owner: Vamsee Achanta (business owner, ACE Engineer)

---

## Cease-and-Desist Runbook (U4)

**Scope:** any written cease-and-desist, abuse report, or formal ToS-violation
notice received from `linkedin.com`, `indeed.com`, or any company career-page host.

**Operational steps (owner-authored):**

1. **Within 24 hours of receipt**, open a pull request that (a) removes the
   affected source from `SOURCE_RATE_LIMITS` / `SOURCE_ALLOWED_DOMAINS` in
   `scripts/gtm/job-market-scanner.py`, and (b) removes any matching
   `Owner override:` block from this file.
2. **Within the same PR**, re-comment the `gtm-job-market-scan` block in
   `config/scheduled-tasks/schedule-tasks.yaml` (re-pause the cron) while the
   situation is under review.
3. **Within 48 hours**, preserve the notice in `docs/strategy/gtm/job-market-scan/`
   under an `INCIDENTS/` directory (creating if necessary) with filename
   `YYYY-MM-DD-cease-and-desist-<source>.md`, together with the full text
   received and the date it was received.
4. **Within 7 days**, open a GitHub issue tagged `compliance` referencing the
   incident file, summarizing the path forward (drop the source, migrate to
   an API, negotiate terms), and assign the owner.
5. **External counsel** may be consulted at owner's discretion for any notice;
   consultation is **not required** for operational takedown (step 1). Counsel
   is required before any response to the issuer.

**SLA:** 24 hours to takedown PR. 48 hours to incident record. 7 days to
GitHub issue. These are maxima; faster is always acceptable.

Owner approved: 2026-04-21
Owner: Vamsee Achanta (business owner, ACE Engineer)

---

## Appendix — REMOVED sources (Q9)

The following sources were **REMOVED** from the scanner in v3 because they
produced zero usable results in production runs and carried scraping risk
disproportionate to their contribution. They are **not revisited without
owner sign-off** — re-adding any of these requires both a code change and a
new section in this document with `Owner approved: YYYY-MM-DD`.

- **google** — REMOVED. `scrape_google_jobs()` deleted. Google search results
  page was scraped via site-scoped queries (`site:linkedin.com/jobs OR site:indeed.com
  OR site:rigzone.com`). Likely UA-blocked or rendered under JS; 0 results in recent
  production runs. Google Jobs API is deprecated.
- **google_direct** — REMOVED. `scrape_google_direct()` deleted. Broader Google
  search for "hiring OR apply now" text; 0 results in recent production runs.
- **rigzone** — REMOVED. `scrape_rigzone()` deleted. Oil-and-gas-specific board;
  0 results in recent production runs suggesting their search endpoint changed
  or requires authentication.

---

## Review cadence (#2348 v3 follow-up V2)

This document is re-read when:

- **Before any owner-override revocation** (if you remove a block, verify the
  doc still makes operational sense).
- **Each calendar quarter** — skim the ToS URLs for changes; update disposition
  lines if terms have materially changed. Calendar reminder: first Monday of
  January, April, July, October.
- **Before unpausing the cron after any pause** — re-read §Mitigations and
  each live-source section.
- **Immediately** on any cease-and-desist (see runbook above).

The scanner's `_parse_owner_overrides_from_tos_review()` function parses this
file at module import; the truthiness of an override is a function of this file
alone.
