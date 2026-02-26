#!/usr/bin/env bash
# Multi-machine SSH helpers — source in ~/.bashrc
# source /mnt/local-analysis/workspace-hub/scripts/operations/system/ssh-helpers.sh
#
# Provides: ace1, ace2, ace1-tmux, ace2-tmux, whoami-machine
# Coloured PS1 prompt with hostname included

MACHINE_1="ace-linux-1"
MACHINE_2="ace-linux-2"
MACHINE_1_USER="${ACE_SSH_USER:-vamsee}"

alias ace1="ssh ${MACHINE_1_USER}@${MACHINE_1}"
alias ace2="ssh ${MACHINE_1_USER}@${MACHINE_2}"
alias ace1-tmux="ssh -t ${MACHINE_1_USER}@${MACHINE_1} 'tmux new-session -A -s main'"
alias ace2-tmux="ssh -t ${MACHINE_1_USER}@${MACHINE_2} 'tmux new-session -A -s main'"

whoami-machine() {
    echo "Hostname:  $(hostname)"
    echo "LAN IP:    $(hostname -I | awk '{print $1}')"
    local ts_ip
    ts_ip=$(tailscale ip 2>/dev/null | head -1 || echo "not installed")
    echo "Tailscale: ${ts_ip}"
}
export -f whoami-machine 2>/dev/null || true

# Coloured PS1 prompt with hostname — only set once per shell
if [[ -z "${PS1_MACHINE_SET:-}" ]]; then
    PS1_MACHINE_SET=1
    export PS1='\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
fi
