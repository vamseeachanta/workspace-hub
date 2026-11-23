# Swarm 2: Capability Gap Map

Date: 2026-05-10 / 2026-05-11 run window
Provider: Codex CLI swarm launched from workspace-hub
Log: `logs/swarm-2-codex.jsonl`
Status: completed (`turn.completed` observed in log)
Artifact note: original worker-local artifact write failed; this report was recovered by Hermes from the worker's final log message during exit closeout.

## Recovered final result

1. Artifact path written
Not written. Local shell failed at sandbox startup; `apply_patch` failed to write the allowed path; GitHub write fallback was canceled.

2. Highest-impact 5 gaps
- `llm-wiki`: missing `AGENTS.md`, docs entrypoint, governance, and schema docs after spinout.
- `worldenergydata`: missing canonical docs/operator map and referenced data residence policy.
- `aceengineer-strategy`: README mission exists, but no repo-local agent/docs execution contract found.
- `digitalmodel`: Tier-1 OrcaFlex and cathodic-protection gaps remain engineering-critical and approval-gated.
- Ecosystem-wide: approval drift risk from many `draft` / `plan-review` plans that look actionable but are not approved.

3. Recommended issue candidates
- Complete tier-1 mission portfolio and refresh workspace-hub repo overview.
- Add worldenergydata canonical docs, operator map, data residence policy.
- Add llm-wiki post-spinout AGENTS/docs/governance/schema entrypoints.
- Add assethold operator map plus data privacy/cache policy.
- Add aceengineer-strategy private AGENTS/docs and privacy-wall enforcement.
- Plan digitalmodel OrcaFlex production-readiness work.
- Plan digitalmodel cathodic-protection maturity work.
- Add assetutilities CLI/devtools/agent_os focused test coverage.
- Refresh aceengineer-website Phase 4/6 content/calculator roadmap.
- Add cross-repo approval-state retrieval checklist.

4. Repos with insufficient mission evidence
- `llm-wiki`
- `aceengineer-strategy`
- `assethold`

5. Suggested next swarm/agent action
Run a follow-on planning-only swarm to create issue-ready evidence packets for `llm-wiki`, `worldenergydata`, `aceengineer-strategy`, and `assethold`, then retry writing the artifact once filesystem or connector write access is available.

## Verification notes

- Process exited before closeout check.
- Worker log exists under `docs/plans/agent-swarm-audits/2026-05-10/logs/`.
- The concise final result is also copied to `logs/swarm-2-last-message.txt` for easier inspection.
