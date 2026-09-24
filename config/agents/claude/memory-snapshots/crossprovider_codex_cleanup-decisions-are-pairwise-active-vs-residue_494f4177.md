---
name: crossprovider codex cleanup-decisions-are-pairwise-active-vs-residue
description: Cleanup decisions are pairwise active-vs-residue comparisons
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cleanup-triage, architecture, data-handling, llm-wiki-pattern]
---

Never blanket-delete migration residue or duplicates. Each candidate pair needs: class (migration-residue, baseline, cleanup-proof), sensitivity, value tier, mtime range, byte totals, duplicate-match rate, residue-only and active-only counts, and approval status. Set-based matching (e.g., signature sets) can falsely collapse multiplicity and trigger wrong delete recommendations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
