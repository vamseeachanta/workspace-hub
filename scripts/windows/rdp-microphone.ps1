#Requires -Version 5.1
<#
.SYNOPSIS
    Audits and narrowly repairs RDP microphone redirection.

.DESCRIPTION
    Run Role=Client locally on the workstation that owns the microphone and
    Role=Server inside the destination RDP session. Audit is the default.

    Default Json mode writes exactly one JSON document to stdout and creates
    no files. Human output is an explicit, mutually exclusive mode.

    The script never restarts services, signs out users, or changes microphone
    privacy or machine policy. Repair can only enable audiocapturemode in an
    explicitly named classic .rdp profile, reset exact saved target consent
    after a checksummed snapshot, or restore such a snapshot.

.EXAMPLE
    .\rdp-microphone.ps1 -Role Client -TargetHost ACMA-HOU-RDS02

.EXAMPLE
    .\rdp-microphone.ps1 -Role Client -ClientType Mstsc -ConfigurationSource C:\Users\me\Desktop\RDS02.rdp -RdpFile C:\Users\me\Desktop\RDS02.rdp -Repair

.EXAMPLE
    .\rdp-microphone.ps1 -Role Client -TargetHost ACMA-HOU-RDS02 -Repair -ResetConsent -StateDirectory C:\Temp\RdpMicState

.EXAMPLE
    .\rdp-microphone.ps1 -Role Server -OutputFormat Human
#>

[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'Medium')]
param(
    [Parameter(Mandatory)]
    [ValidateSet('Client', 'Server')]
    [string]$Role,

    [string]$TargetHost = 'ACMA-HOU-RDS02',
    [string]$RdpFile,
    [ValidateSet('Auto', 'Mstsc', 'MSRDC', 'WindowsApp', 'Unknown')]
    [string]$ClientType = 'Auto',
    [string]$ConfigurationSource,
    [switch]$Repair,
    [switch]$ResetConsent,
    [string]$RestoreSnapshot,
    [string]$StateDirectory,
    [string]$ReportPath,

    [ValidateSet('Json', 'Human')]
    [string]$OutputFormat = 'Json',

    [long]$AfterRecordId = 0,
    [string]$TargetCorrelation
)

$ErrorActionPreference = 'Stop'
# PowerShell propagates the script's WhatIf preference into Import-Module, which can
# emit native "What if" text and even prevent command discovery. Import is read-only,
# so isolate it from WhatIf to preserve the one-document JSON contract.
$requestedWhatIf = $WhatIfPreference
$WhatIfPreference = $false
Import-Module (Join-Path $PSScriptRoot 'lib\RdpMicrophone.psm1') -Force
# Keep the ambient preference disabled for read-only discovery as Windows PowerShell
# may auto-import system modules and otherwise print their ShouldProcess messages.
# Requested mutations are simulated explicitly below when $requestedWhatIf is true.

$findings = New-Object System.Collections.Generic.List[object]
$changes = New-Object System.Collections.Generic.List[object]

function Add-Finding {
    param([string]$Area, [string]$Check, [string]$Status, [string]$Detail)
    $findings.Add([pscustomobject]@{ Area = $Area; Check = $Check; Status = $Status; Detail = $Detail })
}

function Get-PrivacyAudit {
    $root = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\microphone'
    $desktop = Join-Path $root 'NonPackaged'
    $blockedRdpApps = @()
    if (Test-Path -LiteralPath $desktop) {
        $blockedRdpApps = @(
            Get-ChildItem -LiteralPath $desktop -Recurse -ErrorAction SilentlyContinue |
                Where-Object {
                    $_.PSChildName -match 'mstsc|msrdc|windowsapp|remote.*desktop' -and
                    (Get-RdpMicRegistryValue -Path $_.PSPath -Name 'Value') -eq 'Deny'
                } |
                Select-Object -ExpandProperty PSChildName -Unique
        )
    }
    [pscustomobject]@{
        User = Get-RdpMicRegistryValue -Path $root -Name 'Value'
        DesktopApps = Get-RdpMicRegistryValue -Path $desktop -Name 'Value'
        MachineLetApps = Get-RdpMicRegistryValue -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\AppPrivacy' -Name 'LetAppsAccessMicrophone'
        MachineLetDesktopApps = Get-RdpMicRegistryValue -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\AppPrivacy' -Name 'LetDesktopAppsAccessMicrophone'
        BlockedRdpApplications = $blockedRdpApps
        Note = 'Privacy and machine policy are audit-only; use Settings or an administrator-managed policy surface.'
    }
}

function Get-ServerPolicyAudit {
    $path = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows NT\Terminal Services'
    $listener = $null
    try {
        $listener = Get-CimInstance -Namespace 'root\cimv2\terminalservices' -ClassName Win32_TSGeneralSetting -Filter "TerminalName='RDP-tcp'" -ErrorAction Stop
    } catch { }
    [pscustomobject]@{
        fDisableAudioCapture = Get-RdpMicRegistryValue -Path $path -Name 'fDisableAudioCapture'
        EffectiveAudioCaptureRedir = if ($listener) { $listener.AudioCaptureRedir } else { $null }
        EffectiveAudioMapping = if ($listener) { $listener.AudioMapping } else { $null }
        Meaning = '0 or absent permits capture unless another effective policy denies it; 1 disables capture.'
    }
}

function Get-AudioServiceAudit {
    @('AudioEndpointBuilder', 'Audiosrv', 'TermService', 'UmRdpService') | ForEach-Object {
        $service = Get-Service -Name $_ -ErrorAction SilentlyContinue
        [pscustomobject]@{
            Name = $_
            Present = ($null -ne $service)
            Status = if ($service) { [string]$service.Status } else { 'Missing' }
        }
    }
}

function Get-SafeRdpEvents {
    $log = 'Microsoft-Windows-RemoteDesktopServices-RdpCoreTS/Operational'
    try {
        @(
            Get-WinEvent -LogName $log -MaxEvents 80 -ErrorAction Stop |
                Where-Object { $_.RecordId -gt $AfterRecordId } |
                ForEach-Object {
                    ConvertFrom-RdpMicEventXml -Xml $_.ToXml()
                }
        )
    } catch { @() }
}

$exitCode = 0
$errorDetail = $null
try {
    if ($Repair -and -not $RdpFile -and -not $ResetConsent -and -not $RestoreSnapshot) {
        throw '-Repair requires -RdpFile for profile changes.'
    }
    if (($ResetConsent -or $RestoreSnapshot) -and -not $Repair) {
        throw '-ResetConsent and -RestoreSnapshot require -Repair.'
    }
    if ($ResetConsent -and -not $StateDirectory) {
        throw '-ResetConsent requires an explicit -StateDirectory outside the repository.'
    }
    if ($ResetConsent) {
        $repoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
        $stateRoot = [IO.Path]::GetFullPath($StateDirectory)
        if ($stateRoot.TrimEnd('\') -eq $repoRoot.TrimEnd('\') -or $stateRoot.StartsWith($repoRoot.TrimEnd('\') + '\', [StringComparison]::OrdinalIgnoreCase)) {
            throw '-StateDirectory must be outside the repository.'
        }
    }
    if ($Role -eq 'Server' -and ($Repair -or $ResetConsent -or $RestoreSnapshot)) {
        throw 'Server role is audit-only; perform selected client repair locally on the workstation.'
    }

    $privacy = Get-PrivacyAudit
    $endpoints = @(Get-RdpMicCaptureEndpoints)
    $activeEndpoints = @($endpoints | Where-Object { $_.Active })
    $endpointVerdict = Get-RdpMicEndpointVerdict -Role $Role -Endpoints $endpoints

    if ($privacy.User -eq 'Deny' -or $privacy.DesktopApps -eq 'Deny' -or $privacy.BlockedRdpApplications.Count -gt 0 -or $privacy.MachineLetApps -eq 2 -or $privacy.MachineLetDesktopApps -eq 2) {
        Add-Finding 'Privacy' 'Microphone access' 'FAIL' 'A current-user privacy surface explicitly denies microphone access.'
        $exitCode = 2
    } else {
        Add-Finding 'Privacy' 'Microphone access' 'PASS' 'No global or desktop-app Deny was found.'
    }

    if ($Role -eq 'Client') {
        if (-not $endpointVerdict.Passed) {
            Add-Finding 'Audio' 'Local capture endpoint' 'FAIL' 'No active local capture endpoint was found.'
            $exitCode = 2
        } else {
            Add-Finding 'Audio' 'Local capture endpoint' 'PASS' "$($activeEndpoints.Count) active local capture endpoint(s) found."
        }
        $client = Get-RdpMicClientIdentity
        $effectiveClientType = if ($ClientType -eq 'Auto') { $client.Type } else { $ClientType.ToLowerInvariant().Replace('windowsapp', 'windows_app') }
        if ($effectiveClientType -eq 'unknown') {
            Add-Finding 'Client' 'RDP client type' 'WARN' 'No running mstsc, msrdc, or Windows App process was identified; repair must not guess a profile.'
        } else {
            Add-Finding 'Client' 'RDP client type' 'PASS' "Effective client contract is $effectiveClientType (declared: $ClientType; detected: $($client.Type))."
        }
        $profile = if ($RdpFile) { Get-RdpMicProfileAudit -Path $RdpFile } else { $null }
        $savedConsentPath = 'HKCU:\Software\Microsoft\Terminal Server Client\LocalDevices'
        $savedConsent = Get-RdpMicRegistryValue -Path $savedConsentPath -Name $TargetHost
        if ($Repair -and $RdpFile) {
            if ($effectiveClientType -ne 'mstsc') {
                throw "Profile repair is blocked for client type '$effectiveClientType'; only a proven classic mstsc profile can be changed."
            }
            if (-not $ConfigurationSource) {
                throw '-ConfigurationSource must explicitly name the classic .rdp profile used by the target connection.'
            }
            $selectedProfile = [IO.Path]::GetFullPath($RdpFile)
            $declaredSource = [IO.Path]::GetFullPath($ConfigurationSource)
            if (-not $selectedProfile.Equals($declaredSource, [StringComparison]::OrdinalIgnoreCase)) {
                throw '-ConfigurationSource and -RdpFile must resolve to the same classic profile.'
            }
        }
        if ($Repair -and $RdpFile) {
            if ($requestedWhatIf) {
                $change = [pscustomobject]@{ Changed = $false; WhatIf = $true; Path = $RdpFile; Action = 'Would back up and enable audiocapturemode only.' }
            } else {
                $change = Repair-RdpMicProfile -Path $RdpFile
            }
            $changes.Add($change)
        }
        if ($Repair -and $ResetConsent) {
            $change = if ($requestedWhatIf) {
                [pscustomobject]@{ Changed = $false; WhatIf = $true; TargetHost = $TargetHost; Action = 'Would snapshot and remove only exact target consent.' }
            } else {
                Reset-RdpMicTargetConsent -TargetHost $TargetHost -StateDirectory $StateDirectory -Confirm:$false
            }
            if ($null -ne $change) { $changes.Add($change) }
        }
        if ($Repair -and $RestoreSnapshot) {
            $change = if ($requestedWhatIf) {
                [pscustomobject]@{ Changed = $false; WhatIf = $true; SnapshotPath = $RestoreSnapshot; Action = 'Would validate and restore exact target consent.' }
            } else {
                Restore-RdpMicConsentSnapshot -SnapshotPath $RestoreSnapshot -Confirm:$false
            }
            if ($null -ne $change) { $changes.Add($change) }
        }
        $roleEvidence = [ordered]@{ Client = $client; EffectiveClientType = $effectiveClientType; ConfigurationSource = $ConfigurationSource; Profile = $profile; SavedTargetConsent = $savedConsent }
    } else {
        if (-not $endpointVerdict.Passed) {
            Add-Finding 'Audio' 'Redirected Remote Audio endpoint' 'FAIL' 'No active redirected Remote Audio capture endpoint was found; unrelated capture devices cannot satisfy this check.'
            $exitCode = 2
        } else {
            Add-Finding 'Audio' 'Redirected Remote Audio endpoint' 'PASS' "$($endpointVerdict.MatchingCount) active redirected endpoint(s) found."
        }
        $policy = Get-ServerPolicyAudit
        $services = @(Get-AudioServiceAudit)
        if ($policy.fDisableAudioCapture -eq 1) {
            Add-Finding 'Policy' 'Audio capture redirection' 'FAIL' 'Effective registry policy disables capture redirection.'
            $exitCode = 2
        } else {
            Add-Finding 'Policy' 'Audio capture redirection' 'PASS' 'Capture is not disabled by the inspected policy value.'
        }
        $stoppedServices = @($services | Where-Object { -not $_.Present -or $_.Status -ne 'Running' })
        if ($stoppedServices.Count -gt 0) {
            Add-Finding 'Services' 'Required audio/RDP services' 'FAIL' (($stoppedServices.Name | Sort-Object -Unique) -join ', ')
            $exitCode = 2
        } else {
            Add-Finding 'Services' 'Required audio/RDP services' 'PASS' 'AudioEndpointBuilder, Audiosrv, TermService, and UmRdpService are running.'
        }
        $events = @(Get-SafeRdpEvents)
        $eventVerdict = if ($TargetCorrelation) {
            Get-RdpMicEventVerdict -Events $events -AfterRecordId $AfterRecordId -TargetCorrelation $TargetCorrelation
        } else {
            [pscustomobject]@{ Verdict = 'inconclusive'; Reason = 'TargetCorrelation was not supplied; shared-host events cannot be attributed safely.' }
        }
        $roleEvidence = [ordered]@{ Policy = $policy; Services = $services; Events = $events; EventVerdict = $eventVerdict }
    }
} catch {
    $exitCode = 2
    $errorDetail = $_.Exception.Message
    Add-Finding 'Execution' 'Request' 'FAIL' $errorDetail
    if (-not $privacy) { $privacy = $null }
    if (-not $endpoints) { $endpoints = @() }
    if (-not $roleEvidence) { $roleEvidence = [ordered]@{} }
}

$modeName = 'Audit'
if ($Repair) { $modeName = if ($requestedWhatIf) { 'WhatIf' } else { 'Repair' } }
$findingArray = @($findings | ForEach-Object { $_ })
$changeArray = @($changes | ForEach-Object { $_ })
$report = [ordered]@{
    SchemaVersion = 1
    TimestampUtc = (Get-Date).ToUniversalTime().ToString('o')
    Role = $Role
    TargetHost = $TargetHost
    Machine = $env:COMPUTERNAME
    User = $env:USERNAME
    Mode = $modeName
    ExitCode = $exitCode
    Findings = $findingArray
    Privacy = $privacy
    CaptureEndpoints = @($endpoints)
    Evidence = $roleEvidence
    Changes = $changeArray
    Error = $errorDetail
    NextStep = if ($Role -eq 'Server' -and -not $endpointVerdict.Passed) {
        'Sign out fully, configure microphone redirection on the client, reconnect, then require Remote Audio plus a real recording.'
    } else {
        'Validate a 3-5 second recording before testing Win+H.'
    }
}

$json = $report | ConvertTo-Json -Depth 8
if ($ReportPath) {
    if (-not $requestedWhatIf) {
        try {
            [IO.File]::WriteAllText($ReportPath, $json, (New-Object Text.UTF8Encoding($false)))
        } catch {
            $exitCode = 2
            $report.ExitCode = 2
            $report.Error = "ReportPath write failed: $($_.Exception.Message)"
            $report.Findings += [pscustomobject]@{ Area = 'Reporting'; Check = 'ReportPath'; Status = 'FAIL'; Detail = $report.Error }
            $json = $report | ConvertTo-Json -Depth 8
        }
    }
}
if ($OutputFormat -eq 'Json') {
    Write-Output $json
} else {
    Write-Output ("RDP microphone {0} on {1}: exit {2}" -f $Role, $env:COMPUTERNAME, $exitCode)
    foreach ($finding in $findings) {
        Write-Output ("[{0}] {1}: {2}" -f $finding.Status, $finding.Check, $finding.Detail)
    }
    foreach ($change in $changes) {
        Write-Output ('CHANGE/ROLLBACK: ' + ($change | ConvertTo-Json -Compress -Depth 6))
    }
    if ($report.Error) { Write-Output ("[FAIL] {0}" -f $report.Error) }
    Write-Output ("Next: {0}" -f $report.NextStep)
}
exit $exitCode
