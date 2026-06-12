---
name: crossprovider hermes multi-machine-readiness-contract-defect-repo-pla
description: Multi-machine readiness contract defect: repo-placement check fails closed on remote hosts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [multi-machine-orchestration, readiness-checking, contract-design, test-hostname-matching]
---

When adding host-local evidence collection to readiness checks, repo-placement validators that run only on local machines will fail closed on remote hosts querying that machine's status. Fix requires making repo-placement optional in the evidence schema and testing evidence contracts with hostnames that don't match the local machine to catch the failure at write-time.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
