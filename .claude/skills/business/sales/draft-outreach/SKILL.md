---
name: draft-outreach
description: "Create personalized outreach messages by researching prospects and tailoring content before drafting"
type: reference
version: 1.0.0
category: business
last_updated: 2026-02-03
source: https://github.com/anthropics/knowledge-work-plugins
related_skills:
  - account-research
  - call-prep
  - competitive-intelligence
  - create-an-asset
  - daily-briefing
capabilities: []
requires: []
see_also: []
tags: []
---

# Draft Outreach Skill Overview

This tool helps create personalized outreach messages by researching prospects first. Here's what it does:

## Core Function

The skill follows a three-step process: research the prospect, draft a personalized message, and deliver it through available channels. This skill never sends generic outreach -- it always researches the prospect first to personalize the message.

## Key Features

**Research Phase:**
- Conducts web searches by default
- Integrates with enrichment tools for verified contact info
- Accesses CRM data for relationship history
- Identifies personalization hooks from trigger events, mutual connections, or recent company news

**Message Creation:**
The skill avoids generic patterns like "I hope this email finds you well" or "I'm reaching out because..." Instead, it prioritizes opening with something specific you learned about the prospect.

**Output Options:**
- Email drafts (if email connector available)
- LinkedIn connection requests and follow-up messages
- Plain text for manual copying

## User-Specific Formatting and Governance

For AceEngineer GTM/prospect outreach:
- Keep email drafts plain text by default. Avoid markdown bullets, numbered lists, tables, emoji, decorative separators, and special symbols unless the user explicitly asks for them.
- Optimize outreach drafts for easy copy/edit: use normal paragraphs in the email body, not outline formatting. If listing capabilities, prefer a compact sentence with semicolons over bullets or numbered items.
- Use simple labels such as `Subject:`, then the email body, then optional `Notes for editing:` when drafting in a markdown file. Keep the email body itself copy-paste-ready plain text.
- If the user asks to open an outreach markdown file, write the draft to a `.md` file and open it with VS Code (`code path/to/file.md`) when available.
- Do not send outreach or imply outreach is authorized until the user approves the final message and attachments.
- Keep named prospect/contact details in the private strategy repository of record; route generic reusable collateral and implementation work to the appropriate delivery repos.

## Supported Triggers

Users activate the skill with requests like "draft outreach to [person/company]," "write cold email to [prospect]," or "reach out to [name]."

The tool adapts its approach based on relationship type -- cold outreach, warm introductions, re-engagement, or post-event follow-ups -- each with distinct message templates and tone.
