# YAML task readers shared by the Windows scheduler installer.
function Get-ScheduleTaskBlock {
    param([Parameter(Mandatory=$true)][string]$TaskId)
    $schedulePath = Join-Path $WorkspaceRoot "config\scheduled-tasks\schedule-tasks.yaml"
    if (-not (Test-Path $schedulePath)) { throw "Schedule source not found: $schedulePath" }
    $lines = Get-Content $schedulePath
    $start = -1
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match ("^\s*-\s+id:\s+{0}\s*$" -f [regex]::Escape($TaskId))) {
            $start = $i
            break
        }
    }
    if ($start -lt 0) { throw "Task '$TaskId' not found in $schedulePath" }
    $block = New-Object System.Collections.Generic.List[string]
    for ($i = $start; $i -lt $lines.Count; $i++) {
        if ($i -gt $start -and $lines[$i] -match "^\s*-\s+id:\s+") { break }
        $block.Add($lines[$i])
    }
    return ,$block.ToArray()
}

function Get-YamlScalar {
    param([string[]]$Block, [Parameter(Mandatory=$true)][string]$Name)
    $pattern = "^\s+{0}:\s*(.+?)\s*$" -f [regex]::Escape($Name)
    foreach ($line in $Block) {
        if ($line -match $pattern) {
            $value = $Matches[1].Trim()
            if (($value.StartsWith('"') -and $value.EndsWith('"')) -or
                ($value.StartsWith("'") -and $value.EndsWith("'"))) {
                $value = $value.Substring(1, $value.Length - 2)
            }
            return $value
        }
    }
    throw "Field '$Name' not found in YAML task block"
}

function Get-YamlInlineList {
    param([string[]]$Block, [Parameter(Mandatory=$true)][string]$Name)
    $pattern = "^\s+{0}:\s*\[(.+?)\]\s*$" -f [regex]::Escape($Name)
    foreach ($line in $Block) {
        if ($line -match $pattern) {
            return @($Matches[1].Split(',') | ForEach-Object { $_.Trim() } | Where-Object { $_ })
        }
    }
    throw "Inline list '$Name' not found in YAML task block"
}

function Get-YamlOptionalScalar {
    param([string[]]$Block, [Parameter(Mandatory=$true)][string]$Name)
    try { return Get-YamlScalar -Block $Block -Name $Name } catch { return $null }
}

function Get-EqualityReportTask {
    $block = Get-ScheduleTaskBlock -TaskId 'equality-report'
    $label = Get-YamlScalar -Block $block -Name 'label'
    $description = Get-YamlScalar -Block $block -Name 'description'
    if ($description -match '^[>|]') { $description = $label }
    [pscustomobject]@{
        Id = 'equality-report'; Label = $label
        Schedule = Get-YamlScalar -Block $block -Name 'schedule'
        Machines = Get-YamlInlineList -Block $block -Name 'machines'
        Description = $description
    }
}

function Get-ConfiguredTask {
    param([Parameter(Mandatory=$true)][string]$TaskId)
    $block = Get-ScheduleTaskBlock -TaskId $TaskId
    $label = Get-YamlScalar -Block $block -Name 'label'
    $description = Get-YamlScalar -Block $block -Name 'description'
    if ($description -match '^[>|]') { $description = $label }
    [pscustomobject]@{
        Id = $TaskId; Label = $label
        Schedule = Get-YamlScalar -Block $block -Name 'schedule'
        Machines = Get-YamlInlineList -Block $block -Name 'machines'
        Description = $description
        WindowsScript = Get-YamlOptionalScalar -Block $block -Name 'windows_script'
    }
}

function Resolve-RepoTaskScript {
    param([Parameter(Mandatory=$true)][string]$RelativePath)
    if ([IO.Path]::IsPathRooted($RelativePath) -or
        ($RelativePath -split '[\\/]' | Where-Object { $_ -eq '..' })) {
        throw "Unsafe repo-relative Windows task script: $RelativePath"
    }
    $root = [IO.Path]::GetFullPath($WorkspaceRoot).TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
    $full = [IO.Path]::GetFullPath((Join-Path $WorkspaceRoot $RelativePath))
    if (-not $full.StartsWith($root, [StringComparison]::OrdinalIgnoreCase) -or
        -not (Test-Path -LiteralPath $full -PathType Leaf)) {
        throw "Windows task script is missing or escapes the workspace: $RelativePath"
    }
    return $RelativePath
}
