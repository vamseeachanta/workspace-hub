---
name: crossprovider codex central-vs-distributed-tool-provisioning-creates
description: Central vs distributed tool provisioning creates silent version divergence
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tool-provisioning, versioning-hazard, architecture]
---

Mixing `uv tool run` (central install) with per-repo `uv run` (local venv) leads to silent version mismatches when repos pin different tool versions or lack lockfiles (e.g., OGManufacturing has no uv.lock). Harness-wide decision must be explicit; implicit mixing is a hazard.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
