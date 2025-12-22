$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

Write-Host "`n╔═══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   PyWinAppSDK Full Rebuild and Test          ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# --- Step 1: Clean previous builds ---
Write-Host "=== Step 1: Cleaning previous builds ===" -ForegroundColor Yellow
Remove-Item "$root\wheels\*.whl" -Force -ErrorAction SilentlyContinue
# Let FullBuild handle project cleaning
Write-Host "✓ Wheel cleanup completed`n" -ForegroundColor Green

# Determine Python path to use (prefer Python 3.11)
$pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Path
if ($pythonPath) {
    $pythonVersion = & $pythonPath --version 2>&1
    Write-Host "Using Python: $pythonVersion at $pythonPath" -ForegroundColor Cyan
    $pythonArg = "/p:PythonPath=`"$pythonPath`""
} else {
    Write-Host "Warning: Python not found in PATH, using uv default" -ForegroundColor Yellow
    $pythonArg = ""
}

# --- Step 2: Build PyWinAppSDK.Build.Tasks ---
Write-Host "=== Step 2: Building PyWinAppSDK.Build.Tasks ===" -ForegroundColor Yellow
Set-Location "$root\PyWinAppSDK.Build.Tasks"
dotnet build -c Release
if ($LASTEXITCODE -ne 0) { Write-Error "Build failed for PyWinAppSDK.Build.Tasks"; exit 1 }
Write-Host "✓ Build.Tasks built successfully`n" -ForegroundColor Green

# --- Step 3: Build Headers ---
Write-Host "=== Step 3: Building Headers ===" -ForegroundColor Yellow
Set-Location "$root\Headers"
dotnet build
if ($LASTEXITCODE -ne 0) { Write-Error "Build failed for Headers"; exit 1 }
Write-Host "✓ Headers built successfully`n" -ForegroundColor Green

# --- Step 4: Build Component Packages ---
Write-Host "=== Step 4: Building Component Packages ===" -ForegroundColor Yellow
Set-Location "$root\FullBuild"
dotnet build FullBuild.proj /t:Build $pythonArg
if ($LASTEXITCODE -ne 0) { Write-Error "Component package build failed"; exit 1 }
Write-Host "✓ Component packages built successfully`n" -ForegroundColor Green

Set-Location $root

# --- Show built wheels ---
Write-Host "=== Generated Wheels ===" -ForegroundColor Cyan
Get-ChildItem "$root\wheels\*.whl" | ForEach-Object {
    Write-Host "  ✓ $($_.Name)" -ForegroundColor Green
}

# --- Run Integration Test ---
Write-Host "`n=== Running Integration Test ===" -ForegroundColor Cyan
& "$root\test_integration.ps1"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n╔═══════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║   ✅ Full Rebuild and Test PASSED!            ║" -ForegroundColor Green
    Write-Host "╚═══════════════════════════════════════════════╝`n" -ForegroundColor Green
} else {
    Write-Host "`n╔═══════════════════════════════════════════════╗" -ForegroundColor Red
    Write-Host "║   ❌ Integration Test FAILED!                  ║" -ForegroundColor Red
    Write-Host "╚═══════════════════════════════════════════════╝`n" -ForegroundColor Red
    exit 1
}
