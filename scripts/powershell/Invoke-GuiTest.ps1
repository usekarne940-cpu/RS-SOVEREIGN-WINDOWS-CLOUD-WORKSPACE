#Requires -Version 5.1
<#
Invoke-GuiTest.ps1 — GUI smoke tests on a Windows desktop session.
Reads app specs from applications/applications.json, launches each enabled
app, verifies the process and window title, sends keystrokes (where
configured), captures a screenshot and closes the app.

Best-effort policy (D-005): each app is scored independently; the script
exits 1 ONLY if every app failed (all-fail = environment cannot run GUI at
all). Partial results are honest: reports/gui-test-results.json records
per-app step-by-step evidence.
#>
[CmdletBinding()]
param(
    [string]$AppSpecPath,
    [string]$ScreenshotDir
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'Common.psm1') -Force

$logPath = Join-Path (Get-RsReportDir) 'gui-test.log'
if (-not $AppSpecPath) {
    $AppSpecPath = Join-Path (Get-RsRepoRoot) 'applications\applications.json'
}
if (-not $ScreenshotDir) {
    $ScreenshotDir = Join-Path (Get-RsArtifactDir) 'screenshots'
}
if (-not (Test-Path $ScreenshotDir)) {
    New-Item -ItemType Directory -Path $ScreenshotDir -Force | Out-Null
}
Write-RsLog "GUI tests starting (spec: $AppSpecPath)" 'INFO' $logPath

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName Microsoft.VisualBasic

$spec = Get-Content -Raw -Path $AppSpecPath | ConvertFrom-Json
$results = @()

foreach ($app in $spec.apps) {
    if (-not $app.enabled) { continue }

    $steps = New-Object System.Collections.Generic.List[string]
    $appOk = $true
    $errText = ''
    $title = ''
    $target = $null

    # 1. Launch
    try {
        Start-Process -FilePath $app.launch -ErrorAction Stop | Out-Null
        $steps.Add('launch:PASS')
    }
    catch {
        $appOk = $false
        $errText = "launch failed: $_"
        $steps.Add('launch:FAIL')
        $results += [pscustomobject]@{
            app = $app.name; status = 'FAIL'; steps = ($steps -join '; '); error = $errText
        }
        continue
    }

    # 2. Wait for the target process (and window title when one exists)
    $deadline = (Get-Date).AddSeconds([int]$app.launch_wait_s)
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Milliseconds 500
        $target = Get-Process -Name $app.process -ErrorAction SilentlyContinue |
            Select-Object -First 1
        if ($null -ne $target) {
            try {
                $target.Refresh()
                if ($target.MainWindowTitle) { break }
            }
            catch { break }
        }
    }
    if ($null -ne $target) {
        $steps.Add('wait-process:PASS')
        try { $target.Refresh(); $title = $target.MainWindowTitle } catch { $title = '' }
    }
    else {
        $appOk = $false
        $steps.Add('wait-process:FAIL')
        $errText = "process '$($app.process)' did not start within $($app.launch_wait_s)s"
    }

    # 3. Window title verification (when configured)
    if ($app.verify_title_contains) {
        if ($title -and $title -like ('*' + $app.verify_title_contains + '*')) {
            $steps.Add('verify-title:PASS')
        }
        else {
            $appOk = $false
            $steps.Add("verify-title:FAIL(title='$title')")
        }
    }

    # 4. Keystrokes (when configured)
    if ($app.send_keys) {
        $activated = $false
        if ($null -ne $target) {
            try { $activated = [Microsoft.VisualBasic.Interaction]::AppActivate($target.Id) }
            catch { $activated = $false }
        }
        if ($activated) {
            [System.Windows.Forms.SendKeys]::SendWait($app.send_keys)
            Start-Sleep -Milliseconds 800
            $steps.Add('send-keys:PASS')
        }
        else {
            $appOk = $false
            $steps.Add('send-keys:FAIL(no window activation)')
        }
    }

    # 5. Screenshot evidence
    try {
        $shot = Capture-RsScreen -Name ("gui-{0}" -f $app.name) -OutDir $ScreenshotDir
        $steps.Add("screenshot:PASS")
    }
    catch {
        $steps.Add('screenshot:FAIL')
    }

    # 6. Close
    switch ($app.close) {
        'window' {
            if ($null -ne $target) {
                $null = $target.CloseMainWindow()
                Start-Sleep -Seconds 2
                if (-not $target.HasExited) {
                    Stop-Process -Id $target.Id -Force -ErrorAction SilentlyContinue
                }
                $steps.Add('close:PASS')
            }
            else { $steps.Add('close:SKIP(no process)') }
        }
        'process' {
            if ($null -ne $target) {
                Stop-Process -Id $target.Id -Force -ErrorAction SilentlyContinue
                $steps.Add('close:PASS')
            }
            else { $steps.Add('close:SKIP(no process)') }
        }
        default { $steps.Add('close:SKIP(shell-managed)') }
    }

    $status = if ($appOk) { 'PASS' } else { 'FAIL' }
    $results += [pscustomobject]@{
        app = $app.name; status = $status; steps = ($steps -join '; '); error = $errText
    }
    Write-RsLog "App '$($app.name)' -> $status" 'INFO' $logPath
}

$passed = @($results | Where-Object { $_.status -eq 'PASS' }).Count
$failed = @($results | Where-Object { $_.status -eq 'FAIL' }).Count
$report = [ordered]@{
    generated_utc = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
    spec          = $AppSpecPath
    passed        = $passed
    failed        = $failed
    policy        = 'best-effort per app; exit 1 only when ALL apps fail (D-005)'
    results       = $results
}
ConvertTo-RsJsonFile -Data $report -Path (Join-Path (Get-RsReportDir) 'gui-test-results.json')

if ($results.Count -gt 0 -and $passed -eq 0) {
    Write-RsLog "All $failed GUI tests failed" 'ERROR' $logPath
    exit 1
}
Write-RsLog "GUI tests complete: $passed passed, $failed failed" 'INFO' $logPath
exit 0
