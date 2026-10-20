param(
  [string]$ConfigPath = (Join-Path $PSScriptRoot 'job-queue.local.conf'),
  [switch]$DryRun,
  [scriptblock]$FreeSpaceProbe,
  [string]$Launcher
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

function Read-DiskFloor([string]$Value) {
  $floor = 0
  if ($Value -notmatch '^[0-9]+$' -or -not [int]::TryParse($Value, [ref]$floor)) {
    throw 'invalid disk floor'
  }
  return [math]::Max($floor, 50)
}

function Read-Limits([string]$Path, [int]$DiskFloorFromConfig) {
  $limits = @{ max_running = 2; max_starts_per_run = 1; per_repo_max = 0; min_disk_free_gb = $DiskFloorFromConfig }
  if (Test-Path -LiteralPath $Path) {
    foreach ($line in @(Get-Content -LiteralPath $Path -ErrorAction SilentlyContinue)) {
      if ("$line" -match '^\s*min_disk_free_gb\s*=\s*(.*?)\s*$') {
        $limits.min_disk_free_gb = [math]::Max($limits.min_disk_free_gb, (Read-DiskFloor $Matches[1]))
        continue
      }
      if ("$line" -match '^\s*([a-z_]+)\s*=\s*(\d{1,4})\s*$') {
        $key = $Matches[1]
        $value = [int]$Matches[2]
        if ($key -eq 'max_running' -and $value -ge 1) { $limits[$key] = [math]::Min($value, 8) }
        if ($key -eq 'max_starts_per_run' -and $value -ge 1) { $limits[$key] = [math]::Min($value, 6) }
        if ($key -eq 'per_repo_max' -and $value -ge 1) { $limits[$key] = $value }
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
  if ($FreeSpaceProbe) { return & $FreeSpaceProbe $Root $Role }
  $full = [System.IO.Path]::GetFullPath($Root)
  $drive = New-Object System.IO.DriveInfo([System.IO.Path]::GetPathRoot($full))
  # Issue 4081 disk criterion: compare before rounding (49.96 is below 50).
  return $drive.AvailableFreeSpace / 1GB
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
  if ($repo -notmatch '^[A-Za-z0-9][A-Za-z0-9._-]*$' -or $allow -notcontains $repo) { return 'invalid' }
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

function Quote-Bash([string]$Value) {
  $quote = [string][char]39
  $double = [string][char]34
  return $quote + $Value.Replace($quote, ($quote + $double + $quote + $double + $quote)) + $quote
}

function Read-CleanupCapture([string]$Path) {
  $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open,
    [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
  try {
    $reader = New-Object System.IO.StreamReader($stream)
    try { return $reader.ReadToEnd() } finally { $reader.Dispose() }
  } finally { $stream.Dispose() }
}

function Invoke-RecentCleanup([string]$Path) {
  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = 'bash'
  if ($config.BASH_EXECUTABLE) { $psi.FileName = $config.BASH_EXECUTABLE }
  $runner = (Join-Path $PSScriptRoot 'run-job.sh') -replace '\\','/'
  $fullConfig = ([System.IO.Path]::GetFullPath($Path)) -replace '\\','/'
  $capture = [System.IO.Path]::GetFullPath((Join-Path $queueRoot 'logs/recent-cleanup.out'))
  $command = (Quote-Bash $runner) + ' cleanup-recent all none ' + (Quote-Bash $fullConfig)
  if ($DryRun) { $command += ' --dry-run' }
  $command += ' > ' + (Quote-Bash ($capture -replace '\\','/')) + ' 2>&1'
  $psi.Arguments = '-lc "' + $command.Replace('"', '\"') + '"'
  $psi.UseShellExecute = $false
  $psi.CreateNoWindow = $true
  $psi.EnvironmentVariables['GIT_TERMINAL_PROMPT'] = '0'
  $psi.EnvironmentVariables['GCM_INTERACTIVE'] = 'never'
  # Capture through the shell, so inherited pipe handles cannot extend the wait.
  $process = [System.Diagnostics.Process]::Start($psi)
  try {
    $action = 'cleanup-pass'
    $rc = 'timeout'
    if (-not $process.WaitForExit(600000)) {
      & taskkill.exe /T /F /PID $process.Id | Out-Null
      $action = 'cleanup-pass-timeout worktrees=inspect-log'
    } else {
      $rc = $process.ExitCode
    }
    try {
      $text = (Read-CleanupCapture $capture) -replace '[\r\n]+',' / '
    } catch {
      $text = 'capture-read-failed; inspect capture file'
    }
    Write-PumpLog $queueRoot ('action=' + $action + ' rc=' + $rc + ' output=[' + $text + ']')
  } finally {
    $process.Dispose()
  }
}

$config = Read-LocalConfig $ConfigPath
$queueRoot = $config.QUEUE_ROOT
$queueFile = Join-Path $queueRoot 'queue.txt'
$logs = Join-Path $queueRoot 'logs'
$jobs = Join-Path $queueRoot 'jobs'
$locks = Join-Path $queueRoot 'locks'
$pauseFile = Join-Path $queueRoot 'PAUSE'

New-Item -ItemType Directory -Force -Path $logs,$locks | Out-Null
try {
  $floor = 50
  if ($config.ContainsKey('MIN_DISK_FREE_GB')) { $floor = Read-DiskFloor $config.MIN_DISK_FREE_GB }
  $limits = Read-Limits (Join-Path $queueRoot 'limits.txt') $floor
} catch {
  Write-PumpLog $queueRoot 'action=hold reason=invalid-disk-floor'
  exit 0
}

# A paused integration stays paused; invalid disk floors hold cleanup as well.
# Otherwise reclamation precedes disk holds and queue selection, so low space
# or an empty queue cannot starve later passes.
if (-not (Test-Path -LiteralPath $pauseFile) -and
    (Test-Path -LiteralPath (Join-Path $logs 'recent-cleanup'))) {
  try { Invoke-RecentCleanup $ConfigPath } catch {
    Write-PumpLog $queueRoot 'action=cleanup-pass-failed worktrees=inspect-log'
  }
}

try {
  $cloneFree = Get-FreeDiskGb $config.CLONE_ROOT 'clone'
  $worktreeFree = Get-FreeDiskGb $config.WORKTREE_ROOT 'worktree'
  if ($null -eq $cloneFree -or $null -eq $worktreeFree -or
      [double]::IsNaN([double]$cloneFree) -or [double]::IsNaN([double]$worktreeFree) -or
      [double]::IsInfinity([double]$cloneFree) -or [double]::IsInfinity([double]$worktreeFree)) { throw 'invalid disk probe' }
} catch {
  Write-PumpLog $queueRoot 'action=hold reason=disk-probe-failed'
  exit 0
}
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

if ([math]::Max([int]$running.Slots, @($running.Ids).Count) -ge $limits.max_running) {
  Write-PumpLog $queueRoot ($gateText + ' action=hold reason=max-running')
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
  if ($running.Ids -contains $id) { continue }
  if (Test-Path -LiteralPath (Join-Path $logs ($id + '.result'))) { continue }
  if (-not (Test-Path -LiteralPath (Join-Path $jobs ($id + '.md')))) { continue }
  $repo = Get-JobRepo $config $jobs $id
  if ($repo -eq 'invalid') { continue }
  $repoRunning = @($running.Ids | Where-Object { (Get-JobRepo $config $jobs $_) -eq $repo }).Count
  if ($limits.per_repo_max -gt 0 -and $repoRunning -ge $limits.per_repo_max) { continue }
  $pick = $entry
  break
}

if ($null -eq $pick) {
  Write-PumpLog $queueRoot ($gateText + ' action=idle reason=queue-empty-or-all-started')
  exit 0
}

if ($DryRun) {
  Write-PumpLog $queueRoot ($gateText + ' action=would-start job=' + $pick[0] + ' issue=' + $pick[1])
  exit 0
}

# A single pass starts at most one job; live slot acquisition remains required.
if (-not $Launcher) { $Launcher = Join-Path $PSScriptRoot 'launch.ps1' }
$out = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $Launcher -ConfigPath $ConfigPath -Script run-job.sh -A1 $pick[0] -A2 $pick[1] 2>&1
$rc = $LASTEXITCODE
$outText = (@($out) | ForEach-Object { "$_" }) -join ' / '
Write-PumpLog $queueRoot ($gateText + ' action=started job=' + $pick[0] + ' issue=' + $pick[1] + ' launch_rc=' + $rc + ' launch_out=[' + $outText + ']')
