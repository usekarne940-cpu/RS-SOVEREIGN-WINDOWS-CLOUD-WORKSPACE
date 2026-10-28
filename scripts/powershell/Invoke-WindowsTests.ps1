#Requires -Version 5.1
<#
Invoke-WindowsTests.ps1 — pytest driver for Windows.
Ensures Python is available (winget fallback), installs dev requirements and
runs the local test suites with a JUnit XML report at reports/pytest-windows.xml.
#>
[CmdletBinding()]
param(
    [string]$Python = 'python'
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'Common.psm1') -Force

$logPath = Join-Path (Get-RsReportDir) 'windows-tests.log'

try {
    Set-Location -Path (Get-RsRepoRoot)

    $pythonCmd = Get-Command $Python -ErrorAction SilentlyContinue
    if ($null -eq $pythonCmd) {
        Write-RsLog "Python not found; installing via winget" 'WARN' $logPath
        & winget install --id Python.Python.3.12 -e --silent `
            --accept-package-agreements --accept-source-agreements | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "winget Python install failed ($LASTEXITCODE)" }
        $machinePath = [System.Environment]::GetEnvironmentVariable('Path', 'Machine')
        $userPath = [System.Environment]::GetEnvironmentVariable('Path', 'User')
        $env:Path = "$machinePath;$userPath"
    }

    Write-RsLog 'Installing dev requirements' 'INFO' $logPath
    & $Python -m pip install --quiet --disable-pip-version-warning `
        -r scripts\python\requirements.txt
    if ($LASTEXITCODE -ne 0) { throw "pip install failed ($LASTEXITCODE)" }

    Write-RsLog 'Running pytest suites' 'INFO' $logPath
    & $Python -m pytest tests/unit tests/integration tests/workflow `
        tests/security tests/gui -m 'not network' `
        --junitxml=reports\pytest-windows.xml -q
    $code = $LASTEXITCODE
    Write-RsLog "pytest finished with exit code $code" 'INFO' $logPath
    exit $code
}
catch {
    Write-RsLog "Windows test run failed: $_" 'ERROR' $logPath
    Write-Error $_
    exit 1
}
