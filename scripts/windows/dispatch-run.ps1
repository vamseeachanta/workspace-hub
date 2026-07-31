# dispatch-run.ps1
# Durable job dispatch for a Windows fleet host, via Windows Task Scheduler.
#
# WHY: Windows OpenSSH kills the whole descendant process tree when the SSH session
# closes. Measured on a live host 2026-07-31: `cmd /c start /b` blocked the session on
# an inherited handle AND died at close; `Start-Process -WindowStyle Hidden` returned a
# PID in 1s but the process was gone and its redirect files were 0 bytes. Neither
# survives. So nothing long-running can be dispatched over plain SSH -- which nullifies
# the box's actual asset (64 cores, free AQWA seats).
#
# A Scheduled Task is the ONE mechanism proven durable here: the licensed-run agent task
# has run continuously since 2026-07-13 across many sessions. This wraps that mechanism
# in a submit/status/logs/cancel interface so a control-surface host can fire and forget.
#
# ASCII ONLY, deliberately. Windows PowerShell 5.1 reads a BOM-less .ps1 as ANSI, so any
# non-ASCII byte becomes mojibake and the parser dies with misleading errors on valid
# lines. Keep it that way (see enable-remote-exec.ps1 history).
#
# Usage:
#   dispatch-run.ps1 -Action submit -Command "<command line>" [-JobId <id>] [-WorkDir <dir>] [-Shell bash|cmd|powershell]
#   dispatch-run.ps1 -Action status  -JobId <id>
#   dispatch-run.ps1 -Action logs    -JobId <id> [-Tail <n>]
#   dispatch-run.ps1 -Action list
#   dispatch-run.ps1 -Action cancel  -JobId <id>
#   dispatch-run.ps1 -Action cleanup -JobId <id>
#
# Every action emits a single JSON object on stdout so a caller over SSH can parse it.

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('submit','status','logs','list','cancel','cleanup')]
    [string]$Action,

    [string]$Command = "",
    [string]$JobId = "",
    [string]$WorkDir = "",
    [ValidateSet('bash','cmd','powershell')]
    [string]$Shell = 'bash',
    [int]$Tail = 50
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# Task folder is namespaced so this can never collide with, or be confused for, the
# licensed-run agent's task. Nothing here touches \DeckhandLicensedRunAgent.
$TaskFolder = '\WorkspaceHubDispatch'
$Root       = Join-Path $env:LOCALAPPDATA 'workspace-hub\dispatch'

function New-JobId {
    # Caller-supplied ids are validated; generated ones are timestamp + short random.
    $stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
    $rand  = -join ((48..57) + (97..122) | Get-Random -Count 6 | ForEach-Object { [char]$_ })
    "$stamp-$rand"
}

function Assert-JobId {
    param([string]$Id)
    if ([string]::IsNullOrWhiteSpace($Id)) { throw "-JobId is required for action '$Action'" }
    # Task names and paths are built from this; refuse anything that could escape either.
    if ($Id -notmatch '^[A-Za-z0-9._-]{1,64}$') {
        throw "invalid -JobId '$Id' (allowed: letters, digits, dot, underscore, hyphen; max 64)"
    }
}

function Get-JobDir { param([string]$Id) Join-Path $Root $Id }

function Read-Status {
    param([string]$Id)
    $f = Join-Path (Get-JobDir $Id) 'status.json'
    if (-not (Test-Path $f)) { return $null }
    try { Get-Content $f -Raw | ConvertFrom-Json } catch { $null }
}

function Get-TaskName { param([string]$Id) "$TaskFolder\job-$Id" }

function Emit { param($Obj) $Obj | ConvertTo-Json -Depth 6 -Compress }

# ---------------------------------------------------------------------------- submit
if ($Action -eq 'submit') {
    if ([string]::IsNullOrWhiteSpace($Command)) { throw "-Command is required for submit" }
    if ($JobId) { Assert-JobId $JobId } else { $JobId = New-JobId }

    $dir = Get-JobDir $JobId
    if (Test-Path $dir) { throw "job '$JobId' already exists at $dir" }
    New-Item -ItemType Directory -Path $dir -Force | Out-Null

    if (-not $WorkDir) { $WorkDir = $dir }

    # Resolve the interpreter. Bare 'python' on this fleet is the Microsoft Store stub and
    # fails, so bash is the default and callers name their own interpreter explicitly.
    $gitBash = $null
    foreach ($c in @(
        "$env:LOCALAPPDATA\Programs\Git\bin\bash.exe",
        "$env:ProgramFiles\Git\bin\bash.exe",
        "${env:ProgramFiles(x86)}\Git\bin\bash.exe")) {
        if (Test-Path $c) { $gitBash = $c; break }
    }
    if ($Shell -eq 'bash' -and -not $gitBash) {
        throw "-Shell bash requested but Git Bash was not found; use -Shell cmd or -Shell powershell"
    }

    $cmdFile = Join-Path $dir 'command.txt'
    Set-Content -Path $cmdFile -Value $Command -Encoding ascii

    $outLog  = Join-Path $dir 'stdout.log'
    $errLog  = Join-Path $dir 'stderr.log'
    $statusF = Join-Path $dir 'status.json'

    # The runner is a .cmd because Task Scheduler invokes it most predictably, and because
    # it must record the exit code AFTER the payload finishes -- that recording is the
    # whole point. Without it a finished job is indistinguishable from a vanished one.
    switch ($Shell) {
        'bash'       { $payload = "`"$gitBash`" -lc `"$($Command -replace '"','\"')`"" }
        'powershell' { $payload = "powershell -NoProfile -ExecutionPolicy Bypass -Command `"$($Command -replace '"','`"')`"" }
        default      { $payload = $Command }
    }

    $runner = @"
@echo off
setlocal
cd /d "$WorkDir"
call :stamp running
$payload > "$outLog" 2> "$errLog"
set RC=%ERRORLEVEL%
call :stampdone %RC%
exit /b %RC%

:stamp
> "$statusF" echo {"job_id":"$JobId","state":"%~1","shell":"$Shell","work_dir":"$($WorkDir -replace '\\','\\')","started_at":"%DATE% %TIME%","exit_code":null}
exit /b 0

:stampdone
> "$statusF" echo {"job_id":"$JobId","state":"finished","shell":"$Shell","work_dir":"$($WorkDir -replace '\\','\\')","finished_at":"%DATE% %TIME%","exit_code":%~1}
exit /b 0
"@
    $runnerFile = Join-Path $dir 'run.cmd'
    Set-Content -Path $runnerFile -Value $runner -Encoding ascii

    # Seed a submitted status so a poll between create and first write is not a void.
    $seed = [ordered]@{
        job_id = $JobId; state = 'submitted'; shell = $Shell; work_dir = $WorkDir
        submitted_at = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
        exit_code = $null
    }
    $seed | ConvertTo-Json -Depth 4 | Set-Content -Path $statusF -Encoding ascii

    $task = Get-TaskName $JobId
    # /sc ONCE with a past-dated /st plus an immediate /run: the trigger exists only to
    # satisfy schtasks, the /run is what starts it. No /rl HIGHEST -- ordinary compute
    # does not need elevation, and requiring it would make dispatch need an admin session.
    #
    # schtasks writes "WARNING: Task may not run because the trigger start time is in the
    # past" to STDERR on success. Under $ErrorActionPreference='Stop' PowerShell promotes
    # ANY native stderr write to a terminating NativeCommandError, so a warning would kill
    # a successful submit. Drop to 'Continue' around native calls and judge them by
    # $LASTEXITCODE, which is the only reliable signal here.
    $prevEAP = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $create = & schtasks /create /tn "$task" /sc ONCE /st 00:00 /f /tr "`"$runnerFile`"" 2>&1
        $createRc = $LASTEXITCODE
        if ($createRc -ne 0) { throw "schtasks /create failed (rc=$createRc): $create" }
        $run = & schtasks /run /tn "$task" 2>&1
        $runRc = $LASTEXITCODE
        if ($runRc -ne 0) { throw "schtasks /run failed (rc=$runRc): $run" }
    } finally {
        $ErrorActionPreference = $prevEAP
    }

    Emit ([ordered]@{
        ok = $true; action = 'submit'; job_id = $JobId; task = $task
        dir = $dir; stdout = $outLog; stderr = $errLog; shell = $Shell
    })
    exit 0
}

# ---------------------------------------------------------------------------- status
if ($Action -eq 'status') {
    Assert-JobId $JobId
    $dir = Get-JobDir $JobId
    if (-not (Test-Path $dir)) { Emit ([ordered]@{ ok=$false; action='status'; job_id=$JobId; error='no such job' }); exit 2 }

    $st   = Read-Status $JobId
    $task = Get-TaskName $JobId
    $tState = 'absent'; $tResult = $null
    $t = Get-ScheduledTask -TaskPath "$TaskFolder\" -TaskName "job-$JobId" -ErrorAction SilentlyContinue
    if ($t) {
        $tState = "$($t.State)"
        $ti = $t | Get-ScheduledTaskInfo -ErrorAction SilentlyContinue
        if ($ti) { $tResult = $ti.LastTaskResult }
    }

    # The task's own LastTaskResult is reported alongside, but the runner-recorded
    # exit_code is authoritative: Task Scheduler reports its own launch result, which is
    # 0 for a successfully STARTED job whose payload later failed.
    # Null-safe size probe. Under Set-StrictMode, .Length on the $null that Get-Item
    # returns for a missing file THROWS -- and stdout.log legitimately does not exist
    # between submit and the runner's first write, which is exactly when a caller polls.
    function Get-SizeOrNull {
        param([string]$Path)
        $i = Get-Item $Path -ErrorAction SilentlyContinue
        if ($i) { $i.Length } else { $null }
    }

    Emit ([ordered]@{
        ok = $true; action='status'; job_id=$JobId
        state = if ($st -and ($st.PSObject.Properties.Name -contains 'state')) { $st.state } else { 'unknown' }
        exit_code = if ($st -and ($st.PSObject.Properties.Name -contains 'exit_code')) { $st.exit_code } else { $null }
        task_state = $tState; task_last_result = $tResult
        stdout_bytes = Get-SizeOrNull (Join-Path $dir 'stdout.log')
        stderr_bytes = Get-SizeOrNull (Join-Path $dir 'stderr.log')
    })
    exit 0
}

# ------------------------------------------------------------------------------ logs
if ($Action -eq 'logs') {
    Assert-JobId $JobId
    $dir = Get-JobDir $JobId
    if (-not (Test-Path $dir)) { Emit ([ordered]@{ ok=$false; action='logs'; job_id=$JobId; error='no such job' }); exit 2 }
    $o = Join-Path $dir 'stdout.log'; $e = Join-Path $dir 'stderr.log'
    Emit ([ordered]@{
        ok=$true; action='logs'; job_id=$JobId
        stdout = if (Test-Path $o) { (Get-Content $o -Tail $Tail) -join "`n" } else { "" }
        stderr = if (Test-Path $e) { (Get-Content $e -Tail $Tail) -join "`n" } else { "" }
    })
    exit 0
}

# ------------------------------------------------------------------------------ list
if ($Action -eq 'list') {
    $jobs = @()
    if (Test-Path $Root) {
        foreach ($d in (Get-ChildItem $Root -Directory -ErrorAction SilentlyContinue)) {
            $st = Read-Status $d.Name
            $jobs += [ordered]@{
                job_id = $d.Name
                state = if ($st) { $st.state } else { 'unknown' }
                exit_code = if ($st -and ($st.PSObject.Properties.Name -contains 'exit_code')) { $st.exit_code } else { $null }
            }
        }
    }
    Emit ([ordered]@{ ok=$true; action='list'; count=$jobs.Count; jobs=$jobs })
    exit 0
}

# ---------------------------------------------------------------------------- cancel
if ($Action -eq 'cancel') {
    Assert-JobId $JobId
    $task = Get-TaskName $JobId
    # Same native-stderr trap as submit: schtasks writes to stderr for an absent task,
    # which EAP=Stop would promote to a terminating error on an otherwise fine no-op.
    $prevEAP = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
    try { & schtasks /end /tn "$task" 2>&1 | Out-Null } finally { $ErrorActionPreference = $prevEAP }
    Emit ([ordered]@{ ok=$true; action='cancel'; job_id=$JobId; note='task ended; status.json keeps its last recorded state' })
    exit 0
}

# --------------------------------------------------------------------------- cleanup
if ($Action -eq 'cleanup') {
    Assert-JobId $JobId
    $task = Get-TaskName $JobId
    $prevEAP = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
    try { & schtasks /delete /tn "$task" /f 2>&1 | Out-Null } finally { $ErrorActionPreference = $prevEAP }
    $dir = Get-JobDir $JobId
    # Logs are deleted with the job. Fetch them BEFORE cleanup if you need them.
    if (Test-Path $dir) { Remove-Item $dir -Recurse -Force }
    Emit ([ordered]@{ ok=$true; action='cleanup'; job_id=$JobId; removed_dir=$dir })
    exit 0
}
