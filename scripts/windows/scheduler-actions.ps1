# Action helpers shared by the scheduler installers and their previews.
function Resolve-GitBash {
    $candidates = New-Object System.Collections.Generic.List[string]
    $gitCommand = Get-Command git -ErrorAction SilentlyContinue
    if ($gitCommand) {
        $gitRoot = Split-Path -Parent (Split-Path -Parent $gitCommand.Source)
        $candidates.Add((Join-Path $gitRoot 'bin\bash.exe'))
        $candidates.Add((Join-Path $gitRoot 'usr\bin\bash.exe'))
    }
    $candidates.Add('C:\Program Files\Git\bin\bash.exe')
    $candidates.Add('C:\Program Files\Git\usr\bin\bash.exe')
    $candidates.Add('C:\Program Files (x86)\Git\bin\bash.exe')
    $candidates.Add("$env:LOCALAPPDATA\Programs\Git\bin\bash.exe")
    foreach ($candidate in ($candidates | Select-Object -Unique)) {
        if (-not $candidate -or -not (Test-Path $candidate)) { continue }
        $uname = (& $candidate -c 'uname -s' 2>$null)
        if ($uname -match '^(MINGW|MSYS|CYGWIN)') { return $candidate }
    }
    return $null
}

function Get-TaskPowerShell {
    foreach ($name in @('powershell.exe', 'pwsh.exe', 'pwsh')) {
        $candidate = Join-Path $PSHOME $name
        if (Test-Path -LiteralPath $candidate -PathType Leaf) { return $candidate }
    }
    throw 'The running PowerShell executable could not be resolved.'
}

function New-RepoTaskDefinition {
    param(
        [Parameter(Mandatory=$true)][string]$Name,
        [Parameter(Mandatory=$true)][string]$ScriptPath,
        [string[]]$ScriptArguments = @(),
        [string]$GitBashPath = '',
        [string]$LogPattern = '',
        [switch]$PowerShell
    )
    $script = Resolve-RepoTaskScript -RelativePath $ScriptPath
    $runner = Resolve-RepoTaskScript -RelativePath 'scripts/windows/run-scheduled-task.ps1'
    $engine = if ($PowerShell) { 'PowerShell' } else { 'Bash' }
    if (-not $LogPattern) { $LogPattern = "logs/scheduler/$Name-*.log" }
    if ($LogPattern -notmatch '^logs/[a-zA-Z0-9_./-]+\*\.log$' -or
        ($LogPattern -split '/' -contains '..')) {
        throw 'Task log pattern must be a repository log with one date wildcard.'
    }
    $payload = [ordered]@{
        Name = $Name
        WorkingDirectory = $WorkspaceRoot
        ScriptPath = $script
        ScriptArguments = @($ScriptArguments)
        Engine = $engine
        GitBashPath = $GitBashPath
        LogPattern = $LogPattern
    }
    # Encode data only, never a command. This preserves spaces and apostrophes
    # across the Task Scheduler command-line parser without shell interpolation.
    $json = ConvertTo-Json -InputObject $payload -Compress -Depth 5
    $encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($json))
    [pscustomobject]@{
        Name = $Name
        Execute = Get-TaskPowerShell
        Arguments = "-NoProfile -File `"$runner`" -Definition $encoded"
        WorkingDirectory = $WorkspaceRoot
        ScriptPath = $script
        ScriptArguments = @($ScriptArguments)
        Engine = $engine
        LogPattern = $LogPattern
        LogPath = Join-Path $WorkspaceRoot $LogPattern
    }
}
