# PyWinAppSDK Rebuild & Test Guide

This guide outlines the steps to perform a clean rebuild of all PyWinAppSDK components and verify them with a full integration test.

## Quick Start

Run the automated rebuild and test script:

```powershell
cd D:\Code\PyWinAppSDK
.\rebuild_and_test.ps1
```

This script will:
1. Clean all previous builds
2. Build Headers package
3. Build InteractiveExperiences, Foundation, and AI packages
4. Run the full integration test

## Manual Build Steps

If you prefer to build manually, follow these steps to clean and rebuild all packages (`Headers`, `InteractiveExperiences`, `Foundation`, `AI`).

```powershell
$ErrorActionPreference = "Stop"
$root = "D:\Code\PyWinAppSDK"

# --- Step 1: Clean previous builds ---
Write-Host "Cleaning previous builds..." -ForegroundColor Cyan
Remove-Item "$root\wheels\*.whl" -Force -ErrorAction SilentlyContinue
Remove-Item "$root\Headers\obj" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$root\InteractiveExperiences\obj" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$root\Foundation\obj" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$root\AI\obj" -Recurse -Force -ErrorAction SilentlyContinue

# --- Step 2: Build Headers (required first) ---
Write-Host "`nBuilding Headers..." -ForegroundColor Cyan
Set-Location "$root\Headers"
dotnet build  # Note: Headers has its own build targets, don't use /p:GeneratePyWinAppSDK=true
if ($LASTEXITCODE -ne 0) { Write-Error "Build failed for Headers"; exit 1 }

# --- Step 3: Build InteractiveExperiences ---
Write-Host "`nBuilding InteractiveExperiences..." -ForegroundColor Cyan
Set-Location "$root\InteractiveExperiences"
dotnet build /p:GeneratePyWinAppSDK=true
if ($LASTEXITCODE -ne 0) { Write-Error "Build failed for InteractiveExperiences"; exit 1 }

# --- Step 4: Build Foundation ---
Write-Host "`nBuilding Foundation..." -ForegroundColor Cyan
Set-Location "$root\Foundation"
dotnet build /p:GeneratePyWinAppSDK=true
if ($LASTEXITCODE -ne 0) { Write-Error "Build failed for Foundation"; exit 1 }

# --- Step 5: Build AI ---
Write-Host "`nBuilding AI..." -ForegroundColor Cyan
Set-Location "$root\AI"
dotnet build /p:GeneratePyWinAppSDK=true
if ($LASTEXITCODE -ne 0) { Write-Error "Build failed for AI"; exit 1 }

Write-Host "`n✅ All packages built successfully!" -ForegroundColor Green
Get-ChildItem "$root\wheels\*.whl" | Select-Object Name
```

## Integration Test (Standalone)

If you've already built the packages and just want to run the integration test:

```powershell
cd D:\Code\PyWinAppSDK
.\test_integration.ps1
```

The script will:
1. Create a fresh `.test_venv` virtual environment using `uv`
2. Install all generated wheels from the `wheels` directory
3. Run `test_full_integration.py` in that environment
4. Display the results

**Note**: The test script uses a special installation approach to properly handle namespace packages, installing each component with `--force-reinstall --no-deps` first, then resolving dependencies.

### Expected Output

You should see output confirming that namespaces from all three components are accessible:

```text
--- Testing Shared Namespace ---
✓ winappsdk package: ...
✓ winappsdk.microsoft namespace
✓ winappsdk.microsoft.windows namespace
✓ winappsdk.microsoft.ui namespace

--- Testing InteractiveExperiences Component ---
✓ winappsdk_InteractiveExperiences package: ...
✓ Imported AppWindow from winappsdk.microsoft.ui.windowing
✓ Imported Compositor from winappsdk.microsoft.ui.composition

--- Testing Foundation Component ---
✓ winappsdk_Foundation package: ...
✓ Imported AppInstance from winappsdk.microsoft.windows.applifecycle
✓ Imported ResourceManager from winappsdk.microsoft.windows.applicationmodel.resources

--- Testing AI Component ---
✓ winappsdk_AI package: ...
✓ Imported winappsdk.microsoft.windows.ai

✅ Full Integration Test Passed!
```
