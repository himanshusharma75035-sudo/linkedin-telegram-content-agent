$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$scriptPath = Join-Path $root "src\delivery_worker.py"
$stdoutPath = Join-Path $root "worker.stdout.log"
$stderrPath = Join-Path $root "worker.stderr.log"

$existing = Get-CimInstance Win32_Process |
    Where-Object {
        $_.CommandLine -like "*delivery_worker.py*" -and
        $_.Name -in @("python.exe", "pythonw.exe")
    }

if ($existing) {
    exit 0
}

$pythonw = Get-Command "pythonw.exe" -ErrorAction SilentlyContinue
$pythonExe = if ($pythonw) { $pythonw.Source } else { "python.exe" }

Start-Process `
    -FilePath $pythonExe `
    -ArgumentList "`"$scriptPath`"" `
    -WorkingDirectory $root `
    -WindowStyle Hidden `
    -RedirectStandardOutput $stdoutPath `
    -RedirectStandardError $stderrPath
