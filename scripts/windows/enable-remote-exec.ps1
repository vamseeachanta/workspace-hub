# enable-remote-exec.ps1
# Audit-first provisioning of an inbound SSH channel on a Windows fleet host (#3721).
#
# WHY: Windows hosts sit in `manual_hosts` in config/fleet-ssh-hosts.yml, so fleet
# automation cannot reach them and their state drifts silently -- the 2026-07-30 fleet
# sweep covered 3 of 5 machines, and one Windows host's equality evidence was 11.8 days
# stale before anyone noticed. This script closes the reachability half of that gap.
#
# AUDIT-FIRST (same posture as rdp-microphone.ps1): the default run MUTATES NOTHING.
# It reports identity, SSH state, firewall exposure, and the poller's condition, and
# writes an evidence JSON. Pass -Apply to actually provision. Read the audit output
# before applying -- one of the two Windows hosts already has a working SSH service, and
# which physical machine each fleet token denotes is still being settled (deckhand#579,
# deckhand#581), so this script reports identity rather than assuming it.
#
# IDEMPOTENT: every apply step is a no-op when already in the desired state.
#
# Usage (run in an ELEVATED PowerShell -- provisioning needs admin):
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\enable-remote-exec.ps1
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\enable-remote-exec.ps1 -Apply -PublicKey "ssh-ed25519 AAAA... vamsee@ace-linux-1"
#
# The audit run does NOT require admin and is safe to run first as a normal user.

[CmdletBinding()]
param(
    # Provision. Without this the script only reports.
    [switch]$Apply,

    # The operator public key to authorize. Required with -Apply unless the key is
    # already present. Accepts the full "ssh-ed25519 AAAA... comment" line.
    [string]$PublicKey = "",

    # Where to write the evidence JSON. Default: the repo's local state dir.
    [string]$EvidenceOut = "",

    # Restrict the inbound firewall rule to the tailnet CGNAT range. Set to the empty
    # string to skip scoping (NOT recommended -- an unscoped rule exposes 22 on every
    # network the host joins, including untrusted ones).
    [string]$AllowedRemoteAddress = "100.64.0.0/10"
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$script:Findings = [ordered]@{}
$script:Actions  = New-Object System.Collections.Generic.List[string]
$script:Problems = New-Object System.Collections.Generic.List[string]

function Write-Section { param([string]$Text) Write-Host "`n=== $Text ===" -ForegroundColor Cyan }
function Write-Ok      { param([string]$Text) Write-Host "  [ok]   $Text" -ForegroundColor Green }
function Write-Gap     { param([string]$Text) Write-Host "  [gap]  $Text" -ForegroundColor Yellow; $script:Problems.Add($Text) }
function Write-Act     { param([string]$Text) Write-Host "  [act]  $Text" -ForegroundColor Magenta; $script:Actions.Add($Text) }
function Write-Info    { param([string]$Text) Write-Host "  [info] $Text" }

function Test-Elevated {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    (New-Object Security.Principal.WindowsPrincipal($id)).IsInRole(
        [Security.Principal.WindowsBuiltinRole]::Administrator)
}

# -----------------------------------------------------------------------------
# 1. Identity -- report it, never assume it.
#    deckhand#579/#581 are still settling which physical machine each fleet token
#    denotes; an alias was bound to a retired machine for ~18 days undetected. So the
#    first job of this script is to state, from the box itself, who this actually is.
# -----------------------------------------------------------------------------
Write-Section "Identity"
$hostName = $env:COMPUTERNAME
$Findings.hostname = $hostName.ToLower()
Write-Info "hostname: $hostName"

$ts = Get-Command tailscale.exe -ErrorAction SilentlyContinue
if ($ts) {
    try {
        $tsJson = & $ts.Source status --json 2>$null | ConvertFrom-Json
        $Findings.tailnet_node = $tsJson.Self.HostName
        $Findings.tailnet_addrs = @($tsJson.Self.TailscaleIPs)
        $Findings.tailnet_online = [bool]$tsJson.Self.Online
        Write-Info "tailnet node: $($tsJson.Self.HostName)  online=$($tsJson.Self.Online)"
        Write-Info "tailnet addr: $($tsJson.Self.TailscaleIPs -join ', ')"
    } catch {
        Write-Gap "tailscale present but 'status --json' failed: $($_.Exception.Message)"
        $Findings.tailnet_node = $null
    }
} else {
    Write-Gap "tailscale.exe not found -- this host has no private transport"
    $Findings.tailnet_node = $null
}

# -----------------------------------------------------------------------------
# 2. OpenSSH Server capability + service
# -----------------------------------------------------------------------------
Write-Section "OpenSSH Server"
$cap = Get-WindowsCapability -Online -Name 'OpenSSH.Server*' -ErrorAction SilentlyContinue |
       Select-Object -First 1
$Findings.openssh_capability = if ($cap) { "$($cap.State)" } else { 'unavailable' }
if ($cap) { Write-Info "capability OpenSSH.Server: $($cap.State)" }
else      { Write-Gap  "OpenSSH.Server capability not enumerable on this Windows build" }

$svc = Get-Service -Name sshd -ErrorAction SilentlyContinue
$Findings.sshd_status     = if ($svc) { "$($svc.Status)" } else { 'absent' }
$Findings.sshd_start_type = if ($svc) { "$($svc.StartType)" } else { $null }
if ($svc) {
    Write-Info "sshd service: $($svc.Status), start=$($svc.StartType)"
    if ($svc.Status -ne 'Running')   { Write-Gap "sshd is not running" }
    if ($svc.StartType -ne 'Automatic') { Write-Gap "sshd start type is $($svc.StartType), not Automatic -- it will not survive reboot" }
} else {
    Write-Gap "sshd service is absent -- OpenSSH Server is not installed"
}

if ($Apply) {
    if (-not (Test-Elevated)) { throw "-Apply requires an ELEVATED PowerShell (Run as administrator)." }
    if ($cap -and $cap.State -ne 'Installed') {
        Write-Act "installing OpenSSH.Server capability"
        Add-WindowsCapability -Online -Name $cap.Name | Out-Null
        $svc = Get-Service -Name sshd -ErrorAction SilentlyContinue
    }
    if ($svc) {
        if ($svc.StartType -ne 'Automatic') {
            Write-Act "setting sshd start type to Automatic"
            Set-Service -Name sshd -StartupType Automatic
        }
        if ($svc.Status -ne 'Running') {
            Write-Act "starting sshd"
            Start-Service sshd
        }
    }
}

# -----------------------------------------------------------------------------
# 3. authorized_keys -- the Windows ACL trap
#    Administrators do NOT use %USERPROFILE%\.ssh\authorized_keys. sshd reads
#    %ProgramData%\ssh\administrators_authorized_keys for any account in the local
#    Administrators group, and REFUSES it unless the file is owned by Administrators
#    or SYSTEM with no other write access. Getting this wrong produces auth failures
#    that look like bad keys but are permission errors.
# -----------------------------------------------------------------------------
Write-Section "Authorized keys"
$isAdminUser = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
               ).IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)
$adminKeyPath = Join-Path $env:ProgramData 'ssh\administrators_authorized_keys'
$userKeyPath  = Join-Path $env:USERPROFILE '.ssh\authorized_keys'
$targetKeyPath = if ($isAdminUser) { $adminKeyPath } else { $userKeyPath }

$Findings.current_user       = "$env:USERNAME"
$Findings.current_user_admin = $isAdminUser
$Findings.authorized_keys_path = $targetKeyPath
Write-Info "current user: $env:USERNAME (admin=$isAdminUser)"
Write-Info "sshd will read: $targetKeyPath"

$keyPresent = $false
if (Test-Path $targetKeyPath) {
    $existing = Get-Content $targetKeyPath -ErrorAction SilentlyContinue
    $Findings.authorized_keys_count = @($existing | Where-Object { $_ -match '\S' }).Count
    Write-Info "authorized_keys entries: $($Findings.authorized_keys_count)"
    if ($PublicKey -and ($existing -join "`n") -match [regex]::Escape($PublicKey.Split(' ')[1])) {
        $keyPresent = $true; Write-Ok "the supplied key is already authorized"
    }
} else {
    $Findings.authorized_keys_count = 0
    Write-Gap "no authorized_keys file at $targetKeyPath"
}

if ($Apply -and $PublicKey -and -not $keyPresent) {
    $dir = Split-Path $targetKeyPath -Parent
    if (-not (Test-Path $dir)) { Write-Act "creating $dir"; New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    Write-Act "appending public key to $targetKeyPath"
    Add-Content -Path $targetKeyPath -Value $PublicKey -Encoding ascii
    if ($isAdminUser) {
        # Required ACL: Administrators + SYSTEM only. Any other writable principal and
        # sshd silently ignores the file.
        Write-Act "locking ACL on $targetKeyPath to Administrators + SYSTEM"
        icacls.exe $targetKeyPath /inheritance:r /grant "Administrators:F" /grant "SYSTEM:F" | Out-Null
    }
} elseif ($Apply -and -not $PublicKey -and -not $keyPresent) {
    Write-Gap "-Apply given without -PublicKey and no key is present -- key auth will not work"
}

# -----------------------------------------------------------------------------
# 4. Firewall -- private transport only, never public
# -----------------------------------------------------------------------------
Write-Section "Firewall"
$ruleName = 'fleet-ssh-inbound-22'
$rule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
$Findings.firewall_rule = if ($rule) { "$($rule.Enabled)/$($rule.Profile)" } else { 'absent' }
if ($rule) {
    Write-Info "rule '$ruleName': enabled=$($rule.Enabled) profile=$($rule.Profile)"
} else {
    Write-Gap "no '$ruleName' rule -- inbound 22 may be blocked, or allowed by a broader rule"
}

# Report any OTHER rule already opening 22 -- an unscoped one is a real exposure.
$other = Get-NetFirewallRule -Direction Inbound -Enabled True -ErrorAction SilentlyContinue |
    Where-Object { $_.DisplayName -ne $ruleName } |
    Where-Object {
        try { ($_ | Get-NetFirewallPortFilter -ErrorAction SilentlyContinue).LocalPort -contains '22' }
        catch { $false }
    } | Select-Object -ExpandProperty DisplayName -First 5
if ($other) {
    $Findings.other_port22_rules = @($other)
    Write-Gap "other enabled inbound rules already open 22: $($other -join '; ') -- review for public exposure"
}

if ($Apply -and -not $rule) {
    Write-Act "creating scoped inbound rule '$ruleName' (RemoteAddress=$AllowedRemoteAddress)"
    $p = @{ DisplayName=$ruleName; Direction='Inbound'; Action='Allow'; Protocol='TCP'; LocalPort=22 }
    if ($AllowedRemoteAddress) { $p.RemoteAddress = $AllowedRemoteAddress }
    New-NetFirewallRule @p | Out-Null
}

# -----------------------------------------------------------------------------
# 5. Default shell -- non-interactive exit codes are what the fleet helpers branch on
#    A wrong default shell can return correct stdout while losing the exit code, which
#    reads as success. #3721's definition of done requires this be verified, not assumed.
# -----------------------------------------------------------------------------
Write-Section "Default shell"
$shellKey = 'HKLM:\SOFTWARE\OpenSSH'
# Set-StrictMode makes a missing property THROW rather than yield $null, so probe the
# property list first. Verified on a live host 2026-07-31: the naive
# (Get-ItemProperty ...).DefaultShell form aborts the script when DefaultShell is unset,
# which is exactly the case this section exists to detect.
$curShell = $null
$shellProps = Get-ItemProperty -Path $shellKey -ErrorAction SilentlyContinue
if ($shellProps -and ($shellProps.PSObject.Properties.Name -contains 'DefaultShell')) {
    $curShell = $shellProps.DefaultShell
}
$Findings.default_shell = $curShell
if ($curShell) { Write-Info "DefaultShell: $curShell" }
else           { Write-Info "DefaultShell unset (sshd default: cmd.exe)" }

# Locate Git Bash. It ships with Git for Windows but is NOT on PATH, so `where bash`
# finds nothing even though it is installed.
$gitBash = $null
foreach ($c in @(
    "$env:LOCALAPPDATA\Programs\Git\bin\bash.exe",
    "$env:ProgramFiles\Git\bin\bash.exe",
    "${env:ProgramFiles(x86)}\Git\bin\bash.exe")) {
    if (Test-Path $c) { $gitBash = $c; break }
}
$Findings.git_bash = $gitBash

# Why this matters more than it looks. With cmd.exe as DefaultShell, a POSIX command
# sent over SSH does not fail -- it MIS-EXECUTES AND RETURNS 0. Measured on a live host
# 2026-07-31: `ssh <host> 'echo A; echo B'` printed "A; echo B" and exited 0. Every
# fleet guard branches on exit status, so that is a silent wrong answer, not an error.
# Routing through Git Bash restores POSIX separators, && chaining, /d/... MSYS paths and
# exit-code propagation (all verified on the same host).
if (-not $curShell) {
    if ($gitBash) {
        Write-Gap "DefaultShell unset -> sshd serves cmd.exe; POSIX commands will mis-execute and still exit 0"
        Write-Info "Git Bash available for use as DefaultShell: $gitBash"
    } else {
        Write-Gap "DefaultShell unset AND no Git Bash found -- remote POSIX execution cannot be made equivalent here"
    }
}

if ($Apply -and -not $curShell -and $gitBash) {
    Write-Act "setting DefaultShell to Git Bash so remote POSIX commands behave"
    if (-not (Test-Path $shellKey)) { New-Item -Path $shellKey -Force | Out-Null }
    New-ItemProperty -Path $shellKey -Name DefaultShell -Value $gitBash -PropertyType String -Force | Out-Null
    if ((Get-Service sshd -ErrorAction SilentlyContinue).Status -eq 'Running') {
        Write-Act "restarting sshd to pick up DefaultShell"
        Restart-Service sshd
    }
}

# -----------------------------------------------------------------------------
# 6. Licensed-run poller -- report only. Whether it SHOULD run here is deckhand#579's
#    call (one Windows host was reclassified out of the licensed lane on 2026-07-30),
#    so this script never starts or stops it.
# -----------------------------------------------------------------------------
Write-Section "Licensed-run poller (report only)"
$tasks = Get-ScheduledTask -ErrorAction SilentlyContinue |
    Where-Object { $_.TaskName -match 'licensed|deckhand|agent' }
if ($tasks) {
    $Findings.scheduled_tasks = @($tasks | ForEach-Object {
        $i = $_ | Get-ScheduledTaskInfo -ErrorAction SilentlyContinue
        [ordered]@{ name=$_.TaskName; state="$($_.State)"; last_run="$($i.LastRunTime)"; last_result=$i.LastTaskResult }
    })
    foreach ($t in $Findings.scheduled_tasks) {
        Write-Info "task '$($t.name)': state=$($t.state) last_run=$($t.last_run) result=$($t.last_result)"
    }
} else {
    $Findings.scheduled_tasks = @()
    Write-Info "no licensed-run/deckhand/agent scheduled tasks found"
}
$agentProc = Get-Process -Name python*,pythonw* -ErrorAction SilentlyContinue | Select-Object -First 3
$Findings.python_processes = @($agentProc | ForEach-Object { $_.ProcessName })
Write-Info "python-ish processes running: $(@($agentProc).Count)"

# -----------------------------------------------------------------------------
# 7. Evidence
# -----------------------------------------------------------------------------
Write-Section "Summary"
$Findings.applied    = [bool]$Apply
$Findings.actions    = @($script:Actions)
$Findings.gaps       = @($script:Problems)
$Findings.checked_at = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')

if (-not $EvidenceOut) {
    $stateDir = Join-Path $env:LOCALAPPDATA 'workspace-hub\remote-exec'
    if (-not (Test-Path $stateDir)) { New-Item -ItemType Directory -Path $stateDir -Force | Out-Null }
    $EvidenceOut = Join-Path $stateDir "remote-exec-$($Findings.hostname).json"
}
$Findings | ConvertTo-Json -Depth 6 | Set-Content -Path $EvidenceOut -Encoding utf8
Write-Host "`nEvidence written: $EvidenceOut"

if ($script:Problems.Count -eq 0) {
    Write-Ok "no gaps found"
} else {
    Write-Host "`n$($script:Problems.Count) gap(s):" -ForegroundColor Yellow
    $script:Problems | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
}

if (-not $Apply) {
    Write-Host "`nAUDIT ONLY -- nothing was changed. Re-run elevated with -Apply to provision." -ForegroundColor Cyan
} else {
    Write-Host "`nApplied $($script:Actions.Count) change(s)." -ForegroundColor Cyan

    # The login user MUST be spelled out. ssh defaults the remote user to the CALLING
    # host's username, which on the Linux fleet is not the Windows account name here --
    # so a bare `ssh <this-host>` fails with "Permission denied (publickey,...)", which
    # is indistinguishable from a genuine key failure and sends the operator off to
    # re-provision a key that was already correct. Measured 2026-07-31 on ace-win-1:
    # `ssh <host> 'exit 7'` from ace-linux-1 denied; `ssh vamseea@<host> 'exit 7'` -> 7.
    # BatchMode=yes matters for the same reason: without it a password/kbd-interactive
    # fallback can make a FAILED key auth look like a pass.
    $verifyHost = if ($Findings.tailnet_node) { $Findings.tailnet_node } else { $Findings.hostname }
    $verifyTarget = "$env:USERNAME@$verifyHost"
    Write-Host "VERIFY FROM ANOTHER FLEET NODE (exit code matters, not just output):" -ForegroundColor Cyan
    Write-Host "  ssh -o BatchMode=yes $verifyTarget `"exit 7`"; echo `$?    # must print 7, not 0" -ForegroundColor Cyan
    Write-Host "  The '$env:USERNAME@' prefix is required -- omitting it denies on the wrong username." -ForegroundColor Cyan
}

# Non-zero exit when gaps remain and we did not apply, so a scheduled audit can alarm.
if ($script:Problems.Count -gt 0 -and -not $Apply) { exit 1 }
exit 0
