param(
  [string]$ConfigPath = (Join-Path $PSScriptRoot 'job-queue.local.conf'),
  [switch]$Once
)
$ErrorActionPreference = 'Stop'

function Read-LocalConfig([string]$Path) {
  if (-not (Test-Path -LiteralPath $Path)) { throw "configuration file not found" }
  $cfg = @{}
  foreach ($line in @(Get-Content -LiteralPath $Path -ErrorAction Stop)) {
    $s = "$line".Trim()
    if ($s -eq '' -or $s.StartsWith('#')) { continue }
    if ($s -notmatch '^([A-Z0-9_]+)=(.*)$') { throw "bad configuration line" }
    $cfg[$Matches[1]] = $Matches[2].Trim()
  }
  foreach ($key in @('QUEUE_ROOT','CLONE_ROOT','WORKTREE_ROOT','DEFAULT_REPOSITORY','REPOSITORY_ALLOW_LIST')) {
    if (-not $cfg.ContainsKey($key) -or $cfg[$key] -match '^<.*>$|^\s*$') { throw "configuration value missing: $key" }
  }
  return $cfg
}

function Read-Limits([string]$Path, [int]$DiskFloorFromConfig) {
  $limits = @{ max_running = 2; max_starts_per_run = 1; min_free_gb = 60; per_repo_max = 0; min_disk_free_gb = $DiskFloorFromConfig }
  if (Test-Path -LiteralPath $Path) {
    foreach ($line in @(Get-Content -LiteralPath $Path -ErrorAction SilentlyContinue)) {
      if ("$line" -match '^\s*([a-z_]+)\s*=\s*(\d{1,4})\s*$') {
        $key = $Matches[1]
        $value = [int]$Matches[2]
        if ($key -eq 'max_running' -and $value -ge 1) { $limits[$key] = [math]::Min($value, 8) }
        if ($key -eq 'max_starts_per_run' -and $value -ge 1) { $limits[$key] = [math]::Min($value, 6) }
        if ($key -eq 'min_free_gb') { $limits[$key] = [math]::Max($value, 60) }
        if ($key -eq 'per_repo_max' -and $value -ge 1) { $limits[$key] = $value }
        if ($key -eq 'min_disk_free_gb') { $limits[$key] = [math]::Max($value, 50) }
      }
    }
  }
  if ($limits.min_disk_free_gb -lt 50) { $limits.min_disk_free_gb = 50 }
  return $limits
}

function Write-PumpLog([string]$QueueRoot, [string]$Message) {
  $stamp = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
  Add-Content -LiteralPath (Join-Path $QueueRoot 'pump.log') -Value ($stamp + ' ' + $Message) -Encoding ASCII
}

function Get-FreeDiskGb([string]$Root, [string]$Role) {
  if ($env:JOB_QUEUE_TEST_FREE_GB_JSON) {
    $probe = $env:JOB_QUEUE_TEST_FREE_GB_JSON | ConvertFrom-Json
    return [double]$probe.$Role
  }
  $full = [System.IO.Path]::GetFullPath($Root)
  $drive = New-Object System.IO.DriveInfo([System.IO.Path]::GetPathRoot($full))
  return [math]::Round($drive.AvailableFreeSpace / 1GB, 1)
}

function Get-SpecHead([string]$JobsRoot, [string]$Id, [string]$Key) {
  $file = Join-Path $JobsRoot ($Id + '.md')
  if (-not (Test-Path -LiteralPath $file)) { return '' }
  foreach ($line in @(Get-Content -LiteralPath $file -TotalCount 10 -ErrorAction SilentlyContinue)) {
    if ("$line" -cmatch ('^' + $Key + ':\s*(.*?)\s*$')) { return $Matches[1] }
  }
  return ''
}

function Get-JobRepo([hashtable]$Config, [string]$JobsRoot, [string]$Id) {
  $repo = Get-SpecHead $JobsRoot $Id 'REPO'
  if ($repo -eq '') { $repo = $Config.DEFAULT_REPOSITORY }
  $allow = @($Config.REPOSITORY_ALLOW_LIST -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' })
  if ($repo -notmatch '^[A-Za-z0-9._-]+$' -or $allow -notcontains $repo) { return 'invalid' }
  return $repo
}

function Get-RunningState([string]$LocksRoot) {
  $ids = @()
  $slots = 0
  if (Test-Path -LiteralPath $LocksRoot) {
    foreach ($dir in @(Get-ChildItem -LiteralPath $LocksRoot -Directory -Filter 'slot*' -ErrorAction SilentlyContinue)) {
      $slots += 1
      $owner = Join-Path $dir.FullName 'owner'
      if (Test-Path -LiteralPath $owner) {
        $line = '' + (Get-Content -LiteralPath $owner -TotalCount 1 -ErrorAction SilentlyContinue)
        $id = @($line.Trim() -split '\s+')[0]
        if ($id -match '^[a-z0-9-]+$') { $ids += $id }
      }
    }
  }
  return @{ Slots = $slots; Ids = $ids }
}

$config = Read-LocalConfig $ConfigPath
$queueRoot = $config.QUEUE_ROOT
$queueFile = Join-Path $queueRoot 'queue.txt'
$logs = Join-Path $queueRoot 'logs'
$jobs = Join-Path $queueRoot 'jobs'
$locks = Join-Path $queueRoot 'locks'
$pauseFile = Join-Path $queueRoot 'PAUSE'
$limits = Read-Limits (Join-Path $queueRoot 'limits.txt') ([int]($config.MIN_DISK_FREE_GB))

New-Item -ItemType Directory -Force -Path $logs,$locks | Out-Null

$cloneFree = Get-FreeDiskGb $config.CLONE_ROOT 'clone'
$worktreeFree = Get-FreeDiskGb $config.WORKTREE_ROOT 'worktree'
$running = Get-RunningState $locks
$gateText = 'clone_free_gb=' + $cloneFree + ' worktree_free_gb=' + $worktreeFree + ' running=' + ([math]::Max([int]$running.Slots, @($running.Ids).Count)) + ' min_disk_free_gb=' + $limits.min_disk_free_gb

if (Test-Path -LiteralPath $pauseFile) {
  Write-PumpLog $queueRoot ($gateText + ' action=hold reason=PAUSE-file')
  exit 0
}
if ($cloneFree -lt $limits.min_disk_free_gb) {
  Write-PumpLog $queueRoot ($gateText + ' action=hold reason=clone-disk-under-' + $limits.min_disk_free_gb + 'GB')
  exit 0
}
if ($worktreeFree -lt $limits.min_disk_free_gb) {
  Write-PumpLog $queueRoot ($gateText + ' action=hold reason=worktree-disk-under-' + $limits.min_disk_free_gb + 'GB')
  exit 0
}
if (-not (Test-Path -LiteralPath $queueFile)) {
  Write-PumpLog $queueRoot ($gateText + ' action=idle reason=no-queue-file')
  exit 0
}

$entries = @()
foreach ($line in @(Get-Content -LiteralPath $queueFile)) {
  $s = "$line".Trim()
  if ($s -eq '' -or $s.StartsWith('#')) { continue }
  $parts = @($s -split '\s+')
  if ($parts.Count -lt 2) { continue }
  if ($parts[0] -match '^[a-z0-9-]+$' -and $parts[1] -match '^[0-9]+$') { $entries += ,@($parts[0], $parts[1]) }
}

$pick = $null
foreach ($entry in $entries) {
  $id = $entry[0]
  if (Test-Path -LiteralPath (Join-Path $logs ($id + '.result'))) { continue }
  if (-not (Test-Path -LiteralPath (Join-Path $jobs ($id + '.md')))) { continue }
  if ((Get-JobRepo $config $jobs $id) -eq 'invalid') { continue }
  $pick = $entry
  break
}

if ($null -eq $pick) {
  Write-PumpLog $queueRoot ($gateText + ' action=idle reason=queue-empty-or-all-started')
  exit 0
}

$launcher = Join-Path $PSScriptRoot 'launch.ps1'
if ($env:JOB_QUEUE_TEST_LAUNCHER) { $launcher = $env:JOB_QUEUE_TEST_LAUNCHER }
$out = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $launcher -ConfigPath $ConfigPath -Script run-job.sh -A1 $pick[0] -A2 $pick[1] 2>&1
$rc = $LASTEXITCODE
$outText = (@($out) | ForEach-Object { "$_" }) -join ' / '
Write-PumpLog $queueRoot ($gateText + ' action=started job=' + $pick[0] + ' issue=' + $pick[1] + ' launch_rc=' + $rc + ' launch_out=[' + $outText + ']')
