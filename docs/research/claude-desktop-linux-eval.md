# Claude Desktop Linux Evaluation — aaddrick/claude-desktop-debian

**Date:** 2026-03-31
**Issue:** vamseeachanta/workspace-hub#1506
**Parent:** vamseeachanta/workspace-hub#1504
**Target machine:** ace-linux-2 (dev-secondary, Debian/Ubuntu)

---

## Summary

`aaddrick/claude-desktop-debian` is a community-maintained repackaging of Anthropic's Claude Desktop for Debian-based Linux distributions. It provides `.deb`, `.rpm`, and `.AppImage` artifacts plus an APT repository for automatic updates. The project supports amd64 and arm64 architectures.

**Recommendation:** Install via APT repository (not standalone `.deb`) for automatic updates. Run `--doctor` post-install to validate.

---

## Latest Release

| Field | Value |
|-------|-------|
| Tag | `v1.3.25+claude1.1.8629` |
| Published | 2026-03-25 |
| .deb (amd64) | `claude-desktop_1.1.8629-1.3.25_amd64.deb` (94 MB) |
| .deb (arm64) | `claude-desktop_1.1.8629-1.3.25_arm64.deb` (93 MB) |
| Downloads (amd64 .deb) | 463 |
| Release note | Wrapper/packaging update only; fixes self-referential `.mcpb-cache` symlinks before bwrap mount |

---

## Installation (APT — Recommended)

```bash
# 1. Add GPG key
curl -fsSL https://aaddrick.github.io/claude-desktop-debian/KEY.gpg | \
  sudo gpg --dearmor -o /usr/share/keyrings/claude-desktop.gpg

# 2. Add repository
echo "deb [signed-by=/usr/share/keyrings/claude-desktop.gpg arch=amd64,arm64] \
  https://aaddrick.github.io/claude-desktop-debian stable main" | \
  sudo tee /etc/apt/sources.list.d/claude-desktop.list

# 3. Install
sudo apt update && sudo apt install claude-desktop
```

### Alternative: Direct .deb Install

```bash
# Download from https://github.com/aaddrick/claude-desktop-debian/releases
sudo dpkg -i claude-desktop_1.1.8629-1.3.25_amd64.deb && sudo apt-get install -f
```

---

## Prerequisites

- Debian/Ubuntu system (amd64 or arm64)
- `curl` and `gpg` for APT repository setup
- Display server: X11 or Wayland (XWayland recommended for full feature support)
- Optional: `bwrap` (bubblewrap) for Cowork mode sandbox isolation
- Optional: KVM/QEMU, socat, virtiofsd, vsock for advanced Cowork features

---

## Post-Install Verification

```bash
# 1. Run built-in diagnostics
claude-desktop --doctor
# Checks: display server, sandbox permissions, MCP config, stale locks, cowork readiness

# 2. Launch the app
claude-desktop

# 3. Verify MCP config exists (created on first launch)
cat ~/.config/Claude/claude_desktop_config.json
```

---

## MCP Server Configuration

Config path: `~/.config/Claude/claude_desktop_config.json`

Example structure:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"]
    }
  }
}
```

For ace-linux-2, configure MCP servers to access NFS-mounted workspace paths as needed. Node.js is required for npx-based MCP servers (v24.14.0 already installed on dev-secondary per status records).

---

## Known Issues (Upstream)

| Issue | Severity | Notes |
|-------|----------|-------|
| Wayland global hotkeys | Low | Native Wayland mode lacks global hotkeys; Electron/Chromium limitation |
| WebContentsView layout on resize | Medium | Layout can break on snap/tile operations (#239) |
| Cowork rootfs download loop | Medium | Download may loop at ~65-73% (#332) |
| OAuth token staleness | Low | 401 errors after inactivity; clear cached token to resolve |
| Loading screen stuck | Medium | Reported on older versions (#255); verify with latest |

Troubleshooting reference: https://github.com/aaddrick/claude-desktop-debian/blob/main/docs/TROUBLESHOOTING.md

---

## Status

- **Evaluation:** Complete (research only; no install performed)
- **Action:** Ready to install on ace-linux-2 when machine is reachable
- **Blocker:** ace-linux-2 currently unreachable per `ai-tools-status.yaml`
