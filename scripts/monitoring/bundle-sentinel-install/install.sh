#!/usr/bin/env bash
# One-shot installer for the bundle-integrity sentinel (ace-linux-1).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
install -d "$HOME/.local/bin" "$HOME/.config/systemd/user"
install -m 0755 "$HERE/../bundle-verify-sentinel.sh" "$HOME/.local/bin/bundle-verify-sentinel.sh"
install -m 0644 "$HERE"/bundle-verify-sentinel@.service "$HOME/.config/systemd/user/"
install -m 0644 "$HERE"/bundle-verify-sentinel@fast.timer "$HOME/.config/systemd/user/"
install -m 0644 "$HERE"/bundle-verify-sentinel@full.timer "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
systemctl --user enable --now bundle-verify-sentinel@fast.timer bundle-verify-sentinel@full.timer
# Timers must survive logout, or they only run while a session exists.
loginctl enable-linger "$USER" 2>/dev/null || echo "NOTE: enable-linger needs sudo; run: sudo loginctl enable-linger $USER"
echo "--- installed timers ---"
systemctl --user list-timers 'bundle-verify*' --no-pager
echo "--- immediate smoke run ---"
systemctl --user start bundle-verify-sentinel@fast.service
journalctl --user -u bundle-verify-sentinel@fast.service -n 12 --no-pager
