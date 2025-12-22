$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

Write-Host "`n╔═══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   PyWinAppSDK Full Rebuild and Test          ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# --- Step 1: Clean previous builds ---
Write-Host "=== Step 1: Cleaning previous builds ===" -ForegroundColor Yellow
Remove-Item "$root\wheels\*.whl" -Force -ErrorAction SilentlyContinue
Remove-Item "$root\test\.venv" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$root\test\.test_venv" -Recurse -Force -ErrorAction SilentlyContinue
# Let FullBuild handle project cleaning
Write-Host "✓ Cleanup completed`n" -ForegroundColor Green

# --- Step 2: Restore and Build PyWinAppSDK.Build.Tasks ---
Write-Host "=== Step 2: Building PyWinAppSDK.Build.Tasks ===" -ForegroundColor Yellow
Push-Location "$root\PyWinAppSDK.Build.Tasks"
dotnet restore PyWinAppSDK.Build.Tasks.csproj
if ($LASTEXITCODE -ne 0) { Write-Error "NuGet restore failed for Build.Tasks"; exit 1 }
dotnet build -c Release --no-restore
if ($LASTEXITCODE -ne 0) { Write-Error "Build failed for PyWinAppSDK.Build.Tasks"; exit 1 }
Pop-Location
Write-Host "✓ Build.Tasks built successfully`n" -ForegroundColor Green

# --- Step 3: Restore packages that depend on Build.Tasks ---
Write-Host "=== Step 3: Restoring Headers and Component packages ===" -ForegroundColor Yellow
dotnet restore Headers/Headers.proj
if ($LASTEXITCODE -ne 0) { Write-Error "NuGet restore failed for Headers"; exit 1 }
dotnet restore FullBuild/FullBuild.proj
if ($LASTEXITCODE -ne 0) { Write-Error "NuGet restore failed for FullBuild"; exit 1 }
Write-Host "✓ Package restore completed`n" -ForegroundColor Green

# --- Step 4: Build Headers ---
Write-Host "=== Step 4: Building Headers ===" -ForegroundColor Yellow
Push-Location "$root\Headers"
dotnet build --no-restore
if ($LASTEXITCODE -ne 0) { Write-Error "Build failed for Headers"; exit 1 }
Pop-Location
Write-Host "✓ Headers built successfully`n" -ForegroundColor Green

# --- Step 5: Build Component Packages ---
Write-Host "=== Step 5: Building Component Packages ===" -ForegroundColor Yellow
Push-Location "$root\FullBuild"
dotnet build FullBuild.proj /t:Build --no-restore $pythonArg
if ($LASTEXITCODE -ne 0) { Write-Error "Component package build failed"; exit 1 }
Pop-Location
Write-Host "✓ Component packages built successfully`n" -ForegroundColor Green

# --- Show built wheels ---
Write-Host "=== Generated Wheels ===" -ForegroundColor Cyan
Get-ChildItem "$root\wheels\*.whl" | ForEach-Object {
    Write-Host "  ✓ $($_.Name)" -ForegroundColor Green
}

# --- Run Integration Test ---
Write-Host "`n=== Running Integration Test ===" -ForegroundColor Cyan
Push-Location "$root\test"

Write-Host "Syncing dependencies..." -ForegroundColor Yellow
uv sync --force-reinstall
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to sync dependencies"; exit 1 }

Write-Host "Running test_integration.py..." -ForegroundColor Yellow
uv run test_integration.py
uv run test_minimal.py
$testResult = $LASTEXITCODE

Pop-Location

if ($testResult -eq 0) {
    Write-Host "`n╔═══════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║   ✅ Full Rebuild and Test PASSED!            ║" -ForegroundColor Green
    Write-Host "╚═══════════════════════════════════════════════╝`n" -ForegroundColor Green
} else {
    Write-Host "`n╔═══════════════════════════════════════════════╗" -ForegroundColor Red
    Write-Host "║   ❌ Integration Test FAILED!                  ║" -ForegroundColor Red
    Write-Host "╚═══════════════════════════════════════════════╝`n" -ForegroundColor Red
    exit 1
}
