# Cross-Review: Claude (code-reviewer agent)
## Verdict: REVISE → findings incorporated

### P1 Findings
- **P1-A**: GH issue template required fields not enforced via `gh issue create` — need GH Actions validator
- **P1-B**: No delta-sync/TTL in `gh-sync-down.sh` — rate limit risk at scale
- **P1-C**: No rollback path for renumber; burned GH IDs not excluded from mapping

### P2 Findings
- **P2-A**: Projects v2 custom fields not API-creatable — use labels only
- **P2-B**: GH Actions `issues` event not used for auto-sync
- **P2-C**: Cache/fallback contract for offline machines undefined
- **P2-D**: `gh issue list` query strategy unspecified

All findings incorporated into revised plan.
