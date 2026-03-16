---
name: workstations-new-workstation-onboarding
description: 'Sub-skill of workstations: New Workstation Onboarding (+1).'
version: 3.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# New Workstation Onboarding (+1)

## New Workstation Onboarding


Run these steps on any new machine to wire it into the workspace-hub ecosystem:

```bash
# 1. Clone workspace-hub
git clone git@github.com:<org>/workspace-hub.git
cd workspace-hub && git submodule update --init --recursive

# 2. Set up SSH key to ace-linux-1 (for state sync)
ssh-keygen -t ed25519 -C "$(hostname)"   # if no key exists
ssh-copy-id vamsee@ace-linux-1

# 3. Install crontab (hostname-aware; --dry-run to preview first)
bash scripts/cron/setup-cron.sh --dry-run
bash scripts/cron/setup-cron.sh

# 4. Linux system tuning (one-time, requires sudo)
echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf && sudo sysctl -p

# 5. Smoke-test readiness
bash scripts/readiness/nightly-readiness.sh
```

After onboarding, add the machine to the registry table and Software Capability Map
above, then commit.


## Windows equivalent (PowerShell)


```powershell
Get-ComputerInfo | Select-Object CsName, OsName, CsTotalPhysicalMemory
Get-WmiObject Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors
Get-WmiObject Win32_DiskDrive | Select-Object Model, Size, MediaType
Get-WmiObject Win32_VideoController | Select-Object Name, AdapterRAM, DriverVersion
```
