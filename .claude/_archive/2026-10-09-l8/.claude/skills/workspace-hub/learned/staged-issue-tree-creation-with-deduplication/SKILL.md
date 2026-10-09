---
name: staged-issue-tree-creation-with-deduplication
description: Pattern for creating hierarchical GitHub issue trees from phased project plans while checking for duplicate/overlapping issues
version: 1.0.0
source: auto-extracted
extracted: 2026-04-13
metadata:
  tags: ["github-issues", "project-planning", "deduplication", "issue-management"]
---

# Staged Issue Tree Creation with Deduplication

When converting a phased project plan into GitHub issues: (1) Search for existing related issues first to identify overlaps and distinguish scope; (2) Gather local context (files, inventories, labels) to write informed issue descriptions; (3) Design the tree structure by clarifying which existing issues are distinct vs. which new parent/child issues are needed; (4) Assign consistent labels (reusing existing ones) and status markers (e.g., `status:plan-review` for newly created issues pending approval); (5) Create parent issue first, then batch child issues in parallel, then backlink them all. This prevents duplicate effort and ensures hierarchical consistency.