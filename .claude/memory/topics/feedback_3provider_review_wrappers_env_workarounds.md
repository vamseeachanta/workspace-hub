> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-05
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_3provider_review_wrappers_env_workarounds.md

---
name: feedback_3provider_review_wrappers_env_workarounds
description: How to run the 3-provider adversarial review wrappers (Codex/Gemini) from inside a Claude Code session on ace-linux-1
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 385fd1bf-9a54-47c7-b22d-573740acede8
---

Running `scripts/review/submit-to-codex.sh` / `submit-to-gemini.sh` from a Claude Code Bash tool on ace-linux-1 fails by default — both for ENV reasons, not plan/code reasons:

- **Codex**: `codex exec` stdin-hangs when the `CLAUDECODE` env var is set (upstream openai/codex#19945; wshub #2684). Wrapper reports `CODEX_INCOMPATIBLE_VERSION`. **Fix:** dispatch with `env -u CLAUDECODE bash scripts/review/submit-to-codex.sh …` (or run `scripts/review/plan-review-fanout.sh` from a plain terminal).
- **Gemini**: `gemini --yolo` refuses an untrusted dir (the wrapper runs in an isolated `mktemp -d`) → exit 55 "not running in a trusted directory." **Fix:** `GEMINI_CLI_TRUST_WORKSPACE=true` (or `--skip-trust`).

Both wrappers take `--file <path> --prompt <text>` and emit the SAME structured JSON schema (verdict/issues_found/suggestions/questions) via `render-structured-review.py` + `validate-review-output.sh` — works fine for reviewing a PLAN doc, not just code/diffs. Run them with `nohup … &` (Codex can take 100s+); poll for completion.

**Caveat learned 2026-06-15 (#3116):** because the wrappers FORCE the output schema regardless of provider, "all providers produced valid JSON" proves the wrapper works, NOT that agent behavior is portable — never use schema-conformance as an equivalence acceptance bar; use a planted-defect oracle. See [[project_skill_retirement_blocked_on_invocation_signal]] for adjacent provider-portability work.
