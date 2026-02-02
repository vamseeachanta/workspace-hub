#!/bin/bash
set -euo pipefail
# ABOUTME: Cross-platform hardware assessment script (Linux). Collects CPU, RAM, GPU, storage, motherboard, network, and OS info into structured JSON.

SCRIPT_VERSION="1.0.0"
SCHEMA_VERSION="1.0"

# ── Defaults ──────────────────────────────────────────────────────────
OUTPUT_FILE=""
PRETTY=0
QUIET=0

# ── Color Logging ─────────────────────────────────────────────────────
_CLR_BLUE='\033[0;34m'
_CLR_YELLOW='\033[0;33m'
_CLR_RED='\033[0;31m'
_CLR_RESET='\033[0m'

log_info() {
    [[ "$QUIET" -eq 1 ]] && return
    printf "${_CLR_BLUE}[INFO]${_CLR_RESET} %s\n" "$*" >&2
}

log_warn() {
    [[ "$QUIET" -eq 1 ]] && return
    printf "${_CLR_YELLOW}[WARN]${_CLR_RESET} %s\n" "$*" >&2
}

log_error() {
    printf "${_CLR_RED}[ERROR]${_CLR_RESET} %s\n" "$*" >&2
}

# ── JSON Escape Helper ────────────────────────────────────────────────
json_escape() {
    local s="$1"
    s="${s//\\/\\\\}"
    s="${s//\"/\\\"}"
    # Remove control characters (tabs, newlines, carriage returns)
    s="$(printf '%s' "$s" | tr -d '\000-\011\013-\037')"
    printf '%s' "$s"
}

# ── Usage / Help ──────────────────────────────────────────────────────
usage() {
    cat <<'HELPEOF'
Usage: hardware-assess.sh [OPTIONS]

Collect hardware specifications and output a unified JSON file.

Options:
  -o, --output FILE   Override output file path
  -p, --pretty        Pretty-print JSON (requires jq or python3)
  -q, --quiet         Suppress log messages
  -h, --help          Show this help message

Output:
  By default writes to ./hardware-assessment-<HOSTNAME>-<YYYYMMDD>.json

Examples:
  hardware-assess.sh
  hardware-assess.sh -o /tmp/hw.json --pretty
  hardware-assess.sh -q -o report.json
HELPEOF
}

# ── CLI Argument Parsing ──────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -p|--pretty)
            PRETTY=1
            shift
            ;;
        -q|--quiet)
            QUIET=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# ── Collect CPU ───────────────────────────────────────────────────────
collect_cpu() {
    local model="" architecture="" sockets=0 cores_per_socket=0
    local total_cores=0 threads_per_core=0 total_threads=0
    local max_mhz="" l3_cache=""

    if command -v lscpu &>/dev/null; then
        local lscpu_out
        lscpu_out="$(lscpu 2>/dev/null)" || lscpu_out=""

        model="$(printf '%s\n' "$lscpu_out" | grep -i '^Model name:' | sed 's/^[^:]*:[[:space:]]*//' | head -1)"
        architecture="$(printf '%s\n' "$lscpu_out" | grep -i '^Architecture:' | sed 's/^[^:]*:[[:space:]]*//' | head -1)"
        sockets="$(printf '%s\n' "$lscpu_out" | grep -i '^Socket(s):' | sed 's/^[^:]*:[[:space:]]*//' | head -1)"
        cores_per_socket="$(printf '%s\n' "$lscpu_out" | grep -i '^Core(s) per socket:' | sed 's/^[^:]*:[[:space:]]*//' | head -1)"
        threads_per_core="$(printf '%s\n' "$lscpu_out" | grep -i '^Thread(s) per core:' | sed 's/^[^:]*:[[:space:]]*//' | head -1)"
        max_mhz="$(printf '%s\n' "$lscpu_out" | grep -i '^CPU max MHz:' | sed 's/^[^:]*:[[:space:]]*//' | head -1)"
        l3_cache="$(printf '%s\n' "$lscpu_out" | grep -i '^L3 cache:' | sed 's/^[^:]*:[[:space:]]*//' | head -1)"

        # Sanitize numerics
        sockets="${sockets:-0}"
        cores_per_socket="${cores_per_socket:-0}"
        threads_per_core="${threads_per_core:-0}"
        [[ "$sockets" =~ ^[0-9]+$ ]] || sockets=0
        [[ "$cores_per_socket" =~ ^[0-9]+$ ]] || cores_per_socket=0
        [[ "$threads_per_core" =~ ^[0-9]+$ ]] || threads_per_core=0

        total_cores=$(( sockets * cores_per_socket ))
        total_threads=$(( total_cores * threads_per_core ))
    else
        log_warn "lscpu not found, CPU info will be incomplete"
    fi

    local esc_model esc_arch esc_mhz esc_l3
    esc_model="$(json_escape "${model:-unknown}")"
    esc_arch="$(json_escape "${architecture:-unknown}")"
    esc_mhz="$(json_escape "${max_mhz:-unknown}")"
    esc_l3="$(json_escape "${l3_cache:-unknown}")"

    printf '{"model":"%s","architecture":"%s","sockets":%d,"cores_per_socket":%d,"total_cores":%d,"threads_per_core":%d,"total_threads":%d,"max_mhz":"%s","l3_cache":"%s"}' \
        "$esc_model" "$esc_arch" "$sockets" "$cores_per_socket" \
        "$total_cores" "$threads_per_core" "$total_threads" \
        "$esc_mhz" "$esc_l3"
}

# ── Collect Memory ────────────────────────────────────────────────────
collect_memory() {
    local total_kb=0 total_gb="0.0" mem_type="unknown" mem_speed="unknown"

    if [[ -r /proc/meminfo ]]; then
        total_kb="$(grep -i '^MemTotal:' /proc/meminfo | awk '{print $2}')"
        total_kb="${total_kb:-0}"
        [[ "$total_kb" =~ ^[0-9]+$ ]] || total_kb=0
        total_gb="$(awk "BEGIN { printf \"%.1f\", $total_kb / 1048576 }")"
    else
        log_warn "/proc/meminfo not readable, memory info will be incomplete"
    fi

    if [[ $EUID -eq 0 ]] && command -v dmidecode &>/dev/null; then
        local dmi_out
        dmi_out="$(dmidecode -t memory 2>/dev/null)" || dmi_out=""
        if [[ -n "$dmi_out" ]]; then
            mem_type="$(printf '%s\n' "$dmi_out" | grep -i '^\s*Type:' | grep -vi 'Type Detail' | head -1 | sed 's/^[^:]*:[[:space:]]*//')"
            mem_speed="$(printf '%s\n' "$dmi_out" | grep -i '^\s*Speed:' | grep -vi 'Configured' | head -1 | sed 's/^[^:]*:[[:space:]]*//')"
            [[ -z "$mem_type" ]] && mem_type="unknown"
            [[ -z "$mem_speed" ]] && mem_speed="unknown"
        fi
    fi

    local esc_gb esc_type esc_speed
    esc_gb="$(json_escape "$total_gb")"
    esc_type="$(json_escape "$mem_type")"
    esc_speed="$(json_escape "$mem_speed")"

    printf '{"total_kb":%d,"total_gb":"%s","type":"%s","speed":"%s"}' \
        "$total_kb" "$esc_gb" "$esc_type" "$esc_speed"
}

# ── Collect GPU ───────────────────────────────────────────────────────
collect_gpu() {
    local gpu_json_entries=()

    if command -v lspci &>/dev/null; then
        local has_nvidia_smi=0
        command -v nvidia-smi &>/dev/null && has_nvidia_smi=1

        local nvidia_driver=""
        local -A nvidia_vram_map=()

        if [[ "$has_nvidia_smi" -eq 1 ]]; then
            nvidia_driver="$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -1 | tr -d '[:space:]')" || nvidia_driver=""
            while IFS=, read -r gpu_name vram; do
                gpu_name="$(printf '%s' "$gpu_name" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
                vram="$(printf '%s' "$vram" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//;s/ MiB//')"
                [[ -n "$gpu_name" ]] && nvidia_vram_map["$gpu_name"]="$vram"
            done < <(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || true)
        fi

        while IFS= read -r line; do
            [[ -z "$line" ]] && continue
            local pci_id="" gpu_name=""
            # Extract PCI ID (e.g., 01:00.0)
            pci_id="$(printf '%s' "$line" | grep -oP '^\S+')"
            # Extract GPU name — everything after the class code bracket ']:' or '] '
            gpu_name="$(printf '%s' "$line" | sed 's/^[^]]*\][: ]*//')"
            # Strip trailing PCI device IDs like [10de:2204] and revision info
            gpu_name="$(printf '%s' "$gpu_name" | sed 's/ \[[0-9a-fA-F]*:[0-9a-fA-F]*\]//g; s/ (rev [0-9a-fA-F]*)$//')"

            local esc_name esc_pci esc_driver vram_val="null"
            esc_name="$(json_escape "$gpu_name")"
            esc_pci="$(json_escape "$pci_id")"

            # Try to match nvidia-smi data
            local driver_str="unknown"
            if [[ "$has_nvidia_smi" -eq 1 ]]; then
                driver_str="${nvidia_driver:-unknown}"
                # Try to find VRAM match — strip vendor prefix for flexible matching
                for nv_name in "${!nvidia_vram_map[@]}"; do
                    local nv_model="${nv_name#NVIDIA }"
                    if printf '%s' "$gpu_name" | grep -qiF "$nv_model"; then
                        local vram_raw="${nvidia_vram_map[$nv_name]}"
                        if [[ "$vram_raw" =~ ^[0-9]+$ ]]; then
                            vram_val="$vram_raw"
                        fi
                        break
                    fi
                done
            fi
            esc_driver="$(json_escape "$driver_str")"

            gpu_json_entries+=("$(printf '{"name":"%s","pci_id":"%s","vram_mb":%s,"driver_version":"%s"}' \
                "$esc_name" "$esc_pci" "$vram_val" "$esc_driver")")
        done < <(lspci -nn 2>/dev/null | grep -iE 'VGA|3D controller' || true)
    else
        log_warn "lspci not found, GPU info will be incomplete"
    fi

    if [[ ${#gpu_json_entries[@]} -eq 0 ]]; then
        printf '[]'
    else
        local joined=""
        for i in "${!gpu_json_entries[@]}"; do
            [[ $i -gt 0 ]] && joined+=","
            joined+="${gpu_json_entries[$i]}"
        done
        printf '[%s]' "$joined"
    fi
}

# ── Collect Storage ───────────────────────────────────────────────────
collect_storage() {
    local storage_entries=()

    if ! command -v lsblk &>/dev/null; then
        log_warn "lsblk not found, storage info will be incomplete"
        printf '[]'
        return
    fi

    local has_smartctl=0
    [[ $EUID -eq 0 ]] && command -v smartctl &>/dev/null && has_smartctl=1

    while IFS= read -r line; do
        [[ -z "$line" ]] && continue
        local dev_name="" dev_size="" dev_model="" dev_serial="" dev_tran="" dev_type=""
        # Use -P (key=value pairs) output for safe parsing of fields with spaces
        eval "$(printf '%s' "$line" | sed 's/NAME=/dev_name=/; s/SIZE=/dev_size=/; s/MODEL=/dev_model=/; s/SERIAL=/dev_serial=/; s/TRAN=/dev_tran=/; s/TYPE=/dev_type=/')"

        [[ "$dev_type" != "disk" ]] && continue
        # Skip zero-size virtual devices
        [[ "$dev_size" == "0B" || -z "$dev_size" ]] && continue

        local device="/dev/$dev_name"
        local smart_status="unavailable" smart_temp="null" smart_hours="null"

        if [[ "$has_smartctl" -eq 1 ]]; then
            local smart_out
            smart_out="$(smartctl -a "$device" 2>/dev/null)" || smart_out=""
            if [[ -n "$smart_out" ]]; then
                local status_line
                status_line="$(printf '%s\n' "$smart_out" | grep -i 'SMART overall-health' | head -1)"
                if printf '%s' "$status_line" | grep -qi 'PASSED'; then
                    smart_status="PASSED"
                elif printf '%s' "$status_line" | grep -qi 'FAILED'; then
                    smart_status="FAILED"
                elif [[ -n "$status_line" ]]; then
                    smart_status="$(printf '%s' "$status_line" | sed 's/^.*: *//')"
                fi

                # Temperature (ID 194)
                local temp_line
                temp_line="$(printf '%s\n' "$smart_out" | grep -E '^\s*194\s' | head -1)"
                if [[ -n "$temp_line" ]]; then
                    local temp_val
                    temp_val="$(printf '%s' "$temp_line" | awk '{print $NF}')"
                    [[ "$temp_val" =~ ^[0-9]+$ ]] && smart_temp="$temp_val"
                fi

                # Power-On Hours (ID 9)
                local hours_line
                hours_line="$(printf '%s\n' "$smart_out" | grep -E '^\s*9\s' | head -1)"
                if [[ -n "$hours_line" ]]; then
                    local hours_val
                    hours_val="$(printf '%s' "$hours_line" | awk '{print $NF}')"
                    [[ "$hours_val" =~ ^[0-9]+$ ]] && smart_hours="$hours_val"
                fi
            fi
        fi

        local esc_device esc_size esc_model esc_serial esc_type esc_tran esc_smart_status
        esc_device="$(json_escape "$device")"
        esc_size="$(json_escape "${dev_size:-unknown}")"
        esc_model="$(json_escape "${dev_model:-unknown}")"
        esc_serial="$(json_escape "${dev_serial:-unknown}")"
        esc_type="$(json_escape "${dev_type}")"
        esc_tran="$(json_escape "${dev_tran:-unknown}")"
        esc_smart_status="$(json_escape "$smart_status")"

        storage_entries+=("$(printf '{"device":"%s","size":"%s","model":"%s","serial":"%s","type":"%s","transport":"%s","smart":{"status":"%s","temperature_c":%s,"power_on_hours":%s}}' \
            "$esc_device" "$esc_size" "$esc_model" "$esc_serial" \
            "$esc_type" "$esc_tran" "$esc_smart_status" "$smart_temp" "$smart_hours")")
    done < <(lsblk -dPno NAME,SIZE,MODEL,SERIAL,TRAN,TYPE 2>/dev/null || true)

    if [[ ${#storage_entries[@]} -eq 0 ]]; then
        printf '[]'
    else
        local joined=""
        for i in "${!storage_entries[@]}"; do
            [[ $i -gt 0 ]] && joined+=","
            joined+="${storage_entries[$i]}"
        done
        printf '[%s]' "$joined"
    fi
}

# ── Collect Motherboard ──────────────────────────────────────────────
collect_motherboard() {
    local vendor="unknown" model="unknown" fw_version="unknown" fw_date="unknown"

    if [[ $EUID -eq 0 ]] && command -v dmidecode &>/dev/null; then
        local dmi_out
        dmi_out="$(dmidecode -t baseboard 2>/dev/null)" || dmi_out=""
        if [[ -n "$dmi_out" ]]; then
            vendor="$(printf '%s\n' "$dmi_out" | grep -i '^\s*Manufacturer:' | head -1 | sed 's/^[^:]*:[[:space:]]*//')"
            model="$(printf '%s\n' "$dmi_out" | grep -i '^\s*Product Name:' | head -1 | sed 's/^[^:]*:[[:space:]]*//')"
        fi

        local bios_out
        bios_out="$(dmidecode -t bios 2>/dev/null)" || bios_out=""
        if [[ -n "$bios_out" ]]; then
            fw_version="$(printf '%s\n' "$bios_out" | grep -i '^\s*Version:' | head -1 | sed 's/^[^:]*:[[:space:]]*//')"
            fw_date="$(printf '%s\n' "$bios_out" | grep -i '^\s*Release Date:' | head -1 | sed 's/^[^:]*:[[:space:]]*//')"
        fi
    fi

    # Fallback to sysfs
    if [[ "$vendor" == "unknown" || -z "$vendor" ]] && [[ -r /sys/class/dmi/id/board_vendor ]]; then
        vendor="$(cat /sys/class/dmi/id/board_vendor 2>/dev/null)" || vendor="unknown"
    fi
    if [[ "$model" == "unknown" || -z "$model" ]] && [[ -r /sys/class/dmi/id/board_name ]]; then
        model="$(cat /sys/class/dmi/id/board_name 2>/dev/null)" || model="unknown"
    fi
    if [[ "$fw_version" == "unknown" || -z "$fw_version" ]] && [[ -r /sys/class/dmi/id/bios_version ]]; then
        fw_version="$(cat /sys/class/dmi/id/bios_version 2>/dev/null)" || fw_version="unknown"
    fi
    if [[ "$fw_date" == "unknown" || -z "$fw_date" ]] && [[ -r /sys/class/dmi/id/bios_date ]]; then
        fw_date="$(cat /sys/class/dmi/id/bios_date 2>/dev/null)" || fw_date="unknown"
    fi

    [[ -z "$vendor" ]] && vendor="unknown"
    [[ -z "$model" ]] && model="unknown"
    [[ -z "$fw_version" ]] && fw_version="unknown"
    [[ -z "$fw_date" ]] && fw_date="unknown"

    local esc_vendor esc_model esc_fw esc_date
    esc_vendor="$(json_escape "$vendor")"
    esc_model="$(json_escape "$model")"
    esc_fw="$(json_escape "$fw_version")"
    esc_date="$(json_escape "$fw_date")"

    printf '{"vendor":"%s","model":"%s","firmware_version":"%s","firmware_date":"%s"}' \
        "$esc_vendor" "$esc_model" "$esc_fw" "$esc_date"
}

# ── Collect Network ──────────────────────────────────────────────────
collect_network() {
    local net_entries=()

    if ! command -v ip &>/dev/null; then
        log_warn "ip command not found, network info will be incomplete"
        printf '[]'
        return
    fi

    # Get list of interfaces (skip loopback)
    local ifaces
    ifaces="$(ip -o link show 2>/dev/null | awk -F': ' '{print $2}' | grep -v '^lo$' | sed 's/@.*//')" || ifaces=""

    while IFS= read -r iface; do
        [[ -z "$iface" ]] && continue

        local mac="" state="" mtu="" speed_mbps="null" ipv4="" driver=""

        # Get state, mtu, mac from ip link show
        local link_line
        link_line="$(ip -o link show "$iface" 2>/dev/null)" || link_line=""
        if [[ -n "$link_line" ]]; then
            state="$(printf '%s' "$link_line" | grep -oP 'state \K\S+')" || state="unknown"
            mtu="$(printf '%s' "$link_line" | grep -oP 'mtu \K[0-9]+')" || mtu="0"
            mac="$(printf '%s' "$link_line" | grep -oP 'link/\S+ \K[0-9a-fA-F:]{17}')" || mac=""
        fi
        [[ -z "$state" ]] && state="unknown"
        [[ -z "$mtu" || ! "$mtu" =~ ^[0-9]+$ ]] && mtu=0
        [[ -z "$mac" ]] && mac="unknown"

        # Get speed from sysfs
        if [[ -r "/sys/class/net/$iface/speed" ]]; then
            local spd
            spd="$(cat "/sys/class/net/$iface/speed" 2>/dev/null)" || spd=""
            if [[ "$spd" =~ ^-?[0-9]+$ ]] && [[ "$spd" -gt 0 ]]; then
                speed_mbps="$spd"
            fi
        fi

        # Get IPv4 address
        ipv4="$(ip -o -4 addr show "$iface" 2>/dev/null | awk '{print $4}' | head -1)" || ipv4=""
        [[ -z "$ipv4" ]] && ipv4="none"

        # Get driver from sysfs
        if [[ -L "/sys/class/net/$iface/device/driver" ]]; then
            driver="$(basename "$(readlink -f "/sys/class/net/$iface/device/driver" 2>/dev/null)")" || driver="unknown"
        else
            driver="unknown"
        fi

        local esc_name esc_mac esc_state esc_ipv4 esc_driver
        esc_name="$(json_escape "$iface")"
        esc_mac="$(json_escape "$mac")"
        esc_state="$(json_escape "$state")"
        esc_ipv4="$(json_escape "$ipv4")"
        esc_driver="$(json_escape "$driver")"

        net_entries+=("$(printf '{"name":"%s","mac":"%s","state":"%s","mtu":%d,"speed_mbps":%s,"ipv4":"%s","driver":"%s"}' \
            "$esc_name" "$esc_mac" "$esc_state" "$mtu" "$speed_mbps" "$esc_ipv4" "$esc_driver")")
    done <<< "$ifaces"

    if [[ ${#net_entries[@]} -eq 0 ]]; then
        printf '[]'
    else
        local joined=""
        for i in "${!net_entries[@]}"; do
            [[ $i -gt 0 ]] && joined+=","
            joined+="${net_entries[$i]}"
        done
        printf '[%s]' "$joined"
    fi
}

# ── Collect OS ────────────────────────────────────────────────────────
collect_os() {
    local os_name="unknown" kernel="" arch="" hn="" uptime_sec=0

    # OS name from /etc/os-release
    if [[ -r /etc/os-release ]]; then
        os_name="$(. /etc/os-release && printf '%s' "${PRETTY_NAME:-$NAME}")" || os_name="unknown"
    fi

    kernel="$(uname -r 2>/dev/null)" || kernel="unknown"
    arch="$(uname -m 2>/dev/null)" || arch="unknown"
    hn="$(hostname 2>/dev/null)" || hn="unknown"

    if [[ -r /proc/uptime ]]; then
        local raw_uptime
        raw_uptime="$(awk '{print $1}' /proc/uptime 2>/dev/null)" || raw_uptime="0"
        uptime_sec="${raw_uptime%%.*}"
        [[ "$uptime_sec" =~ ^[0-9]+$ ]] || uptime_sec=0
    fi

    local esc_name esc_kernel esc_arch esc_hn
    esc_name="$(json_escape "$os_name")"
    esc_kernel="$(json_escape "$kernel")"
    esc_arch="$(json_escape "$arch")"
    esc_hn="$(json_escape "$hn")"

    printf '{"name":"%s","kernel":"%s","architecture":"%s","hostname":"%s","uptime_seconds":%d}' \
        "$esc_name" "$esc_kernel" "$esc_arch" "$esc_hn" "$uptime_sec"
}

# ── Main ──────────────────────────────────────────────────────────────
main() {
    local hn
    hn="$(hostname 2>/dev/null || printf 'unknown')"
    local datestamp
    datestamp="$(date +%Y%m%d)"

    if [[ -z "$OUTPUT_FILE" ]]; then
        OUTPUT_FILE="./hardware-assessment-${hn}-${datestamp}.json"
    fi

    log_info "Hardware assessment v${SCRIPT_VERSION} starting"
    log_info "Output file: ${OUTPUT_FILE}"

    log_info "Collecting CPU info..."
    local cpu_json
    cpu_json="$(collect_cpu)"

    log_info "Collecting memory info..."
    local mem_json
    mem_json="$(collect_memory)"

    log_info "Collecting GPU info..."
    local gpu_json
    gpu_json="$(collect_gpu)"

    log_info "Collecting storage info..."
    local storage_json
    storage_json="$(collect_storage)"

    log_info "Collecting motherboard info..."
    local mobo_json
    mobo_json="$(collect_motherboard)"

    log_info "Collecting network info..."
    local net_json
    net_json="$(collect_network)"

    log_info "Collecting OS info..."
    local os_json
    os_json="$(collect_os)"

    local timestamp
    timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

    local esc_sv esc_schv esc_ts
    esc_sv="$(json_escape "$SCRIPT_VERSION")"
    esc_schv="$(json_escape "$SCHEMA_VERSION")"
    esc_ts="$(json_escape "$timestamp")"

    local full_json
    full_json="$(printf '{"schema_version":"%s","script_version":"%s","platform":"linux","timestamp":"%s","cpu":%s,"memory":%s,"gpu":%s,"storage":%s,"motherboard":%s,"network":%s,"os":%s}' \
        "$esc_schv" "$esc_sv" "$esc_ts" \
        "$cpu_json" "$mem_json" "$gpu_json" \
        "$storage_json" "$mobo_json" "$net_json" "$os_json")"

    printf '%s\n' "$full_json" > "$OUTPUT_FILE"

    # Pretty-print if requested
    if [[ "$PRETTY" -eq 1 ]]; then
        if command -v jq &>/dev/null; then
            local tmp_file="${OUTPUT_FILE}.tmp"
            if jq '.' "$OUTPUT_FILE" > "$tmp_file" 2>/dev/null; then
                mv "$tmp_file" "$OUTPUT_FILE"
                log_info "Pretty-printed with jq"
            else
                rm -f "$tmp_file"
                log_warn "jq pretty-print failed, keeping compact JSON"
            fi
        elif command -v python3 &>/dev/null; then
            local tmp_file="${OUTPUT_FILE}.tmp"
            if python3 -m json.tool "$OUTPUT_FILE" > "$tmp_file" 2>/dev/null; then
                mv "$tmp_file" "$OUTPUT_FILE"
                log_info "Pretty-printed with python3"
            else
                rm -f "$tmp_file"
                log_warn "python3 pretty-print failed, keeping compact JSON"
            fi
        else
            log_warn "--pretty requested but neither jq nor python3 available"
        fi
    fi

    local file_size
    file_size="$(wc -c < "$OUTPUT_FILE" 2>/dev/null | tr -d '[:space:]')"

    log_info "Assessment complete: ${OUTPUT_FILE} (${file_size} bytes)"
    log_info "Sections: cpu, memory, gpu, storage, motherboard, network, os"
}

main "$@"
