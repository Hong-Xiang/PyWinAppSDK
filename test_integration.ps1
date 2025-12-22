$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

Write-Host "`n=== PyWinAppSDK Integration Test ===" -ForegroundColor Cyan
Write-Host "Using uv project in test/ folder...`n" -ForegroundColor Yellow

Set-Location "$root\test"

# Sync dependencies (installs wheels from ../wheels)
Write-Host "Syncing dependencies..." -ForegroundColor Cyan
uv sync
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to sync dependencies"; exit 1 }

# Run the test
Write-Host "`n=== Running Integration Test ===" -ForegroundColor Cyan
uv run test_integration.py
$testResult = $LASTEXITCODE

Set-Location $root

if ($testResult -eq 0) {
    Write-Host "`n✅ Integration test PASSED!" -ForegroundColor Green
} else {
    Write-Host "`n❌ Integration test FAILED!" -ForegroundColor Red
    exit $testResult
}
