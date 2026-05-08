# Provider Session Learning Transfer — 2026-05-08

Source audit: `docs/reports/provider-session-ecosystem-audit.md` / `analysis/provider-session-ecosystem-audit.json`

- Refreshed audit timestamp: `2026-05-08T11:03:24Z`
- Previous audit boundary: `2026-05-07T09:37:54Z`
- Scope: Claude, Codex, Hermes, and Gemini provider-session artifacts under `logs/orchestrator/`.
- Memory parity check: `bash scripts/memory/check-memory-drift.sh` returned `In sync — no drift detected`; `.claude/memory/agents.md` already contains the 2026-05-08 Hermes memory bridge output.

## Recent activity transfer matrix

| Provider | Recent event-time activity | Key learning to transfer | Repo-system action |
| --- | ---: | --- | --- |
| Claude | 52 post-hook records / 6 runtime sessions | Claude remains the urgent stale-read migration-debt source. Recent work touched the provider audit script, issue #2655 plan artifacts, the legacy Claude reference map, and local Claude memory files. The reusable learning is that Claude local-memory updates must be checked against the repo bridge before claiming cross-agent parity. | Updated canonical audit. Transferred the urgent provider-learning bundle to existing issue #2310 rather than opening a duplicate. |
| Hermes | 1,857 post-hook records / 70 runtime sessions | Hermes is the active control-plane/provider-session learner. Recent high-volume reads/writes were GTM/digitalmodel planning and demo artifacts, while the audit still flags `llm_wiki_spinout_path_drift` as next-up. Treat Hermes corpus growth as partly event-time work and partly classification/export interpretation. | Updated canonical audit. Opened a dedicated follow-up issue for Hermes llm-wiki spinout path drift because no exact open issue was found. |
| Codex | 48 post-hook records / 2 runtime sessions | Codex recent activity was mostly wrapper/process orchestration (`codex`, `sed`, `rg`, `find`) with no recent top missing repo reads. Existing issue #2655 is already closed and the audit says path drift is improving; do not reopen without fresh broken evidence. | Added transfer note to closed issue #2655 as monitoring evidence; no duplicate issue. |
| Gemini | 0 post-hook records / 0 runtime sessions | Gemini had no post-audit event-time activity, but historical corpus still carries high `legacy_local_work_queue_items` migration debt and python3-heavy command hygiene. Interpret as a standing backlog, not fresh Gemini work. | Updated existing open issue #2312 rather than opening a duplicate. |

## Durable learnings now in the repo ecosystem

1. **Audit refresh must precede learning transfer.** The refreshed audit changed provider urgency: Claude escalated to `urgent_now`, Hermes escalated to `next_up`, Codex stayed monitoring/investigate, and Gemini stayed standing backlog with no recent activity.
2. **Separate event-time activity from corpus/snapshot growth.** Hermes showed large recent event-time activity plus corpus growth; Gemini showed no event-time activity but retained historical debt. Future reports must not describe every corpus delta as new provider work.
3. **Use existing issue anchors before creating follow-ups.** Claude maps to #2310; Gemini maps to #2312; Codex maps to #2655. Only Hermes required a new issue because the closest matches were closed/broader llm-wiki architecture issues, not the provider-session drift remediation.
4. **Memory transfer is not complete until repo bridge parity is checked.** Claude wrote/edited local Claude memory artifacts, but the cross-agent repo source of truth is `.claude/memory/`; the drift check verified Hermes memory is currently bridged into the repo.
5. **Provider-command hygiene remains provider-specific.** Claude recent commands still included bare `python3`; Gemini historical density remains python3-heavy; workspace-hub policy remains `uv run` for Python in repo work.
6. **Do not reopen closed closeout issues on audit wording alone.** Codex #2655 stays closed because recent missing reads are zero and the audit reports drift improving. Reopen only if fresh broken-path evidence appears.
7. **Transfer learning into both docs and issue tracker.** This report is the durable doc artifact; issue comments / new issue entries are the operational handles for the next provider-session remediation pass.

## Follow-up handles

- Claude urgent stale-read backlog: #2310
- Gemini legacy local lifecycle guidance: #2312
- Hermes llm-wiki spinout path drift: #2657
- Codex nested repo context drift: #2655 remains closed/monitoring

## Verification

- Provider audit refreshed successfully with `bash scripts/cron/provider-session-ecosystem-audit.sh`.
- Memory bridge drift check returned in sync.
- This report records the final audit timestamp (`2026-05-08T11:03:24Z`) to avoid future boundary ambiguity.
