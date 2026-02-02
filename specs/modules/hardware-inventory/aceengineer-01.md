---
title: "AceEngineer-01 Hardware Assessment"
device: AceEngineer-01
hostname: vamsee-linux1
assessed_date: 2026-02-02
assessed_by: hardware-assess.sh v1.0.0
work_item: WRK-050
---

# AceEngineer-01 (vamsee-linux1) — Hardware Assessment

> Assessed 2026-02-02 using `hardware-assess.sh v1.0.0` (non-root + nvidia-smi)

## Summary

| Component | Specification |
|-----------|---------------|
| CPU | 2x Intel Xeon E5-2630 v3 @ 2.40 GHz (8C/16T each, **16 cores / 32 threads** total) |
| Max Turbo | 3200 MHz |
| L3 Cache | 40 MiB |
| RAM | 31.3 GB (32,810,676 KB) |
| RAM Type | Unknown (requires root + dmidecode) |
| GPU | NVIDIA GeForce GTX 750 Ti, 2048 MB VRAM |
| GPU Driver | 535.288.01 |
| Motherboard | ASUSTeK COMPUTER INC. Z10PE-D16 Series |
| BIOS | v0501 (2014-11-28) |
| OS | Ubuntu 24.04.3 LTS (Noble Numbat) |
| Kernel | 6.8.0-90-generic |
| Architecture | x86_64 |

## Storage

| Device | Size | Model | Serial | Transport | SMART |
|--------|------|-------|--------|-----------|-------|
| /dev/sda | 7.3 TB | ST8000DM004-2U9188 | ZR15GL5E | SATA | Unavailable (needs root) |
| /dev/sdb | 232.9 GB | CT250BX100SSD1 | 1532F00A7EF4 | SATA | Unavailable (needs root) |
| /dev/sdc | 931.5 GB | WDC WD10EZEX-00BN5A0 | WD-WCC3F7PV7H4U | SATA | Unavailable (needs root) |

## Network

| Interface | Driver | State | Speed | IPv4 | MAC |
|-----------|--------|-------|-------|------|-----|
| enp3s0f0 | igb | UP | 1000 Mbps | 192.168.1.100/24 | (on file) |
| enp3s0f1 | igb | DOWN | — | none | (on file) |
| enp4s0f0 | igb | DOWN | — | none | (on file) |
| enp4s0f1 | igb | DOWN | — | none | (on file) |
| tailscale0 | tun | UNKNOWN | — | 100.107.64.76/32 | (on file) |

## Notes

- **RAM type/speed**: Requires re-run with `sudo` to get DDR type and speed via dmidecode
- **SMART data**: Requires re-run with `sudo` and `smartmontools` installed for drive health
- **GPU**: GTX 750 Ti is a low-end card — consider replacing with one of the spare NVIDIA T400 (4 GB) for better compute capability
- **Storage layout**: 8 TB bulk storage + 1 TB HDD + 250 GB SSD (boot). The 250 GB SSD is small for a primary workstation
- **Network**: 4x Gigabit Ethernet (igb driver), only enp3s0f0 active. Tailscale VPN active
- **Motherboard**: Dual-socket Xeon board (Z10PE-D16) — high-end server board, supports up to 512 GB RAM

## Pending Actions

- [ ] Re-run with `sudo` for SMART health + RAM type
- [ ] Assess SSD health (CT250BX100SSD1 is an older model)
- [ ] Evaluate GPU upgrade path (T400 vs keeping GTX 750 Ti)
