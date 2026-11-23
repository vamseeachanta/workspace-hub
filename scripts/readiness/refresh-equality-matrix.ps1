<#
.SYNOPSIS
  refresh-equality-matrix.ps1 --- operator-driven refresh of THIS machine's equality
  snapshot AND the live machine-equality matrix (Windows side; #2801 / #2998).

.DESCRIPTION
  Thin operator wrapper that does the manual-sync flow end to end:
    1. Ensure the checkout is on a fresh `main` (switch + pull --rebase --autostash).
    2. Run the Windows orchestrator scripts/windows/equality-report.ps1 -RefreshMatrix,
       which collects via CIM + Git Bash, builds the matrix, and commits+pushes the state
       yaml AND the matrix HTML in ONE commit so GitHub Pages redeploys.
    3. Print provenance + the resulting commit for quick verification.

  This is the manual equivalent of the scheduled task. The OS-paired Linux/macOS twin is
  refresh-equality-matrix.sh (delegates to equality-matrix-cron.sh). The actual
  collect/build/commit logic stays SINGLE-SOURCED in equality-report.ps1 --- this wrapper
  only adds fresh-main + verification ergonomics, so it cannot drift from the orchestrator.

.PARAMETER Machine
  Optional label override (e.g. ace-win-1) passed through to equality-report.ps1.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts\readiness\refresh-equality-matrix.ps1

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts\readiness\refresh-equality-matrix.ps1 -Machine ace-win-1

.NOTES
  ASCII-only on purpose: PS 5.1 reads BOM-less .ps1 as cp1252, so non-ASCII chars corrupt
  string parsing. Must run from main (equality-report.ps1 enforces this).
#>
[CmdletBinding()]
param(
    [string]$Machine
)

$ErrorActionPreference = 'Stop'

# Repo root = two levels up (scripts/readiness/ -> repo root). No hardcoded absolute paths.
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$WS = (Resolve-Path (Join-Path $ScriptDir '..\..')).Path

function Step($m) { Write-Host "`n=== $m ===" -ForegroundColor Cyan }

try {
    Set-Location $WS

    Step "1/3  Fresh main (switch + pull --rebase --autostash)"
    git switch main
    if ($LASTEXITCODE -ne 0) { throw "git switch main failed (exit $LASTEXITCODE)" }
    git pull --rebase --autostash origin main
    if ($LASTEXITCODE -ne 0) { throw "git pull failed (exit $LASTEXITCODE)" }

    Step "2/3  equality-report.ps1 -RefreshMatrix"
    $report = Join-Path $WS 'scripts\windows\equality-report.ps1'
    if (-not (Test-Path $report)) { throw "orchestrator not found: $report" }
    $reportArgs = @{ RefreshMatrix = $true }
    if ($Machine) { $reportArgs['Machine'] = $Machine }
    & $report @reportArgs
    if ($LASTEXITCODE -ne 0) { throw "equality-report.ps1 failed (exit $LASTEXITCODE)" }

    Step "3/3  Provenance + commit"
    Write-Host "--- provenance (expect dirty=false, behind_main=0, ahead_main=0, origin_ref_age_h 0-48)" -ForegroundColor Yellow
    Select-String -Path (Join-Path $WS '.claude\state\equality-*.yaml') `
                  -Pattern 'dirty|behind_main|ahead_main|origin_ref_age_h'
    Write-Host "`n--- last commit (expect 'chore: equality report from <machine>')" -ForegroundColor Yellow
    git log -1 --oneline
    Write-Host "`n--- status (expect clean, nothing ahead of origin/main)" -ForegroundColor Yellow
    git status -sb

    Write-Host "`nDONE. GitHub Pages redeploys in ~1-2 min:" -ForegroundColor Green
    Write-Host "  https://vamseeachanta.github.io/workspace-hub/machine-equality-matrix.html"
}
catch {
    Write-Host "`nFAILED: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Fix the step above and re-run. Never hand-edit the state yaml." -ForegroundColor Red
    exit 1
}
