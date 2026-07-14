#Requires -Version 5.1
<#
.SYNOPSIS
    Pure helpers for the guarded RDP microphone audit and repair entry point.

.DESCRIPTION
    Privacy and machine policy are audit-only. The only mutation helpers are
    the selected .rdp capture repair and exact per-target consent reset/restore.
#>

Set-StrictMode -Version 2.0

function Get-RdpMicRegistryValue {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$Path, [Parameter(Mandatory)][string]$Name)
    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    try { return (Get-ItemProperty -LiteralPath $Path -Name $Name -ErrorAction Stop).$Name }
    catch { return $null }
}

function Get-RdpMicSha256 {
    [CmdletBinding()]
    param([Parameter(Mandatory)][byte[]]$Bytes)
    $sha = [Security.Cryptography.SHA256]::Create()
    try { return (($sha.ComputeHash($Bytes) | ForEach-Object { $_.ToString('x2') }) -join '') }
    finally { $sha.Dispose() }
}

function Get-RdpMicProfileDocument {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$Path)
    $resolved = (Resolve-Path -LiteralPath $Path -ErrorAction Stop).Path
    $bytes = [IO.File]::ReadAllBytes($resolved)
    $offset = 0
    if ($bytes.Length -ge 2 -and $bytes[0] -eq 0xFF -and $bytes[1] -eq 0xFE) {
        $encoding = New-Object Text.UnicodeEncoding($false, $true, $true)
        $offset = 2
        $encodingName = 'utf-16le-bom'
    } elseif ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
        $encoding = New-Object Text.UTF8Encoding($true, $true)
        $offset = 3
        $encodingName = 'utf-8-bom'
    } else {
        $encoding = New-Object Text.UTF8Encoding($false, $true)
        $encodingName = 'utf-8'
    }
    try { $text = $encoding.GetString($bytes, $offset, $bytes.Length - $offset) }
    catch { throw "Unsupported or invalid .rdp encoding: $Path" }
    $crlf = ([string][char]13) + ([string][char]10)
    $newline = if ($text.Contains($crlf)) { $crlf } else { [string][char]10 }
    [pscustomobject]@{
        Path = $resolved; Bytes = $bytes; Text = $text; Encoding = $encoding
        EncodingName = $encodingName; Newline = $newline
    }
}

function ConvertTo-RdpMicEncodedBytes {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$Text, [Parameter(Mandatory)]$Encoding)
    $body = $Encoding.GetBytes($Text)
    $preamble = $Encoding.GetPreamble()
    if ($preamble.Length -eq 0) { return $body }
    $all = New-Object byte[] ($preamble.Length + $body.Length)
    [Array]::Copy($preamble, 0, $all, 0, $preamble.Length)
    [Array]::Copy($body, 0, $all, $preamble.Length, $body.Length)
    return $all
}

function Get-RdpMicProfileAudit {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$Path)
    $doc = Get-RdpMicProfileDocument -Path $Path
    $matches = [regex]::Matches($doc.Text, '(?im)^audiocapturemode:i:(?<value>[^\r\n]*)\r?$')
    [pscustomobject]@{
        Path = $doc.Path
        Encoding = $doc.EncodingName
        CaptureValues = @($matches | ForEach-Object { $_.Groups['value'].Value })
        Ambiguous = ($matches.Count -gt 1)
        Enabled = ($matches.Count -eq 1 -and $matches[0].Groups['value'].Value -eq '1')
    }
}

function Repair-RdpMicProfile {
    [CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'Medium')]
    param([Parameter(Mandatory)][string]$Path)
    $doc = Get-RdpMicProfileDocument -Path $Path
    $linePattern = '(?im)^audiocapturemode:i:[^\r\n]*'
    $matches = [regex]::Matches($doc.Text, $linePattern)
    if ($matches.Count -gt 0) {
        $candidateText = [regex]::Replace($doc.Text, $linePattern, '')
        $candidateText = $candidateText.Insert($matches[0].Index, 'audiocapturemode:i:1')
    } else {
        $separator = if ($doc.Text.Length -eq 0 -or $doc.Text.EndsWith($doc.Newline)) { '' } else { $doc.Newline }
        $candidateText = $doc.Text + $separator + 'audiocapturemode:i:1' + $doc.Newline
    }
    if ([regex]::Matches($candidateText, '(?im)^audiocapturemode:i:1\r?$').Count -ne 1) {
        throw 'Candidate validation failed: expected exactly one audiocapturemode:i:1.'
    }
    if (-not $PSCmdlet.ShouldProcess($doc.Path, 'Back up and enable RDP microphone capture')) {
        return [pscustomobject]@{ Changed = $false; WhatIf = $true; Path = $doc.Path; BackupPath = $null }
    }
    $candidateBytes = ConvertTo-RdpMicEncodedBytes -Text $candidateText -Encoding $doc.Encoding
    $candidatePath = "$($doc.Path).candidate-$([Guid]::NewGuid().ToString('N'))"
    $backupPath = "$($doc.Path).backup-$(Get-Date -Format 'yyyyMMddHHmmssfff')"
    try {
        [IO.File]::WriteAllBytes($candidatePath, $candidateBytes)
        $candidate = Get-RdpMicProfileDocument -Path $candidatePath
        if ([regex]::Matches($candidate.Text, '(?im)^audiocapturemode:i:1\r?$').Count -ne 1) {
            throw 'Candidate re-read validation failed.'
        }
        [IO.File]::Replace($candidatePath, $doc.Path, $backupPath, $true)
        $active = Get-RdpMicProfileDocument -Path $doc.Path
        if ([regex]::Matches($active.Text, '(?im)^audiocapturemode:i:1\r?$').Count -ne 1) {
            throw 'Post-replacement validation failed; use BackupPath to recover.'
        }
        return [pscustomobject]@{
            Changed = $true; WhatIf = $false; Path = $doc.Path; BackupPath = $backupPath
            BackupSHA256 = Get-RdpMicSha256 -Bytes ([IO.File]::ReadAllBytes($backupPath))
        }
    } catch {
        if (Test-Path -LiteralPath $backupPath) {
            try { [IO.File]::Copy($backupPath, $doc.Path, $true) } catch { }
        }
        throw "Profile replacement failed. BackupPath='$backupPath'. $($_.Exception.Message)"
    } finally {
        if (Test-Path -LiteralPath $candidatePath) {
            Remove-Item -LiteralPath $candidatePath -Force -ErrorAction SilentlyContinue
        }
    }
}

function Get-RdpMicClientIdentity {
    [CmdletBinding()]
    param()
    $known = @('mstsc.exe', 'msrdc.exe', 'WindowsApp.exe')
    $rows = @()
    try {
        $rows = @(Get-CimInstance Win32_Process -ErrorAction Stop |
            Where-Object { $known -contains $_.Name } |
            Select-Object Name, ProcessId, ExecutablePath, CommandLine)
    } catch { }
    $names = @($rows | ForEach-Object { $_.Name })
    $type = if ($names -contains 'mstsc.exe') { 'mstsc' }
        elseif ($names -contains 'msrdc.exe') { 'msrdc' }
        elseif ($names -contains 'WindowsApp.exe') { 'windows_app' }
        else { 'unknown' }
    [pscustomobject]@{ Type = $type; Processes = $rows }
}

function Get-RdpMicCaptureEndpoints {
    [CmdletBinding()]
    param()
    $root = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\MMDevices\Audio\Capture'
    if (-not (Test-Path -LiteralPath $root)) { return @() }
    @(
        Get-ChildItem -LiteralPath $root -ErrorAction SilentlyContinue | ForEach-Object {
            $state = Get-RdpMicRegistryValue -Path $_.PSPath -Name 'DeviceState'
            $props = Get-ItemProperty -LiteralPath (Join-Path $_.PSPath 'Properties') -ErrorAction SilentlyContinue
            $name = $props.'{a45c254e-df1c-4efd-8020-67d146a850e0},2'
            [pscustomobject]@{
                Id = $_.PSChildName
                Name = $name
                State = $state
                Active = ($state -eq 1)
                IsRedirected = ($name -match '(?i)^Remote Audio(?: Microphone)?$')
            }
        }
    )
}

function Get-RdpMicEndpointVerdict {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][ValidateSet('Client', 'Server')][string]$Role,
        [Parameter(Mandatory)][AllowEmptyCollection()][object[]]$Endpoints
    )
    $active = @($Endpoints | Where-Object { $_.Active })
    if ($Role -eq 'Client') {
        return [pscustomobject]@{ Passed = ($active.Count -gt 0); MatchingCount = $active.Count; Requirement = 'active-local-capture' }
    }
    $remote = @($active | Where-Object { $_.IsRedirected -and $_.Name -match '(?i)^Remote Audio(?: Microphone)?$' })
    [pscustomobject]@{ Passed = ($remote.Count -gt 0); MatchingCount = $remote.Count; Requirement = 'active-redirected-remote-audio' }
}

function ConvertFrom-RdpMicEventXml {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$Xml)
    $event = [xml]$Xml
    $provider = [string]$event.Event.System.Provider.Name
    if ($provider -ne 'Microsoft-Windows-RemoteDesktopServices-RdpCoreTS') {
        return [pscustomobject]@{ Recognized = $false; State = 'Unknown'; Channel = $null; Correlation = $null }
    }
    $channelNode = @($event.Event.EventData.Data | Where-Object { $_.Name -eq 'ChannelName' } | Select-Object -First 1)
    $channel = if ($channelNode.Count) { [string]$channelNode[0].'#text' } else { $null }
    $eventId = [int]$event.Event.System.EventID
    $state = if ($eventId -eq 132 -and $channel) { 'Connected' }
        elseif ($eventId -eq 148 -and $channel) { 'Closed' }
        else { 'Observed' }
    [pscustomobject]@{
        Recognized = ($null -ne $channel -and $eventId -in 132, 148)
        RecordId = [long]$event.Event.System.EventRecordID
        TimeUtc = [string]$event.Event.System.TimeCreated.SystemTime
        EventId = $eventId
        Channel = $channel
        State = $state
        Correlation = ([string]$event.Event.System.Correlation.ActivityID).Trim('{}')
    }
}

function Get-RdpMicEventVerdict {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][object[]]$Events,
        [Parameter(Mandatory)][long]$AfterRecordId,
        [Parameter(Mandatory)][string]$TargetCorrelation,
        [string[]]$EmpiricalInputChannels = @()
    )
    $fresh = @($Events | Where-Object { [long]$_.RecordId -gt $AfterRecordId })
    $correlated = @($fresh | Where-Object {
        $_.PSObject.Properties.Name -contains 'Correlation' -and $_.Correlation -eq $TargetCorrelation
    })
    if ($fresh.Count -gt 0 -and $correlated.Count -eq 0) {
        return [pscustomobject]@{ Verdict = 'inconclusive'; Reason = 'target-session correlation unavailable or unmatched' }
    }
    $input = @($correlated | Where-Object {
        $_.State -eq 'Connected' -and $EmpiricalInputChannels -contains $_.Channel
    })
    if ($input.Count -gt 0) {
        return [pscustomobject]@{ Verdict = 'input-present-supporting-evidence'; Reason = 'empirical correlated schema' }
    }
    $playback = @($correlated | Where-Object {
        $_.State -eq 'Connected' -and $_.Channel -match '^(rdpsnd|AUDIO_PLAYBACK)'
    })
    if ($playback.Count -gt 0) {
        return [pscustomobject]@{ Verdict = 'playback-only'; Reason = 'no empirical input connect' }
    }
    [pscustomobject]@{ Verdict = 'no-evidence'; Reason = 'no correlated recognized connect event' }
}

function Export-RdpMicConsentSnapshot {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$TargetHost, [Parameter(Mandatory)][string]$StateDirectory)
    $path = 'HKCU:\Software\Microsoft\Terminal Server Client\LocalDevices'
    if (-not (Test-Path -LiteralPath $path)) { throw "Consent key does not exist: $path" }
    $key = Get-Item -LiteralPath $path -ErrorAction Stop
    $value = $key.GetValue($TargetHost, $null, 'DoNotExpandEnvironmentNames')
    if ($null -eq $value) { throw "No saved LocalDevices consent value exists for '$TargetHost'." }
    $kind = $key.GetValueKind($TargetHost).ToString()
    if (-not (Test-Path -LiteralPath $StateDirectory)) {
        New-Item -ItemType Directory -Path $StateDirectory -Force | Out-Null
    }
    $payload = [ordered]@{
        Schema = 1; RegistryPath = $path; Name = $TargetHost; Type = $kind
        Value = $value; CreatedUtc = (Get-Date).ToUniversalTime().ToString('o')
    }
    $payloadJson = $payload | ConvertTo-Json -Compress
    $utf8 = New-Object Text.UTF8Encoding($false)
    $envelope = [ordered]@{
        Payload = $payload
        SHA256 = Get-RdpMicSha256 -Bytes ($utf8.GetBytes($payloadJson))
    }
    $safeTarget = $TargetHost -replace '[^A-Za-z0-9_.-]', '_'
    $snapshot = Join-Path $StateDirectory ("rdp-consent-{0}-{1}.json" -f $safeTarget, (Get-Date -Format 'yyyyMMddHHmmssfff'))
    [IO.File]::WriteAllText($snapshot, ($envelope | ConvertTo-Json -Depth 6), $utf8)
    return $snapshot
}

function Reset-RdpMicTargetConsent {
    [CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
    param([Parameter(Mandatory)][string]$TargetHost, [Parameter(Mandatory)][string]$StateDirectory)
    $path = 'HKCU:\Software\Microsoft\Terminal Server Client\LocalDevices'
    if (-not $PSCmdlet.ShouldProcess("$path\$TargetHost", 'Snapshot and remove exact saved device-consent value')) {
        return $null
    }
    $snapshot = Export-RdpMicConsentSnapshot -TargetHost $TargetHost -StateDirectory $StateDirectory
    Remove-ItemProperty -LiteralPath $path -Name $TargetHost -ErrorAction Stop
    [pscustomobject]@{
        Changed = $true
        SnapshotPath = $snapshot
        RestoreCommand = ".\rdp-microphone.ps1 -Role Client -Repair -RestoreSnapshot '$snapshot'"
    }
}

function Restore-RdpMicConsentSnapshot {
    [CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
    param([Parameter(Mandatory)][string]$SnapshotPath)
    $envelope = Get-Content -LiteralPath $SnapshotPath -Raw -ErrorAction Stop | ConvertFrom-Json
    $allowed = 'HKCU:\Software\Microsoft\Terminal Server Client\LocalDevices'
    if ($envelope.Payload.Schema -ne 1 -or $envelope.Payload.RegistryPath -ne $allowed) {
        throw 'Snapshot schema/path is not allowlisted.'
    }
    $payloadJson = $envelope.Payload | ConvertTo-Json -Compress
    $actual = Get-RdpMicSha256 -Bytes ((New-Object Text.UTF8Encoding($false)).GetBytes($payloadJson))
    if ($actual -ne $envelope.SHA256) { throw 'Snapshot SHA256 validation failed.' }
    $target = "$($envelope.Payload.RegistryPath)\$($envelope.Payload.Name)"
    if (-not $PSCmdlet.ShouldProcess($target, 'Restore exact saved device-consent value')) { return $null }
    $key = Get-Item -LiteralPath $envelope.Payload.RegistryPath -ErrorAction Stop
    if ($null -ne $key.GetValue([string]$envelope.Payload.Name, $null, 'DoNotExpandEnvironmentNames')) {
        throw "Consent restore conflict: '$($envelope.Payload.Name)' already exists; refusing to overwrite a newer decision."
    }
    New-ItemProperty -LiteralPath $envelope.Payload.RegistryPath -Name $envelope.Payload.Name -Value $envelope.Payload.Value -PropertyType $envelope.Payload.Type -ErrorAction Stop | Out-Null
    [pscustomobject]@{ Restored = $true; Name = $envelope.Payload.Name; SnapshotPath = $SnapshotPath }
}

Export-ModuleMember -Function Get-RdpMicRegistryValue, Get-RdpMicSha256, Get-RdpMicProfileAudit, Repair-RdpMicProfile, Get-RdpMicClientIdentity, Get-RdpMicCaptureEndpoints, Get-RdpMicEndpointVerdict, ConvertFrom-RdpMicEventXml, Get-RdpMicEventVerdict, Export-RdpMicConsentSnapshot, Reset-RdpMicTargetConsent, Restore-RdpMicConsentSnapshot
