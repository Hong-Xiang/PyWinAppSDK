$ErrorActionPreference = "Stop"
$root = "D:\Code\PyWinAppSDK"

Write-Host "`n╔═══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   PyWinAppSDK Full Rebuild and Test          ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# --- Step 1: Clean previous builds ---
Write-Host "=== Step 1: Cleaning previous builds ===" -ForegroundColor Yellow
Remove-Item "$root\wheels\*.whl" -Force -ErrorAction SilentlyContinue
Remove-Item "$root\Headers\obj" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$root\Headers\bin" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$root\InteractiveExperiences\obj" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$root\InteractiveExperiences\bin" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$root\Foundation\obj" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$root\Foundation\bin" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$root\AI\obj" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$root\AI\bin" -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "✓ Clean completed`n" -ForegroundColor Green

# --- Step 2: Build Headers (required first) ---
Write-Host "=== Step 2: Building Headers ===" -ForegroundColor Yellow
Set-Location "$root\Headers"
dotnet build  # Note: Headers has its own build targets, don't use /p:GeneratePyWinAppSDK=true
if ($LASTEXITCODE -ne 0) { Write-Error "Build failed for Headers"; exit 1 }
Write-Host "✓ Headers built successfully`n" -ForegroundColor Green

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

# --- Step 3: Build InteractiveExperiences ---
Write-Host "=== Step 3: Building InteractiveExperiences ===" -ForegroundColor Yellow
Set-Location "$root\InteractiveExperiences"
dotnet build /p:GeneratePyWinAppSDK=true $pythonArg
if ($LASTEXITCODE -ne 0) { Write-Error "Build failed for InteractiveExperiences"; exit 1 }
Write-Host "✓ InteractiveExperiences built successfully`n" -ForegroundColor Green

# --- Step 4: Build Foundation ---
Write-Host "=== Step 4: Building Foundation ===" -ForegroundColor Yellow
Set-Location "$root\Foundation"
dotnet build /p:GeneratePyWinAppSDK=true $pythonArg
if ($LASTEXITCODE -ne 0) { Write-Error "Build failed for Foundation"; exit 1 }
Write-Host "✓ Foundation built successfully`n" -ForegroundColor Green

# --- Step 5: Build AI ---
Write-Host "=== Step 5: Building AI ===" -ForegroundColor Yellow
Set-Location "$root\AI"
dotnet build /p:GeneratePyWinAppSDK=true $pythonArg
if ($LASTEXITCODE -ne 0) { Write-Error "Build failed for AI"; exit 1 }
Write-Host "✓ AI built successfully`n" -ForegroundColor Green

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
