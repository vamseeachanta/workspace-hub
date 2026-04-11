---
name: agent-team-prompt-generation
description: Create self-contained execution prompts that define multi-role workflows for Claude sessions without external dependencies
version: 1.1.0
source: updated-from-use
updated: 2026-04-11
metadata:
  tags: ["workflow", "prompt-engineering", "planning", "role-based-execution", "claude-code", "github-issues"]
---

# Agent-Team Prompt Generation

Use this when handing a GitHub issue or tightly scoped workstream to Claude Code in one self-contained prompt, especially after planning is complete and you want Claude to operate like an internal agent team in a single run.

## When to use
- A parent issue or child issue is already planned and needs an execution-ready Claude prompt
- The repo has workflow gates and Claude needs all constraints in one place
- You want one Claude session to simulate multiple roles (Planner, Architect/Implementer, Reviewer, Integrator)
- You need strict write-path ownership and zero scope creep
- You want a reusable handoff artifact committed into `docs/plans/`

## Core pattern

Write one markdown prompt file that gives Claude:
1. exact repo path
2. exact issue number + title + URL
3. parent/child issue relationships
4. authoritative docs/artifacts to consume
5. allowed write paths
6. read-only paths
7. forbidden paths
8. success condition
9. explicit step-by-step execution flow
10. exact final return format

The key learning: prompts work best when they are not just “do issue #NNN”, but a constrained operating contract.

## Recommended role block

Start the prompt with an internal team definition like:
- Planner
- Architect or Implementer
- Adversarial Reviewer
- Integrator

This reliably pushes Claude to:
- inspect current state first
- draft or revise the main artifact
- critique its own result
- then synthesize and post the final outcome

## Required prompt sections

### 1. Repo and issue identity
State:
- working directory
- primary issue URL
- related/parent/child issues
- whether the issue is planning-only, implementation-ready, or validation-only

### 2. Workflow constraints
Explicitly state:
- whether the repo is plan-gated
- whether the issue is already `status:plan-approved`
- whether this run is architecture-only, planning-only, or implementation-ready
- what must NOT be redefined from the parent issue

This prevents Claude from silently broadening scope.

### 3. Artifact grounding
List the exact authoritative files Claude must read first.
Example categories:
- parent operating-model docs
- current plan file
- review artifacts
- issue thread state
- likely implementation surfaces

Best practice: say “consume these as authoritative” instead of “consider these if helpful.”

### 4. Path contract
Always include three blocks:
- Allowed write paths
- Read-only paths
- Forbidden paths

This is the most reusable high-value pattern from the session.

Rules:
- allowed write paths should be exact files or tightly bounded directories
- forbidden paths should include sibling issue territories
- if the worktree is dirty outside allowed paths, instruct Claude not to touch unrelated files

### 5. Success condition
Give one explicit paragraph describing what must exist by the end of the run.
This should describe outputs, not effort.

Good pattern:
- “By the end of this run, the repo should contain …”
- then list the artifact qualities and required GitHub updates

### 6. Step-by-step execution plan
Use numbered steps.
A robust pattern is:
1. Read and assess current state
2. Produce or update the main artifact
3. Run internal adversarial review
4. Run final integrator pass
5. Post GitHub summary / transition issue state if eligible

### 7. State-transition rule
If the prompt can change GitHub state, include a conditional rule.
Example:
- if final review is APPROVE/MINOR -> move to next state / apply label
- if final review is MAJOR -> do not transition; post blocker summary and stop

This was especially useful in plan-gated issue execution.

### 8. Final return format
End with a strict required-output list such as:
1. What changed
2. Final review verdict
3. Whether label/state was changed
4. Exact files changed
5. Exact GitHub comments/labels added
6. Residual blockers

This makes later orchestration and artifact roundup much easier.

## Recommended template skeleton

```md
# Claude agent-team prompt: <issue>

We are in `<repo-path>`.

You are Claude Code operating as an internal 4-role agent team in one run:
1. Planner
2. <Architect/Implementer>
3. Adversarial Reviewer
4. Integrator

Do not ask the user any questions.

Repo/workflow constraints:
- ...

Primary issue:
- #NNNN <url>

Parent / related issues:
- ...

Authoritative artifacts to consume:
- ...

Allowed write paths:
- ...

Read-only paths:
- ...

Forbidden paths:
- ...

Success condition:
- ...

Execution steps:
STEP 1 — Read and ground
STEP 2 — Produce/update main artifact
STEP 3 — Internal adversarial review
STEP 4 — Final integrator pass
STEP 5 — GitHub update / state transition

Output requirements:
1. What changed
2. Final review verdict
3. ...
```

## GitHub-specific guidance

When the prompt targets a GitHub issue:
- include the exact issue URL
- include child issue URLs if the work must stay inside one child issue’s scope
- tell Claude whether to post a summary comment
- tell Claude whether label changes are allowed
- explicitly forbid changing labels if that should remain orchestrator-owned

## Parent/child issue execution pattern

For issue trees, use this division:
- parent issue prompt: architecture, scope boundaries, dependency order, review synthesis, plan state transitions
- child issue prompt: specialized contract or implementation under the approved parent model

Important lesson:
- tell Claude exactly what the child issue must not redefine from the parent
- otherwise it may re-open already-settled architecture decisions

## Dirty-worktree safety pattern

Add this clause whenever the repo may already be dirty:
- first inspect `git status --short`
- if unrelated changes exist outside allowed paths, do not touch them
- stop and report if safe isolation is not possible

This is especially important in shared orchestration repos.

## Best-fit examples from use
- planning/architecture issue handoff where Claude must finish a normative operating model and only move to `status:plan-review` if review clears
- child contract issue handoff where Claude must write one normative spec document under an already-approved parent model
- validation issue handoff where Claude must create conformance-check design without redefining architecture

## Pitfalls
- vague allowed paths like “relevant files”
- no forbidden-path block
- not telling Claude whether the issue is planning-only vs execution-ready
- asking Claude to both define parent architecture and implement child details in one run
- missing final return format
- no explicit rule for when GitHub labels/comments should or should not change

## Minimal checklist before saving a prompt file
- Is the repo path exact?
- Is the issue URL included?
- Are parent/child boundaries explicit?
- Are allowed/read-only/forbidden paths all present?
- Is there a clear success condition?
- Is there a conditional state-transition rule?
- Is the final return format explicit?

If yes, the prompt is usually robust enough for one-go Claude handoff.
