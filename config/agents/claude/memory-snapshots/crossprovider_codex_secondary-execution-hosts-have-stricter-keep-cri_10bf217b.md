---
name: crossprovider codex secondary-execution-hosts-have-stricter-keep-cri
description: Secondary execution hosts have stricter KEEP criteria than primary workstations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [operations, fleet-management, repo-classification]
---

On secondary execution hosts (e.g., ace-linux-2), clones that merely exist do not justify KEEP classification. Only clones of repos the machine actually executes work for (licensed solver runs, CFD, scheduled jobs) qualify. Primary workstations allow KEEP for repos actively worked on; secondary hosts require demonstrated execution dependency.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
