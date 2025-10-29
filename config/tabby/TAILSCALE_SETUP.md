# Tailscale VPN Setup for Remote Access

Access your Linux workspace from anywhere on the internet using Tailscale VPN.

## What is Tailscale?

Tailscale creates a secure, encrypted peer-to-peer VPN network between your devices:
- ✓ **No port forwarding needed** - Works through any firewall
- ✓ **Zero configuration** - Automatic NAT traversal
- ✓ **Secure** - WireGuard-based encryption
- ✓ **Private** - No SSH exposed to internet
- ✓ **Free** - Up to 100 devices for personal use
- ✓ **Cross-platform** - Works on Windows, Mac, Linux, iOS, Android

## Linux Workspace Setup (Already Done ✓)

Your Linux machine is already configured:
- **Hostname:** vamsee-linux1
- **Tailscale IP:** 100.107.64.76
- **Local IP:** 192.168.1.100
- **Status:** Connected to Tailscale network

## Setup on Remote Machines

### Windows Setup

**1. Install Tailscale:**
```
Visit: https://tailscale.com/download/windows
Download and run the installer
```

**2. Authenticate:**
- Click Tailscale icon in system tray
- Click "Log in to Tailscale"
- Use the same account you used for Linux machine
- Authenticate with Google/Microsoft/GitHub

**3. Verify Connection:**
```powershell
# Open PowerShell
tailscale status

# You should see vamsee-linux1 in the list
# Ping your Linux machine
ping 100.107.64.76
```

**4. Connect via Tabby:**
```powershell
# Sync workspace-hub config
cd C:\workspace-hub
git pull
.\scripts\sync-tabby-windows.ps1

# Open Tabby → "Linux Workspace (Tailscale - Internet)"
```

### Mac Setup

**1. Install Tailscale:**
```bash
# Using Homebrew
brew install tailscale

# Or download from https://tailscale.com/download/mac
```

**2. Start Tailscale:**
```bash
sudo tailscaled install-system-daemon
tailscale up
```

**3. Authenticate:**
- Visit the URL shown in terminal
- Log in with same account
- Authorize the device

**4. Verify and Connect:**
```bash
tailscale status
ping 100.107.64.76

# Sync config and use Tabby
cd /path/to/workspace-hub
git pull
./scripts/sync-tabby-linux.sh
# Open Tabby → "Linux Workspace (Tailscale - Internet)"
```

### Linux Setup (Other Linux Machines)

**1. Install Tailscale:**
```bash
curl -fsSL https://tailscale.com/install.sh | sh
```

**2. Authenticate:**
```bash
sudo tailscale up
# Visit the URL shown
# Log in with same account
```

**3. Verify and Connect:**
```bash
tailscale status
ping 100.107.64.76
ssh vamsee@100.107.64.76
```

### Mobile Setup (iOS/Android)

**1. Install App:**
- iOS: App Store → Search "Tailscale"
- Android: Google Play → Search "Tailscale"

**2. Authenticate:**
- Open app
- Log in with same account
- Enable VPN

**3. Connect:**
- Install Termius or similar SSH app
- Add connection:
  - Host: 100.107.64.76
  - User: vamsee
  - Port: 22

## Connection Methods

### Method 1: Tabby (Recommended)

After syncing config, you'll see two profiles:

1. **"Linux Workspace (Local Network)"**
   - IP: 192.168.1.100
   - Use when on same WiFi network
   - Faster connection

2. **"Linux Workspace (Tailscale - Internet)"**
   - IP: 100.107.64.76
   - Use from anywhere on internet
   - Works through any firewall

### Method 2: Direct SSH

```bash
# From any device on Tailscale network
ssh vamsee@100.107.64.76

# Or use hostname (if enabled)
ssh vamsee@vamsee-linux1
```

### Method 3: Connection Scripts

```bash
# Linux/Mac
./scripts/connect-workspace-tailscale.sh

# Windows
.\scripts\connect-workspace-tailscale.ps1
```

## Advanced Features

### Enable Tailscale SSH (Optional)

Tailscale can manage SSH keys automatically:

**On Linux workspace:**
```bash
sudo tailscale up --ssh
```

**Benefits:**
- No SSH key management needed
- Automatic authentication via Tailscale
- Centralized access control
- Activity logging

**Connect without passwords:**
```bash
ssh vamsee@100.107.64.76
# No password needed if using Tailscale SSH
```

### MagicDNS (Use Hostnames)

Enable in Tailscale admin panel to use hostnames instead of IPs:

```bash
# Instead of: ssh vamsee@100.107.64.76
ssh vamsee@vamsee-linux1

# Or even: ssh vamsee-linux1 (if user matches)
```

**Enable:**
1. Visit: https://login.tailscale.com/admin/dns
2. Enable "MagicDNS"
3. Update Tabby config to use hostname instead of IP

### Subnet Routing (Access Local Network)

Access other devices on your home network (192.168.1.x) through Tailscale:

**On Linux workspace:**
```bash
echo 'net.ipv4.ip_forward = 1' | sudo tee -a /etc/sysctl.d/99-tailscale.conf
echo 'net.ipv6.conf.all.forwarding = 1' | sudo tee -a /etc/sysctl.d/99-tailscale.conf
sudo sysctl -p /etc/sysctl.d/99-tailscale.conf

sudo tailscale up --advertise-routes=192.168.1.0/24
```

**In Tailscale admin:**
- Visit: https://login.tailscale.com/admin/machines
- Click on vamsee-linux1
- Approve subnet routes

**Now you can access any local device:**
```bash
# From anywhere on internet via Tailscale
ping 192.168.1.1  # Your router
ssh user@192.168.1.50  # Other devices
```

### Exit Node (Route All Traffic)

Use your Linux machine as a VPN exit node:

**On Linux workspace:**
```bash
sudo tailscale up --advertise-exit-node
```

**Approve in admin panel, then use on other devices:**
```bash
tailscale up --exit-node=vamsee-linux1
```

All internet traffic will go through your home network.

## Tailscale Admin Panel

Manage your network at: https://login.tailscale.com/admin

**Features:**
- View all connected devices
- Enable/disable MagicDNS
- Approve subnet routes
- Set up ACLs (access control)
- View connection status
- Manage SSH access

## Security & Privacy

### How Tailscale Works

- **Encrypted:** WireGuard protocol (state-of-the-art encryption)
- **Peer-to-peer:** Direct connections between devices
- **No man-in-middle:** Tailscale servers only for coordination
- **Private keys:** Never leave your devices

### Access Control

**Block specific devices:**
```bash
# On Linux workspace
sudo tailscale up --shields-up
```

**Set up ACLs** in admin panel for fine-grained control.

### Logging

**View connections:**
```bash
tailscale status
```

**Check logs:**
```bash
sudo journalctl -u tailscaled -f
```

## Troubleshooting

### Cannot See Other Devices

**Check status:**
```bash
tailscale status
```

**Restart Tailscale:**
```bash
# Linux
sudo systemctl restart tailscaled
tailscale up

# Windows: Right-click icon → Quit → Restart
# Mac: Menu bar → Quit → Restart
```

### Connection Slow

**Check connection type:**
```bash
tailscale status
# Look for "relay" (slower) vs "direct" (faster)
```

**Force direct connection:**
- Disable any VPNs
- Ensure UDP not blocked
- Check firewall settings

### Cannot Connect to Linux Workspace

**Verify Tailscale is running:**
```bash
sudo systemctl status tailscaled
```

**Check SSH is running:**
```bash
sudo systemctl status ssh
```

**Ping test:**
```bash
ping 100.107.64.76
```

**SSH test with verbose:**
```bash
ssh -v vamsee@100.107.64.76
```

### IP Address Changed

Tailscale IPs are usually stable but can change. Check current IP:

```bash
tailscale ip -4
```

Update Tabby config if needed.

## Comparison: Local vs Tailscale

| Feature | Local Network | Tailscale |
|---------|--------------|-----------|
| Speed | Faster (gigabit) | Fast (50-200 Mbps) |
| Access | Same WiFi only | Anywhere on internet |
| Security | Local network security | Encrypted WireGuard |
| Setup | No setup | Install Tailscale |
| Firewall | Not needed | Works through any |
| IP | 192.168.1.100 | 100.107.64.76 |

**Recommendation:** Use local when home, Tailscale when away.

## Cost

- **Free tier:** Up to 100 devices, 1 user
- **Personal:** $48/year - 3 users, unlimited devices
- **Premium:** $120/year - Advanced features
- **Enterprise:** Custom pricing

**For personal use, free tier is more than enough!**

## Alternative: Tailscale + Cloudflare Tunnel

For extra security, you can combine:
- Tailscale for device-to-device
- Cloudflare Tunnel for web services

See: `docs/CLOUDFLARE_TUNNEL.md` (advanced)

## Additional Resources

- **Tailscale Docs:** https://tailscale.com/kb
- **WireGuard:** https://www.wireguard.com/
- **Admin Console:** https://login.tailscale.com/admin
- **Status Page:** https://status.tailscale.com/
- **Community:** https://forum.tailscale.com/

## Quick Command Reference

```bash
# Check status
tailscale status

# Get IP
tailscale ip -4

# Restart
sudo systemctl restart tailscaled

# Logout
tailscale logout

# Login
tailscale up

# Enable SSH
sudo tailscale up --ssh

# Check version
tailscale version

# Ping other device
tailscale ping vamsee-linux1
```
