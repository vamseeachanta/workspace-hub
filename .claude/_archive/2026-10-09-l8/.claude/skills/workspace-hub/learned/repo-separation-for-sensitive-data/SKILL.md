---
name: repo-separation-for-sensitive-data
description: Architecture pattern for splitting confidential data and reusable algorithms across repos
version: 1.0.0
source: auto-extracted
extracted: 2026-04-13
metadata:
  tags: ["architecture", "security", "repo-organization"]
---

# Repo Separation for Sensitive Data & Algorithms

When building personal finance or sensitive-data projects, separate confidential inputs (transactions, positions, account data) into a private personal repo while algorithms/analysis code lives in a shared/public repo. This lets you version control logic independently, share code without exposing data, and keep sensitive CSVs/configs in `.gitignore`. Example: `achantas-data` (private, holds transactions & positions) + `assethold` (shared, holds analysis algorithms). Reference cross-repo issues to track dependencies.