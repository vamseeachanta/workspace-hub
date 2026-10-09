---
name: metadata-only-inventory-sweep
description: Execute constrained file inventory sweeps with metadata-only stubs and validation, useful for staged documentation work on large file sets
version: 1.0.0
source: auto-extracted
extracted: 2026-04-13
metadata:
  tags: ["inventory", "metadata", "validation", "documentation", "workflow"]
---

# Metadata-Only Inventory Sweep

Use this pattern when conducting staged inventory work on large file collections (30+ files) where full content extraction isn't yet authorized. Create YAML inventory, classify files by merge rules (amendments/corrigenda roll into parent standard), generate metadata stubs with required triplet markers (`■ `, `★ `, `▲ `), validate all stubs for compliance, then commit artifacts with STATE.md tracking. Defer ambiguous files (drafts, emails, agendas) explicitly rather than dropping them.