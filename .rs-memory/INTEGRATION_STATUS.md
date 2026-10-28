# INTEGRATION_STATUS

Component-to-component wiring. Status values: WIRED+TESTED (locally verified),
WIRED+CI (executes on GitHub runners), N/A.

| From | To | Interface | Status |
|------|----|-----------|--------|
| config/xlite.json | xlite_inspector.py | JSON config loader (file id, endpoints, size pinning) | WIRED+TESTED |
| xlite_inspector.py | reports/xlite-*.json | inspect/probe report writers | WIRED+TESTED (live probe evidence) |
| Invoke-XliteInspection.ps1 | xlite_inspector.py | subprocess CLI invocation (env-only auth) | WIRED+CI |
| xlite-inspection.yml | Invoke-XliteInspection.ps1 | workflow step + env PIXELDRAIN_API_KEY | WIRED+CI |
| config/applications.json | Install-Applications.ps1 | winget app list | WIRED+CI |
| applications/applications.json | Invoke-GuiTest.ps1 | GUI app specs | WIRED+CI |
| gui.yml | Install-Applications.ps1, Invoke-GuiTest.ps1 | workflow steps | WIRED+CI |
| screenshots.yml | Capture-Screenshots.ps1 | workflow step | WIRED+CI |
| audit.yml | Get-SystemAudit.ps1 / audit.sh | workflow steps | WIRED+CI |
| test.yml | pytest + Test-Syntax.ps1 + shellcheck + actionlint | workflow steps (matrix + lint job) | WIRED+CI |
| build.yml | run_tests.sh + package_release.sh | workflow steps + release gating | WIRED+CI |
| cleanup.yml | Invoke-Cleanup.ps1 / cleanup.sh | workflow steps | WIRED+CI |
| automation/tasks/*.json | run_task.py | task dispatcher | WIRED+TESTED |
| run_all_checks.py | ps_validator / workflow_lint / secret_scanner / pytest | orchestrator gates | WIRED+TESTED (217/0/2) |
| run_all_checks.py | report_generator.py | records -> markdown rendering | WIRED+TESTED |
| artifact_manager.py | package_release.sh | manifest + sha256 tooling | WIRED+TESTED |
| .rs-memory/* | all waves | continuous project memory | WIRED+TESTED (final state) |

CI items are wired and statically contract-tested locally; their real execution is scheduled
on GitHub Windows/Ubuntu runners after owner approval and push (recorded honestly as
NOT_RUN locally — never faked).
