# Build and pack PyWinAppSDK.Build.Tasks to local packages folder
# Run this script after making changes to the build tasks

$ErrorActionPreference = "Stop"

$RootDir = Split-Path $PSScriptRoot -Parent
$ProjectDir = Join-Path $RootDir "PyWinAppSDK.Build.Tasks"
$LocalPackagesDir = Join-Path $RootDir "localpackages"
$ProjectFile = Join-Path $ProjectDir "PyWinAppSDK.Build.Tasks.csproj"

Write-Host "Building PyWinAppSDK.Build.Tasks..." -ForegroundColor Cyan
dotnet build $ProjectFile -c Release

Write-Host "`nPacking NuGet package..." -ForegroundColor Cyan
dotnet pack $ProjectFile -c Release --no-build -o $LocalPackagesDir

Write-Host "`nPackage created in: $LocalPackagesDir" -ForegroundColor Green
Write-Host "To use in test project, run:" -ForegroundColor Yellow
Write-Host "  cd Test.WinMDResolution" -ForegroundColor Yellow
Write-Host "  dotnet restore" -ForegroundColor Yellow
Write-Host "  dotnet build .\TestWinMDResolve.proj" -ForegroundColor Yellow
