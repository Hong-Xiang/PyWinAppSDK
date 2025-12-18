$ErrorActionPreference = "Stop"
$root = "D:\Code\PyWinAppSDK"

Write-Host "`n=== PyWinAppSDK Integration Test ===" -ForegroundColor Cyan
Write-Host "Using uv-managed virtual environment...`n" -ForegroundColor Yellow

# Remove old test environment
$testEnv = "$root\.test_venv"
if (Test-Path $testEnv) {
    Write-Host "Removing old test environment..." -ForegroundColor Yellow
    Remove-Item $testEnv -Recurse -Force
}

# Create fresh uv-managed virtual environment with Python 3.11 to match the wheels
Write-Host "Creating fresh virtual environment with uv (Python 3.11)..." -ForegroundColor Cyan
uv venv $testEnv --python 3.11
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to create venv with uv"; exit 1 }

# Verify Python version
Write-Host "`nPython version in test environment:" -ForegroundColor Cyan
& "$testEnv\Scripts\python.exe" --version

# Install the wheels using uv (allow PyPI for dependencies like winrt-runtime)
# Install in dependency order to ensure namespace packages merge correctly
Write-Host "`nInstalling PyWinAppSDK wheels with uv..." -ForegroundColor Cyan
Write-Host "  Installing winappsdk-headers..." -ForegroundColor Gray
uv pip install --python $testEnv --find-links "$root\wheels" winappsdk-headers
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to install winappsdk-headers"; exit 1 }

Write-Host "  Installing winappsdk-interactiveexperiences..." -ForegroundColor Gray
uv pip install --python $testEnv --find-links "$root\wheels" winappsdk-interactiveexperiences --force-reinstall --no-deps
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to install winappsdk-interactiveexperiences"; exit 1 }

# Install dependencies for InteractiveExperiences
uv pip install --python $testEnv --find-links "$root\wheels" winappsdk-interactiveexperiences
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to install dependencies"; exit 1 }

Write-Host "  Installing winappsdk-foundation..." -ForegroundColor Gray
uv pip install --python $testEnv --find-links "$root\wheels" winappsdk-foundation --force-reinstall --no-deps
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to install winappsdk-foundation"; exit 1 }

# Install dependencies for Foundation
uv pip install --python $testEnv --find-links "$root\wheels" winappsdk-foundation
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to install dependencies"; exit 1 }

Write-Host "  Installing winappsdk-ai..." -ForegroundColor Gray
uv pip install --python $testEnv --find-links "$root\wheels" winappsdk-ai --force-reinstall --no-deps
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to install winappsdk-ai"; exit 1 }

# Install dependencies for AI
uv pip install --python $testEnv --find-links "$root\wheels" winappsdk-ai
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to install dependencies"; exit 1 }

# Show installed packages
Write-Host "`nInstalled PyWinAppSDK packages:" -ForegroundColor Cyan
uv pip list --python $testEnv | Select-String -Pattern "winappsdk|winrt"

# Run the integration test using the uv-managed environment
Write-Host "`n=== Running Integration Test ===" -ForegroundColor Cyan
& "$testEnv\Scripts\python.exe" "$root\test_full_integration.py"

$testResult = $LASTEXITCODE

if ($testResult -eq 0) {
    Write-Host "`n✅ Integration test PASSED!" -ForegroundColor Green
} else {
    Write-Host "`n❌ Integration test FAILED!" -ForegroundColor Red
    exit $testResult
}
