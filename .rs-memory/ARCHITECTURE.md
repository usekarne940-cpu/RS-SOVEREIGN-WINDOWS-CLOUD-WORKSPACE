# ARCHITECTURE — RS Windows Cloud Workspace

## Component map

```
.github/workflows/        7 GitHub Actions workflows (Windows + Ubuntu runners)
  audit.yml               environment audit (windows-latest + ubuntu-latest)
  test.yml                pytest matrix (windows-latest + ubuntu-latest) + PS syntax gate
  build.yml               validation + source packaging (+ GitHub Release on tags)
  gui.yml                 winget app install + GUI automation smoke tests
  screenshots.yml         desktop screenshot capture
  xlite-inspection.yml    X-Lite archive inspection (probe/full) — analysis only
  cleanup.yml             scheduled workspace cleanup

scripts/powershell/       Windows-side automation
  Common.psm1             shared logging / report / screenshot helpers
  Get-SystemAudit.ps1     system audit -> reports/system-audit-windows.json
  Install-Applications.ps1  idempotent winget installs from applications/applications.json
  Invoke-GuiTest.ps1      GUI smoke tests (SendKeys + process/window verification)
  Capture-Screenshots.ps1 desktop + window enumeration -> artifacts/screenshots/
  Invoke-WindowsTests.ps1 pytest driver on Windows
  Invoke-XliteInspection.ps1  X-Lite inspection wrapper
  Invoke-Cleanup.ps1      temp cleanup with guarded paths
  Test-Syntax.ps1         PowerShell AST parser gate (runs on Windows runners)

scripts/python/           cross-platform tooling (stdlib-first, PyYAML for lint)
  xlite_inspector.py      pixeldrain client (metadata/probe/download/resume/sha256/7z/ISO/report)
  workflow_lint.py        GitHub Actions workflow contract linter
  ps_validator.py         PowerShell static validator (+ real pwsh parser when available)
  secret_scanner.py       secret/credential scanner
  artifact_manager.py     manifest + SHA-256 verification
  report_generator.py     test-record markdown + release report rendering
  run_task.py             automation/tasks/*.json dispatcher (cross-OS)
  run_all_checks.py       local validation orchestrator -> reports/local-validation.{json,md}

scripts/linux/            Linux-side automation (audit, bootstrap, run_tests,
                          validate_workflows, cleanup, package_release)

applications/             GUI app specs consumed by Invoke-GuiTest.ps1
automation/tasks/         task definitions consumed by run_task.py
tests/                    unit / integration / workflow / security / gui contract suites
config/                   applications.json (winget), settings.json, xlite.json
reports/                  generated evidence (committed samples from local runs)
artifacts/                runtime outputs (screenshots, xlite workdir, release)
.rs-memory/               this memory system
docs/                     plan analysis, requirements matrix, roadmap, acceptance criteria,
                          setup, testing, security, troubleshooting
```

## Data flow
run_task.py / workflows -> PowerShell|Python|Linux scripts -> reports/*.json + artifacts/ ->
upload-artifact -> GitHub evidence. Local: run_all_checks.py -> reports/local-validation.json ->
report_generator.py -> reports/LOCAL-VALIDATION.md + TEST-RESULTS.md.

## Security posture
- Least-privilege `permissions:` on every workflow; job-scoped `contents: write` only for releases
- Single secret: PIXELDRAIN_API_KEY (optional, never echoed, redacted in reports)
- X-Lite pipeline is inspection-only; no execution of archive contents; guarded extraction paths
- No pull_request_target usage; no untrusted-context interpolation into shell run blocks
