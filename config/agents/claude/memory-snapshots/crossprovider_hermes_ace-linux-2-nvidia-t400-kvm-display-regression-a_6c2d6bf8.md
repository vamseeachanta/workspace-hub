---
name: crossprovider hermes ace-linux-2-nvidia-t400-kvm-display-regression-a
description: ace-linux-2 NVIDIA T400/KVM display regression after OS updates
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [ace-linux-2, nvidia-t400, kvm, edid, display-regression, post-update-hazard]
---

WRK-307: NVIDIA T400 loses EDID when KVM switches away; Wayland amplifies the issue. Existing fix scripts capture EDID to /etc/X11/edid.bin and force X11 + xorg.conf.d config. Post-update failure modes: (1) apt upgrade can reset /etc/gdm3/custom.conf re-enabling Wayland, (2) kernel updates change DRM card numbering (e.g., card2-DP-3 → card0-DP-1), (3) captured EDID binaries stale. Mitigation: after OS updates, validate gdm3 Wayland setting, check current DRM card numbering, re-capture EDID if card numbers changed.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
