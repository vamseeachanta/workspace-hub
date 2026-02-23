---
title: "AceEngineer-02 Hardware Assessment"
device: AceEngineer-02
hostname: ace-linux-2
assessed_date: 2026-02-21
assessed_by: manual assessment (claude)
work_item: WRK-050
---

# AceEngineer-02 (ace-linux-2) — Hardware Assessment

> Last assessed 2026-02-21 via manual system queries

## Summary

| Component | Specification |
|-----------|---------------|
| CPU | 2x Intel Xeon E5-2630 v3 @ 2.40 GHz (8C/16T each, **16 cores / 32 threads** total) |
| Max Turbo | 3200 MHz |
| L3 Cache | 40 MiB |
| Architecture | x86_64 |
| RAM | 31 GB (32 GB nominal) |
| RAM Type | DDR4 ECC (Haswell-EP platform, ASUS Z10PE-D16) |
| GPU | NVIDIA T400 4GB (TU117GL) |
| GPU Driver | 580.126.09 |
| Motherboard | ASUSTeK COMPUTER INC. Z10PE-D16 Series |
| BIOS | v0601 (2014-12-26) |
| OS | Ubuntu 24.04.4 LTS (Noble Numbat) |
| Kernel | 6.17.0-14-generic |

## Storage

| Device | Size | Model | Serial | Transport | Mount Point | Usage |
|--------|------|-------|--------|-----------|-------------|-------|
| /dev/sdb | 465.8 GB | Samsung SSD 870 EVO 500GB | S6PXNM0TB13548D | SATA | / (root) | 19 GB / 458 GB (5%) |
| /dev/sda | 931.5 GB | WDC WD10EZEX-21M2NA0 | WCC3F6EFP0TX | SATA | /media/vamsee/Local Analysis | 441 GB / 932 GB (48%) |
| /dev/sdc | 2.7 TB | ST3000NC002-1DY166 | Z1F2GEBF | SATA | /media/vamsee/DDE | 2.0 TB / 2.8 TB (70%) |

### SMART Health (assessed 2026-02-21 via udisks2, WRK-293)

| Attribute | /dev/sdb (Samsung SSD) | /dev/sda (WDC HDD) | /dev/sdc (Seagate HDD) |
|-----------|------------------------|---------------------|------------------------|
| Overall Health | PASSED | PASSED | PASSED |
| Power-On Hours | 22 hrs | 65,988 hrs (~7.5 yr) | 51,248 hrs (~5.8 yr) |
| Power Cycles | 5 | 132 | 20 |
| Temperature | 30 C | 31 C | 31 C |
| Reallocated Sectors | 0 | **140** | 0 |
| Current Pending Sectors | n/a | 0 | 0 |
| Offline Uncorrectable | n/a | 0 | 0 |
| UDMA CRC Errors | 0 | 0 | 0 |
| Wear Leveling (SSD) | 0% worn | n/a | n/a |
| Spin Retry Count | n/a | 0 | 97 |
| Self-test Status | success | success | success |
| **Health Rating** | **Excellent** | **Caution** | **Good** |

> **Warning — /dev/sda (WDC WD10EZEX-21M2NA0):** 140 reallocated sectors
> at 65,988 power-on hours indicates surface degradation. Drive still
> passes SMART overall health but should be monitored monthly and
> replacement planned. No data on this drive is irreplaceable (analysis
> workspace), but avoid storing critical-path data here.

## Network

| Interface | Driver | State | Speed | MAC | IPv4 | Notes |
|-----------|--------|-------|-------|-----|------|-------|
| enp4s0f0 | igb | UP | 1000 Mbps | 08:62:66:a2:a0:ce | 192.168.1.103/24 | Primary (DHCP) |
| enp4s0f1 | igb | DOWN | — | 08:62:66:a2:a0:cf | none | Unused |
| tailscale0 | wireguard | UP | — | — | 100.93.161.27/32 | Tailscale VPN |

## Platform Analysis

| Aspect | Assessment |
|--------|-----------|
| **CPU** | Dual Xeon E5-2630 v3 — identical to AceEngineer-01. Strong 32-thread multi-threaded capability. |
| **RAM** | 32 GB DDR4 ECC. Board supports up to 512 GB — significant upgrade headroom. |
| **GPU** | NVIDIA T400 4GB — installed from spare inventory (WRK-050 Phase 3 plan). Suitable for display + light compute. |
| **Boot SSD** | Samsung 870 EVO 500 GB — 22 power-on hours, 0% wear, SMART Excellent. Essentially brand new. |
| **Bulk Storage** | 1 TB WDC HDD: **CAUTION** — 140 reallocated sectors, 65,988 hrs (~7.5 yr). Plan replacement. 2.7 TB Seagate HDD: Good — 0 reallocated sectors, 51,248 hrs (~5.8 yr), enterprise-class (Constellation CS). |
| **Motherboard** | ASUS Z10PE-D16 — identical to AceEngineer-01. BIOS v0601 (newer than AE-01's v0501). |
| **Network** | 2x GbE (1 active) + Tailscale VPN (100.93.161.27). |
| **OS** | Ubuntu 24.04.4 LTS — previously ran Windows 10 (flagged "Illegal" in WRK-050). Successfully migrated to Ubuntu. |

## Consolidation Status (from WRK-050)

- [x] Spare Samsung 870 EVO 500 GB SSD installed as boot drive
- [x] Spare NVIDIA T400 4GB installed (per Phase 3 GPU allocation plan)
- [x] OS changed from Windows 10 to Ubuntu 24.04.4 LTS
- [x] SMART health check on all drives (WRK-293, via udisks2; smartmontools not yet installed — requires sudo)
- [x] Tailscale VPN setup (100.93.161.27, matches AceEngineer-01 pattern)
- [x] DHCP reservation at router (MAC 08:62:66:a2:a0:ce -> 192.168.1.103) — confirmed 2026-02-22
- [x] SSHFS network mounts configured — fstab entries written for workspace-hub + ace-linux-1 drives (WRK-287, 2026-02-22)
- [ ] **SSHFS reboot persistence** — mounts fail after reboot (`Connection reset by peer`); root cause: `/root/.ssh/known_hosts` missing for ace-linux-1; fix documented in WRK-287 session log → run `sudo bash /tmp/fix-sshfs-mounts.sh` on ace-linux-2 (or re-create from WRK-287 if /tmp cleared)
- [x] **KVM display loss fixed (WRK-307, 2026-02-23)** — NVIDIA T400 dropped output on KVM switch (EDID lost). Software fix applied: GDM switched to X11 (`WaylandEnable=false`), EDID captured to `/etc/X11/edid.bin`, Xorg config forces `DFP-5` with `CustomEDID` at `/etc/X11/xorg.conf.d/10-force-display.conf`. Remote desktop fallback: x11vnc on display `:1` with autostart (`~/.config/autostart/x11vnc.desktop`), accessible from ace-linux-1 via SSH tunnel + TigerVNC. Hardware EDID dongle deferred (on hold).
- [ ] Reboot test — verify SSHFS mounts auto-recover after known_hosts fix (WRK-287)

## Cross-Machine Comparison (AE-01 vs AE-02)

| Component | AceEngineer-01 (ace-linux-1) | AceEngineer-02 (ace-linux-2) |
|-----------|------------------------------|------------------------------|
| CPU | 2x Xeon E5-2630 v3 (identical) | 2x Xeon E5-2630 v3 (identical) |
| RAM | 32 GB | 32 GB |
| GPU | GTX 750 Ti 2 GB | T400 4 GB |
| Boot Drive | CT250BX100SSD1 250 GB | Samsung 870 EVO 500 GB |
| Bulk Storage | 8 TB + 1 TB | 1 TB + 2.7 TB |
| Motherboard | Z10PE-D16 (BIOS v0501) | Z10PE-D16 (BIOS v0601) |
| OS | Ubuntu 24.04.3 LTS | Ubuntu 24.04.4 LTS |
| Kernel | 6.8.0-90-generic | 6.17.0-14-generic |
| IP | 192.168.1.100 | 192.168.1.103 |
| Tailscale | Yes (100.107.64.76) | Yes (100.93.161.27) |
