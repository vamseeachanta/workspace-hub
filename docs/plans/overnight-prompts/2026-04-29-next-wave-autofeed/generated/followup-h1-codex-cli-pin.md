# Follow-up draft (H1) — Pin codex-cli to 0.123.0 in Hermes preflight

> **Status:** DRAFT. Not filed. Per #2557 report's own duplicate-of analysis, H1 is "likely covered by [#2479](https://github.com/vamseeachanta/workspace-hub/issues/2479)". **Recommendation: comment on #2479 with the preflight pin proposal rather than file a new issue.**
>
> **Plan #2557 r1 review caveat (Finding 5):** the pin only restores Codex for plain-terminal invocations; per `feedback_codex_cli_0_124_upstream_regression.md` (verified 2026-04-24), 0.123.0 also hangs from inside Claude Code's Bash tool, so Hermes-dispatched lanes are NOT unblocked by this hack alone. The owner-time-impact framing in the parent report (≈2-3h/week recovered) reflects un-sandboxed-terminal usage only. Reflect that scope in any comment/filing.

## Title (if filed as new issue)

`feat(hermes): pin codex-cli to 0.123.0 in Hermes preflight (un-sandboxed terminal scope)`

## Body

### Summary

Hermes preflight should refuse to dispatch any Codex review or Codex-implementation lane unless `codex --version` reports `0.123.0`. The 0.124.0 stdin-hang regression (#2479) blocks every `codex exec` invocation; pinning the version at preflight time prevents wasted dispatch attempts.

### Why this is bounded

- Single script change: add a version-gate to `scripts/hermes/preflight.sh` and to `scripts/review/submit-to-codex.sh`.
- No new tooling, no new dependencies.
- Reversible by reverting the gate.

### Scope caveat (READ BEFORE FILING)

Per `feedback_codex_cli_0_124_upstream_regression.md` (verified 2026-04-24 session): downgrade to 0.123.0 also hangs from inside Claude Code's Bash tool. The pin is therefore meaningful **only for invocations that originate from a plain user terminal** (operator-driven cross-review runs). Hermes-dispatched provider lanes that run inside Claude Code agent sessions remain blocked until the upstream regression is fixed.

Owner-time-impact estimate from the #2557 report (≈2-3h/week recovered) reflects the operator-driven surface only.

### Implementation sketch

```bash
# scripts/hermes/preflight.sh — add near the top
require_codex_version() {
  local want="0.123.0"
  local got
  got="$(codex --version 2>/dev/null | awk '{print $NF}')" || true
  if [[ "$got" != "$want" ]]; then
    echo "Hermes preflight: codex-cli must be ${want} (got: ${got:-not installed}). See #2479." >&2
    echo "Fix: npm install -g @openai/codex@${want}" >&2
    return 1
  fi
}
require_codex_version || exit 1
```

Mirror in `scripts/review/submit-to-codex.sh` — exit early with a structured error if the gate fails.

### Acceptance criteria

- [ ] `scripts/hermes/preflight.sh` rejects dispatch when codex-cli version != 0.123.0, with `#2479` cited in the rejection message.
- [ ] `scripts/review/submit-to-codex.sh` carries the same gate.
- [ ] CHANGELOG / runbook entry notes the scope caveat (un-sandboxed terminal only).
- [ ] Issue body links back to #2479 with the preflight-pin proposal.

### Recommended action (NOT filing)

Operator should:
1. Run `gh issue comment 2479 --body-file docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/generated/followup-h1-codex-cli-pin.md` (or just paste the relevant section) **after** removing this DRAFT header.
2. Decide whether to also file a separate Hermes-side preflight issue, or fold the work into #2479's existing scope.

## Duplicate-of check (2026-04-29)

- [#2479](https://github.com/vamseeachanta/workspace-hub/issues/2479) — `fix(review): Codex stdin-hang regression post-#2406 closure (size-dependent)` — OPEN. Direct match for the upstream defect. **Most likely home for H1's preflight pin proposal.**
- No other issue currently scopes the preflight version-gate.

Verdict: NOT SAFE to file as new issue. **Comment on #2479 instead.**
