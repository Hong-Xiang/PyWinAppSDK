#!/usr/bin/env pwsh
# Integration test script using uv for isolated environment
# Tests all three winappsdk packages together

$ErrorActionPreference = "Stop"

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "  PyWinAppSDK Integration Test - Testing All Components" -ForegroundColor Cyan
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan

# Find wheel files
$wheelDir = "D:\Code\PyWinAppSDK\wheels"
$interactiveWheel = Get-ChildItem $wheelDir -Filter "winappsdk_interactiveexperiences-*.whl" | Select-Object -First 1
$foundationWheel = Get-ChildItem $wheelDir -Filter "winappsdk_foundation-*.whl" | Select-Object -First 1
$aiWheel = Get-ChildItem $wheelDir -Filter "winappsdk_ai-*.whl" | Select-Object -First 1

Write-Host "`nFound wheels:" -ForegroundColor Green
Write-Host "  InteractiveExperiences: $($interactiveWheel.Name)"
Write-Host "  Foundation: $($foundationWheel.Name)"
Write-Host "  AI: $($aiWheel.Name)"

if (-not $interactiveWheel -or -not $foundationWheel -or -not $aiWheel) {
    Write-Host "`n❌ Missing wheel files!" -ForegroundColor Red
    Write-Host "Please ensure all packages are built:" -ForegroundColor Yellow
    Write-Host "  cd InteractiveExperiences; dotnet build /p:GeneratePyWinAppSDK=true"
    Write-Host "  cd Foundation; dotnet build /p:GeneratePyWinAppSDK=true"
    Write-Host "  cd AI; dotnet build /p:GeneratePyWinAppSDK=true"
    exit 1
}

Write-Host "`nRunning integration test with uv..." -ForegroundColor Cyan
Write-Host "This will install all three packages in an isolated environment`n" -ForegroundColor Gray

# Use uv run with find-links to resolve dependencies locally
$uvCommand = @(
    "run"
    "--no-project"
    "--find-links"
    $wheelDir
    "--with"
    "winappsdk-ai==3.2.1"
    "python"
    "test\test_integration.py"
)

& uv @uvCommand

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n" -NoNewline
    Write-Host "=" -NoNewline -ForegroundColor Green
    Write-Host ("=" * 69) -ForegroundColor Green
    Write-Host "  ✅ INTEGRATION TEST PASSED!" -ForegroundColor Green
    Write-Host "=" -NoNewline -ForegroundColor Green
    Write-Host ("=" * 69) -ForegroundColor Green
    Write-Host "`nAll three packages work together correctly:" -ForegroundColor Green
    Write-Host "  • Shared namespace (winappsdk.microsoft.*) ✓"
    Write-Host "  • Component isolation (winappsdk_*) ✓"
    Write-Host "  • Cross-package dependencies ✓"
    Write-Host "  • No namespace conflicts ✓"
} else {
    Write-Host "`n" -NoNewline
    Write-Host "=" -NoNewline -ForegroundColor Red
    Write-Host ("=" * 69) -ForegroundColor Red
    Write-Host "  ❌ INTEGRATION TEST FAILED" -ForegroundColor Red
    Write-Host "=" -NoNewline -ForegroundColor Red
    Write-Host ("=" * 69) -ForegroundColor Red
    exit 1
}
