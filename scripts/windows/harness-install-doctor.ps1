# Runs the canonical doctor through Git Bash with an explicit user profile.
# Wrapper conventions: scripts/windows/equivalence-sentinel.ps1.
[CmdletBinding()]
param(
    [string]$WorkspaceRoot = "",
    [string]$GitBashPath = ""
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

if ([string]::IsNullOrWhiteSpace($WorkspaceRoot)) {
    $WorkspaceRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
} else {
    $WorkspaceRoot = (Resolve-Path -LiteralPath $WorkspaceRoot).Path
}
if ([string]::IsNullOrWhiteSpace($env:USERPROFILE)) {
    throw 'USERPROFILE must identify the scheduled task user'
}
if ([string]::IsNullOrWhiteSpace($GitBashPath)) {
    $candidates = @(
        'C:\Program Files\Git\bin\bash.exe',
        'C:\Program Files\Git\usr\bin\bash.exe',
        "$env:LOCALAPPDATA\Programs\Git\bin\bash.exe"
    )
    $GitBashPath = $candidates | Where-Object {
        Test-Path -LiteralPath $_ -PathType Leaf
    } | Select-Object -First 1
}
if (-not $GitBashPath -or -not (Test-Path -LiteralPath $GitBashPath -PathType Leaf)) {
    throw 'Git Bash is required to run the harness install doctor'
}
$bootstrap = Join-Path $WorkspaceRoot 'scripts\windows\harness-install-doctor.sh'
if (-not (Test-Path -LiteralPath $bootstrap -PathType Leaf)) {
    throw 'The Windows doctor entry point is missing'
}
$logDir = Join-Path $WorkspaceRoot 'logs\maintenance'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$log = Join-Path $logDir ("harness-install-doctor-{0}.log" -f (Get-Date -Format 'yyyy-MM-dd'))
Set-Location -LiteralPath $WorkspaceRoot

# Native stderr must be logged, including on Windows PowerShell where redirecting
# stderr creates ErrorRecords. The native exit status remains authoritative.
$previousPreference = $ErrorActionPreference
$PSNativeCommandUseErrorActionPreference = $false
$LASTEXITCODE = $null
try {
    $ErrorActionPreference = 'Continue'
    $output = @(& $GitBashPath $bootstrap.Replace('\', '/') 2>&1)
    $exitCode = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $previousPreference
}
if ($null -eq $exitCode) { throw 'Git Bash did not return an exit status' }
[IO.File]::AppendAllText($log, ($output | Out-String), (New-Object Text.UTF8Encoding($false)))
$output | ForEach-Object { Write-Output $_ }
exit $exitCode
