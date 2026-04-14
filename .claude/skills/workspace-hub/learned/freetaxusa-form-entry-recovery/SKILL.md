---
name: freetaxusa-form-entry-recovery
description: Handle session timeouts and modal dialogs when entering tax forms in FreeTaxUSA
version: 1.0.0
source: auto-extracted
extracted: 2026-04-13
metadata:
  tags: ["freetaxusa", "debugging", "web-automation", "tax-forms"]
---

# FreeTaxUSA Form Entry Recovery

When FreeTaxUSA forms timeout or session dialogs block rendering, use JavaScript to dismiss the timeout modal and retry the form submission. Check page state with `document.body.innerHTML` before attempting clicks. If the form click didn't register, retry via JavaScript executor rather than UI clicks. After successful save, verify navigation to the accounts page and check that the Federal tax amount updated to confirm data was persisted.