---
name: freetaxusa-efiling-workflow
description: Navigate FreeTaxUSA e-filing process through final steps, handling session timeouts and identifying required manual signature steps
version: 1.0.0
source: auto-extracted
extracted: 2026-04-14
metadata:
  tags: ["tax-filing", "freetaxusa", "workflow", "debugging"]
---

# FreeTaxUSA E-filing Final Steps Workflow

When navigating FreeTaxUSA's final submission flow: dismiss recurring session timeout dialogs before each click, skip optional file attachment uploads (IRS already has data from 1099s), verify prior-year AGI matches exactly, and stop at the Electronic Signature page where both filers must manually enter 5-digit PINs. The 3-step flow is (1) Order Products → (2) Review Tax Return → (3) Submit Tax Return; only the final Submit button is irreversible.