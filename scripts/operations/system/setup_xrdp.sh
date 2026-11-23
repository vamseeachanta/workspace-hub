#!/bin/bash

# Script to set up xrdp on Ubuntu for Windows Remote Desktop Connection
# Run with: sudo bash setup_xrdp.sh

set -e  # Exit on any error

echo "========================================="
echo "Ubuntu xrdp Setup Script"
echo "========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Update package list
echo "[1/7] Updating package list..."
apt update

# Install xrdp
echo "[2/7] Installing xrdp..."
apt install -y xrdp

# Install additional packages for better compatibility
echo "[3/7] Installing additional packages..."
apt install -y xorgxrdp

# Add xrdp user to ssl-cert group for certificate access
echo "[4/7] Configuring xrdp user permissions..."
adduser xrdp ssl-cert

# Enable and start xrdp service
echo "[5/7] Enabling and starting xrdp service..."
systemctl enable xrdp
systemctl start xrdp

# Configure firewall if ufw is active
echo "[6/7] Configuring firewall..."
if systemctl is-active --quiet ufw; then
    echo "UFW firewall is active. Adding rule for port 3389..."
    ufw allow 3389/tcp
    echo "Firewall rule added."
else
    echo "UFW firewall is not active. Skipping firewall configuration."
fi

# Display system IP address
echo "[7/7] Getting IP address..."
echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Your IP address(es):"
ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '127.0.0.1'
echo ""
echo "To connect from Windows:"
echo "1. Open Remote Desktop Connection (mstsc)"
echo "2. Enter one of the IP addresses above"
echo "3. Click Connect"
echo "4. Log in with your Ubuntu username and password"
echo ""
echo "Service status:"
systemctl status xrdp --no-pager
echo ""
echo "========================================="
