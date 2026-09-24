---
name: crossprovider codex untracked-generated-artifacts-with-tracked-manif
description: Untracked generated artifacts with tracked manifests cause packaging failures
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, packaging, artifacts, traceability]
---

When manifests reference generated outputs but the outputs are .gitignored or untracked, branch diffs hide dependencies. Imports fail on checkout. Must explicitly include generated artifacts in git or regenerate at build time, not leave them untracked while manifests point to them.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
