# setup-scheduler-tasks.ps1
# Registers all \Claude\ Windows Scheduled Tasks for workspace-hub on this workstation.
# Run as Administrator: powershell -ExecutionPolicy Bypass -File setup-scheduler-tasks.ps1
#
# Tasks registered:
#   \Claude\ContextManagementDaily     - daily context file health check
#   \Claude\WorkstationVersionCheck    - daily ANSYS + OrcaFlex version check
#   \Claude\NightlyReadiness           - daily ecosystem readiness
#   \Claude\RepoSync                   - daily workspace-hub git pull + submodule sync
#   \Claude\MemoryBridgeSync           - daily repo-tracked memory refresh
#   \Claude\HarnessUpdate              - daily AI CLI update (claude/codex/gemini) via native updater
#   \Claude\EqualityReport             - rendered from config/scheduled-tasks/schedule-tasks.yaml
#   \Claude\SessionCuration            - rendered from config/scheduled-tasks/schedule-tasks.yaml
#   \Claude\EcosystemReconcile         - daily report-first reconcile (no unattended apply)
#   \Claude\EquivalenceSentinel        - YAML-backed six-hour drift sentinel

[CmdletBinding()]
[Diagnostics.CodeAnalysis.SuppressMessageAttribute('PSAvoidUsingWriteHost', '', Justification='Operator-facing scheduler installer uses console output.')]
param(
    [string]$WorkspaceRoot = "",
    [switch]$WhatIf,
    [switch]$Remove,
    [switch]$EquivalenceOnly,
    [string]$MachineIdOverride = ""
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

if ($MachineIdOverride -and $MachineIdOverride -notmatch '^ace-win-[12]$') {
    throw "MachineIdOverride must be ace-win-1 or ace-win-2"
}
if ($MachineIdOverride -and (-not $WhatIf -or $Remove)) {
    throw "MachineIdOverride is allowed only with non-removal WhatIf"
}

if ([string]::IsNullOrWhiteSpace($WorkspaceRoot)) {
    $WorkspaceRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
}
$TaskPath = "\Claude\"
$RemoveMode = $Remove

function Resolve-GitBash {
    $candidates = New-Object System.Collections.Generic.List[string]
    $gitCommand = (Get-Command git -ErrorAction SilentlyContinue).Source
    if ($gitCommand) {
        $gitRoot = Split-Path -Parent (Split-Path -Parent $gitCommand)
        $candidates.Add((Join-Path $gitRoot 'bin\bash.exe'))
        $candidates.Add((Join-Path $gitRoot 'usr\bin\bash.exe'))
    }
    $candidates.Add('C:\Program Files\Git\bin\bash.exe')
    $candidates.Add('C:\Program Files\Git\usr\bin\bash.exe')
    $candidates.Add('C:\Program Files (x86)\Git\bin\bash.exe')
    $candidates.Add("$env:LOCALAPPDATA\Programs\Git\bin\bash.exe")
    foreach ($candidate in ($candidates | Select-Object -Unique)) {
        if (-not $candidate -or -not (Test-Path $candidate)) { continue }
        $uname = (& $candidate -c 'uname -s' 2>$null)
        if ($uname -match '^(MINGW|MSYS|CYGWIN)') { return $candidate }
    }
    return $null
}

$GitBash = Resolve-GitBash

function Test-Admin {
    $principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Get-DefaultTaskSetting {
    New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -RunOnlyIfNetworkAvailable:$false `
        -ExecutionTimeLimit (New-TimeSpan -Minutes 60) `
        -MultipleInstances IgnoreNew
}

function Get-CurrentMachineLabel {
    if ($MachineIdOverride) { return $MachineIdOverride }
    $hostName = if ($env:COMPUTERNAME) { $env:COMPUTERNAME.ToLowerInvariant() } else { "" }
    switch -Wildcard ($hostName) {
        "ace-win-1" { return "ace-win-1" }
        "acma-ansys05*" { return "ace-win-1" }
        "ace-win-2" { return "ace-win-2" }
        "acma-ws014*" { return "ace-win-2" }
        default { throw "Unknown Windows scheduler host '$hostName'; refusing to assume a ace-win-* identity" }
    }
}

. "$PSScriptRoot/scheduler-yaml.ps1"

function Convert-CronSchedule {
    param(
        [Parameter(Mandatory=$true)][string]$Schedule
    )

    $parts = $Schedule -split "\s+"
    if ($parts.Count -ne 5) {
        throw "Only 5-field cron schedules are supported for EqualityReport: '$Schedule'"
    }

    $minute, $hour, $dayOfMonth, $month, $dayOfWeek = $parts
    if ($dayOfMonth -ne "*" -or $month -ne "*") {
        throw "Only weekly/daily cron schedules are supported for EqualityReport: '$Schedule'"
    }
    if (-not ($minute -match "^\d+$") -or -not ($hour -match "^(\d+|\*/\d+)$")) {
        throw "Cron minute/hour must be numeric for EqualityReport: '$Schedule'"
    }

    $minuteInt = [int]$minute
    if ($minuteInt -lt 0 -or $minuteInt -gt 59) {
        throw "Cron minute/hour out of range for EqualityReport: '$Schedule'"
    }

    if ($hour -match '^\*/(\d+)$') {
        $intervalHours = [int]$Matches[1]
        if ($intervalHours -lt 1 -or $intervalHours -gt 23 -or $dayOfWeek -ne '*') {
            throw "Unsupported interval cron schedule: '$Schedule'"
        }
        return [pscustomobject]@{
            Kind = "Interval"; Time = (New-TimeSpan -Minutes $minuteInt)
            DaysOfWeek = @(); IntervalHours = $intervalHours
        }
    }

    $hourInt = [int]$hour
    if ($hourInt -lt 0 -or $hourInt -gt 23) {
        throw "Cron minute/hour out of range for EqualityReport: '$Schedule'"
    }

    $time = New-TimeSpan -Hours $hourInt -Minutes $minuteInt
    $days = @{
        "0" = "Sunday"; "7" = "Sunday"; "1" = "Monday"; "2" = "Tuesday";
        "3" = "Wednesday"; "4" = "Thursday"; "5" = "Friday"; "6" = "Saturday"
    }

    if ($dayOfWeek -eq "*") {
        return [pscustomobject]@{ Kind = "Daily"; Time = $time; DaysOfWeek = @() }
    }
    if (-not $days.ContainsKey($dayOfWeek)) {
        throw "Unsupported day-of-week cron field for EqualityReport: '$Schedule'"
    }
    return [pscustomobject]@{ Kind = "Weekly"; Time = $time; DaysOfWeek = @($days[$dayOfWeek]) }
}

function Format-TimeOfDay {
    param([TimeSpan]$Time)
    return "{0:D2}:{1:D2}" -f $Time.Hours, $Time.Minutes
}

function Format-TriggerSpec {
    param([Parameter(Mandatory=$true)]$Spec)
    if ($Spec.Kind -eq "Weekly") {
        return "weekly {0} {1}" -f ($Spec.DaysOfWeek -join ","), (Format-TimeOfDay -Time $Spec.Time)
    }
    if ($Spec.Kind -eq "Interval") {
        return "every {0}h at minute {1:D2}" -f $Spec.IntervalHours, $Spec.Time.Minutes
    }
    return "daily {0}" -f (Format-TimeOfDay -Time $Spec.Time)
}

function ConvertTo-TaskTrigger {
    param([Parameter(Mandatory=$true)]$Spec)
    $at = Format-TimeOfDay -Time $Spec.Time
    if ($Spec.Kind -eq "Weekly") {
        return New-ScheduledTaskTrigger -Weekly -DaysOfWeek $Spec.DaysOfWeek -At $at
    }
    if ($Spec.Kind -eq "Interval") {
        $now = Get-Date
        $start = Get-Date -Hour 0 -Minute $Spec.Time.Minutes -Second 0
        while ($start -le $now) { $start = $start.AddHours($Spec.IntervalHours) }
        return New-ScheduledTaskTrigger -Once -At $start `
            -RepetitionInterval (New-TimeSpan -Hours $Spec.IntervalHours) `
            -RepetitionDuration (New-TimeSpan -Days 3650)
    }
    return New-ScheduledTaskTrigger -Daily -At $at
}

function Register-ClaudeTask {
    [CmdletBinding(DefaultParameterSetName="Daily")]
    param(
        [Parameter(Mandatory=$true)][string]$Name,
        [Parameter(Mandatory=$true)][string]$Description,
        [Parameter(Mandatory=$true)][string]$ScriptPath,
        [Parameter(ParameterSetName="Daily", Mandatory=$true)][string]$DailyAt,
        [Parameter(ParameterSetName="Cron", Mandatory=$true)][string]$CronSchedule,
        [string]$TaskArguments = "",
        [switch]$PowerShell
    )

    $fullName = "${TaskPath}${Name}"

    if ($RemoveMode) {
        if ($WhatIf) {
            Write-Host "  [WhatIf] Would remove: $fullName"
            return
        }
        $existing = Get-ScheduledTask -TaskName $Name -TaskPath $TaskPath -ErrorAction SilentlyContinue
        if ($existing) {
            Unregister-ScheduledTask -TaskName $Name -TaskPath $TaskPath -Confirm:$false
            Write-Host "  Removed: $fullName" -ForegroundColor Yellow
        } else {
            Write-Host "  Not found (skip): $fullName"
        }
        return
    }

    if ($PSCmdlet.ParameterSetName -eq "Cron") {
        $triggerSpec = Convert-CronSchedule -Schedule $CronSchedule
    } else {
        $triggerSpec = [pscustomobject]@{
            Kind = "Daily"
            Time = [DateTime]::Parse($DailyAt).TimeOfDay
            DaysOfWeek = @()
        }
    }
    $triggerSummary = Format-TriggerSpec -Spec $triggerSpec

    if ($PowerShell) {
        $actionArgs = if ($TaskArguments) {
            "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`" $TaskArguments"
        } else {
            "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`""
        }
        $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $actionArgs -WorkingDirectory $WorkspaceRoot
        $execSummary = "powershell.exe $actionArgs"
    } else {
        $actionArgs = if ($TaskArguments) { "-c `"$ScriptPath $TaskArguments`"" } else { "-c `"$ScriptPath`"" }
        $action = New-ScheduledTaskAction -Execute $GitBash -Argument $actionArgs -WorkingDirectory $WorkspaceRoot
        $execSummary = "$GitBash $actionArgs"
    }

    $trigger = ConvertTo-TaskTrigger -Spec $triggerSpec
    $settings = Get-DefaultTaskSetting
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Limited

    if ($WhatIf) {
        Write-Host "  [WhatIf] Would register: $fullName at $triggerSummary"
        Write-Host "           Exec: $execSummary"
        return
    }

    $existing = Get-ScheduledTask -TaskName $Name -TaskPath $TaskPath -ErrorAction SilentlyContinue
    if ($existing) {
        Write-Host "  Removing existing: $fullName"
        Unregister-ScheduledTask -TaskName $Name -TaskPath $TaskPath -Confirm:$false
    }

    try {
        Register-ScheduledTask `
            -TaskName $Name `
            -TaskPath $TaskPath `
            -Action $action `
            -Trigger $trigger `
            -Settings $settings `
            -Principal $principal `
            -Description $Description | Out-Null
        Write-Host "  Registered: $fullName  ($triggerSummary)" -ForegroundColor Green
    } catch {
        Write-Error "  Failed to register ${fullName}: $_"
    }
}

if (-not $WhatIf -and -not (Test-Admin)) {
    Write-Error "Run this script as Administrator."
    exit 1
}

Write-Host ""
Write-Host "=============================================="
Write-Host " Claude Workspace Scheduler Tasks"
Write-Host " Workspace: $WorkspaceRoot"
Write-Host "=============================================="
Write-Host ""

if ($Remove) {
    $names = @('EqualityReport', 'SessionCuration', 'EcosystemReconcile', 'EquivalenceSentinel')
    if (-not $EquivalenceOnly) { $names = @('ContextManagementDaily', 'WorkstationVersionCheck', 'NightlyReadiness', 'RepoSync', 'MemoryBridgeSync', 'HarnessUpdate') + $names }
    foreach ($name in $names) { Register-ClaudeTask -Name $name -Description 'remove' -ScriptPath '.' -DailyAt '00:00' }
    Write-Host ""; Write-Host "Done."
    exit 0
}

if (-not $GitBash -or -not (Test-Path $GitBash)) {
    if ($WhatIf) { Write-Warning "Git Bash not found at '$GitBash'. Git-Bash-backed tasks would fail until it is installed or `$GitBash is updated." }
    else { Write-Error "Git Bash not found at '$GitBash'. Install Git for Windows or update `$GitBash."; exit 1 }
}

$currentMachine = Get-CurrentMachineLabel
$equalityTask = Get-EqualityReportTask
$curationTask = Get-ConfiguredTask -TaskId "session-curation"
$reconcileTask = Get-ConfiguredTask -TaskId "ecosystem-reconcile"
$sentinelTask = Get-ConfiguredTask -TaskId "equivalence-sentinel"
$sentinelScript = $null
if ($sentinelTask.Machines -contains $currentMachine) {
    $sentinelScript = Resolve-RepoTaskScript -RelativePath $sentinelTask.WindowsScript
}

if (-not $EquivalenceOnly) {
    Register-ClaudeTask `
        -Name "ContextManagementDaily" `
        -Description "Daily context file health check and improvement suggestions" `
        -ScriptPath "scripts/coordination/context/daily_context_check.bat" `
        -DailyAt "06:00AM"

    Register-ClaudeTask `
        -Name "WorkstationVersionCheck" `
        -Description "Daily ANSYS and OrcaFlex version check; appends Readiness section to daily log" `
        -ScriptPath "scripts/readiness/workstation-version-check.sh" `
        -DailyAt "07:00AM"

    Register-ClaudeTask `
        -Name "NightlyReadiness" `
        -Description "11-check ecosystem health; updates shared readiness proof" `
        -ScriptPath "scripts/readiness/nightly-readiness.sh" `
        -DailyAt "11:00PM"

    Register-ClaudeTask `
        -Name "RepoSync" `
        -Description "Nightly workspace-hub git pull and submodule sync" `
        -ScriptPath "scripts/windows/repo-sync-daily.sh" `
        -DailyAt "11:30PM"

    Register-ClaudeTask `
        -Name "MemoryBridgeSync" `
        -Description "Refresh repo-tracked memory outputs; commits and pushes (#1918)" `
        -ScriptPath "scripts/memory/bridge-hermes-claude.sh" `
        -TaskArguments "--commit" `
        -DailyAt "04:30AM"

    # HarnessUpdate — native AI CLI updater (claude/codex/gemini; hermes skipped on Windows).
    Register-ClaudeTask `
        -Name "HarnessUpdate" `
        -Description "Daily AI harness update via native updaters (claude/codex/gemini). #2920" `
        -ScriptPath "scripts/maintenance/update-harness-tools.sh" `
        -DailyAt "02:15AM"
}

if ($equalityTask.Machines -contains $currentMachine) {
    Register-ClaudeTask `
        -Name "EqualityReport" `
        -Description $equalityTask.Description `
        -ScriptPath "scripts/windows/equality-report.ps1" `
        -TaskArguments "-Machine $currentMachine" `
        -CronSchedule $equalityTask.Schedule `
        -PowerShell
} else {
    Write-Host "  Skip EqualityReport: $currentMachine is not listed in schedule-tasks.yaml"
}

if ($curationTask.Machines -contains $currentMachine) {
    Register-ClaudeTask `
        -Name "SessionCuration" `
        -Description $curationTask.Description `
        -ScriptPath "scripts/curation/curate-session-memory.ps1" `
        -TaskArguments "-Machine $currentMachine" `
        -CronSchedule $curationTask.Schedule `
        -PowerShell
}

if ($reconcileTask.Machines -contains $currentMachine) {
    Register-ClaudeTask `
        -Name "EcosystemReconcile" `
        -Description $reconcileTask.Description `
        -ScriptPath "scripts/windows/reconcile-ecosystem.ps1" `
        -TaskArguments "-Machine $currentMachine" `
        -CronSchedule $reconcileTask.Schedule `
        -PowerShell
}

if ($sentinelTask.Machines -contains $currentMachine) {
    Register-ClaudeTask `
        -Name "EquivalenceSentinel" `
        -Description $sentinelTask.Description `
        -ScriptPath $sentinelScript `
        -TaskArguments "-WorkspaceRoot `"$WorkspaceRoot`" -GitBashPath `"$GitBash`"" `
        -CronSchedule $sentinelTask.Schedule `
        -PowerShell
}

Write-Host ""
Write-Host "Done. To verify:"
Write-Host "  Get-ScheduledTask -TaskPath '\Claude\' | Select TaskName, State"
Write-Host ""
Write-Host "To run a task now:"
Write-Host "  Start-ScheduledTask -TaskName 'EqualityReport' -TaskPath '\Claude\'"
Write-Host ""
Write-Host "To remove all tasks:"
Write-Host "  powershell -File setup-scheduler-tasks.ps1 -Remove"
