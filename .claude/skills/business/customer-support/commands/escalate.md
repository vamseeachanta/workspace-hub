---
name: escalate
type: command
plugin: customer-support
source: https://github.com/anthropics/knowledge-work-plugins
---

# Escalate Command Overview

The `/escalate` command packages support issues into structured briefs for engineering, product, or leadership teams. Here's what it does:

**Core Function:** Transforms an issue description and optional customer name into a comprehensive escalation document with full context.

**Input Format:** `/escalate <issue description> [customer name or account]`

**Key Workflow Steps:**

1. **Parse the Issue** -- Identify what's broken, who's affected, duration, troubleshooting attempts, and escalation justification
2. **Gather Context** -- Pull relevant information from support platforms, CRM, internal chat, project trackers, and knowledge bases
3. **Assess Impact** -- Quantify breadth (customers affected), depth (severity), duration, revenue risk, and time constraints
4. **Identify Target** -- Route to appropriate team (L2 Support, Engineering, Product, Security, or Leadership)
5. **Document Reproduction Steps** -- For bugs, include environment details and evidence
6. **Generate Brief** -- Structured format covering severity, impact, description, attempted solutions, customer communication status, and specific asks
7. **Suggest Next Actions** -- Offer to post updates, notify customers, set reminders, or draft follow-up communications

The template ensures escalations include business impact assessment, clear asks with deadlines, and supporting evidence -- reducing back-and-forth and accelerating resolution.
