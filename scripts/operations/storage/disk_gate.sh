#!/usr/bin/env bash
# Read disk floors without changing running work or pruning caches.
set -uo pipefail
export LC_ALL=C
conf=${DISK_GATE_CONF:-}
json=0
consumers=0
selected=()
while (($#)); do
    case $1 in
        --conf|--mount)
            (($# >= 2)) || exit 2
            if [[ $1 == --conf ]]; then conf=$2; else selected+=("$2"); fi
            shift 2 ;;
        --json) json=1; shift ;;
        --consumers) consumers=1; shift ;;
        *) echo 'Usage: disk_gate.sh --conf FILE [--mount PATH]... [--json] [--consumers]' >&2; exit 2 ;;
    esac
done
[[ -n $conf && -r $conf && -f $conf ]] || { echo 'Settings unreadable' >&2; exit 2; }
# The line format uses whitespace-delimited paths; it is data, never shell code.
awk '
function num(s) { return s ~ /^[0-9]+([.][0-9]+)?$/ }
/^[[:space:]]*(#|$)/ { next }
{
    if ($1=="cache") { if (NF<3) exit 2; start=4; kind="cache" }
    else if ($1=="tmp") { if (NF<2) exit 2; start=3; kind="tmp" }
    else { start=2; kind="disk"; disks++; warn=85; block=90 }
    for(i=start;i<=NF;i++) {
        split($i,a,"="); if(length(a)!=2 || !num(a[2])) exit 2
        if(kind=="disk") {
            if(a[1]=="warn_pct") warn=a[2]+0
            else if(a[1]=="block_pct") block=a[2]+0
            else if(a[1]!="floor_gb") exit 2
        } else if(a[1]!="cap_gb" && !(kind=="tmp" && a[1]=="old_days")) exit 2
    }
    if(kind=="disk" && (warn>=block || block>100)) exit 2
}
END { if(!disks) exit 2 }
' "$conf" || { echo 'Invalid settings' >&2; exit 2; }
quote() {
    local value=$1
    value=${value//\\/\\\\}; value=${value//\"/\\\"}
    value=${value//$'\t'/\\t}; value=${value//$'\r'/\\r}; value=${value//$'\n'/\\n}
    printf '"%s"' "$value"
}
rc=0
blocked=0
mounts=()
names=()
paths=()
caps=()
old_days=3
add_consumer() { names+=("$1"); paths+=("$2"); caps+=("$3"); }
while read -r first rest; do
    [[ -z $first || $first == \#* ]] && continue
    read -r -a words <<< "$rest"
    if [[ $first == cache ]]; then
        name=${words[0]}; path=${words[1]}
        case $name in uv) cap=20;; npm) cap=5;; pip|pre-commit) cap=3;; *) cap=10;; esac
        for word in "${words[@]:2}"; do [[ $word == cap_gb=* ]] && cap=${word#*=}; done
        add_consumer "$name" "$path" "$cap"
    elif [[ $first == tmp ]]; then
        tmp_root=${words[0]}; old_cap=5
        for word in "${words[@]:1}"; do
            case $word in old_days=*) old_days=${word#*=};; cap_gb=*) old_cap=${word#*=};; esac
        done
        add_consumer tmp "$tmp_root" 15
        add_consumer tmp-old "$tmp_root" "$old_cap"
    else
        mounts+=("$first")
    fi
done < "$conf"
for wanted in "${selected[@]}"; do
    found=0
    for mount in "${mounts[@]}"; do [[ $mount == "$wanted" ]] && found=1; done
    ((found)) || { echo 'Requested mount absent from settings' >&2; exit 2; }
done
for mount in "${mounts[@]}"; do
    if ((${#selected[@]})); then
        found=0
        for wanted in "${selected[@]}"; do [[ $mount == "$wanted" ]] && found=1; done
        ((found)) || continue
    fi
    warn=85; block=90; floor=0
    while read -r first rest; do
        [[ $first == "$mount" ]] || continue
        for word in $rest; do
            case $word in warn_pct=*) warn=${word#*=};; block_pct=*) block=${word#*=};; floor_gb=*) floor=${word#*=};; esac
        done
    done < "$conf"
    state=BLOCK
    size=null; used=null; free=null; pct=null; inode=null
    if reading=$(df -Pk -- "$mount" 2>/dev/null); then
        values=$(printf '%s\n' "$reading" | awk 'NR>1 && $2~/^[0-9]+$/ && $3~/^[0-9]+$/ && $4~/^[0-9]+$/ && $5~/^[0-9]+%$/ {gsub(/%/,"",$5); print $2,$3,$4,$5; n++} END {if(n!=1) exit 1}') || values=
        if [[ -n $values ]]; then read -r size used free pct <<< "$values"; fi
    fi
    # Some filesystems expose no inode accounting; an unsupported read stays unknown.
    inode_unavailable=0
    if reading=$(df -Pi -- "$mount" 2>/dev/null); then
        value=$(printf '%s\n' "$reading" | awk 'NR>1 && $2~/^[0-9]+$/ && $3~/^[0-9]+$/ && $4~/^[0-9]+$/ && $5~/^[0-9]+%$/ {gsub(/%/,"",$5); print $5; n++} END {if(n!=1) exit 1}') || value=
        [[ -n $value ]] && inode=$value
        if [[ $inode == null ]] && printf '%s\n' "$reading" | awk 'NR>1 {n++; if(NF==6 && $2=="-" && $3=="-" && $4=="-" && $5=="-") valid++} END {exit !(n==1 && valid==1)}'; then
            inode_unavailable=1
        fi
    fi
    if [[ $size != null ]]; then
        level=$(awk -v p="$pct" -v f="$free" -v i="$inode" -v w="$warn" -v b="$block" -v floor="$floor" 'BEGIN {print (p>=b || f<floor*1048576 || (i!="null" && i>=95)) ? 20 : (p>=w ? 10 : 0)}')
        # A failed inode command is unreadable df, and must fail closed.
        if [[ $inode == null && $inode_unavailable == 0 ]]; then level=20; fi
        case $level in 0) state=OK;; 10) state=WARN;; esac
    else level=20
    fi
    ((level>rc)) && rc=$level
    [[ $state == BLOCK ]] && blocked=1
    if ((json)); then
        printf '{"mount":'; quote "$mount"
        printf ',"size_kb":%s,"used_kb":%s,"free_kb":%s,"used_pct":%s,"inode_pct":%s,"state":"%s"}\n' "$size" "$used" "$free" "$pct" "$inode" "$state"
    else
        gb=$(awk -v f="$free" 'BEGIN {if(f=="null") print "unknown"; else printf "%.1f",f/1048576}')
        printf '%s used=%s%% free=%s GiB inodes=%s%% %s\n' "$mount" "$pct" "$gb" "$inode" "$state"
    fi
done
# Explicit inspection refreshes; ordinary starts only read this six-hour snapshot.
state_file=$conf.consumers.tsv
signature=$(cksum < "$conf")
now=$(date +%s)
fresh=0
if [[ -f $state_file && ! -L $state_file ]]; then
    IFS=$'\t' read -r stamp saved_signature < "$state_file" || true
    if [[ ${stamp:-} =~ ^[0-9]+$ && ${saved_signature:-} == "$signature" ]] && ((now>=stamp && now-stamp<21600)); then fresh=1; fi
fi
measure() {
    local path=$1 result
    [[ -e $path ]] || { printf 'unknown'; return; }
    if command -v ionice >/dev/null && command -v timeout >/dev/null; then
        result=$(timeout 15 ionice -c 3 du -sk -- "$path" 2>/dev/null) || { printf 'unknown'; return; }
    else
        # No unbounded or normal-priority fallback during inspection.
        printf 'unknown'; return
    fi
    awk 'NR==1 && $1~/^[0-9]+$/ {printf "%.0f", $1*1024; ok=1} END {if(!ok) printf "unknown"}' <<< "$result"
}
if ((consumers && !fresh)); then
    old_minutes=$(awk -v days="$old_days" 'BEGIN {printf "%.0f",days*1440}')
    snapshot=$(printf '%s\t%s\n' "$now" "$signature"
        for index in "${!paths[@]}"; do
            path=${paths[index]}; name=${names[index]}
            cap_bytes=$(awk -v c="${caps[index]}" 'BEGIN {printf "%.0f",c*1073741824}')
            if [[ $name == tmp-old ]]; then
                # Limit traversal as well as each individual du; partial scans are unknown.
                if listing=$(timeout 15 find "$path" -mindepth 1 -maxdepth 1 -type d -mmin "+$old_minutes" -print 2>/dev/null); then
                    total=0; count=0; details=()
                    while IFS= read -r folder; do
                        [[ -n $folder ]] || continue
                        bytes=$(measure "$folder")
                        [[ $bytes == unknown ]] && { total=unknown; break; }
                        total=$((total+bytes)); count=$((count+1)); details+=("$bytes"$'\t'"$folder")
                    done <<< "$listing"
                    printf '%s\t%s\t%s\t%s\n' "$path (older than $old_days days; count=$count)" "$total" "$cap_bytes" "$name"
                    if ((${#details[@]})); then
                        printf '%s\n' "${details[@]}" | sort -nr | head -5 | while IFS=$'\t' read -r bytes folder; do
                            printf '%s\t%s\t0\ttmp-largest\n' "$folder" "$bytes"
                        done
                    fi
                else printf '%s\tunknown\t%s\t%s\n' "$path (old folders)" "$cap_bytes" "$name"
                fi
            else
                printf '%s\t%s\t%s\t%s\n' "$path" "$(measure "$path")" "$cap_bytes" "$name"
            fi
        done)
    # Never execute cached text; update only a regular, private state file.
    if [[ ! -L $state_file ]]; then
        (umask 077; set -o noclobber; printf '%s\n' "$snapshot" > "$state_file.new.$$") 2>/dev/null && mv -- "$state_file.new.$$" "$state_file"
    fi
    fresh=1
elif ((fresh)); then snapshot=$(cat -- "$state_file")
else
    snapshot=$(printf '%s\t%s\n' "$now" "$signature"
        for index in "${!paths[@]}"; do
            cap_bytes=$(awk -v c="${caps[index]}" 'BEGIN {printf "%.0f",c*1073741824}')
            printf '%s\tunknown\t%s\t%s\n' "${paths[index]}" "$cap_bytes" "${names[index]}"
        done)
fi
while IFS=$'\t' read -r path bytes cap_bytes name; do
        [[ $cap_bytes =~ ^[0-9]+$ && ( $bytes == unknown || $bytes =~ ^[0-9]+$ ) ]] || continue
        state=OK
        if [[ $bytes == unknown ]]; then state=UNKNOWN
        elif [[ $name != tmp-largest ]] && ((bytes>cap_bytes)); then state=WARN
        fi
        if [[ $state == WARN || ( $consumers == 1 && $state == UNKNOWN ) ]] && ((rc<10)); then rc=10; fi
        ((consumers || blocked)) || [[ $state == WARN ]] || continue
        if ((json)); then
            printf '{"path":'; quote "$path"
            [[ $bytes == unknown ]] && bytes=null
            printf ',"bytes":%s,"cap_bytes":%s,"state":"%s"}\n' "$bytes" "$cap_bytes" "$state"
        else
            printf '%s bytes=%s cap_bytes=%s %s\n' "$path" "$bytes" "$cap_bytes" "$state"
        fi
done < <(printf '%s\n' "$snapshot" | tail -n +2 | sort -t $'\t' -k2,2nr)
exit "$rc"
