#Requires -Version 5.1
<#
Install-Applications.ps1 — idempotent winget application installer.
Reads config/applications.json and installs each application with winget.
Already-installed applications are detected and skipped. Fails (exit 1) only
when a REQUIRED application cannot be installed. Writes
reports/install-applications.json with per-app evidence.
#>
[CmdletBinding()]
param(
    [string]$AppListPath,
    [string]$Category
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'Common.psm1') -Force

$logPath = Join-Path (Get-RsReportDir) 'install-applications.log'
if (-not $AppListPath) {
    $AppListPath = Join-Path (Get-RsRepoRoot) 'config\applications.json'
}
Write-RsLog "Installing applications from $AppListPath" 'INFO' $logPath

try {
    if (-not (Test-Path $AppListPath)) { throw "Application list not found: $AppListPath" }
    $config = Get-Content -Raw -Path $AppListPath | ConvertFrom-Json

    $results = @()
    foreach ($app in $config.applications) {
        if ($Category -and $app.category -ne $Category) { continue }
        $entry = [ordered]@{
            id = $app.id; name = $app.name
            required = [bool]$app.required; status = 'UNKNOWN'; detail = ''
        }
        Write-RsLog "Processing $($app.id)" 'INFO' $logPath

        & winget list --id $app.id -e --accept-source-agreements 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $entry.status = 'ALREADY_INSTALLED'
            $entry.detail = 'winget list matched an installed package'
        }
        else {
            & winget install --id $app.id -e --silent --accept-package-agreements `
                --accept-source-agreements --disable-interactivity | Out-Null
            if ($LASTEXITCODE -eq 0) {
                $entry.status = 'INSTALLED'
                $entry.detail = 'winget install exit code 0'
            }
            else {
                $entry.status = if ($app.required) { 'FAILED_REQUIRED' } else { 'FAILED_OPTIONAL' }
                $entry.detail = "winget install exit code $LASTEXITCODE"
            }
        }
        $results += [pscustomobject]$entry
    }

    $report = [ordered]@{
        generated_utc = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
        source        = $AppListPath
        results       = $results
    }
    ConvertTo-RsJsonFile -Data $report -Path (Join-Path (Get-RsReportDir) 'install-applications.json')

    $failedRequired = @($results | Where-Object { $_.status -eq 'FAILED_REQUIRED' })
    if ($failedRequired.Count -gt 0) {
        $ids = ($failedRequired | ForEach-Object { $_.id }) -join ', '
        Write-RsLog "Required applications failed to install: $ids" 'ERROR' $logPath
        exit 1
    }
    Write-RsLog 'Application installation complete' 'INFO' $logPath
    exit 0
}
catch {
    Write-RsLog "Installation run failed: $_" 'ERROR' $logPath
    Write-Error $_
    exit 1
}
