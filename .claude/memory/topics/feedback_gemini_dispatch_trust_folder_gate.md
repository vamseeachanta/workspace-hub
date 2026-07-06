> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-05
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_gemini_dispatch_trust_folder_gate.md

---
name: feedback_gemini_dispatch_trust_folder_gate
description: submit-to-gemini.sh fails in isolated temp dir until GEMINI_CLI_TRUST_WORKSPACE=true is set
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f034965f-13d1-4a2f-b6b9-58d211c43da0
---

`scripts/review/submit-to-gemini.sh` runs the Gemini CLI in an isolated temp directory (yolo/json mode), which Gemini CLI 0.43.0 treats as **untrusted** → it refuses with "not running in a trusted directory" and returns empty/exit-55 (the dispatcher reports "failed or timed out"). Fix: prefix the dispatch with `env GEMINI_CLI_TRUST_WORKSPACE=true` (or `--skip-trust`). Verified working 2026-05-26 for #2801 plan + code cross-review.

**Why:** the failure looks like a provider/quota outage but is purely the trust-folder gate; without the env var you wrongly conclude Gemini is unavailable and drop T3→T2.

**How to apply:** `timeout 340 env GEMINI_CLI_TRUST_WORKSPACE=true bash scripts/review/submit-to-gemini.sh --file <f> --prompt "<p>"`. Companion to the Codex dispatch quirk [[feedback_codex_cli_0_124_upstream_regression]] (`env -u CLAUDECODE` for Codex). See also [[feedback_gemini_sandbox_overlay_blindness]] (a separate Gemini issue — overlay file-visibility, not trust).
