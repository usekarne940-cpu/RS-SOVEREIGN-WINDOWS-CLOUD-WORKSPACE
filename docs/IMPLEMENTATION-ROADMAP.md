# IMPLEMENTATION-ROADMAP — waves to artifacts

Wave groups follow PLAN.md §8. Each wave group ends with an RS-Memory update
(checkpoint file under `.rs-memory/checkpoints/`).

| Waves | Plan scope | Concrete artifacts produced | Local gate |
|-------|-----------|------------------------------|------------|
| 01-05 | Environment audit, RS Memory, plan analysis, architecture, dependencies | audit evidence in WAVE_HISTORY; `.rs-memory/` (13 files); docs/PLAN-ANALYSIS.md; docs/REQUIREMENTS-MATRIX.md; docs/IMPLEMENTATION-ROADMAP.md; docs/ACCEPTANCE-CRITERIA.md; repo scaffold; dependency decisions D-001..D-012 | audit output captured; plan SHA-256 recorded |
| 06-10 | Scaffolding, configuration, workflow engine, Windows scripts, core integrations | config/{applications,settings,xlite}.json; root files (LICENSE, .gitignore, VERSION, pytest.ini); `scripts/python/` 8 modules; `scripts/powershell/` Common.psm1 + 8 scripts; `scripts/linux/` 6 scripts | import smoke checks; ps_validator; bash -n |
| 11-15 | Application automation, GUI testing, browser testing, screenshots, X-Lite inspection | applications/applications.json; automation/tasks + run_task.py; live X-Lite probe evidence (reports/xlite-probe.json); .github/workflows 7 files; GUI/screenshot scripts wired | live probe run; workflow_lint; contract tests |
| 16-20 | Artifact handling, monitoring, security, unit + integration tests | tests/ 5 suites; artifact_manager; secret_scanner; run_all_checks orchestration; reports/local-validation.{json,md} first full green run | pytest all local suites green |
| 21-25 | Workflow validation, regression, performance, error recovery, documentation | actionlint/shellcheck fetch attempts (+fallback verdicts); regression rerun; README, SETUP, TESTING, SECURITY, TROUBLESHOOTING; performance notes | regression green; docs reality-check |
| 26-30 | Final integration, security review, packaging, release verification, approval prep | AGENT-01/02/03 parallel reviews + fixes; git freeze commit; source archive + SHA-256 into /home/z/my-project/download/ and artifacts/release/; RELEASE-REPORT.md; final memory update; owner approval request | archive checksum verified; zero secrets; all local gates green |

## Dependency order
config -> python core -> powershell/linux -> applications/automation -> workflows -> tests ->
validation runs -> docs -> parallel reviews -> fixes -> freeze -> package -> release report.

## Concurrency plan (honest)
- ORCH-MAIN executes all build waves (single-writer policy prevents concurrent file edits).
- AGENT-01 (security), AGENT-02 (test audit), AGENT-03 (docs audit) run in parallel AFTER code
  freeze — read-only scopes, no write conflicts, findings integrated centrally.
