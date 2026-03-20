#!/usr/bin/env bash
# ABOUTME: Open an SSH terminal session to dev-secondary
# ABOUTME: Uses hostname alias; falls back to Tailscale IP if alias unresolved

ACE2_ALIAS="dev-secondary"
ACE2_TAILSCALE="10.1.0.2"
ACE2_USER="vamsee"

echo "=== SSH → dev-secondary ==="

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
#   ./ssh-dev-secondary.sh           # interactive shell
#   ./ssh-dev-secondary.sh -- <cmd>  # not supported; use: ssh dev-secondary <cmd>
#
# Quick one-liners (no script needed):
#   ssh dev-secondary                          # terminal
#   ssh dev-secondary 'ls ~/workspace-hub'     # run remote command
#   ssh vamsee@10.1.0.2                 # via Tailscale IP directly
