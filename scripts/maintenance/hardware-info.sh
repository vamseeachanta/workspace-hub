#!/usr/bin/env bash
# hardware-info.sh — Collect machine specs for workstations registry
#
# Usage:
#   ./scripts/maintenance/hardware-info.sh
#   ./scripts/maintenance/hardware-info.sh --json   # JSON output for scripting
#
# Outputs: hostname, OS, CPU, RAM, disks, GPUs — formatted for SKILL.md table.
# Run on each machine; paste results into workstations/SKILL.md.

set -euo pipefail

JSON=false
[[ "${1:-}" == "--json" ]] && JSON=true

# ── helpers ────────────────────────────────────────────────────────────────────

cmd_exists() { command -v "$1" >/dev/null 2>&1; }

get_hostname()  { hostname -s 2>/dev/null || hostname; }
get_os()        { . /etc/os-release 2>/dev/null && echo "${PRETTY_NAME:-$(uname -s)}" || uname -s; }
get_kernel()    { uname -r; }

get_cpu() {
    if [[ -f /proc/cpuinfo ]]; then
        local model cores threads
        model=$(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2 | xargs)
        cores=$(grep -c '^processor' /proc/cpuinfo)
        threads=$(grep -m1 'siblings' /proc/cpuinfo | awk '{print $3}' 2>/dev/null || echo "$cores")
        echo "${model} (${cores}c/${threads}t)"
    elif cmd_exists sysctl; then
        sysctl -n machdep.cpu.brand_string 2>/dev/null || echo "unknown"
    else
        echo "unknown"
    fi
}

get_ram() {
    if cmd_exists free; then
        free -h | awk '/^Mem:/ {print $2 " total, " $3 " used"}'
    else
        echo "unknown"
    fi
}

get_ram_type() {
    if cmd_exists dmidecode; then
        sudo dmidecode -t memory 2>/dev/null \
            | grep -E '^\s+(Type|Speed|Size):' \
            | grep -v 'No Module' \
            | head -6 \
            | xargs \
            || echo "(run as root for RAM type)"
    else
        echo "(dmidecode not available)"
    fi
}

get_disks() {
    if cmd_exists lsblk; then
        lsblk -d -o NAME,SIZE,TYPE,ROTA,MODEL \
            | grep -v 'loop\|sr[0-9]' \
            | column -t
    elif cmd_exists df; then
        df -h --output=source,fstype,size,used,avail,target 2>/dev/null \
            | grep -v tmpfs \
            | head -20
    else
        echo "unknown"
    fi
}

get_gpus() {
    local gpus=""
    if cmd_exists lspci; then
        gpus=$(lspci | grep -iE 'vga|3d|display' || true)
    fi
    if cmd_exists nvidia-smi; then
        local nv
        nv=$(nvidia-smi --query-gpu=name,memory.total,driver_version \
                 --format=csv,noheader 2>/dev/null || true)
        [[ -n "$nv" ]] && gpus="${gpus}
nvidia-smi: ${nv}"
    fi
    echo "${gpus:-none detected}"
}

get_network() {
    if cmd_exists ip; then
        ip -brief addr show | grep -v '^lo' | awk '{print $1, $3}' | head -5
    elif cmd_exists ifconfig; then
        ifconfig | grep -E '^[a-z]|inet ' | grep -v 'lo' | head -10
    else
        echo "unknown"
    fi
}

# ── output ─────────────────────────────────────────────────────────────────────

HOSTNAME=$(get_hostname)
OS=$(get_os)
KERNEL=$(get_kernel)
CPU=$(get_cpu)
RAM=$(get_ram)
RAM_TYPE=$(get_ram_type)
GPUS=$(get_gpus)

if $JSON; then
    DISKS_RAW=$(get_disks | tr '\n' '|')
    GPUS_RAW=$(echo "$GPUS" | tr '\n' '|')
    cat <<EOF
{
  "hostname": "${HOSTNAME}",
  "os": "${OS}",
  "kernel": "${KERNEL}",
  "cpu": "${CPU}",
  "ram": "${RAM}",
  "ram_type": "${RAM_TYPE}",
  "gpus": "${GPUS_RAW}",
  "disks": "${DISKS_RAW}"
}
EOF
    exit 0
fi

cat <<EOF
════════════════════════════════════════════════════════════
  Hardware Info: ${HOSTNAME}
════════════════════════════════════════════════════════════

Hostname : ${HOSTNAME}
OS       : ${OS}
Kernel   : ${KERNEL}

── CPU ──────────────────────────────────────────────────────
${CPU}

── RAM ──────────────────────────────────────────────────────
${RAM}
Type: ${RAM_TYPE}

── GPU(s) ───────────────────────────────────────────────────
${GPUS}

── Disks ────────────────────────────────────────────────────
$(get_disks)

── Network interfaces ───────────────────────────────────────
$(get_network)

════════════════════════════════════════════════════════════
  Workstations SKILL.md table row (fill in Nickname + Use):
════════════════════════════════════════════════════════════
| (nickname) | ${OS} | (primary use) | ${CPU} / ${RAM} |

EOF
