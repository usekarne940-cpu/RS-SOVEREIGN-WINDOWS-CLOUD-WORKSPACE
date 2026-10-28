# ACCEPTANCE-CRITERIA

Two gate classes: **LG** (locally verifiable now, in the Linux sandbox) and **WG** (verifiable on
GitHub Windows runners after owner approval and push — recorded NOT_RUN until then, never faked).

## Local gates (must be PASS before release readiness)

| # | Criterion | Verification method |
|---|-----------|---------------------|
| LG-01 | Repository tree matches PLAN.md §7 exactly (all dirs + 7 workflows + 5 test suites) | tree inspection; tests/workflow/test_workflow_contracts.py |
| LG-02 | Every Python module imports cleanly under Python 3.12 | pytest import/integration suite |
| LG-03 | pytest unit + integration + workflow + security + gui-contract suites: 0 FAIL | `python -m pytest tests/ -m "not network"` green; reports/local-validation.json |
| LG-04 | Live X-Lite evidence: pixeldrain metadata retrieved as JSON + 7z magic verified on real bytes | reports/xlite-probe.json (Wave 11) |
| LG-05 | All 7 workflows parse as YAML and satisfy contract rules (runners, permissions, timeouts, concurrency, pinned actions, artifact uploads) | workflow_lint.py + contract tests |
| LG-06 | All PowerShell scripts pass static validation (or real pwsh AST parse if pwsh present); zero ERROR-severity findings | ps_validator.py report |
| LG-07 | All Linux scripts pass `bash -n` (plus shellcheck if obtainable) | run_all_checks.py |
| LG-08 | Zero secrets in repository; single optional secret referenced by name only | secret_scanner.py + AGENT-01 |
| LG-09 | No RDP/RustDesk/ssh-server/OS-replacement code paths anywhere | AGENT-01 grep review + SECURITY.md |
| LG-10 | X-Lite pipeline: analysis-only, traversal-guarded extraction, never executes archive content | AGENT-01 + security contract tests |
| LG-11 | All configs (config/, applications/, automation/tasks/) are valid JSON matching their schemas | unit tests + run_all_checks |
| LG-12 | Source archive produced with SHA-256; checksum re-verified | package_release.sh output |
| LG-13 | RS-Memory complete: 13 files + 6 wave-group checkpoints, statuses accurate | memory audit vs actual tree |
| LG-14 | Test records use the mandated 8-field schema with PASS/FAIL/BLOCKED/NOT_RUN only | report_generator schema test + report inspection |
| LG-15 | Docs traceable: every documented command/path exists in the repo | AGENT-03 audit |

## Windows-runner gates (post-approval checklist for the owner)

| # | Criterion | Where it runs |
|---|-----------|---------------|
| WG-01 | `test.yml` green on windows-latest AND ubuntu-latest (real Windows Python execution) | GitHub Actions |
| WG-02 | PowerShell AST syntax gate green on Windows | Test-Syntax.ps1 inside test.yml |
| WG-03 | `audit.yml` uploads real Windows system audit JSON | reports artifact |
| WG-04 | `gui.yml`: winget installs succeed; >=1 GUI smoke test PASS with screenshot evidence | artifacts upload |
| WG-05 | `screenshots.yml` produces desktop PNGs | artifacts upload |
| WG-06 | `xlite-inspection.yml` mode=full: download + SHA-256 + 7z listing + ISO detection + image metadata report | reports + artifacts upload |
| WG-07 | `cleanup.yml` scheduled run succeeds | Actions log |
| WG-08 | `build.yml` produces release archive artifact (GitHub Release on v* tag) | release artifact |

## Release readiness definition
All LG gates PASS; WG gates scheduled (NOT_RUN locally is expected and honest); source frozen
with local git commit; archive + SHA-256 delivered; final report issued with measured values
only; owner approval requested for GitHub deployment (PLAN.md §11).
