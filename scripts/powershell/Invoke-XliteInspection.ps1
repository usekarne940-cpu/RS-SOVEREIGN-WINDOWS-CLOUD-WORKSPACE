#Requires -Version 5.1
<#
Invoke-XliteInspection.ps1 — Windows X-Lite archive inspection wrapper.

Mode 'probe': metadata-free availability check — HTTP range probe of the
first 64 KiB, verifies the 7z signature without a multi-GB transfer.

Mode 'full': complete inspection — download (resume/retry, optional
PIXELDRAIN_API_KEY from the environment, never logged), SHA-256 verification,
safe 7z listing with traversal guard, extraction into a dedicated workdir and
ISO / Windows-image marker detection.

ANALYSIS ONLY (PLAN.md section 6): nothing extracted from the archive is ever
executed, and the image is never installed onto the runner.
#>
[CmdletBinding()]
param(
    [ValidateSet('probe', 'full')][string]$Mode = 'probe',
    [string]$Python = 'python',
    [string]$SevenZip = '7z',
    [string]$ExpectedSha256 = ''
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'Common.psm1') -Force

$logPath = Join-Path (Get-RsReportDir) 'xlite-inspection.log'

try {
    Set-Location -Path (Get-RsRepoRoot)

    if (-not (Get-Command $Python -ErrorAction SilentlyContinue)) {
        throw "Python interpreter '$Python' not found on PATH"
    }

    # Ensure 7-Zip is available for full mode
    if (-not (Get-Command $SevenZip -ErrorAction SilentlyContinue)) {
        Write-RsLog '7z missing; installing 7-Zip via winget' 'WARN' $logPath
        & winget install --id 7zip.7zip -e --silent --accept-package-agreements `
            --accept-source-agreements | Out-Null
        $machinePath = [System.Environment]::GetEnvironmentVariable('Path', 'Machine')
        $userPath = [System.Environment]::GetEnvironmentVariable('Path', 'User')
        $env:Path = "$machinePath;$userPath"
        if (-not (Get-Command $SevenZip -ErrorAction SilentlyContinue)) {
            throw '7-Zip still unavailable after winget install'
        }
    }

    # Disk guard for full mode (reads config/xlite.json min_free_disk_gb)
    if ($Mode -eq 'full') {
        $minGb = 15.0
        try {
            $cfg = Get-Content -Raw -Path 'config\xlite.json' | ConvertFrom-Json
            $minGb = [double]$cfg.min_free_disk_gb
        }
        catch { Write-RsLog 'Could not read config/xlite.json; using default 15 GB guard' 'WARN' $logPath }
        $freeGb = [math]::Round((Get-PSDrive -Name C).Free / 1GB, 1)
        if ($freeGb -lt $minGb) {
            throw "Insufficient disk space: $freeGb GB free on C:, need >= $minGb GB"
        }
        Write-RsLog "Disk guard passed: $freeGb GB free" 'INFO' $logPath
    }

    if ($env:PIXELDRAIN_API_KEY) {
        Write-RsLog 'Using PIXELDRAIN_API_KEY from environment (value never logged)' 'INFO' $logPath
    }
    else {
        Write-RsLog 'No PIXELDRAIN_API_KEY set; proceeding anonymously' 'INFO' $logPath
    }

    $inspector = 'scripts\python\xlite_inspector.py'
    $cliArgs = @($inspector, '--config', 'config\xlite.json')

    if ($Mode -eq 'probe') {
        $cliArgs += @('probe', '--bytes', '65536',
            '--report', (Join-Path (Get-RsReportDir) 'xlite-probe.json'))
        & $Python @cliArgs
        if ($LASTEXITCODE -ne 0) { throw "probe failed with exit code $LASTEXITCODE" }
        Write-RsLog 'Probe complete — report at reports/xlite-probe.json' 'INFO' $logPath
        exit 0
    }

    # full mode
    $workdir = Join-Path (Get-RsArtifactDir) 'xlite'
    if (-not (Test-Path $workdir)) {
        New-Item -ItemType Directory -Path $workdir -Force | Out-Null
    }
    $archive = Join-Path $workdir 'xlite.7z'

    $dlArgs = @($inspector, '--config', 'config\xlite.json', 'download', '--dest', $archive)
    if ($ExpectedSha256) { $dlArgs += @('--expected-sha256', $ExpectedSha256) }
    & $Python @dlArgs
    if ($LASTEXITCODE -ne 0) { throw "download failed with exit code $LASTEXITCODE" }

    $verifyArgs = @($inspector, '--config', 'config\xlite.json', 'verify',
        '--archive', $archive, '--seven-zip', $SevenZip,
        '--report', (Join-Path (Get-RsReportDir) 'xlite-inspection.json'),
        '--extract-to', (Join-Path $workdir 'extracted'))
    if ($ExpectedSha256) { $verifyArgs += @('--expected-sha256', $ExpectedSha256) }
    & $Python @verifyArgs
    if ($LASTEXITCODE -ne 0) { throw "verify failed with exit code $LASTEXITCODE" }

    Write-RsLog 'Inspection complete (analysis only; archive contents never executed)' 'INFO' $logPath
    exit 0
}
catch {
    Write-RsLog "X-Lite inspection failed: $_" 'ERROR' $logPath
    Write-Error $_
    exit 1
}
