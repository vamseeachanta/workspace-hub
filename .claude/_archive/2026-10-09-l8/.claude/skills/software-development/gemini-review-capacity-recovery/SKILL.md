---
name: gemini-review-capacity-recovery
description: Handle Gemini adversarial-review runs that emit repeated 429 capacity errors before either recovering with a real verdict or failing unavailable.
version: 1.0.0
author: Hermes Agent
category: software-development
tags: [gemini, adversarial-review, review-artifacts, capacity, retries]
---

# Gemini Review Capacity Recovery

Use when `gemini exec` is part of a plan/code adversarial review wave and the command prints repeated `429 RESOURCE_EXHAUSTED` / `MODEL_CAPACITY_EXHAUSTED` blocks.

## Why this exists
A Gemini run that looks failed at first glance may still recover and produce a substantive review verdict later in the same command output. If you stop early or mark it unavailable too soon, you can lose valid review evidence.

## Trigger pattern
Typical output starts with one or more retry blocks like:
- `Attempt N failed with status 429`
- `RESOURCE_EXHAUSTED`
- `MODEL_CAPACITY_EXHAUSTED`

This does **not** necessarily mean the run is unusable.

## Required workflow
1. Prefer foreground Gemini review for compact rerun prompts when possible.
2. Let the command complete if the timeout budget allows.
3. Inspect the **tail** of the full captured output for a real review block:
   - `Verdict:`
   - `Retrieval adequacy:`
   - `Key findings:`
   - `Main blockers to fix:`
4. If those appear, treat the run as a successful substantive review even if multiple 429 retry blocks occurred first.
5. Save a normal canonical artifact under `scripts/review/results/...-gemini.md`.
6. Only mark Gemini `UNAVAILABLE` if the command ends without a substantive review after retries.

## Artifact decision rule

### If Gemini recovers and produces a verdict
Save a normal artifact, for example:
- `scripts/review/results/YYYY-MM-DD-plan-<issue>-gemini.md`

Include the actual review findings, not the retry noise.

### If Gemini never produces a verdict
Save an unavailable artifact, for example:
- `scripts/review/results/YYYY-MM-DD-plan-<issue>-gemini.md`

With:
- `Verdict: UNAVAILABLE`
- concrete failure reason
- note that repeated capacity retries did not end in a substantive review
- path to the raw CLI log if captured

## Startup/config failure handling
Capacity retries are not the only Gemini failure mode. If the captured log contains only startup diagnostics — for example `Agent loading error`, agent-definition validation errors such as unsupported `permissionMode`, tool fallback warnings, or duplicate skill conflict warnings — and no substantive `Verdict:` block appears, mark the provider artifact `Verdict: UNAVAILABLE` as tool/config startup unavailability, not as a substantive `MAJOR` finding.

When a background Gemini review completion notification arrives after closeout, update the existing provider artifact with the final exit code and whether a verdict appeared. If no verdict appeared, keep `UNAVAILABLE`, commit the artifact-only correction, and verify remote state.

Reference: `references/startup-config-failure-vs-capacity.md`.

## Practical notes
- Do not classify a run from the first screenful of output.
- Gemini foreground runs may look noisy but still succeed.
- Capacity exhaustion is different from tool/config failure; treat them separately.
- If a provider-specific review artifact already exists as `UNAVAILABLE` and a later rerun recovers with a real verdict, replace the placeholder with the substantive artifact.
- If `git push` reports a remote ref-lock rejection after an artifact-only correction, fetch and compare `HEAD` vs `origin/main` before retrying; the push may already have landed.

## Example reusable summary
"Gemini printed repeated 429 capacity retries but eventually emitted a valid `Verdict:` block. Save the substantive review artifact and do not mark the provider unavailable."
