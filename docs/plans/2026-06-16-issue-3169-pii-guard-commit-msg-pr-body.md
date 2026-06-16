# Plan for #3169: PII guard — extend coverage to commit messages + PR bodies

> **Status:** adversarial-reviewed → plan-review (awaiting user approval)
> **Complexity:** T2
> **Date:** 2026-06-16
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3169
> **Client:** N/A
> **Project:** (none)
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-16-plan-3169-{claude,codex,gemini,disagreement}.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/legal/check-client-pii.py` — guard reusing the redactor engine; CLI is `--map`, `--base-ref`, `--staged`, `--all`, positional `paths`. **Scans files only** (line ~88 already does `_engine.redact_text(line, rules)` per line). **Gap:** no text/stdin mode → commit messages and PR bodies can't be fed in.
- Found: `scripts/legal/redact-client-pii.py` — `redact_text(text, rules)`; name-agnostic. Reuse point (guard ≡ redactor).
- Found: `.github/workflows/legal-client-pii-gate.yml` — `pull_request` gate, types `[opened, synchronize, reopened]`; materializes `LEGAL_CLIENT_MAP` secret → `$RUNNER_TEMP/client-map.yaml`, exports it to `$GITHUB_ENV`, runs `check-client-pii.py --base-ref origin/<base> --strict`. **Gaps:** (a) scans only the file diff, (b) no `edited` trigger so a post-open title/body edit isn't re-scanned.
- Found: `.pre-commit-config.yaml` — `legal-client-pii` hook runs `--staged`. The framework **already uses the `commit-msg` stage** (commitizen `stages: [commit-msg]`; header documents `pre-commit install --hook-type commit-msg`). No `default_install_hook_types`. **Gaps:** no PII hook on `commit-msg`; commit-msg stage not auto-installed.
- Found: `scripts/legal/legal-sanity-scan.sh` — repo legal/security hard-gate script (must be in acceptance for a legal-tooling change).

### Standards
Not applicable (tooling/governance issue).

### LLM Wiki pages consulted
No relevant wiki pages (workspace-hub-internal tooling).

### Documents consulted
- `.claude/docs/client-pii-prevention.md` — #3099 prevention doc; will declare commit messages + PR metadata in-scope + recommend squash-merge.
- `analysis/3095-epic-closeout.md` + issue #3169 — record the gap + the merge-commit residue that motivated this.
- `.claude/rules/patterns.md` — enforcement gradient; this adds a Level-2 text mode + Level-3 `commit-msg` hook + the server-side CI extension.

### Gaps identified
- No text/stdin scan mode in the guard.
- No `commit-msg`-stage hook; commit-msg stage not auto-wired.
- CI does not scan PR title/body or PR-range commit messages, and does not re-run on PR `edited`.
- Prevention doc does not name commit messages / PR metadata as in-scope surfaces.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-16 via `gh issue view`):
- `#3169` — OPEN — "PII guard: extend coverage to commit messages + PR bodies" (label `status:plan-review`)
- `#3095` — CLOSED — epic (file-content objective met)

**File existence** (`test -f` 2026-06-16 — rebuts Gemini r2 #1, which claimed these don't exist):
- EXISTS + tracked on `main`: `scripts/legal/check-client-pii.py`, `scripts/legal/redact-client-pii.py`, `.pre-commit-config.yaml`, `.github/workflows/legal-client-pii-gate.yml`, `scripts/legal/tests/test_check_client_pii.py`, `scripts/legal/legal-sanity-scan.sh`
- MISSING (this plan creates): the guard text mode, the `commit-msg` hook entry, the CI metadata/commit-message steps, and their tests

**Line excerpts** (guard CLI surface):
```
--base-ref / --staged / --all / paths(nargs=*)   # no --message-file / --stdin
```
(workflow trigger) `.github/workflows/legal-client-pii-gate.yml:18-21` → `types: [opened, synchronize, reopened]` (no `edited`).

**Reproduction proofs** (Step 1.5 — the gap is empirical, observed this session):
```
# #3098 closeout merged with short client tokens in two commit MESSAGES while the
# file-content guard reported clean throughout:
$ git log origin/main~8..origin/main --format='%B' | grep -ic '<client-token>'
<nonzero>                                          # tokens in main commit-message history
$ uv run python scripts/legal/check-client-pii.py --all
✓ legal-client-pii: 21356 changed file(s) clean.  # file content clean — guard never saw the messages
```
- Reproduced at: 2026-06-16 (this session). Failure mode matches the issue claim: YES.

<!-- distinct sources: issue #3169 + check-client-pii.py + CI workflow + .pre-commit-config.yaml + prevention doc + legal-sanity-scan.sh = 6 (≥3) -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-06-16-issue-3169-pii-guard-commit-msg-pr-body.md |
| Guard text mode | scripts/legal/check-client-pii.py (modify) |
| Tests | scripts/legal/tests/test_check_client_pii.py (extend) |
| Pre-commit hook | .pre-commit-config.yaml (modify) |
| CI extension | .github/workflows/legal-client-pii-gate.yml (modify) |
| Docs | .claude/docs/client-pii-prevention.md (modify) |
| Plan reviews | scripts/review/results/2026-06-16-plan-3169-{claude,codex,gemini,disagreement}.md |

---

## Deliverable

The client-PII guard scans **commit messages and PR titles/bodies** in addition to file content, **blocking** on a match (`--strict`), reusing the existing engine and withholding matched values from public logs:
- a `commit-msg` pre-commit hook (auto-wired via `default_install_hook_types`) blocks a local commit whose message contains an identifier;
- the CI gate (re-triggered on PR `edited`) fails a PR whose title, body, or **any individual commit message in range** (scanned per-commit so the offending SHA is named) contains one.

---

## Pseudocode

```
# check-client-pii.py — new text mode (reuses _engine.redact_text)
add args: --message-file PATH   --stdin   --source LABEL   (LABEL = "commit <sha>" | "PR title" | "stdin")
scan_text(text, rules, label):
    _, n = engine.redact_text(text, rules)      # n>0 => contains an identifier
    if n: print f"client identifier in {label} (value withheld)"; return 1   # never print the match
    return 0
# map sourcing + degrade-open identical to the file path: --map defaults to $LEGAL_CLIENT_MAP;
# absent map + non-strict => warn+exit 0; absent map + --strict => exit 2.

# CI workflow — explicit --map "$LEGAL_CLIENT_MAP" on every call (Gemini #3); add `edited` trigger (Codex #1):
on.pull_request.types: [opened, synchronize, reopened, edited]
# PR metadata via env (never shell-interpolated) — Claude r1 #1:
env: PR_TITLE: ${{ github.event.pull_request.title }} ; PR_BODY: ${{ github.event.pull_request.body }}
printf '%s\n%s' "$PR_TITLE" "$PR_BODY" | check-client-pii.py --stdin --source "PR metadata" --map "$LEGAL_CLIENT_MAP" $STRICT
# per-commit so the offending SHA is identifiable (Gemini #2):
for sha in $(git rev-list "origin/$BASE..HEAD"); do
    git log -1 --format=%B "$sha" | check-client-pii.py --stdin --source "commit $sha" --map "$LEGAL_CLIENT_MAP" $STRICT || fail=1
done
# $STRICT is "--strict" when the secret is present (mirrors the existing diff-scan step) => blocking.
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | scripts/legal/check-client-pii.py | add `--message-file` + `--stdin` + `--source` text-scan mode (engine reuse; withholds values; same map/degrade-open semantics) |
| Modify | scripts/legal/tests/test_check_client_pii.py | TDD for text mode **and** a real `commit-msg` hook-path test (synthetic names only) |
| Modify | .pre-commit-config.yaml | add `legal-client-pii-commit-msg` hook on `stages: [commit-msg]` running `--message-file "$1"` (degrade-open); add `default_install_hook_types: [pre-commit, commit-msg]` so it auto-installs |
| Modify | .github/workflows/legal-client-pii-gate.yml | add `edited` trigger; scan PR title+body (via env) and per-commit messages with explicit `--map` + `$STRICT` |
| Modify | .claude/docs/client-pii-prevention.md | declare commit messages + PR metadata in-scope; recommend squash-merge for transient-token branches |
| Update | docs/plans/README.md | index this plan |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_text_mode_clean_passes | clean text exits 0 | "fix(x): refactor loader" | exit 0 |
| test_text_mode_detects_identifier | synthetic token → nonzero | "rename betacorp dir" (synthetic map) | nonzero |
| test_text_mode_withholds_value | matched text never emitted | text w/ synthetic token | output contains neither token nor codename |
| test_text_mode_source_label | `--source` label appears, value does not | token + `--source "commit abc123"` | "...in commit abc123 (value withheld)" |
| test_message_file_reads_path | `--message-file` reads file | temp file w/ token | nonzero |
| test_stdin_mode_reads_stdin | `--stdin` reads pipe | piped token | nonzero |
| test_text_mode_degrade_open_no_map | missing map + non-strict → exit 0 | any text, no map | exit 0 (warn) |
| test_text_mode_strict_no_map | missing map + `--strict` → exit 2 | any text | exit 2 |
| test_commit_msg_hook_blocks | the actual `commit-msg` hook path (`$1`/`--message-file`) blocks a dirty message and passes a clean one | run hook against temp message files | dirty→nonzero, clean→0 |

---

## Acceptance Criteria

- [ ] New tests pass: `uv run pytest scripts/legal/tests/test_check_client_pii.py -v`
- [ ] No regression: existing guard/redactor tests still pass.
- [ ] **Real commit-msg hook check** (not just `--stdin`): `pre-commit run legal-client-pii-commit-msg --hook-stage commit-msg --commit-msg-filename <tmp>` blocks a dirty message, passes a clean one.
- [ ] CI YAML parses; trigger includes `edited`; PR title/body + per-commit messages scanned with explicit `--map` + `$STRICT`; values withheld from `$GITHUB_STEP_SUMMARY`/logs; a violation names the offending commit SHA.
- [ ] Engine parity preserved (guard ≡ redactor; no second name list).
- [ ] **Legal/security gate:** `bash scripts/legal/legal-sanity-scan.sh` passes on the change (repo hard-gate #6).
- [ ] `.claude/docs/client-pii-prevention.md` updated; squash-merge recommendation documented.
- [ ] Review artifacts present in scripts/review/results/ (claude/codex/gemini/disagreement).

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (r1, inline) | MINOR | CI shell-injection via PR metadata (env-pass); withhold-invariant test; degrade-open commit-msg hook; merge-method/squash gap — all folded pre-dispatch. |
| Codex (r2) | MAJOR | (1) workflow lacks `edited` trigger → post-open title/body edits unscanned; (2) blocking-vs-warn contradiction; (3) false PASS + missing claude artifact; (4) issue label ahead of review state; (5) acceptance tested `--stdin`, not the real `--message-file`/`$1` hook; (6) auto-wire undecided but "blocked" claimed; (7) `legal-sanity-scan.sh` missing from acceptance. |
| Gemini (r2) | MAJOR | (1) **REJECTED** — claimed cited files don't exist; disproven via `test -f` + `git ls-files` (all present + tracked); (2) piping all commit messages loses the offending SHA; (3) CI snippet should pass `--map` explicitly. |

**Overall result (pre-revision):** FAIL — both dispatched providers MAJOR.
**Overall result (post-r3 revision):** PASS — all valid findings folded inline (no re-dispatch, per `feedback_r3_inline_loop_break_pattern`).

**r3 revisions made (this draft):**
- Added `edited` to the workflow trigger (Codex #1).
- Resolved the control to **blocking** end-to-end; removed the warn/blocking ambiguity (Codex #2).
- Wrote `scripts/review/results/2026-06-16-plan-3169-claude.md`; corrected the verdict trail; no false PASS (Codex #3).
- Reconciled status (`adversarial-reviewed → plan-review`) with the actual review state (Codex #4).
- Added a real `commit-msg` hook-path test + acceptance check (Codex #5).
- Decided **auto-wire** via `default_install_hook_types` so the "local commit blocked" claim holds (Codex #6).
- Added `legal-sanity-scan.sh` to acceptance (Codex #7).
- Per-commit scan with SHA label (Gemini #2); explicit `--map "$LEGAL_CLIENT_MAP"` in CI (Gemini #3).
- Rejected Gemini #1 with embedded file-existence evidence.

---

## Risks and Open Questions

- **Risk:** PR title/body with shell metacharacters → mitigated by env-var passing, not interpolation.
- **Risk:** `commit-msg` hook footgun on unprovisioned hosts → mitigated by degrade-open when the map is absent (parity with `--staged`); bypass `LEGAL_PII_ALLOW=1`.
- **Risk:** already-merged leaky messages can't be rewritten → out of scope (HEAD-only); this is prevention for future PRs, paired with the squash-merge recommendation.
- **Decided (confirm at approval):** auto-wire `commit-msg` via `default_install_hook_types` (so blocking is guaranteed); CI metadata/message scan is **blocking** (`--strict`, matching the existing gate). Both were open questions in the draft; resolved per Codex #2/#6. Flag if you prefer warn-only / opt-in.

---

## Complexity: T2

**T2** — multi-file (guard + tests + pre-commit config + CI workflow + docs), TDD required, no cross-provider/systemic runtime change. Lane: claude.
