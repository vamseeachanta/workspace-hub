Latest Codex re-review update:

- Verdict: MAJOR
- Ready for user approval: No
- Retrieval adequacy: insufficient

Current remaining blockers:
1. The `--no-verify` / manual-shell bypass row still is not closed by a blocking control; the plan still leans on advisory dashboard detection for the direct-push path.
2. Some key tests are still too weak, especially provider-bootstrap proof and rollback-child validation.
3. Required dependencies are still not fully retrieved into resource intelligence, especially #2289 and #2129.
4. Owner boundaries remain ambiguous in parts of the bypass matrix.
5. CI parity and env-var / safe-path controls still need more explicit, falsifiable design.

New artifact:
- `scripts/review/results/2026-04-15-plan-2018-codex-rereview6.md`
