---
name: project-ace-linux-2-nvidia-hold-drift
description: "ace-linux-2 recurring desktop/VNC death = held NVIDIA stack + flowing kernels; FIXED 2026-06-04 (unheld, 580.159.03, kernel -35); blacklist removal still open"
metadata: 
  node_type: memory
  type: project
  originSessionId: a090259b-5019-42b7-9045-d4401a388d16
---

ace-linux-2's recurring "VNC/desktop dead" ([#1581](https://github.com/vamseeachanta/workspace-hub/issues/1581)) root cause, diagnosed+fixed 2026-06-04:

**Mechanism (structural):** NVIDIA stack apt-held + unattended-upgrades blacklist (`nvidia`,`libnvidia` in `50unattended-upgrades`, added 2026-02-22) while kernels kept auto-upgrading. Ubuntu per-kernel nvidia module pkgs hard-pin the driver point release (`>= X, <= X-1`) and superseded point releases are DELETED from the archive → held stack = built-in expiry; modules for new kernels become permanently uninstallable. Missing nvidia.ko → nvidia-drm absent → Xorg OutputClass ModulePath never activates → `(EE) Failed to load module "nvidia"` even though `xserver-xorg-video-nvidia-580` is installed. WRK-307 EDID confs (`/etc/X11/xorg.conf.d/10-{force,virtual}-display.conf`) hard-require `Driver "nvidia"` → no modesetting fallback → total session crash-loop, no `:0`, x11vnc has nothing to mirror.

**Fix applied:** unhold all 17 nvidia pkgs → `apt-get full-upgrade` (580.159.03 + -35 modules) → reboot into already-installed kernel 6.17.0-35. Verified: nvidia-smi OK (T400 4GB), 1920x1080 on DP-0, VNC working.

**Still open:** remove `"nvidia"`/`"libnvidia"` from the unattended-upgrades blacklist on ace-linux-2 or drift restarts on the next driver point release.

**Diagnostic shortcuts for next time:** GDM auto-login fires only once per gdm start (logout/crash → greeter forever; restart gdm to re-trigger). `gdm.service` ActiveSince timestamp = proof whether a remote restart actually ran. Machine notes live in docs/reports/2026-04-27-issue-2519-*, scripts/operations/system/fix-kvm-display-ace-linux-2.sh, [[feedback_x11vnc_vs_tigervnc_headless]].
