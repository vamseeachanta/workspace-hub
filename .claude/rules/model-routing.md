# Model routing across the AI ecosystem — agent rule (#3390)

**When to apply:** choosing which model/provider runs a session, a subagent lane, or a delegated implementation marathon — at session start, at epic fan-out, and whenever a model becomes unavailable mid-run.

**Why:** two-week transcript audit 2026-06-21 → 2026-07-06 (186 sessions; auto-memory `reference_fable5_vs_opus48_session_comparison.md`). Fable 5 burned its quota in 2 days of heavy use and went dark for 3 (Jul 3–5); the 2026-07-04 quota wall killed two implementation subagents mid-run with uncommitted worktree edits. A separate `model_refusal_fallback` ejected Fable from a screenshot-heavy browser session. Meanwhile 104/186 session starts were one-shot adversarial reviews on premium models, and Opus's costliest waste came from building on stale local state (2h reskin on a stale branch) and manually babysitting merges.

**Routing table:**

| Lane | Use for | Do NOT use for |
|---|---|---|
| **Fable 5** | Orchestration, planning, forensic verification (git archaeology, memory-vs-reality reconciliation), epic curation, r2+/T2 adversarial reviews — short, high-leverage phases | Implementation marathons (quota); browser automation (safeguard-fallback risk in screenshot loops) |
| **Opus 4.8** | Implementation marathons, merge/CI mechanics (rulesets, merge-when-CLEAN), browser automation. **Automatic fallback whenever Fable is unavailable** (quota or safeguard) — a policy, not an incident | Burning 1M-context on crawl/scan work a cheaper lane can do |
| **Codex** | Sanctioned for **grunt/heavy marathon implementation lanes too**, not just review (owner directive 2026-07-06). Also r1 reviews via `submit-to-codex.sh` | Anything when codex weekly quota <10% (per `lane:codex` label); never trust its self-report — verify the artifact exists on the remote |
| **Sonnet / Haiku** | Crawls, scans, read-only fan-out, r1 hygiene reviews | Final synthesis or gate decisions |

**Operational corollaries (from the same audit):**

1. **Quota-resilience:** implementation subagents `commit && push -u` at every green milestone. Quota death clobbers uncommitted worktrees exactly like autorun does — see `feedback_autorun_clobbers_subagent_worktree_commits`.
2. **Review economics:** r1 plan/code reviews go to cheaper lanes (Codex/Sonnet); premium models only for r2+ or T2-scope reviews.
3. **Start-of-task grounding:** before building, verify the working branch against `origin/main` and the issue/PR state (`gh issue view` / `gh pr list --search`) — see `feedback_check_issue_state_before_implementing_on_detached_head` and `feedback_verify_generated_state_against_origin_not_working_copy`.
4. **Self-merge:** governed by [`merge-authorization.md`](merge-authorization.md) — default is verify green + hand the human the command; agent-run merges only under an explicit, per-PR, non-sticky authorization (owner-adopted policy, #3390 item 4).
5. **Automate waiting:** if you catch yourself polling a merge or a slow op in the foreground, switch to a background watcher immediately — don't re-derive this per session.

**Do NOT apply when:** the user explicitly names the model/provider for a task — their directive wins.

**Related:** [`patterns.md`](patterns.md), [`verify-ci-lint-toolchain.md`](verify-ci-lint-toolchain.md). Memory: `reference_fable5_vs_opus48_session_comparison`, `feedback_delegate_token_heavy_to_codex`, `ai-orchestration-models-agents-and-cross-review`. Issue: workspace-hub#3390.
