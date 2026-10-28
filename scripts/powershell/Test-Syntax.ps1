#Requires -Version 5.1
<#
Test-Syntax.ps1 — REAL PowerShell AST syntax gate.
Parses every .ps1/.psm1 file in the repository with the PowerShell language
parser (the same engine that compiles the scripts) and writes
reports/powershell-syntax.json. Runs on Windows runners (test.yml) where the
parser exists; exit 1 when any file has syntax errors.
#>
[CmdletBinding()]
param(
    [string]$Root
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'Common.psm1') -Force

try {
    if (-not $Root) { $Root = Get-RsRepoRoot }
    $files = Get-ChildItem -Path $Root -Recurse -Include *.ps1, *.psm1 -File
    Write-Host "Parsing $($files.Count) PowerShell files with the AST parser..."

    $results = @()
    $totalErrors = 0
    foreach ($f in $files) {
        $tokens = $null
        $errors = $null
        $null = [System.Management.Automation.Language.Parser]::ParseFile(
            $f.FullName, [ref]$tokens, [ref]$errors)
        $messages = @($errors | ForEach-Object {
                '{0}:{1} {2}' -f $_.Extent.StartLineNumber, $_.Extent.StartColumnNumber, $_.Message
            })
        $totalErrors += $messages.Count
        $results += [pscustomobject]@{
            file   = $f.FullName
            errors = $messages.Count
            messages = ($messages -join ' | ')
        }
    }

    $report = [ordered]@{
        generated_utc = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
        parser        = 'System.Management.Automation.Language.Parser (real AST parse)'
        files_checked = $results.Count
        total_errors  = $totalErrors
        results       = $results
    }
    ConvertTo-RsJsonFile -Data $report -Path (Join-Path $Root 'reports\powershell-syntax.json')

    foreach ($r in $results) {
        if ($r.errors -gt 0) {
            Write-Host "FAIL $($r.file): $($r.messages)"
        }
    }
    if ($totalErrors -gt 0) {
        Write-Host "Syntax gate FAILED: $totalErrors error(s) in $($results.Count) files"
        exit 1
    }
    Write-Host "Syntax gate PASSED: $($results.Count) files, 0 errors"
    exit 0
}
catch {
    Write-Error $_
    exit 1
}
