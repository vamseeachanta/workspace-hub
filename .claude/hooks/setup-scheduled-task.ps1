# Setup Windows Scheduled Task for Daily RAG Aggregation
# Run as Administrator: powershell -ExecutionPolicy Bypass -File setup-scheduled-task.ps1

$TaskName = "ClaudeRAGAggregation"
$TaskPath = "D:\workspace-hub\.claude\hooks\daily-rag-aggregate.bat"
$Description = "Daily extraction and aggregation of Claude session transcripts for RAG analysis"

# Create the action
$Action = New-ScheduledTaskAction -Execute $TaskPath

# Create the trigger (daily at 11 PM)
$Trigger = New-ScheduledTaskTrigger -Daily -At "11:00PM"

# Create settings
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd

# Register the task
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description $Description -Force

Write-Host "Scheduled task '$TaskName' created successfully"
Write-Host "Will run daily at 11:00 PM"
