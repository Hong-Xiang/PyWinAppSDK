param(
    [Parameter(Mandatory=$false)]
    [string]$Repo = "Hong-Xiang/PyWinAppSDK",
    
    [Parameter(Mandatory=$false)]
    [string]$Tag = "latest",
    
    [Parameter(Mandatory=$false)]
    [string]$OutDir = "wheels"
)

$ErrorActionPreference = "Stop"

# Ensure output directory exists
if (-not (Test-Path $OutDir)) {
    Write-Host "Creating directory: $OutDir" -ForegroundColor Cyan
    New-Item -ItemType Directory -Path $OutDir -Force | Out-Null
}

# Determine API URL
$apiUrl = if ($Tag -eq "latest") {
    "https://api.github.com/repos/$Repo/releases/latest"
} else {
    "https://api.github.com/repos/$Repo/releases/tags/$Tag"
}

Write-Host "Fetching release info from: $apiUrl" -ForegroundColor Cyan

try {
    $headers = @{
        "Accept" = "application/vnd.github.v3+json"
    }
    
    # Use GITHUB_TOKEN if available to avoid rate limits
    if ($env:GITHUB_TOKEN) {
        $headers["Authorization"] = "token $env:GITHUB_TOKEN"
    }

    $release = Invoke-RestMethod -Uri $apiUrl -Headers $headers
    $assets = $release.assets | Where-Object { $_.name -like "*.whl" }

    if ($null -eq $assets -or $assets.Count -eq 0) {
        Write-Warning "No wheel files found in release '$($release.tag_name)'"
        return
    }

    Write-Host "Found $($assets.Count) wheels in release $($release.tag_name)" -ForegroundColor Green

    foreach ($asset in $assets) {
        $destFile = Join-Path $OutDir $asset.name
        Write-Host "Downloading $($asset.name)..." -ForegroundColor Yellow
        
        # Use browser_download_url for public assets
        Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $destFile
    }

    Write-Host "`nSuccessfully downloaded all wheels to $OutDir" -ForegroundColor Green
}
catch {
    Write-Error "Failed to download wheels: $($_.Exception.Message)"
    exit 1
}
