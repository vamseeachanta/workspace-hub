---
name: crossprovider codex ssh-target-null-creates-silent-parity-false-posi
description: ssh_target null creates silent parity false positives
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [config-validation, multi-machine, defect-class]
---

In multi-machine audits, null ssh_target is interpreted as "collect locally on this machine" but fails to surface when a remote machine is misconfigured (no ssh_target, no linux_reachable flag). Add explicit `local: true` field or pre-flight validation that all remote machines have named ssh_target.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
