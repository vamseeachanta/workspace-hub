# Runs the canonical Bash equivalence sentinel from Windows Task Scheduler.
[CmdletBinding()]
param(
    [string]$WorkspaceRoot = "",
    [string]$GitBashPath = ""
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

if ([string]::IsNullOrWhiteSpace($WorkspaceRoot)) {
    $WorkspaceRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
} else {
    $WorkspaceRoot = (Resolve-Path $WorkspaceRoot).Path
}

if ([string]::IsNullOrWhiteSpace($GitBashPath)) {
    $candidates = @(
        'C:\Program Files\Git\bin\bash.exe',
        'C:\Program Files\Git\usr\bin\bash.exe',
        "$env:LOCALAPPDATA\Programs\Git\bin\bash.exe"
    )
    $GitBashPath = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
}
if (-not $GitBashPath -or -not (Test-Path -LiteralPath $GitBashPath -PathType Leaf)) {
    throw "Git Bash is required to run the equivalence sentinel"
}

$sentinel = Join-Path $WorkspaceRoot 'scripts\monitoring\equivalence-sentinel.sh'
if (-not (Test-Path -LiteralPath $sentinel -PathType Leaf)) {
    throw "Sentinel script not found: $sentinel"
}
$logDir = Join-Path $WorkspaceRoot 'logs\monitoring'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$log = Join-Path $logDir ("equivalence-sentinel-{0}.log" -f (Get-Date -Format 'yyyy-MM-dd'))

function ConvertTo-GitBashPath {
    param([Parameter(Mandatory=$true)][string]$WindowsPath)
    $normalized = $WindowsPath.Replace('\', '/')
    if ($normalized -notmatch '^([A-Za-z]):/(.*)$') {
        throw "Expected a drive-qualified Windows path: $WindowsPath"
    }
    return "/{0}/{1}" -f $Matches[1].ToLowerInvariant(), $Matches[2]
}

$bashWorkspace = ConvertTo-GitBashPath -WindowsPath $WorkspaceRoot
$bashSentinel = ConvertTo-GitBashPath -WindowsPath $sentinel
$env:WORKSPACE_HUB = $bashWorkspace
Set-Location -LiteralPath $WorkspaceRoot
$output = @(& $GitBashPath $bashSentinel 2>&1)
$exitCode = $LASTEXITCODE
$text = $output | Out-String
[IO.File]::AppendAllText($log, $text, (New-Object Text.UTF8Encoding($false)))
$output | ForEach-Object { Write-Output $_ }
exit $exitCode
