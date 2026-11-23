# ABOUTME: One-time setup -- creates Windows Task Scheduler job for solver queue polling
# Run as Administrator on licensed-win-1:
#   powershell -ExecutionPolicy Bypass -File .\scripts\solver\setup-scheduler.ps1
#
# What it does:
#   1. Creates a scheduled task "SolverQueue" that runs every 30 minutes
#   2. Each run: git pull -> python process-queue.py -> logs to queue/solver-queue.log
#   3. If task already exists, updates it in place

$RepoPath = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$TaskName = "SolverQueue"
$PythonScript = Join-Path $RepoPath "scripts\solver\process-queue.py"
$LogFile = Join-Path $RepoPath "queue\solver-queue.log"

Write-Host "Solver Queue Scheduler Setup"
Write-Host "============================"
Write-Host "Repo path:      $RepoPath"
Write-Host "Python script:  $PythonScript"
Write-Host "Log file:       $LogFile"
Write-Host ""

# Verify files exist
if (-not (Test-Path $PythonScript)) {
    Write-Error "Queue processor not found: $PythonScript"
    exit 1
}

# Create the scheduled task action
# Pull latest, then process queue, log everything
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument @"
-NoProfile -ExecutionPolicy Bypass -Command "cd '$RepoPath'; git pull origin main 2>&1 | Out-File -Append '$LogFile'; python '$PythonScript' 2>&1 | Out-File -Append '$LogFile'; Write-Output '--- $(Get-Date -Format o) ---' | Out-File -Append '$LogFile'"
"@

# Trigger: every 30 minutes, indefinitely
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Minutes 30) `
    -RepetitionDuration (New-TimeSpan -Days 3650)

# Settings: run whether logged in or not, don't stop if running longer than default
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1)

# Register (or update if exists)
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Set-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings
    Write-Host "Updated existing task: $TaskName"
} else {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $Action `
        -Trigger $Trigger `
        -Settings $Settings `
        -Description "Polls queue/pending/ for solver jobs every 30 minutes" `
        -RunLevel Highest
    Write-Host "Created task: $TaskName"
}

Write-Host ""
Write-Host "Next steps:"
Write-Host "  Verify:     Get-ScheduledTask -TaskName '$TaskName'"
Write-Host "  Manual run: Start-ScheduledTask -TaskName '$TaskName'"
Write-Host "  Logs:       Get-Content '$LogFile' -Tail 20"
