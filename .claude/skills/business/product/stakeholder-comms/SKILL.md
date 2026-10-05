---
name: stakeholder-comms
description: Draft stakeholder updates tailored to audience -- executives, engineering,
  customers, or cross-functional partners
type: reference
version: 1.1.0
category: business
last_updated: 2026-10-05
source: https://github.com/anthropics/knowledge-work-plugins
metadata:
  adaptation_owner: workspace-hub
  adaptation_date: 2026-10-05
  adaptation_scope: PM evidence, acceptance, private ownership and action authorization
related_skills:
- feature-spec
- metrics-tracking
capabilities: []
requires: []
see_also: []
tags: []
---

# Stakeholder Communications Skill

## Evidence and way forward

Apply the existing [Engineering register](../../../../../config/agents/SHARED_SOUL.md#engineering-register--documents-chat-email-agent-output) and the owning repository's reporting template. Use the analysis/document as subject, tie conclusions to criteria and evidence, separate recommendations from requirements, and expose specific limitations. Select the report audience/surface under the existing repository rule before authoring; common methods do not authorize promoting private content. Reuse existing style rather than establishing another PM reporting standard.

Identify the project, audience, approved scope and reporting as-of time. Reuse its existing plan, decision log and deliverable register. Retrieve only audience-authorized sources for this project; common skills contain reusable methods and synthetic examples, while private facts and restricted locators stay with their private owner.

For material claims retain source locator/revision, source date and verification time. Newly retrieving an old update does not make it current. Refresh owners, dates, completion and blockers against primary evidence; inaccessible sources remain explicitly last-known with their dates. Conflicting evidence requires both observations and a reconciliation action; recency alone does not overrule approved scope.

Lead with the outcome or blocker, then the concrete way forward. Use only fields that affect the reader's decision:

- As of / scope reference / confidence (current, partial, last-known).
- Verified outcome and evidence link.
- Next deliverable and acceptance check; confirmed owner or unassigned; date explicitly committed, forecast, proposed or unknown.
- Dependency/risk, impact, mitigation owner and escalation trigger.
- Decision needed: options, recommendation, decision owner, needed-by date or unknown.

Never invent commitments to fill missing fields. Distinguish approved decisions from recommendations. Green requires current evidence against stated acceptance/milestone criteria; stale or conflicted status cannot justify it. Escalate observed triggers with impact and the smallest concrete ask. Drafting does not authorize sending or publishing.

Read [Space context and transfer](references/space-context.md) when preparing Space updates or transfers.

You are an expert at product management communications -- status updates, stakeholder management, risk communication, decision documentation, and meeting facilitation. You help product managers communicate clearly and effectively with diverse audiences.

## Update Templates by Audience

### Executive / Leadership Update
Executives want: strategic context, progress against goals, risks that need their help, decisions that need their input.

**Format**:
```
Status: [Green / Yellow / Red against stated criteria, or Partial / Last-known when current evidence is insufficient]

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
- Keep it scannable: status and asks first, and only the detail the reader will act on
- Status color should reflect current evidence against the stated milestone/acceptance criteria; otherwise report partial or last-known status
- Include material risks and limitations affecting the reported outcome; make escalation asks explicit where help is needed
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

**Green** (On Track): Current evidence satisfies the stated on-track criteria and no documented risk or blocker exceeds its reporting threshold.

**Yellow** (At Risk): Current evidence reaches a documented at-risk trigger; report the mitigation owner and evidence, or their absence.

**Red** (Off Track): Current evidence reaches a documented off-track trigger or fails criteria due at the reporting time.

### When to Change Status
- Report material risks when evidence first supports them; use Yellow against stated at-risk criteria, or Partial / Last-known when current evidence is insufficient
- Use Red when evidence establishes that criteria due at the reporting time are not met, or a documented off-track trigger is reached; escalate on the documented trigger rather than waiting until all options are exhausted
- Move back to Green only when current evidence satisfies the on-track criteria and verifies the relevant risk disposition
- Document what changed when you change status

## Risk Communication

### ROAM Framework for Risk Management
- **Resolved**: Current evidence satisfies the recorded resolution criterion; retain that evidence and its date.
- **Owned**: Risk has a confirmed accountable owner and a recorded next action; otherwise mark ownership unassigned.
- **Accepted**: Risk is known and the authorized decision owner has recorded acceptance without mitigation.
- **Mitigated**: Evidence shows actions reduced the risk to its documented acceptance threshold.

### Communicating Risks Effectively
1. **State the risk clearly**: "There is a risk that [thing] happens because [reason]"
2. **Quantify the impact**: "If this happens, the consequence is [impact]"
3. **State the likelihood**: "This is [likely/possible/unlikely] because [evidence]"
4. **Present the mitigation**: "The mitigation consists of [actions], owned by [confirmed owner or unassigned]"
5. **Make the ask**: "Required input: [specific help] to reduce this risk"

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
