# Registers a Windows scheduled task that runs daily_runner.py every night (wakes the PC, runs even when on battery, up to 6 hours).
# Run once in PowerShell:   powershell -ExecutionPolicy Bypass -File install_daily_task.ps1 -At 01:30
# Remove later:             Unregister-ScheduledTask -TaskName CartoonDaily -Confirm:$false
param([string]$At = "01:30")
$dir = $PSScriptRoot
$py = (Get-Command python).Source
$action = New-ScheduledTaskAction -Execute $py -Argument "-u daily_runner.py" -WorkingDirectory $dir
$trigger = New-ScheduledTaskTrigger -Daily -At $At
$settings = New-ScheduledTaskSettingsSet -WakeToRun -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Hours 6)
Register-ScheduledTask -TaskName "CartoonDaily" -Action $action -Trigger $trigger -Settings $settings -Description "Makes one cartoon episode per night from stories/*/story.json" -Force
Write-Host "Registered CartoonDaily at $At. Test now with:  Start-ScheduledTask -TaskName CartoonDaily"
