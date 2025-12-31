param (
    [string]$DistDir = "dist"
)

$ErrorActionPreference = "Stop"

# Configuration
$PythonVersion = "3.12"
$PackageDir = $DistDir
$PythonTargetDir = "$PackageDir\python"
$AppCodeDir = "$PackageDir\app"

# 1. Clean and Create Dist Directory
Write-Host "Cleaning dist directory..."
if (Test-Path $DistDir) { Remove-Item $DistDir -Recurse -Force }
New-Item -ItemType Directory -Path $PackageDir | Out-Null
New-Item -ItemType Directory -Path $AppCodeDir | Out-Null

# 2. Locate and Copy Standalone Python
# uv manages portable python builds. We find the one we want and copy it.
Write-Host "Fetching and copying Python $PythonVersion..."
# Ensure the version is installed/cached
uv python install $PythonVersion

# Get the path to the executable (Use --no-project to ignore local venv/pyproject)
$OriginalPythonExe = uv python find $PythonVersion --no-project

# Get the root folder of that python installation (usually parent of python.exe)
$OriginalPythonDir = Split-Path $OriginalPythonExe -Parent

# Copy the entire python folder to our dist
Copy-Item -Path $OriginalPythonDir -Destination $PythonTargetDir -Recurse

# 3. Install Dependencies into the Bundled Python
Write-Host "Installing dependencies into bundled Python..."
# Use --target to avoid inspecting the copied python executable which might fail
$SitePackages = "$PythonTargetDir\Lib\site-packages"
New-Item -ItemType Directory -Path $SitePackages -Force | Out-Null
uv pip install . --python $PythonVersion --target "$SitePackages"

# 4. Copy Application Assets
Write-Host "Copying application files..."

# Use Robocopy to safely copy project files while excluding build/env artifacts
# We copy everything to the 'app' folder, except the manifest which goes to root
$RoboArgs = @(
    ".", 
    "$AppCodeDir", 
    "/E", 
    "/XD", "$DistDir", ".venv", ".git", ".winapp", "__pycache__", ".idea", ".vscode", "dist",
    "/XF", "uv.lock", "pyproject.toml", "*.pyc", "*.ps1", "appxmanifest.xml", "*.pyd"
)
# Robocopy returns exit codes 0-7 for success (files copied, no errors)
& robocopy $RoboArgs | Out-Null
if ($LASTEXITCODE -gt 7) { 
    Write-Warning "Robocopy finished with exit code $LASTEXITCODE" 
}

# Copy manifest to package root (MSIX requires it at root)
Copy-Item "appxmanifest.xml" -Destination "$PackageDir\appxmanifest.xml"

# 5. Update Manifest for Bundle Layout
# Since we moved main.py to the 'app' subfolder, we need to update the manifest parameters
$ManifestPath = "$PackageDir\appxmanifest.xml"
(Get-Content $ManifestPath) -replace 'uap10:Parameters="main.py"', 'uap10:Parameters="app\main.py"' | Set-Content $ManifestPath

# 6. Cleanup (Optional)
# Remove __pycache__ to save space
Get-ChildItem -Path $PackageDir -Include "__pycache__" -Recurse | Remove-Item -Recurse -Force

Write-Host "Bundle complete at: $PackageDir"
Write-Host "You can now register this folder as a sparse package."