---
name: crossprovider codex unfrozen-npm-caret-range-dependencies-enable-sup
description: Unfrozen npm + caret-range dependencies enable supply-chain exposure windows
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [supply-chain, npm, dependencies, caret-ranges, packaging]
---

When npm install is not locked to a committed package-lock.json and dependencies use caret ranges (^1.5.0), fresh installs during a malicious package publish window can pull compromised versions. The monitoring-dashboard/frontend's axios dependency was exposed to this risk. Lockfiles freeze both direct and transitive dependencies.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
