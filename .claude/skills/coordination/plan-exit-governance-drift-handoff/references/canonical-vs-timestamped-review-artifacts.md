# Canonical vs timestamped review artifacts at exit

Use this reference when exiting a plan-review session that has both canonical review files and timestamped rerun files under `scripts/review/results/`.

## Failure mode

A session can have two simultaneous review-evidence surfaces:

1. **Canonical artifacts** named like `scripts/review/results/YYYY-MM-DD-plan-<issue>-<provider>.md`.
2. **Timestamped rerun artifacts** named like `scripts/review/results/YYYYMMDDTHHMMSSZ-<plan-file>-plan-<provider>.md`.

If the exit audit only inspects canonical artifacts, it may miss newer timestamped evidence. If it only inspects timestamped artifacts, it may ignore the files named in the plan body or README. Treat disagreement between these surfaces as governance drift, not as a reason to pick whichever is convenient.

## Exit-audit pattern

For each issue under review:

- List canonical artifacts with mtime, size, and verdict.
- List timestamped artifacts with mtime, size, and verdict.
- Identify zero-byte or tiny stub files explicitly.
- Mark Gemini/provider quota/capacity outputs as `UNAVAILABLE`, never as approval evidence.
- If any newer timestamped artifact is untracked or not named by the plan, call it noncanonical evidence and decide whether next session should canonicalize, discard, or rerun.
- If canonical and timestamped verdicts disagree, block advancement until the next session reconciles which artifact set governs.

## Handoff wording

Use explicit wording such as:

- `Canonical artifacts remain MAJOR/invalid; timestamped rerun artifacts are newer but untracked and not yet canonicalized.`
- `Do not publish approval-ready comments until the governing review artifact set is decided and non-empty provider outputs clear MAJOR findings.`
- `Tiny or zero-byte artifacts are invalid evidence, not implicit APPROVE.`

## What not to do

- Do not silently promote timestamped rerun outputs into canonical status during exit unless the user asked for commit/push/canonicalization.
- Do not report only one artifact family when both exist.
- Do not let an `APPROVE` from one provider override a `MAJOR` from another provider in the same review wave.
