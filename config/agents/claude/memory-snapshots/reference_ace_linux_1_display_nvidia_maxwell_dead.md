---
name: ace-linux-1-display-nvidia-maxwell-dead
description: "ace-linux-1 display broke on kernel 7.0 — NVIDIA 535 (last Maxwell branch) has no 7.0 modules; fix = purge nvidia stack, use nouveau"
metadata: 
  node_type: memory
  type: reference
  originSessionId: fc75e0dc-470f-4d5c-931a-6a1fae5b54f8
  modified: 2026-07-19T18:06:18.125Z
---

ace-linux-1 (GTX 750 Ti, Maxwell GM107) display fell back to simpledrm 640×480 +
llvmpipe on 2026-07-19 after `linux-generic-hwe-24.04` moved to kernel
**7.0.0-28**. Ubuntu ships prebuilt NVIDIA modules for 7.0 only for branches
580/595, which dropped Maxwell; the 535 branch (last to support the 750 Ti) tops
out at 6.17.0-40. Leftover `nvidia-kernel-common-535` still blacklists nouveau
(`/lib/modprobe.d/nvidia-graphics-drivers.conf`), so NO GPU driver could load.

Fix applied (user-run, agent sudo is permission-blocked): purge
`^nvidia-.*` `^libnvidia-.*` `^linux-modules-nvidia-.*` `^linux-objects-nvidia-.*`
`^linux-signatures-nvidia-.*`, then `update-initramfs -u`, then reboot → nouveau
drives the card. Proprietary NVIDIA on this card is a dead end on the 24.04 HWE
kernel track (Maxwell legacy since driver 555+); do NOT reinstall nvidia-535.
Rescue if nouveau ever misbehaves: GRUB → Advanced → boot 6.17.0-40.

Trap: `dpkg -S /usr/lib/modprobe.d/<file>` returns "no path found" on usrmerged
systems — query the `/lib/...` path instead.
