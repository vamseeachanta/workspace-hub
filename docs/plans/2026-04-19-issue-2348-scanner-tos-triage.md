# Plan for #2348: Scanner ToS / Robots / Unpause Governance

> **Status:** draft v2 (2026-04-17) — revised after round-1 adversarial review; not yet re-dispatched; awaiting round-2 review
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2348
> **In-scope issue:** #1707 (OPEN — robots.txt + documented ToS review + unpause governance)
> **Out of scope (already closed 2026-04-20):** #1708 (closed, `70c3975b2`), #1709 (closed, `d0840bd42`)
> **Complexity:** T2 — one code change (robots.txt in `safe_request()`) + compliance docs + explicit unpause checklist gated on non-engineer sign-off
> **Author:** Claude Code

---

## Revision History

| Version | Date | Change |
|---|---|---|
| v1 | 2026-04-17 | Initial draft — 3-issue triage (#1707 fix + #1708/#1709 close-with-comment) + cron-pause flag |
| v2 | 2026-04-17 | Post-review refresh: (a) remove #1708/#1709 close actions — they closed during round-1 review cycle; (b) reconcile sources to live reality (`linkedin/indeed/career_page` only — Google and Rigzone NOT in live run); (c) add non-engineer approver to sign-off chain; (d) replace unpause "recommendation" with explicit checklist; (e) flip robots-unreachable default ALLOW → DENY (fail-closed); (f) mark cease-and-desist runbook as requiring counsel input or explicit deferral with owner sign-off; (g) add README + operator-doc updates as Commit-2 hard requirement; (h) rewrite rollback as explicit state machine given cron is already paused; (i) drop the spurious memory-correction item (the "Mon-Fri" memory entry is about GSD nightly researchers, not the GTM scanner — no conflict once re-read) |

---

## Adversarial Review Summary (Round 1, 2026-04-17)

| Reviewer | Verdict | BLOCKER/HIGH findings | Addressed in v2 |
|---|---|---|---|
| Claude (Opus 4.7) | REQUEST-CHANGES | F1 stale #1708/#1709 close actions; F2 LinkedIn elevated-risk deferred; F3 robots-unreachable default wrong; F4 C&D runbook beyond agent authority; F5 rollback state machine ambiguous; F6 memory correction deferred | F1 removed; F3 flipped to DENY; F4 reframed as counsel-dependent or deferred-with-sign-off; F5 rewritten as state machine; F6 re-examined — determined not applicable (memory was about a different job). F2 LinkedIn remains deferred to the non-engineer approver's decision at sign-off (documented explicitly) |
| Codex (GPT-5.4) | MAJOR-REVISION | M1 engineer-authored legal compliance; M2 resume gate too soft; M3 plan stale post-close; m1 review scope mismatch vs live sources; m2 README/operator docs not mandatory before unpause | M1 non-engineer approver added to sign-off chain; M2 resume gate replaced with concrete checklist; M3 de-scoped #1708/#1709; m1 live-source table rewritten against dashboard reality; m2 README/ops doc update now Commit-2 hard requirement |

Round 2 dispatch: after user sign-off on the v2 revision. Do NOT advance to `status:plan-approved` until the live-source scope call and the non-engineer approver identity are confirmed by the user.

---

## Resource Intelligence Summary

### What the parent issue shipped
- `#1671` (closed 2026-04-05) — shipped GTM job-market scanner at `scripts/gtm/job-market-scanner.py` (~1360 lines).
- Cron schedule: `config/scheduled-tasks/schedule-tasks.yaml` line 411 region — `id: gtm-job-market-scan`, schedule `0 5 * * 1` (Monday 5AM UTC, weekly).
- Wrapper: `scripts/gtm/weekly-scan-refresh.sh` — `git pull`, run scanner, auto-commit, auto-push to `main` (public repo).
- **Current state (verified 2026-04-17):** cron is PAUSED via commit `a9a2a922b` (`chore(cron): PAUSE gtm-job-market-scan — #2348 legal exposure`). `schedule-tasks.yaml` region for `gtm-job-market-scan` is fully commented out.

### Live sources (ground truth — NOT plan v1's assumption)
**Plan v1 reasoned about Google, Indeed, LinkedIn, Rigzone.** The most recent actual scan output (`docs/strategy/gtm/job-market-scan/dashboard.md`, auto-generated 2026-04-13) shows:

| Source | Live? | Count last scan |
|---|---|---|
| `linkedin` | YES | 584 |
| `indeed` | YES | 112 |
| `career_page` (company career pages) | YES | 42 |
| `google` | NO | 0 — not in dashboard output |
| `google_direct` | NO | 0 — not in dashboard output |
| `rigzone` | NO | 0 — not in dashboard output |

The scanner code (`SOURCE_ALLOWLIST` at line 154) still allowlists all six (`google`, `google_direct`, `indeed`, `linkedin`, `rigzone`, `career_page`, `example-board`), but in the real weekly run Google and Rigzone are returning zero results (likely anti-bot block against the forged UA). **The live legal exposure is LinkedIn, Indeed, and individual company career pages.** Google and Rigzone are allowlisted-but-dead; they can be either (a) removed from `SOURCE_ALLOWLIST` to match reality, or (b) kept as dead code with a note. Decision goes to the non-engineer approver.

### #1707 acceptance criteria status (file-verified)

| Criterion | File + lines | Status |
|---|---|---|
| Per-site rate limit config | `job-market-scanner.py:145-153` (`SOURCE_RATE_LIMITS`) | DONE |
| Retry-After respected | `job-market-scanner.py:197-206` | DONE |
| Exponential backoff on 429/503 | `job-market-scanner.py:198-207` | DONE |
| Source allowlist | `job-market-scanner.py:154-163` (`SOURCE_ALLOWLIST`, `SOURCE_ALLOWED_DOMAINS`) | DONE |
| robots.txt check before scraping | grep `robotparser` on scanner → 0 matches | **GAP** |
| Documented ToS compliance per source | No `TOS_REVIEW.md`; no ADR | **GAP** |
| Consider official APIs | No comment/ADR in repo | **GAP** (covered in `TOS_REVIEW.md` body) |

### The legal/ToS dimension
The actually-live sources (LinkedIn, Indeed, career pages) all have terms of service that address automated access. LinkedIn in particular has a known enforcement posture (hiQ remand 2022, active CFAA theories against scrapers). The current scanner:
- Uses a forged Chrome desktop User-Agent (line 132-135)
- Has no robots.txt check
- Has no affirmative ToS review on record
- Auto-commits scraped output to a **public** repo — `vamseeachanta/workspace-hub` (visibility PUBLIC, confirmed)

**This is a compliance gap, not a code-style defect.** It is also — critically — not an engineer's call to close unilaterally. See §Legal Authority below.

### Parallel work / worktrees
- `git worktree list` — no worktree for #1707 or #2348. Safe to proceed.
- No existing plan for #1707 in `docs/plans/`.

### Sources consulted
Issue bodies (#2348, #1707), scanner source, cron wrapper, cron config, dashboard.md (2026-04-13), README.md, `.gitignore`, round-1 Claude review (`scripts/review/results/2026-04-19-plan-2348-claude.md`), Codex round-1 review (per task prompt — artifact path absent on disk; relying on prompt-conveyed findings), git log on `config/scheduled-tasks/schedule-tasks.yaml`, `gh issue view 1707 1708 1709` (state verification), `docs/plans/README.md` index. ≥12 sources.

---

## Legal Authority (NEW in v2 — addresses Codex MAJOR 1)

Per Codex round-1 finding: an engineer-authored plan cannot be the source of legal safety for a scraping program. The following roles/approvals are required for any "keep scraping source X" decision:

| Role | Responsibility | This plan's treatment |
|---|---|---|
| Engineer (this plan's author) | Observe, document, implement mitigations | Drafts `TOS_REVIEW.md` as *observations*, not legal conclusions |
| Non-engineer approver | Decide keep/remove per source; sign off `TOS_REVIEW.md`; decide C&D response posture | Explicitly named in v2 sign-off chain |
| External counsel (optional, owner-directed) | Review `TOS_REVIEW.md` and C&D runbook | Optional but must be invited OR explicitly deferred by approver |

**Non-engineer approver (this repo's context):** the user (`vamseeachanta`) is the sole business owner. For this plan, "non-engineer approver" resolves to the user acting in business-owner capacity — not in engineer capacity. This plan's acceptance criteria require the user to sign off on `TOS_REVIEW.md` **as owner**, separate from approving the plan as technical reviewer. If the user chooses to engage external counsel, the plan accommodates that (criterion allows "approver signs off on deferral-to-counsel" as a valid path).

Rationale: the legal-safety artifact must come from an authority role, not from the engineering delivery role. This separation is what makes `TOS_REVIEW.md` a real compliance record rather than an author-defending-their-own-code document.

---

## Unpause Checklist (NEW in v2 — replaces v1's soft "recommendation")

The cron is already paused (`a9a2a922b`). Unpause requires **all** of the following, in order:

- [ ] **U1 — robots.txt parser wired into `safe_request()`:** `urllib.robotparser.RobotFileParser` call lives between allowlist check and rate-limit sleep. Unit tests prove skip-on-disallow and fail-closed on unreachable. Each live source (`linkedin`, `indeed`, plus every URL in `COMPANY_CAREER_URLS`) either passes the check OR is removed from the allowlist/career-page dict by Commit 2.
- [ ] **U2 — `TOS_REVIEW.md` committed and signed off by non-engineer approver.** Each live source has a row: ToS URL, observed robots.txt disposition, keep/remove decision, signed by approver (commit trailer `Signed-off-by: Vamsee Achanta <...>` acting as owner, OR approver-named comment on PR).
- [ ] **U3 — `docs/strategy/gtm/job-market-scan/README.md` updated** to reflect: robots.txt enforcement is active; any sources removed; pointer to `TOS_REVIEW.md`; statement that `auto-commits results to main` remains true but "only for sources whose ToS review signed off on public publication".
- [ ] **U4 — Cease-and-desist runbook committed.** EITHER authored with counsel input (approver confirms) OR explicitly deferred to external legal response (approver-signed note in `TOS_REVIEW.md` — "on receipt of any legal notice, this plan's operational action is: remove the source from the allowlist within 24h via PR; legal response is routed to counsel, not to this repo").
- [ ] **U5 — Dry-run cycle succeeds on manual trigger** (`python scripts/gtm/job-market-scanner.py --limit 2 --skip-career-pages` then a full run) without policy violations — no disallowed fetches, no zero-result full-block. If dry-run is degenerate (e.g., every source blocks), unpause is deferred pending re-scoping.

All five are required. If any fails, the resting state is **paused**. Unpause is a separate commit after all five are green.

---

## Triage Decision — #1707 only

**Decision: FIX (robots.txt + documented ToS review + unpause governance)**

#1708 and #1709 are out of scope — both closed `2026-04-20T03:17Z` during this session's review cycle.

Remaining work on #1707:
1. `urllib.robotparser.RobotFileParser` in `safe_request()`; cache per-domain; skip on disallow; **fail-closed on fetch error** (v2 change from v1's fail-open).
2. `docs/strategy/gtm/job-market-scan/TOS_REVIEW.md` — per-source facts + observed robots disposition + keep/remove *proposal* by engineer + signed decision by non-engineer approver + C&D runbook with counsel-or-deferral note.
3. README.md + dashboard-header updates — operator docs must reflect new state before cron resumes.

**Labels:** `review-backlog` replaced with `priority:high` + `status:plan-review` → (after user approves v2 + round-2 review) `status:plan-approved` → `status:in-progress`. Owner: `vamseeachanta`.

---

## Pseudocode

### A. robots.txt respect in `safe_request()` — fail-closed on unreachable

```python
# module-level cache
_ROBOTS_CACHE: dict[str, urllib.robotparser.RobotFileParser | None] = {}

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
    print(f"  [WARN] robots.txt unreachable; skipping {url} (fail-closed)")
    return None
if not rp.can_fetch(USER_AGENT, url):
    print(f"  [WARN] robots.txt disallows {url}; skipping")
    return None
```

Rationale for fail-closed: the scanner uses a forged Chrome UA. Sites that detect the bot and deny robots.txt specifically are the exact case where fail-open breaks compliance posture. Fail-closed turns "cannot verify permission" into "do not fetch" — matches the compliance-first posture that drove the cron pause in the first place.

### B. `TOS_REVIEW.md` structure (new file)

- Header: what this doc is; who signed off; date.
- Per-source section for each currently-live source (at time of writing: `linkedin`, `indeed`, `career_page`; others as approver decides).
- Each section: ToS URL, observed robots.txt disposition, engineer-proposed decision (keep / remove / restrict), **approver's signed decision**, residual risk acknowledgement.
- Mitigations in force (rate limits, allowlist, robots.txt enforcement, retry/backoff).
- C&D runbook: operational step only ("remove source from `SOURCE_ALLOWLIST` within 24h via PR") separated from legal response ("route to counsel; this runbook does not author legal responses"). Approver signs off on runbook or on deferral.

---

## Files to Change

| Action | Path | Reason | Commit |
|---|---|---|---|
| Modify | `scripts/gtm/job-market-scanner.py` | Add `urllib.robotparser` import; `_ROBOTS_CACHE`; `_get_robots_parser`; fail-closed check inside `safe_request()` between allowlist and rate-limit sleep | 2 |
| Create | `docs/strategy/gtm/job-market-scan/TOS_REVIEW.md` | Per-source review + approver sign-off + C&D runbook (operational; legal deferred) | 1 |
| Modify | `docs/strategy/gtm/job-market-scan/README.md` | Reflect new state: robots.txt enforcement, removed sources (if any), pointer to TOS_REVIEW.md; revise "auto-commits results to main" line to note the review gate | 2 |
| Modify | `docs/strategy/gtm/job-market-scan/dashboard.md` (header only, on next scan) | Will regenerate automatically on unpause scan; not edited by hand | auto (Commit 3 side-effect) |
| Create | `tests/gtm/test_robots_respect.py` | Test `_get_robots_parser` caching + disallow → None + unreachable → DENY | 2 |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | Un-comment `gtm-job-market-scan` — ONLY after U1-U5 green | 3 |
| Update | `docs/plans/README.md` | Plan index row updated to v2 | this commit |

**Not modified:** `cumulative-index.json`, scanner outputs (regenerated on next scan), `weekly-scan-refresh.sh` (unchanged — the gate is at cron config and inside `safe_request`).

---

## TDD Test List

| Test | Claim | Pass criterion |
|---|---|---|
| `test_robots_parser_cached` | `_get_robots_parser("www.linkedin.com")` called twice reads robots.txt once | mock network call count == 1 |
| `test_robots_disallow_blocks_fetch` | If `can_fetch` returns False, `safe_request` returns None; `requests.get` never called | requests.get not called |
| `test_robots_unreachable_fails_closed` | If `rp.read()` raises, `_get_robots_parser` returns None; `safe_request` returns None; `requests.get` never called | requests.get not called |
| `test_tos_review_doc_exists_and_covers_live_sources` | `TOS_REVIEW.md` exists; has a section for every source present in the most recent dashboard | set(dashboard sources) ⊆ set(doc sections) |
| `test_readme_references_tos_review` | README.md contains a relative link to `TOS_REVIEW.md` | link present |
| (verification) retention tests still pass | `tests/gtm/test_job_market_retention.py` unchanged | all pass |
| (verification) dedup tests still pass | `tests/gtm/test_job_market_scanner.py` unchanged | all pass |

Test-writing order: robots tests first (TDD drives the code), then doc/link tests, then verification of untouched tests.

---

## Acceptance Criteria

### For this plan (#2348)
- [ ] Plan v2 committed at `docs/plans/2026-04-19-issue-2348-scanner-tos-triage.md`
- [ ] Index row in `docs/plans/README.md` updated to `draft (v2)` with revised notes
- [ ] Round-2 adversarial review dispatched (Claude + Codex) and resolved before `status:plan-approved`
- [ ] User (as owner) sign-off recorded on the v2 scope, specifically: (a) live-source list for `TOS_REVIEW.md`, (b) engineer vs owner vs counsel responsibility split, (c) unpause checklist U1-U5

### For #1707 residual fix (the real code work)
- [ ] `_get_robots_parser` + per-domain cache implemented in `job-market-scanner.py`
- [ ] `safe_request()` calls robots check; skips on disallow; **fails-closed on unreachable**
- [ ] New tests `tests/gtm/test_robots_respect.py` pass
- [ ] Existing tests `tests/gtm/test_job_market_scanner.py` + `tests/gtm/test_job_market_retention.py` still pass
- [ ] `TOS_REVIEW.md` created with per-source review + owner sign-off + C&D runbook (operational-only; legal deferred)
- [ ] `README.md` at `docs/strategy/gtm/job-market-scan/` updated to reflect robots.txt enforcement and new state
- [ ] #1707 closed with comment citing implementing commit + `TOS_REVIEW.md` path

### For unpause (Commit 3, separate decision)
- [ ] All five unpause-checklist items (U1-U5) green
- [ ] Dry-run scan completes cleanly
- [ ] Commit 3 lands: un-comment cron task

---

## Rollback / State Machine (v2 rewrite — addresses Claude F5)

Cron is currently **paused**. The four states below are the only legal resting states; two others are explicitly unsafe.

### Resting states

| State | paused? | docs (TOS_REVIEW, README)? | robots.txt code? | OK as resting state? |
|---|---|---|---|---|
| S0 (current) | YES | no | no | **YES** — safe baseline; the work begins here |
| S1 (after Commit 1) | YES | yes | no | **YES** — docs alone introduce no runtime change |
| S2 (after Commit 2) | YES | yes | yes + tests green | **YES** — code is in place but cron still paused; U5 dry-run can run from here |
| S3 (after Commit 3) | no | yes | yes + tests green | **YES** — full unpause, the target state |

### Unsafe / forbidden resting states

| State | Why forbidden |
|---|---|
| unpaused + docs + no robots.txt code | Runtime resumes scraping without robots.txt — violates the reason for the pause |
| unpaused + docs + partial-robots (tests red) | Code exists but is not verified — false sense of compliance |
| paused + robots.txt code + no TOS_REVIEW.md | Technical control without the governance artifact — incomplete per #1707 acceptance |

### Rule
- Never commit Commit 3 (unpause) unless Commits 1 and 2 are both green and U1-U5 all check.
- If Commit 2 test run fails, the correct action is **stop, fix, re-commit — not revert Commit 1**. Commit 1 is additive and safe to leave.
- If the #1707 code change lands but later reveals a defect in production (e.g., robots.txt check blocks everything on a bad fetch), the resting state rolls back to **S2** (paused + docs + code-reverted) pending fix, NOT S3. Reverting the robots check while cron is active would silently restore pre-#1707 behavior; that's the dangerous path.

### Failure modes
- **Scanner crashes on `rp.read()` for a new domain:** handled — `try/except` in `_get_robots_parser` returns None; caller fails-closed.
- **robots.txt denies everything for a source:** correct signal — that source moves to the "remove from allowlist" column in `TOS_REVIEW.md`; approver decides; no silent scan-through.
- **Zero-result scan after unpause because all sources block robots.txt:** file as a separate issue; do NOT silently accept. Add a minimum-result alarm as follow-up (not in this plan's scope).

---

## Risks and Open Questions

### Open questions for user (required before round-2 review)
- **Q1 (load-bearing): Confirm live-source scope for `TOS_REVIEW.md`.** Plan v2 lists `linkedin`, `indeed`, `career_page` based on dashboard.md. User decides: (a) remove dead sources (`google`, `google_direct`, `rigzone`) from `SOURCE_ALLOWLIST` now; or (b) keep as dead code with a note; or (c) treat the dead sources as "block-detected" and remove on that basis.
- **Q2 (load-bearing): Confirm owner-as-non-engineer-approver path, or direct to counsel.** Plan v2 assumes the user signs off as owner. If the user wants external counsel, the acceptance criteria accommodate that — approve the deferral path.
- **Q3: LinkedIn specifically — keep, restrict, or remove?** Plan v1 flagged as ELEVATED RISK. v2 routes the decision to the approver sign-off on `TOS_REVIEW.md`. No pre-emptive removal in this plan; removal remains available at approver's discretion.

### Known risks
- **Risk: robots.txt check adds ~N network calls per scan (one per new domain).** Mitigation: per-domain caching.
- **Risk: `TOS_REVIEW.md` is a compliance record, not a legal opinion.** Mitigation: explicit split between operational step (remove from allowlist) and legal response (route to counsel); approver signs off on the split.
- **Risk: fail-closed on robots-unreachable may produce near-empty scans if sites block.** Mitigation: dry-run in U5 surfaces this before unpause; a degenerate dry-run blocks Commit 3 until the scope is re-approved.
- **Risk: C&D never arrives but scraping continues.** Mitigation: residual risk explicitly acknowledged in `TOS_REVIEW.md`; approver accepts in writing. Not a hidden assumption.

### Decided (not open)
- #1708 and #1709 are CLOSED. Not reopened.
- Scanner will not be rewritten around official APIs (Indeed Publisher deprecated 2023; LinkedIn Talent Solutions paywalled; Google Jobs API deprecated 2023). Documented in `TOS_REVIEW.md`; not re-litigated in-plan.
- robots-unreachable defaults to **DENY** (fail-closed). Flipped from v1's ALLOW.

### Not applicable (removed from v1)
- The v1 "memory correction for Mon-Fri cadence" item was a misread. `project_nightly_researchers.md` is about the GSD nightly researchers (Mon-Fri rotation), not the GTM scanner (weekly-Monday). No memory edit needed.

---

## Adversarial Review Plan (Round 2)

Dispatch after user confirms Q1-Q3 above:
- Claude (self-review via `/code-review` skill) — focus on whether fail-closed default is correctly wired and whether the state machine holds.
- Codex (push plan to GitHub, then dispatch) — focus on the approver-sign-off path and whether `TOS_REVIEW.md` structure meets the governance bar Codex raised in round 1.
- (Optional) Gemini — cross-provider redundancy on the approver-authority question.

Specific stress-test questions for round 2:
- Is fail-closed on robots-unreachable now correctly defended, or does the plan's own "if all sources block, dry-run fails" clause reveal a scope problem?
- Does the `TOS_REVIEW.md` approver sign-off actually bind, given it's a git commit trailer rather than a separate legal document?
- Is the "remove source within 24h on C&D" still too specific? Should the SLA be "within reasonable time as directed by counsel"?

---

## Complexity: T2

Single code file modified (`job-market-scanner.py`), one new test file, one new doc, one README update, one cron-config toggle (Commit 3). No new dependency (`urllib.robotparser` is stdlib). Sign-off governance and the explicit state machine are what make this T2 rather than T1.
