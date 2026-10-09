#!/usr/bin/env bash
# bridge-commit.sh — private commit path for bridge-hermes-claude.sh.
#
# Function: bridge_private_commit_and_push <private_repo> <host_slug> <timestamp>

bridge_private_commit_and_push() {
    local private_repo="$1" host_slug="$2" timestamp="$3"
    cd "$private_repo" || return 1

    local host_dir="hosts/${host_slug}"
    if [[ ! -d "$host_dir" ]]; then
        echo "[bridge] private host directory missing: ${host_dir}" >&2
        return 1
    fi

    git add "$host_dir" || return 1

    if git diff --cached --quiet -- "$host_dir"; then
        echo "[bridge] nothing to commit in private memory snapshot for ${host_slug}"
        return 0
    fi

    git commit -q -m "chore(memory): bridge refresh ${host_slug} (${timestamp})" -- "$host_dir" || return 1

    local attempt
    for attempt in 1 2 3; do
        if ! git pull --rebase --autostash --quiet; then
            echo "[bridge] private repo rebase conflict during pull — resolve manually, then git push" >&2
            return 1
        fi
        if git push --quiet; then
            return 0
        fi
        echo "[bridge] private repo push rejected (non-FF); retry ${attempt}/3" >&2
    done
    echo "[bridge] private repo push still failing after 3 attempts — commit is local" >&2
    return 1
}
