#!/usr/bin/env bash
# Report old, idle temporary folders; copy and verify before optional removal.
set -uo pipefail

root=/tmp
archive=
old_days=3
while (($#)); do
    case $1 in
        --root|--move|--old-days)
            (($# >= 2)) || { echo 'missing option value' >&2; exit 2; }
            case $1 in
                --root) root=$2 ;;
                --move) archive=$2 ;;
                --old-days) old_days=$2 ;;
            esac
            shift 2 ;;
        --help)
            echo 'Usage: tmp_sweep.sh [--root directory] [--old-days days] [--move archive-directory|host:directory]'
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
process_clear() {
    local proc link target maps
    [[ -d /proc/self/fd && -r /proc/self/maps ]] || return 2
    for proc in /proc/[0-9]*; do
        [[ -d $proc ]] || continue
        [[ -r $proc/maps && -r $proc/fd && -x $proc/fd ]] || {
            [[ ! -d $proc ]] && continue
            return 2
        }
        for link in "$proc/cwd" "$proc/root" "$proc"/fd/*; do
            [[ -L $link ]] || continue
            if ! target=$(readlink -- "$link" 2>/dev/null); then
                [[ ! -d $proc || ! -L $link ]] && continue
                return 2
            fi
            case $target in "$folder"|"$folder/"*|"$folder (deleted)") return 1 ;; esac
        done
        if ! maps=$(cat -- "$proc/maps" 2>/dev/null); then
            [[ ! -d $proc ]] && continue
            return 2
        fi
        if awk -v p="$folder" 'index($0,p "/") || substr($0,length($0)-length(p)+1)==p {found=1} END {exit !found}' <<< "$maps"; then
            return 1
        fi
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
    local scan entry repo proc_rc
    reason=
    [[ -d $folder && ! -L $folder ]] || { reason=symlink-or-missing; return 1; }
    [[ ${folder##*/} != .* ]] || { reason=hidden; return 1; }
    if ! scan=$(find "$folder" -printf '%U\t%y\t%T@\t%m\n' 2>/dev/null); then
        reason=unreadable-tree; return 1
    fi
    if ! awk -F '\t' -v u="$uid" 'BEGIN {ok=1} $1 != u {ok=0} END {exit !ok}' <<< "$scan"; then
        reason=ownership; return 1
    fi
    if awk -F '\t' '$2=="s" {found=1} END {exit !found}' <<< "$scan"; then reason=socket; return 1; fi
    if awk -F '\t' '$2=="l" {found=1} END {exit !found}' <<< "$scan"; then reason=symlink; return 1; fi
    if ! awk -F '\t' -v c="$cutoff" 'BEGIN {ok=1} $3>=c {ok=0} END {exit !ok}' <<< "$scan"; then
        reason=recent; return 1
    fi
    if ! entry=$(find "$folder" ! -perm -u=w -print -quit 2>/dev/null); then reason=unreadable-tree; return 1; fi
    [[ -z $entry ]] || { reason='readonly'; return 1; }
    if ! entry=$(find "$folder" \( -name $'*\n*' -o -name $'*\t*' \) -print -quit 2>/dev/null); then reason=unreadable-tree; return 1; fi
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
    done < <(find "$folder" -name .git -print0 -prune)
    # Bare repositories have no .git child; retain them conservatively.
    while IFS= read -r -d '' entry; do
        repo=${entry%/HEAD}
        if [[ ${repo##*/} != .git && -d $repo/objects && -f $repo/config ]]; then
            reason=bare-git; return 1
        fi
    done < <(find "$folder" -type f -name HEAD -print0)
    process_clear
    proc_rc=$?
    case $proc_rc in
        1) reason=in-use; return 1 ;;
        2) reason=process-view-unreadable; return 1 ;;
    esac
    return 0
}

metrics() {
    find "$1" -printf '%y %s\n' | awk '{entries++; if($1=="f") {n++; b+=$2}} END {printf "%d %.0f %d",n,b,entries}'
}
fingerprint() {
    find "$1" -printf '%P\t%y\t%s\t%T@\t%m\t%U\t%G\n' | LC_ALL=C sort | cksum
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
        if ssh -n -- "$remote" "test ! -L $(quote_remote "$archive/MANIFEST.tsv") && test ! -L $(quote_remote "$destination") && test ! -e $(quote_remote "$destination") && mkdir -p -- $(quote_remote "$destination")" &&
            rsync -a --protect-args -e 'ssh -n' -- "$folder/" "$remote:$destination/"; then copied=true; fi
        remote_command="find $(quote_remote "$destination") -printf '%y %s\\n' | awk '{entries++; if(\$1==\"f\") {n++; b+=\$2}} END {printf \"%d %.0f %d\",n,b,entries}'"
        after_metrics=$(ssh -n -- "$remote" "bash -o pipefail -c $(quote_remote "$remote_command")") || copied=false
    else
        if [[ ! -e $destination && ! -L $destination ]] && cp -a -- "$folder" "$destination"; then copied=true; fi
        after_metrics=$(metrics "$destination" 2>/dev/null) || copied=false
    fi
    if [[ $copied != true || $before_metrics != "$after_metrics" ]] ||
        [[ $before_fingerprint != "$(fingerprint "$folder")" ]] || ! eligible; then
        printf 'KEPT\t%s\tverification-failed\n' "$folder"
        manifest verification-failed || true
        ((failed+=1)); continue
    fi
    # BEGIN VERIFIED MOVE: this is the only branch permitted to remove data.
    if ! manifest verified; then
        printf 'KEPT\t%s\tmanifest-failed\n' "$folder"; ((failed+=1)); continue
    fi
    if (
        rm -r -- "$folder"
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
printf 'SUMMARY\tsweepable=%d\tmoved=%d\tfailed=%d\n' "$sweepable" "$moved" "$failed"
((failed == 0))
