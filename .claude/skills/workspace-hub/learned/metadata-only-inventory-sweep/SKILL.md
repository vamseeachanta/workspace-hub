---
name: metadata-only-inventory-sweep
description: Systematic parallel classification and documentation of file inventories using metadata (filename, path, extension) without reading content
version: 1.0.0
source: auto-extracted
extracted: 2026-04-13
metadata:
  tags: ["inventory", "documentation", "parallel-processing", "metadata-classification", "automation"]
---

# Metadata-Only Inventory Sweep

Classify large file directories into families (parent/fragment/supporting/reject) using only filename, path structure, and extension—never content. Inventory 4+ directories in parallel, then generate 3 artifacts: comprehensive YAML inventory with family maps, metadata stubs document, and validation report. Validate counts across artifacts and post summary to GitHub. Use this for large-scale documentation audits where content reading is infeasible.