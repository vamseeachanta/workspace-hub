# 2026-05-08 — Provider review unavailability during plan transfer

## Context
During #2657 planning/review, Claude produced usable plan-review artifacts, while Codex and Gemini did not. This mattered because the user expected provider-session learnings to be transferred into the repo ecosystem and the plan had to enter `status:plan-review` without pretending unavailable providers had approved it.

## What happened
- Claude review artifacts needed preservation under round-numbered filenames because rerunning the fanout mutates/truncates the runner output path (`claude.md`). The durable citation target became `*-claude-round4.md`.
- Codex had two incompatible failure modes:
  - Newer Codex CLI versions were in a known bad range for stdin/fanout behavior.
  - The pinned workaround (`codex-cli 0.123.0`) started successfully but failed server-side because the configured `gpt-5.5` model required a newer Codex CLI.
- Gemini returned capacity/429 for `gemini-3.1-pro-preview`.

## Reusable handling
1. Preserve the latest usable provider review as a round-numbered Markdown artifact.
2. For unavailable providers, create a concise Markdown stub containing:
   - verdict: `UNAVAILABLE`
   - workaround/retry attempted
   - raw failure excerpt
   - explicit statement that no review signal was produced
3. Do not cite raw `.err` files in the plan or issue comment; keep the raw excerpt inside the Markdown stub if needed.
4. Refresh the synthesis/disagreement artifact after the final plan patch, not before.
5. Before posting to GitHub, scan the plan for stale review state:
   - old MAJOR/MINOR verdicts
   - old round numbers
   - references to mutable runner outputs
   - contradicted acceptance criteria (for example conditional regeneration wording after later mandatory-regeneration decisions)
   - stale evidence counts

## Failure to avoid
Do not spend the remaining tool budget on polishing review text after the review gate is effectively complete while leaving the GitHub comment, `status:plan-review` label, commit, push, and verification undone. When budget is tight, perform the transactional closeout first and record remaining polish as follow-up.