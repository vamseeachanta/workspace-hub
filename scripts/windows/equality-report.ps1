# equality-report.ps1
# Windows Task Scheduler wrapper for the #2801 machine-equality report.
#
# Responsibilities:
#   1. Prove the checkout is current with origin/main before collecting.
#   2. Run the CIM-backed Windows collector.
#   3. Build the matrix with system python.
#   4. Commit and push .claude/state/equality-<machine>.yaml when it changed.

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
    if ($branch -ne "main") {
        throw "EqualityReport must run from main, not '$branch'"
    }
    return $branch
}

function Get-EqualityMachineLabel {
    $hostName = if ($env:COMPUTERNAME) { $env:COMPUTERNAME.ToLowerInvariant() } else { "" }
    switch -Wildcard ($hostName) {
        "ace-win-1" { return "ace-win-1" }
        "acma-ansys05*" { return "ace-win-1" }
        "ace-win-2" { return "ace-win-2" }
        "acma-ws014*" { return "ace-win-2" }
        default { throw "Unknown Windows equality host '$hostName'; refusing to assume a ace-win-* identity" }
    }
}

function Get-MatrixReportPath {
    return ("docs/reports/{0}-machine-equality-matrix.html" -f (Get-Date -Format "yyyy-MM-dd"))
}

function Invoke-EqualityTranscript {
    param([Parameter(Mandatory=$true)][string]$Machine)

    $logDir = Join-Path $WorkspaceRoot "logs\quality"
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null
    $logPath = Join-Path $logDir ("equality-{0}-{1}.log" -f (Get-Date -Format "yyyy-MM-dd"), $Machine)
    Start-Transcript -Path $logPath -Append | Out-Null
    return $true
}

function Get-RevCount {
    param([Parameter(Mandatory=$true)][string]$Range)
    $count = (& git rev-list --count $Range 2>$null).Trim()
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($count)) {
        throw "Unable to compare git range $Range"
    }
    return [int]$count
}

function Test-AheadCommitIsEqualityReport {
    param([Parameter(Mandatory=$true)][string]$Machine)

    $expectedPath = ".claude/state/equality-$Machine.yaml"
    $subjects = & git log --format=%s "origin/main..HEAD"
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to inspect local commits ahead of origin/main"
    }
    foreach ($subject in $subjects) {
        if ($subject -notmatch "^chore: equality report from ") {
            return $false
        }
    }

    $commits = & git rev-list "origin/main..HEAD"
    if ($LASTEXITCODE -ne 0 -or $commits.Count -eq 0) {
        throw "Unable to inspect local commit paths ahead of origin/main"
    }
    foreach ($commit in $commits) {
        $paths = & git diff-tree --no-commit-id --name-only -r $commit
        if ($LASTEXITCODE -ne 0 -or $paths.Count -eq 0) {
            return $false
        }
        foreach ($path in $paths) {
            if ($path -ne $expectedPath) {
                return $false
            }
        }
    }
    return $true
}

function Push-ExistingEqualityCommit {
    param(
        [Parameter(Mandatory=$true)][string]$Branch,
        [Parameter(Mandatory=$true)][string]$Machine,
        [Parameter(Mandatory=$true)][int]$Ahead
    )

    if ($Ahead -le 0) {
        return
    }
    if (-not (Test-AheadCommitIsEqualityReport -Machine $Machine)) {
        throw "Checkout is $Ahead commit(s) ahead of origin/main with non-equality commits; refusing to push"
    }

    & git push origin $Branch
    if ($LASTEXITCODE -ne 0) {
        throw "Existing local equality commit(s) could not be pushed; will retry on the next scheduled run"
    }

    Invoke-Checked -File "git" -Arguments @("fetch", "--quiet", "origin", "+refs/heads/main:refs/remotes/origin/main") `
        -FailureMessage "Unable to refresh origin/main after pushing existing equality commit(s)"

    $remainingAhead = Get-RevCount -Range "origin/main..HEAD"
    if ($remainingAhead -ne 0) {
        throw "Checkout remains $remainingAhead commit(s) ahead after pushing existing equality commit(s)"
    }
}

function Invoke-ExistingEqualityCommitRebase {
    param(
        [Parameter(Mandatory=$true)][string]$Machine,
        [Parameter(Mandatory=$true)][int]$Behind,
        [Parameter(Mandatory=$true)][int]$Ahead
    )

    if ($Behind -le 0) {
        return $false
    }
    if ($Ahead -le 0) {
        throw "Checkout is $Behind commit(s) behind origin/main; refusing to write an equality report"
    }
    if (-not (Test-AheadCommitIsEqualityReport -Machine $Machine)) {
        throw "Checkout is behind origin/main and has non-equality local commits; refusing unattended recovery"
    }

    & git rebase origin/main
    if ($LASTEXITCODE -ne 0) {
        & git rebase --abort 2>$null | Out-Null
        throw "Failed to rebase existing equality commit onto origin/main; refusing stale report"
    }
    return $true
}

function Confirm-FreshCheckout {
    param(
        [Parameter(Mandatory=$true)][string]$Branch,
        [Parameter(Mandatory=$true)][string]$Machine
    )

    Invoke-Checked -File "git" -Arguments @("fetch", "--quiet", "origin", "+refs/heads/main:refs/remotes/origin/main") `
        -FailureMessage "Unable to refresh origin/main; refusing to write an equality report"

    $behind = Get-RevCount -Range "HEAD..origin/main"
    $ahead = Get-RevCount -Range "origin/main..HEAD"
    Invoke-ExistingEqualityCommitRebase -Machine $Machine -Behind $behind -Ahead $ahead | Out-Null
    $ahead = Get-RevCount -Range "origin/main..HEAD"
    Push-ExistingEqualityCommit -Branch $Branch -Machine $Machine -Ahead $ahead

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

function Confirm-MatrixReportClean {
    param([Parameter(Mandatory=$true)][string]$ReportPath)

    $status = & git status --porcelain --untracked-files=all -- $ReportPath
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to check matrix report worktree state"
    }
    if (-not [string]::IsNullOrWhiteSpace(($status -join ""))) {
        throw "Matrix report path is already dirty; refusing to overwrite $ReportPath"
    }
}

function Clear-GeneratedMatrixReport {
    param([Parameter(Mandatory=$true)][string]$ReportPath)

    & git ls-files --error-unmatch -- $ReportPath *> $null
    if ($LASTEXITCODE -eq 0) {
        Invoke-Checked -File "git" -Arguments @("restore", "--worktree", "--", $ReportPath) `
            -FailureMessage "Failed to restore generated matrix report"
    } elseif (Test-Path $ReportPath) {
        Remove-Item -LiteralPath $ReportPath -Force
    }
}

function Confirm-PythonYaml {
    & python -c "import yaml" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Windows equality report requires system python with PyYAML installed: python -m pip install PyYAML"
    }
}

function Sync-EqualityState {
    param(
        [Parameter(Mandatory=$true)][string]$Branch,
        [Parameter(Mandatory=$true)][string]$Machine
    )

    $statePath = ".claude/state/equality-$Machine.yaml"
    if (-not (Test-Path $statePath)) {
        throw "Expected equality state was not written: $statePath"
    }

    Invoke-Checked -File "git" -Arguments @("add", "--", $statePath) `
        -FailureMessage "Failed to stage equality state"

    & git diff --cached --quiet -- $statePath
    if ($LASTEXITCODE -eq 0) {
        Write-Output "No equality state changes to commit."
        return
    }

    $ahead = Get-RevCount -Range "origin/main..HEAD"
    $machine = if ($env:COMPUTERNAME) { $env:COMPUTERNAME.ToLowerInvariant() } else { "windows-machine" }
    if ($ahead -gt 0) {
        if ($ahead -gt 1 -or -not (Test-AheadCommitIsEqualityReport -Machine $Machine)) {
            throw "Local commits ahead of origin/main are not a single equality report; refusing to amend"
        }
        $commitArgs = @("commit", "--amend", "--only", "-m", "chore: equality report from $machine", "--", $statePath)
    } else {
        $commitArgs = @("commit", "--only", "-m", "chore: equality report from $machine", "--", $statePath)
    }

    Invoke-Checked -File "git" -Arguments $commitArgs `
        -FailureMessage "Failed to commit equality state"

    & git push origin $Branch
    if ($LASTEXITCODE -eq 0) {
        Write-Output "Pushed equality state on branch $Branch."
        return
    }

    throw "Failed to push equality state; leaving local equality commit for the next scheduled retry"
}

$transcriptStarted = $false
Set-Location $WorkspaceRoot
try {
    $machine = Get-EqualityMachineLabel
    $transcriptStarted = Invoke-EqualityTranscript -Machine $machine

    Test-CommandAvailable -Name "git"
    Test-CommandAvailable -Name "bash"
    Test-CommandAvailable -Name "python"

    $branch = Get-CurrentBranch
    $matrixReport = Get-MatrixReportPath
    Confirm-FreshCheckout -Branch $branch -Machine $machine
    Confirm-MatrixReportClean -ReportPath $matrixReport
    Confirm-PythonYaml

    $collector = Join-Path $WorkspaceRoot "scripts\readiness\collect-equality.ps1"
    $builder = Join-Path $WorkspaceRoot "scripts\readiness\build-equality-matrix.py"

    Invoke-Checked -File "powershell" -Arguments @(
        "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $collector, "-Machine", $machine) `
        -FailureMessage "collect-equality.ps1 failed"
    Invoke-Checked -File "python" -Arguments @($builder) `
        -FailureMessage "build-equality-matrix.py failed"
    Clear-GeneratedMatrixReport -ReportPath $matrixReport

    Sync-EqualityState -Branch $branch -Machine $machine
} finally {
    if ($transcriptStarted) {
        Stop-Transcript | Out-Null
    }
}
