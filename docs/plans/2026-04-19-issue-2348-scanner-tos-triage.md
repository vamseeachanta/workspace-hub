# Plan for #2348: Scanner ToS / Rate-Limit / Dedup / Retention Triage

> **Status:** draft (2026-04-17) — plan-drafting only; no implementation; no adversarial review dispatched yet
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2348
> **Triaged issues:** #1707 (fix, partial — robots.txt + ToS audit still open), #1708 (verify-and-close), #1709 (verify-and-close)
> **Complexity:** T2 — one real code change (robots.txt + ToS audit gate in the scanner) + two "verify and close" triage decisions
> **Author:** Claude Code (plan-drafting agent for agent team task #14)

---

## Resource Intelligence Summary

### What the parent issue shipped
- `#1671` (closed 2026-04-05) — shipped the GTM job-market scanner at `scripts/gtm/job-market-scanner.py` (1360 lines).
- Actual cron schedule (verified by file read, not memory):
  - `config/scheduled-tasks/schedule-tasks.yaml` line 411 — `id: gtm-job-market-scan`, schedule `0 5 * * 1` (Monday 5AM UTC, **weekly**, not daily Mon-Fri).
  - Wrapper: `scripts/gtm/weekly-scan-refresh.sh` (100 lines) — `git pull`, run scanner, auto-commit, auto-push to `main`.
  - Last successful run: `dashboard.md` header shows `Auto-generated: 2026-04-13`. Most recent weekly scan is on cadence.
- **Correction to memory:** `project_nightly_researchers.md` says "LIVE, rotating Mon-Fri" — incorrect for this specific job. GTM scanner is **Monday-only weekly**. Flag for memory correction at close time.

### What the three follow-up issues actually asked for
Source: `scripts/review/results/2026-04-02T132222Z-retroactive-review-codex.md` — Codex retroactive review of the #1671 deliverable identified six defects (G1-G6); three were promoted into issues:

| Issue | Severity | Codex defect | Acceptance criteria (verbatim from issue body) |
|---|---|---|---|
| #1707 | HIGH (G1) | No credible rate-limit or ToS compliance | (1) per-site rate limit config, (2) robots.txt check before scraping new domains, (3) Retry-After respected, (4) exponential backoff on 429/503, (5) source allowlist with documented ToS compliance, (6) consider official APIs where available |
| #1708 | HIGH (G2) | Deduplication too weak | (1) dedup key includes source URL or requisition ID, (2) posting date included, (3) source board included, (4) tests cover dedup edge cases |
| #1709 | MEDIUM (G4) | Unbounded `cumulative-index.json` growth | (1) keep raw results 12 weeks max, (2) archive entries older than N months, (3) move historical results to gitignored archive, (4) document retention policy |

### What actually got committed after the issues were filed
Git log on `scripts/gtm/` and `docs/strategy/gtm/job-market-scan/`:

| Commit | Scope | Issues tagged |
|---|---|---|
| `70c3975b2` (2026-04-02 21:01) | `fix(gtm): harden dedup keys and request compliance` | #1708, #1707 |
| `d0840bd42` (2026-04-02 21:15) | `feat(config): add shared user profile and GTM retention policy` | #1709 |
| `7664453e8` (later) | `feat(gtm): full scan restored (708 jobs/460 companies) + email templates` | #1671, #1669 |
| `009f44947` (most recent) | `chore(gtm): weekly job market scan refresh 2026-04-13` | — |

**All three follow-up issues have landed code fixes but none of the three issues were ever closed.** They remained stuck in `review-backlog`. That is what #2348 is flagging.

### Evidence of what's actually in the scanner right now (file-verified)

| Acceptance criterion | File + lines | Implemented? |
|---|---|---|
| #1708 — dedup key includes `source`, `url`, `posted_date` | `scripts/gtm/job-market-scanner.py` lines 225-242 (`job_id()`) | **YES** — `raw = title|company|location|source|url|posted_date` |
| #1708 — legacy key migration | lines 219-222 (`legacy_job_id()`) + lines 1042-1047 (migration in `update_cumulative_index`) | **YES** |
| #1708 — tests cover dedup edge cases | `tests/gtm/test_job_market_scanner.py` (186 lines added in `70c3975b2`) | **YES** |
| #1707 — per-site rate limit config | lines 143-153 (`SOURCE_RATE_LIMITS`) — google 3s, indeed 4s, linkedin 4s, rigzone 4s | **YES** |
| #1707 — Retry-After respected | lines 197-206 (parses `Retry-After` header, takes `max(backoff, retry_after)`) | **YES** |
| #1707 — exponential backoff on 429/503 | lines 198-207 (`delay * (2 ** attempt)`) | **YES** |
| #1707 — source allowlist | lines 154-163 (`SOURCE_ALLOWLIST`, `SOURCE_ALLOWED_DOMAINS`) + line 180 guard | **YES** |
| #1707 — **robots.txt check before scraping new domains** | `grep -n "robots\.txt\|robotparser" scripts/gtm/job-market-scanner.py` → **zero matches** | **NO — GAP** |
| #1707 — documented ToS compliance | `SOURCE_ALLOWLIST` exists but **no accompanying doc** lists the ToS review for google.com, indeed.com, linkedin.com, rigzone.com | **NO — GAP** |
| #1707 — consider official APIs where available | No comment or ADR in repo discussing Indeed Publisher API, LinkedIn Talent Solutions API, or Rigzone data access | **NO — GAP** |
| #1709 — 12-week raw retention | lines 55 (`RAW_RETENTION_WEEKS = 12`), 971-989 (`enforce_retention_policy()` archives older) | **YES** |
| #1709 — 6-month history retention | lines 56 + 991-1004 (prunes `scan_history` and `company_history` older than 180 days) | **YES** |
| #1709 — gitignored archive dir | `.gitignore` line 169 — `/docs/strategy/gtm/job-market-scan/archive/` | **YES** |
| #1709 — policy documented | `docs/strategy/gtm/job-market-scan/RETENTION_POLICY.md` (24 lines, references #1709 explicitly) | **YES** |
| #1709 — tests | `tests/gtm/test_job_market_retention.py` (62 lines) | **YES** |

### The legal/ToS dimension
The four scraped sources are Google Search, Indeed, LinkedIn, and Rigzone. All four have terms of service that explicitly prohibit automated scraping (LinkedIn in particular — LinkedIn v. hiQ Labs went to the Supreme Court; the post-remand ruling (2022) narrowed hiQ's win and LinkedIn continues to pursue scrapers under CFAA and ToS). Indeed and Google have similar ToS. Rigzone's ToS is less well-publicized but also prohibits scraping.

The current scanner:
- Uses a forged browser User-Agent (line 132-135) to evade automation detection
- Has no robots.txt check
- Has no affirmative record of ToS review
- Auto-commits scraped data to a **public** GitHub repo (`vamseeachanta/workspace-hub`) via `weekly-scan-refresh.sh` line 95 (`git push origin main`)

The combination of (a) forged UA, (b) no robots.txt, (c) auto-publish of scraped output to a public repo is the legal exposure #2348 is asking us to address. This is not a code style defect — it is a compliance gap.

### Parallel work / worktrees
- `git worktree list` shows **no worktree for #2348, #1707, #1708, or #1709**. Safe to proceed.
- No existing plan for any of these four issues in `docs/plans/`.

### Sources consulted
12 distinct sources: issue bodies (#2348, #1671, #1707, #1708, #1709), scanner source (`scripts/gtm/job-market-scanner.py`), cron wrapper (`scripts/gtm/weekly-scan-refresh.sh`), cron config (`config/scheduled-tasks/schedule-tasks.yaml`), retention doc (`RETENTION_POLICY.md`), `.gitignore`, review artifact (`scripts/review/results/2026-04-02T132222Z-retroactive-review-codex.md`), git log on `scripts/gtm/`, `docs/plans/` index, memory (`project_nightly_researchers.md`), worktree list. Exceeds minimum 3.

---

## Triage Decisions

### #1707 — Rate limiting and ToS compliance
**Decision: FIX (partial — scope narrowed to remaining gaps)**

Four of the six acceptance criteria are already met. Remaining work:
1. Add `urllib.robotparser.RobotFileParser` check in `safe_request()` before first fetch per domain; cache per-domain allow/deny; skip fetch (with `[WARN] robots.txt disallows <path>`) on disallow.
2. Add `docs/strategy/gtm/job-market-scan/TOS_REVIEW.md` documenting the explicit ToS status of google.com, indeed.com, linkedin.com, rigzone.com + a decision per source: keep / replace-with-api / remove. Reference the `SOURCE_ALLOWLIST` from this doc so allowlist changes stay in sync.
3. ADR (section in `TOS_REVIEW.md`): explicit statement of whether to pursue official APIs (Indeed Publisher Program was deprecated 2023; LinkedIn Talent Solutions is paid enterprise only; Google doesn't offer a jobs API post-Google Jobs deprecation 2023). Expected outcome: document that official APIs are NOT viable at current scale and record the residual risk.

**Remove `review-backlog`; add `priority:high`, `status:plan-review` → eventually `status:plan-approved` → `status:in-progress`; owner `vamseeachanta`.**

### #1708 — Deduplication key improvement
**Decision: CLOSE AS COMPLETE**

All four acceptance criteria met in `70c3975b2`:
- Dedup key now includes `source`, `url`, `posted_date` (lines 232-241)
- Legacy key migration path (lines 219-222, 1042-1047)
- Tests at `tests/gtm/test_job_market_scanner.py` (186 lines)
- Cumulative index uses new key

Action: post closure comment citing `70c3975b2`, remove `review-backlog`, close with `status:done`. No implementation required.

### #1709 — Data retention policy
**Decision: CLOSE AS COMPLETE**

All four acceptance criteria met in `d0840bd42`:
- 12-week raw retention enforced (lines 55, 974, 981-989)
- 6-month history retention enforced (lines 56, 975, 991-1004)
- Archive directory gitignored (`.gitignore` line 169)
- Policy documented (`RETENTION_POLICY.md` explicitly references #1709)
- Tests at `tests/gtm/test_job_market_retention.py` (62 lines)

Action: post closure comment citing `d0840bd42`, remove `review-backlog`, close with `status:done`. No implementation required.

---

## Should the Cron Be Paused While This Plan Awaits Approval?

**Recommendation: YES — pause the cron while #1707 remainder is being fixed.**

Rationale:
- The **legal** exposure (scraping LinkedIn/Indeed/Google without robots.txt respect + auto-publishing the results) is ongoing every Monday at 5AM UTC.
- The cron auto-commits scraped output to a **public** repo. Public output of possibly-ToS-violating scrapes is materially worse than local-only scraping — it is durable and discoverable.
- Pausing for 1-2 weeks (plan approval + implementation + review) costs one skipped scan. That is acceptable against the legal tail risk.
- Pausing is cheap to implement: comment out the `gtm-job-market-scan` entry in `config/scheduled-tasks/schedule-tasks.yaml` and add a note — reversible in one commit.

**This is ultimately a user risk call.** The plan surfaces it; the user decides. If the user chooses not to pause, the plan still proceeds, but the #1707 fix should then be prioritized to land within one week.

**Pause action (if user approves):** add a preceding Commit 0 to this plan's implementation — comment out the `gtm-job-market-scan` entry in `schedule-tasks.yaml` and commit as `chore(gtm): pause job-market-scan cron pending #1707 ToS review`. Reverse as final Commit 3 after all other work lands.

---

## Pseudocode (#1707 implementation scope only)

### A. robots.txt respect in `safe_request()`
```python
# module-level cache
_ROBOTS_CACHE: dict[str, urllib.robotparser.RobotFileParser] = {}

def _get_robots_parser(netloc: str) -> urllib.robotparser.RobotFileParser:
    if netloc in _ROBOTS_CACHE:
        return _ROBOTS_CACHE[netloc]
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(f"https://{netloc}/robots.txt")
    try:
        rp.read()  # network fetch; tolerate failure
    except Exception as e:
        print(f"  [WARN] robots.txt unreachable for {netloc}: {e}; defaulting to ALLOW")
    _ROBOTS_CACHE[netloc] = rp
    return rp

# inside safe_request(), AFTER allowlist check, BEFORE time.sleep(delay):
rp = _get_robots_parser(parsed.netloc)
if not rp.can_fetch(USER_AGENT, url):
    print(f"  [WARN] robots.txt disallows {url}; skipping")
    return None
```

### B. TOS_REVIEW.md structure (new file, ~80 lines)
```
# ToS Review for GTM Job Market Scanner Sources

## Summary
Four sources allowlisted. This document records the ToS position for each,
the compliance mechanisms in place, and the residual risk.

## Per-source review

### google.com (Google Search / Google Jobs)
- ToS: https://policies.google.com/terms — prohibits "access, use, or interfere
  with automated means"
- Current treatment: rate-limited 3s, forged UA, robots.txt honored (post-#1707 fix)
- Official API: Google Jobs API was deprecated 2023; no replacement
- Decision: KEEP with documented residual risk; revisit if Google enforces

### indeed.com
- ToS: https://www.indeed.com/legal — prohibits scraping
- Current treatment: rate-limited 4s, robots.txt honored
- Official API: Indeed Publisher Program deprecated 2023
- Decision: KEEP with documented residual risk

### linkedin.com
- ToS: https://www.linkedin.com/legal/user-agreement — prohibits scraping;
  history of enforcement (hiQ remand 2022)
- Current treatment: rate-limited 4s, robots.txt honored
- Official API: LinkedIn Talent Solutions (paid enterprise only)
- Decision: ELEVATED RISK. Consider removing or replacing with a lawful
  alternative (e.g., LinkedIn job-alert email subscriptions with manual export)

### rigzone.com
- ToS: https://www.rigzone.com/info/terms.asp — prohibits automated access
- Current treatment: rate-limited 4s, robots.txt honored
- Official API: none public
- Decision: KEEP with documented residual risk

## Mitigations in force
- Per-source rate limits (SOURCE_RATE_LIMITS)
- Source allowlist (SOURCE_ALLOWLIST)
- robots.txt enforcement (post-#1707)
- Retry-After honored, exponential backoff
- Output auto-committed to public repo — flagged as RISK MULTIPLIER

## Residual risk acknowledgement
Scraping + public auto-publish remains technically out-of-policy for all
four sources. This is accepted as a cost of the current GTM approach. Any
cease-and-desist email from any listed source terminates use of that source
immediately and triggers an allowlist removal PR within 24 hours.
```

### C. (Optional, deferred) Remove LinkedIn from allowlist
Not in this plan's scope — flagged as a follow-up issue "evaluate removing LinkedIn source from GTM scanner given elevated enforcement risk." Current plan is a documentation + robots.txt fix; source removal is a policy call separate from defect closure.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify (optional preceding Commit 0) | `config/scheduled-tasks/schedule-tasks.yaml` | Comment out `gtm-job-market-scan` task with note; only if user accepts cron pause |
| Modify | `scripts/gtm/job-market-scanner.py` | Add `urllib.robotparser` import; add `_ROBOTS_CACHE` + `_get_robots_parser`; insert `rp.can_fetch()` check in `safe_request()` between allowlist check and rate-limit sleep |
| Create | `docs/strategy/gtm/job-market-scan/TOS_REVIEW.md` | Per-source ToS review + residual-risk acknowledgement + cease-and-desist runbook |
| Modify | `docs/strategy/gtm/job-market-scan/README.md` | Link from overview to `TOS_REVIEW.md` |
| Create | `tests/gtm/test_robots_respect.py` | Test `_get_robots_parser` caching + `can_fetch` denial path |
| Modify (final Commit 3, if Commit 0 was taken) | `config/scheduled-tasks/schedule-tasks.yaml` | Un-comment `gtm-job-market-scan`; cron resumes |
| Update | `docs/plans/README.md` | Register this plan |

**Not modified:**
- `cumulative-index.json`, `dashboard.md`, etc. — scanner outputs; untouched.
- `weekly-scan-refresh.sh` — unchanged; pause/unpause happens at the cron config, not the wrapper.

---

## TDD Test List

All tests new; no existing tests break.

| Test | Tool | Claim | Pass criterion |
|---|---|---|---|
| test_robots_parser_cached | pytest + mock | `_get_robots_parser("www.indeed.com")` called twice reads `/robots.txt` once | network mock called == 1 |
| test_robots_disallow_blocks_fetch | pytest + mock | If `RobotFileParser.can_fetch` returns False, `safe_request` returns None and never calls `requests.get` | `requests.get` not called |
| test_robots_unreachable_defaults_allow | pytest + mock | If `rp.read()` raises, `can_fetch` defaults True, fetch proceeds | `requests.get` called once |
| test_tos_review_doc_exists | pytest | `docs/strategy/gtm/job-market-scan/TOS_REVIEW.md` exists and mentions all four allowlisted sources | all 4 substrings present |
| test_readme_links_to_tos_review | pytest | `README.md` contains a relative link to `TOS_REVIEW.md` | link present |
| test_allowlist_matches_tos_review | pytest | Every source in `SOURCE_ALLOWLIST` has a section heading in `TOS_REVIEW.md` | set equality |
| (verification) retention policy tests still pass | pytest | `tests/gtm/test_job_market_retention.py` unchanged, still green | 62 lines, all pass |
| (verification) dedup tests still pass | pytest | `tests/gtm/test_job_market_scanner.py` unchanged, still green | all pass |

Test-writing order: robots tests first (drive the code change), then doc/allowlist sync tests, then verification of untouched tests.

---

## Acceptance Criteria

### For this plan (#2348)
- [ ] `#1708` closed with comment citing commit `70c3975b2`; `review-backlog` removed
- [ ] `#1709` closed with comment citing commit `d0840bd42`; `review-backlog` removed
- [ ] `#1707` retains `review-backlog` label replaced with `priority:high` + `status:in-progress`; owner `vamseeachanta`
- [ ] (if user approves) Cron paused via Commit 0; un-paused via Commit 3 after Commit 2 lands
- [ ] Plan file committed at `docs/plans/2026-04-19-issue-2348-scanner-tos-triage.md`
- [ ] Index row added to `docs/plans/README.md`
- [ ] Memory correction filed: `project_nightly_researchers.md` says "Mon-Fri" but GTM scanner is weekly Monday — log as a follow-up

### For #1707 residual fix (the real code work in this plan)
- [ ] `_get_robots_parser` + per-domain cache implemented in `job-market-scanner.py`
- [ ] `safe_request()` calls `rp.can_fetch()` and skips disallowed URLs with a `[WARN]` log
- [ ] robots.txt fetch failures default to ALLOW with `[WARN]` (don't hard-fail the scan)
- [ ] `TOS_REVIEW.md` created, listing all four sources with ToS URL + decision + residual risk + C&D runbook
- [ ] `README.md` links to `TOS_REVIEW.md`
- [ ] New tests `tests/gtm/test_robots_respect.py` pass
- [ ] Existing tests `tests/gtm/test_job_market_scanner.py` + `tests/gtm/test_job_market_retention.py` still pass
- [ ] After merge: one scan cycle runs successfully with robots.txt enforcement active; dashboard generated; no empty-scrape failures
- [ ] #1707 closed with comment citing new commit + `TOS_REVIEW.md`

---

## Rollback Plan

Three-commit structure (Commit 0 is conditional on user approval):

**Commit 0 (optional) — pause cron**
- Scope: `config/scheduled-tasks/schedule-tasks.yaml` only. Comment out the `gtm-job-market-scan` task with a note referencing this plan and #1707.
- Rollback: `git revert <commit0-sha>` restores the weekly Monday schedule.

**Commit 1 — `TOS_REVIEW.md` + README link (docs only)**
- Scope: `docs/strategy/gtm/job-market-scan/TOS_REVIEW.md` (new), `README.md` (link added).
- Rollback: `git revert <commit1-sha>`. Zero runtime impact — docs only.
- Blast radius: none; purely additive.

**Commit 2 — robots.txt respect + tests (code change)**
- Scope: `scripts/gtm/job-market-scanner.py` + `tests/gtm/test_robots_respect.py`.
- Rollback: `git revert <commit2-sha>`. Scanner reverts to pre-#1707-final behavior (rate-limited but no robots.txt check).
- Blast radius: scanner-only. No change to dashboards, cumulative index, or retention.

**Commit 3 (conditional, required if Commit 0 was taken) — resume cron**
- Scope: `schedule-tasks.yaml`, un-comment the task.
- Rollback: `git revert <commit3-sha>` re-pauses.

Failure modes:
- **Scanner crashes on `rp.read()` for a new domain:** already handled — `try/except` defaults to ALLOW with `[WARN]`.
- **robots.txt is too permissive (explicit ALLOW) and scan still violates ToS in spirit:** `TOS_REVIEW.md` is the compensating control; residual risk is explicitly accepted. If cease-and-desist received, remove that source from `SOURCE_ALLOWLIST` within 24h per the runbook.
- **Weekly scan produces zero results because robots.txt denies everything:** flag as a separate triage issue; do NOT silently accept zero-result scans. The scanner's existing empty-result path (`git diff --staged --quiet` → "No changes to commit") is safe; just visibly weird. Follow-up: add a minimum-result alarm.

---

## Risks and Open Questions

### Open questions for user
- **Q1 (load-bearing): Pause the cron while #1707 lands?** Recommendation: YES. User decides at plan-approval time. This plan is written to work either way.
- **Q2: Should LinkedIn be removed from `SOURCE_ALLOWLIST` given elevated enforcement risk?** Out of scope for this plan; filed as a follow-up if the user wants to take the conservative path.
- **Q3: Is anyone actually reading the weekly scan output?** If the business value is low, the cheapest ToS fix is to turn the scanner off. Not this plan's call, but worth raising.

### Known risks
- **Risk: robots.txt check adds ~N network calls per scan (one per new domain).** Mitigation: per-domain caching; ~4 domains total.
- **Risk: ToS review is inherently a legal-judgment call; the agent is not a lawyer.** Mitigation: `TOS_REVIEW.md` records facts + decisions, not legal opinions. User/counsel can revise post-hoc.
- **Risk: residual-risk acknowledgement is not a legal shield.** Noted. The compensating control is speed-of-response (24h removal on C&D), not pre-emptive immunity.
- **Risk: cron pause forgotten if Commit 3 skipped.** Mitigation: Commit 3 is a required acceptance criterion IF Commit 0 was taken. Tracked as an explicit acceptance item.

### Decided (not open)
- **Dedup (#1708) and retention (#1709) are already done.** Plan does not reopen these decisions.
- **Scanner will not be rewritten around official APIs.** Indeed/Google deprecated their APIs; LinkedIn's is paywalled. Plan does not pursue this path.

---

## Adversarial Review Plan

Dispatch **after** user provides initial comment on this draft (per `feedback_cross_provider_review_payoff.md`):
- Claude (self-review via `/code-review` skill)
- Codex (push plan to GitHub, then dispatch — Codex sandbox cannot read local-only files per `feedback_codex_needs_pushed_artifact.md`)
- Gemini (via `superpowers:requesting-code-review`)

Expected defect classes to stress-test:
- Does robots.txt caching survive a multi-process scan run? (currently only single-process)
- Is "default ALLOW on robots unreachable" the right choice, or should it be "default DENY"?
- Is `TOS_REVIEW.md` the right place for a cease-and-desist runbook, or should that live in `docs/legal/`?
- Does the cron-pause recommendation inadvertently leak scraping activity (via the commit message) to anyone watching the public repo?

---

## Complexity: T2

Single code file modified, two new tests, one new doc. No architecture change, no new dependency (`urllib.robotparser` is stdlib). The triage-vs-fix split across three issues is what makes this T2 instead of T1 — the plan is doing three things at once, only one of which is code.
