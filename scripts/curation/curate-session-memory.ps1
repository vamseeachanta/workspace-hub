<#
.SYNOPSIS
  curate-session-memory.ps1 --- Windows Task Scheduler companion to curate-session-memory.sh.

.DESCRIPTION
  Fail-loud wrapper for the "session analysis & memory curation" line item of the machine-equality
  matrix. Mirrors scripts/curation/curate-session-memory.sh one-for-one on Windows:

    curate (analyze provider logs + memory delta, publish the session-curation-state fingerprint)
      -> refresh THIS box's equality column (collect-equality.ps1 -> build-equality-matrix.py)

  so a healthy box always shows the freshness cell green and an up-to-date render.

  Python selection mirrors the .sh: prefer the uv path that resolves pyyaml
  ('uv run --no-project --with pyyaml python <script>'), else fall back to plain 'python'.

  Collector: runs collect-equality.ps1 (the Windows-appropriate collector --- it computes the
  Windows-hard CIM compute fields and delegates the rest, INCLUDING the session_curation block,
  to collect-equality.sh; that delegation is why no PowerShell session_curation emission is needed).

  On ANY hard failure: emit a notify.sh JSONL event (best-effort, via Git Bash --- same channel as
  the .sh) and exit non-zero. The notification is non-blocking; a missing Git Bash never masks the
  real failure exit code.

.NOTES
  Owner-machine-only (Windows Task Scheduler). PowerShell cannot run on Linux CI; the Linux-runnable
  parity is pinned by the .sh wrapper + the collector contract tests.
#>
[CmdletBinding()]
param([string]$Machine = "")

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ── repo root = git toplevel, else two levels up from scripts/curation/ ───────
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = (& git -C $ScriptDir rev-parse --show-toplevel 2>$null)
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = (Resolve-Path (Join-Path $ScriptDir '..\..')).Path
}
Set-Location $RepoRoot

# Windows PowerShell 5.1 otherwise gives Python a cp1252 stdout stream; the
# curation engine emits Unicode status text after writing its state.
$env:PYTHONUTF8 = '1'

if (-not [string]::IsNullOrWhiteSpace($Machine)) {
    $env:EQ_MACHINE = $Machine
}

# ── best-effort Git Bash resolver (for notify.sh only; never fatal) ──────────
function Resolve-GitBash {
    $candidates = New-Object System.Collections.Generic.List[string]
    $gitCmd = (Get-Command git -ErrorAction SilentlyContinue).Source
    if ($gitCmd) {
        $gitRoot = Split-Path -Parent (Split-Path -Parent $gitCmd)
        $candidates.Add((Join-Path $gitRoot 'bin\bash.exe'))
        $candidates.Add((Join-Path $gitRoot 'usr\bin\bash.exe'))
    }
    $candidates.Add('C:\Program Files\Git\bin\bash.exe')
    $candidates.Add("$env:LOCALAPPDATA\Programs\Git\bin\bash.exe")
    foreach ($c in ($candidates | Select-Object -Unique)) {
        if ($c -and (Test-Path $c)) { return $c }
    }
    return $null
}

function Send-Notify {
    param([string]$Status, [string]$Details)
    # Mirrors `bash scripts/notify.sh cron session-curation <status> "<details>"`; non-blocking.
    $bash = Resolve-GitBash
    if ($null -eq $bash) { return }
    $notify = (Join-Path $RepoRoot 'scripts/notify.sh') -replace '\\', '/'
    try { & $bash $notify cron session-curation $Status $Details 2>$null | Out-Null } catch { }
}

function Fail {
    param([string]$Message)
    Send-Notify -Status 'fail' -Details $Message
    Write-Error "curate-session-memory FAIL: $Message"
    exit 1
}

# ── 1. curation engine (prefer the uv pyyaml path, else plain python) ────────
$engine = (Join-Path $RepoRoot 'scripts/curation/curate_session_memory.py')
if (Get-Command uv -ErrorAction SilentlyContinue) {
    & uv run --no-project --with pyyaml python $engine
    if ($LASTEXITCODE -ne 0) { Fail 'curation engine failed (uv)' }
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python $engine
    if ($LASTEXITCODE -ne 0) { Fail 'curation engine failed (python)' }
} else {
    Fail 'no python runtime (uv/python) available'
}

# ── 1a2. regenerate the per-machine skills index before the audit (no rot) ────
$genIndex = (Join-Path $RepoRoot 'scripts/skills/generate_skills_index.py')
if (Test-Path $genIndex) {
    if (Get-Command uv -ErrorAction SilentlyContinue) {
        & uv run --no-project --with pyyaml python $genIndex
        if ($LASTEXITCODE -ne 0) { Write-Warning 'skills-index regen failed (soft)' }
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        & python $genIndex
        if ($LASTEXITCODE -ne 0) { Write-Warning 'skills-index regen failed (soft)' }
    }
}

# ── 1b. skill-currency audit (#3249) — best-effort; must not block the curation run ──
# Without this the skill_currency cell is permanently MISSING-EVIDENCE on Windows boxes.
$skillAudit = (Join-Path $RepoRoot 'scripts/curation/audit_skill_currency.py')
if (Get-Command uv -ErrorAction SilentlyContinue) {
    & uv run --no-project --with pyyaml python $skillAudit
    if ($LASTEXITCODE -ne 0) { Write-Warning 'skill-currency audit failed (soft)' }
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python $skillAudit
    if ($LASTEXITCODE -ne 0) { Write-Warning 'skill-currency audit failed (soft)' }
}

# ── 1c. skill-drift detect + alert (#3250) — best-effort, after the audit ────
$skillDrift = (Join-Path $RepoRoot 'scripts/curation/detect_skill_drift.py')
if (Get-Command uv -ErrorAction SilentlyContinue) {
    & uv run --no-project --with pyyaml python $skillDrift
    if ($LASTEXITCODE -ne 0) { Write-Warning 'skill-drift detect failed (soft)' }
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python $skillDrift
    if ($LASTEXITCODE -ne 0) { Write-Warning 'skill-drift detect failed (soft)' }
}

# ── 1d. memory-freshness audit (#3255) — best-effort, after skill drift ──────
$memFresh = (Join-Path $RepoRoot 'scripts/curation/audit_memory_freshness.py')
if (Get-Command uv -ErrorAction SilentlyContinue) {
    & uv run --no-project --with pyyaml python $memFresh
    if ($LASTEXITCODE -ne 0) { Write-Warning 'memory-freshness audit failed (soft)' }
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python $memFresh
    if ($LASTEXITCODE -ne 0) { Write-Warning 'memory-freshness audit failed (soft)' }
}

# ── 1e. skill-link-health audit (#3251) — BASH engine via Git Bash; best-effort ──
# resync-skill-links.sh is bash; invoke it through the resolved Git Bash. If Git Bash is absent the
# skill_link_health cell stays MISSING-EVIDENCE (honest scoping — no silent green).
$bashForSkills = Resolve-GitBash
if ($null -ne $bashForSkills) {
    $resync = (Join-Path $RepoRoot 'scripts/skills/resync-skill-links.sh') -replace '\\', '/'
    try {
        if ([string]::IsNullOrWhiteSpace($Machine)) {
            & $bashForSkills $resync 2>$null | Out-Null
        } else {
            & $bashForSkills $resync --machine $Machine 2>$null | Out-Null
        }
    } catch { Write-Warning 'skill-link-health audit failed (soft)' }
} else {
    Write-Warning 'skill-link-health audit skipped — Git Bash not found'
}

# ── 2. refresh THIS box's equality column (Windows collector + matrix build) ──
$collector = (Join-Path $ScriptDir '..\readiness\collect-equality.ps1')
if ([string]::IsNullOrWhiteSpace($Machine)) {
    & $collector
} else {
    & $collector -Machine $Machine
}
if ($LASTEXITCODE -ne 0) { Fail 'collect-equality.ps1 failed' }

$matrix = (Join-Path $RepoRoot 'scripts/readiness/build-equality-matrix.py')
if (Get-Command uv -ErrorAction SilentlyContinue) {
    & uv run --no-project --with pyyaml python $matrix
    if ($LASTEXITCODE -ne 0) { Fail 'build-equality-matrix.py failed (uv)' }
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python $matrix
    if ($LASTEXITCODE -ne 0) { Fail 'build-equality-matrix.py failed (python)' }
} else {
    Fail 'no python runtime (uv/python) available for matrix build'
}

Send-Notify -Status 'pass' -Details 'curated + matrix refreshed'
Write-Output 'curate-session-memory OK'
exit 0
