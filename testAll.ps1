$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

Write-Host "`n╔═══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   PyWinAppSDK Integration Tests               ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# --- Run Integration Test ---
Write-Host "=== Running Integration Tests ===" -ForegroundColor Cyan
Push-Location "$root\test"

Write-Host "Syncing dependencies..." -ForegroundColor Yellow
uv sync --force-reinstall
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to sync dependencies"; exit 1 }

Write-Host "Running test_integration.py..." -ForegroundColor Yellow
uv run test_integration.py
if ($LASTEXITCODE -ne 0) { 
    Pop-Location
    Write-Host "`n╔═══════════════════════════════════════════════╗" -ForegroundColor Red
    Write-Host "║   ❌ Integration Test FAILED!                  ║" -ForegroundColor Red
    Write-Host "╚═══════════════════════════════════════════════╝`n" -ForegroundColor Red
    exit 1 
}

Write-Host "Running test_minimal.py..." -ForegroundColor Yellow
uv run test_minimal.py
$testResult = $LASTEXITCODE

Pop-Location

if ($testResult -eq 0) {
    Write-Host "`n╔═══════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║   ✅ All Tests PASSED!                         ║" -ForegroundColor Green
    Write-Host "╚═══════════════════════════════════════════════╝`n" -ForegroundColor Green
} else {
    Write-Host "`n╔═══════════════════════════════════════════════╗" -ForegroundColor Red
    Write-Host "║   ❌ Tests FAILED!                             ║" -ForegroundColor Red
    Write-Host "╚═══════════════════════════════════════════════╝`n" -ForegroundColor Red
    exit 1
}
