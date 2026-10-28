#Requires -Version 5.1
<#
Capture-Screenshots.ps1 — desktop screenshot capture.
Captures the full virtual screen to artifacts/screenshots/ and records the
list of visible top-level windows to reports/screenshots.json.
#>
[CmdletBinding()]
param(
    [string]$OutDir
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'Common.psm1') -Force

$logPath = Join-Path (Get-RsReportDir) 'screenshots.log'
Write-RsLog 'Screenshot capture starting' 'INFO' $logPath

try {
    $shot = Capture-RsScreen -Name 'desktop' -OutDir $OutDir
    $windows = Get-Process |
        Where-Object { $_.MainWindowTitle } |
        Select-Object -Property ProcessName, Id, MainWindowTitle
    $report = [ordered]@{
        generated_utc  = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
        screenshot     = $shot
        visible_windows = $windows
    }
    ConvertTo-RsJsonFile -Data $report -Path (Join-Path (Get-RsReportDir) 'screenshots.json')
    Write-RsLog "Captured $shot" 'INFO' $logPath
    exit 0
}
catch {
    Write-RsLog "Screenshot capture failed (no interactive desktop session?): $_" 'ERROR' $logPath
    Write-Error $_
    exit 1
}
