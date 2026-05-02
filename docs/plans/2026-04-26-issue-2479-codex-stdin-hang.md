# Plan for #2479: fix(review): Codex stdin-hang regression post-#2406 closure (size-dependent)

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-26
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2479
> **Review artifacts (to be produced):** scripts/review/results/2026-04-26-plan-2479-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/review/plan-review-fanout.sh` (line 94 on `main` branch as of 2026-04-26) — currently passes `--no-interactive` and lacks the `</dev/null` redirect on the codex branch. The wrapper will be patched.
- Found: `scripts/review/submit-to-codex.sh:200-218` — `run_codex_exec()` already redirects stdin to `/dev/null` per the original #2406 fix; this is the canonical pattern that `plan-review-fanout.sh` will mirror.
- Found: `scripts/review/tests/test_plan_review_fanout.sh:169-178` (on `main`) — currently asserts inline plan body + delimiter; the fix branch already extends test 5 with a removed-flag regression guard.
- Found: existing in-flight branch `origin/fix/codex-stdin-hang` at commit `257b47dd9` (authored 2026-04-24 by vamseeachanta; parent `4b2d4fbef`). The branch already lands the wrapper fix and the regression-guard test. The plan will not propose a fresh start; it will propose merging this branch plus adding a version-pinning safety net.
- Found: `docs/plans/2026-04-20-issue-2406-codex-stdin-hang-fix.md` (40 KB) — the prior plan for #2406 against codex-cli 0.121.0. Superseded by this plan against the 0.124.0+ failure class.

### Standards
Not applicable — harness fix, not engineering calculation.

### LLM Wiki pages consulted
Not applicable — harness/infrastructure scope.

### Documents consulted
- Issue #2479 body (counts as 1 source) — defines the two-part regression: wrapper-side (`--no-interactive` removed in 0.124.0) and upstream-side (`codex exec` stdin-hang). Lists 8/8 batch failures on 2026-04-23 with file paths under `scripts/review/results/`.
- Issue #2406 body — closing context. Original `</dev/null` fix landed against 0.121.0; closure was 2026-04-20; closure was silently defeated by the 2026-04-23 0.124.0 upgrade.
- `.claude/memory/topics/feedback_codex_sandbox_fallback_paths.md` — git-tracked memory file; reviewer-side context for codex sandbox behavior.
- `CLAUDE.md` global memory `feedback_codex_cli_0_124_upstream_regression` — installed 2026-04-23, blocks all `codex exec` calls regardless of stdin redirection, reproduces on 90-byte plans, workaround = downgrade to 0.123.0.
- `scripts/review/plan-review-prompt.md` — shared adversarial-stance prompt that the codex invocation feeds; unchanged by this plan but cited as part of the wrapper invocation contract.

### Gaps identified
- **Gap 1 (already addressed on `fix/codex-stdin-hang`):** wrapper still passes the removed `--no-interactive` flag on `main`. The fix branch removes the flag and adds the `</dev/null` redirect, plus a regression-guard assertion in `test_plan_review_fanout.sh`. The plan will land that branch on `main`.
- **Gap 2 (NEW — this plan adds):** there is no version-pinning or preflight check that detects an incompatible codex-cli version before a batch of plan reviews dispatches. The 2026-04-23 regression discovered itself only after 8/8 reviews failed silently into UNAVAILABLE stubs.
- **Gap 3 (NEW — this plan adds):** there is no end-to-end live smoke test that exercises `plan-review-fanout.sh` against a tiny real plan and asserts a non-stub artifact for codex; existing tests are mock-only and would not have caught either the flag-removal regression or the upstream stdin-hang.
- **Gap 4 (state-drift cleanup):** issue #2406 is closed-as-fixed but the closure was premature against the broader 0.124.0+ failure class. The plan will leave #2406 as closed-superseded (the user may reopen if preferred per #2479 body) and treat #2479 as the authoritative parent for the post-#2406 failure class.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-26 via `gh issue view`):
- `#2479` — OPEN — "fix(review): Codex stdin-hang regression post-#2406 closure (size-dependent)" — labels: bug, cat:harness, domain:knowledge-management, priority:high
- `#2406` — CLOSED — "fix(review): submit-to-codex.sh hangs on 'Reading additional input from stdin' for substantial plan files" — closed 2026-04-20; 3 comments; labels include status:plan-approved (stale-but-historical)

**Branch existence** (verified 2026-04-26 via `gh api repos/vamseeachanta/workspace-hub/branches/fix/codex-stdin-hang`):
- EXISTS: `fix/codex-stdin-hang` at SHA `257b47dd9cbe1cd81ae7aa97165c98de76eb25a4`
- Parent: `4b2d4fbef8c38a856dd62e4479741600e0f2ea65` (`docs(plans): revise batch-design to 2-agent pods (Explorer + Planner) in 2 waves`)
- Authored: 2026-04-24T10:21:17Z
- Files changed: `scripts/review/plan-review-fanout.sh` (+15/-3), `scripts/review/tests/test_plan_review_fanout.sh` (+6/-1)

**File existence** (`ls`/`git ls-files` 2026-04-26):
- EXISTS (git-tracked): `scripts/review/plan-review-fanout.sh`
- EXISTS (git-tracked): `scripts/review/submit-to-codex.sh`
- EXISTS (git-tracked): `scripts/review/tests/test_plan_review_fanout.sh`
- EXISTS (git-tracked): `scripts/review/plan-review-prompt.md`
- EXISTS (git-tracked): `scripts/review/lib/plan-file-parse.sh`
- EXISTS (git-tracked): `scripts/review/lib/disagreement-diff.sh`
- EXISTS (git-tracked): `docs/plans/2026-04-20-issue-2406-codex-stdin-hang-fix.md`
- EXISTS (git-tracked, 10 files): `scripts/review/results/2026-04-23-plan-{2105,2216,2227,2363,2368,2373,2380,2392,2441,2452}-codex.md` (the 2026-04-23 batch failure manifest)
- MISSING (NEW — this plan creates): `scripts/review/check-codex-version.sh` (preflight version probe)
- MISSING (NEW — this plan creates): `scripts/review/tests/test_check_codex_version.sh`
- MISSING (NEW — this plan creates): `scripts/review/tests/smoke_codex_live.sh` (opt-in live smoke)

**Wrapper line under repair** (`sed -n '85,95p' scripts/review/plan-review-fanout.sh` on `main`):
```
    codex)
      local combined
      combined="$(printf '%s\n\n--- PLAN (%s) ---\n%s' \
        "$(cat "$PROMPT_FILE")" "$PLAN_FILE" "$(cat "$PLAN_FILE")")"
      codex exec --no-interactive "$combined" > "$out" 2>"$err" || rc=$?
```
The fix branch replaces line 94 with `codex exec "$combined" > "$out" 2>"$err" </dev/null || rc=$?`.

**Currently-installed codex-cli version** (verified 2026-04-26 via `codex --version`):
- `codex-cli 0.125.0` (upgraded from 0.124.0 on 2026-04-25 per `stat /home/vamsee/.npm-global/lib/node_modules/@openai/codex/`)
- Available stable npm versions ≤ 0.125.0: `0.120.0`, `0.121.0`, `0.122.0`, `0.123.0`, `0.124.0`, `0.125.0`
- Post-0.125 batch artifacts that completed successfully: `scripts/review/results/2026-04-25-plan-2487-codex.md`, `2026-04-25-plan-2488-codex.md`, `2026-04-26-plan-2488-codex.md`, `2026-04-26-plan-2489-codex.md` — these contain real `## Verdict` blocks (`MAJOR`) with retrieval citations, not UNAVAILABLE stubs.

**Codex exec help output** (verified 2026-04-26 via `codex exec --help`):
- `--no-interactive` is NOT listed; flag remains removed in 0.125.0
- Subcommands: `resume`, `review`, `help`
- Stdin behavior documented: "If not provided as an argument (or if `-` is used), instructions are read from stdin."

**Source count:** 5 distinct sources (issue #2479 body, issue #2406 body, feedback memory file, fix-branch commit metadata, wrapper source code). Meets ≥3 retrieval contract.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-26-issue-2479-codex-stdin-hang-regression.md |
| In-flight fix branch (already exists, will be merged) | `origin/fix/codex-stdin-hang` @ `257b47dd9` |
| Wrapper fix (already on fix branch) | `scripts/review/plan-review-fanout.sh` |
| Wrapper-test regression guard (already on fix branch) | `scripts/review/tests/test_plan_review_fanout.sh` |
| New: codex-version preflight probe | `scripts/review/check-codex-version.sh` |
| New: preflight probe test | `scripts/review/tests/test_check_codex_version.sh` |
| New: opt-in live codex smoke test | `scripts/review/tests/smoke_codex_live.sh` |
| Wrapper integration | `scripts/review/plan-review-fanout.sh` (will call the preflight probe in `invoke_provider` for the codex branch and emit a structured UNAVAILABLE stub on incompatible version, instead of attempting and timing out) |
| Plan review — Claude | scripts/review/results/2026-04-26-plan-2479-claude.md |
| Plan review — Codex | scripts/review/results/2026-04-26-plan-2479-codex.md |
| Plan review — Gemini | scripts/review/results/2026-04-26-plan-2479-gemini.md |
| Plan index update | docs/plans/README.md |

---

## Deliverable

A merged `fix/codex-stdin-hang` branch on `main` plus a new `scripts/review/check-codex-version.sh` preflight probe that detects incompatible codex-cli versions before a fanout dispatches, surfaces a fast-fail UNAVAILABLE stub instead of timing out, and is wired into both `plan-review-fanout.sh` and an opt-in live smoke test, so a future upstream regression is detected at the first invocation rather than after an entire batch fails silently.

---

## Pseudocode

```
# scripts/review/check-codex-version.sh
function main():
    if codex CLI not on PATH:
        emit "MISSING: codex CLI not installed"
        return rc=2

    raw = `codex --version` (timeout 5s)
    parse "codex-cli X.Y.Z" → version_string
    parsed = split version_string into (major, minor, patch)

    # Compatibility window: known-good versions for the fanout argv shape.
    # 0.121.0 was the #2406 baseline; 0.123.0 is the last pre-regression release;
    # 0.125.0 was empirically validated 2026-04-25/2026-04-26 (real verdicts in
    # post-0.125 review artifacts). 0.124.0 is on the deny-list (upstream stdin-hang).
    KNOWN_GOOD = ["0.121.x", "0.122.x", "0.123.x", "0.125.x"]
    KNOWN_BAD  = ["0.124.0"]
    UNTESTED   = anything outside both lists

    if parsed in KNOWN_BAD:
        emit "INCOMPATIBLE: codex-cli {version} (known stdin-hang regression — issue #2479)"
        return rc=3
    if parsed in KNOWN_GOOD:
        emit "OK: codex-cli {version}"
        return rc=0
    # UNTESTED: warn but do not block — surface it in the artifact so the
    # operator notices novel-version drift without auto-disabling reviews.
    emit "WARN: codex-cli {version} is outside the tested window — may pass or fail; see #2479"
    return rc=0
```

```
# Integration in scripts/review/plan-review-fanout.sh, codex branch
case "$prov" in
  codex)
    if ! version_msg=$(check_codex_version); then
        rc=3
        echo "$version_msg" > "$err"
        # falls through to UNAVAILABLE stub builder; reason includes version
    else
        codex exec "$combined" > "$out" 2>"$err" </dev/null || rc=$?
    fi
    ;;
```

```
# scripts/review/tests/smoke_codex_live.sh (opt-in; requires CODEX_LIVE=1)
function main():
    if CODEX_LIVE != "1":
        skip "live smoke gated by CODEX_LIVE=1"
    fixture = "/tmp/2026-04-26-issue-9999-smoke.md" with 90-byte body
    run plan-review-fanout.sh on fixture, providers=codex only, timeout=120s
    artifact = scripts/review/results/...-9999-codex.md
    assert artifact contains real "## Verdict" line, NOT "UNAVAILABLE"
    assert artifact size > 200 bytes (UNAVAILABLE stub is ~191 bytes)
    cleanup fixture + artifact
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Merge | `origin/fix/codex-stdin-hang` → `main` | Lands the wrapper fix (drops `--no-interactive`, adds `</dev/null`) and the existing regression-guard test |
| Create | `scripts/review/check-codex-version.sh` | Preflight probe — detects KNOWN_BAD versions and surfaces UNTESTED versions |
| Create | `scripts/review/tests/test_check_codex_version.sh` | Unit tests for the probe (mocks `codex --version` output for each version class) |
| Create | `scripts/review/tests/smoke_codex_live.sh` | Opt-in live smoke; gated by `CODEX_LIVE=1` env var so CI does not consume credits |
| Modify | `scripts/review/plan-review-fanout.sh` | Wire the probe into the codex branch; emit version-aware UNAVAILABLE stub on rc=3 |
| Modify | `scripts/review/tests/test_plan_review_fanout.sh` | Add a test asserting the codex branch emits a version-aware stub when the probe returns rc=3 (mocked) |
| Update | `docs/plans/README.md` | Add this plan to the index |
| Update | `docs/plans/2026-04-20-issue-2406-codex-stdin-hang-fix.md` | Add a one-line trailer noting #2479 supersedes the closure for the 0.124.0+ failure class |

No changes to `scripts/review/submit-to-codex.sh` — it already has the `</dev/null` redirect from the original #2406 fix and works correctly under codex-cli 0.125.0 (verified by the 2026-04-25 / 2026-04-26 successful-codex artifacts).

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_check_codex_version_missing` | probe returns rc=2 with MISSING when codex not on PATH | `PATH=/empty` | rc=2, stdout contains "MISSING" |
| `test_check_codex_version_known_good_0_121` | probe returns rc=0 OK for 0.121.0 | mock `codex-cli 0.121.0` | rc=0, stdout contains "OK" |
| `test_check_codex_version_known_good_0_125` | probe returns rc=0 OK for 0.125.0 | mock `codex-cli 0.125.0` | rc=0, stdout contains "OK" |
| `test_check_codex_version_known_bad_0_124` | probe returns rc=3 INCOMPATIBLE for 0.124.0 | mock `codex-cli 0.124.0` | rc=3, stdout contains "INCOMPATIBLE", message references "#2479" |
| `test_check_codex_version_untested_warns` | probe returns rc=0 with WARN for novel version (e.g. 0.130.0) | mock `codex-cli 0.130.0` | rc=0, stdout contains "WARN: codex-cli 0.130.0 is outside the tested window" |
| `test_check_codex_version_malformed_output` | probe returns rc=2 on unparseable `codex --version` | mock `garbage` | rc=2, stdout contains "MISSING" or "PARSE" |
| `test_fanout_codex_unavailable_on_known_bad` | wrapper emits UNAVAILABLE stub when probe returns rc=3 (does NOT call `codex exec`) | mock probe returning rc=3, mock `codex` that hangs 60s | rc=0 from wrapper (graceful degradation), stub artifact contains "UNAVAILABLE" + version reason, NO 60s wait observed |
| `test_fanout_codex_no_no_interactive_flag` | regression-guard from fix branch — argv must never contain `--no-interactive` | normal mock invocation | passes (already on fix branch; this plan re-asserts it merges cleanly to `main`) |
| `smoke_codex_live_minimal_plan` (opt-in) | live `codex exec` against 90-byte fixture produces real Verdict | `CODEX_LIVE=1`; fixture plan; 0.125.0 installed | artifact contains "## Verdict" with one of APPROVE/MINOR/MAJOR/REJECT, size > 200 bytes, exit 0 |

---

## Acceptance Criteria

- [ ] `git merge --no-ff origin/fix/codex-stdin-hang` lands on `main` cleanly with no conflicts (or conflicts resolved without dropping the wrapper fix or the test guard).
- [ ] `bash scripts/review/tests/test_plan_review_fanout.sh` passes all 12+ tests on `main` after merge, including the regression guard for `--no-interactive`.
- [ ] `bash scripts/review/tests/test_check_codex_version.sh` passes all 6 unit tests listed above.
- [ ] On a host running codex-cli 0.124.0 (manually downgraded), `bash scripts/review/check-codex-version.sh` returns rc=3 with stdout containing `INCOMPATIBLE` and the issue reference `#2479`.
- [ ] On a host running codex-cli 0.125.0 (current install), `bash scripts/review/check-codex-version.sh` returns rc=0 with stdout containing `OK`.
- [ ] `CODEX_LIVE=1 bash scripts/review/tests/smoke_codex_live.sh` produces a real `## Verdict` artifact under codex-cli 0.125.0 within 120s.
- [ ] If `plan-review-fanout.sh` runs against a fixture with codex-cli 0.124.0 mocked, the codex artifact is a structured UNAVAILABLE stub naming the version, and the wrapper does not block on the timeout.
- [ ] `docs/plans/README.md` index row added for this plan.
- [ ] `docs/plans/2026-04-20-issue-2406-codex-stdin-hang-fix.md` trailer notes that #2479 supersedes the closure for the 0.124.0+ failure class.
- [ ] Review artifacts posted to `scripts/review/results/2026-04-26-plan-2479-{claude,codex,gemini}.md`.
- [ ] If the user opts to close #2406 (or reopen-then-close as superseded), this plan does not block on that decision — #2479 carries the authority going forward.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | (pending) | (will be filled after the adversarial wave runs against this plan) |
| Codex | (pending) | (will be filled after the adversarial wave runs against this plan) |
| Gemini | (pending) | (will be filled after the adversarial wave runs against this plan) |

**Overall result:** PENDING (re-draft if any provider returns MAJOR)

Pre-empted critiques (the plan will be hardened against these before adversarial review):

1. **"What if upstream lands a fix mid-implementation and 0.126.0 fixes the regression?"** — the probe's `KNOWN_GOOD` list will be updated as part of this plan only for versions where post-0.125 batch artifacts demonstrably succeed (e.g. 0.125.0 confirmed via 2026-04-25/2026-04-26 review files). Versions outside the tested window emit `WARN` (rc=0), not `INCOMPATIBLE` (rc=3) — the harness does not auto-block novel versions. A follow-up issue will be filed if-and-when codex-cli ships a documented stdin-hang fix and 0.126+ is whitelisted.

2. **"How does this avoid masking future regressions?"** — three layers: (a) the version probe surfaces UNTESTED versions with `WARN` so operators see drift in artifact metadata; (b) the opt-in live smoke test asserts a real `## Verdict` against a 90-byte fixture and is intended to run on every codex-cli upgrade and once per nightly batch (NOT in unit-test CI, to avoid credit consumption); (c) the regression-guard test on the fix branch ensures `--no-interactive` cannot resurface — this is the durable Level-2 enforcement per `.claude/rules/patterns.md`.

3. **"Why not just pin codex-cli to a known-good version in `package.json` or a setup script?"** — pinning was considered and rejected for v1: the workspace runs codex-cli as a global npm install across multiple operator machines (Linux + Windows), and pinning would require a `npm install -g @openai/codex@X.Y.Z` line in machine bootstrap that does not exist today. The probe is the lighter-weight surface: it does not change install state, it just tells the wrapper to fail fast. A follow-up issue can promote pinning to a setup-script change once the operator surface is unified (out of scope for this plan).

4. **"What if the probe itself hangs (e.g., `codex --version` regression)?"** — the probe wraps `codex --version` in a 5s `timeout`; on timeout it returns rc=2 (MISSING) — the same code path as missing-binary, which produces a fast UNAVAILABLE stub rather than blocking the fanout. Test `test_check_codex_version_malformed_output` covers this.

5. **"Why not detect the hang dynamically by reading codex stderr for the `Reading additional input from stdin...` token instead of version-gating?"** — considered and noted as a complementary v2 enhancement. v1 prefers the version probe because it is deterministic, fast (≤5s), and does not require speculatively running `codex exec` (which is exactly the operation the regression breaks). A follow-up issue will be filed proposing stderr-based detection as a defense-in-depth layer if a future regression manifests outside the version blocklist.

6. **"The plan claims 0.125.0 works — is that asserted on a single artifact, or is the evidence solid?"** — four post-0.125 codex artifacts (`2026-04-25-plan-2487-codex.md`, `2026-04-25-plan-2488-codex.md`, `2026-04-26-plan-2488-codex.md`, `2026-04-26-plan-2489-codex.md`) all contain real verdict blocks (`MAJOR` with retrieval citations), not UNAVAILABLE stubs. The acceptance criterion adds a live smoke test that re-validates this on the implementing operator's machine before the merge lands.

---

## Risks and Open Questions

- **Risk:** if `fix/codex-stdin-hang` falls behind `main` materially before merge, the rebase may conflict with unrelated wrapper changes. Mitigation: rebase the fix branch on current `main` as the first action item; the branch is small (2 files, +21/-4) and conflicts will be obvious.
- **Risk:** codex-cli ships a 0.126.x release that re-breaks `codex exec` differently. Mitigation: probe's WARN-on-untested behavior surfaces this in artifact metadata; live smoke test (run on upgrade) will trip the acceptance gate before the version makes it into KNOWN_GOOD.
- **Risk:** operators may run a stale codex-cli on a different machine without re-running the probe in their setup. Mitigation: probe is invoked at fanout time, not install time, so every batch picks it up.
- **Risk:** the "size-dependent" framing in the issue title is misleading per the issue body itself — the hang reproduces on a 90-byte plan in 0.124.0. The plan does not chase a size-based heuristic; it gates on version. This is intentional and consistent with the issue's own root-cause section.
- **Open:** does the user want to reopen #2406 to leave a public superseded-by-#2479 marker, or leave it closed-as-fixed? The plan is neutral; the fix-branch commit message and this plan both reference #2406 explicitly.
- **Open:** should the probe's KNOWN_GOOD list live in the script or in a YAML config under `config/ai-tools/`? The plan assumes the script for v1 simplicity; promoting to YAML is straightforward later.
- **Open:** is a 5s timeout on `codex --version` enough on slow CI runners? The plan can raise this to 15s without affecting normal-path latency materially.

---

## Complexity: T2

**T2** — small surface (2 new scripts, 2 new test files, 2 modified files, 1 branch merge) with TDD coverage; one in-flight branch must be respected; no architectural changes; the most complex piece is the version-class matrix in the probe, which is mechanical.
