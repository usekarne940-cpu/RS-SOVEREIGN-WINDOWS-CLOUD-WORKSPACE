# TROUBLESHOOTING

## Local development

**`ModuleNotFoundError: xlite_inspector` (or any scripts/python module)**
Run from the repository root; the test conftest and the orchestrator inject
`scripts/python` into `PYTHONPATH`. If calling modules manually:

```bash
PYTHONPATH=scripts/python python scripts/python/xlite_inspector.py --help
```

**pytest hangs or times out**
The default suite deselects network tests (`-m "not network"`). Any test that touches the
network must carry the `network` marker and use bounded, size-capped reads (see
`docs/TESTING.md` and ERROR-HISTORY E-003 for why unbounded reads are dangerous on this
endpoint).

**`run_all_checks.py` reports BLOCKED for shellcheck/actionlint**
Expected in restricted environments. Both linters execute in CI (`test.yml` → `lint-external`).
Install them locally (`apt install shellcheck`, or download actionlint) to unblock locally.

## GitHub Actions

**Workflows don't appear in the Actions tab**
Push to the default branch (`main`) at least once; `workflow_dispatch` triggers appear after
the workflow file exists on that branch.

**GUI tests fail or screenshot is black (gui.yml / screenshots.yml)**
GitHub Windows runners execute in an interactive session with a desktop, but display
availability can vary transiently. The GUI suite is best-effort per app (D-005): partial
failures are reported with per-step evidence in `reports/gui-test-results.json`; the job only
fails when EVERY app fails. Re-run once before investigating deeper.

**winget install fails**
Winget source indexes can lag behind. Check `reports/install-applications.json` for which app
and exit code. Optional apps failing does not fail the job; required apps (Git, Python, 7-Zip)
do — verify the package id still exists (`winget search`).

**`xlite-inspection.yml` mode=full fails with "Insufficient disk space"**
The runner needs ≥ 15 GB free for the 2.55 GB archive + extracted ISO + scratch. The disk
guard reads `min_free_disk_gb` from `config/xlite.json`. Free runner disk (the cleanup job
removes prior artifacts) or raise the guard if your archive is larger.

**Download interrupted mid-inspection**
The inspector resumes: re-running mode=full continues from the partial file via HTTP Range
(live-verified `Accept-Ranges: bytes`, HTTP 206). If the server ever stops honoring ranges,
the partial file is discarded automatically and the download restarts.

**`PIXELDRAIN_API_KEY` rejected (HTTP 401/403)**
The inspector exits with code 2 (BLOCKED) and never logs the key. Verify the secret name is
exactly `PIXELDRAIN_API_KEY` and the key is valid. Current live checks (2026-10-28) show the
file downloads anonymously, so the key is likely unnecessary.

**PowerShell AST gate fails on Windows (Test-Syntax.ps1)**
`reports/powershell-syntax.json` lists the exact file, line and column of every parse error.
The same scripts already pass the static heuristic validator locally, so a failure here means
a construct only the real parser catches (e.g. automatic-variable misuse) — fix the reported
line and re-run.

**Windows job minutes drain quickly**
Windows minutes bill at 2x on private repositories. Make the repository public (free Actions)
or trim: `audit.yml` and `screenshots.yml` are the cheapest; `xlite-inspection.yml` mode=full
is the most expensive (up to 120 min).

**A test failed — where is the evidence?**
Local: `reports/local-validation.json` (8-field records) and `reports/LOCAL-VALIDATION.md`.
CI: the workflow's uploaded artifacts (JUnit XML, JSON reports, screenshots). Nothing is
suppressed; BLOCKED/NOT_RUN statuses explain exactly what did not run and why.
