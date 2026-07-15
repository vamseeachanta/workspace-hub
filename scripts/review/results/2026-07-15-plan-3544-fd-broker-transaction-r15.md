# Adversarial plan review: issue #3544 — FD broker transaction R15

- Date: 2026-07-15
- Reviewed commit: `fab055aa3708d414ab1f84a6a01887aac7fbc3f6`
- Verdict: **MAJOR**

## Findings

The outer bootstrap's Bash exec omitted `genesis-current` and every transaction
argument. The outer digest domain ambiguously mixed decoded source, quoted token,
and a self-referential whole-command digest.

No files or external state were changed by the reviewer.
