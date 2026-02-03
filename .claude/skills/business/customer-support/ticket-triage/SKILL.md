---
name: ticket-triage
description: "Categorize, prioritize, and route support tickets based on severity and type"
version: 1.0.0
category: customer-support
last_updated: 2026-02-03
source: https://github.com/anthropics/knowledge-work-plugins
related_skills:
  - customer-research
  - response-drafting
  - escalation
  - knowledge-management
---

# Ticket Triage Skill Summary

This document provides a comprehensive framework for support ticket management with the following key components:

## Core Functions
The skill enables categorization of support issues, priority assignment (P1-P4), and appropriate team routing based on issue severity and type.

## Nine-Category Taxonomy
Issues are classified as: Bug, How-to, Feature request, Billing, Account, Integration, Security, Data, or Performance. The framework emphasizes that the bug is primary when multiple issue types coexist, and suggests leaning toward Bug classification when uncertain.

## Priority Levels
- **P1 (Critical)**: Production down, data loss, security breach, affecting most users
- **P2 (High)**: Core workflow broken, multiple users impacted, no workaround available
- **P3 (Medium)**: Partial functionality loss with available workarounds, single user/small team affected
- **P4 (Low)**: Cosmetic issues, feature requests, general inquiries

SLA response times range from 1 hour (P1) to 2 business days (P4).

## Routing Strategy
Tickets route to appropriate teams: Tier 1 handles basic inquiries, Tier 2 manages complex investigations, Engineering addresses confirmed bugs, Product reviews feature requests, and specialized teams handle Security and Billing issues.

## Practical Guidance
The framework includes duplicate detection procedures, template responses by category, and escalation triggers, emphasizing that pattern recognition across multiple tickets warrants elevated priority consideration.
