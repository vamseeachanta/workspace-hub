---
name: claude-worker-patch-loop
description: Use Claude as a delegated worker to patch canonical skills or policy files directly, then verify and iterate from the main session.
version: 1.0.0
author: Hermes Agent
tags: [claude, delegate_task, patching, skills, orchestration, verification]
related_skills:
  - claude-code
  - subagent-driven-development
  - overnight-parallel-agent-prompts
---

# Claude Worker Patch Loop

Use this when you want Claude to act as a specialist worker that directly edits files, while the main session stays as orchestrator/reviewer.

Best for:
- refining skills, workflows, policies, and route definitions
- applying a batch of structured documentation/process edits
- tightening a canonical file over several review/patch cycles
- using Claude for execution while Hermes keeps orchestration, verification, and synthesis

## When to use

Choose this pattern when:
- the work is non-trivial but file-local or small-batch
- you want Claude to make edits directly, not just give advice
- you already know the target file(s)
- you want an external worker to improve wording/structure while preserving orchestration discipline

Do not use this pattern when:
- the task needs user interaction mid-stream
- the file ownership is unclear
- many files have overlapping edits that require central conflict resolution first

## Core pattern

1. Orchestrate in the main session
- identify the exact target skill/file
- inspect current content first
- define the specific improvement scope
- keep the worker task self-contained

2. Delegate to Claude as worker
Use `delegate_task` with `acp_command: claude` and tell Claude to:
- patch the target file directly
- avoid asking questions
- preserve current route/style
- return a concise change summary

Pass context that includes:
- exact skill/file path
- current conventions already present
- the exact sections to strengthen
- constraints such as “targeted edits only” and “do not bloat”

3. Prefer focused worker goals
Good worker goals:
- patch Step 4 with reviewer schema, synthesis, and re-review rules
- patch Step 5 with approval normalization and label discipline
- strengthen entry gate and verification-first closure path

Avoid vague goals like:
- improve this skill
- make it better

4. Verify from the main session after Claude returns
Always inspect the file after the worker completes.
Check for:
- intended sections actually present
- no accidental regressions in neighboring sections
- version/frontmatter updated if appropriate
- canonical names preserved
- wording consistent with the existing route style

Use `skill_view` and `search_files` to verify exact inserted section titles/phrases.

5. Iterate in small loops
If more improvements are needed:
- send Claude back for the next bounded patch
- do not bundle too many conceptual changes into one worker pass
- keep a verify step between worker passes

## Recommended delegate_task template

Use a worker task shaped like this:

- Goal:
  Patch the canonical skill `<name>` to strengthen `<specific sections>`. Edit the file directly. Keep current style. Do not ask questions. Return a concise summary of exact changes made.

- Context:
  Include:
  - exact file/skill name
  - current sections already present
  - desired additions
  - constraints like:
    - preserve canonical route style
    - targeted edits only
    - avoid bloating too much

## Good verification pattern

After Claude returns:
1. `skill_view(name)` to inspect the current full skill
2. `search_files(pattern=...)` for the newly required section names
3. confirm version bump and description change if expected
4. synthesize the worker result into next-step recommendations

## What worked well in practice

This pattern worked well for canonical route refinement by having Claude directly patch:
- planning-route Step 4 and Step 5 gates
- execution-route early entry and verification-first checks
- delegation structure for agent-team packaging
- middle/late execution gates (TDD loop, targeted validation, adversarial review, commit/push, unified closeout)
- cross-route consistency cleanup between paired canonical skills
- creation of compact checklist companion skills derived from long canonical routes

Useful section-level additions Claude handled well:
- decision gates
- GitHub authority split
- zero-contention rules
- workstream split contracts
- reviewer output schemas
- verification-first closure checks
- prompt-pack vocabulary alignment
- closeout/result vocabulary alignment
- compact checklist extraction from canonical skills

### Paired-route pattern

For two closely related canonical files, use Claude in one of these ways:
- one worker for planning route, one worker for execution route in parallel
- then a follow-up Claude worker for cross-route consistency audit

This worked especially well for:
- `gh-work-planning`
- `gh-work-execution`
- their companion checklist skills

### Companion-checklist extraction pattern

After a canonical route becomes comprehensive, ask Claude to create a short checklist companion skill rather than over-compressing the main skill.
Use this when:
- the canonical skill is now the source of truth
- users need a live-execution checklist
- you want fast operational use without weakening the canonical route

Checklist companion rules:
- explicitly state the canonical skill remains authoritative
- keep the checklist action-oriented and short
- include trigger notes and one-screen live sequence
- do not duplicate the full decision framework

### Interrupted-worker recovery pattern

If a Claude delegate task is interrupted mid-audit or mid-review:
- launch a continuation delegate task with explicit "continue the interrupted audit" context
- keep the target files and audit scope the same
- ask for direct patches only where real inconsistencies exist

This worked well for a cross-route consistency pass after an interrupted audit.

## Pitfalls

- Do not assume the worker edited the right file without verification.
- Do not skip reading the current file first; give Claude concrete context.
- Do not ask Claude for broad “improvements” without explicit target sections.
- Do not let the worker own final synthesis; keep that in the main session.
- If a bulk patch fails, break the next worker request into smaller targeted edits.

## Decision rule

Use Claude as worker when:
- execution quality matters more than keeping all edits in the main context
- the task is patchable with clear scope
- you want the main session to remain the orchestrator and verifier

Keep Hermes as orchestrator for:
- deciding what to change next
- verifying edits
- reconciling multiple worker passes
- reporting the final state to the user
