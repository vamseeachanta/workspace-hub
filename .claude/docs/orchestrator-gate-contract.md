# Orchestrator Gate Contract Reference

Every orchestrator must produce validator-friendly evidence for the WRK, plan, cross-review, TDD, and legal gates before claiming execution. `scripts/work-queue/verify-gate-evidence.py WRK-xxx` checks these artifacts; run it (or embed it) before a WRK moves out of `pending`/`working`.

- **Close gate cross-review**
- The close evidence must include multi-agent cross-review artifacts (Claude, Codex, Gemini) that explicitly assess the executed artifacts and HTML output versus the approved plan. Capture per-seed verdicts in `assets/WRK-<id>/review.*` and reference them in `claim-evidence.yaml`.

## Evidence locations
- `.claude/work-queue/assets/WRK-<id>/plan-html-review-final.md` plus the `plan_reviewed`/`plan_approved` frontmatter flags.
- `.claude/work-queue/assets/WRK-<id>/review.*` (html/md/results) capturing the latest cross-review verdicts.
- variation/test files in the assets folder (marked with `test` in the filename) summarizing executed TDD checks.
- `.claude/work-queue/assets/WRK-<id>/legal-scan.md` with `result: pass` (or documented waiver).

## Close gate cross-review
Closing a WRK requires multi-agent cross-review evidence (Claude, Codex, Gemini) that explicitly evaluates the execution artifacts and HTML outputs against the approved plan. The Close script now invokes `scripts/work-queue/verify-gate-evidence.py` to prove each gate has the required artifacts before moving the item to `done`. Save the final `claim-evidence.yaml` so it references the same cross-review verdicts.

## NO_OUTPUT policy
1. Timeout/no-output results from review scripts must be classified as `NO_OUTPUT` in the gate evidence and rerun/fallback logic must execute (Codex hard gate still requires at least one successful review verdict).`
2. The template in `.claude/work-queue/assets/WRK-656/claim-evidence-template.yaml` enumerates the required fields and fallback guidance.

## Invocation guidance
- Run `scripts/work-queue/verify-gate-evidence.py WRK-xxx` after generating all artifacts. Non-zero exit prevents claiming.
- Prefer adding the verifier call inside `scripts/work-queue/claim-item.sh` before the claim move; `close-item.sh` already triggers the same script for the Close gate.
- Document the gate evidence status in `assets/WRK-<id>/claim-evidence.yaml` for auditability.
