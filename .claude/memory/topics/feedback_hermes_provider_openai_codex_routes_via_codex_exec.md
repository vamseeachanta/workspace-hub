> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-16
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_hermes_provider_openai_codex_routes_via_codex_exec.md

---
name: hermes-provider-openai-codex-routes-via-codex-exec
description: "Hermes config `Provider: OpenAI Codex` actually shells out to `codex exec` binary subprocess for tool-using prompts (not direct OpenAI API calls); this makes the entire route subject to codex-cli hangs (#2715 / #2479-recurrence)"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d4fe73ec-6517-4e58-a943-20b6e6bd30f0
---

When `hermes status` shows `Provider: OpenAI Codex`, the Hermes default profile is NOT making direct OpenAI API calls — it shells out to the `codex exec` binary subprocess for tool-using or larger prompts. This means **the entire Hermes default-profile route is subject to whatever `codex` CLI bugs are current**, including the stdin-hang regressions tracked at [[issue-2479]] (v0.124) and [[issue-2715]] (v0.130).

**Why:** This is non-obvious from the surface API. `Provider: OpenAI Codex` reads like "OpenAI's Codex API" but it's actually a wrapper around the local `codex` binary. Without this knowledge, you'd debug Hermes hangs by checking OpenAI billing / network / API-key configs — all of which would look fine while the real cause is a hung `codex exec` subprocess. I burned 60 min of overnight dispatch + 30 min of post-mortem before connecting the dots; the explicit cross-reference was only found by reading [[issue-2715]]'s "Hermes routing also affected" section.

**How to apply:**

1. **Before delegating to Hermes default profile**, check: is the prompt tool-using or larger than ~30 bytes? If yes, and `Provider: OpenAI Codex`, expect codex-cli regressions to hit. Defer or route around.
2. **Diagnostic signal for the hang:** kanban worker shows `running` status with `last_heartbeat_at: None` on `claim_extended` events, low CPU (1-2%), zero stdout/stderr. That's the codex-exec hang pattern, not a Hermes bug.
3. **Workarounds** (until upstream codex-cli fix):
   - Tiny probes work (30-byte "say hello" returns OK per [[issue-2715]])
   - Route via `claude-code` (Anthropic Max overage) instead — different binary, different code path
   - Avoid kanban-worker dispatch through `default` profile entirely until [[issue-2715]] closes
4. **Track the cross-issue link** in dispatch failure post-mortems — don't file new bug reports for Hermes hangs without first checking [[issue-2715]] / [[issue-2479]] status.

Cross-references:
- [[issue-2715]] codex-cli 0.130.0 stdin-hang regression (current upstream)
- [[issue-2479]] codex-cli 0.124.0 stdin-hang (prior recurrence, supposedly fixed)
- [[issue-2718]] kanban-worker dispatch hazards (downstream effect, filed 2026-05-15)
- [[issue-2696]] Hermes routing-layer empirical audit (would have caught this)
- [[project_hermes_codex_quota]] — quota investigation context
