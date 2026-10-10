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
    # Messages embed paths and probe text that can come from the environment.
    $findings.Add([ordered]@{ id = $Id; severity = $Severity; message = (Protect-Text $Message) })
}

# Shape patterns cannot list every token format, so the values of secret-named environment
# variables are also redacted exactly, raw and in their JSON-escaped form.
$secretEnvValues = @(Get-ChildItem Env: | Where-Object {
        $_.Name -match '(?i)(TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL|API_?KEY|ACCESS_?KEY|PRIVATE_?KEY|(^|_)PAT$|AUTH)' -and
        $_.Value -and $_.Value.Length -ge 8 } | ForEach-Object { $_.Value } | Select-Object -Unique |
    Sort-Object -Property Length -Descending)

function Hide-Secrets([string]$Text) {
    if ($null -eq $Text) { return $null }
    $t = $Text -replace '(?i)(gh[pousr]_[A-Za-z0-9]{8,}|github_pat_[A-Za-z0-9_]{8,}|\bhf_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_\-]{8,}|xox[abpr]-[A-Za-z0-9\-]{8,}|AKIA[0-9A-Z]{12,}|eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-\.]+)', '[REDACTED]'
    foreach ($v in $secretEnvValues) {
        $escaped = ConvertTo-Json -InputObject $v -Compress
        $t = $t.Replace($v, '[REDACTED]').Replace($escaped.Substring(1, $escaped.Length - 2), '[REDACTED]')
    }
    return $t
}

function Get-GhFailureLayer([string]$Text) {
    # Name the layer that failed; only a credential rejection means "not authenticated".
    if ($Text -match '(?i)HTTP 401|Bad credentials|gh auth login|not logged in|authentication (failed|required)') { return 'auth' }
    if ($Text -match '(?i)no such host|could not resolve|dial tcp|connection (refused|reset|timed out)|i/o timeout|network is unreachable|TLS handshake|proxyconnect|error connecting to') { return 'network' }
    if ($Text -match '(?i)rate limit') { return 'rate-limit' }
    return 'unknown'
}

function Protect-Text([string]$Text) {
    # Recorded strings come from external programs; strip anything token-shaped and cap the length.
    # The serialized receipt is filtered again as a whole (paths and env-derived fields included).
    $t = Hide-Secrets $Text
    if ($t -and $t.Length -gt 400) { $t = $t.Substring(0, 400) }
    return $t
}

function Stop-Tree($Proc) {
    # Kill the whole tree (a .cmd shim's node child would otherwise outlive it).
    # Kill($true) needs .NET Core 3+ (pwsh 7); Windows PowerShell 5.1 falls back to taskkill.
    try { $Proc.Kill($true) } catch { try { & taskkill.exe /T /F /PID $Proc.Id 2>&1 | Out-Null } catch { } }
}

function Invoke-Probe([string]$Exe, [string[]]$ArgList) {
    # Hidden, captured, bounded by one deadline covering both exit and stream collection
    # (a detached child can hold the pipes open after the parent exits).
    # Returns @{ ok; exit; out; text; failure } where out is the first line, text the redacted, capped
    # combined output (for classification, not for the receipt), and failure is $null, 'launch' or 'timeout'.
    # Never throws. ArgList must be fixed literal arguments: quoting covers spaces and quotes, not every CRT edge case.
    $result = [ordered]@{ ok = $false; exit = $null; out = $null; text = $null; failure = $null }
    if (-not $Exe) { $result.failure = 'launch'; return $result }
    $p = $null
    try {
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = $Exe
        $psi.Arguments = ($ArgList | ForEach-Object { if ($_ -match '[\s"]') { '"' + ($_ -replace '"', '\"') + '"' } else { $_ } }) -join ' '
        $psi.UseShellExecute = $false
        $psi.CreateNoWindow = $true
        $psi.RedirectStandardOutput = $true
        $psi.RedirectStandardError = $true
        try { $p = [System.Diagnostics.Process]::Start($psi) } catch { $result.failure = 'launch'; return $result }
        $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSec)
        $outTask = $p.StandardOutput.ReadToEndAsync()
        $errTask = $p.StandardError.ReadToEndAsync()
        $exited = $p.WaitForExit($TimeoutSec * 1000)
        $left = [int][Math]::Max(0, ($deadline - [DateTime]::UtcNow).TotalMilliseconds)
        $drained = $exited -and [System.Threading.Tasks.Task]::WaitAll(@($outTask, $errTask), $left)
        if (-not $drained) {
            Stop-Tree $p
            $result.failure = 'timeout'
            return $result
        }
        $text = ($outTask.Result + "`n" + $errTask.Result).Trim()
        $result.exit = $p.ExitCode
        $result.ok = ($p.ExitCode -eq 0)
        $first = ($text -split "`r?`n" | Select-Object -First 1)
        $result.out = $(if ($first) { Protect-Text $first } else { $null })
        $result.text = Protect-Text $text
    } catch {
        $result.failure = 'launch'
    } finally {
        if ($p) { $p.Dispose() }
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
$pathCandidates = @(Get-Command python -CommandType Application -All -ErrorAction SilentlyContinue | ForEach-Object Source)
$pathPython = if ($pathCandidates.Count) { $pathCandidates[0] } else { $null }
$pathIsStub = Test-StoreStub $pathPython
if ($pathIsStub) {
    Add-Finding 'PYTHON_STORE_STUB' 'warn' "bare 'python' on PATH resolves to the Microsoft Store alias ($pathPython); name an interpreter explicitly"
}
$selected = $null
$selectedSource = $null
if ($Python) { $selected = $Python; $selectedSource = 'parameter-or-AGENT_PYTHON' }
else {
    $firstReal = $pathCandidates | Where-Object { -not (Test-StoreStub $_) } | Select-Object -First 1
    if ($firstReal) { $selected = $firstReal; $selectedSource = 'PATH (first non-alias)' }
}

$py = [ordered]@{
    path_python = $pathPython
    path_python_is_store_stub = $pathIsStub
    selected = $selected
    selected_source = $selectedSource
    selected_exists = $false
    venv_cfg_present = $null
    version = $null
    preferred_encoding = $null
    pythonutf8_env = Protect-Text $env:PYTHONUTF8
}
if (-not $selected) {
    Add-Finding 'NO_USABLE_PYTHON' 'error' 'no interpreter selected and PATH python is missing or the Store alias; pass -Python or set AGENT_PYTHON'
} elseif (-not (Test-Path -LiteralPath $selected -PathType Leaf)) {
    Add-Finding 'PYTHON_SELECTED_MISSING' 'error' "selected interpreter does not exist: $selected"
} elseif (Test-StoreStub $selected) {
    Add-Finding 'PYTHON_SELECTED_IS_STORE_STUB' 'error' "selected interpreter is the Microsoft Store alias: $selected"
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
    } elseif ($v.ok) {
        Add-Finding 'PYTHON_PROBE_EMPTY' 'error' 'selected interpreter exited 0 but printed no version; it is not a working python'
    } else {
        $why = $(if ($v.failure) { $v.failure } else { "exit $($v.exit)" })
        Add-Finding 'PYTHON_NOT_RUNNABLE' 'error' "selected interpreter did not run ($why)"
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
    api_failure_layer = $null
    gh_token_env_present = [bool]$env:GH_TOKEN
}
if ($ghPath) {
    $gh.version = (Invoke-Probe $ghPath @('--version')).out
    # `gh auth status` exits 1 when ANY stored account is invalid, even while the active
    # one (e.g. GH_TOKEN) works, so an authenticated API call decides auth_ok.
    # Outputs are deliberately not recorded; a failed call is classified by layer, and only
    # a credential rejection sets auth_ok to false.
    $api = Invoke-Probe $ghPath @('api', 'user', '-q', '.login')
    $gh.auth_ok = $(if ($api.ok) { $true } else { $null })
    $status = Invoke-Probe $ghPath @('auth', 'status')
    $gh.auth_status_ok = $(if ($status.failure) { $null } else { $status.ok })
    if ($api.failure) {
        $gh.api_failure_layer = $api.failure
        Add-Finding 'GH_PROBE_FAILED' 'warn' "gh api user could not be completed ($($api.failure)); authentication is not established"
    } elseif (-not $api.ok) {
        $gh.api_failure_layer = Get-GhFailureLayer $api.text
        switch ($gh.api_failure_layer) {
            'auth' {
                $gh.auth_ok = $false
                Add-Finding 'GH_NOT_AUTHENTICATED' 'warn' 'gh api user was rejected for its credentials; issue/PR reads will 401'
            }
            'network' { Add-Finding 'GH_NETWORK_UNREACHABLE' 'warn' 'gh api user could not reach GitHub; authentication is not established either way' }
            'rate-limit' { Add-Finding 'GH_RATE_LIMITED' 'warn' 'gh api user was rate-limited; authentication is not established either way' }
            default { Add-Finding 'GH_API_FAILED' 'warn' "gh api user failed (exit $($api.exit)) for an unclassified reason; authentication is not established either way" }
        }
    } elseif ($status.failure) {
        Add-Finding 'GH_STATUS_PROBE_FAILED' 'info' "gh auth status could not be completed ($($status.failure)); the active account works"
    } elseif (-not $gh.auth_status_ok) {
        Add-Finding 'GH_STALE_STORED_ACCOUNT' 'info' "the active gh account works, but another stored account is invalid, so 'gh auth status' exits 1; do not read that exit code as unauthenticated"
    }
} else {
    Add-Finding 'GH_MISSING' 'warn' 'gh not found on PATH'
}

# --- agent CLIs ---------------------------------------------------------------
$clis = [ordered]@{}
foreach ($name in 'claude', 'codex') {
    # Application only: npm drops a .ps1 shim beside the .cmd, and the shim must not hide it.
    $p = Get-AppPath $name
    $clis[$name] = [ordered]@{ path = $p; version = $null; probe_failure = $null }
    if ($p) {
        $r = Invoke-Probe $p @('--version')
        $clis[$name].version = $r.out
        $clis[$name].probe_failure = $r.failure
    }
}

$receipt = [ordered]@{
    schema = 'agent-preflight/1'
    generated_at = (Get-Date).ToUniversalTime().ToString('o')
    host_label = Protect-Text $env:AGENT_HOST_LABEL
    powershell_version = $PSVersionTable.PSVersion.ToString()
    python = $py
    encoding = $encoding
    shells = $shells
    git = $git
    gh = $gh
    clis = $clis
    findings = $findings.ToArray()   # @($list) inside an [ordered] literal throws "Argument types do not match"
}
$json = Hide-Secrets ($receipt | ConvertTo-Json -Depth 6)
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
