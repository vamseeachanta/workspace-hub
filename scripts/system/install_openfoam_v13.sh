#!/bin/bash
# ABOUTME: OpenFOAM v13 installation script for Ubuntu 24.04 LTS
# ABOUTME: Removes old OpenFOAM v2212 and installs latest OpenFOAM.org v13

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Log file
LOG_FILE="${LOG_FILE:-logs/openfoam_install.log}"
mkdir -p "$(dirname "$LOG_FILE")"

# Logging functions
log_info() {
    local message="$1"
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO${NC} - $message"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO - $message" >> "$LOG_FILE"
}

log_success() {
    local message="$1"
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS${NC} - $message"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS - $message" >> "$LOG_FILE"
}

log_warning() {
    local message="$1"
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING${NC} - $message"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARNING - $message" >> "$LOG_FILE"
}

log_error() {
    local message="$1"
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR${NC} - $message" >&2
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR - $message" >> "$LOG_FILE"
}

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         OpenFOAM v13 Installation Script                      ║"
echo "║         OpenFOAM.org (Foundation Edition)                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if running on Ubuntu 24.04
log_info "Checking system requirements..."
if ! grep -q "Ubuntu 24.04" /etc/lsb-release; then
    log_warning "This script is designed for Ubuntu 24.04 LTS"
    log_warning "Your system: $(lsb_release -d | cut -f2)"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Installation cancelled by user"
        exit 0
    fi
fi

# Check available disk space
AVAILABLE_SPACE=$(df / | tail -1 | awk '{print $4}')
REQUIRED_SPACE=3000000  # ~3GB in KB
if [ "$AVAILABLE_SPACE" -lt "$REQUIRED_SPACE" ]; then
    log_error "Insufficient disk space. Need at least 3GB free."
    exit 1
fi
log_success "Sufficient disk space available"

# Check for sudo access
if ! sudo -n true 2>/dev/null; then
    log_info "This script requires sudo access. You may be prompted for your password."
fi

echo ""
log_info "=========================================="
log_info "Step 1: Removing old OpenFOAM v2212"
log_info "=========================================="
echo ""

# Remove old OpenFOAM packages
log_info "Removing OpenFOAM v2212 packages..."
sudo apt-get remove --purge -y \
    openfoam2212 \
    openfoam2212-common \
    openfoam2212-source \
    openfoam2212-tools \
    openfoam2212-tutorials \
    openfoam-selector 2>&1 | tee -a "$LOG_FILE"

log_info "Cleaning up unused dependencies..."
sudo apt-get autoremove -y 2>&1 | tee -a "$LOG_FILE"

log_success "Old OpenFOAM v2212 removed successfully"

echo ""
log_info "=========================================="
log_info "Step 2: Adding OpenFOAM.org Repository"
log_info "=========================================="
echo ""

# Add OpenFOAM.org GPG key
log_info "Adding OpenFOAM.org GPG key..."
sudo sh -c "wget -O - https://dl.openfoam.org/gpg.key > /etc/apt/trusted.gpg.d/openfoam.asc" 2>&1 | tee -a "$LOG_FILE"

# Add OpenFOAM.org repository
log_info "Adding OpenFOAM.org repository..."
sudo add-apt-repository -y http://dl.openfoam.org/ubuntu 2>&1 | tee -a "$LOG_FILE"

log_success "Repository added successfully"

echo ""
log_info "=========================================="
log_info "Step 3: Installing OpenFOAM v13"
log_info "=========================================="
echo ""

# Update package lists
log_info "Updating package lists..."
sudo apt-get update 2>&1 | tee -a "$LOG_FILE"

# Install OpenFOAM v13
log_info "Installing OpenFOAM v13 (this may take several minutes)..."
sudo apt-get install -y openfoam13 2>&1 | tee -a "$LOG_FILE"

log_success "OpenFOAM v13 installed successfully"

echo ""
log_info "=========================================="
log_info "Step 4: Configuring Environment"
log_info "=========================================="
echo ""

# Configure bashrc
BASHRC_LINE="source /opt/openfoam13/etc/bashrc"
if ! grep -q "$BASHRC_LINE" ~/.bashrc; then
    log_info "Adding OpenFOAM environment to ~/.bashrc..."
    echo "" >> ~/.bashrc
    echo "# OpenFOAM v13 environment" >> ~/.bashrc
    echo "$BASHRC_LINE" >> ~/.bashrc
    log_success "Environment configuration added to ~/.bashrc"
else
    log_info "OpenFOAM environment already configured in ~/.bashrc"
fi

# Source the bashrc for current session
log_info "Loading OpenFOAM environment..."
source /opt/openfoam13/etc/bashrc

log_success "Environment configured successfully"

echo ""
log_info "=========================================="
log_info "Step 5: Verifying Installation"
log_info "=========================================="
echo ""

# Verify installation
log_info "Checking OpenFOAM installation..."

if [ -d "/opt/openfoam13" ]; then
    log_success "OpenFOAM directory found: /opt/openfoam13"
else
    log_error "OpenFOAM directory not found!"
    exit 1
fi

# Test simpleFoam
log_info "Testing simpleFoam solver..."
source /opt/openfoam13/etc/bashrc
if command -v simpleFoam &> /dev/null; then
    OPENFOAM_VERSION=$(simpleFoam -help 2>&1 | grep "Build:" | head -1)
    log_success "simpleFoam found and working"
    log_info "Version info: $OPENFOAM_VERSION"
else
    log_error "simpleFoam command not found!"
    exit 1
fi

# Display installation summary
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                 Installation Complete! ✓                      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
log_success "OpenFOAM v13 has been successfully installed!"
echo ""
echo "📋 Installation Summary:"
echo "  • Version: OpenFOAM v13 (OpenFOAM.org)"
echo "  • Location: /opt/openfoam13"
echo "  • Old version removed: v2212"
echo "  • Environment: Configured in ~/.bashrc"
echo ""
echo "🚀 Next Steps:"
echo "  1. Start a new terminal session or run:"
echo "     source ~/.bashrc"
echo ""
echo "  2. Verify installation:"
echo "     simpleFoam -help"
echo ""
echo "  3. Test with a tutorial:"
echo "     cp -r /opt/openfoam13/tutorials/incompressible/simpleFoam/pitzDaily ~/openfoam_test"
echo "     cd ~/openfoam_test"
echo "     blockMesh"
echo "     simpleFoam"
echo ""
echo "📖 Documentation:"
echo "  • OpenFOAM v13 Release: https://openfoam.org/release/13/"
echo "  • User Guide: https://doc.cfd.direct/openfoam/user-guide-v13"
echo "  • Tutorials: /opt/openfoam13/tutorials"
echo ""
echo "📝 Log file: $LOG_FILE"
echo ""

log_info "Installation script completed successfully"
