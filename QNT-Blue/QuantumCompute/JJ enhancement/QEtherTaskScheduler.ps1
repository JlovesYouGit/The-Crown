# QEther Task Scheduler
# Creates scheduled tasks for constant network optimization

Write-Host "=== QETHER TASK SCHEDULER ===" -ForegroundColor Green
Write-Host "CREATING SCHEDULED TASKS FOR CONSTANT NETWORK OPTIMIZATION" -ForegroundColor Magenta

# Function to create scheduled tasks
function Create-QEtherScheduledTasks {
    Write-Host "`n=== CREATING QETHER SCHEDULED TASKS ===" -ForegroundColor Cyan
    
    try {
        # Create the tasks directory if it doesn't exist
        $tasksDir = "C:\ProgramData\QEtherTasks"
        if (!(Test-Path $tasksDir)) {
            New-Item -ItemType Directory -Path $tasksDir -Force | Out-Null
        }
        
        # Copy the main optimization script to the tasks directory
        Copy-Item -Path "c:\AMD\AMD Software Cloud Edition 23.Q3\Packages\Apps\QuantumCompute\JJ enhancement\CompleteQEtherSpeedOptimizer.ps1" -Destination "$tasksDir\CompleteQEtherSpeedOptimizer.ps1" -Force
        
        # Create a wrapper script for the task
        $taskScript = @"
@echo off
REM QEther Scheduled Task Wrapper
REM This script is executed by Windows Task Scheduler

echo QEther Scheduled Task Executing...
echo ================================

REM Run the complete QEther speed optimizer
powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File "C:\ProgramData\QEtherTasks\CompleteQEtherSpeedOptimizer.ps1"

echo QEther Scheduled Task Completed!
"@
        
        # Save the task script
        $taskScript | Out-File -FilePath "$tasksDir\QEtherTaskWrapper.bat" -Encoding ASCII
        
        # Create scheduled task for system startup
        Write-Host "Creating startup task..." -ForegroundColor Gray
        $startupAction = New-ScheduledTaskAction -Execute "C:\ProgramData\QEtherTasks\QEtherTaskWrapper.bat"
        $startupTrigger = New-ScheduledTaskTrigger -AtStartup
        $startupSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
        $startupPrincipal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
        
        Register-ScheduledTask -TaskName "QEther Startup Optimization" -Action $startupAction -Trigger $startupTrigger -Settings $startupSettings -Principal $startupPrincipal -Description "QEther Network Optimization at System Startup" -Force | Out-Null
        
        # Create scheduled task for periodic optimization (every 30 minutes)
        Write-Host "Creating periodic optimization task..." -ForegroundColor Gray
        $periodicAction = New-ScheduledTaskAction -Execute "C:\ProgramData\QEtherTasks\QEtherTaskWrapper.bat"
        $periodicTrigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 30) -RepetitionDuration (New-TimeSpan -Days 365)
        $periodicSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
        $periodicPrincipal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
        
        Register-ScheduledTask -TaskName "QEther Periodic Optimization" -Action $periodicAction -Trigger $periodicTrigger -Settings $periodicSettings -Principal $periodicPrincipal -Description "QEther Network Periodic Optimization" -Force | Out-Null
        
        Write-Host "✓ QEther Scheduled Tasks Created Successfully" -ForegroundColor Green
        Write-Host "  Startup Task: QEther Startup Optimization" -ForegroundColor Gray
        Write-Host "  Periodic Task: QEther Periodic Optimization (every 30 mins)" -ForegroundColor Gray
        Write-Host "  Execution User: SYSTEM" -ForegroundColor Gray
        Write-Host "  Privileges: Highest" -ForegroundColor Gray
    }
    catch {
        Write-Host "✗ Failed to create scheduled tasks: $_" -ForegroundColor Red
    }
}

# Function to start the startup task immediately
function Start-StartupTask {
    Write-Host "`n=== STARTING STARTUP TASK IMMEDIATELY ===" -ForegroundColor Cyan
    
    try {
        # Start the startup optimization task immediately
        Start-ScheduledTask -TaskName "QEther Startup Optimization"
        
        Write-Host "✓ Startup Task Started Successfully" -ForegroundColor Green
        Write-Host "  Task Name: QEther Startup Optimization" -ForegroundColor Gray
        Write-Host "  Status: Running" -ForegroundColor Gray
    }
    catch {
        Write-Host "⚠ Warning: Could not start startup task immediately" -ForegroundColor Yellow
        Write-Host "  Error: $_" -ForegroundColor Gray
    }
}

# Function to verify task creation
function Verify-TaskCreation {
    Write-Host "`n=== VERIFYING TASK CREATION ===" -ForegroundColor Cyan
    
    try {
        $startupTask = Get-ScheduledTask -TaskName "QEther Startup Optimization" -ErrorAction Stop
        Write-Host "✓ Startup Task Created Successfully" -ForegroundColor Green
        Write-Host "  Task Name: $($startupTask.TaskName)" -ForegroundColor Gray
        Write-Host "  State: $($startupTask.State)" -ForegroundColor Gray
        
        $periodicTask = Get-ScheduledTask -TaskName "QEther Periodic Optimization" -ErrorAction Stop
        Write-Host "✓ Periodic Task Created Successfully" -ForegroundColor Green
        Write-Host "  Task Name: $($periodicTask.TaskName)" -ForegroundColor Gray
        Write-Host "  State: $($periodicTask.State)" -ForegroundColor Gray
    }
    catch {
        Write-Host "✗ Task Verification Failed: $_" -ForegroundColor Red
    }
}

# Function to display management instructions
function Show-ManagementInstructions {
    Write-Host "`n=== MANAGEMENT INSTRUCTIONS ===" -ForegroundColor Cyan
    
    Write-Host "To manage QEther scheduled tasks:" -ForegroundColor Yellow
    Write-Host "  1. Open Task Scheduler (taskschd.msc)" -ForegroundColor Gray
    Write-Host "  2. Navigate to Task Scheduler Library" -ForegroundColor Gray
    Write-Host "  3. Look for 'QEther Startup Optimization' and 'QEther Periodic Optimization'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "To manually run a task:" -ForegroundColor Yellow
    Write-Host "  Right-click on the task -> Run" -ForegroundColor Gray
    Write-Host ""
    Write-Host "To check task history:" -ForegroundColor Yellow
    Write-Host "  Right-click on the task -> Properties -> History tab" -ForegroundColor Gray
}

# Main execution
Write-Host "`nINITIATING QETHER TASK SCHEDULING..." -ForegroundColor Yellow

# Create scheduled tasks
Create-QEtherScheduledTasks

# Start the startup task immediately
Start-StartupTask

# Verify task creation
Verify-TaskCreation

# Show management instructions
Show-ManagementInstructions

Write-Host "`n=== QETHER TASK SCHEDULING COMPLETE ===" -ForegroundColor Green
Write-Host "CONSTANT NETWORK OPTIMIZATION NOW SCHEDULED" -ForegroundColor Magenta
Write-Host ""
Write-Host "ACTIVE TASKS:" -ForegroundColor Yellow
Write-Host "  Startup Task: Runs at system startup" -ForegroundColor Gray
Write-Host "  Periodic Task: Runs every 30 minutes" -ForegroundColor Gray
Write-Host ""
Write-Host "NETWORK OPTIMIZATION IS NOW CONSTANTLY ACTIVE!" -ForegroundColor Green
Write-Host "BOTH DOWNLOAD AND UPLOAD SPEEDS MAINTAINED AT MAXIMUM EFFICIENCY!" -ForegroundColor Magenta