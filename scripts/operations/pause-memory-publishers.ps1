param(
    [switch]$Undo
)

$ErrorActionPreference = "Stop"
$TaskName = "MemoryBridgeSync"
$TaskPath = "\Claude\"
$BackupRoot = if ($env:PAUSE_MEMORY_TASK_BACKUP_DIR) { $env:PAUSE_MEMORY_TASK_BACKUP_DIR } else { Join-Path $HOME "scheduled-task-backups" }
$DateStamp = if ($env:PAUSE_MEMORY_DATE) { $env:PAUSE_MEMORY_DATE } else { Get-Date -Format "yyyyMMdd-HHmmss" }
$BackupPath = Join-Path $BackupRoot "$TaskName-$DateStamp.xml"
$SchTasks = if ($env:SCHTASKS_BIN) { $env:SCHTASKS_BIN } else { "schtasks.exe" }

New-Item -ItemType Directory -Force -Path $BackupRoot | Out-Null

if ($Undo) {
    Enable-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath | Out-Null
    Write-Host "Enabled scheduled task $TaskPath$TaskName"
    exit 0
}

if ($env:SCHTASKS_BIN) {
    $definition = & $SchTasks /Query /TN "$TaskPath$TaskName" /XML
    if ($LASTEXITCODE -ne 0 -or -not $definition) {
        throw "Failed to back up scheduled task $TaskPath$TaskName"
    }
    Set-Content -Path $BackupPath -Value $definition -Encoding UTF8
} else {
    $definition = Export-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath
    Set-Content -Path $BackupPath -Value $definition -Encoding UTF8
}
Disable-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath | Out-Null
Write-Host "Backup: $BackupPath"
Write-Host "Disabled scheduled task $TaskPath$TaskName"
