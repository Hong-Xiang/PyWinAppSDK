#!/usr/bin/env pwsh
# Quick test script using uv to verify winappsdk namespace imports

$ErrorActionPreference = "Stop"

Write-Host "=== Testing winappsdk_InteractiveExperiences with uv ===" -ForegroundColor Cyan

# Find the wheel file
$wheelDir = "D:\Code\PyWinAppSDK\wheels"
$wheel = Get-ChildItem $wheelDir -Filter "winappsdk_InteractiveExperiences-*.whl" | Select-Object -First 1

if (-not $wheel) {
    Write-Host "❌ Wheel not found in $wheelDir" -ForegroundColor Red
    Write-Host "Run: dotnet build /p:GeneratePyWinAppSDK=true" -ForegroundColor Yellow
    exit 1
}

Write-Host "Found wheel: $($wheel.Name)" -ForegroundColor Green

# Also check for dependencies (winappsdk_headers)
$headersWheel = Get-ChildItem $wheelDir -Filter "winappsdk_headers-*.whl" | Select-Object -First 1
if (-not $headersWheel) {
    Write-Host "⚠️  Warning: winappsdk_headers wheel not found - import may fail" -ForegroundColor Yellow
}

# Create a temporary test environment and run the test
Write-Host "`nRunning test with uv..." -ForegroundColor Cyan

# Use uv run with inline dependencies
uv run --no-project --with "$($wheel.FullName)" python test_import.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Test passed!" -ForegroundColor Green
} else {
    Write-Host "`n❌ Test failed!" -ForegroundColor Red
    exit 1
}
