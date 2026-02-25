---
title: "AceEngineer-01 Hardware Assessment"
device: AceEngineer-01
hostname: vamsee-linux1
assessed_date: 2026-02-02
assessed_by: hardware-assess.sh v1.0.0 (root)
work_item: WRK-050
maintenance_date: 2026-02-02
---

# AceEngineer-01 (vamsee-linux1) — Hardware Assessment

> Last assessed 2026-02-02 using `system-maintain.sh v1.0.0` (root)

## Summary

| Component | Specification |
|-----------|---------------|
| CPU | 2x Intel Xeon E5-2630 v3 @ 2.40 GHz (8C/16T each, **16 cores / 32 threads** total) |
| Max Turbo | 3200 MHz |
| L3 Cache | 40 MiB |
| Architecture | x86_64 |
| RAM | 31.3 GB (32,810,676 KB) |
| RAM Type | DDR4 (reported as "Other" by dmidecode — Haswell-EP platform confirms DDR4 ECC) |
| RAM Speed | 2133 MT/s |
| GPU | NVIDIA GeForce GTX 750 Ti, 2048 MB VRAM |
| GPU Driver | 535.288.01 |
| Motherboard | ASUSTeK COMPUTER INC. Z10PE-D16 Series |
| BIOS | v0501 (2014-11-28) |
| OS | Ubuntu 24.04.3 LTS (Noble Numbat) |
| Kernel | 6.8.0-90-generic → 6.8.0-94-generic (pending reboot) |

## Storage

| Device | Size | Model | Serial | Transport | SMART |
|--------|------|-------|--------|-----------|-------|
| /dev/sda | 7.3 TB | ST8000DM004-2U9188 | ZR15GL5E | SATA | Unavailable (smartmontools not installed) |
| /dev/sdb | 232.9 GB | CT250BX100SSD1 | 1532F00A7EF4 | SATA | Unavailable (smartmontools not installed) |
| /dev/sdc | 931.5 GB | WDC WD10EZEX-00BN5A0 | WD-WCC3F7PV7H4U | SATA | Unavailable (smartmontools not installed) |

## Network

| Interface | Driver | State | Speed | IPv4 | Notes |
|-----------|--------|-------|-------|------|-------|
| enp3s0f0 | igb | UP | 1000 Mbps | 192.168.1.100/24 | Primary |
| enp3s0f1 | igb | DOWN | — | none | Unused |
| enp4s0f0 | igb | DOWN | — | none | Unused |
| enp4s0f1 | igb | DOWN | — | none | Unused |
| tailscale0 | tun | UNKNOWN | — | 100.107.64.76/32 | VPN |

## Maintenance Log (2026-02-02)

### OS Packages — 17 upgraded
- linux-generic 6.8.0-90 → 6.8.0-94 (kernel, headers, image, nvidia modules)
- gnome-shell 46.0 → 46.0 (patch)
- google-chrome-stable 144.0.7559.96 → .109
- fwupd 1.9.31 → 1.9.33
- libpng16, libmysqlclient21, xwayland, python3-apt, others

### Tools
- npm 10.8.2 → 11.8.0 (major version bump)
- NVIDIA driver: unchanged (535.288.01)
- Docker, Flatpak, pip, uv: not installed

### Reboot Required
Yes — new kernel 6.8.0-94-generic installed, pending activation.

## Platform Analysis

| Aspect | Assessment |
|--------|-----------|
| **CPU** | Dual Xeon E5-2630 v3 — strong multi-threaded capability (32T). Good for OpenFOAM, builds, parallel workloads. |
| **RAM** | 31.3 GB DDR4 @ 2133 MT/s. Board supports up to 512 GB — significant upgrade headroom. |
| **GPU** | GTX 750 Ti (2 GB) — very dated for compute. Consider replacing with spare NVIDIA T400 (4 GB). |
| **Boot SSD** | CT250BX100SSD1 (250 GB) — older SATA SSD, small for a workstation. Candidate for replacement with spare 500 GB SSD. |
| **Bulk Storage** | 8 TB Seagate + 1 TB WD — adequate for data. Need SMART check after smartmontools install. |
| **Motherboard** | ASUS Z10PE-D16 — dual-socket server board, supports up to 512 GB RAM, good expansion. BIOS is from 2014 — check for updates. |
| **Network** | 4x GbE (only 1 active) + Tailscale VPN. Could bond unused ports for throughput. |

## Pending Actions

- [ ] Reboot to activate kernel 6.8.0-94-generic
- [ ] Install smartmontools: `sudo apt install -y smartmontools`
- [ ] Run SMART check on all 3 drives after install
- [ ] Evaluate GPU swap: GTX 750 Ti → NVIDIA T400 (4 GB)
- [ ] Evaluate SSD swap: 250 GB CT250BX100SSD1 → spare 500 GB SSD
- [ ] Check BIOS update availability for Z10PE-D16 (current: v0501 from 2014)
- [ ] Re-run `system-maintain.sh` after reboot to confirm kernel change and get SMART data
