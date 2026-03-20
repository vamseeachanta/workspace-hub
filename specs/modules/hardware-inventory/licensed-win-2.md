---
title: "ACMA-WS014 Hardware Assessment"
device: ACMA-WS014
hostname: ACMA-WS014
assessed_date: 2026-02-20
assessed_by: hardware-assess.ps1 v1.0.0
work_item: WRK-050
---

# ACMA-WS014 — Hardware Assessment

> Assessed 2026-02-20 using `hardware-assess.ps1 v1.0.0` on Windows 11 Pro

## Summary

| Component | Specification |
|-----------|---------------|
| CPU | Intel Core i9-13900 (Raptor Lake), 8 P-cores + 16 E-cores, **24 cores / 32 threads** |
| Base Clock | 2000 MHz |
| L3 Cache | 72 MB |
| Architecture | x64 |
| RAM | ~16 GB DDR5 @ 4800 MHz |
| GPU (discrete) | NVIDIA T1000 8GB, driver 32.0.15.8142 |
| GPU (integrated) | Intel UHD Graphics 770, ~2 GB shared |
| Storage | Samsung MZVL2512HDJD-00BLL, 512 GB NVMe SSD |
| Motherboard | LENOVO 1066, firmware S0JKT12A (2023-09-07) |
| OS | Microsoft Windows 11 Pro, Build 10.0.22631 |

## Storage

| Device | Size | Model | Type | Health |
|--------|------|-------|------|--------|
| NVMe SSD | 477 GB (512 GB nominal) | Samsung MZVL2512HDJD-00BLL | NVMe SSD | OK |

*Note: Storage detection in `hardware-assess.ps1` returned empty — supplemented via `Get-PhysicalDisk` directly.*

## Network

| Interface | Driver | State | Speed | IPv4 | Notes |
|-----------|--------|-------|-------|------|-------|
| Ethernet 2 | Intel I225-LM | Up | 1000 Mbps | 192.168.1.132 | Primary |
| Ethernet | Intel I210 Gigabit | Disconnected | — | 169.254.255.230 | Unused |
| Wi-Fi | Intel Wi-Fi 6E AX211 160MHz | Disconnected | — | 169.254.18.95 | Not in use |

## Platform Analysis

| Aspect | Assessment |
|--------|-----------|
| **CPU** | i9-13900 Raptor Lake — excellent single and multi-threaded performance. P-cores turbo to ~5.6 GHz. Well-suited for simulation, CAD, and compute workloads. |
| **RAM** | 16 GB DDR5 @ 4800 MHz — adequate for most tasks. Could be a bottleneck for large simulations (e.g. COMSOL, OpenFOAM). Max capacity likely 64 GB+. |
| **GPU** | NVIDIA T1000 8GB — professional Turing GPU (not a spare T400). Already installed. Supports 4 display outputs. Good for CAD/visualization; not a gaming or CUDA-heavy card. |
| **Storage** | 512 GB Samsung NVMe PM9A1 — fast, healthy. Single drive with no redundancy. Adequate for a workstation. |
| **Motherboard** | LENOVO 1066 — likely ThinkStation P-series. Firmware from Sep 2023, check for updates. |
| **Network** | Intel I225-LM 2.5 GbE (running at 1 Gbps) + I210 GbE. Wi-Fi 6E capable but not in use. Dual wired NICs available for bonding or secondary subnet. |
| **OS** | Windows 11 Pro — corporate workstation. Check for active domain/corporate policies before repurposing. |

## Pending Actions

- [ ] Check available RAM slots and max RAM capacity (likely 2x SODIMM or 4x DIMM)
- [ ] Verify GPU PCIe slot availability if additional T400 card considered
- [ ] Check for Lenovo firmware updates (current: S0JKT12A, 2023-09-07)
- [ ] Fix storage detection in `hardware-assess.ps1` (returned empty object — likely WMI query incompatibility)
- [ ] Confirm corporate domain/AD membership — impacts repurposing options
- [ ] Check existing software installations (CAD tools, Autodesk, etc.)
- [ ] Enable Tailscale VPN for remote access consistency with AceEngineer-01

## Notes

- WRK-050 originally listed GPU as "8 GB graphics card" — confirmed **NVIDIA T1000 8GB** (professional, not spare T400)
- T400 spare GPUs still available for installation elsewhere (AceEngineer-02/03 or other machines)
- Uptime at assessment time: ~12.5 days (1,078,631 seconds)
