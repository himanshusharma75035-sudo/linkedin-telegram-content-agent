$ErrorActionPreference = "Stop"

$runPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
Remove-ItemProperty `
    -Path $runPath `
    -Name "LinkedInTelegramContentAgent" `
    -ErrorAction SilentlyContinue

Write-Host "Removed per-user startup entry."
