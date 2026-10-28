# TESTING — test suites, evidence model and how results are recorded

## Zero-fake policy (PLAN.md §9)

Every recorded test uses the mandated 8-field schema (TEST ID, NAME, COMMAND, EXPECTED,
ACTUAL, STATUS, EVIDENCE, ERROR DETAILS). Allowed statuses are exactly:

- `PASS` — verified passing, with captured evidence
- `FAIL` — verified failing; never suppressed
- `BLOCKED` — cannot execute in the current environment (with reason and where it WILL run)
- `NOT_RUN` — intentionally not executed (e.g. scheduled for Windows runners)

Windows-only checks are never marked PASS from Linux. The Linux sandbox statically validates
Windows code and records live execution as scheduled-on-runners.

## Test suites

| Suite | Location | What it proves | Runs where |
|---|---|---|---|
| Unit | `tests/unit/` | xlite inspector (network fully mocked), workflow linter rules, PowerShell validator heuristics, secret scanner rules, artifact manifests, report schema, task dispatcher, config schemas | Linux + Windows (pytest) |
| Integration | `tests/integration/` | CLI entrypoints (`--help`), real-config wiring, manifest roundtrip, repo-wide JSON validity | Linux + Windows (pytest) |
| Integration (network) | `tests/integration/test_pixeldrain_live.py` | LIVE pixeldrain endpoint: metadata (2,555,783,617 bytes) + 7z magic via HTTP range | opt-in: `-m network` (deselected by default, including CI) |
| Workflow contracts | `tests/workflow/` | all 7 workflows exist, structure, runners, permissions, timeouts, wiring of real scripts, pinned actions | Linux + Windows (pytest) |
| Security contracts | `tests/security/` | repo-wide secret scan clean, no remote-desktop/tunnel code, no OS-install attempts, X-Lite marker is detection-only, no policy weakening | Linux + Windows (pytest) |
| GUI contracts | `tests/gui/` | GUI spec shape, driver wiring (AppActivate/SendKeys/CloseMainWindow/screenshots), workflow wiring | Linux + Windows (pytest) |
| Real GUI automation | `scripts/powershell/Invoke-GuiTest.ps1` | actual GUI smoke tests on a Windows desktop session | **Windows runners only** (gui.yml) — NOT_RUN locally |
| PowerShell AST gate | `scripts/powershell/Test-Syntax.ps1` | real parser pass over all .ps1/.psm1 | **Windows runners only** (test.yml) |
| External linters | shellcheck + actionlint | shell + workflow lint | **ubuntu runners** (test.yml `lint-external`) — BLOCKED in the dev sandbox (release downloads stripped by proxy) |

## Commands

```bash
# default suite (what CI runs)
python -m pytest tests/unit tests/integration tests/workflow tests/security tests/gui -m "not network"

# live pixeldrain evidence (opt-in)
python -m pytest tests/integration/test_pixeldrain_live.py -m network

# full local gate with 8-field records + markdown report
python scripts/python/run_all_checks.py
# evidence -> reports/local-validation.json + reports/LOCAL-VALIDATION.md
```

## Verified results (dev sandbox, 2026-10-28)

- pytest default suite: **159 passed, 0 failed, 2 deselected** (network-marked)
- Orchestrator gate (`run_all_checks.py`): **205 PASS / 0 FAIL / 2 BLOCKED / 207 total**
  (BLOCKED = shellcheck + actionlint in-sandbox; both execute in CI instead)
- Live X-Lite probe: HTTP 206, 7z magic `377abcaf271c`, 2,555,783,617 bytes —
  `reports/xlite-probe.json`
- Windows-side real execution: scheduled on GitHub runners (wg-gates in
  `docs/ACCEPTANCE-CRITERIA.md`)

## How failures were handled during development

Every failure encountered during the build was diagnosed, fixed and regression-verified; the
complete trail is in `.rs-memory/ERROR_HISTORY.md` (E-001 … E-009) and `worklog.md`.
