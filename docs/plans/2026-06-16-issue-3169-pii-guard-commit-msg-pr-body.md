# Plan for #3169: PII guard — extend coverage to commit messages + PR bodies

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-06-16
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3169
> **Client:** N/A
> **Project:** (none)
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-16-plan-3169-claude.md (+ codex/gemini if T2 dispatch run)

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/legal/check-client-pii.py` — guard reusing the redactor engine; CLI surface is `--map`, `--base-ref`, `--staged`, `--all`, positional `paths`. **Scans files only** (line 88 already does `_engine.redact_text(line, rules)` per line, so a text-scanning primitive exists but is not exposed for arbitrary text). **Gap:** no `--message-file`/`--stdin` mode → commit messages and PR bodies cannot be fed to it.
- Found: `scripts/legal/redact-client-pii.py` — `redact_text(text, rules)` engine; name-agnostic, reads private map. This is the reuse point (guard ≡ redactor).
- Found: `.github/workflows/legal-client-pii-gate.yml` — `pull_request` gate; materializes the `LEGAL_CLIENT_MAP` secret to a temp file, runs `check-client-pii.py --base-ref origin/<base> --strict`, withholds values in the public log. **Gap:** scans only the file diff; not the PR title/body, not commit messages.
- Found: `.pre-commit-config.yaml` — `legal-client-pii` hook runs `--staged` (file content). The framework **already uses the `commit-msg` stage** (header line `pre-commit install --hook-type commit-msg`; the `commitizen` hook declares `stages: [commit-msg]`). **Gap:** no PII hook on the `commit-msg` stage.

### Standards
Not applicable (tooling/governance issue).

### LLM Wiki pages consulted
No relevant wiki pages (workspace-hub-internal tooling).

### Documents consulted
- `.claude/docs/client-pii-prevention.md` — the #3099 prevention doc; will be extended to declare commit messages + PR metadata in-scope and recommend squash-merge.
- Epic `analysis/3095-epic-closeout.md` + issue #3169 — record the gap and the merge-commit residue that motivated this.
- `.claude/rules/patterns.md` — enforcement gradient (prose→script→hook); this work adds a Level-2 text mode + Level-3 `commit-msg` hook + the CI (server-side) extension.

### Gaps identified
- No text/stdin scan mode in the guard.
- No `commit-msg`-stage hook.
- CI does not scan PR title/body or PR-range commit messages.
- Prevention doc does not name commit messages / PR metadata as in-scope surfaces.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-16 via `gh issue view`):
- `#3169` — OPEN — "PII guard: extend coverage to commit messages + PR bodies (gap found in #3098 closeout)"
- `#3095` — CLOSED — epic (file-content objective met)

**File existence** (`ls` 2026-06-16):
- EXISTS: `scripts/legal/check-client-pii.py`, `scripts/legal/redact-client-pii.py`, `.github/workflows/legal-client-pii-gate.yml`, `.pre-commit-config.yaml`, `.claude/docs/client-pii-prevention.md`, `scripts/legal/tests/test_check_client_pii.py`
- MISSING (this plan creates): a `commit-msg` hook entry + a guard text mode + CI steps + tests for them

**Line excerpts** (guard CLI surface, `grep add_argument scripts/legal/check-client-pii.py`):
```
97: --base-ref   98: --staged   99: --all   101: paths (nargs=*)
# no --message-file / --stdin
```

**Reproduction proofs** (Step 1.5 — the gap is empirically real, observed this session):
```
# The #3098 closeout merged with short client tokens in two commit MESSAGES while
# the file-content guard reported clean throughout:
$ git log origin/main~8..origin/main --format='%B' | grep -ic '<client-token>'
<nonzero>           # tokens present in main commit-message history
$ uv run python scripts/legal/check-client-pii.py --all
✓ legal-client-pii: 21356 changed file(s) clean.   # file content clean — guard never saw the messages
```
- Reproduced at: 2026-06-16 (this session).
- Failure mode matches issue claim: YES — the guard scans file content only; commit messages and PR metadata are unscanned public surfaces.

<!-- distinct sources: issue #3169 + check-client-pii.py + CI workflow + .pre-commit-config.yaml + prevention doc = 5 (≥3) -->

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

---

## Deliverable

The client-PII guard scans **commit messages and PR titles/bodies** (not just file content): a `commit-msg` pre-commit hook blocks a local commit whose message contains a client identifier, and the CI gate fails a PR whose title, body, or any commit message in range contains one — all reusing the existing engine and withholding matched values from public logs.

---

## Pseudocode

```
# check-client-pii.py — new text mode (reuses _engine.redact_text)
add args: --message-file PATH  (mutually exclusive-ish with file modes)
          --stdin               (read text from stdin)
scan_text(text, rules):
    _, n = engine.redact_text(text, rules)     # n>0 => contains an identifier
    if n: print "client identifier in <source> (value withheld)"; return 1
    return 0
# source label = the arg name only (never the matched text)

# CI workflow — after the existing diff scan, add:
printf '%s\n%s' "$PR_TITLE" "$PR_BODY" | check-client-pii.py --stdin --strict
git log --format=%B "origin/$BASE..HEAD" | check-client-pii.py --stdin --strict
# PR_TITLE/PR_BODY from github.event.pull_request.{title,body} via env (not interpolated into shell)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | scripts/legal/check-client-pii.py | add `--message-file` + `--stdin` text-scan mode (engine reuse; withholds values) |
| Modify | scripts/legal/tests/test_check_client_pii.py | TDD for the text mode (synthetic names only) |
| Modify | .pre-commit-config.yaml | add `legal-client-pii-commit-msg` hook on `stages: [commit-msg]` running `--message-file` |
| Modify | .github/workflows/legal-client-pii-gate.yml | scan PR title+body and PR-range commit messages via `--stdin --strict` |
| Modify | .claude/docs/client-pii-prevention.md | declare commit messages + PR metadata in-scope; recommend squash-merge for transient-token branches |
| Update | docs/plans/README.md | index this plan |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_text_mode_clean_passes | clean text exits 0 | "fix(x): refactor loader" | exit 0, no match |
| test_text_mode_detects_identifier | synthetic client token in text → exit nonzero | "rename betacorp dir" (synthetic map) | nonzero, value withheld |
| test_text_mode_withholds_value | matched text never printed | text w/ synthetic token | stdout/stderr contain neither the token nor codename |
| test_message_file_reads_path | `--message-file` reads file content | temp file w/ token | nonzero |
| test_stdin_mode_reads_stdin | `--stdin` reads piped text | piped token | nonzero |
| test_text_mode_degrade_open_no_map | missing map + non-strict → exit 0 (warn) | any text, no map | exit 0 |
| test_text_mode_strict_no_map | missing map + `--strict` → exit 2 | any text | exit 2 |

---

## Acceptance Criteria

- [ ] New tests pass: `uv run pytest scripts/legal/tests/test_check_client_pii.py -v`
- [ ] No regression: existing guard/redactor tests still pass.
- [ ] `commit-msg` hook blocks a commit whose message contains a synthetic identifier; passes a clean one (manual: `echo "msg" | uv run python scripts/legal/check-client-pii.py --stdin --map <synthetic>`).
- [ ] CI workflow YAML lints/parses; PR title/body + commit-range messages are scanned with `--strict`; values withheld from `$GITHUB_STEP_SUMMARY` and logs.
- [ ] Engine parity preserved (guard still ≡ redactor; no second name list introduced).
- [ ] `.claude/docs/client-pii-prevention.md` updated; squash-merge recommendation documented.
- [ ] Review artifacts posted to scripts/review/results/.

---

## Adversarial Review Summary

<!-- Inline Claude adversarial pass (r1); T2 expects a 2nd provider (Codex) at review time. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (r1, inline) | MINOR | (1) **Leak-via-CI risk:** PR title/body must reach the guard via **env vars**, never shell-interpolated into the `run:` script, or a malicious/odd PR title could break the step or echo. (2) **Withhold invariant:** the text mode must print only the source label + line/offset, never the matched substring — add an explicit test asserting absence. (3) **commit-msg hook scope:** must read `$1` (the message file arg) and degrade-open if the map is absent (parity with `--staged`), else every local commit breaks on unprovisioned hosts. (4) **Merge-method gap:** the hook/CI catch *new* messages, but a merge-commit can still carry a feature-branch message into main — so the doc must recommend squash-merge, and CI should scan the full PR-range messages (not just HEAD). |
| Codex | (pending T2 dispatch) | |
| Gemini | (n/a unless T3) | |

**Overall result:** PASS (draft ready for user review; T2 second-provider review can run on request)

Revisions folded in from r1: env-var passing for PR metadata; explicit withhold test; degrade-open commit-msg hook; squash-merge doc + full-range commit scan.

---

## Risks and Open Questions

- **Risk:** PR title/body containing shell metacharacters — mitigated by passing via env vars, not interpolation.
- **Risk:** `commit-msg` hook adds latency/footgun on unprovisioned hosts — mitigated by degrade-open when the map is absent (same as the existing `--staged` hook); bypass remains `LEGAL_PII_ALLOW=1`.
- **Risk:** CI cannot rewrite history for an already-merged leaky message — by design out of scope (HEAD-only); this is *prevention* for future PRs.
- **Open (for approval):** Should the `commit-msg` hook be added to `default_install_hook_types` so `pre-commit install` wires it automatically, or left opt-in (`--hook-type commit-msg`)? Recommend auto-wire for consistency.
- **Open (for approval):** Make the CI title/body/message scan **blocking** (`--strict`, like the diff scan) or **warn-only** for a soft-launch? Recommend blocking, matching the existing gate posture.

---

## Complexity: T2

**T2** — multi-file (guard + tests + pre-commit config + CI workflow + docs), TDD required, no cross-provider/systemic change. Lane: claude (light tooling code).
