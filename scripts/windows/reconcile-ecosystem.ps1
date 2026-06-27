<#
.SYNOPSIS
  Windows-native driver for scripts/readiness/reconcile-ecosystem.sh (#2801 / equality matrix).

.DESCRIPTION
  Windows counterpart to the bash reconcile driver. On Windows hosts the Claude/agent Bash tool
  and a bare `bash` launch can hang (ace-win-2: WSL stub shadows Git Bash; UNC/PATH stalls), so
  this resolves the REAL Git Bash (MSYS/MINGW) explicitly — never the WSL stub — and runs the
  canonical .sh through it. The .sh stays the single source of truth for the classify/apply logic;
  this is only the OS-appropriate launcher (mirrors the sync-ecosystem.sh/.ps1 pairing).

  All flags pass straight through to the .sh:
    (none)                read-only classified plan (AUTO-SAFE / NEEDS-APPROVAL / OPERATOR-ONLY)
    -- --apply            run the AUTO-SAFE subset (ff-pulls, guard-gated deletes, prunes)
    -- --apply --stash-dirty   also stash (recoverable) dirty trees
    -- --apply --equality      after hygiene, re-collect + rebuild the matrix
    -- --json             machine-readable plan

  NOTE the `--` separator: PowerShell needs it before the bash-style `--flags` so they reach the
  script verbatim instead of being parsed as PowerShell parameters.

  Output is shown live AND tee'd to logs/quality/reconcile-<machine>-<date>.log.

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\reconcile-ecosystem.ps1
.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\reconcile-ecosystem.ps1 -- --apply
.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\reconcile-ecosystem.ps1 -- --apply --equality
#>
[CmdletBinding()]
param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Flags)

$ErrorActionPreference = 'Continue'

# --- repo root: this script lives in <hub>/scripts/windows ---
$hub = (Get-Item $PSScriptRoot).Parent.Parent.FullName

# --- resolve the REAL Git Bash (MSYS/MINGW), never the WSL stub (same contract as collect-equality.ps1) ---
function Resolve-GitBash {
    $cands = New-Object System.Collections.Generic.List[string]
    $gitCmd = (Get-Command git -ErrorAction SilentlyContinue).Source
    if ($gitCmd) {
        $root = Split-Path -Parent (Split-Path -Parent $gitCmd)
        $cands.Add((Join-Path $root 'bin\bash.exe'))
        $cands.Add((Join-Path $root 'usr\bin\bash.exe'))
    }
    $cands.Add('C:\Program Files\Git\bin\bash.exe')
    $cands.Add('C:\Program Files\Git\usr\bin\bash.exe')
    $cands.Add('C:\Program Files (x86)\Git\bin\bash.exe')
    $cands.Add("$env:LOCALAPPDATA\Programs\Git\bin\bash.exe")
    foreach ($c in ($cands | Select-Object -Unique)) {
        if ($c -and (Test-Path $c)) {
            $u = (& $c -c 'uname -s' 2>$null)
            if ($u -match '^(MINGW|MSYS|CYGWIN)') { return $c }
        }
    }
    return $null
}

$bash = Resolve-GitBash
if (-not $bash) {
    Write-Error "Could not find a Git Bash (MSYS/MINGW) bash.exe. Bare 'bash' here is the WSL stub and will hang. Install Git for Windows."
    exit 1
}

# --- POSIX form of the hub path for Git Bash (C:\ws\workspace-hub -> /c/ws/workspace-hub) ---
$posixHub = '/' + $hub.Substring(0, 1).ToLowerInvariant() + ($hub.Substring(2) -replace '\\', '/')

# --- machine label (for the log name) + log path ---
$machine = if ($env:COMPUTERNAME) { $env:COMPUTERNAME.ToLowerInvariant() } else { 'windows' }
$logDir = Join-Path $hub 'logs\quality'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$log = Join-Path $logDir ("reconcile-{0}-{1}.log" -f $machine, (Get-Date -Format 'yyyy-MM-dd'))

$flagStr = ($Flags -join ' ').Trim()
$inner = "cd '$posixHub' && bash scripts/readiness/reconcile-ecosystem.sh $flagStr"

"=== reconcile-ecosystem (windows) @ $(Get-Date -Format o) | host=$env:COMPUTERNAME | flags='$flagStr' ===" |
    Tee-Object -FilePath $log
"using Git Bash: $bash" | Tee-Object -FilePath $log -Append
"command: $inner"       | Tee-Object -FilePath $log -Append
"" | Tee-Object -FilePath $log -Append

& $bash -lc $inner 2>&1 | Tee-Object -FilePath $log -Append
$rc = $LASTEXITCODE

"" | Tee-Object -FilePath $log -Append
"=== exit=$rc | log: $log ===" | Tee-Object -FilePath $log -Append
exit $rc
