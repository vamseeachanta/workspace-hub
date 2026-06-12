---
name: crossprovider hermes hermes-control-plane-with-machine-specific-roles
description: Hermes control-plane with machine-specific roles
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, workstation, orchestration, dispatch]
---

ace-linux-1 is the default Hermes orchestration/control-plane workstation. ace-linux-2 is first overflow/execution worker. Before dispatching to ace-linux-2, verify tier-1 repos exist, engineering tools installed, Hermes/GitHub auth ready. Use `ssh host 'bash -lc "cmd"'` (login shell) for remote tool discovery.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
