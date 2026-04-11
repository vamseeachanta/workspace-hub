---
name: single-terminal-gh-issue-prompts
description: Generate live issue-specific Claude prompts for a single terminal, with repo-aware path contracts and plan-gate safety checks.
version: 1.0.0
author: Hermes Agent
category: software-development
license: MIT
tags: [github, prompts, claude, single-terminal, issue-execution, planning-gate]
---

# Single-Terminal GH Issue Prompts

Use when a user asks for issue-specific Claude prompts to execute GitHub issues in a single terminal.

## Why this skill exists

Static prompt templates are not enough for plan-gated repos. Before drafting issue-specific prompts, do a live eligibility pass against the current repo and issue set. If no issues are actually execution-ready, generate assessment-first prompts instead of pretending they are directly executable.

## Trigger conditions

Use this skill when the user asks for any of:
- "issue-specific prompts"
- "10 gh issue prompts"
- "Claude prompts for these issues"
- "single terminal Claude agent-team prompts"
- "prompts for actual repo issues"

## Workflow

1. Identify the live repo
- Run `git remote -v`
- Run `git rev-parse --show-toplevel`
- Use the real owner/repo in all GH calls

2. Fetch live issues
- Run `gh issue list --repo OWNER/REPO --state open --limit 200 --json number,title,labels,updatedAt`
- Do not invent issue numbers or status

3. Check execution readiness
- Count issues with `status:plan-approved` if the repo uses plan gates
- Inspect the repo policy files (`AGENTS.md`, relevant docs) when available
- If `status:plan-approved` count is zero, explicitly say so

4. Pull issue details for the selected set
- For each chosen issue, fetch body/labels via `gh issue view N --repo OWNER/REPO --json number,title,body,labels`
- Use the issue body to extract scope and deliverables

5. Inspect the repo for likely implementation surfaces
- Search likely directories/files before writing prompts
- Prefer existing module/test/doc locations over generic guesses
- Build prompts around real paths found in the repo

6. Choose prompt mode honestly
- If issues are truly execution-ready: generate execution prompts
- If issues are not plan-approved: generate assessment-first / verification-first prompts
- Never present blocked issues as safely executable without caveat

## Prompt construction rules

Each prompt should include:
- repo name
- issue number and exact title
- one-terminal internal role split (Planner, Implementer, Tester, Reviewer, Synthesizer)
- live issue scope summary
- owned paths
- read-only paths
- forbidden paths
- required workflow
- validation commands
- required output format

## Path-contract guidance

Build path contracts from the real repo structure.

Minimum pattern:
- `Owned paths:` exact directories likely to change
- `Read-only paths:` policy/docs/context areas
- `Forbidden paths:` unrelated repos/modules or high-risk shared surfaces

Do not use vague path contracts like "any relevant files." Prefer concrete repo-aware boundaries.

## Assessment-first fallback (important)

If the repo is plan-gated and the selected issues are not plan-approved:
- say that live plan-approved count is zero
- still provide useful issue-specific prompts
- frame them as:
  - verification-first
  - assessment-first
  - operator-ready execution dossiers
- instruct Claude not to implement blindly if approval is missing

Recommended wording:
- "First verify whether this issue is directly executable now. If plan approval is missing or scope is blocked, do not implement blindly; instead produce an operator-ready execution dossier."

## Selection heuristics

Good batches for prompt generation:
- recent issues in the same initiative
- tightly scoped sibling issues
- issues whose bodies clearly define deliverables
- issues whose likely file surfaces can be inferred from the repo

Avoid mixing:
- unrelated domains
- issues with unknown implementation surface
- issues already likely complete without first checking

## Output style

When delivering the prompts to the user:
- include a short live status note first
- mention real repo path and owner/repo if helpful
- clearly state whether prompts are execution-ready or assessment-first
- keep each prompt ready to paste into Claude

## Example live status note

- `I used the live repo context from /path/to/repo and the current issues in OWNER/REPO.`
- `Open issues with status:plan-approved right now: 0.`
- `So these prompts are issue-specific and real, but they should be used in assessment/verification-first mode until approval is added.`

## Pitfalls

- Do not assume issues are executable just because they are open
- Do not fabricate file paths without checking the repo
- Do not ignore repo hard gates from AGENTS.md / policy docs
- Do not claim "direct execution" when live eligibility says otherwise
- Do not give generic prompts when the user asked for actual repo/issues

## Companion skills

- `gh-work-execution`
- `overnight-parallel-agent-prompts`
