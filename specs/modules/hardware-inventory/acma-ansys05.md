---
title: "ACMA-ANSYS05 Hardware Assessment"
device: ACMA-ANSYS05
hostname: ACMA-ANSYS05
assessed_date: 2026-02-20
assessed_by: hardware-assess.ps1 v1.0.0 + manual supplementation
work_item: WRK-050
---

# ACMA-ANSYS05 — Hardware Assessment

> Assessed 2026-02-20 using `hardware-assess.ps1 v1.0.0` on Windows 11 Pro
> **Role**: OrcaFlex / OrcaWave / ANSYS / AQWA licensed engineering simulation server

## Summary

| Component | Specification |
|-----------|---------------|
| CPU | 2× Intel Xeon Platinum 8562Y+ (Sapphire Rapids), 32 cores/socket, **64 cores / 64 threads** |
| Base Clock | 2800 MHz (turbo ~3.6–4.0 GHz) |
| L3 Cache | 120 MB |
| Architecture | x64 |
| RAM | **256 GB DDR5 @ 4800 MHz** |
| GPU (management) | ASPEED Graphics Family — BMC/IPMI chip, 16 MB (server remote-management only) |
| Discrete GPU | None detected |
| Motherboard | Supermicro X13DEI (dual-socket Sapphire Rapids), firmware 2.5 (2025-02-10) |
| OS | Microsoft Windows 11 Pro, Build 10.0.26100 |
| Uptime at assessment | ~22 days 18 hours |

## Storage

| # | Device | Size | Model | Type | Health |
|---|--------|------|-------|------|--------|
| 1–6 | SATA SSD ×6 | 500 GB each | Samsung SSD 870 EVO 500GB | SSD | Healthy |
| 7–8 | SATA SSD ×2 | 1.92 TB each | Micron 5400 MTFDDAK1T9TGA | SSD | Healthy |

**Total raw storage: ~6.7 TB across 8 SSDs (all SATA)**

*Note: Storage detection in `hardware-assess.ps1` returned empty due to type conversion error — supplemented via `Get-PhysicalDisk` directly.*

## Network

| Interface | Driver | State | Speed | IPv4 | Notes |
|-----------|--------|-------|-------|------|-------|
| Ethernet 3 | Supermicro GbE | Up | 1000 Mbps | 192.168.0.184 | Primary |
| Ethernet 2 | Supermicro GbE | Up | 1000 Mbps | 192.168.0.95 | Secondary / bonding |
| Ethernet | Remote NDIS | Up | 426 Mbps | 169.254.3.1 | Internet sharing |

*Dual Supermicro GbE NICs — could be bonded for 2 Gbps aggregate or used for separate subnets.*

## Licensed Software (on this machine)

| Software | Vendor | Notes |
|----------|--------|-------|
| OrcaFlex | Orcina | Structural/mooring dynamics |
| OrcaWave | Orcina | Diffraction / wave loads |
| ANSYS | ANSYS Inc. | FEA / multi-physics |
| AQWA | ANSYS Inc. | Hydrodynamics / diffraction (v252 confirmed) |

## Platform Analysis

| Aspect | Assessment |
|--------|-----------|
| **CPU** | Dual Xeon Platinum 8562Y+ — server-class Sapphire Rapids. 64 physical cores make this excellent for parallel FEA (ANSYS), batch OrcaFlex runs, and multi-case hydrodynamic analysis. |
| **RAM** | 256 GB DDR5 @ 4800 MHz — very large capacity, well-suited for large ANSYS models, OpenFOAM, and memory-intensive hydrodynamic meshes. No bottleneck expected. |
| **GPU** | ASPEED is purely a BMC management chip — no CUDA or compute GPU present. GPU-accelerated solvers (ANSYS GPU solver, CUDA) are not available without adding a discrete card. |
| **Storage** | 8× SSDs (~6.7 TB) — high-capacity, fast SATA SSDs. No RAID configuration confirmed; check Windows Storage Spaces or hardware RAID for redundancy. |
| **Motherboard** | Supermicro X13DEI — enterprise dual-socket board with PCIe 5.0. Firmware recently updated (Feb 2025). PCIe slots available for GPU or NVMe expansion cards. |
| **Network** | Dual GbE, both active on 192.168.0.x subnet. Consider bonding for throughput or designating one for management. |
| **Role fit** | Ideal primary machine for all licensed engineering simulation work: OrcaFlex/OrcaWave batch runs, ANSYS/AQWA analysis. High core count enables parallel parametric studies. |

## Pending Actions

- [ ] Confirm storage RAID/pool configuration (are the 8 SSDs independent, RAID, or Storage Spaces?)
- [ ] Check PCIe slot availability — Supermicro X13DEI has PCIe 5.0 slots; a GPU (e.g. RTX / A-series) would enable ANSYS GPU acceleration
- [ ] Verify OrcaFlex / OrcaWave license server config (node-locked vs. floating, license server host)
- [ ] Check ANSYS / AQWA license server config
- [ ] Evaluate adding a CUDA-capable GPU for ANSYS GPU solver acceleration
- [ ] Confirm network: are both NICs on same subnet intentionally, or should one be on management VLAN?
- [ ] Enable Tailscale VPN for remote access consistency with AceEngineer-01
- [ ] Document installed software versions (OrcaFlex, OrcaWave, ANSYS, AQWA build numbers)

## Notes

- ASPEED GPU detected by script as only GPU — this is normal for Supermicro server boards; it serves the IPMI/BMC remote console only
- Firmware 2.5 (2025-02-10) is recent — no immediate update needed
- Machine name pattern: `ACMA-ANSYS05` confirms ACMA ownership; ANSYS suffix indicates its primary role
- Raw assessment JSON saved to: `pyproject-starter/hardware-assessment-ACMA-ANSYS05-20260220.json` (to be moved)
