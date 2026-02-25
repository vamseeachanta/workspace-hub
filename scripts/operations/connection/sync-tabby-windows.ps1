# ABOUTME: Sync Tabby terminal config from workspace-hub to Windows system
# ABOUTME: Run this script after pulling workspace-hub changes

param(
    [string]$WorkspaceRoot = "C:\workspace-hub"
)

$ErrorActionPreference = "Stop"

$WorkspaceConfig = Join-Path $WorkspaceRoot "config\tabby"
$TabbyConfig = Join-Path $env:APPDATA "tabby"

Write-Host "=== Tabby Config Sync (Windows) ===" -ForegroundColor Blue

# Check if Tabby is installed
$tabbyPath = Get-Command tabby -ErrorAction SilentlyContinue
if (-not $tabbyPath) {
    Write-Host "Warning: Tabby is not installed" -ForegroundColor Yellow
    Write-Host "Download from: https://github.com/Eugeny/tabby/releases/latest" -ForegroundColor Yellow
    Write-Host "Install the .exe installer for Windows" -ForegroundColor Yellow
    exit 1
}

# Create config directory if it doesn't exist
if (-not (Test-Path $TabbyConfig)) {
    New-Item -ItemType Directory -Path $TabbyConfig -Force | Out-Null
}

# Backup existing config
$configFile = Join-Path $TabbyConfig "config.yaml"
if (Test-Path $configFile) {
    Write-Host "Backing up existing config..." -ForegroundColor Blue
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    Copy-Item $configFile "$configFile.backup.$timestamp"
}

# Copy config from workspace-hub
Write-Host "Syncing config from workspace-hub..." -ForegroundColor Blue
$sourceConfig = Join-Path $WorkspaceConfig "config.yaml"
Copy-Item $sourceConfig $configFile -Force

# Copy plugins if they exist
$pluginsSource = Join-Path $WorkspaceConfig "plugins"
if (Test-Path $pluginsSource) {
    Write-Host "Syncing plugins..." -ForegroundColor Blue
    $pluginsDest = Join-Path $TabbyConfig "plugins"
    if (-not (Test-Path $pluginsDest)) {
        New-Item -ItemType Directory -Path $pluginsDest -Force | Out-Null
    }
    Copy-Item "$pluginsSource\*" $pluginsDest -Recurse -Force
}

Write-Host "✓ Tabby config synced successfully" -ForegroundColor Green
Write-Host "Note: Restart Tabby for changes to take effect" -ForegroundColor Yellow
