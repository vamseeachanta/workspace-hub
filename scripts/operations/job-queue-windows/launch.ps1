param(
  [string]$ConfigPath = (Join-Path $PSScriptRoot 'job-queue.local.conf'),
  [Parameter(Mandatory=$true)][string]$Script,
  [Parameter(Mandatory=$true)][string]$A1,
  [string]$A2 = 'none'
)
$ErrorActionPreference = 'Stop'

function Read-LocalConfig([string]$Path) {
  $cfg = @{}
  foreach ($line in @(Get-Content -LiteralPath $Path -ErrorAction Stop)) {
    $s = "$line".Trim()
    if ($s -eq '' -or $s.StartsWith('#')) { continue }
    if ($s -notmatch '^([A-Z0-9_]+)=(.*)$') { throw "bad configuration line" }
    $cfg[$Matches[1]] = $Matches[2].Trim()
  }
  return $cfg
}

if ($Script -notmatch '^[A-Za-z0-9._-]+\.sh$') { Write-Output 'bad script name'; exit 1 }
if ($A1 -notmatch '^[a-z0-9-]+$' -or $A2 -notmatch '^[a-z0-9-]+$') { Write-Output 'bad argument'; exit 1 }

$cfg = Read-LocalConfig $ConfigPath
$bash = $env:JOB_QUEUE_BASH
if (-not $bash) { $bash = 'bash' }
$scriptPath = Join-Path $PSScriptRoot $Script
$out = Join-Path (Join-Path $cfg.QUEUE_ROOT 'logs') ($A1 + '.launch.out')
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $bash
$psi.Arguments = '-lc "' + ($scriptPath -replace '\\','/') + ' start ' + $A1 + ' ' + $A2 + ' > ' + ($out -replace '\\','/') + ' 2>&1 < /dev/null"'
$psi.WorkingDirectory = $PSScriptRoot
$psi.UseShellExecute = $false
$psi.CreateNoWindow = $true
$process = [System.Diagnostics.Process]::Start($psi)
Write-Output ("launched " + $A1 + " pid=" + $process.Id)
