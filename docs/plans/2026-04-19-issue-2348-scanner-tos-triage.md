# Plan for #2348: Scanner ToS / Robots / Unpause Governance

> **Status:** draft v3 (revised 2026-04-20 after user design-Q answers) — not yet re-dispatched; awaiting round-2 review
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2348
> **In-scope issue:** #1707 (OPEN — robots.txt + documented ToS review + unpause governance)
> **Out of scope (already closed 2026-04-20):** #1708 (closed, `70c3975b2`), #1709 (closed, `d0840bd42`)
> **Complexity:** T2 — code changes (robots.txt in `safe_request()` + dead-source removal from `SOURCE_ALLOWLIST`) + compliance docs + explicit unpause checklist gated on owner sign-off
> **Author:** Claude Code

---

## Revision History

| Version | Date | Change |
|---|---|---|
| v1 | 2026-04-17 | Initial draft — 3-issue triage (#1707 fix + #1708/#1709 close-with-comment) + cron-pause flag |
| v2 | 2026-04-17 | Post-review refresh: (a) remove #1708/#1709 close actions — they closed during round-1 review cycle; (b) reconcile sources to live reality (`linkedin/indeed/career_page` only — Google and Rigzone NOT in live run); (c) add non-engineer approver to sign-off chain; (d) replace unpause "recommendation" with explicit checklist; (e) flip robots-unreachable default ALLOW → DENY (fail-closed); (f) mark cease-and-desist runbook as requiring counsel input or explicit deferral with owner sign-off; (g) add README + operator-doc updates as Commit-2 hard requirement; (h) rewrite rollback as explicit state machine given cron is already paused; (i) drop the spurious memory-correction item |
| v3 | 2026-04-20 | Integrate user answers to Q9/Q10/Q11. **Q9 (dead sources: REMOVE) — prescribed, not yet implemented:** implementation will remove `google`, `google_direct`, `rigzone` from `SOURCE_RATE_LIMITS` + `SOURCE_ALLOWED_DOMAINS` (scanner.py:146-163), delete the dead-code scrape functions (`scrape_google_jobs`, `scrape_google_direct`, `scrape_rigzone`) along with their dispatcher calls (scanner.py:644/663/669), and update `TOS_REVIEW.md` (file itself prescribed — see §Files to Change) to list them as "REMOVED — zero results, not revisited without owner sign-off"; README to be updated to the 3-source reality. **Q10 (approver: owner-only):** dual-path "counsel OR owner" framing collapsed to owner-only; owner = user (Vamsee Achanta) acting as business owner of ACE Engineer; sign-off prescribed as a datestamped "Owner approved: <YYYY-MM-DD>" line per source in `TOS_REVIEW.md` at implementation time. **Q11 (LinkedIn: KEEP):** explicit keep-decision documented with risk acknowledgment; robots.txt integration will likely DENY LinkedIn; plan prescribes a documented owner-override mechanism (owner to sign an explicit "scraping override despite robots.txt" block in `TOS_REVIEW.md`), OR a switch to LinkedIn official API/RSS as a deferred alternate. Unpause checklist rewritten for 3-source reality. New TDD tests specified for allowlist composition and per-source owner-signoff (test files also prescribed). New risk entry on robots-vs-owner-directive conflict. |
| v3-addendum | 2026-04-20 | Tense-audit per `feedback_plan_past_tense_artifact_claims.md`: scanner.py still carries all 6 sources at plan-commit time (verified via `grep 'scrape_google\|scrape_rigzone' scripts/gtm/job-market-scanner.py` → 3 matches at lines 302/392/474; `SOURCE_RATE_LIMITS` at 145-153 still lists all 6). `TOS_REVIEW.md` is absent from git. `_OWNER_OVERRIDE_SOURCES` + `urllib.robotparser` integration absent. Revision-history language in v3 rewritten above to describe this work as **prescribed**, not as **done**. |

---

## Adversarial Review Summary (Round 1, 2026-04-17)

| Reviewer | Verdict | BLOCKER/HIGH findings | Addressed in v2 |
|---|---|---|---|
| Claude (Opus 4.7) | REQUEST-CHANGES | F1 stale #1708/#1709 close actions; F2 LinkedIn elevated-risk deferred; F3 robots-unreachable default wrong; F4 C&D runbook beyond agent authority; F5 rollback state machine ambiguous; F6 memory correction deferred | F1 removed; F3 flipped to DENY; F4 reframed as counsel-dependent or deferred-with-sign-off (v3: collapsed to owner-only per Q10); F5 rewritten as state machine; F6 re-examined — determined not applicable. F2 LinkedIn: v3 resolves via Q11 KEEP + override mechanism |
| Codex (GPT-5.4) | MAJOR-REVISION | M1 engineer-authored legal compliance; M2 resume gate too soft; M3 plan stale post-close; m1 review scope mismatch vs live sources; m2 README/operator docs not mandatory before unpause | M1 owner approver added (v3: owner-only per Q10); M2 resume gate replaced with concrete checklist; M3 de-scoped #1708/#1709; m1 live-source table rewritten (v3: dead sources removed per Q9); m2 README update now Commit-2 hard requirement |

Round 2 dispatch: after v3 commit lands. Do NOT advance to `status:plan-approved` until round-2 review is complete.

---

## Resource Intelligence Summary

### What the parent issue shipped
- `#1671` (closed 2026-04-05) — shipped GTM job-market scanner at `scripts/gtm/job-market-scanner.py` (~1360 lines).
- Cron schedule: `config/scheduled-tasks/schedule-tasks.yaml` line 411 region — `id: gtm-job-market-scan`, schedule `0 5 * * 1` (Monday 5AM UTC, weekly).
- Wrapper: `scripts/gtm/weekly-scan-refresh.sh` — `git pull`, run scanner, auto-commit, auto-push to `main` (public repo).
- **Current state (verified 2026-04-17):** cron is PAUSED via commit `a9a2a922b`. `schedule-tasks.yaml` region for `gtm-job-market-scan` is fully commented out.

### Live sources (ground truth) + Q9 dispositions
The most recent actual scan output (`docs/strategy/gtm/job-market-scan/dashboard.md`, 2026-04-13) shows:

| Source | Live? | Count last scan | v3 disposition |
|---|---|---|---|
| `linkedin` | YES | 584 | **KEEP (Q11)** — highest-volume; robots-conflict reconciled via owner override |
| `indeed` | YES | 112 | KEEP — pending per-source owner sign-off |
| `career_page` | YES | 42 | KEEP — pending per-source owner sign-off |
| `google` | NO | 0 | **REMOVE (Q9)** — allowlisted-but-dead; likely UA-blocked |
| `google_direct` | NO | 0 | **REMOVE (Q9)** — allowlisted-but-dead |
| `rigzone` | NO | 0 | **REMOVE (Q9)** — allowlisted-but-dead |

### Exact code sites for dead-source removal (Q9)
The constants live in `scripts/gtm/job-market-scanner.py` (verified 2026-04-20 via grep):

| Site | Lines | v3 action |
|---|---|---|
| `SOURCE_RATE_LIMITS` dict | 145-153 | Remove `google` (146), `google_direct` (147), `rigzone` (150) |
| `SOURCE_ALLOWLIST` | 154 | Derived from `SOURCE_RATE_LIMITS` — auto-updates; verify equals `{"indeed", "linkedin", "career_page", "example-board"}` |
| `SOURCE_ALLOWED_DOMAINS` | 155-163 | Remove `google` (156), `google_direct` (157), `rigzone` (160) |
| `scrape_google_jobs()` | 302-348 | Delete function |
| `scrape_rigzone()` | 392-429 | Delete function |
| `scrape_google_direct()` | 474-516 | Delete function |
| `scrape_linkedin_search()` | 431-472 | Retain — Q11 KEEP |
| `scrape_indeed()` | 350-390 | Retain; verify no residual `site:rigzone.com` in query (line 308 area) after Google scraper removal |
| Main scan loop dispatcher | 644, 663, 669 | Delete calls to `scrape_google_jobs`, `scrape_rigzone`, `scrape_google_direct` + any accumulator updates |

**Post-removal `SOURCE_ALLOWLIST` composition (target state after implementation; current git state still has all 6):** `{"indeed", "linkedin", "career_page", "example-board"}` (3 live scraped + 1 test fixture). The three scraped live sources will be `linkedin`, `indeed`, `career_page`. Today at plan-commit time, `SOURCE_ALLOWLIST = set(SOURCE_RATE_LIMITS)` in scanner.py:154 still evaluates to the 7-entry set; verify the shrink landed via `test_allowlist_contains_exactly_3_live_sources` before declaring #1707 complete.

### #1707 acceptance criteria status (file-verified)

| Criterion | File + lines | Status |
|---|---|---|
| Per-site rate limit config | `job-market-scanner.py:145-153` | DONE (present in git; will be pruned to 4 entries by v3 implementation) |
| Retry-After respected | `job-market-scanner.py:197-206` | DONE (present in git) |
| Exponential backoff on 429/503 | `job-market-scanner.py:198-207` | DONE (present in git) |
| Source allowlist | `job-market-scanner.py:154-163` | DONE structurally (derived constant exists) — **v3 prescribes shrinking from 7 entries to 4** |
| robots.txt check before scraping | grep `robotparser` → 0 matches | **GAP** (v3 prescribed) |
| Documented ToS compliance per source | No `TOS_REVIEW.md` in git | **GAP** (v3 prescribed) |
| Consider official APIs | No ADR | **GAP** (LinkedIn API as deferred alternate per Q11) |

### The legal/ToS dimension
Live sources (LinkedIn, Indeed, career pages) all have terms addressing automated access. LinkedIn has a known enforcement posture (hiQ remand 2022, CFAA theories). The current scanner:
- Uses a forged Chrome UA (line 132-135)
- No robots.txt check
- No ToS review on record
- Auto-commits to a **public** repo

**This is a compliance gap.** Owner is the sign-off authority per Q10.

### Parallel work / worktrees
- `git worktree list` — no worktree for #1707 or #2348. Safe.
- No existing plan for #1707.

### Sources consulted
Issue bodies (#2348, #1707), scanner source (grep-verified `SOURCE_ALLOWLIST` at line 154), cron wrapper, cron config, dashboard.md, README.md, round-1 Claude review, Codex round-1 review, git log, `gh issue view`, `docs/plans/README.md` index, user Q9/Q10/Q11 answers. ≥13 sources.

---

## Legal Authority (v3 — owner-only, per Q10)

Per Q10: the **owner** is the approver. The "counsel OR owner" hedge from v2 is dropped — owner is sufficient.

| Role | Responsibility | Treatment |
|---|---|---|
| Engineer (plan author) | Observe, document, implement mitigations | Drafts `TOS_REVIEW.md` as observations |
| **Owner (Vamsee Achanta, business owner of ACE Engineer)** | Decide keep/remove per source; sign off `TOS_REVIEW.md`; author C&D runbook; accept residual risk | **Canonical approver** |

**Sign-off mechanism (Q10):** per-source owner approval is a datestamped line in `TOS_REVIEW.md`:

```
## Source: linkedin
...
Owner approved: 2026-04-20
Owner: Vamsee Achanta (business owner, ACE Engineer)
```

The line must be committed by the user's git identity (`vamsee.achanta@aceengineer.com`). No separate trailer; no counsel path required. Owner may consult counsel at discretion — outside plan acceptance criteria.

---

## LinkedIn Handling (v3 — Q11: KEEP + robots-conflict reconciliation)

**Decision (Q11):** KEEP LinkedIn. Highest-volume live source (584 on 2026-04-13 — 79% of all results). User explicitly directs retention.

**Conflict:** LinkedIn's robots.txt is known-restrictive. The U1 robots check will likely DENY LinkedIn URLs for a generic UA. This conflicts directly with owner's KEEP directive.

**Reconciliation paths (v3 documents all three; owner picks one at U2 sign-off):**

1. **Owner override (canonical, lowest friction):** Owner signs an explicit override block for LinkedIn in `TOS_REVIEW.md`:
   ```
   ## Source: linkedin
   ...
   Owner override: LinkedIn robots.txt disallows scraping. Owner has evaluated
   the legal risk (CFAA/ToS exposure; post-hiQ enforcement landscape) and
   accepts it. Effective <date>. Revocable at any time via PR removing this block.
   Owner approved: <date>
   Owner: Vamsee Achanta (business owner, ACE Engineer)
   ```
   Scanner honors override via `_OWNER_OVERRIDE_SOURCES`, populated by parsing `TOS_REVIEW.md` at import. When `can_fetch()` returns False AND source is in override set, scanner logs `[WARN] robots.txt disallows <url>; owner override in effect per TOS_REVIEW.md` and proceeds. **Removing the override block from the doc in a future PR automatically disables the override** (since the constant parses from the doc).

2. **Official API switch (deferred):** LinkedIn Talent Solutions API — paywalled, enterprise contract + OAuth. Documented as deferred; not in v3 scope. Owner may choose as future follow-up.

3. **Alternate RSS feed (deferred, unlikely):** LinkedIn public job-search RSS if still available. Would require engineering spike. Not in v3 scope.

**Code-level safeguard:** override is file-driven, not flag-driven. No CLI flag or env var can bypass robots — only a committed, signed block in `TOS_REVIEW.md`. Keeps the override auditable and revocable via a single PR.

---

## Unpause Checklist (v3 — 3-source reality + Q11 reconciliation)

The cron is already paused. Unpause requires **all** of the following, in order:

- [ ] **U1 — robots.txt parser wired into `safe_request()`:** `urllib.robotparser.RobotFileParser` call between allowlist check and rate-limit sleep. Unit tests prove skip-on-disallow and fail-closed on unreachable. Each live source (`linkedin`, `indeed`, every URL in `COMPANY_CAREER_URLS`) either passes the check OR is explicitly handled. **Q11 contingency:** LinkedIn will likely DENY; Commit 2 must not silently skip — owner-override path (U2) applies. If no override signed, LinkedIn is effectively removed from the live run. No silent-skip; no code-level robots-override flag.

- [ ] **U2 — `TOS_REVIEW.md` committed with per-source owner sign-off (Q10).** Exactly three live-source sections: `linkedin`, `indeed`, `career_page`. Each ends with `Owner approved: <YYYY-MM-DD>` authored by the user's git identity. A "REMOVED sources (Q9)" appendix lists `google`, `google_direct`, `rigzone` with "REMOVED — zero results, not revisited without owner sign-off." If LinkedIn's robots.txt DENIES, the LinkedIn section carries the explicit owner-override block from §LinkedIn Handling.

- [ ] **U3 — `docs/strategy/gtm/job-market-scan/README.md` updated** to reflect 3-source reality (`linkedin`, `indeed`, `career_page`) — not the previous 6-source allowlist. README states: (a) dead sources removed per Q9; (b) robots.txt enforcement active; (c) pointer to `TOS_REVIEW.md`; (d) any LinkedIn owner-override disclosed; (e) "auto-commits results to main" remains true but "only for sources whose ToS review is signed off by owner".

- [ ] **U4 — Cease-and-desist runbook committed (owner-authored, canonical per Q10).** Owner-authored, committed in `TOS_REVIEW.md` (or a separate `CEASE_AND_DESIST_RUNBOOK.md` linked from it). Operational action: "remove source from `SOURCE_ALLOWLIST` within 24h via PR; remove owner-override for that source; re-pause cron." Owner signs with date. External counsel remains available at owner's discretion but is not required.

- [ ] **U5 — Dry-run cycle succeeds on the 3 remaining live sources** (`linkedin`, `indeed`, `career_page`): `python scripts/gtm/job-market-scanner.py --limit 2 --skip-career-pages` then full run. No policy violations — no disallowed fetches (unless owner-override in force), no zero-result full-block on a signed source. If dry-run is degenerate (robots denies LinkedIn AND owner declined override), unpause is deferred pending re-scoping.

All five required. If any fails, resting state is **paused**. Unpause is a separate commit.

---

## Triage Decision — #1707 only

**Decision: FIX** — robots.txt + documented ToS review + unpause governance + Q9 dead-source removal.

Remaining work on #1707 (v3 scope):
1. `urllib.robotparser.RobotFileParser` in `safe_request()`; cache per-domain; skip on disallow; **fail-closed on unreachable** (v2); **owner-override honored iff doc-parsed** (v3, Q11).
2. **Dead-source removal (Q9):** remove `google`, `google_direct`, `rigzone` from `SOURCE_RATE_LIMITS` + `SOURCE_ALLOWED_DOMAINS`; delete `scrape_google_jobs`, `scrape_google_direct`, `scrape_rigzone` functions; delete their dispatcher calls. `SOURCE_ALLOWLIST` → `{"indeed", "linkedin", "career_page", "example-board"}`.
3. `TOS_REVIEW.md` — per-source facts for 3 live sources + robots disposition + engineer proposal + **owner-signed decision (Q10)** + owner-authored C&D runbook; REMOVED-sources appendix for Google/Rigzone; LinkedIn owner-override block if robots denies (Q11).
4. README.md — 3-source reality, not 6-source allowlist.

**Labels:** `priority:high` + `status:plan-review` → (after round-2) `status:plan-approved` → `status:in-progress`. Owner: `vamseeachanta`.

---

## Pseudocode

### A. robots.txt respect in `safe_request()` — fail-closed + doc-driven owner override

```python
# module-level cache
_ROBOTS_CACHE: dict[str, urllib.robotparser.RobotFileParser | None] = {}

# Populated at import time by parsing TOS_REVIEW.md for owner-override blocks.
# Removing the block from the doc shrinks this set and stops scraping.
_OWNER_OVERRIDE_SOURCES: set[str] = _parse_owner_overrides_from_tos_review()

def _get_robots_parser(netloc: str) -> urllib.robotparser.RobotFileParser | None:
    """Return cached RobotFileParser, or None if unreachable (caller treats as DENY)."""
    if netloc in _ROBOTS_CACHE:
        return _ROBOTS_CACHE[netloc]
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(f"https://{netloc}/robots.txt")
    try:
        rp.read()
    except Exception as e:
        print(f"  [WARN] robots.txt unreachable for {netloc}: {e}; DENYING (fail-closed)")
        _ROBOTS_CACHE[netloc] = None
        return None
    _ROBOTS_CACHE[netloc] = rp
    return rp

# inside safe_request(), AFTER allowlist check, BEFORE time.sleep(delay):
rp = _get_robots_parser(parsed.netloc)
if rp is None:
    if source_name in _OWNER_OVERRIDE_SOURCES:
        print(f"  [WARN] robots.txt unreachable; OWNER OVERRIDE in effect for {source_name}; proceeding")
    else:
        return None  # fail-closed
elif not rp.can_fetch(USER_AGENT, url):
    if source_name in _OWNER_OVERRIDE_SOURCES:
        print(f"  [WARN] robots.txt disallows {url}; OWNER OVERRIDE per TOS_REVIEW.md; proceeding")
    else:
        return None
```

### B. `TOS_REVIEW.md` structure (new file)

- Header: doc purpose; owner identity; date.
- Per-source section for each live source (`linkedin`, `indeed`, `career_page`): ToS URL, observed robots disposition, engineer-proposed decision, **owner-signed decision**, residual risk acknowledgment.
- LinkedIn section (if robots denies): explicit owner-override block.
- Mitigations in force: rate limits, allowlist, robots enforcement, retry/backoff.
- **C&D runbook (owner-authored):** operational step + owner sign-off + date.
- **Appendix — REMOVED sources (Q9):** `google`, `google_direct`, `rigzone` — "REMOVED — zero results in production runs, not revisited without owner sign-off."

---

## Files to Change

| Action | Path | Reason | Commit |
|---|---|---|---|
| Modify | `scripts/gtm/job-market-scanner.py` | (a) Add `urllib.robotparser` import; `_ROBOTS_CACHE`; `_get_robots_parser`; fail-closed check inside `safe_request()`. (b) **Q9 removal:** delete `google`, `google_direct`, `rigzone` entries from `SOURCE_RATE_LIMITS` (146, 147, 150) + `SOURCE_ALLOWED_DOMAINS` (156, 157, 160); delete `scrape_google_jobs` (302-348), `scrape_google_direct` (474-516), `scrape_rigzone` (392-429); delete dispatcher calls (644, 663, 669). (c) **Q11 override:** add `_parse_owner_overrides_from_tos_review()` + `_OWNER_OVERRIDE_SOURCES`; honor in `safe_request()` per §A. | 2 |
| Create | `docs/strategy/gtm/job-market-scan/TOS_REVIEW.md` | Per-source review for 3 live sources + **owner sign-off (Q10)** + owner-authored C&D runbook + REMOVED-sources appendix (Q9) + LinkedIn owner-override block if needed (Q11) | 1 |
| Modify | `docs/strategy/gtm/job-market-scan/README.md` | 3-source reality (not 6-source); robots enforcement; pointer to `TOS_REVIEW.md`; LinkedIn override disclosure if in force; revised "auto-commits" line | 2 |
| Modify | `docs/strategy/gtm/job-market-scan/dashboard.md` (header) | Regenerates on next scan | auto (Commit 3 side-effect) |
| Create | `tests/gtm/test_robots_respect.py` | `_get_robots_parser` caching + disallow → None + unreachable → DENY; owner-override bypasses deny when source in override set | 2 |
| Create | `tests/gtm/test_source_allowlist.py` | **Q9:** `test_allowlist_contains_exactly_3_live_sources` — asserts `SOURCE_ALLOWLIST == {"indeed", "linkedin", "career_page", "example-board"}`; `test_dead_source_scrapers_removed` — asserts `scrape_google_jobs`, `scrape_google_direct`, `scrape_rigzone` not importable | 2 |
| Create | `tests/gtm/test_tos_review_doc.py` | **Q10:** `test_tos_review_md_has_owner_signoff_per_source` — each live-source section contains `Owner approved: YYYY-MM-DD`; `test_tos_review_md_lists_removed_sources` — REMOVED appendix mentions google/google_direct/rigzone; `test_linkedin_override_parser_round_trips` — `_parse_owner_overrides_from_tos_review()` returns `{"linkedin"}` iff override block present | 2 |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | Un-comment `gtm-job-market-scan` — ONLY after U1-U5 green | 3 |
| Update | `docs/plans/README.md` | Plan index row → v3 | this commit |

**Not modified:** `cumulative-index.json`, scanner outputs, `weekly-scan-refresh.sh`.

---

## TDD Test List

| Test | Claim | Pass criterion |
|---|---|---|
| `test_robots_parser_cached` | `_get_robots_parser("www.linkedin.com")` called twice reads robots.txt once | mock call count == 1 |
| `test_robots_disallow_blocks_fetch` | `can_fetch` False AND source not in override → `safe_request` returns None | requests.get not called |
| `test_robots_unreachable_fails_closed` | `rp.read()` raises AND source not in override → returns None | requests.get not called |
| `test_owner_override_bypasses_disallow` (NEW v3) | `can_fetch` False AND source in `_OWNER_OVERRIDE_SOURCES` → `safe_request` proceeds with logged warning | requests.get IS called; warning logged |
| `test_allowlist_contains_exactly_3_sources` (NEW v3, Q9) | Post-Q9, `SOURCE_ALLOWLIST == {"indeed", "linkedin", "career_page", "example-board"}` | equality |
| `test_dead_source_scrapers_removed` (NEW v3, Q9) | `scrape_google_jobs`, `scrape_google_direct`, `scrape_rigzone` not at module scope | `hasattr` False for all |
| `test_tos_review_md_has_owner_signoff_per_source` (NEW v3, Q10) | Each live-source section contains `Owner approved: YYYY-MM-DD` | regex per section |
| `test_tos_review_md_lists_removed_sources` (NEW v3, Q9) | REMOVED appendix mentions google, google_direct, rigzone | substring match |
| `test_readme_references_tos_review` | README contains relative link to `TOS_REVIEW.md` | link present |
| (verification) retention/dedup tests | `tests/gtm/test_job_market_retention.py`, `test_job_market_scanner.py` unchanged | all pass |

Test-writing order: Q9 allowlist tests first (drives deletion), robots tests second, override test third, doc tests last.

---

## Acceptance Criteria

### For this plan (#2348)
- [ ] Plan v3 committed
- [ ] Index row in `docs/plans/README.md` → `draft (v3)` with Q9/Q10/Q11 notes
- [ ] Round-2 adversarial review dispatched (Claude + Codex) and resolved before `status:plan-approved`

### For #1707 residual fix (code work)
- [ ] `_get_robots_parser` + per-domain cache in `job-market-scanner.py`
- [ ] `safe_request()` robots check; skip on disallow (unless override); **fail-closed on unreachable**
- [ ] Dead sources removed per Q9
- [ ] `_parse_owner_overrides_from_tos_review()` + `_OWNER_OVERRIDE_SOURCES` implemented
- [ ] New tests pass (`test_robots_respect.py`, `test_source_allowlist.py`, `test_tos_review_doc.py`)
- [ ] Existing tests still pass
- [ ] `TOS_REVIEW.md` created with 3 per-source reviews + owner sign-off + C&D runbook + REMOVED appendix + LinkedIn override block (if needed)
- [ ] `README.md` reflects 3-source reality
- [ ] #1707 closed with comment citing implementing commit + `TOS_REVIEW.md` path

### For unpause (Commit 3)
- [ ] All five U1-U5 green
- [ ] Dry-run scan clean on 3 live sources
- [ ] Commit 3: un-comment cron task

---

## Rollback / State Machine

Cron is currently **paused**. Four legal resting states:

| State | paused? | docs? | robots.txt code? | Q9 removal? | OK? |
|---|---|---|---|---|---|
| S0 (current) | YES | no | no | no | **YES** — baseline |
| S1 (after Commit 1) | YES | yes | no | no | **YES** — docs only |
| S2 (after Commit 2) | YES | yes | yes + tests green | yes | **YES** — code + paused |
| S3 (after Commit 3) | no | yes | yes + tests green | yes | **YES** — target |

**Forbidden states:**
- unpaused + no robots code
- unpaused + partial-robots (tests red)
- paused + robots code + no `TOS_REVIEW.md`
- Q9 removal partially applied (must land atomically)

**Rule:** Never commit Commit 3 unless Commits 1+2 green and U1-U5 all check. If Commit 2 tests fail, stop and fix — do not revert Commit 1. Production defect rolls back to S2, not S3.

### Failure modes
- **Scanner crashes on `rp.read()`:** handled — try/except returns None; caller fails-closed unless override.
- **robots denies everything for a source without override:** source effectively removed; owner decides override or drop.
- **Zero-result scan after unpause:** separate follow-up issue; minimum-result alarm out of scope.

---

## Risks and Open Questions

### Resolved in v3 (design-decisions; implementation prescribed in §Files to Change)
- **Q9 (dead sources):** decision REMOVE. Implementation prescribed in §Files to Change (scanner.py still carries all 6 sources at plan-commit time; no removals yet landed).
- **Q10 (approver):** owner-only. Dual-path language removed from this plan.
- **Q11 (LinkedIn):** KEEP + robots-conflict reconciled via owner-override mechanism with API/RSS as deferred. The override mechanism itself (`_OWNER_OVERRIDE_SOURCES`, `_parse_owner_overrides_from_tos_review()`, `TOS_REVIEW.md` block parser) is **prescribed** — none of it exists in scanner.py today.

### Residual open questions
- **R1 (LinkedIn override wording):** owner may adjust the legal-acceptance language. Decided at U2.
- **R2 (C&D SLA):** "24h via PR" may be tightened/loosened by owner at U4.
- **R3 (LinkedIn API follow-up):** if override becomes untenable, does a separate issue track API procurement? Not opened automatically in v3.

### Known risks
- **Risk: robots check adds ~N network calls per scan.** Mitigation: per-domain caching.
- **Risk: `TOS_REVIEW.md` is a compliance record, not a legal opinion.** Mitigation: owner sign-off is explicit; plain legal-acceptance language in override.
- **Risk: fail-closed may produce near-empty scans.** Mitigation: U5 dry-run surfaces this; owner-override is the escape hatch with signed acknowledgment.
- **Risk: C&D never arrives but scraping continues.** Mitigation: residual risk acknowledged in writing by owner.
- **NEW v3 risk: robots.txt deny for LinkedIn conflicts with owner's KEEP directive (Q11).** Mitigation: doc-driven owner-override with plain-English acceptance; revocable via single PR removing the block; API/RSS documented for future migration. Owner-override is the canonical reconciliation; API escalation is a follow-up decision, not gating for v3.
- **NEW v3 risk: owner-override mechanism could be mis-used (e.g., copied to other sources without scrutiny).** Mitigation: per-source, explicit block in `TOS_REVIEW.md` with date + owner name; test asserts override set matches doc; removing block revokes override.

### Decided (not open)
- #1708 and #1709 CLOSED. Not reopened.
- Scanner not rewritten around official APIs for v3 (Indeed Publisher deprecated 2023; LinkedIn paywalled; Google Jobs API deprecated). LinkedIn API remains a deferred Q11 option.
- robots-unreachable → DENY (fail-closed).
- Dead sources removed in v3 (Q9); not revisited absent owner sign-off.
- Owner is sole approver (Q10); no counsel hedge.
- LinkedIn retained (Q11); robots conflict reconciled via owner override.

### Not applicable
- v1 "memory correction for Mon-Fri cadence" was a misread — `project_nightly_researchers.md` is about GSD researchers, not the GTM scanner.

---

## Adversarial Review Plan (Round 2)

Dispatch after v3 commit lands:
- **Claude** (`/code-review`) — focus on: (a) owner-override mechanism defensibility (doc-parsed vs flag); (b) state machine post-Q9; (c) fail-closed + override interaction.
- **Codex** (push plan, then dispatch) — focus on: (a) owner-only sign-off sufficiency given Q11 LinkedIn retention; (b) override-parser-from-doc audit gaps.
- **(Optional) Gemini** — cross-provider redundancy on Q11 LinkedIn-keep-despite-robots reasoning.

Specific stress tests:
- Is the owner-override genuinely revocable in a single PR, or does caching/runtime state break that property?
- Does the `Owner approved: <date>` line meet the governance bar given it's a git commit, not a signed document?
- Is "24h via PR" on C&D the right SLA?
- Does Q9 deletion introduce test-fixture coupling (e.g., `example-board`) needing follow-up?

---

## Complexity: T2

Single code file (`job-market-scanner.py`), three new test files, one new doc, one README update, one cron toggle (Commit 3). No new dependency (`urllib.robotparser` is stdlib). Q9 removal is bounded. Sign-off governance (Q10) + owner-override (Q11) are what make this T2 rather than T1.
