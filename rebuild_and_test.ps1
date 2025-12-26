$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

Write-Host "`n╔═══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   PyWinAppSDK Full Rebuild and Test          ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Run rebuild script
& "$root\rebuildAll.ps1"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# Run test script
& "$root\testAll.ps1"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`n╔═══════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║   ✅ Full Rebuild and Test PASSED!            ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════╝`n" -ForegroundColor Green
