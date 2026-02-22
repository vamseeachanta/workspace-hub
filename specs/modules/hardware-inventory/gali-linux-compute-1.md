---
title: "gali-linux-compute-1 Hardware Assessment"
device: gali-linux-compute-1
hostname: shoerack
assessed_date: 2026-02-22
assessed_by: user-provided specs
work_item: WRK-050
---

# gali-linux-compute-1 (shoerack) — Hardware Assessment

> Last assessed 2026-02-22 via user-provided system query output

## Summary

| Component | Specification |
|-----------|---------------|
| CPU | AMD Ryzen Threadripper PRO 3955WX — 16 cores / 32 threads |
| Base Clock | Up to 3.9 GHz |
| L3 Cache | 64 MiB |
| Architecture | x86_64 |
| RAM | 128 GB DDR4 (125 GiB usable, ~6 GB in use at assessment) |
| GPU | 2x NVIDIA GeForce RTX 3090 24 GB (GA102) + 1x ASPEED BMC/IPMI |
| GPU VRAM Total | 48 GB (2x 24 GB) |
| OS | Ubuntu Linux (kernel 6.8.0-90-generic) |
| Swap | 2 GB (unused) |

## Storage

| Device | Size | Model | Type | Notes |
|--------|------|-------|------|-------|
| nvme0n1 | 931.5 GB | Samsung SSD 980 PRO 1TB | NVMe SSD | Boot drive — **89% used (critical)** |
| nvme1n1 | 465.8 GB | WD_BLACK SN750 SE 500GB | NVMe SSD | |
| sda | 1.8 TB | Seagate ST2000LM015 | HDD | |

> **⚠ Warning — nvme0n1 (boot drive) at 89% used.** NVMe drives degrade in performance
> and lifespan above ~80% capacity. Recommend freeing space or migrating data to sda/nvme1n1
> before the next heavy compute session.

## SMART Health

SMART data not yet collected. Run on shoerack:
```bash
sudo apt install smartmontools -y
sudo smartctl -a /dev/nvme0n1
sudo smartctl -a /dev/nvme1n1
sudo smartctl -a /dev/sda
```

## Platform Analysis

| Aspect | Assessment |
|--------|-----------|
| **CPU** | Threadripper PRO 3955WX — 16C/32T, workstation-class. Strong single and multi-threaded performance. Lower core count than AceEngineer-01/02 (32T total) but higher IPC and clock speed. |
| **RAM** | 128 GB DDR4 — large capacity, well-suited for big in-memory workloads. |
| **GPU** | Dual RTX 3090 (48 GB VRAM total) — primary strength of this machine. Excellent for ML training, CUDA compute, rendering, simulation with GPU acceleration. |
| **Boot NVMe** | Samsung 980 PRO — fast, but **89% full**. Immediate action recommended. |
| **Secondary NVMe** | WD_BLACK SN750 SE 500GB — available for data offload. |
| **HDD** | 1.8 TB Seagate 2.5" HDD (ST2000LM015) — bulk storage / data staging. |
| **Network** | Not yet assessed. |
| **Role** | Primary GPU compute node — ML training, CUDA workloads, large simulations. Route heavy compute WRK items here. |

## Network / Access

- External machine — access method TBD (SSH, Tailscale VPN, or direct LAN)
- Not yet confirmed on same LAN as ace-linux-1/ace-linux-2

## Consolidation Status (WRK-050)

- [x] Hardware specs documented
- [ ] SMART health check on all drives
- [ ] Network access method confirmed (SSH key, Tailscale, or VPN)
- [ ] Boot drive cleanup — free space on nvme0n1 (currently 89% full)
- [ ] Machine manifest created (`specs/modules/hardware-inventory/manifests/shoerack.yml`)
- [ ] Dev environment check (agent CLIs, workspace-hub clone path)
