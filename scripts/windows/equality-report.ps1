# equality-report.ps1
# Windows Task Scheduler wrapper for the #2801 machine-equality report.
#
# Responsibilities:
#   1. Prove the checkout is current with origin/main before collecting.
#   2. Run the CIM-backed Windows collector.
#   3. Build the matrix with system python.
#   4. Commit and push .claude/state/equality-*.yaml when it changed.

[CmdletBinding()]
param(
    [string]$WorkspaceRoot = ""
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

if ([string]::IsNullOrWhiteSpace($WorkspaceRoot)) {
    $WorkspaceRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
}

function Invoke-Checked {
    param(
        [Parameter(Mandatory=$true)][string]$File,
        [Parameter(Mandatory=$true)][string[]]$Arguments,
        [Parameter(Mandatory=$true)][string]$FailureMessage
    )

    & $File @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$FailureMessage (exit $LASTEXITCODE)"
    }
}

function Test-CommandAvailable {
    param([Parameter(Mandatory=$true)][string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command not found on PATH: $Name"
    }
}

function Get-CurrentBranch {
    $branch = (& git branch --show-current 2>$null).Trim()
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($branch)) {
        throw "Unable to determine current git branch"
    }
    return $branch
}

function Confirm-FreshCheckout {
    Invoke-Checked -File "git" -Arguments @("fetch", "--quiet", "origin", "main") `
        -FailureMessage "Unable to refresh origin/main; refusing to write an equality report"

    $behind = (& git rev-list --count "HEAD..origin/main" 2>$null).Trim()
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($behind)) {
        throw "Unable to compare HEAD with origin/main"
    }
    if ([int]$behind -ne 0) {
        throw "Checkout is $behind commit(s) behind origin/main; refusing to write an equality report"
    }

    $ahead = (& git rev-list --count "origin/main..HEAD" 2>$null).Trim()
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($ahead)) {
        throw "Unable to compare local commits with origin/main"
    }
    if ([int]$ahead -ne 0) {
        throw "Checkout is $ahead commit(s) ahead of origin/main; refusing to write a non-canonical equality report"
    }

    $measuredPaths = @(
        ".claude/skills",
        ".claude/memory/context.md",
        ".claude/dispatch",
        ".claude/rules",
        ".claude/hooks/plan-approval-gate.sh",
        ".claude/settings.json",
        "scripts/readiness/harness-config.yaml",
        "config/scheduled-tasks/schedule-tasks.yaml"
    )
    $statusArgs = @("status", "--porcelain", "--untracked-files=no", "--") + $measuredPaths
    $dirty = & git @statusArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to check measured-path dirty state"
    }
    if (-not [string]::IsNullOrWhiteSpace(($dirty -join ""))) {
        throw "Measured equality inputs are dirty; refusing to write a STALE-CHECKOUT report"
    }
}

function Confirm-PythonYaml {
    & python -c "import yaml" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Windows equality report requires system python with PyYAML installed: python -m pip install PyYAML"
    }
}

function Sync-EqualityState {
    param([Parameter(Mandatory=$true)][string]$Branch)

    Invoke-Checked -File "git" -Arguments @("add", "--", ".claude/state/equality-*.yaml") `
        -FailureMessage "Failed to stage equality state"

    & git diff --cached --quiet -- ".claude/state/equality-*.yaml"
    if ($LASTEXITCODE -eq 0) {
        Write-Output "No equality state changes to commit."
        return
    }

    $machine = if ($env:COMPUTERNAME) { $env:COMPUTERNAME.ToLowerInvariant() } else { "windows-machine" }
    Invoke-Checked -File "git" -Arguments @("commit", "-m", "chore: equality report from $machine") `
        -FailureMessage "Failed to commit equality state"

    $attempts = 3
    for ($attempt = 1; $attempt -le $attempts; $attempt++) {
        & git pull --rebase origin $Branch
        if ($LASTEXITCODE -ne 0) {
            & git rebase --abort 2>$null | Out-Null
            if ($attempt -eq $attempts) {
                throw "Failed to rebase before pushing equality state"
            }
            Start-Sleep -Seconds (5 * $attempt)
            continue
        }

        & git push origin $Branch
        if ($LASTEXITCODE -eq 0) {
            Write-Output "Pushed equality state on branch $Branch."
            return
        }

        if ($attempt -eq $attempts) {
            throw "Failed to push equality state after $attempts attempts"
        }
        Start-Sleep -Seconds (5 * $attempt)
    }
}

Set-Location $WorkspaceRoot
Test-CommandAvailable -Name "git"
Test-CommandAvailable -Name "bash"
Test-CommandAvailable -Name "python"

$branch = Get-CurrentBranch
Confirm-FreshCheckout
Confirm-PythonYaml

$collector = Join-Path $WorkspaceRoot "scripts\readiness\collect-equality.ps1"
$builder = Join-Path $WorkspaceRoot "scripts\readiness\build-equality-matrix.py"

Invoke-Checked -File "powershell" -Arguments @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $collector) `
    -FailureMessage "collect-equality.ps1 failed"
Invoke-Checked -File "python" -Arguments @($builder) `
    -FailureMessage "build-equality-matrix.py failed"

Sync-EqualityState -Branch $branch
