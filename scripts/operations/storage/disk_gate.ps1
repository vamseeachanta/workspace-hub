# Windows filesystem-drive implementation of the disk-floor exit contract.
[CmdletBinding()]
param(
    [string]$Conf = $env:DISK_GATE_CONF,
    [string[]]$Mount = @(),
    [switch]$Json
)
$ErrorActionPreference = 'Stop'
if (-not $Conf -or -not (Test-Path -LiteralPath $Conf -PathType Leaf)) {
    Write-Error 'Settings unreadable' -ErrorAction Continue
    exit 2
}
$disks = @()
try {
    foreach ($line in Get-Content -LiteralPath $Conf) {
        if ($line -match '^\s*(#|$)') { continue }
        $parts = $line.Trim() -split '\s+'
        if ($parts[0] -in @('cache', 'tmp')) { continue }
        $warn = 85.0; $block = 90.0; $floor = 0.0
        foreach ($part in $parts | Select-Object -Skip 1) {
            if ($part -notmatch '^(warn_pct|block_pct|floor_gb)=([0-9]+(?:\.[0-9]+)?)$') {
                throw 'Invalid setting'
            }
            $number = [double]::Parse($Matches[2], [cultureinfo]::InvariantCulture)
            switch ($Matches[1]) {
                warn_pct { $warn = $number }
                block_pct { $block = $number }
                floor_gb { $floor = $number }
            }
        }
        if ($warn -ge $block -or $block -gt 100) { throw 'Invalid thresholds' }
        $disks += @{ Path=$parts[0]; Warn=$warn; Block=$block; Floor=$floor }
    }
    if ($disks.Count -eq 0) { throw 'No drives configured' }
    foreach ($path in $Mount) {
        if ($path -notin $disks.Path) { throw 'Requested drive absent from settings' }
    }
} catch {
    Write-Error 'Settings unreadable or invalid' -ErrorAction Continue
    exit 2
}
$result = 0
foreach ($disk in $disks) {
    if ($Mount.Count -gt 0 -and $disk.Path -notin $Mount) { continue }
    $row = [ordered]@{mount=$disk.Path; size_kb=$null; used_kb=$null;
        free_kb=$null; used_pct=$null; inode_pct=$null; state='BLOCK'}
    $level = 4
    try {
        $name = $disk.Path -replace '[:\\/]+$', ''
        $drive = Get-PSDrive -Name $name -PSProvider FileSystem -ErrorAction Stop
        if (@($drive).Count -ne 1 -or $null -eq $drive.Used -or $null -eq $drive.Free) {
            throw 'Drive unreadable'
        }
        $used = [double]$drive.Used; $free = [double]$drive.Free
        $size = $used + $free
        if ($size -le 0 -or $used -lt 0 -or $free -lt 0) { throw 'Invalid drive sizes' }
        $pct = [math]::Ceiling(100 * $used / $size)
        $inode = $null
        # Windows exposes no inode quota through Get-PSDrive.
        if ($drive.PSObject.Properties['InodePct']) { $inode = [double]$drive.InodePct }
        $row.size_kb = [math]::Floor($size / 1KB)
        $row.used_kb = [math]::Floor($used / 1KB)
        $row.free_kb = [math]::Floor($free / 1KB)
        $row.used_pct = $pct; $row.inode_pct = $inode
        if ($pct -ge $disk.Block -or $free -lt $disk.Floor * 1GB -or
            ($null -ne $inode -and $inode -ge 95)) {
            $level = 4
        } elseif ($pct -ge $disk.Warn) { $row.state = 'WARN'; $level = 10 }
        else { $row.state = 'OK'; $level = 0 }
    } catch { $level = 4 }
    if ($level -eq 4 -or ($result -ne 4 -and $level -eq 10)) { $result = $level }
    if ($Json) { $row | ConvertTo-Json -Compress }
    else {
        $freeText = if ($null -eq $row.free_kb) { 'unknown' }
            else { ($row.free_kb / 1MB).ToString('F1', [cultureinfo]::InvariantCulture) }
        Write-Output "$($row.mount) used=$($row.used_pct)% free=$freeText GiB inodes=$($row.inode_pct)% $($row.state)"
    }
}
exit $result
