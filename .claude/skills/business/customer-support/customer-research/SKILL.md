---
name: customer-research
description: "Investigate customer questions through multi-source research with confidence scoring"
version: 1.0.0
category: customer-support
last_updated: 2026-02-03
source: https://github.com/anthropics/knowledge-work-plugins
related_skills:
  - ticket-triage
  - response-drafting
  - escalation
  - knowledge-management
capabilities: []
requires: []
see_also: []
---

# Customer Research Skill Overview

The **customer-research** skill is a structured methodology for investigating customer questions through multi-source research. Here are its key components:

## Core Process
The skill follows five steps: understanding the question, planning search strategy, executing systematic searches, synthesizing findings, and presenting with attribution.

## Source Hierarchy
Sources are prioritized by authority:

1. **Tier 1** (Highest): Official documentation, knowledge bases, policies, and internal roadmaps
2. **Tier 2**: CRM records, support tickets, internal documents
3. **Tier 3**: Chat history, emails, calendar notes
4. **Tier 4**: Web searches, forums, third-party resources
5. **Tier 5**: Inferences and analogous situations

## Confidence Scoring
Answers are labeled as:
- **High**: Confirmed by authoritative sources or multiple corroborations
- **Medium**: Found in informal sources or single sources without corroboration
- **Low**: Inferred or from outdated/unreliable sources
- **Unable to Determine**: No relevant information available

## Escalation Triggers
Escalate when answers involve roadmap commitments, pricing, legal terms, security/compliance, precedent-setting, custom configurations, specialized expertise, or high-risk situations.

## Documentation
Research findings should be captured in the knowledge base when they address recurring questions, required significant effort, or correct common misunderstandings, with date-stamps and quarterly reviews.
