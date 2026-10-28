# setup_scheduled_task.ps1 - Create Windows scheduled task for daily context check
# Run as Administrator: powershell -NoProfile -File setup_scheduled_task.ps1

[CmdletBinding()]
param(
    [string]$WorkspaceRoot = '',
    [Alias('DryRun')][switch]$WhatIf
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$TaskName = "ContextManagementDaily"
$TaskPath = "\Claude\"
$Description = "Daily context file health check and improvement suggestions"
if (-not $WorkspaceRoot) { $WorkspaceRoot = Join-Path $PSScriptRoot '../../..' }
$WorkspaceRoot = (Resolve-Path -LiteralPath $WorkspaceRoot).Path
. (Join-Path $WorkspaceRoot 'scripts/windows/scheduler-yaml.ps1')
. (Join-Path $WorkspaceRoot 'scripts/windows/scheduler-actions.ps1')
$bash = Resolve-GitBash
if (-not $bash -and -not $WhatIf) { throw 'Git Bash was not found.' }
$definition = New-RepoTaskDefinition -Name $TaskName `
    -ScriptPath 'scripts/coordination/context/daily_context_check.sh' -GitBashPath $bash
if ($WhatIf) {
    Write-Output ($definition | Select-Object *, @{Name='Schedule'; Expression={'daily 06:00'}} | ConvertTo-Json -Compress -Depth 5)
    return
}

# Check if running as admin
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "Please run this script as Administrator" -ForegroundColor Red
    exit 1
}

Write-Host "=========================================="
Write-Host "Setting up Windows Scheduled Task"
Write-Host "=========================================="
Write-Host ""

# Remove existing task if present
$existingTask = Get-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "Removing existing task..."
    Unregister-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath -Confirm:$false
}

# Create the action
$Action = New-ScheduledTaskAction -Execute $definition.Execute -Argument $definition.Arguments -WorkingDirectory $definition.WorkingDirectory

# Create the trigger (daily at 6:00 AM)
$Trigger = New-ScheduledTaskTrigger -Daily -At 6:00AM

# Create settings
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable:$false `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

# Create the principal (run whether user is logged on or not)
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Limited

# Register the task
try {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -TaskPath $TaskPath `
        -Action $Action `
        -Trigger $Trigger `
        -Settings $Settings `
        -Principal $Principal `
        -Description $Description

    Write-Host ""
    Write-Host "Task created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task Details:"
    Write-Host "  Name: $TaskName"
    Write-Host "  Path: $TaskPath"
    Write-Host "  Schedule: Daily at 6:00 AM"
    Write-Host "  Script: $($definition.ScriptPath)"
    Write-Host ""
    Write-Host "To run manually:"
    Write-Host "  schtasks /run /tn `"\Claude\$TaskName`""
    Write-Host ""
    Write-Host "To view task:"
    Write-Host "  Get-ScheduledTask -TaskName $TaskName"
    Write-Host ""
    Write-Host "To remove task:"
    Write-Host "  Unregister-ScheduledTask -TaskName $TaskName"
}
catch {
    Write-Host "Error creating task: $_" -ForegroundColor Red
    exit 1
}

# Verify task was created
$task = Get-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath -ErrorAction SilentlyContinue
if ($task) {
    Write-Host "Verification: Task exists and is ready." -ForegroundColor Green
}
else {
    Write-Host "Verification failed: Task not found." -ForegroundColor Red
}
