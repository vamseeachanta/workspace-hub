# Provider Stall Recovery + Autofeed Reference

Session pattern captured 2026-04-30 from workspace-hub provider recovery.

## Symptoms that provider credits are not actually being used

- Background wrappers are still alive, but provider logs remain unchanged for multiple minutes.
- Claude print/noninteractive log remains `0` bytes while only wrapper/timeout/tee children are visible.
- Codex log contains only `Reading additional input from stdin...`; treat this as a likely stdin/EOF invocation problem, not useful credit burn, until output or artifacts advance.
- Gemini starts but only emits local agent-definition validation errors, e.g. `.gemini/agents/*.md` rejected for unsupported keys such as `permissionMode`.
- Hermes or tmux lanes exit `143` after fixed timeout windows without durable artifacts, often around git worktree operations.

## Recovery pattern

1. Capture a bounded snapshot: time, repo head/origin, active process tree, lane log sizes/mtimes, quota file, and current cron/monitor state. Wrap all git/process commands in `timeout`.
2. If a recurring autofeed is creating overlapping run directories or process saturation, pause that feeder before launching any replacements. Reconciliation comes before more fan-out.
3. Classify each lane as: useful-active, completed-with-artifact, completed-no-artifact, hung-no-output, launcher-error, capacity-exhausted, duplicate/overlap, or orphan/stale.
4. Preserve a read-only process/kill-candidate packet first; do not kill provider PIDs unless the user explicitly approves the kill list. When approved, kill only process trees with stale result/log mtimes or terminal signatures, record PID/cmdline/log evidence first, prefer TERM, then verify and clean orphaned child PIDs separately if the parent exits but `timeout/node` children remain.
5. For hung/no-output provider lanes in an under-utilized window, do not just report. Launch replacement lanes with corrected noninteractive invocation and unique prompt/log/result paths.
6. For saturated windows, keep the autofeed paused until launcher/classifier rules are patched and dry-run verified; then relaunch only bounded missing deliverables. A safe monitor patch should include `DRY_RUN=1`, syntax check (`bash -n`), result-file freshness gates, stale-orphan gates, provider signature gates, same-run/recent-success skip gates, and a per-provider launch cap before any live tick.
7. Add a local autofeed/monitor job (for example every 30 minutes for 24 runs) that checks whether the desired number of useful lanes is active and starts bounded follow-up lanes when capacity is idle.
8. Preserve hard gates in every auto-launched prompt: no outreach, no self-approval, no `status:plan-approved` mutation, no unapproved implementation, isolated worktrees only, validated artifacts before push/close.
9. Report old failed/stalled lanes, useful salvaged artifacts, kill candidates, and any new recovery lanes separately so apparent process count is not confused with actual provider-spend throughput.

## CLI-specific notes

- Codex: if the log stalls at `Reading additional input from stdin...`, revisit invocation and ensure prompt delivery/EOF semantics match the current `codex exec --help`. Prefer a known-good stdin-close pattern from `agent-cli-delegation-operations`.
- Gemini: repository-local `.gemini/agents` files can break startup if their frontmatter/schema uses unsupported keys. Capture the exact validation error; either run from a context that avoids loading those agents or plan a validated config fix. If Gemini CLI returns `429 No capacity available` for the default preview model, retry explicit stable models (`-m gemini-2.5-pro`, then `-m gemini-2.5-flash`); if those also 429, fall back to the configured OpenRouter Gemini route (`hermes chat --provider openrouter --model google/gemini-2.5-pro --quiet -q ...`) while recording that native Gemini capacity is unavailable. In workspace-hub-style overlay environments, prefer cwd `/mnt/local-analysis`, set `GEMINI_CLI_TRUST_WORKSPACE=true`, pass `--include-directories /mnt/local-analysis/workspace-hub`, and make prompts explicitly say `Write final output to <result-file>` because Gemini logs can advance while the result file remains a STARTED stub.
- Claude: zero-byte logs are inconclusive for a short warm-up, but after repeated unchanged snapshots treat them as suspect and require artifact/process-tree evidence. If `--output-format stream-json` is used with `-p/--print`, include `--verbose`; otherwise Claude exits immediately with `stream-json requires --verbose`. For autofeed monitors, text output can be safer than stream-json because it avoids the fragile `--verbose` coupling and keeps classifier tails smaller.
- Codex: for sandbox/no-exec environments (`bwrap: loopback: Failed RTM_NEWADDR`) or known stdin regressions, append a prompt fallback such as `Codex sandbox cannot exec; produce text-only audit.` and count the lane as scout/review evidence only, not implementation readiness.
- Redaction: avoid overly broad token scrubbers like `sk-` with short suffixes; they can corrupt ordinary lane names such as `gtm-legal-risk`. Match full credential prefixes with long token bodies instead.
