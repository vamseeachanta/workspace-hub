# Archived Skill: `plan-resubmit-wave-prompts`

Original path: `/home/vamsee/.hermes/skills/software-development/plan-resubmit-wave-prompts`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/software-development/plan-resubmit-wave-prompts`
Consolidation date: 2026-04-29

---

---
name: plan-resubmit-wave-prompts
description: Run a planning-only multi-terminal wave to harden blocked `status:plan-review` issues for fresh adversarial re-review, with zero implementation work and explicit path ownership.
version: 1.0.0
author: Hermes Agent
category: software-development
tags: [planning, github, review, overnight, claude, prompts, contention-avoidance]
---

# Plan Resubmit Wave Prompts

Use when multiple GitHub issues are in `status:plan-review` but are not actually approval-ready, and the best next move is to harden the canonical plan artifacts rather than implement code.

## When this is the right pattern

Choose this pattern when:
- there are no true `status:plan-approved` implementation candidates
- several plans are close and need blocker-specific revision
- the user wants parallel Claude terminals or prompt packs
- the repo is plan-gated and implementation would be unsafe or premature

Do NOT use this pattern for code execution. This is planning-only.

## Core idea

Split the work by canonical plan artifact, not by code area.
Each terminal owns one plan file. If `docs/plans/README.md` must be synchronized, only one terminal may edit README rows.

A highly effective variant is:
- main session directly executes the top/fastest-fix plan lane
- other lanes are emitted as self-contained prompt files for Claude terminals

## Recommended 3-lane structure

- T1: strongest candidate plan file + optional README row ownership
- T2: second candidate plan file only
- T3: third candidate plan file only

Example ownership map:
- T1 writes: `docs/plans/issue-A.md`, one owned row in `docs/plans/README.md`
- T2 writes: `docs/plans/issue-B.md`
- T3 writes: `docs/plans/issue-C.md`

Never let more than one terminal edit `docs/plans/README.md` in the same wave.

## Required prompt contract for each lane

Each prompt should explicitly say:
- planning-only work; no implementation
- do not ask the user questions
- do not change labels or approval markers
- owned write paths
- forbidden write paths
- exact known blockers to reconcile
- required verification commands (`grep`, `read_file`, targeted checks)
- final output must summarize:
  - files changed
  - blockers resolved
  - blockers still remaining before fresh re-review

## Good blocker classes for this pattern

This works especially well for plans blocked by:
- stale README row or status drift
- contradictory plan text across sections
- outdated review-summary wording
- missing required plan headings or sections
- command-policy drift (`python3` vs `uv run`, etc.)
- stale assumptions that later review comments disproved

## Main-session execution pattern

When doing one lane yourself while also preparing prompts for other terminals:
1. inspect the target plan + README row + latest issue comments
2. patch only the owned plan artifacts
3. verify with targeted grep/checks
4. avoid commits if the workspace has unrelated dirt
5. leave the plan in a conservative state (`draft` if fresh provider artifacts do not yet exist)

## README row synchronization rule

If the canonical plan was hardened but no new provider review artifacts were generated:
- sync the README row to the actual plan maturity
- do NOT overstate `plan-review` or approval-readiness
- mention that fresh external re-review is still required

## Prompt-pack deliverables

For a reusable wave, save:
- one master summary file with contention map and issue-to-terminal assignment
- one prompt file per terminal under `docs/plans/overnight-prompts/<date>-.../`

Master file should include:
- repo path
- issue map
- contention map
- negative write boundaries
- suggested launch command
- morning deliverables / expected outputs

## Practical lesson

For blocked approval queues, this pattern is often higher leverage than launching more review immediately. First fix the canonical plan contradictions and governance drift, then rerun the adversarial review wave on cleaner artifacts.
