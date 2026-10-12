---
name: handle-freetaxusa-session-timeouts
description: Recover from FreeTaxUSA session timeout dialogs blocking form submission and navigation
version: 1.0.0
source: auto-extracted
extracted: 2026-04-13
metadata:
  tags: ["freetaxusa", "web-automation", "error-recovery", "modal-handling"]
---

# Handle FreeTaxUSA Session Timeouts

When FreeTaxUSA's session timeout dialog blocks form rendering or navigation: (1) detect the blank/blocked page state, (2) use JavaScript to find and click the primary "Continue" button on the modal, (3) if the modal persists, use JavaScript to dismiss it programmatically and retry the original action via JavaScript click rather than direct interaction. This pattern prevents infinite retry loops when standard clicks don't register against modal-obscured buttons.