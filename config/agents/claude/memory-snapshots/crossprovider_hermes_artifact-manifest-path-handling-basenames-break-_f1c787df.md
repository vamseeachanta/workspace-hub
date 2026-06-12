---
name: crossprovider hermes artifact-manifest-path-handling-basenames-break-
description: Artifact manifest path handling: basenames break sha256sum from artifact dir
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [build-artifacts, testing-gates]
---

If manifest includes only file basenames (no relative paths), sha256sum -c fails when run from the artifact directory. #2511 had `artifact_manifest.sha256` with report basename only, requiring workaround. Manifest should use consistent relative paths from a known root for portability.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
