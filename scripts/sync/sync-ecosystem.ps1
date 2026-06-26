<#
.SYNOPSIS
  Sync every git repo in the ecosystem (Windows-native PowerShell driver).

.DESCRIPTION
  Windows counterpart to scripts/sync/sync-ecosystem.sh. Use this on Windows hosts where
  launching Git Bash can hang (e.g. ace-win-2: a stale entry in the inherited Windows PATH
  / UNC cwd stalls bash startup). PowerShell + the git CLI runs reliably there.

  Like the bash driver, it does NOT assume the repository_sync nested layout
  (workspace-hub/<repo>). It resolves the ecosystem root by detection so it works whether
  the repos are siblings of workspace-hub (this host) or nested inside it.

  Root resolution order: -Root  >  $env:WS_ECOSYSTEM_ROOT  >  auto-detect (sibling vs nested).

.PARAMETER Mode
  full   (default): per repo  git add -u -> commit if staged -> fetch --prune -> pull --ff-only -> push
  pull            : per repo  fetch --prune -> pull --ff-only            (no commit, no push)
  status          : per repo  fetch --prune -> report branch/ahead/behind/dirty (read-only)

.PARAMETER Root
  Ecosystem root directory holding the repo clones. Overrides detection.

.PARAMETER Message
  Commit message for 'full' mode. Defaults to "chore(sync): auto-sync <yyyy-MM-dd>".

.PARAMETER DryRun
  Report intended action per repo without mutating anything.

.EXAMPLE
  pwsh -File scripts/sync/sync-ecosystem.ps1

.EXAMPLE
  pwsh -File scripts/sync/sync-ecosystem.ps1 -Mode status
#>
[CmdletBinding()]
param(
  [ValidateSet('full','pull','status')] [string]$Mode = 'full',
  [string]$Root,
  [string]$Message,
  [switch]$DryRun
)

$ErrorActionPreference = 'Continue'

function Get-GitChildCount([string]$Base) {
  if (-not (Test-Path $Base)) { return 0 }
  (Get-ChildItem $Base -Directory -ErrorAction SilentlyContinue |
    Where-Object { Test-Path (Join-Path $_.FullName '.git') }).Count
}

function Resolve-EcosystemRoot {
  if ($Root) { return (Resolve-Path $Root).Path }
  if ($env:WS_ECOSYSTEM_ROOT) { return (Resolve-Path $env:WS_ECOSYSTEM_ROOT).Path }
  # This script lives in <hub>/scripts/sync ; hub parent holds siblings.
  $hub    = (Get-Item $PSScriptRoot).Parent.Parent.FullName
  $parent = (Get-Item $hub).Parent.FullName
  $sib = Get-GitChildCount $parent   # sibling layout: hub + siblings under parent
  $nes = Get-GitChildCount $hub      # nested layout: repos inside hub
  if ($sib -ge 2) { return $parent }
  elseif ($nes -ge 1) { return $hub }
  else { return $parent }
}

if (-not $Message) { $Message = "chore(sync): auto-sync $(Get-Date -Format yyyy-MM-dd)" }
$resolved = Resolve-EcosystemRoot
if (-not (Test-Path $resolved)) { Write-Error "Ecosystem root not found: $resolved"; exit 1 }

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "sync-ecosystem | os=Windows | mode=$Mode | root=$resolved" -ForegroundColor Cyan
if ($DryRun) { Write-Host "(dry-run: no mutations)" -ForegroundColor Yellow }
Write-Host "====================================================" -ForegroundColor Cyan

$nOk = 0; $nWarn = 0; $nFail = 0

Get-ChildItem $resolved -Directory | Where-Object { Test-Path (Join-Path $_.FullName '.git') } | ForEach-Object {
  $d = $_.FullName
  Write-Host "=== $($_.Name) ===" -ForegroundColor Blue
  $branch = (git -C $d rev-parse --abbrev-ref HEAD 2>$null)
  if (-not $branch) { $branch = '?' }

  if ($Mode -eq 'status') {
    git -C $d fetch --prune origin 2>$null | Out-Null
    $dirty = if (git -C $d status --porcelain) { 'dirty' } else { 'clean' }
    $ahead = (git -C $d rev-list --count '@{u}..HEAD' 2>$null);  if (-not $ahead)  { $ahead = '?' }
    $behind = (git -C $d rev-list --count 'HEAD..@{u}' 2>$null); if (-not $behind) { $behind = '?' }
    Write-Host "  $branch  ahead=$ahead behind=$behind  $dirty"
    $script:nOk++
    return
  }

  if ($DryRun) {
    Write-Host "  [dry-run] would: $Mode on branch $branch"
    $script:nOk++
    return
  }

  $result = 'ok'
  if ($Mode -eq 'full') {
    git -C $d add -u
    git -C $d diff --cached --quiet
    if ($LASTEXITCODE -ne 0) {
      git -C $d commit -m $Message | Out-Null
      if ($LASTEXITCODE -ne 0) { $result = 'commit-failed' }
    }
  }

  git -C $d fetch --prune origin 2>$null | Out-Null
  git -C $d pull --ff-only 2>$null
  if ($LASTEXITCODE -ne 0) { Write-Host "  pull skipped (diverged/no-ff)"; if ($result -eq 'ok') { $result = 'warn-pull' } }

  if ($Mode -eq 'full') {
    git -C $d push 2>$null
    if ($LASTEXITCODE -ne 0) { Write-Host "  push skipped/failed"; $result = 'push-failed' }
  }

  switch -Wildcard ($result) {
    'ok'      { $script:nOk++ }
    'warn-*'  { $script:nWarn++ }
    default   { $script:nFail++ }
  }
}

Write-Host "----------------------------------------------------"
Write-Host "Done. ok=$nOk warn=$nWarn fail=$nFail"
if ($nFail -ne 0) { exit 1 } else { exit 0 }
