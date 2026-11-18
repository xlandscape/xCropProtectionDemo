@echo off
setlocal
cd /d "%~dp0"

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
  "$root = (Get-Location).Path; $app = Join-Path $root 'simulation_ui\app.py'; $processes = @(Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^pythonw?\.exe$' -and $_.CommandLine -match '(?i)streamlit' -and $_.CommandLine -like ('*' + $app + '*') }); if ($processes.Count -eq 0) { Write-Host 'xCropProtection dashboard server is not running.'; exit 0 }; foreach ($process in $processes) { Stop-Process -Id $process.ProcessId -Force -ErrorAction Stop; Write-Host ('Stopped xCropProtection dashboard server (PID {0}).' -f $process.ProcessId) }"

set "EXIT_CODE=%ERRORLEVEL%"
endlocal & exit /b %EXIT_CODE%
