# Archived Skill: `plan-gated-overnight-queue-partition`

Original path: `/home/vamsee/.hermes/skills/coordination/plan-gated-overnight-queue-partition`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/coordination/plan-gated-overnight-queue-partition`
Consolidation date: 2026-04-29

---

---
name: plan-gated-overnight-queue-partition
description: Partition a plan-gated GitHub queue before launching overnight work so ineligible pre-approval issues are routed to planning/review lanes and only approved issues are used for merge-capable execution.
version: 1.0.0
author: Hermes Agent
category: coordination
tags: [github, overnight, plan-gated, queue-triage, execution]
---

# Plan-Gated Overnight Queue Partition

Use when the user asks for overnight parallel execution, adversarial review, and merge-to-main behavior in a repo that enforces a strict plan gate (for example: Issue -> Plan -> Adversarial Review -> User Approval -> status:plan-approved -> Implement).

## Problem

Users may ask for a wave like:
- identify issues before `status:plan-approved`
- execute them with 4 parallel agents
- adversarial-review the work
- merge to main overnight

In a plan-gated repo, that request is internally inconsistent. Issues before approval are not implementation-eligible.

## Required move

Before promising execution, do a live queue partition.

Classify every candidate issue into:
1. `pre-plan-approved`
   - no `status:plan-approved`
   - no local approval marker
2. `status:plan-review`
   - has `status:plan-review`
   - still not implementation-eligible
3. `status:plan-approved`
   - live GitHub label present
4. `locally approved`
   - `.planning/plan-approved/<issue>.md` exists

In workspace-hub-style repos, implementation eligibility should be treated conservatively:
- before-approved and plan-review items -> planning/review hardening only
- merge-capable overnight implementation -> select from approved pool only

## Minimal audit pattern

1. Fetch live open issues via `gh issue list --state open --json ...`
2. Inspect `.planning/plan-approved/*.md`
3. Reconcile label state + local marker state
4. Count each bucket
5. Only then decide whether the requested overnight work can include code execution/merge

## Routing rule

- If the user wants work specifically from the before-approved queue:
  - do planning/review/adversarial hardening only
  - do not promise implementation or merge
- If the user wants overnight implementation + review + merge:
  - pivot execution to already-approved issues
  - say explicitly that this is required by repo policy
- If needed, offer a mixed mode:
  - some lanes harden blocked plans
  - other lanes execute already-approved issues

## Why this matters

Without this partition, it is easy to promise an overnight merge wave that the repo policy forbids. Doing the partition first prevents invalid execution plans and makes the constraint visible early.

## Reusable phrasing

"I can assess and adversarially harden the before-approved queue, but I cannot implement or merge those items until they reach `status:plan-approved`. For overnight merge-capable execution, I need to draw from the approved pool instead."
