> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_gemini_trust_env_blocks_reviews.md

---
name: Gemini CLI trusted-directory check silently breaks headless reviews
description: Gemini CLI added a trusted-directory security check that exits 55 with no structured output in headless environments, manifesting as persistent "Gemini returned NO_OUTPUT" in cross-review pipelines. Fix is a one-liner export. Durable fix landed in submit-to-gemini.sh on 2026-04-24.
type: feedback
originSessionId: 5b5fa564-d428-4456-ad9a-5bab022aefa8
---
Gemini CLI now refuses to run in "untrusted" directories by default. In headless mode (no interactive trust prompt), this surfaces as exit 55 with stderr:

```
Gemini CLI is not running in a trusted directory. To proceed, either use `--skip-trust`,
set the `GEMINI_CLI_TRUST_WORKSPACE=true` environment variable, or trust this directory
in interactive mode.
```

The `submit-to-gemini.sh` wrapper suppressed this stderr before the fix, so the failure mode looked like generic flakiness: `# Gemini returned NO_OUTPUT` (wrapper-generated placeholder, not a real empty response from Gemini). That made it easy to misdiagnose as independent API flakiness for days.

**Why:** Google added this check as a workspace-trust hardening feature. It fires regardless of whether the directory is a git repo or has any other trust signal — it needs an explicit opt-in.

**How to apply:**
- The durable fix is in `scripts/review/submit-to-gemini.sh` near the top:
  ```
  export GEMINI_CLI_TRUST_WORKSPACE="${GEMINI_CLI_TRUST_WORKSPACE:-true}"
  ```
  Any future caller of that script (cross-review.sh, direct invocations, CI) inherits the trust automatically. Callers can still override by pre-exporting a different value.
- If future Gemini NO_OUTPUT symptoms reappear: FIRST check whether the wrapper is still suppressing the real stderr. Run `submit-to-gemini.sh` directly and inspect the exit code + stderr before assuming API flakiness.
- Exit 55 is not documented anywhere in the Gemini CLI README — it's a "trust rejection" code specific to this check.
- This fix does NOT affect the Codex stdin-hang (unrelated issue, tracked in #2479) or the `cross-review.sh` path-guard bug (separate, also fixed in this same 2026-04-24 session).
- If running Gemini in a context where the workspace really IS untrusted (external contributor sandbox, etc.), the caller should pre-export `GEMINI_CLI_TRUST_WORKSPACE=false` AND expect reviews to fail — the self-default only provides the permissive behavior for in-workspace tooling.

**Diagnostic shortcut:** if you see `# Gemini returned NO_OUTPUT` as the entire gemini result file (28 bytes), immediately check whether the `.raw.md` sidecar contains "Gemini review failed" (wrapper stub). If it does, run `submit-to-gemini.sh` directly on the same input to surface the real stderr.
