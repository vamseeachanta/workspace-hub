---
name: label-driven-prompt-generation-architecture
description: Pattern for building automation scripts that classify GitHub issues into prompt templates using label-based routing and extract contextual data for batch processing
version: 1.0.0
source: auto-extracted
extracted: 2026-04-10
metadata:
  tags: ["automation", "github-api", "python-cli", "prompt-engineering", "architecture"]
---

# Label-Driven Prompt Generation Architecture

When building issue-to-prompt automation, use Python + gh CLI for structured classification: parse issue labels (e.g., `cat:bugfix`) to map to prompt templates, extract plan files or metadata from issue bodies using path tables, and implement both single-issue and batch-query modes. Store scripts in `scripts/automation/`, mark transient output directories in `.gitignore`, and verify classification against real issues before batch deployment. Test label matching, plan extraction, and batch filtering in sequence to catch routing logic errors early.