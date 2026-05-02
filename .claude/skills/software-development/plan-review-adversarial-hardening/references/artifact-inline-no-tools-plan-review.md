# Archived Skill: `artifact-inline-no-tools-plan-review`

Original path: `/home/vamsee/.hermes/skills/software-development/artifact-inline-no-tools-plan-review`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/software-development/artifact-inline-no-tools-plan-review`
Consolidation date: 2026-04-29

---

---
name: artifact-inline-no-tools-plan-review
version: 1.0.0
description: Recover adversarial plan reviews on large or sandbox-hostile repos by embedding grounded facts + full plan text directly in a compact prompt and explicitly forbidding reviewer tool use.
category: software-development
tags: [review, adversarial-review, prompt-packaging, codex, gemini, plan-review]
---

# Artifact-inline no-tools plan review

Use when adversarial plan reviews keep failing because providers try to search the repo, read ignored files, or hit sandbox/path/tooling problems.

## When this fits
- Codex/Gemini review runs fail due file access, ignored-path restrictions, sandbox errors, or repo-scale grep/search timeouts
- You already have the key grounded facts and the full plan text locally
- You want a fast rerun review focused on the plan artifact itself, not exploratory repo browsing

## Core pattern
1. Build a compact prompt file in the real workspace, not `/tmp/`.
2. Put these into the prompt explicitly:
   - adversarial reviewer instructions
   - grounded facts already verified by you
   - the exact review questions
   - the full current plan text
3. Add an explicit restriction:
   - "Do NOT use tools, repo search, file reads, or web access. Review ONLY the grounded facts and plan text included below."
4. Dispatch Codex/Gemini with the compact prompt.
5. Save canonical review artifacts under `scripts/review/results/`.
6. If Gemini still fails due capacity, save an `UNAVAILABLE` artifact instead of leaving the slot blank.

## Why this works
On large repos, providers may waste the run on:
- ignored-path read failures
- repo grep timeouts
- sandboxed shell/file-access failures
- startup agent noise that derails actual review

Inlining the artifact and forbidding tool use turns the run into pure document review. This worked well for worldenergydata plan reruns on issues #343 and #344 after earlier attempts failed or produced noisy/non-substantive runs.

## Minimal prompt skeleton

```text
Adversarial review request for Issue #NNN.

Rules:
- You are adversarial. Assume defects until proven otherwise.
- Do not praise. Do not restate the plan.
- Focus only on what is wrong, missing, risky, ambiguous, or insufficiently grounded.
- IMPORTANT: Do NOT use tools, repo search, file reads, or web access. Review ONLY the grounded facts and plan text included below.
- Return APPROVE only if the draft is truly implementation-ready.
- Every finding must cite a specific plan section or quoted claim.

Grounded facts:
- ...
- ...

Review questions:
1. ...
2. ...

Plan under review:
[full plan text]

Required output format:
Verdict: APPROVE | MINOR | MAJOR
Retrieval adequacy: adequate | inadequate
Key findings:
- <severity> <finding>
Main blockers to fix:
1. <item>
2. <item>
```

## Implementation notes
- Write prompt files with `terminal`/real filesystem paths under `.planning/quick/`
- Prefer absolute paths in `$(cat ...)` when dispatching to avoid cwd surprises
- Save raw compact outputs separately from canonical review artifacts
- If the review returns duplicated output, keep only the canonical distilled artifact in `scripts/review/results/`

## Good use cases
- plan review reruns after first-wave provider/tool failures
- large repos with ignore rules that block provider tool access
- architecture/planning reviews where the artifact text is the real object under review

## Not for
- code review where the diff itself is too large and must be inspected from the repo
- cases where the grounded facts are weak or unverified
- implementation validation that truly requires runtime inspection
