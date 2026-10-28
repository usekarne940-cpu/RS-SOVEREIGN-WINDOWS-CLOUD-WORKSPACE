#Requires -Version 5.1
<#
Get-SystemAudit.ps1 — Windows environment audit.
Collects OS, hardware, tool and network facts and writes
reports/system-audit-windows.json. Runs on GitHub windows-latest runners
(audit.yml) and locally on any Windows machine.
#>
[CmdletBinding()]
param(
    [string]$ReportPath
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'Common.psm1') -Force

$logPath = Join-Path (Get-RsReportDir) 'system-audit-windows.log'
Write-RsLog 'Windows system audit starting' 'INFO' $logPath

function Test-RsCommand {
    param([string]$Name)
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if ($null -ne $cmd) {
        return [ordered]@{ present = $true; source = $cmd.Source }
    }
    return [ordered]@{ present = $false; source = $null }
}

try {
    $os = Get-CimInstance Win32_OperatingSystem |
        Select-Object -Property Caption, Version, BuildNumber, OSArchitecture
    $cs = Get-CimInstance Win32_ComputerSystem |
        Select-Object -Property Manufacturer, Model, TotalPhysicalMemory
    $cpu = Get-CimInstance Win32_Processor |
        Select-Object -First 1 -Property Name, NumberOfCores, NumberOfLogicalProcessors
    $drives = Get-PSDrive -PSProvider FileSystem |
        Select-Object Name,
            @{ n = 'FreeGB'; e = { [math]::Round($_.Free / 1GB, 1) } },
            @{ n = 'UsedGB'; e = { [math]::Round($_.Used / 1GB, 1) } }

    $tools = [ordered]@{}
    foreach ($name in @('git', 'python', 'node', 'npm', '7z', 'winget', 'pwsh', 'powershell')) {
        $tools[$name] = Test-RsCommand -Name $name
    }

    $networkReachable = $false
    try {
        $networkReachable = Test-Connection -ComputerName github.com -Count 1 -Quiet -ErrorAction Stop
    }
    catch {
        $networkReachable = $false
    }

    $audit = [ordered]@{
        generated_utc   = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
        host            = $env:COMPUTERNAME
        user            = $env:USERNAME
        ps_version      = $PSVersionTable.PSVersion.ToString()
        os              = $os
        computer        = $cs
        cpu             = $cpu
        total_memory_gb = [math]::Round($cs.TotalPhysicalMemory / 1GB, 1)
        drives          = $drives
        tools           = $tools
        network_github_reachable = $networkReachable
        runner          = [ordered]@{
            github_actions = [bool]$env:GITHUB_ACTIONS
            runner_name    = $env:RUNNER_NAME
        }
    }

    if (-not $ReportPath) {
        $ReportPath = Join-Path (Get-RsReportDir) 'system-audit-windows.json'
    }
    ConvertTo-RsJsonFile -Data $audit -Path $ReportPath
    Write-RsLog "Audit report written to $ReportPath" 'INFO' $logPath
    exit 0
}
catch {
    Write-RsLog "Audit failed: $_" 'ERROR' $logPath
    Write-Error $_
    exit 1
}
