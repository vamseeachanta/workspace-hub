#!/usr/bin/env bash
# engineering-suite-install.sh — Repeatable engineering workstation setup
# Target: Ubuntu 24.04 LTS (ace-linux-2 and future machines)
# Usage: sudo bash scripts/setup/engineering-suite-install.sh [--all | --core | --gis | --fea | --python]
#
# History:
#   2026-02-21  Initial creation from WRK-290 (ace-linux-2 setup)
#   2026-02-24  WRK-291: added --fea section (CalculiX, Elmer, FEniCSx)
#
# Tested on:
#   ace-linux-2  Ubuntu 24.04  2026-02-21  OpenFOAM OK, FreeCAD OK (PPA)
#   ace-linux-1  Ubuntu 24.04  2026-02-24  FEA user-space install (no root available)
#
# NOTE for ace-linux-1 (no-root user-space install):
#   CalculiX:  .deb extracted to ~/.local/lib/fea-libs + ~/.local/bin/ccx wrapper
#   Elmer FEM: built from source using miniforge3 compilers (v26.1)
#              install at ~/.local/elmer, wrapper at ~/.local/bin/ElmerSolver
#   FEniCSx:   conda env at ~/miniforge3/envs/fenicsx-env (v0.10.0)
#              wrapper at ~/.local/bin/fenicsx-python
#   Gmsh:      pip install --user --break-system-packages gmsh (v4.15.1)
#   See: docs/ops/fea-install-ace-linux-1.md for full details

set -euo pipefail

LOGFILE="/tmp/engineering-suite-install-$(date +%Y%m%d-%H%M%S).log"
echo "Logging to $LOGFILE"

log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOGFILE"; }

# ---------------------------------------------------------------------------
# Pre-flight
# ---------------------------------------------------------------------------
preflight() {
    log "=== Pre-flight checks ==="
    if [[ $EUID -ne 0 ]]; then
        echo "ERROR: Run with sudo or as root."
        echo "  sudo bash $0 $*"
        exit 1
    fi
    log "OS: $(lsb_release -ds 2>/dev/null || cat /etc/os-release | head -1)"
    log "Kernel: $(uname -r)"
    log "User: $(logname 2>/dev/null || echo "$SUDO_USER")"
    apt update -qq
}

# ---------------------------------------------------------------------------
# Core suite: Blender, FreeCAD, Gmsh, ParaView, OpenFOAM
# ---------------------------------------------------------------------------
install_core() {
    log "=== Installing core engineering suite ==="

    # Blender (apt — version 4.x on 24.04; snap has 5.x if preferred)
    log "Installing Blender..."
    apt install -y blender 2>&1 | tail -1 | tee -a "$LOGFILE"

    # Gmsh (mesh generation)
    log "Installing Gmsh..."
    apt install -y gmsh 2>&1 | tail -1 | tee -a "$LOGFILE"

    # ParaView (post-processing / visualization)
    log "Installing ParaView..."
    apt install -y paraview 2>&1 | tail -1 | tee -a "$LOGFILE"

    # FreeCAD (parametric CAD + FEM workbench)
    log "Installing FreeCAD via PPA..."
    add-apt-repository -y ppa:freecad-maintainers/freecad-stable 2>&1 | tail -1 | tee -a "$LOGFILE"
    apt update -qq
    apt install -y freecad 2>&1 | tail -1 | tee -a "$LOGFILE"

    # OpenFOAM (CFD — ESI version)
    log "Installing OpenFOAM..."
    if ! dpkg -l | grep -q openfoam; then
        curl -s https://dl.openfoam.com/add-debian-repo.sh | bash 2>&1 | tail -1 | tee -a "$LOGFILE"
        apt install -y openfoam2312-default 2>&1 | tail -1 | tee -a "$LOGFILE"
    else
        log "OpenFOAM already installed, skipping."
    fi
}

# ---------------------------------------------------------------------------
# GIS suite: QGIS, Google Earth Pro
# ---------------------------------------------------------------------------
install_gis() {
    log "=== Installing GIS suite ==="

    # QGIS (via official ubuntu repo — qgis.org)
    log "Installing QGIS..."
    if ! dpkg -l qgis &>/dev/null; then
        apt install -y gnupg software-properties-common 2>&1 | tail -1 | tee -a "$LOGFILE"
        local CODENAME
        CODENAME="$(lsb_release -cs)"
        local KEYRING="/etc/apt/keyrings/qgis-archive-keyring.gpg"
        if [[ ! -f "$KEYRING" ]]; then
            curl -fsSL https://download.qgis.org/downloads/qgis-archive-keyring.gpg \
                -o "$KEYRING"
        fi
        local SOURCES="/etc/apt/sources.list.d/qgis.sources"
        if [[ ! -f "$SOURCES" ]]; then
            cat > "$SOURCES" <<QGISEOF
Types: deb
URIs: https://qgis.org/ubuntu-ltr
Suites: ${CODENAME}
Architectures: amd64
Components: main
Signed-By: ${KEYRING}
QGISEOF
        fi
        apt update -qq
        apt install -y qgis python3-qgis 2>&1 | tail -1 | tee -a "$LOGFILE"
    else
        log "QGIS already installed, skipping."
    fi

    # Google Earth Pro
    log "Installing Google Earth Pro..."
    if ! dpkg -l google-earth-pro-stable &>/dev/null; then
        local GEP_DEB="/tmp/google-earth-pro-stable.deb"
        curl -fsSL -o "$GEP_DEB" \
            "https://dl.google.com/dl/earth/client/current/google-earth-pro-stable_current_amd64.deb"
        apt install -y "$GEP_DEB" 2>&1 | tail -1 | tee -a "$LOGFILE"
        rm -f "$GEP_DEB"
    else
        log "Google Earth Pro already installed, skipping."
    fi
}

# ---------------------------------------------------------------------------
# BemRosetta (BEM hydrodynamic analysis)
# ---------------------------------------------------------------------------
install_bemrosetta() {
    log "=== Installing BemRosetta ==="
    local USER_HOME
    USER_HOME=$(eval echo "~${SUDO_USER:-$USER}")
    local APP_DIR="$USER_HOME/Applications"
    mkdir -p "$APP_DIR"

    # Try release tarball first, fall back to AppImage
    local RELEASE_URL="https://github.com/BEMRosetta/BEMRosetta/releases/latest"
    log "Checking latest BemRosetta release..."
    local ACTUAL_URL
    ACTUAL_URL=$(curl -sIL "$RELEASE_URL" | grep -i '^location:' | tail -1 | tr -d '\r' | awk '{print $2}')
    log "Latest release: $ACTUAL_URL"

    # Download what's available — user may need to adjust
    log "NOTE: BemRosetta Linux packaging varies by release."
    log "Check $RELEASE_URL/latest for the correct download."
    log "Install manually to $APP_DIR if automated download fails."
}

# ---------------------------------------------------------------------------
# FEA programs (from WRK-289 research — top 3 recommendations)
# ---------------------------------------------------------------------------
install_fea() {
    log "=== Installing FEA programs ==="

    # CalculiX (structural FEA — #1 recommendation)
    log "Installing CalculiX..."
    apt install -y calculix-ccx calculix-cgx 2>&1 | tail -1 | tee -a "$LOGFILE"

    # Elmer FEM (multiphysics — #2 recommendation)
    log "Installing Elmer FEM..."
    add-apt-repository -y ppa:elmer-csc-team/elmer-csc-ppa 2>&1 | tail -1 | tee -a "$LOGFILE"
    apt update -qq
    apt install -y elmerfem-csc 2>&1 | tail -1 | tee -a "$LOGFILE"

    # FEniCSx (Python-based FEA — #3 recommendation)
    log "Installing FEniCSx..."
    add-apt-repository -y ppa:fenics-packages/fenics 2>&1 | tail -1 | tee -a "$LOGFILE"
    apt update -qq
    apt install -y fenicsx 2>&1 | tail -1 | tee -a "$LOGFILE" || {
        log "WARN: fenicsx PPA failed, try conda instead:"
        log "  conda create -n fenicsx-env python=3.12 fenics-dolfinx -c conda-forge"
    }
}

# ---------------------------------------------------------------------------
# Python packages
# ---------------------------------------------------------------------------
install_python() {
    log "=== Installing Python packages ==="
    apt install -y python3-pip python3-venv 2>&1 | tail -1 | tee -a "$LOGFILE"

    local SUDO_USER_HOME
    SUDO_USER_HOME=$(eval echo "~${SUDO_USER:-$USER}")

    # Install into user space (avoids --break-system-packages)
    su - "${SUDO_USER:-$USER}" -c "pip3 install --user meshio PyFoam pyvista gmsh" 2>&1 | tee -a "$LOGFILE" || {
        log "WARN: pip --user failed, trying with --break-system-packages..."
        su - "${SUDO_USER:-$USER}" -c "pip3 install --user --break-system-packages meshio PyFoam pyvista gmsh" 2>&1 | tee -a "$LOGFILE"
    }
}

# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------
verify() {
    log "=== Verification ==="
    local pass=0 fail=0

    check() {
        if eval "$2" &>/dev/null; then
            log "  PASS: $1"
            ((pass++))
        else
            log "  FAIL: $1"
            ((fail++))
        fi
    }

    check "Blender"         "blender --version"
    check "FreeCAD"         "which freecad || which freecad-cmd"
    check "Gmsh"            "gmsh --version"
    check "ParaView"        "paraview --version"
    check "OpenFOAM"        "which simpleFoam || ls /usr/lib/openfoam/*/bin/simpleFoam"
    check "QGIS"            "which qgis"
    check "Google Earth"    "which google-earth-pro"
    check "CalculiX"        "which ccx || which ccx_2.23 || ~/.local/bin/ccx --version"
    check "Elmer"           "which ElmerSolver || ~/.local/bin/ElmerSolver --version"
    check "FEniCSx"         "python3 -c 'import dolfinx' || ~/.local/bin/fenicsx-python -c 'import dolfinx'"
    check "Gmsh (Python)"   "python3 -c 'import gmsh'"
    check "ccx2paraview"    "python3 -m ccx2paraview --help"
    check "meshio"          "python3 -c 'import meshio'"
    check "PyFoam"          "python3 -c 'import PyFoam'"

    log ""
    log "Results: $pass passed, $fail failed"
    log "Full log: $LOGFILE"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
    local mode="${1:---all}"
    preflight

    case "$mode" in
        --all)
            install_core
            install_gis
            install_bemrosetta
            install_fea
            install_python
            ;;
        --core)
            install_core
            install_bemrosetta
            ;;
        --gis)
            install_gis
            ;;
        --fea)
            install_fea
            ;;
        --python)
            install_python
            ;;
        --verify)
            verify
            return
            ;;
        *)
            echo "Usage: sudo bash $0 [--all | --core | --gis | --fea | --python | --verify]"
            exit 1
            ;;
    esac

    verify
}

main "$@"
