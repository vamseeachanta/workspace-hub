# Disagreement report — plan #3518 (2026-07-13)

## Verdicts

| Provider | Verdict |
|---|---|
| Claude | APPROVE after three revision rounds |
| Codex | APPROVE after revision |
| Gemini | UNAVAILABLE — no non-interactive authentication configured |

## Resolution

Claude and Codex converged on the same load-bearing defect: semantic mutants must be self-pinned so `_setup_shape()` is exercised independently of digest drift. The plan now also specifies fresh/restored record state, exact index-loading behavior, staged RED/GREEN checkpoints, concrete reachability mutants, and staged-blob digest provenance.

Gemini produced no review signal. Its provider artifact preserves the authentication failure. The T2 two-provider gate is satisfied by independent Claude and Codex reviews.
