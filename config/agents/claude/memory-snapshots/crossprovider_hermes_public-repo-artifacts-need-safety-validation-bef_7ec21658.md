---
name: crossprovider hermes public-repo-artifacts-need-safety-validation-bef
description: Public repo artifacts need safety validation before commit
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [public-repo-safety, artifact-hygiene, validation]
---

Before committing new files to public repos, run git diff inspection for private paths and vendor patterns (regex grep). Validate root-level artifact placement against repo structure guidelines. Document validation evidence (grep output, manual inspection notes) in the commit; do not claim validation without running checks.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
