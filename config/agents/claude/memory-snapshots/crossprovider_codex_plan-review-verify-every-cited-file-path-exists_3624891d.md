---
name: crossprovider codex plan-review-verify-every-cited-file-path-exists
description: Plan review: verify every cited file path exists
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [adversarial-review, plan-review, verification]
---

Adversarial reviewers must explicitly verify file existence for every path mentioned in a plan (e.g., `scripts/foo.sh`, `docs/bar.md`, `config/templates.yaml`). Don't assume presence; check with grep or ls and cite results as evidence. Multiple plan reviews surfaced missing files cited as existing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
