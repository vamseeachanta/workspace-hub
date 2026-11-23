---
name: tax-form-navigation-verification
description: Systematic workflow for verifying tax software calculations against entry guide specifications
version: 1.0.0
source: auto-extracted
extracted: 2026-04-13
metadata:
  tags: ["tax", "verification", "workflow", "debugging"]
---

# Tax Form Navigation & Verification Workflow

When processing tax forms through automated software, systematically verify each page against source entry guide data before proceeding. Check that auto-populated values match expected amounts (e.g., standard deduction, child tax credit, foreign tax credit), inspect for Form requirements (e.g., Form 1116 simplified election threshold at $600), and confirm qualifying dependent/filer names. Use accessibility tree inspection when UI state is unclear (dialogs, expanded sections). Document insights about tax rule changes (e.g., OBBB 2025 updates) and phase-out thresholds to catch errors early.