#!/usr/bin/env bash
# Create a worktree or blob-filtered clone only after the destination passes.
set -euo pipefail
export GIT_LFS_SKIP_SMUDGE=1

usage() {
    printf 'Usage: %s --repo <checkout-or-URL> --branch <new> --base <ref> --dest <dir> [--profile <name>] [--min-free-gb <n>] [--dry-run]\n' "${0##*/}" >&2
    exit 2
}
repo='' branch='' base='' dest='' profile='' dry_run=false
floor_args=()
while (($#)); do
    case $1 in
        --repo|--branch|--base|--dest|--profile|--min-free-gb)
            (($# >= 2)) || usage
            [[ -n $2 ]] || usage
            case $1 in
                --repo) repo=$2 ;;
                --branch) branch=$2 ;;
                --base) base=$2 ;;
                --dest) dest=$2 ;;
                --profile) profile=$2 ;;
                --min-free-gb) floor_args=(--min-free-gb "$2") ;;
            esac
            shift 2 ;;
        --dry-run) dry_run=true; shift ;;
        *) usage ;;
    esac
done
[[ -n $repo && -n $branch && -n $base && -n $dest ]] || usage
# Git -C changes the base for relative worktree paths; pin it to the caller.
if [[ $dest != /* ]]; then
    dest="$(pwd -P)/$dest"
fi
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
# This must precede every Git operation, including the dry-run plan.
bash "$script_dir/worktree_location_guard.sh" --dest "$dest" "${floor_args[@]}" || exit $?

# Do not let an inherited repository binding redirect explicit -C operations.
unset GIT_DIR GIT_WORK_TREE GIT_COMMON_DIR GIT_INDEX_FILE
unset GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES
[[ $base != -* && $branch != -* ]] || usage
git check-ref-format --branch "$branch" >/dev/null 2>&1 || usage
profile_paths=()
if [[ -n $profile ]]; then
    [[ $profile =~ ^[a-zA-Z0-9_-]+$ ]] || usage
    repo_name=${repo%/}
    repo_name=${repo_name##*/}
    repo_name=${repo_name%.git}
    [[ $repo_name =~ ^[a-zA-Z0-9_.-]+$ ]] || usage
    profile_file="$script_dir/../../../config/storage/sparse-profiles/$repo_name-$profile.txt"
    if [[ ! -f $profile_file ]]; then
        printf 'Unknown sparse profile: %s-%s\n' "$repo_name" "$profile" >&2
        exit 2
    fi
    while IFS= read -r path || [[ -n $path ]]; do
        [[ -z $path || $path == \#* ]] && continue
        [[ $path != /* && $path != -* && $path != *'..'* && $path != *\\* ]] || usage
        profile_paths+=("$path")
    done < "$profile_file"
    ((${#profile_paths[@]})) || usage
fi
mode=partial-clone
if [[ -d $repo ]] && git -C "$repo" rev-parse --git-dir >/dev/null 2>&1; then
    mode=worktree
    git -C "$repo" rev-parse --verify --end-of-options "$base^{commit}" >/dev/null 2>&1 || usage
fi
base_branch=${base#refs/heads/}
base_branch=${base_branch#refs/remotes/origin/}
base_branch=${base_branch#origin/}
if [[ $mode == partial-clone ]]; then
    git check-ref-format "refs/heads/$base_branch" >/dev/null 2>&1 || usage
fi
if $dry_run; then
    printf 'plan mode=%s branch=%s base=%s profile=%s location=ok dest=%s\n' "$mode" "$branch" "$base" "${profile:-none}" "$dest"
    exit 0
fi

if [[ $mode == worktree ]]; then
    git -C "$repo" worktree add --no-checkout "$dest" -b "$branch" "$base"
else
    git clone --filter=blob:none --single-branch --branch "$base_branch" --no-checkout -- "$repo" "$dest"
    git -C "$dest" branch "$branch"
    git -C "$dest" symbolic-ref HEAD "refs/heads/$branch"
fi
# Git's worktree-config extension is shared; the actual checkout settings are not.
# Its initial enablement is documented, including core.bare/core.worktree migration.
if [[ $(git -C "$dest" config --bool extensions.worktreeConfig || true) != true ]]; then
    common_dir=$(git -C "$dest" rev-parse --path-format=absolute --git-common-dir)
    common_config="$common_dir/config"
    main_config="$common_dir/config.worktree"
    for setting in core.bare core.worktree; do
        if value=$(git config --file "$common_config" --get "$setting"); then
            git config --file "$main_config" "$setting" "$value"
            git config --file "$common_config" --unset-all "$setting"
        fi
    done
    git -C "$dest" config extensions.worktreeConfig true
fi
git -C "$dest" config --worktree core.bare false
git -C "$dest" config --worktree core.untrackedCache true
git -C "$dest" config --worktree lfs.fetchexclude '*'
if [[ -n $profile ]]; then
    git -C "$dest" sparse-checkout set --cone -- "${profile_paths[@]}"
else
    # A linked worktree can inherit an existing sparse setting; opt out explicitly.
    git -C "$dest" sparse-checkout disable
fi
git -C "$dest" checkout
# shellcheck source=scripts/lib/worktree-index.sh
source "$script_dir/../../lib/worktree-index.sh"
worktree_index_preflight "$dest" --fresh
checkout_kb=$(du -sk -- "$dest" | awk '{print $1}')
printf 'checkout_kb=%s mode=%s profile=%s location=ok\n' "$checkout_kb" "$mode" "${profile:-none}"
