---
name: freetaxusa-eefile-navigation-pattern
description: Handling session timeouts and navigating FreeTaxUSA's multi-step e-filing flow to the signature page
version: 1.0.0
source: auto-extracted
extracted: 2026-04-14
metadata:
  tags: ["freetaxusa", "tax-filing", "session-management", "ui-navigation"]
---

# FreeTaxUSA E-file Navigation Pattern

When navigating FreeTaxUSA's Final Steps (Order Products → Review Return → Submit Return), expect session timeout dialogs to intercept clicks. Always dismiss the timeout dialog first before clicking the intended navigation button. Use element references to click buttons directly when page scrolling is uncertain. Recognize the three-step flow structure and stop at the Electronic Signature page—the final irreversible step requiring manual PIN entry and legal consent from both filers.