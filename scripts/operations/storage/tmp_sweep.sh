#!/usr/bin/env bash
# Report old, idle temporary folders; copy and verify before optional removal.
set -uo pipefail

root=/tmp
archive=
old_days=3
proc_root=${TMP_SWEEP_PROC_ROOT:-/proc}
target_uid=
while (($#)); do
    case $1 in
        --root|--move|--old-days|--uid)
            (($# >= 2)) || { echo 'missing option value' >&2; exit 2; }
            case $1 in
                --root) root=$2 ;;
                --move) archive=$2 ;;
                --old-days) old_days=$2 ;;
                --uid) target_uid=$2 ;;
            esac
            shift 2 ;;
        --help)
            echo 'Usage: tmp_sweep.sh [--root directory] [--old-days days] [--uid uid] [--move archive-directory|host:directory]'
            exit 0 ;;
        *) echo 'unknown option' >&2; exit 2 ;;
    esac
done
[[ $old_days =~ ^[0-9]+$ && -d $root && ! -L $root ]] || exit 2
for tool in find awk stat readlink sort cksum git date; do
    command -v "$tool" >/dev/null || { echo "required tool unavailable: $tool" >&2; exit 2; }
done
root=$(cd -- "$root" && pwd -P) || exit 2
[[ $root != *$'\n'* && $root != *$'\t'* ]] || exit 2
uid=$(id -u)
if [[ -n $target_uid ]]; then
    [[ $uid == 0 && $target_uid =~ ^[0-9]+$ ]] || exit 2
    uid=$target_uid
fi
declare -A skipped_foreign=()
cutoff=$(( $(date +%s) - old_days * 86400 ))
remote=
if [[ -n $archive ]]; then
    if [[ $archive == *:* ]]; then
        remote=${archive%%:*}
        archive=${archive#*:}
        [[ $remote =~ ^[a-zA-Z0-9][a-zA-Z0-9._@-]*$ && -n $archive && $archive != -* ]] || exit 2
        command -v ssh >/dev/null && command -v rsync >/dev/null || exit 2
    else
        command -v realpath >/dev/null && command -v cp >/dev/null || exit 2
        archive=$(realpath -m -- "$archive") || exit 2
        case $archive/ in "$root/"*) echo 'archive must be outside the sweep root' >&2; exit 2 ;; esac
        case $root/ in "$archive/"*) echo 'archive must not contain the sweep root' >&2; exit 2 ;; esac
        mkdir -p -- "$archive" || exit 2
        [[ ! -L $archive/MANIFEST.tsv ]] || exit 2
    fi
    [[ $archive != *$'\n'* && $archive != *$'\t'* ]] || exit 2
fi

# Shell-quote data for the remote command without evaluating its contents.
quote_remote() {
    printf "'%s'" "${1//\'/\'\\\'\'}"
}

# An unreadable process view is uncertainty, so the folder remains in place.
inspect_process() {
    local link target maps
    [[ -r $1/maps && -r $1/fd && -x $1/fd ]] || return 2
    local proc=$1
    for link in "$proc/cwd" "$proc/root" "$proc"/fd/*; do
        [[ -L $link ]] || continue
        if ! target=$(readlink -- "$link" 2>/dev/null); then
            [[ ! -d $proc || ! -L $link ]] && continue
            return 2
        fi
        case $target in "$folder"|"$folder/"*|"$folder (deleted)") return 1 ;; esac
    done
    if ! maps=$(cat -- "$proc/maps" 2>/dev/null); then
        [[ ! -d $proc ]] && return 0
        return 2
    fi
    if awk -v p="$folder" 'index($0,p "/") || substr($0,length($0)-length(p)+1)==p {found=1} END {exit !found}' <<< "$maps"; then
        return 1
    fi
    return 0
}

# A foreign process can be skipped only for a tree denying all group/other access.
process_clear() {
    local proc owners owner foreign proc_rc
    [[ -d $proc_root/self/fd && -r $proc_root/self/maps ]] || return 2
    for proc in "$proc_root"/[0-9]*; do
        [[ -d $proc ]] || continue
        inspect_process "$proc"
        proc_rc=$?
        ((proc_rc == 0)) && continue
        ((proc_rc == 1)) && return 1
        [[ ! -d $proc ]] && continue
        # Proc-directory ownership changes for non-dumpable same-user processes.
        # All real/effective/saved/filesystem UIDs must establish a foreign identity.
        owners=$(awk '
            /^Uid:/ {
                n++
                if(NF==5 && $2~/^[0-9]+$/ && $3~/^[0-9]+$/ &&
                   $4~/^[0-9]+$/ && $5~/^[0-9]+$/) {print $2,$3,$4,$5; valid++}
            }
            END {if(n!=1 || valid!=1) exit 1}
        ' "$proc/status" 2>/dev/null) || return 2
        foreign=1
        for owner in $owners; do [[ $owner == "$uid" ]] && foreign=0; done
        if [[ $private_tree == 1 && $foreign == 1 ]]; then
            skipped_foreign["$proc"]=1
            continue
        fi
        return 2
    done
    return 0
}

# Caller environment must not redirect repository checks to unrelated work.
run_git() {
    env -u GIT_DIR -u GIT_WORK_TREE -u GIT_COMMON_DIR -u GIT_INDEX_FILE \
        -u GIT_OBJECT_DIRECTORY -u GIT_ALTERNATE_OBJECT_DIRECTORIES \
        -u GIT_CONFIG_COUNT -u GIT_CONFIG_PARAMETERS git --no-optional-locks "$@"
}

eligible() {
    local scan entry repo proc_rc scan_permissions private_tree
    reason=
    [[ -d $folder && ! -L $folder ]] || { reason=symlink-or-missing; return 1; }
    [[ ${folder##*/} != .* ]] || { reason=hidden; return 1; }
    if ! scan=$(find "$folder" -xdev -printf '%U\t%y\t%T@\t%m\t%D\n' 2>/dev/null); then
        reason=unreadable-tree; return 1
    fi
    local device
    device=$(stat -c %d -- "$folder") || { reason=unreadable-tree; return 1; }
    if ! awk -F '\t' -v d="$device" 'BEGIN {ok=1} $5 != d {ok=0} END {exit !ok}' <<< "$scan"; then
        reason=mount-point; return 1
    fi
    # Bind mounts may share the device number, so inspect the mount table too.
    [[ -r $proc_root/self/mountinfo ]] || { reason=mount-view-unreadable; return 1; }
    local mount_rc
    SWEEP_FOLDER=$folder awk '
        function decode(s, out, i, code) {
            out=""
            for(i=1;i<=length(s);i++) {
                code=substr(s,i,4)
                if(code=="\\040") {out=out " "; i+=3}
                else if(code=="\\011") {out=out sprintf("%c",9); i+=3}
                else if(code=="\\012") {out=out sprintf("%c",10); i+=3}
                else if(code=="\\134") {out=out sprintf("%c",92); i+=3}
                else out=out substr(s,i,1)
            }
            return out
        }
        {m=decode($5); p=ENVIRON["SWEEP_FOLDER"]; if(m==p || index(m,p "/")==1) found=1}
        END {exit !found}
    ' "$proc_root/self/mountinfo"
    mount_rc=$?
    if ((mount_rc == 0)); then reason=mount-point; return 1; fi
    if ((mount_rc != 1)); then reason=mount-view-unreadable; return 1; fi
    scan_permissions=$scan
    if ! awk -F '\t' -v u="$uid" 'BEGIN {ok=1} $1 != u {ok=0} END {exit !ok}' <<< "$scan"; then
        reason=ownership; return 1
    fi
    if awk -F '\t' '$2=="s" {found=1} END {exit !found}' <<< "$scan"; then reason=socket; return 1; fi
    if awk -F '\t' '$2=="l" {found=1} END {exit !found}' <<< "$scan"; then reason=symlink; return 1; fi
    if ! awk -F '\t' -v c="$cutoff" 'BEGIN {ok=1} $3>=c {ok=0} END {exit !ok}' <<< "$scan"; then
        reason=recent; return 1
    fi
    if ! entry=$(find "$folder" -xdev ! -perm -u=w -print -quit 2>/dev/null); then reason=unreadable-tree; return 1; fi
    [[ -z $entry ]] || { reason='readonly'; return 1; }
    if ! entry=$(find "$folder" -xdev \( -name $'*\n*' -o -name $'*\t*' \) -print -quit 2>/dev/null); then reason=unreadable-tree; return 1; fi
    [[ -z $entry ]] || { reason=unsupported-name; return 1; }
    # Both .git directories and .git files (linked worktrees) are inspected.
    while IFS= read -r -d '' entry; do
        repo=${entry%/.git}
        if ! run_git -C "$repo" rev-parse --is-inside-work-tree >/dev/null 2>&1; then reason=unknown-git; return 1; fi
        if ! scan=$(run_git -C "$repo" status --porcelain --untracked-files=all 2>/dev/null); then reason=unknown-git; return 1; fi
        [[ -z $scan ]] || { reason=uncommitted-git; return 1; }
        if ! scan=$(run_git -C "$repo" remote 2>/dev/null); then reason=unknown-git; return 1; fi
        [[ -n $scan ]] || { reason=git-without-remote; return 1; }
        if ! scan=$(run_git -C "$repo" rev-list --all --not --remotes 2>/dev/null); then reason=unknown-git; return 1; fi
        [[ -z $scan ]] || { reason=unshared-git; return 1; }
    done < <(find "$folder" -xdev -name .git -print0 -prune)
    # Bare repositories have no .git child; retain them conservatively.
    while IFS= read -r -d '' entry; do
        repo=${entry%/HEAD}
        if [[ ${repo##*/} != .git && -d $repo/objects && -f $repo/config ]]; then
            reason=bare-git; return 1
        fi
    done < <(find "$folder" -xdev -type f -name HEAD -print0)
    private_tree=0
    if awk -F '\t' 'BEGIN {ok=1} $4 !~ /^[0-7]*00$/ {ok=0} END {exit !ok}' <<< "$scan_permissions"; then
        private_tree=1
    fi
    process_clear
    proc_rc=$?
    case $proc_rc in
        1) reason=in-use; return 1 ;;
        2) reason=process-view-unreadable; return 1 ;;
    esac
    return 0
}

metrics() {
    find "$1" -xdev -printf '%y %s\n' | awk '{entries++; if($1=="f") {n++; b+=$2}} END {printf "%d %.0f %d",n,b,entries}'
}
fingerprint() {
    find "$1" -xdev -printf '%P\t%y\t%s\t%T@\t%m\t%U\t%G\n' | LC_ALL=C sort | cksum
}
manifest() {
    local row
    printf -v row '%s\t%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "${folder##*/}" "$1" "$before_metrics"
    if [[ -n $remote ]]; then
        ssh -n -- "$remote" "test ! -L $(quote_remote "$archive/MANIFEST.tsv") && printf '%s' $(quote_remote "$row") >> $(quote_remote "$archive/MANIFEST.tsv")"
    else
        printf '%s' "$row" >> "$archive/MANIFEST.tsv"
    fi
}

sweepable=0
moved=0
failed=0
shopt -s nullglob dotglob
for folder in "$root"/*; do
    [[ -d $folder || -L $folder ]] || continue
    if ! eligible; then printf 'KEPT\t%s\t%s\n' "$folder" "$reason"; continue; fi
    ((sweepable+=1))
    printf 'SWEEPABLE\t%s\n' "$folder"
    [[ -n $archive ]] || continue
    if ! before_metrics=$(metrics "$folder") || ! before_fingerprint=$(fingerprint "$folder"); then
        printf 'KEPT\t%s\tunreadable-tree\n' "$folder"; ((failed+=1)); continue
    fi
    destination=$archive/${folder##*/}
    copied=false
    if [[ -n $remote ]]; then
        # Each attempt owns a fresh staging directory; failed copies remain for inspection.
        # A partial transfer never occupies the final name or blocks a later attempt.
        staging=
        if staging=$(ssh -n -- "$remote" "test ! -L $(quote_remote "$archive/MANIFEST.tsv") && test ! -L $(quote_remote "$destination") && test ! -e $(quote_remote "$destination") && mkdir -p -- $(quote_remote "$archive") && mktemp -d -- $(quote_remote "$archive/.tmp-sweep-XXXXXXXX")") &&
            [[ -n $staging && $staging != *$'\n'* ]] &&
            rsync -a -x --protect-args -e ssh -- "$folder/" "$remote:$staging/" </dev/null; then copied=true; fi
        remote_command="find $(quote_remote "$staging") -xdev -printf '%y %s\\n' | awk '{entries++; if(\$1==\"f\") {n++; b+=\$2}} END {printf \"%d %.0f %d\",n,b,entries}'"
        after_metrics=
        if [[ $copied == true ]]; then
            after_metrics=$(ssh -n -- "$remote" "bash -o pipefail -c $(quote_remote "$remote_command")") || copied=false
        fi
    else
        if [[ ! -e $destination && ! -L $destination ]] && cp -a --one-file-system -- "$folder" "$destination"; then copied=true; fi
        after_metrics=$(metrics "$destination" 2>/dev/null) || copied=false
    fi
    if [[ $copied != true || $before_metrics != "$after_metrics" ]] ||
        [[ $before_fingerprint != "$(fingerprint "$folder")" ]] || ! eligible; then
        printf 'KEPT\t%s\tverification-failed\n' "$folder"
        manifest verification-failed || true
        ((failed+=1)); continue
    fi
    if [[ -n $remote ]]; then
        if ! ssh -n -- "$remote" "test ! -e $(quote_remote "$destination") && test ! -L $(quote_remote "$destination") && mv -T -n -- $(quote_remote "$staging") $(quote_remote "$destination") && test ! -e $(quote_remote "$staging")"; then
            printf 'KEPT\t%s\tarchive-finalization-failed\n' "$folder"
            ((failed+=1)); continue
        fi
    fi
    # BEGIN VERIFIED MOVE: this is the only branch permitted to remove data.
    if ! manifest verified; then
        printf 'KEPT\t%s\tmanifest-failed\n' "$folder"; ((failed+=1)); continue
    fi
    if (
        rm -r --one-file-system -- "$folder"
    ); then
        printf 'MOVED\t%s\n' "$folder"
        manifest moved || { printf 'WARNING\tmanifest-update-failed\n'; ((failed+=1)); }
        ((moved+=1))
    else
        printf 'KEPT\t%s\tsource-removal-incomplete; copies-retained\n' "$folder"
        manifest source-removal-incomplete || true
        ((failed+=1))
    fi
    # END VERIFIED MOVE
 done
printf 'SUMMARY\tsweepable=%d\tmoved=%d\tfailed=%d\tforeign-processes-skipped=%d\n' "$sweepable" "$moved" "$failed" "${#skipped_foreign[@]}"
((failed == 0))
