# Remote Access to Tabby Terminal

Access your Linux workspace machine terminal from anywhere using SSH through Tabby.

## Machine Information

**Linux Workspace Machine:**
- **Hostname:** vamsee-linux1
- **Local IP:** 192.168.1.100
- **Username:** vamsee
- **SSH Port:** 22

## Quick Connect

### From Windows Machine (Tabby)

1. Install Tabby on Windows (see SETUP_QUICK.md)
2. Sync config: `.\scripts\sync-tabby-windows.ps1`
3. Open Tabby → Connection profiles → "Linux Workspace (vamsee-linux1)"
4. Enter password when prompted

### From Any Machine (SSH)

**Using command line:**
```bash
ssh vamsee@192.168.1.100
```

**Using Tabby manually:**
1. Open Tabby → New Tab → SSH Connection
2. Enter:
   - Host: 192.168.1.100
   - User: vamsee
   - Port: 22
3. Save profile (optional)

## Setup Requirements

### On Linux Machine (Already Done ✓)

- [x] SSH server installed and running
- [x] SSH profile added to Tabby config
- [x] Firewall allows port 22

### On Remote Machine (Windows/Linux/Mac)

1. **Install Tabby** (if not installed)
   - Windows: Download from https://tabby.sh
   - Linux: See main README.md
   - Mac: `brew install tabby`

2. **Sync workspace-hub config:**
   - Windows: `.\scripts\sync-tabby-windows.ps1`
   - Linux: `./scripts/sync-tabby-linux.sh`

3. **Connect:**
   - Open Tabby
   - Find "Linux Workspace (vamsee-linux1)" in profiles
   - Click to connect

## SSH Key Authentication (Recommended)

For passwordless login, set up SSH keys:

### On Remote Machine:

**Generate SSH key (if you don't have one):**
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

**Copy key to Linux workspace:**
```bash
ssh-copy-id vamsee@192.168.1.100
```

**Test connection:**
```bash
ssh vamsee@192.168.1.100
```

### Update Tabby Profile:

Edit `config/tabby/config.yaml` and add your private key:

```yaml
profiles:
  - name: Linux Workspace (vamsee-linux1)
    type: ssh
    id: workspace-linux-main
    options:
      host: 192.168.1.100
      user: vamsee
      port: 22
      privateKey: ~/.ssh/id_ed25519  # Linux/Mac
      # privateKey: C:\Users\YourName\.ssh\id_ed25519  # Windows
```

## Remote Access Over Internet

To access from outside your local network:

### Option 1: Port Forwarding (Requires Router Access)

1. **Configure router:**
   - Forward external port (e.g., 2222) to 192.168.1.100:22
   - Set up Dynamic DNS (recommended)

2. **Update connection:**
   ```bash
   ssh -p 2222 vamsee@your-public-ip-or-domain
   ```

### Option 2: Tailscale VPN (Recommended)

1. **Install Tailscale:**
   ```bash
   # On Linux workspace
   curl -fsSL https://tailscale.com/install.sh | sh
   sudo tailscale up
   
   # On remote machine
   # Install Tailscale client
   ```

2. **Connect using Tailscale IP:**
   - Both machines join same Tailscale network
   - Use Tailscale IP instead of local IP

### Option 3: SSH Tunnel/Jump Host

Use a cloud server as jump host:
```bash
ssh -J jumphost@cloud-server.com vamsee@192.168.1.100
```

## Tabby Features for Remote Access

### Multiple Tabs/Splits

- **New tab:** Ctrl+Shift+T
- **Split vertical:** Ctrl+Shift+E
- **Split horizontal:** Ctrl+Shift+D

### Session Persistence (tmux)

Keep sessions alive after disconnect:

```bash
# On Linux workspace, install tmux
sudo apt install tmux

# Start tmux session
tmux new -s workspace

# Detach: Ctrl+B then D
# Reattach after reconnect
tmux attach -t workspace
```

### File Transfer

**Using SCP:**
```bash
# Upload to Linux workspace
scp file.txt vamsee@192.168.1.100:~/

# Download from Linux workspace
scp vamsee@192.168.1.100:~/file.txt ./
```

**Using Tabby SFTP:**
1. Connect to SSH profile
2. Right-click → "Open SFTP panel"
3. Drag and drop files

## Troubleshooting

### Cannot Connect

**Check SSH service:**
```bash
sudo systemctl status ssh
```

**Check firewall:**
```bash
sudo ufw status
sudo ufw allow 22
```

**Verify IP address:**
```bash
hostname -I
```

### Connection Drops

**Keep connection alive:**

Edit `~/.ssh/config` on remote machine:
```
Host workspace
    HostName 192.168.1.100
    User vamsee
    ServerAliveInterval 60
    ServerAliveCountMax 10
```

**In Tabby:**
- Settings → SSH → Keep-alive interval: 60 seconds

### Slow Connection

**Enable compression:**

In Tabby SSH profile options:
```yaml
options:
  algorithms:
    compression: ['zlib@openssh.com', 'zlib', 'none']
```

### Permission Denied

**Check SSH key permissions:**
```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
```

**Check authorized_keys:**
```bash
chmod 600 ~/.ssh/authorized_keys
```

## Security Best Practices

1. **Use SSH keys instead of passwords**
2. **Disable password authentication** (after SSH keys working):
   ```bash
   sudo nano /etc/ssh/sshd_config
   # Set: PasswordAuthentication no
   sudo systemctl restart ssh
   ```
3. **Change default SSH port** (optional):
   ```bash
   # Edit /etc/ssh/sshd_config
   Port 2222
   ```
4. **Enable fail2ban**:
   ```bash
   sudo apt install fail2ban
   sudo systemctl enable --now fail2ban
   ```
5. **Use VPN for internet access** (Tailscale/WireGuard)

## Connection Profiles for Different Networks

Add multiple profiles for different scenarios:

```yaml
profiles:
  # Local network
  - name: Workspace (Local)
    options:
      host: 192.168.1.100
  
  # Internet (port forwarding)
  - name: Workspace (Internet)
    options:
      host: your-domain.com
      port: 2222
  
  # Tailscale VPN
  - name: Workspace (VPN)
    options:
      host: 100.x.x.x  # Tailscale IP
```

## Advanced: Web-Based Terminal Access

For browser-based access, see: `docs/WEB_TERMINAL_SETUP.md` (optional)

## Need Help?

- Tabby docs: https://tabby.sh/
- SSH troubleshooting: `man ssh_config`
- Community: https://github.com/Eugeny/tabby/discussions
