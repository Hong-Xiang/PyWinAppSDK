$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

Write-Host "`n╔═══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   PyWinAppSDK Full Rebuild and Test          ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Run rebuild script
& "$PSScriptRoot\rebuildAll.ps1"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# Run test script
& "$PSScriptRoot\testAll.ps1"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`n╔═══════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║   ✅ Full Rebuild and Test PASSED!            ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════╝`n" -ForegroundColor Green
