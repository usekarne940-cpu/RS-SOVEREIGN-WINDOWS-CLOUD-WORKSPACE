#Requires -Version 5.1
<#
Invoke-Cleanup.ps1 — workspace cleanup with guarded paths.
Removes transient directories (reports/tmp, artifacts/xlite, artifacts/tmp,
Python caches). Every target is verified to be inside the repository root
before deletion. -Deep also clears artifacts/screenshots.
Writes reports/cleanup.json with before/after free space evidence.
#>
[CmdletBinding()]
param(
    [switch]$Deep
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'Common.psm1') -Force

$logPath = Join-Path (Get-RsReportDir) 'cleanup.log'

try {
    $repo = Get-RsRepoRoot
    $freeBefore = [math]::Round((Get-PSDrive -Name C).Free / 1MB, 0)

    $targets = @(
        (Join-Path $repo 'reports\tmp'),
        (Join-Path $repo 'artifacts\xlite'),
        (Join-Path $repo 'artifacts\tmp')
    )
    if ($Deep) { $targets += (Join-Path $repo 'artifacts\screenshots') }

    $removed = @()
    # guard includes the directory separator so sibling dirs like
    # "<repo>-evil" can never pass the prefix check (AGENT-01 finding 10)
    $repoGuard = $repo + [System.IO.Path]::DirectorySeparatorChar
    foreach ($t in $targets) {
        $full = [System.IO.Path]::GetFullPath($t)
        if (-not $full.StartsWith($repoGuard, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "Unsafe cleanup target refused (outside repo root): $full"
        }
        if (Test-Path $t) {
            Remove-Item -Path $t -Recurse -Force
            $removed += $t
        }
    }

    Get-ChildItem -Path $repo -Directory -Recurse -Filter '__pycache__' -ErrorAction SilentlyContinue |
        ForEach-Object {
            Remove-Item -Path $_.FullName -Recurse -Force
            $removed += $_.FullName
        }

    $freeAfter = [math]::Round((Get-PSDrive -Name C).Free / 1MB, 0)
    $report = [ordered]@{
        generated_utc = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
        deep          = [bool]$Deep
        removed       = $removed
        free_mb_before = $freeBefore
        free_mb_after  = $freeAfter
        reclaimed_mb   = ($freeAfter - $freeBefore)
    }
    ConvertTo-RsJsonFile -Data $report -Path (Join-Path (Get-RsReportDir) 'cleanup.json')
    Write-RsLog "Cleanup removed $($removed.Count) paths (reclaimed $($freeAfter - $freeBefore) MB)" 'INFO' $logPath
    exit 0
}
catch {
    Write-RsLog "Cleanup failed: $_" 'ERROR' $logPath
    Write-Error $_
    exit 1
}
