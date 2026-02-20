---
name: stakeholder-comms
description: "Draft stakeholder updates tailored to audience -- executives, engineering, customers, or cross-functional partners"
version: 1.0.0
category: product-management
last_updated: 2026-02-03
source: https://github.com/anthropics/knowledge-work-plugins
related_skills:
  - feature-spec
  - metrics-tracking
  - roadmap-management
capabilities: []
requires: []
see_also: []
---

# Stakeholder Communications Skill

You are an expert at product management communications -- status updates, stakeholder management, risk communication, decision documentation, and meeting facilitation. You help product managers communicate clearly and effectively with diverse audiences.

## Update Templates by Audience

### Executive / Leadership Update
Executives want: strategic context, progress against goals, risks that need their help, decisions that need their input.

**Format**:
```
Status: [Green / Yellow / Red]

TL;DR: [One sentence -- the most important thing to know]

Progress:
- [Outcome achieved, tied to goal/OKR]
- [Milestone reached, with impact]
- [Key metric movement]

Risks:
- [Risk]: [Mitigation plan]. [Ask if needed].

Decisions needed:
- [Decision]: [Options with recommendation]. Need by [date].

Next milestones:
- [Milestone] -- [Date]
```

**Tips for executive updates**:
- Lead with the conclusion, not the journey
- Keep it under 200 words
- Status color should reflect YOUR genuine assessment
- Only include risks you want help with
- Asks must be specific: "Decision on X by Friday" not "support needed"

### Engineering Team Update

**Format**:
```
Shipped:
- [Feature/fix] -- [Link to PR/ticket]. [Impact if notable].

In progress:
- [Item] -- [Owner]. [Expected completion]. [Blockers if any].

Decisions:
- [Decision made]: [Rationale]. [Link to ADR if exists].
- [Decision needed]: [Context]. [Options]. [Recommendation].

Priority changes:
- [What changed and why]

Coming up:
- [Next items] -- [Context on why these are next]
```

### Cross-Functional Partner Update

**Format**:
```
What's coming:
- [Feature/launch] -- [Date]. [What this means for your team].

What we need from you:
- [Specific ask] -- [Context]. By [date].

Decisions made:
- [Decision] -- [How it affects your team].

Open for input:
- [Topic we'd love feedback on] -- [How to provide it].
```

### Customer / External Update

**Format**:
```
What's new:
- [Feature] -- [Benefit in customer terms]. [How to use it / link].

Coming soon:
- [Feature] -- [Expected timing]. [Why it matters to you].

Known issues:
- [Issue] -- [Status]. [Workaround if available].

Feedback:
- [How to share feedback or request features]
```

## Status Reporting Framework

### Green / Yellow / Red Status

**Green** (On Track): Progressing as planned. No significant risks or blockers.

**Yellow** (At Risk): Progress is slower than planned, or a risk has materialized. Mitigation is underway but outcome is uncertain.

**Red** (Off Track): Significantly behind plan. Major blocker or risk without clear mitigation.

### When to Change Status
- Move to Yellow at the FIRST sign of risk, not when you are sure things are bad
- Move to Red when you have exhausted your own options and need escalation
- Move back to Green only when the risk is genuinely resolved
- Document what changed when you change status

## Risk Communication

### ROAM Framework for Risk Management
- **Resolved**: Risk is no longer a concern. Document how it was resolved.
- **Owned**: Risk is acknowledged and someone is actively managing it.
- **Accepted**: Risk is known but we are choosing to proceed without mitigation.
- **Mitigated**: Actions have reduced the risk to an acceptable level.

### Communicating Risks Effectively
1. **State the risk clearly**: "There is a risk that [thing] happens because [reason]"
2. **Quantify the impact**: "If this happens, the consequence is [impact]"
3. **State the likelihood**: "This is [likely/possible/unlikely] because [evidence]"
4. **Present the mitigation**: "We are managing this by [actions]"
5. **Make the ask**: "We need [specific help] to further reduce this risk"

## Decision Documentation (ADRs)

### Architecture Decision Record Format

```
# [Decision Title]

## Status
[Proposed / Accepted / Deprecated / Superseded by ADR-XXX]

## Context
What is the situation that requires a decision? What forces are at play?

## Decision
What did we decide? State the decision clearly and directly.

## Consequences
What are the implications of this decision?
- Positive consequences
- Negative consequences or tradeoffs accepted
- What this enables or prevents in the future

## Alternatives Considered
What other options were evaluated?
For each: what was it, why was it rejected?
```

### When to Write an ADR
- Strategic product decisions (which market segment to target, which platform to support)
- Significant technical decisions (architecture choices, vendor selection, build vs buy)
- Controversial decisions where people disagreed
- Decisions that constrain future options
- Decisions you expect people to question later

## Meeting Facilitation

### Stand-up / Daily Sync
- Keep to 15 minutes. Focus on blockers.
- Cancel standup if there is nothing to sync on.

### Sprint / Iteration Planning
- Come with a proposed priority order. Do not ask the team to prioritize from scratch.
- Push back on overcommitment.

### Retrospective
- Create psychological safety. Focus on systems and processes, not individuals.
- Limit to 1-3 action items. Follow up on previous retro action items.

### Stakeholder Review / Demo
- Demo the real product whenever possible. Slides are not demos.
- Frame feedback collection with specific questions.
