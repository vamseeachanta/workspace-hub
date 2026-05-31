<#
.SYNOPSIS
  collect-equality.ps1 — Windows compute overlay for the #2801 machine-equality matrix (#2816).

.DESCRIPTION
  A THIN compute overlay over collect-equality.sh. Git Bash on Windows cannot reliably read
  RAM / disk / GPU (the .sh emits "unknown" for them, which the matrix grades MISSING-EVIDENCE),
  so this script computes those Windows-hard fields via CIM, exports them as EQ_* environment
  overrides, then delegates to `bash scripts/readiness/collect-equality.sh`.

  Schema, the provenance block, solver probes, behaviour probes, and the canonical-hash
  commit-on-change idempotency stay SINGLE-SOURCED in the .sh — this script only fills the five
  Windows compute fields. That avoids the schema-drift trap of a standalone reimplementation.

  W1 (Codex r2): this collector does NOT commit or push the resulting .claude/state/equality-*.yaml.
  Committing + pushing the state to origin so the central matrix can see it is the wrapper's job
  (scripts/windows/equality-report.ps1, #2815) — NOT this collector's. Run standalone, the report
  stays local (same as collect-equality.sh on Linux, which relies on repo-sync to push).

  W3 (Codex r2): a freshness preflight runs FIRST. If the checkout's origin/main ref cannot be
  shown to be fresh (fetch fails AND the local ref is stale/behind), the script FAILS FAST without
  writing a report — so a stale checkout never silently produces an all-STALE-CHECKOUT report.

.PARAMETER Stdout
  Pass through to collect-equality.sh --stdout (emit to stdout, do not write the state file).

.PARAMETER Machine
  Pass through to collect-equality.sh --machine <label> (override machine-label autodetection).

.NOTES
  Owner-machine-only. PowerShell cannot run on Linux CI; the contract is pinned by the
  Linux-runnable tests/readiness/test_collect_equality_ps1_schema.py against a golden fixture and
  the .sh EQ_* override seam. Run Invoke-ScriptAnalyzer on a PowerShell-present machine.
#>
[CmdletBinding()]
param(
    [switch]$Stdout,
    [string]$Machine
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# Resolve workspace root = two levels up from this script (scripts/readiness/ -> repo root).
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$WS = (Resolve-Path (Join-Path $ScriptDir '..\..')).Path

# ── W3: freshness preflight — establish a fresh origin/main BEFORE collecting ────────────────────
# A stale origin/main ref makes is_stale() fail-closed (origin_ref_age_h out of window OR
# behind_main != 0), so every cell would grade STALE-CHECKOUT. Try a fetch; if that fails, only
# proceed when the LOCAL origin/main ref is already current (behind_main == 0) AND recent. Else
# FAIL FAST without writing a report — a silent STALE report is worse than a loud, actionable miss.
function Test-Fresh {
    param([string]$Repo)
    # Best effort: refresh origin/main. A transient network miss is tolerated only if the local
    # ref is already current+recent (checked below); a hard inability to prove freshness fails.
    & git -C $Repo fetch --quiet origin main 2>$null | Out-Null
    $fetchOk = ($LASTEXITCODE -eq 0)

    $behind = (& git -C $Repo rev-list --count 'HEAD..origin/main' 2>$null)
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($behind)) {
        return @{ Fresh = $false; Reason = 'no origin/main ref (cannot establish freshness)' }
    }
    if ([int]$behind -ne 0) {
        return @{ Fresh = $false; Reason = "checkout is $behind commit(s) behind origin/main" }
    }
    if (-not $fetchOk) {
        # Fetch failed but local ref says behind==0. Only trust that if the ref is recent
        # (matches the matrix is_stale() 12h window), else we can't prove it's truly fresh.
        $commonDir = (& git -C $Repo rev-parse --git-common-dir 2>$null)
        if (-not [System.IO.Path]::IsPathRooted($commonDir)) {
            $commonDir = Join-Path $Repo $commonDir
        }
        # Age-check the tracked origin/main ref ONLY — NOT FETCH_HEAD. FETCH_HEAD is bumped by ANY
        # fetch (e.g. of an unrelated branch) and does not prove origin/main itself is fresh, so a
        # recent unrelated fetch could falsely pass freshness while origin/main is stale. If the
        # loose ref is absent (packed/never-fetched), we cannot prove freshness -> fail closed.
        $refPath = Join-Path $commonDir 'refs/remotes/origin/main'
        if (-not (Test-Path $refPath)) {
            return @{ Fresh = $false; Reason = 'fetch failed and no loose origin/main ref to age-check' }
        }
        $ageH = ((Get-Date) - (Get-Item $refPath).LastWriteTime).TotalHours
        if ($ageH -lt 0 -or $ageH -gt 12) {
            return @{ Fresh = $false; Reason = "fetch failed and local origin ref is $([math]::Round($ageH,1))h old (>12h)" }
        }
    }
    return @{ Fresh = $true; Reason = 'origin/main current' }
}

$freshness = Test-Fresh -Repo $WS
if (-not $freshness.Fresh) {
    Write-Error ("collect-equality.ps1: freshness preflight FAILED ({0}). " -f $freshness.Reason +
                 'Refusing to write a STALE-CHECKOUT report. Run the RepoSync task / `git fetch` ' +
                 'and retry.')
    exit 1
}

# ── CIM compute (the .ps1's real job) ────────────────────────────────────────────────────────────
$cs = Get-CimInstance Win32_ComputerSystem
$os = Get-CimInstance Win32_OperatingSystem

# Each CIM value is $null-guarded BEFORE arithmetic: PowerShell coerces a missing/null numeric
# to 0 in math (e.g. [math]::Floor($null / 1MB) == 0), which eqint() would accept as a valid 0 and
# mis-grade as BELOW-BASELINE instead of MISSING-EVIDENCE. A degraded CIM response must emit
# "unknown" (the .sh validator keeps it unknown -> matrix grades MISSING-EVIDENCE, fail-closed).
# cores
$env:EQ_CORES = if ($null -ne $cs -and $null -ne $cs.NumberOfLogicalProcessors) {
    [string]$cs.NumberOfLogicalProcessors } else { 'unknown' }
# RAM total: TotalPhysicalMemory is BYTES -> MiB
$env:EQ_RAM_TOTAL_MIB = if ($null -ne $cs -and $null -ne $cs.TotalPhysicalMemory) {
    [string][math]::Floor($cs.TotalPhysicalMemory / 1MB) } else { 'unknown' }
# RAM available: FreePhysicalMemory is KB -> MiB
$env:EQ_RAM_AVAIL_MIB = if ($null -ne $os -and $null -ne $os.FreePhysicalMemory) {
    [string][math]::Floor($os.FreePhysicalMemory / 1KB) } else { 'unknown' }

# Disk free on the drive that actually HOSTS the resolved workspace path — NOT a hardcoded D:.
$wsQualifier = (Split-Path -Qualifier $WS)              # e.g. "D:"
$disk = Get-CimInstance Win32_LogicalDisk -Filter ("DeviceID='{0}'" -f $wsQualifier)
if ($null -ne $disk -and $null -ne $disk.FreeSpace) {
    $env:EQ_DISK_AVAIL_GB = [string][math]::Floor($disk.FreeSpace / 1GB)
} else {
    $env:EQ_DISK_AVAIL_GB = 'unknown'                  # .sh validates -> stays unknown
}

# GPU: first video controller name, or "none". (Free-form string; the .sh escapes it.)
$gpu = (Get-CimInstance Win32_VideoController | Select-Object -First 1 -ExpandProperty Name -ErrorAction SilentlyContinue)
$env:EQ_GPU_MODEL = if ([string]::IsNullOrWhiteSpace($gpu)) { 'none' } else { $gpu }

# ── delegate to the canonical .sh (schema/provenance/solvers/idempotency single-sourced there) ───
$shPath = Join-Path $ScriptDir 'collect-equality.sh'
$shArgs = @($shPath)
if ($Stdout) { $shArgs += '--stdout' }
if (-not [string]::IsNullOrWhiteSpace($Machine)) { $shArgs += @('--machine', $Machine) }

& bash @shArgs
exit $LASTEXITCODE
