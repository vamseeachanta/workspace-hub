---
name: crossprovider gemini pre-existing-wrk-infrastructure-often-overlooked
description: Pre-existing WRK infrastructure often overlooked in planning
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [planning, codebase-inventory, scope-creep]
---

Multiple Gemini reviews of WRK-303 repeatedly discovered ensemble-plan.sh, synthesise.sh, and stance prompts already in the codebase. Plans written without full inventory of related scripts miss existing half-finished work and create false scope estimates. Before writing a work plan, grep for related scripts/files and examine partial implementations.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
