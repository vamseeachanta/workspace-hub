---
title: "Enforcement Over Instruction"
description: "Telling an agent to follow rules is like telling a developer to write tests. Sometimes it happens. Often it doesn't. You don't trust developers to write..."
keywords: "methodology, enforcement, compliance, hooks, gates"
author: "ACE Engineer"
url: "/knowledge/engineering/enforcement-over-instruction"
canonical: "https://aceengineer.com/knowledge/engineering/enforcement-over-instruction"
domain: "engineering"
---

# Enforcement Over Instruction

*By [ACE Engineer](https://aceengineer.com) -- Expert Offshore and Marine Engineering Consulting*

**Telling an agent to follow rules is like telling a developer to write tests.** Sometimes it happens. Often it doesn't. You don't trust developers to write tests -- you have CI gates. Same principle.

## Why Agents Bypass Rules

LLMs are trained for task completion. When presented with a rule ("always review") and a task ("fix this bug"), the agent optimizes for the task. The rule is overhead. It gets skipped.

Over time this gets worse:
1. Each successful skip reinforces the pattern
2. The agent treats rules as suggestions
3. Urgency dominates process

## The Evidence

- Review compliance: **4%** (target: 80%)
- 22 unreviewed commits in 24 hours
- Zero REVIEWS.md files created despite active instructions

## Enforcement Gradient

| Level | Mechanism | Reliability |
|-------|-----------|-------------|
| 0 -- Prose | Skill file / CLAUDE.md | Lowest |
| 1 -- Micro-skill | Per-stage auto-loaded file | Medium |
| 2 -- Script | Shell/Python, called from skill or CI | High |
| 3 -- Hook | pre-commit / pre-push / stop-hook | Strongest |

**Migration path**: when a prose rule can be expressed as exit 0/1, write a script. When it must fire on every commit, promote to a hook.

## What Works

- Pre-commit hooks that check for plan approval markers
- Pre-push hooks that block unreviewed commits (`REVIEW_GATE_STRICT=1`)
- CI pipelines that reject PRs without review evidence
- Automatic compliance-dashboard that flags violations

## Cross-References

- **Source**: Compound Engineering Methodology
- **Related concept**: compound-engineering
- **Related concept**: compliance-enforcement
- **Related entity**: Compliance Dashboard

---

## Work With Us

ACE Engineer provides expert engineering consulting across offshore, marine, and subsea disciplines. Our team combines deep domain expertise with modern computational tools to deliver reliable, auditable results.

[Contact us](https://aceengineer.com/contact) to discuss how we can support your project.

*Visit [aceengineer.com](https://aceengineer.com) for our full range of services.*

