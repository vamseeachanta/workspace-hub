---
name: systematic-debugging
description: Four-phase debugging methodology emphasizing root cause analysis before fixes. Use for bug investigation, preventing random fixes, and systematic problem-solving.
type: reference
version: 1.1.0
category: development
last_updated: 2026-04-03
source: https://github.com/obra/superpowers
related_skills:
- tdd-obra
- writing-plans
- code-reviewer
capabilities: []
requires: []
tags: []
freedom: high
---

# Systematic Debugging

## Core Rule

Do not fix symptoms until you understand the root cause.

Random fixes waste time, create regressions, and hide the real failure mode.

## Quick Start

1. Investigate
2. Analyze patterns
3. Form a hypothesis
4. Implement one fix with test coverage

## When to Use

- bug reports needing investigation
- failing tests with unclear causes
- production incidents
- performance regressions
- integration failures
- any debugging taking more than a few minutes

## Phase 1: Investigation

Goal: understand what is actually failing before changing code.

Checklist:
- read the exact error message carefully
- reproduce the issue consistently
- inspect recent code/config/dependency changes
- gather logs, traces, metrics, and intermediate state
- for multi-component systems, trace data across each boundary

Questions:
- what fails exactly?
- what changed recently?
- what input or state triggers the failure?
- can it be reproduced reliably?

## Phase 2: Pattern Analysis

Goal: compare broken behavior against known-good behavior.

Checklist:
- find a working example in the codebase
- compare inputs, outputs, assumptions, and dependencies
- inspect configuration differences
- look for invariant violations

## Phase 3: Hypothesis and Testing

Goal: prove or disprove a specific theory.

Hypothesis format:
"The bug occurs because [condition] when [trigger], causing [symptom]."

Rules:
- test one variable at a time
- prefer minimal experiments
- if you do not know, say you do not know yet
- do not stack speculative fixes

## Phase 4: Implementation

Goal: fix the root cause with regression protection.

Checklist:
- write or update a failing test reproducing the bug
- implement a single fix aimed at the root cause
- verify the targeted test passes
- verify broader tests still pass
- document the fix if future maintainers need the context

## Hard Stop Rule

If three attempted fixes fail, stop and question the architecture instead of continuing to patch symptoms.

## Red Flags

Restart the process if you catch yourself:
- proposing fixes before reproducing the problem
- changing multiple things at once
- assuming framework/tool behavior without checking
- saying "it should work" without evidence
- skipping the failing-test step for a bug fix

## Anti-Patterns

| Anti-pattern | Better approach |
|---|---|
| shotgun debugging | controlled investigation |
| print-debugging only | structured instrumentation + comparison |
| blame the framework | verify framework behavior explicitly |
| works-on-my-machine reasoning | document exact repro inputs and runtime context |

## Good Debugging Artifacts

- failing test case
- repro command
- captured logs / traces
- working vs broken comparison note
- concise root-cause statement

## Agent Guidance

When delegating debugging work, require the delegate to return:
- observed symptoms
- hypothesis tested
- evidence gathered
- root cause found / not yet found
- minimal verified fix

## Exit Condition

Debugging is complete only when:
- root cause is identified or the unknown is explicitly stated
- the fix is verified by tests or direct repro
- no major regressions appear in adjacent behavior
