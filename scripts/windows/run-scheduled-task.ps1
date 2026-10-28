# Execute one installed task, recording output and preserving the child exit code.
[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$Definition)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
. "$PSScriptRoot/scheduler-actions.ps1"

$result = 1
$log = $null
try {
    $task = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($Definition)) | ConvertFrom-Json
    $root = (Resolve-Path -LiteralPath $task.WorkingDirectory).Path
    Set-Location -LiteralPath $root
    if ($task.LogPattern -notmatch '^logs/[a-zA-Z0-9_./-]+\*\.log$' -or
        ($task.LogPattern -split '/' -contains '..')) {
        throw 'Scheduled log pattern is invalid; reinstall the task.'
    }
    $log = Join-Path $root ($task.LogPattern.Replace('*', (Get-Date -Format 'yyyy-MM-dd-HHmmss-fff')))
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $log) | Out-Null
    "[$(Get-Date -Format o)] START $($task.Name)" | Out-File -LiteralPath $log -Encoding utf8 -Append
    if (-not [IO.Path]::IsPathRooted($task.ScriptPath) -or
        -not (Test-Path -LiteralPath $task.ScriptPath -PathType Leaf)) {
        throw 'Scheduled script is missing or is not absolute; reinstall the task.'
    }
    $env:WORKSPACE_HUB = $root -replace '\\', '/'
    $env:WORKSPACE_ROOT = $env:WORKSPACE_HUB
    $arguments = @($task.ScriptArguments)
    switch ($task.Engine) {
        'PowerShell' {
            $executable = Get-TaskPowerShell
            $arguments = @('-NoProfile', '-File', $task.ScriptPath) + $arguments
        }
        'Bash' {
            $executable = $task.GitBashPath
            if (-not $executable -or -not (Test-Path -LiteralPath $executable -PathType Leaf)) {
                throw 'Git Bash is unavailable; reinstall the task after installing Git for Windows.'
            }
            $arguments = @('--', ($task.ScriptPath -replace '\\', '/')) + $arguments
        }
        default { throw 'Unknown scheduled script engine; reinstall the task.' }
    }
    # Windows PowerShell turns native stderr into error records. Continue here
    # so a diagnostic on stderr cannot terminate a successful native process.
    $previousPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $LASTEXITCODE = $null
        & $executable @arguments 2>&1 | Out-File -LiteralPath $log -Encoding utf8 -Append
        $result = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousPreference
    }
    if ($null -eq $result) { throw 'Scheduled process did not return an exit code.' }
    $status = if ($result -eq 0) { 'OK:' } else { 'ERROR:' }
    "[$(Get-Date -Format o)] $status exit=$result" | Out-File -LiteralPath $log -Encoding utf8 -Append
} catch {
    $result = 1
    if ($log) {
        "[$(Get-Date -Format o)] ERROR: $($_.Exception.Message)" | Out-File -LiteralPath $log -Encoding utf8 -Append
    }
    Write-Error -Message $_ -ErrorAction Continue
}
exit $result
