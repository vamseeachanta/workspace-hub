# ABOUTME: Quick connect script for Windows machines to access Linux workspace
# ABOUTME: Opens SSH connection in Tabby or fallback to Windows Terminal/PowerShell

param(
    [string]$Method = "tabby"  # Options: tabby, cmd, powershell
)

$WorkspaceHost = "192.168.1.100"
$WorkspaceUser = "vamsee"
$WorkspacePort = 22

Write-Host "=== Connecting to Linux Workspace ===" -ForegroundColor Blue
Write-Host "Host: $WorkspaceHost" -ForegroundColor Cyan
Write-Host "User: $WorkspaceUser" -ForegroundColor Cyan

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
# .\connect-workspace-windows.ps1                    # Use Tabby (default)
# .\connect-workspace-windows.ps1 -Method cmd        # Use Command Prompt
# .\connect-workspace-windows.ps1 -Method powershell # Use PowerShell
