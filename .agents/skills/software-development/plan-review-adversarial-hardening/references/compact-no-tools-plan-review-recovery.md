# Archived Skill: `compact-no-tools-plan-review-recovery`

Original path: `/home/vamsee/.hermes/skills/software-development/compact-no-tools-plan-review-recovery`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/software-development/compact-no-tools-plan-review-recovery`
Consolidation date: 2026-04-29

---

---
name: compact-no-tools-plan-review-recovery
description: Recover adversarial plan reviews in large or tool-constrained repos by using compact self-contained prompts that forbid tool use and rely only on embedded grounded facts plus the plan text.
version: 1.0.0
author: Hermes Agent
category: software-development
tags: [review, planning, adversarial-review, codex, gemini, prompt-packaging]
related_skills:
  - multi-provider-adversarial-review
  - adversarial-review-prompt-refresh-guard
---

# Compact No-Tools Plan Review Recovery

Use this when adversarial plan review runs are failing because the provider keeps trying to inspect the repo directly instead of reviewing the artifact you've already grounded.

Typical symptoms:
- Codex tries shell/file inspection and fails with bubblewrap / user-namespace / sandbox errors
- Gemini tries `read_file` / repo search / GrepLogic and fails on ignore patterns or large-repo timeouts
- a full-path prompt works, but provider tool access makes the review flaky or noisy
- you already have the relevant facts and only need an adversarial verdict on the current draft

## Core idea

Instead of sending a prompt that encourages provider-side repo exploration, send a compact rerun prompt that:
1. embeds only the grounded facts you have already verified
2. embeds the full current plan text (or the critical excerpt)
3. explicitly forbids tool use, repo search, file reads, and web access
4. asks the provider to review only the prompt contents

This turns the provider into a pure reviewer instead of a repo investigator.

## When to prefer this pattern

Use it when at least one of these is true:
- provider-side repo tools are failing repeatedly
- the repo is large enough that search/read attempts time out
- ignore rules block the exact files the reviewer wants to inspect
- the artifact is already locally grounded, and the open problem is review quality, not discovery
- you are doing a rerun review after patching the draft and want to minimize new failure modes

Do not use it when the main problem is missing grounding. First gather the facts yourself, then use this pattern.

## Required prompt structure

Your compact review prompt should contain five parts:

1. Reviewer stance
- "You are adversarial. Assume defects until proven otherwise."
- "Do not praise. Do not restate the plan."
- "Focus only on what is still wrong, missing, risky, ambiguous, or insufficiently grounded."

2. Tool prohibition
- "IMPORTANT: Do NOT use tools, repo search, file reads, or web access."
- "Review ONLY the grounded facts and plan text included below."

3. Grounded facts block
Include only verified facts needed for review, for example:
- exact failing import path
- exact current missing file
- exact surviving precedent module
- exact supported labels, enums, seed sets, or mappings already decided

4. Current artifact text
Embed the current plan text directly.
Do not rely on the reviewer opening files.

5. Tight output format
Require:
- Verdict: APPROVE | MINOR | MAJOR
- Retrieval adequacy: adequate | inadequate
- Key findings
- Main blockers to fix

## Recommended workflow

1. Read the current plan yourself.
2. Extract the minimum verified facts needed to review it.
3. Write a compact prompt file under `.planning/quick/`.
4. Include an explicit no-tools instruction.
5. Run Codex/Gemini with that prompt file.
6. Save canonical artifacts under `scripts/review/results/`.
7. Patch the plan from the findings.
8. On rerun, refresh the prompt from the latest plan text.

## Example recovery prompt skeleton

```text
Adversarial rerun review for revised Issue #NNN plan.

Rules:
- You are adversarial. Assume defects until proven otherwise.
- Do not praise. Do not restate the plan.
- Focus only on what is still wrong, missing, risky, ambiguous, or insufficiently grounded.
- IMPORTANT: Do NOT use tools, repo search, file reads, or web access.
- Review ONLY the grounded facts and plan text included below.
- Return APPROVE only if the revised draft is truly implementation-ready.
- Each finding must cite a specific plan section or quoted claim.

Grounded facts:
- <verified fact 1>
- <verified fact 2>
- <verified fact 3>

Review questions:
1. <question>
2. <question>

Plan under review:
<full plan text>

Required output format:
Verdict: APPROVE | MINOR | MAJOR
Retrieval adequacy: adequate | inadequate
Key findings:
- <severity> <finding>
Main blockers to fix:
1. <item>
2. <item>
```

## What this pattern prevented in live use

This pattern was validated while reviewing plan drafts in `worldenergydata` where:
- Codex attempted sandboxed repo commands and hit bwrap/user-namespace failures
- Gemini attempted repo reads/searches and failed on ignore-pattern restrictions and GrepLogic timeouts
- compact no-tools prompts still produced useful adversarial MAJOR findings grounded in the embedded facts and plan text

## Pitfalls

- Do not omit critical facts just because they exist in the repo; the reviewer will not fetch them.
- Do not say "review the file at path X" if you also forbid file reads.
- Do not reuse stale prompts after editing the draft.
- Do not overstuff the prompt with irrelevant history; keep it compact and decision-focused.

## Good signs

- provider output goes straight to verdict/findings instead of spending time on repo inspection
- failures shift from tool/sandbox errors to substantive review findings
- reruns become stable and reproducible across providers

## Minimum artifact set

- `.planning/quick/review-<issue>-compact-prompt.md`
- `.planning/quick/review-<issue>-<provider>-compact.out`
- `scripts/review/results/YYYY-MM-DD-plan-<issue>-<provider>.md`

## Decision rule

If compact no-tools review still returns MAJOR, treat the plan as not approval-ready. The benefit of this pattern is review reliability, not leniency.
