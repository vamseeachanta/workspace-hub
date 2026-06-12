---
name: crossprovider hermes mount-paths-alias-to-different-block-devices-acr
description: Mount paths alias to different block devices across machines
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [storage, multi-machine, diagnostics, workspace-hub]
---

Identical mount paths (e.g., `/mnt/local-analysis`) map to different physical block devices on different machines. Verify with `lsblk` before assuming shared storage or designing multi-machine workflows. Example: ace-linux-1 `/mnt/local-analysis` → `/dev/sdc1`, ace-linux-2 `/mnt/local-analysis` → `/dev/sda2`.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
