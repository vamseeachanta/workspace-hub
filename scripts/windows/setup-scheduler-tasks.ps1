# setup-scheduler-tasks.ps1
# Registers all \Claude\ Windows Scheduled Tasks for workspace-hub on this workstation.
# Run as Administrator: powershell -ExecutionPolicy Bypass -File setup-scheduler-tasks.ps1
#
# Tasks registered:
#   \Claude\ContextManagementDaily     — 06:00 daily  — context file health check
#   \Claude\WorkstationVersionCheck    — 07:00 daily  — ANSYS + OrcaFlex version check
#   \Claude\NightlyReadiness           — 23:00 daily  — 11-check ecosystem readiness
#   \Claude\RepoSync                   — 23:30 daily  — workspace-hub git pull + submodule sync
#   \Claude\MemoryBridgeSync           — 04:30 daily  — refresh repo-tracked memory outputs (#1918)

param(
    [switch]$WhatIf,
    [switch]$Remove
)

$WorkspaceRoot = "D:\workspace-hub"
$GitBash = "C:\Program Files\Git\bin\bash.exe"
$TaskPath = "\Claude\"

# ── Helpers ──────────────────────────────────────────────────────────────────

function Require-Admin {
    $p = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    if (-not $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Write-Error "Run this script as Administrator."
        exit 1
    }
}

function Default-Settings {
    New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -RunOnlyIfNetworkAvailable:$false `
        -ExecutionTimeLimit (New-TimeSpan -Minutes 60) `
        -MultipleInstances IgnoreNew
}

function Register-ClaudeTask {
    param(
        [string]$Name,
        [string]$Description,
        [string]$ScriptPath,
        [string]$Time,
        [string]$Args = ""
    )

    $fullName = "${TaskPath}${Name}"

    if ($Remove) {
        $existing = Get-ScheduledTask -TaskName $Name -ErrorAction SilentlyContinue
        if ($existing) {
            Unregister-ScheduledTask -TaskName $Name -TaskPath $TaskPath -Confirm:$false
            Write-Host "  Removed: $fullName" -ForegroundColor Yellow
        } else {
            Write-Host "  Not found (skip): $fullName"
        }
        return
    }

    $actionArgs = if ($Args) { "-c `"$ScriptPath $Args`"" } else { "-c `"$ScriptPath`"" }
    $Action    = New-ScheduledTaskAction -Execute $GitBash -Argument $actionArgs -WorkingDirectory $WorkspaceRoot
    $Trigger   = New-ScheduledTaskTrigger -Daily -At $Time
    $Settings  = Default-Settings
    $Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Limited

    if ($WhatIf) {
        Write-Host "  [WhatIf] Would register: $fullName at $Time"
        Write-Host "           Exec: $GitBash $actionArgs"
        return
    }

    $existing = Get-ScheduledTask -TaskName $Name -ErrorAction SilentlyContinue
    if ($existing) {
        Write-Host "  Removing existing: $fullName"
        Unregister-ScheduledTask -TaskName $Name -TaskPath $TaskPath -Confirm:$false
    }

    try {
        Register-ScheduledTask `
            -TaskName $Name `
            -TaskPath $TaskPath `
            -Action $Action `
            -Trigger $Trigger `
            -Settings $Settings `
            -Principal $Principal `
            -Description $Description | Out-Null
        Write-Host "  Registered: $fullName  ($Time daily)" -ForegroundColor Green
    } catch {
        Write-Error "  Failed to register ${fullName}: $_"
    }
}

# ── Main ─────────────────────────────────────────────────────────────────────

if (-not $WhatIf) { Require-Admin }

if (-not (Test-Path $GitBash)) {
    Write-Error "Git Bash not found at '$GitBash'. Install Git for Windows or update `$GitBash."
    exit 1
}

Write-Host ""
Write-Host "=============================================="
Write-Host " Claude Workspace Scheduler Tasks"
Write-Host " Workspace: $WorkspaceRoot"
Write-Host "=============================================="
Write-Host ""

# 1. Context management — 06:00
Register-ClaudeTask `
    -Name "ContextManagementDaily" `
    -Description "Daily context file health check and improvement suggestions" `
    -ScriptPath "scripts/coordination/context/daily_context_check.bat" `
    -Time "06:00AM"

# 2. Workstation version check (ANSYS + OrcaFlex) — 07:00
Register-ClaudeTask `
    -Name "WorkstationVersionCheck" `
    -Description "Daily ANSYS and OrcaFlex version check; appends Readiness section to daily log" `
    -ScriptPath "scripts/readiness/workstation-version-check.sh" `
    -Time "07:00AM"

# 3. Nightly readiness (11 ecosystem checks) — 23:00
# Writes shared readiness proof under .claude/state/harness-readiness-licensed-win-1.yaml
Register-ClaudeTask `
    -Name "NightlyReadiness" `
    -Description "11-check ecosystem health: memory, context budget, submodules, harness files, ANSYS, OrcaFlex; updates shared readiness proof" `
    -ScriptPath "scripts/readiness/nightly-readiness.sh" `
    -Time "11:00PM"

# 4. Repo sync — 23:30
Register-ClaudeTask `
    -Name "RepoSync" `
    -Description "Nightly workspace-hub git pull and submodule sync" `
    -ScriptPath "scripts/windows/repo-sync-daily.sh" `
    -Time "11:30PM"

# 5. Memory bridge sync — 04:30 (#1918)
# Refreshes context.md, Claude auto-memory snapshot, and topic mirrors; commits + pushes.
# On Windows, Hermes is absent — the bridge gracefully skips Hermes-specific steps.
Register-ClaudeTask `
    -Name "MemoryBridgeSync" `
    -Description "Refresh repo-tracked memory outputs (context.md, auto-memory snapshot, topic mirrors); commits and pushes (#1918)" `
    -ScriptPath "scripts/memory/bridge-hermes-claude.sh" `
    -Args "--commit" `
    -Time "04:30AM"

Write-Host ""
Write-Host "Done. To verify:"
Write-Host "  Get-ScheduledTask -TaskPath '\Claude\' | Select TaskName, State"
Write-Host ""
Write-Host "To run a task now:"
Write-Host "  Start-ScheduledTask -TaskName 'WorkstationVersionCheck' -TaskPath '\Claude\'"
Write-Host ""
Write-Host "To remove all tasks:"
Write-Host "  powershell -File setup-scheduler-tasks.ps1 -Remove"
