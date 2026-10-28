# Behavioral preview and execution tests. Uses scratch fixtures; never installs tasks.
[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$ScratchDirectory)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$repo = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$root = Join-Path $ScratchDirectory "repository with spaces and 'quotes'"
if (Test-Path -LiteralPath $root) { throw 'Use a fresh scratch directory.' }
New-Item -ItemType Directory -Path $root -Force | Out-Null

function Assert-True {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { throw $Message }
}

# Any accidental scheduler call during a preview fails the test immediately.
foreach ($suffix in @('Action', 'Trigger', 'SettingsSet', 'Principal')) {
    Set-Item -Path ("function:New-ScheduledTask$suffix") -Value { throw 'Preview constructed a scheduler object.' }
}
foreach ($verb in @('Get', 'Register', 'Unregister')) {
    Set-Item -Path ("function:$verb-ScheduledTask") -Value { throw 'Preview accessed installed tasks.' }
}

$WorkspaceRoot = $repo
. (Join-Path $repo 'scripts/windows/scheduler-yaml.ps1')
. (Join-Path $repo 'scripts/windows/scheduler-actions.ps1')
$machines = @((Get-EqualityReportTask).Machines | Where-Object { $_ -match '-win-' })
Assert-True ($machines.Count -eq 2) 'Expected two Windows configurations in the catalog.'
$expected = @{
    ContextManagementDaily = 'scripts/coordination/context/daily_context_check.sh'
    WorkstationVersionCheck = 'scripts/readiness/workstation-version-check.sh'
    NightlyReadiness = 'scripts/readiness/nightly-readiness.sh'
    RepoSync = 'scripts/windows/repo-sync-daily.sh'
    MemoryBridgeSync = 'scripts/memory/bridge-hermes-claude.sh'
    HarnessUpdate = 'scripts/maintenance/update-harness-tools.sh'
    EqualityReport = 'scripts/windows/equality-report.ps1'
    SessionCuration = 'scripts/curation/curate-session-memory.ps1'
    EcosystemReconcile = 'scripts/windows/reconcile-ecosystem.ps1'
    EquivalenceSentinel = 'scripts/windows/equivalence-sentinel.ps1'
}
$files = @($expected.Values) + @(
    'scripts/windows/setup-scheduler-tasks.ps1',
    'scripts/windows/scheduler-yaml.ps1',
    'scripts/windows/scheduler-actions.ps1',
    'scripts/windows/run-scheduled-task.ps1',
    'scripts/coordination/context/setup_scheduled_task.ps1',
    'config/scheduled-tasks/schedule-tasks.yaml'
)
foreach ($relative in $files) {
    $destination = Join-Path $root $relative
    New-Item -ItemType Directory -Path (Split-Path -Parent $destination) -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $repo $relative) -Destination $destination
}
$installer = Join-Path $root 'scripts/windows/setup-scheduler-tasks.ps1'
foreach ($machine in $machines) {
    $definitions = @(& $installer -WorkspaceRoot $root -DryRun -MachineIdOverride $machine |
        ForEach-Object { $_ | ConvertFrom-Json })
    Assert-True ($definitions.Count -eq $expected.Count) 'Unexpected preview task count.'
    foreach ($definition in $definitions) {
        Assert-True ($definition.WorkingDirectory -eq $root) 'Working directory was not resolved.'
        Assert-True ([IO.Path]::IsPathRooted($definition.Execute)) 'Executable is relative.'
        Assert-True ($definition.ScriptPath -eq (Join-Path $root $expected[$definition.Name])) 'Script was not resolved.'
        Assert-True ($definition.Arguments.StartsWith('-NoProfile -File "')) 'Unexpected interpreter flags.'
        Assert-True ($definition.Arguments -notmatch 'ExecutionPolicy') 'Execution policy was overridden.'
        Assert-True ($definition.Arguments -match ' -Definition ([A-Za-z0-9+/=]+)$') 'Missing action data.'
        $data = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($Matches[1])) | ConvertFrom-Json
        Assert-True ($data.WorkingDirectory -eq $root) 'Action data lost path quoting.'
        Assert-True ($data.ScriptPath -eq $definition.ScriptPath) 'Preview and installed script disagree.'
        Assert-True ($definition.LogPath.StartsWith($root)) 'Log is outside the repository.'
        if ($definition.Name -eq 'SessionCuration') {
            Assert-True ($data.LogPattern -eq 'logs/monitoring/session-curation-*.log') 'Collector log pattern changed.'
            Assert-True ($definition.Schedule -eq 'every 6h at minute 47') 'Curation cadence changed.'
        }
        if ($definition.Name -eq 'EqualityReport') {
            Assert-True ($definition.Schedule -eq 'weekly Monday 04:30') 'Equality cadence changed.'
        }
        if ($definition.Name -eq 'ContextManagementDaily') {
            Assert-True ($data.Engine -eq 'Bash') 'Context shell script uses the wrong interpreter.'
        }
    }
    $subset = @(& $installer -WorkspaceRoot $root -WhatIf -EquivalenceOnly -MachineIdOverride $machine)
    Assert-True ($subset.Count -eq 4) 'Equivalence-only preview changed.'
}
$context = @(& (Join-Path $root 'scripts/coordination/context/setup_scheduled_task.ps1') -WorkspaceRoot $root -DryRun)
Assert-True ($context.Count -eq 1) 'Context compatibility installer did not render one task.'
$contextDefinition = $context[0] | ConvertFrom-Json
Assert-True ($contextDefinition.ScriptPath -eq (Join-Path $root $expected.ContextManagementDaily)) 'Context installers disagree.'

# The runner starts only disposable child scripts, including a nonzero result.
$WorkspaceRoot = $root
$child = Join-Path $root 'scripts/child.ps1'
$powershell = Get-TaskPowerShell
foreach ($code in @(0, 7)) {
    @"
param([string]`$Value)
Write-Output `$Value
[Console]::Error.WriteLine('child diagnostic')
exit $code
"@ | Set-Content -LiteralPath $child -Encoding utf8
    $argument = "argument with spaces and 'quotes'"
    $definition = New-RepoTaskDefinition -Name "child-$code" -ScriptPath 'scripts/child.ps1' `
        -PowerShell -ScriptArguments @('-Value', $argument)
    $encoded = ($definition.Arguments -split ' -Definition ')[1]
    & $powershell -NoProfile -File (Join-Path $root 'scripts/windows/run-scheduled-task.ps1') -Definition $encoded
    Assert-True ($LASTEXITCODE -eq $code) 'Child exit status was lost.'
    $logs = @(Get-ChildItem -LiteralPath (Join-Path $root 'logs/scheduler') -Filter "child-$code-*.log")
    Assert-True ($logs.Count -eq 1) 'Task log is missing.'
    $text = Get-Content -LiteralPath $logs[0].FullName -Raw
    Assert-True ($text.Contains($argument)) 'Child arguments or stdout were lost.'
    Assert-True ($text.Contains('child diagnostic')) 'Child stderr was lost.'
    Assert-True ($text.Contains("exit=$code")) 'Completion status was not logged.'
}
$bash = Resolve-GitBash
Assert-True (-not [string]::IsNullOrWhiteSpace($bash)) 'Git Bash is needed for the shell execution test.'
$child = Join-Path $root 'scripts/child.sh'
@'
printf '%s\n' "$1"
printf '%s\n' 'shell diagnostic' >&2
exit 3
'@ | Set-Content -LiteralPath $child -Encoding ascii
$definition = New-RepoTaskDefinition -Name 'shell-child' -ScriptPath 'scripts/child.sh' `
    -GitBashPath $bash -ScriptArguments @("shell argument with spaces and 'quotes'")
$encoded = ($definition.Arguments -split ' -Definition ')[1]
& $powershell -NoProfile -File (Join-Path $root 'scripts/windows/run-scheduled-task.ps1') -Definition $encoded
Assert-True ($LASTEXITCODE -eq 3) 'Shell exit status was lost.'
$logs = @(Get-ChildItem -LiteralPath (Join-Path $root 'logs/scheduler') -Filter 'shell-child-*.log')
Assert-True ($logs.Count -eq 1) 'Shell task log is missing.'
$text = Get-Content -LiteralPath $logs[0].FullName -Raw
Assert-True ($text.Contains("shell argument with spaces and 'quotes'")) 'Shell arguments were lost.'
Assert-True ($text.Contains('shell diagnostic')) 'Shell stderr was lost.'
Assert-True ($text.Contains('ERROR: exit=3')) 'Collector cannot recognize a failed shell task.'
Write-Output 'PASS: task previews, quoting, logging, and native exit status.'
