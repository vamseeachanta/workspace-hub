---
name: call-summary
type: command
plugin: sales
source: https://github.com/anthropics/knowledge-work-plugins
---

# Call Summary Tool Overview

This documentation describes the `/call-summary` command, a feature for processing call notes and transcripts to generate structured business outputs.

## Core Functionality

The tool performs three main functions:

1. **Extract action items** -- Identifies tasks with assigned owners and due dates
2. **Draft follow-up communications** -- Creates customer-facing emails
3. **Generate internal summaries** -- Produces structured team documentation

## Input Options

Users can provide input through:
- Pasted notes or bullet points
- Full transcripts from conferencing tools
- Informal call descriptions

## Output Structure

**Internal summaries** include: attendee details, discussion points, customer priorities, objections, competitive intelligence, action items in table format, next steps, and deal impact assessment.

**Customer emails** follow plain-text formatting without markdown, emphasizing clarity and scannability through short paragraphs and simple lists.

## Enhanced Capabilities

When connected to external tools, the system can:
- Automatically retrieve transcripts from platforms like Gong or Fireflies
- Update CRM records and log activities
- Draft or send emails directly
- Link calendar invitations

## Best Practices Emphasized

The documentation recommends providing detailed context, naming attendees, flagging critical information, and specifying deal stage to optimize output quality.
