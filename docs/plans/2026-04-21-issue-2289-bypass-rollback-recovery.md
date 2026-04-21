# Plan for #2289: bypass rollback / recovery — detect, decide, revert when enforcement gates are bypassed after commit or push

> **Status:** draft (v3, post-v2-adversarial-review revision)
> **Complexity:** T2
> **Date:** 2026-04-21
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2289
> **Parent:** #2018
> **Review artifacts (v1):** `scripts/review/results/2026-04-21-plan-2289-claude.md` (MAJOR) | `2026-04-21-plan-2289-gemini.md` (MAJOR). Codex v1 dispatch timed out at 5-min cap; no artifact produced.
> **Review artifacts (v2):** `scripts/review/results/2026-04-21-plan-2289-claude-v2.md` (MINOR) | `2026-04-21-plan-2289-codex-v2.md` (MAJOR) | `2026-04-21-plan-2289-gemini-v2.md` (MAJOR)
> **Review artifacts (v3):** pending — re-dispatch after this revision lands.

---

## Adversarial Review History

| Rev | Date | Claude | Codex | Gemini | Disposition |
|---|---|---|---|---|---|
| v1 | 2026-04-21 | MAJOR | (timed out) | MAJOR | Revised to v2. See v2 rationale in this section's history. |
| v2 | 2026-04-21 | MINOR (all v1 resolved; N1-N4 + MM1 + L1-L2) | MAJOR | MAJOR | Revised to v3. See v3 rationale below. |
| v3 | 2026-04-21 | (pending) | (pending) | (pending) | Re-dispatch after this commit. |

### v3 revision rationale (addresses all v2 findings)

**Codex v2 (6 findings):**
1. **`git commit --no-verify` detection** — v3 adds an `all-commits-observer` post-commit hook that logs every HEAD commit SHA+branch+author+timestamp to `logs/hooks/all-commits-observer.jsonl` regardless of whether any bypass event was flagged. Advisor detects `--no-verify` bypasses by finding commits in the observer log that (a) have no corresponding pre-commit `plan-gate-events.jsonl` entry within the correlation window AND (b) touch impl files AND (c) have no approval marker. This closes the coverage gap.
2. **`$GIT_COMMIT` → `git rev-parse HEAD`** — v3 corrects the Log Schema: post-commit hook resolves SHA via `git rev-parse HEAD`, not an undocumented env var.
3. **Correlation contract canonicalized as content-based** — v3 defines `staged_files_digest` as `sha256(<git diff --cached --format=raw>)` (content-hash of the staged diff). Reconciled across §Log Schema, §Risks, and §TDD. Adds `test_correlator_same_digest_collision_is_reported_as_ambiguous` for same-file-set+5s-window collision detection.
4. **`has_approval_intent()` normative rule** — v3 defines the rule precisely: a commit SHA has approval intent iff EITHER (a) a file at `.planning/plan-approved/*.md` exists containing a line matching regex `^Approved by: \S+` and its mtime is within 24h of the commit timestamp, OR (b) the parent issue (resolved from commit message `#NNNN` reference or from the staged_files path `docs/plans/YYYY-MM-DD-issue-NNNN-*.md`) transitioned to `status:plan-approved` on GitHub after the commit date. Fallback behavior for `gh` unavailable is `log_only_auth_failed` (NOT `revert_recommended`).
5. **`pushed` as tri-state** — v3 changes `pushed: bool` to `pushed: true | false | unknown`. `true` when `git branch -r --contains <sha>` prints at least one remote-tracking ref; `false` when the command returns empty AND the repo has at least one remote with fetched refs within the last 7 days; `unknown` otherwise (shallow clone, no remote, stale refs). `unknown` propagates as `log_only_pushed_unknown` verdict rather than a forced bool decision.
6. **Safe-list split for governance paths** — v3 defines two distinct safe-lists. `COMMIT_GATE_SAFE_PATHS` (existing, read from `require-plan-approval.sh`) determines when a commit needs approval. `ADVISOR_SAFE_PATHS` (new, defined in `BYPASS-ROLLBACK-POLICY.md`) is a NARROWER set used only for `log_only_safe_paths` verdict: `docs/plans/`, `docs/reports/`, `docs/standards/`, `.planning/` only. Changes to `.claude/hooks/`, `scripts/enforcement/`, `.github/workflows/enforcement-gate.yml`, `docs/governance/TRUST-ARCHITECTURE.md`, and the 4 agent-adapter markdown files are EXPLICITLY classified as `enforcement_surface_change` and get a dedicated verdict path — even if they bypassed approval, they stay rollback-eligible.

**Gemini v2 (3 findings):**
1. **`staged_files_digest` contradiction** — fixed in v3 Codex #3 above (content-hash canonicalized).
2. **Pushed-revert detection missing** — v3 adds `has_been_reverted_via_revert_commit(sha)` check. Uses `git log --grep="^Revert \"" --fixed-strings <sha>..HEAD` AND `git log --format="%b" <sha>..HEAD | grep "This reverts commit <sha>"` to find both conventional revert messages and SHA-embedded reverts. If found, emit `log_only_reverted_later`. Added to pseudocode between `any_later_commit_has_review_evidence` and the `revert_recommended` path. New TDD: `test_advisor_skips_pushed_commit_already_reverted`.
3. **Fragile `gh` auth fallback** — v3 introduces `log_only_auth_failed` verdict (see Codex #4 above). `--strict` exit semantics updated per Claude N3.

**Claude v2 (7 findings):**
- N1 (staged_files_digest contradiction) — fixed above via Codex #3.
- N2 (approval phrase not defined) — fixed above via Codex #4 (normative regex).
- N3 (`--strict` silent on unresolvable) — v3 specifies `--strict` exits non-zero on `revert_recommended` OR `log_only_unresolved` OR `log_only_auth_failed` OR `log_only_pushed_unknown`. These four states represent "operator attention required."
- N4 (install-hook wiring untested) — v3 adds `test_install_hooks_wires_post_commit_hooks`.
- MM1 (AGENTS.md update missing) — v3 adds `AGENTS.md` to §Files to Change with note documenting `FORCE_PLAN_GATE=1` as a logged-bypass env var (parity with push-gate `SKIP_REVIEW_GATE=1`).
- L1 (stale v1 Codex artifact link) — v3 top-matter now correctly states Codex v1 produced no artifact.
- L2 (source count mismatch) — v3 source count below is re-tallied.

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/enforcement/require-review-on-push.sh` logs push-gate bypass events to `logs/hooks/review-gate-bypass.jsonl` when `SKIP_REVIEW_GATE=1` is set (lines 149–167: `log_bypass()`, writes JSON with timestamp/user/branch/local_oid/remote_oid/action=bypass).
- Found: `scripts/enforcement/require-plan-approval.sh` is the pre-commit gate. Line 113 currently logs `plan-gate-blocked` events to `logs/hooks/plan-gate-events.jsonl` when it blocks. Does NOT currently read `$FORCE_PLAN_GATE`; the line 105 help text is misleading. v3 adds the real env check + log.
- Found: `scripts/enforcement/compliance-dashboard.sh` reads from `logs/hooks/` and emits aggregated metrics (`stage_prompt_drift_summary_json`). Does NOT currently aggregate bypass events. v3 adds `bypass_pending_review`.
- Found: `scripts/enforcement/enforcement-env.sh` defines `FORCE_PLAN_GATE_STRICT` (opt-in strict mode, line 17). Does NOT define `FORCE_PLAN_GATE`. v3 adds the bypass env var alongside.
- Found: `.claude/hooks/plan-approval-gate.sh` is the runtime write gate. Reads `SKIP_PLAN_APPROVAL_GATE=1` as bypass. Does NOT currently emit a bypass log. Future extension; v3 tolerant-read.
- Found: `.github/workflows/enforcement-gate.yml` is the CI/PR gate.
- Found: `docs/governance/TRUST-ARCHITECTURE.md` §Rollback Rules (lines 216–248) defines agent-initiated auto-rollback for failing tests. Distinct scope from bypass-initiated; v3 §Precedence covers both local-reset and pushed-revert handoffs.
- Found: `needs_plan_approval()` in `require-plan-approval.sh` lines 26–44 classifies commits as impl vs non-impl. v3 preserves this for the commit-gate, but introduces a separate narrower `ADVISOR_SAFE_PATHS` for advisor use — this is the Codex v2 #6 governance-safe-list fix.
- Found: git post-commit hook spec — no parameters, no `$GIT_COMMIT`. Use `git rev-parse HEAD` to obtain the commit SHA. Source: git hooks documentation.
- Found: `git branch -r --contains <sha>` behavior in shallow/no-remote/stale-ref states — returns empty, cannot distinguish "unpushed" from "unknown." v3 tri-state models this.
- Gap (v3 creates): `scripts/enforcement/bypass-rollback-advisor.sh`, `scripts/enforcement/post-commit-bypass-logger.sh`, `scripts/enforcement/all-commits-observer.sh` (new in v3), `tests/enforcement/test_bypass_rollback_advisor.py`, `docs/governance/BYPASS-ROLLBACK-POLICY.md`.

### Standards
| Standard | Status | Source |
|---|---|---|
| Rollback policy | partial — agent-initiated auto-rollback defined | `docs/governance/TRUST-ARCHITECTURE.md` §Rollback Rules (lines 216–248) |
| Hard-stop policy | established | `docs/standards/HARD-STOP-POLICY.md` |
| Review routing | established | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` |

### Documents consulted (v3)
- GitHub issue #2289 (body retrieved 2026-04-21) — parent=#2018; scope: trigger rules, mechanism, audit trail, tests.
- GitHub issue #2018 — closure dependency: child must be in `status:plan-review` or later.
- `docs/governance/TRUST-ARCHITECTURE.md` §Rollback Rules.
- `scripts/enforcement/require-review-on-push.sh` lines 149–170.
- `scripts/enforcement/require-plan-approval.sh` lines 1–123 in full.
- `scripts/enforcement/compliance-dashboard.sh` lines 1–40.
- `scripts/enforcement/enforcement-env.sh`.
- Adversarial reviews v1 (Claude MAJOR, Gemini MAJOR) and v2 (Claude MINOR, Codex MAJOR, Gemini MAJOR) — artifacts under `scripts/review/results/`.
- Git hooks official documentation: post-commit takes no parameters.
- Git branch -r behavior in shallow/no-remote modes.

### Gaps identified (v3-remaining)
- `--no-verify` bypass requires an always-on observer log (v3 adds `all-commits-observer.sh`).
- Hook wiring must be tested (v3 adds `test_install_hooks_wires_post_commit_hooks`).
- Governance-surface-path changes must remain rollback-eligible (v3 safe-list split).
- Advisor must handle `gh` auth failure without producing false `revert_recommended` (v3 `log_only_auth_failed`).
- Tri-state `pushed` for shallow/stale/no-remote conditions (v3 `pushed: unknown`).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-21):
- `#2289` OPEN — labels: priority:high, cat:harness, domain:workflow.
- `#2018` OPEN — labels: priority:high, cat:engineering, cat:harness, domain:workflow, `status:plan-review`.

**File existence** (`ls -la` 2026-04-21):
- EXISTS: `require-review-on-push.sh`, `require-plan-approval.sh`, `compliance-dashboard.sh`, `enforcement-env.sh`, `TRUST-ARCHITECTURE.md`.
- MISSING (v3 creates): `bypass-rollback-advisor.sh`, `post-commit-bypass-logger.sh`, `all-commits-observer.sh`, `test_bypass_rollback_advisor.py`, `BYPASS-ROLLBACK-POLICY.md`.

**Line excerpt verifying v1 defect claim persists as fix-target:**
```
$ grep -n '^[^#]*FORCE_PLAN_GATE\b' scripts/enforcement/require-plan-approval.sh
12:STRICT_MODE="${FORCE_PLAN_GATE_STRICT:-0}"
# (no bare FORCE_PLAN_GATE check — v3 adds one)
```

**Gap proofs:**
- `grep -r "bypass-rollback" scripts/` → no matches.
- `ls tests/enforcement/*rollback*` → does not exist.
- `grep -n bypass scripts/enforcement/compliance-dashboard.sh` → no matches.
- `ls scripts/enforcement/all-commits-observer.sh` → does not exist (v3 creates).

**v3 source count:** 8 repo files + 2 GitHub issues + 5 review artifacts (Claude v1, Gemini v1, Claude v2, Codex v2, Gemini v2) + 2 governance docs + 2 external refs (git hooks docs, git branch -r behavior) = 19 distinct sources.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-21-issue-2289-bypass-rollback-recovery.md` |
| Policy doc (new) | `docs/governance/BYPASS-ROLLBACK-POLICY.md` |
| Advisor script (new) | `scripts/enforcement/bypass-rollback-advisor.sh` |
| Post-commit correlator (new) | `scripts/enforcement/post-commit-bypass-logger.sh` |
| All-commits observer (new, v3) | `scripts/enforcement/all-commits-observer.sh` |
| Install-hook wiring (modify) | `scripts/enforcement/install-hooks.sh` |
| Tests (new) | `tests/enforcement/test_bypass_rollback_advisor.py` |
| Commit-gate bypass path (modify) | `scripts/enforcement/require-plan-approval.sh` |
| Dashboard signal (modify) | `scripts/enforcement/compliance-dashboard.sh` |
| AGENTS.md (modify, v3) | `AGENTS.md` — document `FORCE_PLAN_GATE=1` as a logged-bypass env var |
| TRUST-ARCHITECTURE cross-ref (modify) | `docs/governance/TRUST-ARCHITECTURE.md` |
| README index (modify) | `docs/plans/README.md` |
| v3 reviews (pending) | `scripts/review/results/2026-04-21-plan-2289-claude-v3.md`, `...-codex-v3.md`, `...-gemini-v3.md` |

---

## Deliverable

A written bypass-rollback policy (`BYPASS-ROLLBACK-POLICY.md`), an advisor script that: (i) enumerates deduplicated commit-level bypass events across multiple log sources (push-gate, plan-gate, and an `all-commits-observer` for `--no-verify` coverage); (ii) emits one of six verdicts per commit SHA (`log_only_approved_later` / `log_only_safe_paths` / `log_only_remediated_later` / `log_only_reverted_later` / `log_only_auth_failed` / `log_only_pushed_unknown` / `revert_recommended`); (iii) resolves `pushed` state as tri-valued; (iv) treats enforcement-surface paths as rollback-eligible regardless of commit-gate safe-list classification. Plus a three-hook install mechanism, AGENTS.md update, and TDD coverage.

---

## Key Design Decisions (reviewer-contestable)

1. **Advisory, not automatic.** The advisor produces verdicts; human or higher-scope tool executes. Future auto-revert is a separate extension issue.
2. **Six-verdict taxonomy.** `log_only_approved_later`, `log_only_safe_paths`, `log_only_remediated_later`, `log_only_reverted_later`, `log_only_auth_failed`, `log_only_pushed_unknown`, `revert_recommended`. The `log_only_*` variants differ semantically — `auth_failed` and `pushed_unknown` indicate observability gaps; `safe_paths` is a policy exemption; `approved_later` / `remediated_later` / `reverted_later` are post-hoc closures.
3. **Dual safe-list split.** `COMMIT_GATE_SAFE_PATHS` governs commit-approval requirement (per `require-plan-approval.sh`). `ADVISOR_SAFE_PATHS` governs rollback-exemption (narrower). Enforcement-surface paths are explicitly NOT in `ADVISOR_SAFE_PATHS` so bypass of an enforcement-surface change stays rollback-eligible.
4. **Three-hook install.** Pre-commit (existing, modified), post-commit bypass correlator (new), post-commit all-commits observer (new). The observer is what enables `--no-verify` detection.
5. **Default exit zero + `--strict`.** `--strict` exits non-zero when any verdict is `revert_recommended`, `log_only_unresolved`, `log_only_auth_failed`, or `log_only_pushed_unknown`.
6. **`has_approval_intent` is normative.** Regex, mtime window, and GH-label fallback are all specified; `gh` auth failure → `log_only_auth_failed` (never silent approval-false).
7. **`pushed` is tri-valued.** `true` / `false` / `unknown`; `unknown` → `log_only_pushed_unknown`.

---

## Pseudocode

```
bypass_rollback_advisor(argv):
    strict_mode = parse_strict(argv)

    events = []
    events += read_jsonl(logs/hooks/review-gate-bypass.jsonl)        # push gate
    events += read_jsonl(logs/hooks/plan-gate-bypass.jsonl)          # plan-gate post-commit correlator
    events += synthesize_observer_events(logs/hooks/all-commits-observer.jsonl,
                                         logs/hooks/plan-gate-events.jsonl)
                                                                     # --no-verify synthesized events
    if exists(logs/hooks/runtime-write-bypass.jsonl):
        events += read_jsonl(logs/hooks/runtime-write-bypass.jsonl)  # tolerant-read

    # Resolve commit SHA for every event.
    for event in events:
        event.resolved_sha = event.get("commit_sha") or event.get("local_oid") or None
        if not event.resolved_sha:
            event.verdict = "log_only_unresolved"

    # Dedup by resolved_sha.
    grouped = group_by(events, key="resolved_sha")

    for sha, sha_events in grouped.items():
        # Approval-intent check (normative; falls back to auth_failed on gh failure)
        intent = has_approval_intent(sha)
        if intent == "approved":
            emit_verdict(sha, "log_only_approved_later", sha_events); continue
        if intent == "auth_failed":
            audit_write(sha, sha_events, verdict="log_only_auth_failed")
            emit_verdict(sha, "log_only_auth_failed", sha_events); continue

        touched = git_show_names_only(sha)

        # Enforcement-surface changes are NEVER safe-listed
        if any_path_in_enforcement_surface(touched):
            # skip safe-list exemption; continue evaluation below
            pass
        elif all_paths_in(touched, ADVISOR_SAFE_PATHS):
            emit_verdict(sha, "log_only_safe_paths", sha_events); continue

        # Pushed-revert detection (Gemini v2 #2)
        if has_been_reverted_via_revert_commit(sha):
            emit_verdict(sha, "log_only_reverted_later", sha_events); continue

        # Later-commit review-evidence remediation (existing)
        if any_later_commit_has_review_evidence(sha):
            emit_verdict(sha, "log_only_remediated_later", sha_events); continue

        # Pushed tri-state
        pushed = resolve_pushed_state(sha)      # true | false | unknown
        if pushed == "unknown":
            audit_write(sha, sha_events, touched, pushed=pushed,
                        verdict="log_only_pushed_unknown")
            emit_verdict(sha, "log_only_pushed_unknown", sha_events); continue

        audit_write(sha, sha_events, touched, pushed=pushed,
                    verdict="revert_recommended")
        emit_verdict(sha, "revert_recommended", sha_events, pushed=pushed)

    exit_code = 0
    if strict_mode and any_verdict_in({
        "revert_recommended", "log_only_unresolved",
        "log_only_auth_failed", "log_only_pushed_unknown"
    }):
        exit_code = 1
    return exit_code


# --- helper function contracts -------------------------------------

synthesize_observer_events(observer_log, plan_events_log):
    # For each commit in observer_log, find matching plan-gate-events within
    # the correlation window by (branch, staged_files_digest, time).
    # If NO match exists → synthesize a "--no-verify-bypass" event for the SHA.
    # If a match exists → skip (already captured by plan-gate-bypass.jsonl).
    ...

has_approval_intent(sha):
    # Returns: "approved" | "unapproved" | "auth_failed"
    # (1) .planning/plan-approved/*.md: file contains regex `^Approved by: \S+`
    #     AND mtime within 24h of commit timestamp → "approved"
    # (2) Parent issue (from commit message #NNNN or plan file path) transitioned
    #     to status:plan-approved on GitHub after commit date → "approved"
    #     If gh command fails or returns non-auth error → "auth_failed"
    # (3) Otherwise → "unapproved"
    ...

resolve_pushed_state(sha):
    # Returns: "true" | "false" | "unknown"
    # "true" if `git branch -r --contains <sha>` prints any ref.
    # "false" if command returns empty AND `git fetch --dry-run 2>&1` shows
    #         successful contact AND last `.git/FETCH_HEAD` mtime within 7 days.
    # "unknown" otherwise (shallow clone, no remote, stale >7d, offline).
    ...

has_been_reverted_via_revert_commit(sha):
    # Returns: bool
    # True if either:
    #   (a) `git log --grep="^Revert" <sha>..HEAD` includes a commit whose
    #       body contains `This reverts commit <sha>`, OR
    #   (b) `git log --grep="<sha>" <sha>..HEAD --fixed-strings` matches.

any_path_in_enforcement_surface(paths):
    # Returns True if any path matches:
    #   .claude/hooks/**
    #   scripts/enforcement/**
    #   .github/workflows/enforcement-gate.yml
    #   docs/governance/TRUST-ARCHITECTURE.md
    #   AGENTS.md, CLAUDE.md, GEMINI.md, .codex/CODEX.md
```

---

## Log Schema (v3 — explicit field map)

| Field | push-gate bypass (existing) | pre-commit plan-gate events (modified) | post-commit plan-gate bypass (new) | all-commits-observer (new v3) |
|---|---|---|---|---|
| `timestamp` | ✓ | ✓ | ✓ | ✓ |
| `user` | ✓ | (v3: add) | ✓ | ✓ |
| `branch` | ✓ | ✓ | ✓ | ✓ |
| `action` | `"bypass"` | `"plan-gate-blocked"` or `"plan-gate-bypass-attempted"` | `"bypass-landed"` | `"commit-observed"` |
| `local_oid` | ✓ | — (n/a pre-commit) | — | — |
| `remote_oid` | ✓ | — (n/a pre-commit) | — | — |
| `staged_files_digest` | — | ✓ — `sha256(git diff --cached --format=raw)` (content-based; v3) | ✓ (v3, for correlation) | — |
| `commit_sha` | — | — (not yet available at pre-commit) | ✓ — obtained via `git rev-parse HEAD` (v3) | ✓ — obtained via `git rev-parse HEAD` (v3) |
| `touched_paths` | — | — | — | ✓ (v3, from `git diff-tree --no-commit-id --name-only -r HEAD`) |

Canonical correlation key is `staged_files_digest` (content-based). See `synthesize_observer_events` for `--no-verify` synthesis.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/governance/BYPASS-ROLLBACK-POLICY.md` | Policy: triggers, dual safe-lists, audit contract, §Precedence |
| Create | `scripts/enforcement/bypass-rollback-advisor.sh` | Advisor per §Pseudocode; 6 verdicts; tri-state `pushed` |
| Create | `scripts/enforcement/post-commit-bypass-logger.sh` | Post-commit correlator — joins pre-commit event by content-hash; writes bypass log with `git rev-parse HEAD` |
| Create | `scripts/enforcement/all-commits-observer.sh` | Post-commit always-on logger — enables `--no-verify` detection |
| Create | `tests/enforcement/test_bypass_rollback_advisor.py` | 20-test TDD suite |
| Modify | `scripts/enforcement/require-plan-approval.sh` | Real `$FORCE_PLAN_GATE=1` check + `log_bypass()` writing `staged_files_digest` (content-hash) |
| Modify | `scripts/enforcement/install-hooks.sh` | Wire both post-commit hooks (correlator + observer) |
| Modify | `scripts/enforcement/compliance-dashboard.sh` | Add `bypass_pending_review` field |
| Modify | `AGENTS.md` | Document `FORCE_PLAN_GATE=1` as logged-bypass env var (parity with `SKIP_REVIEW_GATE=1`) |
| Update | `docs/governance/TRUST-ARCHITECTURE.md` | Cross-reference BYPASS-ROLLBACK-POLICY.md §Precedence |
| Update | `docs/plans/README.md` | Plan row |

---

## TDD Test List (v3 — 20 tests)

| Test name | What it verifies |
|---|---|
| `test_advisor_no_events_clean_exit` | Empty logs → exit 0, empty verdicts |
| `test_advisor_log_only_when_approval_intent_exists` | Marker with `^Approved by: \S+` within 24h → `log_only_approved_later` |
| `test_advisor_distinguishes_advisory_mode_from_explicit_approval` | Marker without approval phrase → not masked as approved |
| `test_advisor_log_only_when_safe_path_only` | Commit touching `docs/plans/` only → `log_only_safe_paths` |
| `test_advisor_enforcement_surface_commit_never_safe_listed` (**v3**) | Commit touching `scripts/enforcement/` → NOT `log_only_safe_paths`, gets full evaluation |
| `test_advisor_log_only_when_remediated_later` | Later commit with review evidence → `log_only_remediated_later` |
| `test_advisor_log_only_when_reverted_via_revert_commit` (**v3**) | Pushed commit reverted via `git revert` → `log_only_reverted_later` |
| `test_advisor_log_only_when_gh_auth_fails` (**v3**) | `gh` unavailable during `has_approval_intent` → `log_only_auth_failed` (NOT `revert_recommended`) |
| `test_advisor_deduplicates_events_by_sha` | Same SHA from commit-gate + push-gate → one verdict |
| `test_advisor_pushed_state_tri_valued_true` (**v3**) | Pushed commit + remote refs current → `pushed=true` |
| `test_advisor_pushed_state_tri_valued_false` (**v3**) | Unpushed commit + remote contactable + fresh refs → `pushed=false` |
| `test_advisor_pushed_state_tri_valued_unknown` (**v3**) | Shallow clone or no-remote → `pushed=unknown` → `log_only_pushed_unknown` verdict |
| `test_advisor_revert_recommended_pushed_true` | Pushed + impl + unremediated → `revert_recommended, pushed=true` |
| `test_advisor_revert_recommended_pushed_false` | Local-only + impl + unremediated → `revert_recommended, pushed=false` |
| `test_advisor_writes_audit_before_emitting_proposal` | Audit record JSONL line written before verdict emission |
| `test_advisor_multi_file_commit_reported_atomically` | N-file commit → one verdict entry |
| `test_advisor_detects_no_verify_bypass_via_observer_log` (**v3**) | `git commit --no-verify` that skipped pre-commit → observer synthesizes bypass event → `revert_recommended` |
| `test_commit_gate_detects_force_plan_gate_env_var` | `FORCE_PLAN_GATE=1 git commit` → logged as `plan-gate-bypass-attempted` with content-hash digest |
| `test_correlator_same_digest_collision_is_reported_as_ambiguous` (**v3**) | Two concurrent commits on same branch with identical staged content → correlator emits both records + logs `correlation_ambiguous` warning |
| `test_install_hooks_wires_post_commit_hooks` (**v3**) | After `install-hooks.sh` runs, `.git/hooks/post-commit` invokes both correlator and observer |
| `test_dashboard_surfaces_pending_bypass_count` | Dashboard JSON `bypass_pending_review` matches non-log-only count |

**TDD-first rule:** all 20 tests written and failing before implementation lands.

---

## Acceptance Criteria

- [ ] All 20 tests pass: `uv run pytest tests/enforcement/test_bypass_rollback_advisor.py -v`
- [ ] No regression: `uv run pytest tests/enforcement/ -v`
- [ ] `docs/governance/BYPASS-ROLLBACK-POLICY.md` exists; referenced from TRUST-ARCHITECTURE.md; includes §Precedence and dual safe-list specs.
- [ ] `bypass-rollback-advisor.sh` executable; default exit 0; `--strict` exits non-zero on `revert_recommended`, `log_only_unresolved`, `log_only_auth_failed`, `log_only_pushed_unknown`.
- [ ] Both post-commit hooks installed via `install-hooks.sh`; verified by test.
- [ ] `require-plan-approval.sh` genuinely honors `$FORCE_PLAN_GATE=1` and emits content-hash `staged_files_digest`.
- [ ] `AGENTS.md` documents `FORCE_PLAN_GATE=1` as logged-bypass env var.
- [ ] Compliance dashboard exposes `bypass_pending_review` field.
- [ ] All three v3 review artifacts exist under `scripts/review/results/`.
- [ ] Adversarial review v3 returns APPROVE or MINOR.

---

## Risks and Open Questions

- **Risk:** same-content same-branch same-second collision in `staged_files_digest` remains possible (rare but real — amend, concurrent worktrees). Mitigation: `test_correlator_same_digest_collision_is_reported_as_ambiguous` asserts detection; advisor adds `correlation_ambiguous` to audit record instead of silently picking one match.
- **Risk:** `--no-verify` observer creates a per-commit log entry unconditionally; volume could grow. Mitigation: observer log rotates weekly (future work tracked as extension issue); advisor tolerates missing historical entries via correlation-window cutoff.
- **Risk:** `has_been_reverted_via_revert_commit` can miss hand-crafted reverts that don't use `git revert`'s default message format. Mitigation: acceptable — those would produce `revert_recommended`, which is advisory (human can decline).
- **Risk:** `--strict` exit non-zero on `log_only_pushed_unknown` could trigger CI alerts on shallow-clone CI runners. Mitigation: document in `BYPASS-ROLLBACK-POLICY.md` that `--strict` should NOT be wired into CI runners using shallow clones; default cron/local use is fine.
- **Resolved:** v1 findings all addressed in v2; v2 findings all addressed in v3 (see §Adversarial Review History).
- **Open #1:** should the observer log be committed to a new `logs/hooks/README.md` with retention policy? Deferred to extension issue.
- **Open #2:** should `has_approval_intent` also honor `.planning/phases/*/REVIEWS.md APPROVE` (as the commit gate does at `require-plan-approval.sh:57`)? Current stance: yes — added to the rule; test coverage pending in implementation.

---

## Precedence vs TRUST-ARCHITECTURE.md §Rollback Rules

`TRUST-ARCHITECTURE.md` §Rollback Rules defines **agent-initiated** rollback (agent's commit breaks tests → auto-revert or human-confirmed). This plan defines **bypass-initiated** rollback (any actor's commit bypassed the gates).

Precedence when both apply to the same commit:
1. Agent-initiated rollback runs first when applicable (local commit + failing tests → `git reset HEAD~1`).
2. If the original commit was pushed and reverted via `git revert`, advisor detects via `has_been_reverted_via_revert_commit` → `log_only_reverted_later`.
3. If the original commit was local-only and reset via `git reset HEAD~1`, advisor's `git branch -r --contains` returns false AND the commit no longer exists on the branch → skipped (no event emitted beyond the already-logged bypass history).
4. If neither rollback path fired, advisor's verdict stands per §Pseudocode.

This precedence is restated in `BYPASS-ROLLBACK-POLICY.md` §Precedence with full evidence.

---

## Complexity: T2

**T2** — two new shell scripts (~200 lines combined: advisor + observer), one new post-commit correlator (~80 lines), one new policy doc (~150 lines), one new test file (20 tests), four modified files (commit-gate bypass logger + hooks installer + dashboard field + AGENTS.md). No cross-repo changes; no new infrastructure surface; no CI wiring. Scope expanded from v2 (added observer + tri-state pushed + safe-list split + pushed-revert detection + auth-failed verdict + AGENTS.md update) but remains T2 — multi-file, no architecture change.
