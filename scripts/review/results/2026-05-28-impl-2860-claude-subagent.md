# Code-stage adversarial review — #2860 Hermes consistency probe

> **Stage:** code/artifact (implementation) · **Issue:** [#2860](https://github.com/vamseeachanta/workspace-hub/issues/2860) · **PR:** #2861 · **Date:** 2026-05-28 · **Complexity:** T1
> **Artifact:** `scripts/readiness/hermes-consistency-check.sh`

## Provenance / method

Cross-provider Codex/Gemini dispatch is unavailable from a Claude-Code session (`CLAUDECODE=1` trips `submit-to-codex`; Gemini trust-folder gate). Per the documented fallback (`feedback_permission_gate_blocks_cross_review`, SHARED_SOUL "use subagents for parallel work where the runtime supports it"), the code-stage adversarial review was performed by **two independent fresh-context Claude-Code subagents** (no visibility into the author's reasoning), each prompted to hunt defects and default to non-APPROVE. Main session then **empirically verified** every actionable finding before applying fixes (`feedback_verify_subagent_firewall_claims`, subagent-write-phantom hazard).

## Round 1 (initial review)

The first subagent was inadvertently pointed at a **stale untracked copy** of the script in the dirty working tree, not the PR-branch version. It reported 3 BLOCKER/MAJOR comment-blindness findings. Main-session verification (`/tmp` config fixtures) confirmed the *stale copy* was comment-blind — but a diff against the PR branch showed the **PR-branch version already carried the comment-strip fix** (lines 91–100, `CFG_ACTIVE=$(grep -vE '^\s*#' ...)`). Those 3 findings were therefore already resolved on the artifact under review. Lesson recorded: review the merge-target ref, not a working-tree copy.

Findings that **did** apply to the PR-branch version and were fixed:

| # | Sev | Site | Defect | Fix |
|---|-----|------|--------|-----|
| 4 | MAJOR | repo-sync | `git fetch origin $br` on a local-only branch → bogus "? commits behind" WARN | Guard on `git ls-remote --exit-code --heads origin "$br"`; distinguish behind=0 / "?" / N / not-on-origin |
| 5 | MAJOR | color helpers | ANSI escapes with no TTY guard → garbled CI/redirected/Windows output | Gate color on `[ -t 1 ] && [ -z "${NO_COLOR:-}" ]`; `printf '%b'` with empty vars when non-TTY |
| 7 | MINOR | SOUL section | comparison silently skipped if canonical SOUL absent → falsely-clean section | added `else wn "canonical SOUL not found ..."` |
| 9 | MINOR | SOUL diff | `diff -q` flags CRLF-vs-LF as DIFFERS on Windows (false FAIL) | CRLF-insensitive `diff <(tr -d '\r' < a) <(tr -d '\r' < b)` |
| 10 | NIT | bridges | message asserted "+ -win variant" without checking it; `\b` also matched base id inside `-win` | check base AND `-win` explicitly; anchor with `([[:space:]]|$)` |
| 11 | NIT | header | `hostname` absent on minimal Git Bash | fall back to `$COMPUTERNAME` then "unknown" |

## Round 2 (re-review of the fixed file)

Second subagent re-reviewed the fixed artifact. **Verified all 6 edits functionally correct** (no format-injection via `%b`/positional `%s`; pipefail does not abort on no-match command substitutions; `<(...)` works on Git Bash; ls-remote-success-but-rev-list-fail handled honestly; CRLF compare correct). Found 2 **LOW** items, both in the newly-written bridge grep: not start-anchored, so a commented `# id: ...` or a longer key (`grid:`) could match. Fixed by anchoring to the YAML list-item form `^[[:space:]]*-?[[:space:]]*id:[[:space:]]*<id>([[:space:]]|$)`. Main-session re-verified: anchor matches all four live ids, rejects `# id:` and `grid:` negatives, bridges section still PASS.

## Verification evidence

- `bash -n` clean (both rounds).
- Live smoke-run on ace-linux-1 (read-only): PASS=15 WARN=3 FAIL=1, exit 1. Colors correctly suppressed when piped. Sync-check correctly WARNs (local-only worktree branch) instead of bogus behind-count. Both bridge `-win` variants detected.
- **Material downstream finding:** the fixed routing checks report ace-linux-1 routing as **compliant** (no OpenRouter / no `provider: auto` on active lines). Direct inspection of `~/.hermes/config.yaml` confirms *zero* references (not even commented). The handoff's "config.yaml still references OpenRouter + provider:auto" was a **false positive from the pre-fix comment-blind probe** — not a real regression (#2841 step-3 routing item resolved). The SOUL.md copy-not-symlink + DIFFERS drift, by contrast, is **real** and confirmed.

## Verdict

Both rounds' actionable findings applied and re-verified. Read-only guarantee holds (only `git ls-remote`/`fetch` of remote-tracking refs). No secret values printed. **APPROVE for merge** pending owner action.
