<#
.SYNOPSIS
  Agent session preflight for Windows hosts: writes a JSON capability receipt (#3973 R5).

.DESCRIPTION
  Agent sessions on Windows repeatedly rediscovered the same faults: the Microsoft
  Store python execution alias, venvs without pyvenv.cfg, cp1252 default encoding,
  WSL bash shadowing Git Bash, missing gh auth. This script probes them once and
  writes a receipt the session can read instead of rediscovering them.

  Every child process is started hidden (no console window) with a timeout.
  Secret values are never recorded; only their presence.

.PARAMETER Python
  Interpreter the session intends to use. Defaults to $env:AGENT_PYTHON, then the
  first python on PATH that is not the Store alias.

.PARAMETER OutFile
  Write the receipt here (UTF-8). Without it the receipt goes to stdout.

.PARAMETER Strict
  Exit 1 when any finding has severity "error".

.EXAMPLE
  pwsh -NoProfile -File scripts/windows/agent-preflight.ps1 -OutFile $env:TEMP\agent-preflight.json
#>
[CmdletBinding()]
param(
    [string]$Python = $env:AGENT_PYTHON,
    [string]$OutFile,
    [switch]$Strict,
    [int]$TimeoutSec = 20
)

$ErrorActionPreference = 'Stop'
$findings = New-Object System.Collections.Generic.List[object]
function Add-Finding([string]$Id, [string]$Severity, [string]$Message) {
    $findings.Add([ordered]@{ id = $Id; severity = $Severity; message = $Message })
}

function Invoke-Probe([string]$Exe, [string[]]$ArgList) {
    # Hidden, captured, time-limited. Returns @{ ok; exit; out } — never throws.
    $result = [ordered]@{ ok = $false; exit = $null; out = $null }
    if (-not $Exe) { return $result }
    try {
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = $Exe
        $psi.Arguments = ($ArgList | ForEach-Object { if ($_ -match '[\s"]') { '"' + ($_ -replace '"', '\"') + '"' } else { $_ } }) -join ' '
        $psi.UseShellExecute = $false
        $psi.CreateNoWindow = $true
        $psi.RedirectStandardOutput = $true
        $psi.RedirectStandardError = $true
        $p = [System.Diagnostics.Process]::Start($psi)
        $outTask = $p.StandardOutput.ReadToEndAsync()
        $errTask = $p.StandardError.ReadToEndAsync()
        if (-not $p.WaitForExit($TimeoutSec * 1000)) {
            try { $p.Kill() } catch { }
            $result.out = 'timeout'
            return $result
        }
        $text = ($outTask.Result + "`n" + $errTask.Result).Trim()
        $result.exit = $p.ExitCode
        $result.ok = ($p.ExitCode -eq 0)
        $result.out = ($text -split "`r?`n" | Select-Object -First 1)
    } catch {
        $result.out = $_.Exception.Message
    }
    return $result
}

function Get-AppPath([string]$Name) {
    $c = Get-Command $Name -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($c) { return $c.Source } else { return $null }
}

function Test-StoreStub([string]$Path) {
    if (-not $Path) { return $false }
    $dir = Split-Path -Parent $Path
    return ($dir -match '[\\/]Microsoft[\\/]WindowsApps$')
}

# --- python -----------------------------------------------------------------
$pathPython = Get-AppPath 'python'
$pathIsStub = Test-StoreStub $pathPython
if ($pathIsStub) {
    Add-Finding 'PYTHON_STORE_STUB' 'warn' "bare 'python' on PATH resolves to the Microsoft Store alias ($pathPython); name an interpreter explicitly"
}
$selected = $null
$selectedSource = $null
if ($Python) { $selected = $Python; $selectedSource = 'parameter-or-AGENT_PYTHON' }
elseif ($pathPython -and -not $pathIsStub) { $selected = $pathPython; $selectedSource = 'PATH' }

$py = [ordered]@{
    path_python = $pathPython
    path_python_is_store_stub = $pathIsStub
    selected = $selected
    selected_source = $selectedSource
    selected_exists = $false
    venv_cfg_present = $null
    version = $null
    preferred_encoding = $null
    pythonutf8_env = $env:PYTHONUTF8
}
if (-not $selected) {
    Add-Finding 'NO_USABLE_PYTHON' 'error' 'no interpreter selected and PATH python is missing or the Store alias; pass -Python or set AGENT_PYTHON'
} elseif (-not (Test-Path -LiteralPath $selected -PathType Leaf)) {
    Add-Finding 'PYTHON_SELECTED_MISSING' 'error' "selected interpreter does not exist: $selected"
} else {
    $py.selected_exists = $true
    $scriptsDir = Split-Path -Parent $selected
    if ((Split-Path -Leaf $scriptsDir) -ieq 'Scripts') {
        $cfg = Join-Path (Split-Path -Parent $scriptsDir) 'pyvenv.cfg'
        $py.venv_cfg_present = (Test-Path -LiteralPath $cfg)
        if (-not $py.venv_cfg_present) {
            Add-Finding 'VENV_NO_PYVENV_CFG' 'error' "venv at $(Split-Path -Parent $scriptsDir) has no pyvenv.cfg; it will not start or will start the wrong base interpreter"
        }
    }
    $v = Invoke-Probe $selected @('-c', 'import sys,locale;print(sys.version.split()[0], locale.getpreferredencoding(False))')
    if ($v.ok -and $v.out) {
        $parts = $v.out -split ' '
        $py.version = $parts[0]
        if ($parts.Count -gt 1) { $py.preferred_encoding = $parts[1] }
        if ($py.preferred_encoding -and $py.preferred_encoding -notmatch '(?i)utf-?8' -and $env:PYTHONUTF8 -ne '1') {
            Add-Finding 'PYTHON_ENCODING_NOT_UTF8' 'warn' "python default encoding is $($py.preferred_encoding); set PYTHONUTF8=1 or pass encoding='utf-8' when reading and writing files"
        }
    } elseif (-not $v.ok) {
        Add-Finding 'PYTHON_NOT_RUNNABLE' 'error' "selected interpreter did not run: $($v.out)"
    }
}

# --- shells -----------------------------------------------------------------
$bashAll = @(Get-Command bash -CommandType Application -All -ErrorAction SilentlyContinue | ForEach-Object Source)
$firstBash = if ($bashAll.Count) { $bashAll[0] } else { $null }
# Locate Git Bash from git.exe (<root>\cmd|mingw64\bin\git.exe), so per-user installs are found too.
$gitBash = $null
$gitExe = Get-AppPath 'git'
$gitRoots = @()
if ($gitExe) {
    $d = Split-Path -Parent $gitExe
    $gitRoots += (Split-Path -Parent $d), (Split-Path -Parent (Split-Path -Parent $d))
}
$gitRoots += (Join-Path $env:ProgramFiles 'Git')
foreach ($r in $gitRoots) {
    foreach ($rel in 'bin\bash.exe', 'usr\bin\bash.exe') {
        $c = Join-Path $r $rel
        if (-not $gitBash -and (Test-Path -LiteralPath $c -PathType Leaf)) { $gitBash = $c }
    }
}
$shells = [ordered]@{
    pwsh = Get-AppPath 'pwsh'
    windows_powershell = Get-AppPath 'powershell'
    bash_on_path = $bashAll
    bash_first_is_wsl = [bool]($firstBash -and $firstBash -match '(?i)\\System32\\bash\.exe$')
    git_bash = $gitBash
    claude_code_git_bash_path = $env:CLAUDE_CODE_GIT_BASH_PATH
}
if ($shells.bash_first_is_wsl) {
    Add-Finding 'WSL_BASH_SHADOWS_GIT_BASH' 'warn' "first bash on PATH is WSL ($firstBash); scripts expecting Git Bash must call it by path"
}

# --- encoding ---------------------------------------------------------------
$encoding = [ordered]@{
    console_output_codepage = [Console]::OutputEncoding.CodePage
    ansi_codepage = [System.Text.Encoding]::Default.CodePage
}

# --- git --------------------------------------------------------------------
$gitPath = Get-AppPath 'git'
$git = [ordered]@{ path = $gitPath; version = $null; core_longpaths = $null; core_symlinks = $null; core_autocrlf = $null }
if ($gitPath) {
    $git.version = (Invoke-Probe $gitPath @('--version')).out
    foreach ($k in 'longpaths', 'symlinks', 'autocrlf') {
        $r = Invoke-Probe $gitPath @('config', '--global', '--get', "core.$k")
        $git["core_$k"] = $(if ($r.ok) { $r.out } else { $null })
    }
    if ($git.core_longpaths -ne 'true') {
        Add-Finding 'GIT_LONGPATHS_OFF' 'warn' 'global core.longpaths is not true; deep checkouts fail with Filename too long'
    }
} else {
    Add-Finding 'GIT_MISSING' 'error' 'git not found on PATH'
}

# --- gh ---------------------------------------------------------------------
$ghPath = Get-AppPath 'gh'
$gh = [ordered]@{
    path = $ghPath
    version = $null
    auth_ok = $null
    auth_status_ok = $null
    gh_token_env_present = [bool]$env:GH_TOKEN
}
if ($ghPath) {
    $gh.version = (Invoke-Probe $ghPath @('--version')).out
    # `gh auth status` exits 1 when ANY stored account is invalid, even while the active
    # one (e.g. GH_TOKEN) works, so an authenticated API call decides auth_ok.
    # Outputs are deliberately not recorded.
    $gh.auth_ok = (Invoke-Probe $ghPath @('api', 'user', '-q', '.login')).ok
    $gh.auth_status_ok = (Invoke-Probe $ghPath @('auth', 'status')).ok
    if (-not $gh.auth_ok) {
        Add-Finding 'GH_NOT_AUTHENTICATED' 'warn' 'gh api user failed; issue/PR reads will 401 (or the network is unreachable)'
    } elseif (-not $gh.auth_status_ok) {
        Add-Finding 'GH_STALE_STORED_ACCOUNT' 'info' "the active gh account works, but another stored account is invalid, so 'gh auth status' exits 1; do not read that exit code as unauthenticated"
    }
} else {
    Add-Finding 'GH_MISSING' 'warn' 'gh not found on PATH'
}

# --- agent CLIs ---------------------------------------------------------------
$clis = [ordered]@{}
foreach ($name in 'claude', 'codex') {
    $p = Get-Command $name -ErrorAction SilentlyContinue | Select-Object -First 1
    $clis[$name] = [ordered]@{ path = $(if ($p) { $p.Source } else { $null }); version = $null }
    if ($p -and $p.CommandType -eq 'Application') {
        $clis[$name].version = (Invoke-Probe $p.Source @('--version')).out
    }
}

$receipt = [ordered]@{
    schema = 'agent-preflight/1'
    generated_at = (Get-Date).ToUniversalTime().ToString('o')
    host_label = $env:AGENT_HOST_LABEL
    powershell_version = $PSVersionTable.PSVersion.ToString()
    python = $py
    encoding = $encoding
    shells = $shells
    git = $git
    gh = $gh
    clis = $clis
    findings = $findings.ToArray()   # @($list) inside an [ordered] literal throws "Argument types do not match"
}
$json = $receipt | ConvertTo-Json -Depth 6
if ($OutFile) {
    [System.IO.File]::WriteAllText($OutFile, $json + "`n", (New-Object System.Text.UTF8Encoding($false)))
    $errs = @($findings | Where-Object { $_.severity -eq 'error' }).Count
    $warns = @($findings | Where-Object { $_.severity -eq 'warn' }).Count
    Write-Output "agent-preflight: $errs error(s), $warns warning(s) -> $OutFile"
} else {
    Write-Output $json
}
if ($Strict -and @($findings | Where-Object { $_.severity -eq 'error' }).Count -gt 0) { exit 1 }
exit 0
