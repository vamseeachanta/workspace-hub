# WRK-050 Phase 1: Hardware Assessment Script

## Goal
Build two self-contained scripts (Bash + PowerShell) that collect hardware specs and output a unified JSON file. User copies one file to any machine, runs it, gets structured JSON back.

## Files to Create

| File | Purpose |
|------|---------|
| `scripts/operations/system/hardware-assess.sh` | Linux Bash script |
| `scripts/operations/system/hardware-assess.ps1` | Windows PowerShell script |

## Data Collected (both scripts, identical schema)

CPU, RAM (size + type), GPU (name + VRAM), storage (devices + SMART health), motherboard, network interfaces, OS version.

## Unified JSON Output Schema

```json
{
  "schema_version": "1.0",
  "script_version": "1.0.0",
  "platform": "linux|windows",
  "timestamp": "ISO-8601",
  "cpu": { "model", "architecture", "sockets", "cores_per_socket", "total_cores", "threads_per_core", "total_threads", "max_mhz", "l3_cache" },
  "memory": { "total_kb", "total_gb", "type", "speed" },
  "gpu": [{ "name", "pci_id", "vram_mb", "driver_version" }],
  "storage": [{ "device", "size", "model", "serial", "type", "transport", "smart": { "status", "temperature_c", "power_on_hours" } }],
  "motherboard": { "vendor", "model", "firmware_version", "firmware_date" },
  "network": [{ "name", "mac", "state", "mtu", "speed_mbps", "ipv4", "driver" }],
  "os": { "name", "kernel", "architecture", "hostname", "uptime_seconds" }
}
```

Output file: `./hardware-assessment-<HOSTNAME>-<YYYYMMDD>.json`

## Linux Script Design

- **Zero dependencies** — uses `lscpu`, `lsblk`, `lspci`, `ip`, `/proc/meminfo`, `hostnamectl`, `uname`
- **Optional root** — `dmidecode` (RAM type), `smartctl` (SMART data). Gracefully reports "unknown"/"unavailable" when not root
- **JSON built with printf** — no jq dependency. Pretty-print via jq or python3 if available
- **Workspace conventions** — `#!/bin/bash`, `set -euo pipefail`, `# ABOUTME:` headers, color logging, usage heredoc, while/case arg parsing
- **Flags**: `-o`/`--output`, `-p`/`--pretty`, `-q`/`--quiet`, `-h`/`--help`

### Collection functions
| Function | Primary source | Root fallback |
|----------|---------------|---------------|
| `collect_cpu` | `lscpu` | — |
| `collect_memory` | `/proc/meminfo` | `dmidecode -t memory` for type/speed |
| `collect_gpu` | `lspci` | `nvidia-smi` for VRAM |
| `collect_storage` | `lsblk` | `smartctl` for SMART |
| `collect_motherboard` | `hostnamectl` | `dmidecode -t baseboard` |
| `collect_network` | `ip` + `/sys/class/net/` | — |
| `collect_os` | `hostnamectl` + `uname` | — |

## Windows Script Design

- **Zero dependencies** — all via built-in CIM/WMI cmdlets (PowerShell 5.1+, included in Win 10/11)
- **Flags**: `-OutputFile`, `-Pretty`, `-Quiet`, `-Help`
- `Get-CimInstance` for CPU, RAM, GPU, motherboard, OS
- `Get-PhysicalDisk` + `Get-StorageReliabilityCounter` for storage + SMART
- `Get-NetAdapter` + `Get-NetIPAddress` for network
- Known limitation: `Win32_VideoController.AdapterRAM` caps at 4 GB (uint32). Falls back to `nvidia-smi` for NVIDIA GPUs.

## Implementation Steps

1. Create `hardware-assess.sh` with all collection functions
2. Test on AceEngineer-01 (this machine): non-root + root runs
3. Validate JSON parses cleanly
4. Create `hardware-assess.ps1` with equivalent CIM/WMI functions
5. Update WRK-050 Phase 1 acceptance criteria checkboxes

## Verification

```bash
# 1. Run on current machine (non-root)
bash scripts/operations/system/hardware-assess.sh -p
# 2. Validate JSON
python3 -c "import json; d=json.load(open('hardware-assessment-vamsee-linux1-*.json')); print(list(d.keys()))"
# 3. Check all top-level keys present
# Expected: schema_version, script_version, platform, timestamp, cpu, memory, gpu, storage, motherboard, network, os
# 4. Run with sudo for SMART + RAM type
sudo bash scripts/operations/system/hardware-assess.sh -p
```
