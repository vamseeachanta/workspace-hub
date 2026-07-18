---
name: crossprovider codex source-class-contracts-accept-only-synthetic-pub
description: Source-class contracts accept only synthetic/public/authorized inputs
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [privacy, api-design, architecture]
---

When defining source-class API boundaries, enforce contract to accept only synthetic data, public content, or expressly authorized inputs. Private mappings, identities, and original document bodies remain untracked and never passed through the contract.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
