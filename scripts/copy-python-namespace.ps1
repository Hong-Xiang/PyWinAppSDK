# Copy Python namespace files from PyWinRT output to winappsdk namespace
# Usage: .\copy-python-namespace.ps1 -PyWinRTOutputPath <path> -SafePackageName <name> -DestPath <path>

param(
    [Parameter(Mandatory=$true)]
    [string]$PyWinRTOutputPath,
    
    [Parameter(Mandatory=$true)]
    [string]$SafePackageName,
    
    [Parameter(Mandatory=$true)]
    [string]$DestPath
)

$ErrorActionPreference = 'Stop'

Write-Host "Copying .py files from $PyWinRTOutputPath to $DestPath"
Write-Host "  Looking for files under: $SafePackageName\microsoft\"

# Recursively find all .py files in winappsdk_Component/microsoft/ subdirectories
$count = 0
Get-ChildItem $PyWinRTOutputPath -Recurse -Filter '*.py' | Where-Object {
    $_.FullName -match "\\$SafePackageName\\microsoft\\"
} | ForEach-Object {
    $src = $_.FullName
    # Extract relative path starting from winappsdk_Component/microsoft/
    $match = $src | Select-String -Pattern "\\$SafePackageName\\(microsoft\\.*)"
    if ($match) {
        $relPath = $match.Matches[0].Groups[1].Value
        $dest = Join-Path $DestPath $relPath
        $destDir = Split-Path $dest
        
        # Create destination directory if needed
        if (-not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }
        
        Copy-Item $src $dest -Force
        $count++
        if ($count % 10 -eq 0) {
            Write-Host "  Copied $count files..."
        }
    }
}

Write-Host "Completed copying $count .py files"
