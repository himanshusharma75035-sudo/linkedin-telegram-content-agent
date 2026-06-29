$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$launcher = Join-Path $root "scripts\start_worker_silent.vbs"
$runPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
$value = "wscript.exe `"$launcher`""

New-Item -Path $runPath -Force | Out-Null
Set-ItemProperty `
    -Path $runPath `
    -Name "LinkedInTelegramContentAgent" `
    -Value $value

Write-Host "Installed per-user startup entry."
