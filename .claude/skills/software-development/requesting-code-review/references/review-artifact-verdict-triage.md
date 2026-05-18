# Review Artifact Verdict Triage

Use this when an adversarial review run writes a long artifact that includes the full prompt, diff, tool warnings, and final reviewer output.

## Why this matters

Review artifacts often begin with the prompt text, including required-output examples such as `Verdict: APPROVE, MINOR, or MAJOR`. A naive read from the top can miss the actual reviewer verdict near the end. Conversely, finding `MAJOR` in the prompt section is not evidence of a blocker. Always locate the final reviewer-authored verdict before acting.

## Fast triage pattern

1. Search the artifact for final verdict terms:
   - `Verdict:`
   - `MAJOR`
   - `MINOR`
   - `APPROVE`
2. Ignore matches in the prompt/instructions section.
3. Read the lines around the final reviewer-authored verdict.
4. If verdict is `MAJOR`, read all findings before patching.
5. Add or update focused regression tests for each blocker before changing implementation.
6. Re-run narrow tests, affected suites, and another adversarial review after fixes.

## Tool/context cap handoff rule

If tool budget or context limits hit before blockers are read and fixed, do not summarize as complete. The final handoff must include:

- repo/worktree path and branch;
- exact review artifact path;
- exact line/range to inspect next if known;
- unresolved verdict status;
- verification commands still required;
- explicit non-closeout language such as: `Do not commit, push, or close the issue yet.`

## Security note

When review artifacts concern dispatch credentials, chat IDs, allowlists, tokens, invite links, phone-like identifiers, or connection strings, preserve only redacted evidence in user-facing summaries and GitHub comments. Use `[REDACTED]` for sensitive values.
