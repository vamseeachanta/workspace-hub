# ABOUTME: System update script (Windows). Updates OS via Windows Update, common tools via winget, and custom software. Logs all changes to JSON.

param(
    [string]$ConfigFile = "",
    [string]$OutputFile = "",
    [switch]$SkipOS,
    [switch]$SkipTools,
    [switch]$SkipCustom,
    [switch]$Reboot,
    [switch]$Quiet,
    [switch]$Help
)

$SCRIPT_VERSION = "1.0.0"
$SCHEMA_VERSION = "1.0"

# ── Logging ──────────────────────────────────────────────────────────────

function Write-Log {
    param(
        [ValidateSet("Info", "Warn", "Error", "Success")]
        [string]$Level = "Info",
        [string]$Message
    )

    if ($Quiet -and $Level -notin @("Error", "Success")) { return }

    $color = switch ($Level) {
        "Info"    { "Cyan" }
        "Warn"    { "Yellow" }
        "Error"   { "Red" }
        "Success" { "Green" }
    }

    $prefix = "[$($Level.ToUpper())]"
    Write-Host "$prefix $Message" -ForegroundColor $color
}

# ── Help ─────────────────────────────────────────────────────────────────

if ($Help) {
    $helpText = @"
Usage: system-update.ps1 [OPTIONS]

Update OS packages, common tools, and custom software on Windows.
Logs all changes to a structured JSON file for unified reporting.

Options:
  -ConfigFile <path>   Path to custom packages config (JSON)
  -OutputFile <path>   Override output file path
  -SkipOS              Skip Windows Update
  -SkipTools           Skip winget/choco/pip/npm/uv updates
  -SkipCustom          Skip custom software from config file
  -Reboot              Schedule restart after updates if required
  -Quiet               Suppress info/warn messages (errors still shown)
  -Help                Show this help message

Output:
  By default writes to ./system-update-<HOSTNAME>-<YYYYMMDD>.json

Examples:
  .\system-update.ps1
  .\system-update.ps1 -SkipOS -SkipCustom
  .\system-update.ps1 -ConfigFile .\my-packages.json -Reboot
  .\system-update.ps1 -Quiet -OutputFile C:\logs\update.json
"@
    Write-Host $helpText
    exit 0
}

# ── Utility Functions ────────────────────────────────────────────────────

function Test-IsAdministrator {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Get-CommandVersion {
    param([string]$Command, [string]$VersionArg = "--version")

    try {
        $output = & $Command $VersionArg 2>&1
        if ($LASTEXITCODE -eq 0 -or $output) {
            $versionStr = ($output | Out-String).Trim()
            if ($versionStr.Length -gt 200) {
                $versionStr = $versionStr.Substring(0, 200)
            }
            return $versionStr
        }
    } catch {}
    return $null
}

function Test-CommandExists {
    param([string]$Command)

    try {
        $cmd = Get-Command $Command -ErrorAction SilentlyContinue
        return ($null -ne $cmd)
    } catch {
        return $false
    }
}

function Get-IsoTimestamp {
    return (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
}

function Test-RebootRequired {
    # Method 1: PSWindowsUpdate module
    if (Get-Module -ListAvailable -Name PSWindowsUpdate -ErrorAction SilentlyContinue) {
        try {
            $rebootStatus = Get-WURebootStatus -Silent -ErrorAction SilentlyContinue
            if ($rebootStatus) { return $true }
        } catch {}
    }

    # Method 2: Registry keys
    $rebootKeys = @(
        "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired",
        "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending"
    )
    foreach ($key in $rebootKeys) {
        if (Test-Path $key) { return $true }
    }

    # Method 3: PendingFileRenameOperations
    try {
        $pfro = Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager" -Name PendingFileRenameOperations -ErrorAction SilentlyContinue
        if ($pfro) { return $true }
    } catch {}

    return $false
}

# ── Update-OSPackages ────────────────────────────────────────────────────

function Update-OSPackages {
    $result = [ordered]@{
        status              = "skipped"
        manager             = "WindowsUpdate"
        upgraded_count      = 0
        newly_installed_count = 0
        removed_count       = 0
        packages            = @()
        errors              = @()
    }

    if ($SkipOS) {
        Write-Log -Level Info -Message "Skipping OS updates (--SkipOS)"
        return $result
    }

    if (-not (Test-IsAdministrator)) {
        $msg = "Administrator privileges required for Windows Update. Run as Admin or use -SkipOS."
        Write-Log -Level Error -Message $msg
        $result.status = "failed"
        $result.errors += $msg
        return $result
    }

    Write-Log -Level Info -Message "Starting Windows Update..."

    # Approach 1: PSWindowsUpdate module
    $pswuAvailable = $null -ne (Get-Module -ListAvailable -Name PSWindowsUpdate -ErrorAction SilentlyContinue)

    if ($pswuAvailable) {
        Write-Log -Level Info -Message "Using PSWindowsUpdate module"
        try {
            Import-Module PSWindowsUpdate -ErrorAction Stop

            # Get available updates first
            Write-Log -Level Info -Message "Scanning for available updates..."
            $available = @(Get-WindowsUpdate -ErrorAction Stop)

            if ($available.Count -eq 0) {
                Write-Log -Level Success -Message "No Windows updates available"
                $result.status = "success"
                return $result
            }

            Write-Log -Level Info -Message "Found $($available.Count) update(s). Installing..."

            # Install all available updates
            $installed = @(Install-WindowsUpdate -AcceptAll -AutoReboot:$false -Confirm:$false -ErrorAction Stop)

            foreach ($update in $installed) {
                $kb = if ($update.KBArticleIDs) { "KB$($update.KBArticleIDs -join ',')" } else { "N/A" }
                $title = if ($update.Title) { $update.Title } else { "Unknown update" }
                $result.packages += "$kb - $title"
                $result.upgraded_count++
            }

            $result.status = "success"
            Write-Log -Level Success -Message "Installed $($result.upgraded_count) update(s) via PSWindowsUpdate"
            return $result
        } catch {
            $errMsg = "PSWindowsUpdate failed: $($_.Exception.Message)"
            Write-Log -Level Warn -Message "$errMsg. Falling back to UsoClient."
            $result.errors += $errMsg
        }
    }

    # Approach 2: UsoClient (built-in on Windows 10/11)
    if (Test-CommandExists "UsoClient") {
        Write-Log -Level Info -Message "Using UsoClient for Windows Update"
        try {
            Write-Log -Level Info -Message "Scanning for updates..."
            $scanOutput = & UsoClient StartScan 2>&1
            Start-Sleep -Seconds 5

            Write-Log -Level Info -Message "Starting update installation..."
            $installOutput = & UsoClient StartInstall 2>&1
            Start-Sleep -Seconds 5

            # UsoClient does not provide detailed output; record what we can
            $result.status = "success"
            $result.packages += "UsoClient scan and install triggered (details in Windows Update history)"
            Write-Log -Level Success -Message "UsoClient update cycle completed"
            return $result
        } catch {
            $errMsg = "UsoClient failed: $($_.Exception.Message)"
            Write-Log -Level Warn -Message "$errMsg. Falling back to DISM."
            $result.errors += $errMsg
        }
    }

    # Approach 3: DISM fallback for component store health
    if (Test-CommandExists "DISM") {
        Write-Log -Level Info -Message "Running DISM component store repair as fallback"
        try {
            $dismOutput = & DISM /Online /Cleanup-Image /RestoreHealth 2>&1
            $dismText = ($dismOutput | Out-String).Trim()

            if ($LASTEXITCODE -eq 0) {
                $result.status = "success"
                $result.packages += "DISM /RestoreHealth completed successfully"
                Write-Log -Level Success -Message "DISM component store repair completed"
            } else {
                $result.status = "failed"
                $result.errors += "DISM exited with code $LASTEXITCODE"
                Write-Log -Level Error -Message "DISM failed with exit code $LASTEXITCODE"
            }
            return $result
        } catch {
            $errMsg = "DISM failed: $($_.Exception.Message)"
            $result.errors += $errMsg
            Write-Log -Level Error -Message $errMsg
        }
    }

    if ($result.status -eq "skipped") {
        $result.status = "failed"
        $result.errors += "No Windows Update method available"
        Write-Log -Level Error -Message "No Windows Update method available on this system"
    }

    return $result
}

# ── Update-Tools ─────────────────────────────────────────────────────────

function Update-WingetPackages {
    $result = [ordered]@{
        status         = "skipped"
        upgraded_count = 0
        packages       = @()
        errors         = @()
    }

    if (-not (Test-CommandExists "winget")) {
        $result.status = "not_available"
        Write-Log -Level Warn -Message "winget not found, skipping"
        return $result
    }

    Write-Log -Level Info -Message "Upgrading winget packages..."
    try {
        $output = & winget upgrade --all --accept-package-agreements --accept-source-agreements --include-unknown 2>&1
        $outputText = ($output | Out-String).Trim()

        # Parse upgrade output for package lines
        $lines = $outputText -split "`n"
        $upgradeSection = $false
        foreach ($line in $lines) {
            $trimmed = $line.Trim()

            # Skip header and separator lines
            if ($trimmed -match '^-{3,}') {
                $upgradeSection = $true
                continue
            }
            if (-not $upgradeSection) { continue }
            if ([string]::IsNullOrWhiteSpace($trimmed)) { continue }
            if ($trimmed -match 'upgrades? available|No installed package') { continue }
            if ($trimmed -match '^\d+ package') { continue }

            # Lines that look like package upgrade entries
            if ($trimmed -match '\S+\s+\S+') {
                $result.packages += $trimmed
                $result.upgraded_count++
            }
        }

        # If winget reported success but we could not parse lines, note it
        if ($LASTEXITCODE -eq 0 -or $result.upgraded_count -gt 0) {
            $result.status = "success"
            Write-Log -Level Success -Message "winget: $($result.upgraded_count) package(s) processed"
        } else {
            # Exit code non-zero and no packages found might mean nothing to upgrade
            $result.status = "success"
            $result.upgraded_count = 0
            Write-Log -Level Success -Message "winget: no upgrades available"
        }
    } catch {
        $result.status = "failed"
        $result.errors += $_.Exception.Message
        Write-Log -Level Error -Message "winget upgrade failed: $($_.Exception.Message)"
    }

    return $result
}

function Update-NvidiaDriver {
    $result = [ordered]@{
        status       = "skipped"
        from_version = $null
        to_version   = $null
        errors       = @()
    }

    # Detect nvidia-smi
    $nvidiaSmi = $null
    $paths = @(
        "nvidia-smi",
        "C:\Windows\System32\nvidia-smi.exe",
        "C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe"
    )
    foreach ($p in $paths) {
        if (Test-CommandExists $p) {
            $nvidiaSmi = $p
            break
        }
        if (Test-Path $p -ErrorAction SilentlyContinue) {
            $nvidiaSmi = $p
            break
        }
    }

    if (-not $nvidiaSmi) {
        $result.status = "not_available"
        Write-Log -Level Info -Message "NVIDIA driver not detected, skipping"
        return $result
    }

    # Get current version
    try {
        $smiOutput = & $nvidiaSmi --query-gpu=driver_version --format=csv,noheader 2>&1
        $currentVersion = ($smiOutput | Out-String).Trim()
        $result.from_version = $currentVersion
        Write-Log -Level Info -Message "Current NVIDIA driver: $currentVersion"
    } catch {
        $result.from_version = "unknown"
        Write-Log -Level Warn -Message "Could not query NVIDIA driver version"
    }

    # Try updating via winget
    if (Test-CommandExists "winget") {
        try {
            $upgradeOutput = & winget upgrade --id "NVIDIA.GeForceExperience" --accept-package-agreements --accept-source-agreements 2>&1
            $upgradeText = ($upgradeOutput | Out-String).Trim()

            if ($upgradeText -match "No applicable update found" -or $upgradeText -match "No available upgrade") {
                $result.status = "success"
                $result.to_version = $result.from_version
                Write-Log -Level Info -Message "NVIDIA driver already up to date"
            } else {
                # Re-query version after upgrade
                try {
                    $newOutput = & $nvidiaSmi --query-gpu=driver_version --format=csv,noheader 2>&1
                    $result.to_version = ($newOutput | Out-String).Trim()
                } catch {
                    $result.to_version = "check manually"
                }
                $result.status = "success"
                Write-Log -Level Success -Message "NVIDIA driver update attempted via winget"
            }
        } catch {
            $result.status = "failed"
            $result.errors += $_.Exception.Message
            Write-Log -Level Warn -Message "NVIDIA driver update via winget failed: $($_.Exception.Message)"
        }
    } else {
        $result.status = "skipped"
        $result.to_version = $result.from_version
        Write-Log -Level Warn -Message "winget not available for NVIDIA driver update"
    }

    return $result
}

function Update-ChocoPackages {
    $result = [ordered]@{
        status         = "skipped"
        upgraded_count = 0
        packages       = @()
        errors         = @()
    }

    if (-not (Test-CommandExists "choco")) {
        $result.status = "not_available"
        Write-Log -Level Info -Message "Chocolatey not found, skipping"
        return $result
    }

    Write-Log -Level Info -Message "Upgrading Chocolatey packages..."
    try {
        $output = & choco upgrade all -y --no-progress 2>&1
        $outputText = ($output | Out-String).Trim()

        # Parse choco output for upgraded packages
        $lines = $outputText -split "`n"
        foreach ($line in $lines) {
            $trimmed = $line.Trim()
            if ($trimmed -match '^\s*(\S+)\s+v?([\d.]+)\s*->\s*v?([\d.]+)') {
                $pkg = "$($Matches[1]) $($Matches[2]) -> $($Matches[3])"
                $result.packages += $pkg
                $result.upgraded_count++
            }
        }

        if ($LASTEXITCODE -eq 0) {
            $result.status = "success"
            Write-Log -Level Success -Message "Chocolatey: $($result.upgraded_count) package(s) upgraded"
        } else {
            # Choco may return non-zero for partial success
            $result.status = if ($result.upgraded_count -gt 0) { "success" } else { "failed" }
            if ($result.status -eq "failed") {
                $result.errors += "choco exited with code $LASTEXITCODE"
            }
        }
    } catch {
        $result.status = "failed"
        $result.errors += $_.Exception.Message
        Write-Log -Level Error -Message "Chocolatey upgrade failed: $($_.Exception.Message)"
    }

    return $result
}

function Update-SingleTool {
    param(
        [string]$Name,
        [string]$Command,
        [string]$VersionArg,
        [string]$UpdateCommand,
        [string[]]$UpdateArgs
    )

    $result = [ordered]@{
        status       = "skipped"
        from_version = $null
        to_version   = $null
        errors       = @()
    }

    if (-not (Test-CommandExists $Command)) {
        $result.status = "not_available"
        Write-Log -Level Info -Message "$Name not found, skipping"
        return $result
    }

    # Get current version
    $result.from_version = Get-CommandVersion -Command $Command -VersionArg $VersionArg

    Write-Log -Level Info -Message "Updating $Name..."
    try {
        $output = & $UpdateCommand $UpdateArgs 2>&1
        $outputText = ($output | Out-String).Trim()

        # Get new version
        $result.to_version = Get-CommandVersion -Command $Command -VersionArg $VersionArg

        if ($LASTEXITCODE -eq 0 -or $result.to_version) {
            $result.status = "success"
            Write-Log -Level Success -Message "$Name updated: $($result.from_version) -> $($result.to_version)"
        } else {
            $result.status = "failed"
            $result.errors += "$Name update exited with code $LASTEXITCODE"
            Write-Log -Level Warn -Message "$Name update returned exit code $LASTEXITCODE"
        }
    } catch {
        $result.status = "failed"
        $result.errors += $_.Exception.Message
        Write-Log -Level Error -Message "$Name update failed: $($_.Exception.Message)"
    }

    return $result
}

function Update-Tools {
    $result = [ordered]@{
        winget        = [ordered]@{ status = "skipped"; upgraded_count = 0; packages = @() }
        nvidia_driver = [ordered]@{ status = "skipped"; from_version = $null; to_version = $null }
        choco         = [ordered]@{ status = "skipped"; upgraded_count = 0 }
        pip           = [ordered]@{ status = "skipped"; from_version = $null; to_version = $null }
        npm           = [ordered]@{ status = "skipped"; from_version = $null; to_version = $null }
        uv            = [ordered]@{ status = "skipped"; from_version = $null; to_version = $null }
    }

    if ($SkipTools) {
        Write-Log -Level Info -Message "Skipping tool updates (--SkipTools)"
        return $result
    }

    Write-Log -Level Info -Message "Updating common tools..."

    # winget
    $result.winget = Update-WingetPackages

    # NVIDIA
    $result.nvidia_driver = Update-NvidiaDriver

    # Chocolatey
    $result.choco = Update-ChocoPackages

    # pip
    $pipResult = Update-SingleTool -Name "pip" -Command "pip" -VersionArg "--version" `
        -UpdateCommand "pip" -UpdateArgs @("install", "--upgrade", "pip")
    $result.pip = [ordered]@{
        status       = $pipResult.status
        from_version = $pipResult.from_version
        to_version   = $pipResult.to_version
    }

    # npm
    $npmResult = Update-SingleTool -Name "npm" -Command "npm" -VersionArg "--version" `
        -UpdateCommand "npm" -UpdateArgs @("update", "-g")
    $result.npm = [ordered]@{
        status       = $npmResult.status
        from_version = $npmResult.from_version
        to_version   = $npmResult.to_version
    }

    # uv
    $uvResult = Update-SingleTool -Name "uv" -Command "uv" -VersionArg "--version" `
        -UpdateCommand "uv" -UpdateArgs @("self", "update")
    $result.uv = [ordered]@{
        status       = $uvResult.status
        from_version = $uvResult.from_version
        to_version   = $uvResult.to_version
    }

    return $result
}

# ── Update-Custom ────────────────────────────────────────────────────────

function Update-Custom {
    $result = [ordered]@{
        status = "skipped"
        items  = @()
    }

    if ($SkipCustom) {
        Write-Log -Level Info -Message "Skipping custom software updates (--SkipCustom)"
        return $result
    }

    if (-not $ConfigFile -or -not (Test-Path $ConfigFile)) {
        if ($ConfigFile) {
            Write-Log -Level Warn -Message "Config file not found: $ConfigFile"
            $result.status = "failed"
            $result.items += [ordered]@{
                name   = "config"
                action = "skip"
                result = "Config file not found: $ConfigFile"
            }
        } else {
            Write-Log -Level Info -Message "No config file specified, skipping custom updates"
        }
        return $result
    }

    Write-Log -Level Info -Message "Loading custom config: $ConfigFile"
    try {
        $configContent = [System.IO.File]::ReadAllText($ConfigFile)
        $config = $configContent | ConvertFrom-Json
    } catch {
        $result.status = "failed"
        $result.items += [ordered]@{
            name   = "config"
            action = "skip"
            result = "Failed to parse config: $($_.Exception.Message)"
        }
        Write-Log -Level Error -Message "Failed to parse config file: $($_.Exception.Message)"
        return $result
    }

    $hasErrors = $false

    # Process winget packages
    if ($config.packages -and $config.packages.winget) {
        foreach ($pkg in $config.packages.winget) {
            $item = [ordered]@{
                name   = $pkg
                action = "skip"
                result = ""
            }

            if (-not (Test-CommandExists "winget")) {
                $item.result = "winget not available"
                $result.items += $item
                continue
            }

            Write-Log -Level Info -Message "Processing winget package: $pkg"
            try {
                # Check if installed
                $listOutput = & winget list --id $pkg --accept-source-agreements 2>&1
                $listText = ($listOutput | Out-String).Trim()

                if ($listText -match $pkg) {
                    # Already installed, try upgrade
                    $item.action = "upgrade"
                    $upgradeOutput = & winget upgrade --id $pkg --accept-package-agreements --accept-source-agreements 2>&1
                    $upgradeText = ($upgradeOutput | Out-String).Trim()

                    if ($upgradeText -match "No applicable update|No available upgrade|already installed") {
                        $item.result = "already up to date"
                    } else {
                        $item.result = "upgraded"
                    }
                } else {
                    # Not installed, install it
                    $item.action = "install"
                    $installOutput = & winget install --id $pkg --accept-package-agreements --accept-source-agreements 2>&1
                    $installText = ($installOutput | Out-String).Trim()

                    if ($LASTEXITCODE -eq 0) {
                        $item.result = "installed"
                    } else {
                        $item.result = "install failed (exit $LASTEXITCODE)"
                        $hasErrors = $true
                    }
                }

                Write-Log -Level Info -Message "  $pkg -> $($item.action): $($item.result)"
            } catch {
                $item.result = "error: $($_.Exception.Message)"
                $hasErrors = $true
                Write-Log -Level Error -Message "  $pkg failed: $($_.Exception.Message)"
            }

            $result.items += $item
        }
    }

    # Process choco packages
    if ($config.packages -and $config.packages.choco) {
        foreach ($pkg in $config.packages.choco) {
            $item = [ordered]@{
                name   = $pkg
                action = "skip"
                result = ""
            }

            if (-not (Test-CommandExists "choco")) {
                $item.result = "choco not available"
                $result.items += $item
                continue
            }

            Write-Log -Level Info -Message "Processing choco package: $pkg"
            try {
                # choco upgrade handles both install and upgrade
                $item.action = "upgrade"
                $output = & choco upgrade $pkg -y --no-progress 2>&1
                $outputText = ($output | Out-String).Trim()

                if ($outputText -match "already installed" -or $outputText -match "is the latest version") {
                    $item.result = "already up to date"
                } elseif ($LASTEXITCODE -eq 0) {
                    $item.result = "upgraded"
                } else {
                    $item.result = "failed (exit $LASTEXITCODE)"
                    $hasErrors = $true
                }

                Write-Log -Level Info -Message "  $pkg -> $($item.action): $($item.result)"
            } catch {
                $item.result = "error: $($_.Exception.Message)"
                $hasErrors = $true
                Write-Log -Level Error -Message "  $pkg failed: $($_.Exception.Message)"
            }

            $result.items += $item
        }
    }

    # Process pip packages
    if ($config.packages -and $config.packages.pip) {
        foreach ($pkg in $config.packages.pip) {
            $item = [ordered]@{
                name   = $pkg
                action = "skip"
                result = ""
            }

            if (-not (Test-CommandExists "pip")) {
                $item.result = "pip not available"
                $result.items += $item
                continue
            }

            Write-Log -Level Info -Message "Processing pip package: $pkg"
            try {
                $item.action = "upgrade"
                $output = & pip install --upgrade $pkg 2>&1
                $outputText = ($output | Out-String).Trim()

                if ($outputText -match "already satisfied" -or $outputText -match "already up-to-date") {
                    $item.result = "already up to date"
                } elseif ($LASTEXITCODE -eq 0) {
                    $item.result = "upgraded"
                } else {
                    $item.result = "failed (exit $LASTEXITCODE)"
                    $hasErrors = $true
                }

                Write-Log -Level Info -Message "  $pkg -> $($item.action): $($item.result)"
            } catch {
                $item.result = "error: $($_.Exception.Message)"
                $hasErrors = $true
                Write-Log -Level Error -Message "  $pkg failed: $($_.Exception.Message)"
            }

            $result.items += $item
        }
    }

    # Process custom scripts
    if ($config.scripts) {
        foreach ($script in $config.scripts) {
            $scriptName = $script.name
            $item = [ordered]@{
                name   = $scriptName
                action = "skip"
                result = ""
            }

            Write-Log -Level Info -Message "Processing custom script: $scriptName"
            try {
                # Check if already installed
                $checkCmd = $script.check
                $isInstalled = $false
                if ($checkCmd) {
                    try {
                        $checkOutput = Invoke-Expression $checkCmd 2>&1
                        if ($LASTEXITCODE -eq 0) {
                            $isInstalled = $true
                            $item.result = "already installed: $(($checkOutput | Out-String).Trim())"
                            $item.action = "skip"
                            Write-Log -Level Info -Message "  $scriptName already installed"
                        }
                    } catch {
                        $isInstalled = $false
                    }
                }

                if (-not $isInstalled) {
                    $item.action = "install"
                    $installCmd = $script.install
                    if ($installCmd) {
                        $installOutput = Invoke-Expression $installCmd 2>&1
                        if ($LASTEXITCODE -eq 0) {
                            $item.result = "installed"
                            Write-Log -Level Success -Message "  $scriptName installed"
                        } else {
                            $item.result = "install failed (exit $LASTEXITCODE)"
                            $hasErrors = $true
                            Write-Log -Level Error -Message "  $scriptName install failed"
                        }
                    } else {
                        $item.result = "no install command specified"
                        Write-Log -Level Warn -Message "  $scriptName has no install command"
                    }
                }
            } catch {
                $item.result = "error: $($_.Exception.Message)"
                $hasErrors = $true
                Write-Log -Level Error -Message "  $scriptName failed: $($_.Exception.Message)"
            }

            $result.items += $item
        }
    }

    $result.status = if ($hasErrors) { "failed" } else { "success" }
    return $result
}

# ── Main ─────────────────────────────────────────────────────────────────

$timestampStart = Get-IsoTimestamp
$hostname = $env:COMPUTERNAME
if (-not $hostname) { $hostname = "unknown" }
$datestamp = (Get-Date -Format "yyyyMMdd")

if (-not $OutputFile) {
    $OutputFile = Join-Path -Path (Get-Location) -ChildPath "system-update-$hostname-$datestamp.json"
}

Write-Log -Level Info -Message "========================================="
Write-Log -Level Info -Message "System Update - Windows"
Write-Log -Level Info -Message "Script version: $SCRIPT_VERSION"
Write-Log -Level Info -Message "Hostname: $hostname"
Write-Log -Level Info -Message "Started: $timestampStart"
Write-Log -Level Info -Message "Output: $OutputFile"
Write-Log -Level Info -Message "========================================="

# Admin check (warn early but don't exit unless doing OS updates)
$isAdmin = Test-IsAdministrator
if (-not $isAdmin) {
    Write-Log -Level Warn -Message "Not running as Administrator. Windows Update will be skipped unless -SkipOS is set."
}

# Run update phases
Write-Log -Level Info -Message ""
Write-Log -Level Info -Message "--- Phase 1: OS Updates ---"
try {
    $osResult = Update-OSPackages
} catch {
    Write-Log -Level Error -Message "OS update phase failed: $($_.Exception.Message)"
    $osResult = [ordered]@{
        status              = "failed"
        manager             = "WindowsUpdate"
        upgraded_count      = 0
        newly_installed_count = 0
        removed_count       = 0
        packages            = @()
        errors              = @($_.Exception.Message)
    }
}

Write-Log -Level Info -Message ""
Write-Log -Level Info -Message "--- Phase 2: Tool Updates ---"
try {
    $toolsResult = Update-Tools
} catch {
    Write-Log -Level Error -Message "Tools update phase failed: $($_.Exception.Message)"
    $toolsResult = [ordered]@{
        winget        = [ordered]@{ status = "failed"; upgraded_count = 0; packages = @() }
        nvidia_driver = [ordered]@{ status = "failed"; from_version = $null; to_version = $null }
        choco         = [ordered]@{ status = "failed"; upgraded_count = 0 }
        pip           = [ordered]@{ status = "failed"; from_version = $null; to_version = $null }
        npm           = [ordered]@{ status = "failed"; from_version = $null; to_version = $null }
        uv            = [ordered]@{ status = "failed"; from_version = $null; to_version = $null }
    }
}

Write-Log -Level Info -Message ""
Write-Log -Level Info -Message "--- Phase 3: Custom Software ---"
try {
    $customResult = Update-Custom
} catch {
    Write-Log -Level Error -Message "Custom update phase failed: $($_.Exception.Message)"
    $customResult = [ordered]@{
        status = "failed"
        items  = @([ordered]@{
            name   = "phase"
            action = "skip"
            result = "Phase failed: $($_.Exception.Message)"
        })
    }
}

# Reboot detection
$timestampEnd = Get-IsoTimestamp
$rebootRequired = Test-RebootRequired

# Build summary
$osPatchCount = $osResult.upgraded_count
$wingetCount = if ($toolsResult.winget.upgraded_count) { $toolsResult.winget.upgraded_count } else { 0 }
$chocoCount = if ($toolsResult.choco.upgraded_count) { $toolsResult.choco.upgraded_count } else { 0 }
$customCount = ($customResult.items | Where-Object {
    $_.result -eq "installed" -or $_.result -eq "upgraded"
}).Count
$toolTotal = $wingetCount + $chocoCount
$summary = "Updated $osPatchCount OS patches, $toolTotal tool packages ($wingetCount winget, $chocoCount choco), $customCount custom items"

Write-Log -Level Info -Message ""
Write-Log -Level Info -Message "========================================="
Write-Log -Level Success -Message $summary
if ($rebootRequired) {
    Write-Log -Level Warn -Message "A system reboot is required"
}
Write-Log -Level Info -Message "========================================="

# Build JSON report
$report = [ordered]@{
    schema_version  = $SCHEMA_VERSION
    script_version  = $SCRIPT_VERSION
    platform        = "windows"
    hostname        = $hostname
    timestamp_start = $timestampStart
    timestamp_end   = $timestampEnd
    updates         = [ordered]@{
        os_packages   = $osResult
        snap_packages = [ordered]@{
            status         = "not_applicable"
            upgraded_count = 0
            packages       = @()
            errors         = @()
        }
        tools         = $toolsResult
        custom        = $customResult
    }
    reboot_required = $rebootRequired
    summary         = $summary
}

# Write JSON output
try {
    $parentDir = Split-Path -Parent $OutputFile
    if ($parentDir -and -not (Test-Path $parentDir)) {
        New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
    }

    $jsonOutput = $report | ConvertTo-Json -Depth 5
    [System.IO.File]::WriteAllText(
        $OutputFile,
        $jsonOutput,
        (New-Object System.Text.UTF8Encoding $false)
    )

    $fileSize = (Get-Item $OutputFile).Length
    $fileSizeKB = "{0:N1}" -f ($fileSize / 1024)
    Write-Log -Level Success -Message "Report written to: $OutputFile ($fileSizeKB KB)"
} catch {
    Write-Log -Level Error -Message "Failed to write output file: $($_.Exception.Message)"

    # Attempt fallback write to temp
    try {
        $fallbackPath = Join-Path $env:TEMP "system-update-$hostname-$datestamp.json"
        $jsonOutput = $report | ConvertTo-Json -Depth 5
        [System.IO.File]::WriteAllText(
            $fallbackPath,
            $jsonOutput,
            (New-Object System.Text.UTF8Encoding $false)
        )
        Write-Log -Level Warn -Message "Fallback report written to: $fallbackPath"
    } catch {
        Write-Log -Level Error -Message "Fallback write also failed: $($_.Exception.Message)"
        exit 1
    }
}

# Handle reboot if requested
if ($Reboot -and $rebootRequired) {
    Write-Log -Level Warn -Message "Scheduling system restart in 60 seconds..."
    & shutdown /r /t 60 /c "System update completed. Restarting." 2>&1 | Out-Null
    Write-Log -Level Info -Message "Restart scheduled. Use 'shutdown /a' to abort."
} elseif ($Reboot -and -not $rebootRequired) {
    Write-Log -Level Info -Message "Reboot requested but not required. Skipping restart."
}

Write-Log -Level Success -Message "System update complete."
