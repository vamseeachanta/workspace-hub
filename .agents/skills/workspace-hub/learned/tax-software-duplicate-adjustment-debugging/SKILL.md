---
name: tax-software-duplicate-adjustment-debugging
description: Identify and fix duplicate tax adjustments entered through multiple mechanisms in tax software
version: 1.0.0
source: auto-extracted
extracted: 2026-04-14
metadata:
  tags: ["tax", "debugging", "freetaxusa", "form-8949", "wash-sale"]
---

# Tax Software Duplicate Adjustment Debugging

When a tax adjustment (like wash sale loss) appears doubled on Form 8949, check if the tax software has multiple entry mechanisms for the same adjustment type. Navigate through all adjustment pages (wash sale flow, other adjustments section, and dedicated adjustment information pages) to identify which fields are populated. Remove the duplicate entry from the non-primary mechanism while keeping the correct value in the dedicated field for that adjustment type. Verify the correction by checking if the tax calculation updates immediately.