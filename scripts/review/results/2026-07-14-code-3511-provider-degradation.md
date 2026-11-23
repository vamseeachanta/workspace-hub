# #3511 code review — provider degradation record

**Commit reviewed:** `a77839505`  
**Requested depth:** T3, Claude + Codex + Gemini  
**Usable provider verdicts:** none; all are `UNAVAILABLE`, not approvals.

## Provider attempts

- **Claude:** `UNAVAILABLE`. `submit-to-claude.sh` detected DNS resolution failure for `api.anthropic.com` and returned no structured review. Raw harness artifact: `20260714T160603Z-commit-a778395058-commit-claude.raw.md`.
- **Codex:** `UNAVAILABLE`. Codex CLI 0.144.4 timed out after printing `Reading additional input from stdin...`, matching the documented stdin regression class. Raw harness artifact: `20260714T160603Z-commit-a778395058-commit-codex.raw.md`.
- **Gemini:** `UNAVAILABLE`. Direct `submit-to-gemini.sh --commit a77839505` exited 41 because no auth method is configured in `~/.gemini/settings.json` and no approved Gemini environment credential is present.

## Effective review evidence

Two independent read-only adversarial lanes completed against the full local diff. Both initially returned MAJOR/non-approve and supplied exact defects. Their findings were patched inline and regression-tested; see:

- `2026-07-14-code-3511-equality-lane.md`
- `2026-07-14-code-3511-windows-lane.md`

This is a documented T3-to-independent-two-lane degradation, not three-provider consensus. External provider recovery is not required to preserve the already-completed local defect-hunting evidence, but no unavailable provider is counted as approval.

