#!/usr/bin/env bash
# ABOUTME: Upgrade gh CLI to latest via official GitHub apt repo
# Usage: sudo bash scripts/maintenance/upgrade-gh.sh

set -euo pipefail

curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
    | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] \
https://cli.github.com/packages stable main" \
    | sudo tee /etc/apt/sources.list.d/github-cli.list

sudo apt update && sudo apt install -y gh

echo "Done: $(gh --version | head -1)"
