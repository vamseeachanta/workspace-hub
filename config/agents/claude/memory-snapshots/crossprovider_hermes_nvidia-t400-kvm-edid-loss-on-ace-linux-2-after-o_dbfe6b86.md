---
name: crossprovider hermes nvidia-t400-kvm-edid-loss-on-ace-linux-2-after-o
description: NVIDIA T400 + KVM EDID loss on ace-linux-2 after OS updates
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [ace-linux-2, display-quirk, kvm-edid, post-update-guard]
---

WRK-307 documented root cause: NVIDIA T400 loses EDID signal when KVM switches away from display. OS updates reset /etc/gdm3/custom.conf (re-enable Wayland, breaking X11 fix), kernel updates change DRM card numbering (card2-DP-3 → card0-DP-1), NVIDIA driver updates change DFP mappings. Fixes exist in scripts/operations/system/fix-kvm-display-ace-linux-2.sh (capture EDID sysfs, force X11, update xorg.conf.d). Workaround: DP EDID emulator dongle (~$10). Action: add post-update guard script that validates Wayland off, NVIDIA loaded, DRM cards unchanged (issue needed).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
