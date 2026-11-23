# collect-machine-baseline.ps1
# Collects a redacted machine baseline for multi-machine workspace readiness.
# No secrets are intentionally collected; command output is redacted for common credential keys.

param(
    [string]$OutputDir = ""
)

$ErrorActionPreference = "Continue"

function Get-DefaultOutputDir {
    if ($OutputDir) { return $OutputDir }
    $pwdDocs = Join-Path (Get-Location).Path "docs"
    if (Test-Path $pwdDocs) { return (Join-Path (Get-Location).Path "docs\reports\machine-baseline") }
    if (Test-Path "D:\workspace-hub\docs") { return "D:\workspace-hub\docs\reports\machine-baseline" }
    $userRepoDocs = Join-Path $env:USERPROFILE "workspace-hub\docs"
    if (Test-Path $userRepoDocs) { return (Join-Path $env:USERPROFILE "workspace-hub\docs\reports\machine-baseline") }
    return ([Environment]::GetFolderPath("Desktop"))
}

function Redact-Text([string]$Text) {
    if ($null -eq $Text) { return "" }
    $redacted = $Text -replace '(?i)(token|password|secret|apikey|api_key|authorization|credential)(\s*[:=]\s*)\S+', '$1$2[REDACTED]'
    $redacted = $redacted -replace 'gh[opsu]_[A-Za-z0-9_]{20,}', '[REDACTED_GITHUB_TOKEN]'
    $redacted = $redacted -replace 'sk-[A-Za-z0-9_-]{20,}', '[REDACTED_API_KEY]'
    return $redacted
}

function Add-Section([string]$Name) {
    Add-Content -Path $script:TxtPath -Value ""
    Add-Content -Path $script:TxtPath -Value "===== $Name ====="
}

function Invoke-LoggedCommand([string]$Label, [string]$Command) {
    Add-Section $Label
    Add-Content -Path $script:TxtPath -Value ("$ " + $Command)
    try {
        $out = cmd.exe /c $Command 2>&1 | Out-String
        Add-Content -Path $script:TxtPath -Value (Redact-Text $out)
    } catch {
        Add-Content -Path $script:TxtPath -Value ("ERROR: " + $_.Exception.Message)
    }
}

$OutBase = Get-DefaultOutputDir
New-Item -ItemType Directory -Force -Path $OutBase | Out-Null
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$HostName = $env:COMPUTERNAME
$script:TxtPath = Join-Path $OutBase "machine-baseline-$HostName-$Stamp.txt"
$JsonPath = Join-Path $OutBase "machine-baseline-$HostName-$Stamp.json"

Set-Content -Path $script:TxtPath -Value ("Machine baseline report - " + (Get-Date -Format o))

Add-Section "Identity"
Add-Content $script:TxtPath "ComputerName=$env:COMPUTERNAME"
Add-Content $script:TxtPath "User=$env:USERNAME"
Add-Content $script:TxtPath "Domain=$env:USERDOMAIN"
Add-Content $script:TxtPath ("PWD=" + (Get-Location).Path)

Add-Section "OS and hardware"
$cs = Get-CimInstance Win32_ComputerSystem
$os = Get-CimInstance Win32_OperatingSystem
$bios = Get-CimInstance Win32_BIOS
Add-Content $script:TxtPath ($cs | Format-List Manufacturer,Model,TotalPhysicalMemory | Out-String)
Add-Content $script:TxtPath ($os | Format-List Caption,Version,BuildNumber,OSArchitecture,LastBootUpTime | Out-String)
Add-Content $script:TxtPath ($bios | Format-List SerialNumber,SMBIOSBIOSVersion | Out-String)

Add-Section "CPU"
Get-CimInstance Win32_Processor |
    Select-Object Name,NumberOfCores,NumberOfLogicalProcessors,MaxClockSpeed |
    Format-Table -AutoSize | Out-String | Add-Content $script:TxtPath

Add-Section "GPU"
Get-CimInstance Win32_VideoController |
    Select-Object Name,AdapterRAM,DriverVersion |
    Format-Table -AutoSize | Out-String | Add-Content $script:TxtPath
Invoke-LoggedCommand "nvidia-smi" "nvidia-smi"

Add-Section "Drives"
Get-Volume |
    Sort-Object DriveLetter |
    Select-Object DriveLetter,FileSystemLabel,FileSystem,DriveType,HealthStatus,SizeRemaining,Size |
    Format-Table -AutoSize | Out-String | Add-Content $script:TxtPath

Add-Section "Network"
Get-NetIPAddress -AddressFamily IPv4 |
    Where-Object { $_.IPAddress -notlike '169.254*' } |
    Select-Object InterfaceAlias,IPAddress,PrefixLength |
    Format-Table -AutoSize | Out-String | Add-Content $script:TxtPath

Add-Section "Important paths"
$importantPaths = @(
    "D:\workspace-hub",
    "C:\workspace-hub",
    (Join-Path $env:USERPROFILE "workspace-hub"),
    "D:\",
    "E:\",
    "F:\",
    "G:\"
)
foreach ($p in $importantPaths) {
    $prefix = if (Test-Path $p) { "[OK]" } else { "[MISSING]" }
    Add-Content $script:TxtPath "$prefix $p"
}

Add-Section "Tool paths"
$tools = @('git','gh','python','py','uv','claude','codex','hermes','OrcaFlex','OrcaWave','aqwa','ansys','matlab')
$toolMap = @{}
foreach ($c in $tools) {
    $cmd = Get-Command $c -ErrorAction SilentlyContinue
    $source = if ($cmd) { $cmd.Source } else { "not-found" }
    $toolMap[$c] = $source
    Add-Content $script:TxtPath "$c=$source"
}

Invoke-LoggedCommand "git version" "git --version"
Invoke-LoggedCommand "gh auth status redacted" "gh auth status"
Invoke-LoggedCommand "python version" "python --version"
Invoke-LoggedCommand "uv version" "uv --version"

Add-Section "Repo status candidates"
$repoCandidates = @(
    "D:\workspace-hub",
    "C:\workspace-hub",
    (Join-Path $env:USERPROFILE "workspace-hub")
)
foreach ($r in $repoCandidates) {
    if (Test-Path (Join-Path $r ".git")) {
        Add-Content $script:TxtPath "--- repo $r"
        Push-Location $r
        Invoke-LoggedCommand "repo branch $r" "git branch --show-current"
        Invoke-LoggedCommand "repo head $r" "git rev-parse --short HEAD"
        Invoke-LoggedCommand "repo status no-untracked $r" "git status --porcelain=v1 --untracked-files=no"
        Pop-Location
    }
}

$obj = [ordered]@{
    generated_at = (Get-Date -Format o)
    computer = $env:COMPUTERNAME
    user = $env:USERNAME
    pwd = (Get-Location).Path
    txt_report = $script:TxtPath
    os = (Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,BuildNumber,OSArchitecture)
    computer_system = (Get-CimInstance Win32_ComputerSystem | Select-Object Manufacturer,Model,TotalPhysicalMemory)
    volumes = (Get-Volume | Select-Object DriveLetter,FileSystemLabel,FileSystem,DriveType,HealthStatus,SizeRemaining,Size)
    gpu = (Get-CimInstance Win32_VideoController | Select-Object Name,AdapterRAM,DriverVersion)
    tools = $toolMap
    repo_candidates = $repoCandidates
}
$obj | ConvertTo-Json -Depth 6 | Set-Content -Path $JsonPath

Write-Host "Collection complete."
Write-Host "TXT=$script:TxtPath"
Write-Host "JSON=$JsonPath"
