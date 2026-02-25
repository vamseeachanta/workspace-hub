# ABOUTME: Cross-platform hardware assessment script (Windows). Collects CPU, RAM, GPU, storage, motherboard, network, and OS info into structured JSON.

param(
    [string]$OutputFile = "",
    [switch]$Pretty,
    [switch]$Quiet,
    [switch]$Help
)

$SCRIPT_VERSION = "1.0.0"
$SCHEMA_VERSION = "1.0"

# ── Logging ──────────────────────────────────────────────────────────────

function Write-Log {
    param(
        [ValidateSet("Info", "Warn", "Error")]
        [string]$Level = "Info",
        [string]$Message
    )

    if ($Quiet -and $Level -ne "Error") { return }

    $color = switch ($Level) {
        "Info"  { "Cyan" }
        "Warn"  { "Yellow" }
        "Error" { "Red" }
    }

    $prefix = "[$($Level.ToUpper())]"
    Write-Host "$prefix $Message" -ForegroundColor $color
}

# ── Help ─────────────────────────────────────────────────────────────────

if ($Help) {
    $helpText = @"
Usage: hardware-assess.ps1 [OPTIONS]

Collect hardware specifications and output a unified JSON file.

Options:
  -OutputFile <path>   Override output file path
  -Pretty              Pretty-print JSON output
  -Quiet               Suppress log messages (errors still shown)
  -Help                Show this help message

Output:
  By default writes to ./hardware-assessment-<HOSTNAME>-<YYYYMMDD>.json

Examples:
  .\hardware-assess.ps1
  .\hardware-assess.ps1 -OutputFile C:\temp\hw.json -Pretty
  .\hardware-assess.ps1 -Quiet -OutputFile report.json
"@
    Write-Host $helpText
    exit 0
}

# ── CPU ──────────────────────────────────────────────────────────────────

function Get-CpuInfo {
    try {
        $ErrorActionPreference = 'SilentlyContinue'

        $processors = @(Get-CimInstance -ClassName Win32_Processor)
        if (-not $processors -or $processors.Count -eq 0) {
            Write-Log -Level Warn -Message "No CPU information found via Win32_Processor"
            return [ordered]@{
                model             = $null
                architecture      = $null
                sockets           = $null
                cores_per_socket  = $null
                total_cores       = $null
                threads_per_core  = $null
                total_threads     = $null
                max_mhz           = $null
                l3_cache          = $null
            }
        }

        $archMap = @{
            0  = "x86"
            5  = "ARM"
            9  = "x64"
            12 = "ARM64"
        }

        $first = $processors[0]
        $model = $first.Name -replace '\s+', ' '
        $architecture = if ($archMap.ContainsKey([int]$first.Architecture)) {
            $archMap[[int]$first.Architecture]
        } else {
            "Unknown ($($first.Architecture))"
        }

        $sockets = $processors.Count
        $totalCores = ($processors | Measure-Object -Property NumberOfCores -Sum).Sum
        $totalThreads = ($processors | Measure-Object -Property NumberOfLogicalProcessors -Sum).Sum
        $coresPerSocket = if ($sockets -gt 0) { [math]::Floor($totalCores / $sockets) } else { $null }
        $threadsPerCore = if ($totalCores -gt 0) { [math]::Floor($totalThreads / $totalCores) } else { $null }
        $maxMhz = [string]$first.MaxClockSpeed

        # L3 cache: try Win32_CacheMemory Level 3 first, fall back to processor L3CacheSize
        $l3Cache = $null
        try {
            $caches = @(Get-CimInstance -ClassName Win32_CacheMemory | Where-Object { $_.Level -eq 5 })
            if ($caches -and $caches.Count -gt 0) {
                $totalL3KB = ($caches | Measure-Object -Property MaxCacheSize -Sum).Sum
                if ($totalL3KB -and $totalL3KB -gt 0) {
                    if ($totalL3KB -ge 1024) {
                        $l3Cache = "$([math]::Round($totalL3KB / 1024, 1)) MB"
                    } else {
                        $l3Cache = "$totalL3KB KB"
                    }
                }
            }
        } catch {}

        if (-not $l3Cache) {
            try {
                $l3KB = ($processors | Measure-Object -Property L3CacheSize -Sum).Sum
                if ($l3KB -and $l3KB -gt 0) {
                    if ($l3KB -ge 1024) {
                        $l3Cache = "$([math]::Round($l3KB / 1024, 1)) MB"
                    } else {
                        $l3Cache = "$l3KB KB"
                    }
                }
            } catch {}
        }

        return [ordered]@{
            model             = $model
            architecture      = $architecture
            sockets           = [int]$sockets
            cores_per_socket  = [int]$coresPerSocket
            total_cores       = [int]$totalCores
            threads_per_core  = [int]$threadsPerCore
            total_threads     = [int]$totalThreads
            max_mhz           = $maxMhz
            l3_cache          = $l3Cache
        }
    } catch {
        Write-Log -Level Warn -Message "Failed to collect CPU info: $_"
        return [ordered]@{
            model = $null; architecture = $null; sockets = $null
            cores_per_socket = $null; total_cores = $null
            threads_per_core = $null; total_threads = $null
            max_mhz = $null; l3_cache = $null
        }
    }
}

# ── Memory ───────────────────────────────────────────────────────────────

function Get-MemoryInfo {
    try {
        $ErrorActionPreference = 'SilentlyContinue'

        $cs = Get-CimInstance -ClassName Win32_ComputerSystem
        $totalBytes = $cs.TotalPhysicalMemory
        $totalKB = if ($totalBytes) { [math]::Floor($totalBytes / 1024) } else { $null }
        $totalGB = if ($totalBytes) { "{0:N1}" -f ($totalBytes / 1GB) } else { $null }

        # Memory type mapping
        $memTypeMap = @{
            20 = "DDR"
            21 = "DDR2"
            22 = "DDR2 FB-DIMM"
            24 = "DDR3"
            26 = "DDR4"
            34 = "DDR5"
        }

        $memType = $null
        $memSpeed = $null

        $dimms = @(Get-CimInstance -ClassName Win32_PhysicalMemory)
        if ($dimms -and $dimms.Count -gt 0) {
            $first = $dimms[0]

            # SMBIOSMemoryType is more reliable than MemoryType
            $typeCode = $first.SMBIOSMemoryType
            if (-not $typeCode) { $typeCode = $first.MemoryType }
            if ($typeCode -and $memTypeMap.ContainsKey([int]$typeCode)) {
                $memType = $memTypeMap[[int]$typeCode]
            } elseif ($typeCode) {
                $memType = "Type $typeCode"
            }

            if ($first.Speed) {
                $memSpeed = "$($first.Speed) MHz"
            }
        }

        return [ordered]@{
            total_kb = $totalKB
            total_gb = $totalGB
            type     = $memType
            speed    = $memSpeed
        }
    } catch {
        Write-Log -Level Warn -Message "Failed to collect memory info: $_"
        return [ordered]@{
            total_kb = $null; total_gb = $null; type = $null; speed = $null
        }
    }
}

# ── GPU ──────────────────────────────────────────────────────────────────

function Get-GpuInfo {
    try {
        $ErrorActionPreference = 'SilentlyContinue'

        $controllers = @(Get-CimInstance -ClassName Win32_VideoController)
        if (-not $controllers -or $controllers.Count -eq 0) {
            Write-Log -Level Warn -Message "No GPU information found via Win32_VideoController"
            return @()
        }

        # Check for nvidia-smi availability
        $nvidiaSmiPath = $null
        $nvidiaSmiData = @{}
        try {
            $nvidiaSmiTest = Get-Command "nvidia-smi" -ErrorAction SilentlyContinue
            if ($nvidiaSmiTest) {
                $nvidiaSmiPath = $nvidiaSmiTest.Source
            } elseif (Test-Path "C:\Windows\System32\nvidia-smi.exe") {
                $nvidiaSmiPath = "C:\Windows\System32\nvidia-smi.exe"
            } elseif (Test-Path "C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe") {
                $nvidiaSmiPath = "C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe"
            }
        } catch {}

        if ($nvidiaSmiPath) {
            try {
                $smiOutput = & $nvidiaSmiPath --query-gpu=index,name,memory.total --format=csv,noheader,nounits 2>$null
                if ($smiOutput) {
                    foreach ($line in $smiOutput) {
                        $parts = $line -split ',\s*'
                        if ($parts.Count -ge 3) {
                            $gpuName = $parts[1].Trim()
                            $vramMB = $null
                            try { $vramMB = [int]$parts[2].Trim() } catch {}
                            $nvidiaSmiData[$gpuName] = $vramMB
                        }
                    }
                }
            } catch {
                Write-Log -Level Warn -Message "nvidia-smi found but query failed: $_"
            }
        }

        $gpuList = @()
        foreach ($vc in $controllers) {
            $name = $vc.Name
            $driverVersion = $vc.DriverVersion

            # PCI ID from PNPDeviceID (e.g., PCI\VEN_10DE&DEV_2684&...)
            $pciId = $null
            if ($vc.PNPDeviceID -match 'VEN_([0-9A-Fa-f]{4})&DEV_([0-9A-Fa-f]{4})') {
                $pciId = "$($Matches[1]):$($Matches[2])".ToLower()
            }

            # VRAM: try nvidia-smi first for NVIDIA GPUs, then fall back to AdapterRAM
            $vramMB = $null
            $isNvidia = $name -match 'NVIDIA|GeForce|Quadro|Tesla'

            if ($isNvidia -and $nvidiaSmiData.Count -gt 0) {
                # Try to match by name
                foreach ($smiName in $nvidiaSmiData.Keys) {
                    if ($name -like "*$smiName*" -or $smiName -like "*$name*") {
                        $vramMB = $nvidiaSmiData[$smiName]
                        break
                    }
                }
                # If no name match, use first entry for single-GPU systems
                if (-not $vramMB -and $nvidiaSmiData.Count -eq 1 -and $controllers.Count -le 2) {
                    $vramMB = $nvidiaSmiData.Values | Select-Object -First 1
                }
            }

            if (-not $vramMB -and $vc.AdapterRAM) {
                # AdapterRAM is uint32, caps at ~4GB
                $adapterRAM = [uint64]$vc.AdapterRAM
                if ($adapterRAM -gt 0) {
                    $vramMB = [int][math]::Floor($adapterRAM / 1MB)
                }
            }

            $gpuEntry = [ordered]@{
                name           = $name
                pci_id         = $pciId
                vram_mb        = $vramMB
                driver_version = $driverVersion
            }
            $gpuList += $gpuEntry
        }

        return , $gpuList
    } catch {
        Write-Log -Level Warn -Message "Failed to collect GPU info: $_"
        return @()
    }
}

# ── Storage ──────────────────────────────────────────────────────────────

function Get-StorageInfo {
    try {
        $ErrorActionPreference = 'SilentlyContinue'

        $disks = @(Get-PhysicalDisk)
        if (-not $disks -or $disks.Count -eq 0) {
            Write-Log -Level Warn -Message "No physical disks found via Get-PhysicalDisk"
            return @()
        }

        $mediaTypeMap = @{
            0 = "Unspecified"
            3 = "HDD"
            4 = "SSD"
            5 = "SCM"
        }

        $busTypeMap = @{
            1  = "SCSI"
            2  = "ATAPI"
            3  = "ATA"
            4  = "IEEE 1394"
            5  = "SSA"
            6  = "Fibre Channel"
            7  = "USB"
            8  = "RAID"
            9  = "iSCSI"
            10 = "SAS"
            11 = "SATA"
            12 = "SD"
            13 = "MMC"
            15 = "File Backed Virtual"
            16 = "Storage Spaces"
            17 = "NVMe"
        }

        $storageList = @()
        foreach ($disk in $disks) {
            $deviceId = $disk.DeviceId
            $model = $disk.FriendlyName
            $serial = $disk.SerialNumber
            if ($serial) { $serial = $serial.Trim() }

            # Size in human-readable format
            $sizeStr = $null
            if ($disk.Size) {
                $sizeBytes = [double]$disk.Size
                if ($sizeBytes -ge 1TB) {
                    $sizeStr = "{0:N2} TB" -f ($sizeBytes / 1TB)
                } elseif ($sizeBytes -ge 1GB) {
                    $sizeStr = "{0:N1} GB" -f ($sizeBytes / 1GB)
                } elseif ($sizeBytes -ge 1MB) {
                    $sizeStr = "{0:N0} MB" -f ($sizeBytes / 1MB)
                } else {
                    $sizeStr = "$sizeBytes bytes"
                }
            }

            # Media type
            $mediaCode = [int]$disk.MediaType
            $mediaType = if ($mediaTypeMap.ContainsKey($mediaCode)) {
                $mediaTypeMap[$mediaCode]
            } else {
                "Unknown"
            }

            # Bus type / transport
            $busCode = [int]$disk.BusType
            $transport = if ($busTypeMap.ContainsKey($busCode)) {
                $busTypeMap[$busCode]
            } else {
                "Unknown"
            }

            # Health status
            $healthStatus = $disk.HealthStatus

            # SMART-like data from StorageReliabilityCounter
            $tempC = $null
            $powerOnHours = $null
            try {
                $reliability = Get-StorageReliabilityCounter -PhysicalDisk $disk -ErrorAction SilentlyContinue
                if ($reliability) {
                    if ($null -ne $reliability.Temperature -and $reliability.Temperature -gt 0) {
                        $tempC = [int]$reliability.Temperature
                    }
                    if ($null -ne $reliability.PowerOnHours -and $reliability.PowerOnHours -gt 0) {
                        $powerOnHours = [int]$reliability.PowerOnHours
                    }
                }
            } catch {}

            $entry = [ordered]@{
                device    = "PhysicalDisk$deviceId"
                size      = $sizeStr
                model     = $model
                serial    = $serial
                type      = $mediaType
                transport = $transport
                smart     = [ordered]@{
                    status        = $healthStatus
                    temperature_c = $tempC
                    power_on_hours = $powerOnHours
                }
            }
            $storageList += $entry
        }

        return , $storageList
    } catch {
        Write-Log -Level Warn -Message "Failed to collect storage info: $_"
        return @()
    }
}

# ── Motherboard ──────────────────────────────────────────────────────────

function Get-MotherboardInfo {
    try {
        $ErrorActionPreference = 'SilentlyContinue'

        $board = Get-CimInstance -ClassName Win32_BaseBoard
        $bios = Get-CimInstance -ClassName Win32_BIOS

        $vendor = if ($board) { $board.Manufacturer } else { $null }
        $model = if ($board) { $board.Product } else { $null }
        $fwVersion = if ($bios) { $bios.SMBIOSBIOSVersion } else { $null }

        $fwDate = $null
        if ($bios -and $bios.ReleaseDate) {
            try {
                $fwDate = $bios.ReleaseDate.ToString("yyyy-MM-dd")
            } catch {
                $fwDate = $bios.ReleaseDate.ToString()
            }
        }

        return [ordered]@{
            vendor           = $vendor
            model            = $model
            firmware_version = $fwVersion
            firmware_date    = $fwDate
        }
    } catch {
        Write-Log -Level Warn -Message "Failed to collect motherboard info: $_"
        return [ordered]@{
            vendor = $null; model = $null
            firmware_version = $null; firmware_date = $null
        }
    }
}

# ── Network ──────────────────────────────────────────────────────────────

function Get-NetworkInfo {
    try {
        $ErrorActionPreference = 'SilentlyContinue'

        # Try to get physical adapters first; fall back to all non-virtual
        $adapters = @(Get-NetAdapter -Physical -ErrorAction SilentlyContinue)
        if (-not $adapters -or $adapters.Count -eq 0) {
            $adapters = @(Get-NetAdapter | Where-Object { $_.Virtual -eq $false })
        }
        if (-not $adapters -or $adapters.Count -eq 0) {
            $adapters = @(Get-NetAdapter)
        }

        if (-not $adapters -or $adapters.Count -eq 0) {
            Write-Log -Level Warn -Message "No network adapters found"
            return @()
        }

        $netList = @()
        foreach ($adapter in $adapters) {
            $name = $adapter.Name
            $mac = $adapter.MacAddress
            $state = $adapter.Status
            $mtu = if ($adapter.MtuSize) { [int]$adapter.MtuSize } else { $null }
            $driver = $adapter.DriverDescription

            # Parse link speed to Mbps
            $speedMbps = $null
            if ($adapter.LinkSpeed) {
                $speedStr = $adapter.LinkSpeed
                if ($speedStr -match '([\d.]+)\s*Gbps') {
                    $speedMbps = [int]([double]$Matches[1] * 1000)
                } elseif ($speedStr -match '([\d.]+)\s*Mbps') {
                    $speedMbps = [int][double]$Matches[1]
                } elseif ($speedStr -match '([\d.]+)\s*Kbps') {
                    $speedMbps = [int][math]::Floor([double]$Matches[1] / 1000)
                }
            }

            # IPv4 address
            $ipv4 = $null
            try {
                $ipAddr = Get-NetIPAddress -InterfaceIndex $adapter.InterfaceIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue |
                    Where-Object { $_.IPAddress -ne "127.0.0.1" } |
                    Select-Object -First 1
                if ($ipAddr) {
                    $ipv4 = $ipAddr.IPAddress
                }
            } catch {}

            $entry = [ordered]@{
                name       = $name
                mac        = $mac
                state      = $state
                mtu        = $mtu
                speed_mbps = $speedMbps
                ipv4       = $ipv4
                driver     = $driver
            }
            $netList += $entry
        }

        return , $netList
    } catch {
        Write-Log -Level Warn -Message "Failed to collect network info: $_"
        return @()
    }
}

# ── OS ───────────────────────────────────────────────────────────────────

function Get-OsInfo {
    try {
        $ErrorActionPreference = 'SilentlyContinue'

        $os = Get-CimInstance -ClassName Win32_OperatingSystem

        $name = if ($os) { $os.Caption } else { $null }
        $kernel = if ($os) { $os.Version } else { $null }
        $arch = if ($os) { $os.OSArchitecture } else { $null }
        $hostname = $env:COMPUTERNAME

        $uptimeSeconds = $null
        if ($os -and $os.LastBootUpTime) {
            try {
                $uptime = (Get-Date) - $os.LastBootUpTime
                $uptimeSeconds = [int][math]::Floor($uptime.TotalSeconds)
            } catch {}
        }

        return [ordered]@{
            name           = $name
            kernel         = $kernel
            architecture   = $arch
            hostname       = $hostname
            uptime_seconds = $uptimeSeconds
        }
    } catch {
        Write-Log -Level Warn -Message "Failed to collect OS info: $_"
        return [ordered]@{
            name = $null; kernel = $null; architecture = $null
            hostname = $null; uptime_seconds = $null
        }
    }
}

# ── Main ─────────────────────────────────────────────────────────────────

# Determine output file path
if (-not $OutputFile) {
    $hostname = $env:COMPUTERNAME
    if (-not $hostname) { $hostname = "unknown" }
    $datestamp = (Get-Date -Format "yyyyMMdd")
    $OutputFile = Join-Path -Path (Get-Location) -ChildPath "hardware-assessment-$hostname-$datestamp.json"
}

Write-Log -Level Info -Message "Starting hardware assessment..."
Write-Log -Level Info -Message "Output file: $OutputFile"

# Collect all sections
Write-Log -Level Info -Message "Collecting CPU information..."
$cpuData = Get-CpuInfo

Write-Log -Level Info -Message "Collecting memory information..."
$memData = Get-MemoryInfo

Write-Log -Level Info -Message "Collecting GPU information..."
$gpuData = Get-GpuInfo

Write-Log -Level Info -Message "Collecting storage information..."
$storageData = Get-StorageInfo

Write-Log -Level Info -Message "Collecting motherboard information..."
$mbData = Get-MotherboardInfo

Write-Log -Level Info -Message "Collecting network information..."
$netData = Get-NetworkInfo

Write-Log -Level Info -Message "Collecting OS information..."
$osData = Get-OsInfo

# Build top-level object
$timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

$report = [ordered]@{
    schema_version = $SCHEMA_VERSION
    script_version = $SCRIPT_VERSION
    platform       = "windows"
    timestamp      = $timestamp
    cpu            = $cpuData
    memory         = $memData
    gpu            = $gpuData
    storage        = $storageData
    motherboard    = $mbData
    network        = $netData
    os             = $osData
}

# Convert to JSON
if ($Pretty) {
    $jsonOutput = $report | ConvertTo-Json -Depth 5
} else {
    $jsonOutput = $report | ConvertTo-Json -Depth 5 -Compress
}

# Write to file with UTF-8 no-BOM encoding
try {
    $parentDir = Split-Path -Parent $OutputFile
    if ($parentDir -and -not (Test-Path $parentDir)) {
        New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
    }
    [System.IO.File]::WriteAllText($OutputFile, $jsonOutput, (New-Object System.Text.UTF8Encoding $false))
    Write-Log -Level Info -Message "Assessment complete. Output written to: $OutputFile"
} catch {
    Write-Log -Level Error -Message "Failed to write output file: $_"
    exit 1
}

# Print summary
$fileSize = (Get-Item $OutputFile).Length
$fileSizeKB = "{0:N1}" -f ($fileSize / 1024)
Write-Log -Level Info -Message "File size: $fileSizeKB KB"
Write-Log -Level Info -Message "Sections: cpu, memory, gpu, storage, motherboard, network, os"
