# INTEGRATION_STATUS

Component-to-component wiring. Status values: WIRED+TESTED / WIRED (static) / PENDING / N-A.

| From | To | Interface | Status |
|------|----|-----------|--------|
| config/xlite.json | xlite_inspector.py | JSON config loader (file id, endpoints, sha256) | WIRED (tests pending) |
| xlite_inspector.py | reports/xlite-inspection.json | inspect() report writer | WIRED (tests pending) |
| Invoke-XliteInspection.ps1 | xlite_inspector.py | subprocess CLI invocation | WIRED (static) |
| xlite-inspection.yml | Invoke-XliteInspection.ps1 / python | workflow step + env PIXELDRAIN_API_KEY | WIRED (static) |
| applications/applications.json | Install-Applications.ps1 | winget app list | WIRED (static) |
| applications/applications.json | Invoke-GuiTest.ps1 | GUI app specs | WIRED (static) |
| gui.yml | Install-Applications.ps1, Invoke-GuiTest.ps1 | workflow steps | WIRED (static) |
| screenshots.yml | Capture-Screenshots.ps1 | workflow step | WIRED (static) |
| audit.yml | Get-SystemAudit.ps1 / audit.sh | workflow steps | WIRED (static) |
| test.yml | pytest + Test-Syntax.ps1 | workflow steps (matrix) | WIRED (static) |
| build.yml | run_tests.sh + package_release.sh | workflow steps | WIRED (static) |
| cleanup.yml | Invoke-Cleanup.ps1 / cleanup.sh | workflow steps | WIRED (static) |
| automation/tasks/*.json | run_task.py | task dispatcher | WIRED (tests pending) |
| run_all_checks.py | ps_validator / workflow_lint / secret_scanner / pytest | orchestrator subprocess calls | WIRED (tests pending) |
| run_all_checks.py | report_generator.py | records -> markdown | WIRED (tests pending) |
| artifact_manager.py | package_release.sh | manifest + sha256 | WIRED (static) |

Static = validated locally without Windows execution (BLOCKERS B-03/B-04). All Windows-side
wiring executes for real on GitHub runners after push.
