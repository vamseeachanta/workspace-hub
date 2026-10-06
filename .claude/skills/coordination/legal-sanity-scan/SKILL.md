---
name: legal-sanity-scan
description: "Retired scanner compatibility notice; route legacy requests to manual final-report verification. Do not run or reinstall identifier gates."
version: 3.0.0
category: coordination
type: reference
---

# Retired: legal-sanity-scan

Owner decision: [issue 3936](https://github.com/vamseeachanta/workspace-hub/issues/3936), 2026-10-03.

This skill is a compatibility pointer, not an executable gate. The scanner and
repository identifier gates are retired. Do not require a PASS, restore hooks,
or interpret identifier presence as a commit/ingestion failure.

Follow `docs/standards/FINAL_REPORT_VERIFICATION.md` in workspace-hub: manually
review the actual final report and attachments for the intended audience, rights,
source qualification, independent secret checks and unresolved findings.
Identifiers may flow through authorized repository workflows. Secrets, access
permissions and source-specific publication rights remain separate controls.
