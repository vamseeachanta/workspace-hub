#!/usr/bin/env bash
# ABOUTME: Open an SSH terminal session to ace-linux-2
# ABOUTME: Uses hostname alias; falls back to Tailscale IP if alias unresolved

ACE2_ALIAS="ace-linux-2"
ACE2_TAILSCALE="100.93.161.27"
ACE2_USER="vamsee"

echo "=== SSH → ace-linux-2 ==="

# Resolve host: prefer alias, fall back to Tailscale IP
if ssh -o ConnectTimeout=3 -o BatchMode=yes "${ACE2_USER}@${ACE2_ALIAS}" exit 2>/dev/null; then
    TARGET="${ACE2_USER}@${ACE2_ALIAS}"
else
    echo "Alias unreachable, trying Tailscale (${ACE2_TAILSCALE})..."
    TARGET="${ACE2_USER}@${ACE2_TAILSCALE}"
fi

echo "Connecting to ${TARGET}..."
ssh "${TARGET}"

# Usage:
#   ./ssh-ace-linux-2.sh           # interactive shell
#   ./ssh-ace-linux-2.sh -- <cmd>  # not supported; use: ssh ace-linux-2 <cmd>
#
# Quick one-liners (no script needed):
#   ssh ace-linux-2                          # terminal
#   ssh ace-linux-2 'ls ~/workspace-hub'     # run remote command
#   ssh vamsee@100.93.161.27                 # via Tailscale IP directly
