# ABOUTME: System maintenance orchestrator (Windows). Runs hardware assessment, system updates, and re-assessment to track changes over time.

param(
    [string]$ConfigFile = "",
    [string]$OutputDir = ".",
    [switch]$SkipAssess,
    [switch]$SkipUpdate,
    [switch]$Reboot,
    [switch]$Quiet,
    [switch]$Help
)

$SCRIPT_VERSION = "1.0.0"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# ── Logging ───────────────────────────────────────────────────────────
function Write-Log {
    param([string]$Level = "Info", [string]$Message)
    if ($Quiet -and $Level -ne "Error") { return }
    $color = switch ($Level) {
        "Info"    { "Cyan" }
        "Warn"    { "Yellow" }
        "Error"   { "Red" }
        "Success" { "Green" }
        "Phase"   { "Magenta" }
        default   { "White" }
    }
    if ($Level -eq "Phase") {
        Write-Host ""
        Write-Host ("=" * 50) -ForegroundColor $color
        Write-Host "  $Message" -ForegroundColor $color
        Write-Host ("=" * 50) -ForegroundColor $color
        Write-Host ""
    } else {
        $prefix = switch ($Level) {
            "Info"    { "[INFO]" }
            "Warn"    { "[WARN]" }
            "Error"   { "[ERROR]" }
            "Success" { "[OK]" }
        }
        Write-Host "$prefix $Message" -ForegroundColor $color
    }
}

# ── Help ──────────────────────────────────────────────────────────────
if ($Help) {
    @"
Usage: system-maintain.ps1 [OPTIONS]

Orchestrate full system maintenance: assess -> update -> re-assess -> changelog.

Options:
  -ConfigFile FILE    Custom software config for updates (JSON)
  -OutputDir DIR      Directory for all output files (default: .)
  -SkipAssess         Skip hardware assessments (update only)
  -SkipUpdate         Skip updates (assess only)
  -Reboot             Reboot after updates if needed
  -Quiet              Suppress log messages
  -Help               Show this help message

Workflow:
  1. Pre-update hardware assessment
  2. System update
  3. Post-update hardware assessment
  4. Changelog generation

Examples:
  .\system-maintain.ps1 -OutputDir C:\maintenance-logs
  .\system-maintain.ps1 -ConfigFile .\custom-packages.json -Reboot
  .\system-maintain.ps1 -SkipUpdate    # Assessment only
"@
    exit 0
}

# ── Changelog Generator ──────────────────────────────────────────────
function New-Changelog {
    param(
        [string]$PreFile,
        [string]$PostFile,
        [string]$UpdateFile,
        [string]$ChangelogFile
    )

    Write-Log -Level "Info" -Message "Generating changelog..."

    $changelog = [ordered]@{
        schema_version = "1.0"
        generated      = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        hostname       = $env:COMPUTERNAME
        changes        = [ordered]@{
            hardware = @()
            software = @()
            os       = @()
        }
        summary        = [ordered]@{
            hardware_changes = 0
            software_changes = 0
            os_changes       = 0
            total_changes    = 0
        }
    }

    # Load files
    $pre = $post = $updates = $null
    try { if (Test-Path $PreFile)    { $pre     = Get-Content $PreFile -Raw | ConvertFrom-Json } } catch {}
    try { if (Test-Path $PostFile)   { $post    = Get-Content $PostFile -Raw | ConvertFrom-Json } } catch {}
    try { if (Test-Path $UpdateFile) { $updates = Get-Content $UpdateFile -Raw | ConvertFrom-Json } } catch {}

    # Compare hardware (pre vs post)
    if ($pre -and $post) {
        foreach ($section in @("cpu", "memory", "motherboard")) {
            $preSec  = $pre.$section
            $postSec = $post.$section
            if ($preSec -and $postSec) {
                foreach ($prop in ($preSec.PSObject.Properties.Name + $postSec.PSObject.Properties.Name | Sort-Object -Unique)) {
                    $oldVal = $preSec.$prop
                    $newVal = $postSec.$prop
                    if ("$oldVal" -ne "$newVal") {
                        $changelog.changes.hardware += [ordered]@{
                            section = $section
                            field   = $prop
                            before  = $oldVal
                            after   = $newVal
                        }
                    }
                }
            }
        }

        # OS changes
        foreach ($key in @("name", "kernel")) {
            $oldVal = $pre.os.$key
            $newVal = $post.os.$key
            if ("$oldVal" -ne "$newVal") {
                $changelog.changes.os += [ordered]@{
                    field  = $key
                    before = $oldVal
                    after  = $newVal
                }
            }
        }
    }

    # Software changes from update log
    if ($updates -and $updates.updates) {
        $up = $updates.updates

        if ($up.os_packages.status -eq "success" -and $up.os_packages.upgraded_count -gt 0) {
            $changelog.changes.software += [ordered]@{
                category = "os_packages"
                manager  = $up.os_packages.manager
                count    = $up.os_packages.upgraded_count
                packages = @($up.os_packages.packages)
            }
        }

        if ($up.tools) {
            foreach ($prop in $up.tools.PSObject.Properties) {
                $toolData = $prop.Value
                if ($toolData.status -eq "updated") {
                    $changelog.changes.software += [ordered]@{
                        category     = "tool"
                        name         = $prop.Name
                        from_version = $toolData.from_version
                        to_version   = $toolData.to_version
                    }
                }
            }
        }

        if ($up.custom.items) {
            foreach ($item in $up.custom.items) {
                if ($item.action -in @("install", "upgrade")) {
                    $changelog.changes.software += [ordered]@{
                        category = "custom"
                        name     = $item.name
                        action   = $item.action
                        result   = $item.result
                    }
                }
            }
        }
    }

    # Summary
    $changelog.summary.hardware_changes = $changelog.changes.hardware.Count
    $changelog.summary.software_changes = $changelog.changes.software.Count
    $changelog.summary.os_changes       = $changelog.changes.os.Count
    $changelog.summary.total_changes    = $changelog.changes.hardware.Count + $changelog.changes.software.Count + $changelog.changes.os.Count

    $jsonContent = $changelog | ConvertTo-Json -Depth 5
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($ChangelogFile, $jsonContent, $utf8NoBom)

    Write-Log -Level "Info" -Message "Changelog: $($changelog.summary.total_changes) changes detected"
}

# ── Main ──────────────────────────────────────────────────────────────
$hostname = $env:COMPUTERNAME
$datestamp = (Get-Date).ToString("yyyyMMdd")

if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

$assessScript = Join-Path $ScriptDir "hardware-assess.ps1"
$updateScript = Join-Path $ScriptDir "system-update.ps1"

# Verify scripts exist
if (-not $SkipAssess -and -not (Test-Path $assessScript)) {
    Write-Log -Level "Error" -Message "hardware-assess.ps1 not found at: $assessScript"
    exit 1
}
if (-not $SkipUpdate -and -not (Test-Path $updateScript)) {
    Write-Log -Level "Error" -Message "system-update.ps1 not found at: $updateScript"
    exit 1
}

$preAssess   = Join-Path $OutputDir "hardware-assessment-$hostname-$datestamp-pre.json"
$updateLog   = Join-Path $OutputDir "system-update-$hostname-$datestamp.json"
$postAssess  = Join-Path $OutputDir "hardware-assessment-$hostname-$datestamp-post.json"
$changelogFile = Join-Path $OutputDir "system-changelog-$hostname-$datestamp.json"

Write-Log -Level "Info" -Message "System maintenance v$SCRIPT_VERSION starting on $hostname"
Write-Log -Level "Info" -Message "Output directory: $OutputDir"

# ── Phase 1: Pre-update assessment ──
if (-not $SkipAssess) {
    Write-Log -Level "Phase" -Message "Phase 1/4: Pre-Update Assessment"
    $assessArgs = @{ OutputFile = $preAssess; Pretty = $true }
    if ($Quiet) { $assessArgs.Quiet = $true }
    & $assessScript @assessArgs
    Write-Log -Level "Success" -Message "Pre-assessment saved: $preAssess"
} else {
    Write-Log -Level "Info" -Message "Skipping pre-update assessment"
}

# ── Phase 2: System updates ──
if (-not $SkipUpdate) {
    Write-Log -Level "Phase" -Message "Phase 2/4: System Updates"
    $updateArgs = @{ OutputFile = $updateLog }
    if ($ConfigFile) { $updateArgs.ConfigFile = $ConfigFile }
    if ($Quiet) { $updateArgs.Quiet = $true }
    & $updateScript @updateArgs
    Write-Log -Level "Success" -Message "Update log saved: $updateLog"
} else {
    Write-Log -Level "Info" -Message "Skipping system updates"
}

# ── Phase 3: Post-update assessment ──
if (-not $SkipAssess) {
    Write-Log -Level "Phase" -Message "Phase 3/4: Post-Update Assessment"
    $assessArgs = @{ OutputFile = $postAssess; Pretty = $true }
    if ($Quiet) { $assessArgs.Quiet = $true }
    & $assessScript @assessArgs
    Write-Log -Level "Success" -Message "Post-assessment saved: $postAssess"
} else {
    Write-Log -Level "Info" -Message "Skipping post-update assessment"
}

# ── Phase 4: Changelog ──
Write-Log -Level "Phase" -Message "Phase 4/4: Generating Changelog"
New-Changelog -PreFile $preAssess -PostFile $postAssess -UpdateFile $updateLog -ChangelogFile $changelogFile
Write-Log -Level "Success" -Message "Changelog saved: $changelogFile"

# ── Summary ──
Write-Log -Level "Phase" -Message "Maintenance Complete"
Write-Log -Level "Info" -Message "Files generated:"
if (-not $SkipAssess) { Write-Log -Level "Info" -Message "  Pre-assessment:  $preAssess" }
if (-not $SkipUpdate) { Write-Log -Level "Info" -Message "  Update log:      $updateLog" }
if (-not $SkipAssess) { Write-Log -Level "Info" -Message "  Post-assessment: $postAssess" }
Write-Log -Level "Info" -Message "  Changelog:       $changelogFile"

# ── Reboot if requested ──
$rebootRequired = Test-Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired"
if ($Reboot -and $rebootRequired) {
    Write-Log -Level "Warn" -Message "Reboot required - rebooting in 60 seconds (run 'shutdown /a' to cancel)"
    shutdown /r /t 60 /c "System maintenance complete - scheduled reboot"
} elseif ($rebootRequired) {
    Write-Log -Level "Warn" -Message "Reboot required - restart when ready"
}
