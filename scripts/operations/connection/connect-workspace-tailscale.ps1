# ABOUTME: Quick connect script to access Linux workspace via Tailscale VPN (Windows)
# ABOUTME: Works from anywhere on the internet

param(
    [string]$Method = "tabby"  # Options: tabby, cmd, powershell
)

$WorkspaceHost = "100.107.64.76"
$WorkspaceHostname = "vamsee-linux1"
$WorkspaceUser = "vamsee"
$WorkspacePort = 22

Write-Host "=== Connecting to Linux Workspace (Tailscale) ===" -ForegroundColor Blue

# Check if Tailscale is installed
$tailscalePath = Get-Command tailscale -ErrorAction SilentlyContinue
if (-not $tailscalePath) {
    Write-Host "❌ Tailscale is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Install Tailscale:" -ForegroundColor Yellow
    Write-Host "  Visit: https://tailscale.com/download/windows" -ForegroundColor Yellow
    Write-Host "  Download and run the installer" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Check if Tailscale is connected
$tailscaleStatus = & tailscale status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Tailscale is not connected!" -ForegroundColor Red
    Write-Host "Click Tailscale icon in system tray → Log in to Tailscale" -ForegroundColor Yellow
    exit 1
}

# Check if we can reach the workspace
Write-Host "Checking connection to workspace..." -ForegroundColor Cyan
$pingResult = Test-Connection -ComputerName $WorkspaceHost -Count 1 -Quiet -ErrorAction SilentlyContinue
if ($pingResult) {
    Write-Host "✓ Workspace is reachable via Tailscale" -ForegroundColor Green
} else {
    Write-Host "❌ Cannot reach workspace!" -ForegroundColor Red
    Write-Host "Check:" -ForegroundColor Yellow
    Write-Host "  1. Workspace machine is online" -ForegroundColor Yellow
    Write-Host "  2. Both devices on same Tailscale network" -ForegroundColor Yellow
    Write-Host "  3. Run: tailscale status" -ForegroundColor Yellow
    exit 1
}

Write-Host "Host: $WorkspaceHost ($WorkspaceHostname)" -ForegroundColor Cyan
Write-Host "User: $WorkspaceUser" -ForegroundColor Cyan
Write-Host ""

switch ($Method.ToLower()) {
    "tabby" {
        $tabbyPath = Get-Command tabby -ErrorAction SilentlyContinue
        if ($tabbyPath) {
            Write-Host "Opening Tabby..." -ForegroundColor Green
            & tabby ssh://${WorkspaceUser}@${WorkspaceHost}:${WorkspacePort}
        } else {
            Write-Host "Tabby not found. Install from: https://tabby.sh" -ForegroundColor Yellow
            Write-Host "Falling back to PowerShell SSH..." -ForegroundColor Yellow
            ssh ${WorkspaceUser}@${WorkspaceHost}
        }
    }
    "cmd" {
        Write-Host "Opening in Command Prompt..." -ForegroundColor Green
        Start-Process cmd.exe -ArgumentList "/k ssh ${WorkspaceUser}@${WorkspaceHost}"
    }
    "powershell" {
        Write-Host "Opening in PowerShell..." -ForegroundColor Green
        Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", "ssh ${WorkspaceUser}@${WorkspaceHost}"
    }
    default {
        Write-Host "Connecting via SSH..." -ForegroundColor Green
        ssh ${WorkspaceUser}@${WorkspaceHost}
    }
}

# Usage examples:
# .\connect-workspace-tailscale.ps1                    # Use Tabby (default)
# .\connect-workspace-tailscale.ps1 -Method cmd        # Use Command Prompt
# .\connect-workspace-tailscale.ps1 -Method powershell # Use PowerShell
