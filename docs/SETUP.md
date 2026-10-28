# SETUP — RS Windows Cloud Workspace

## Prerequisites

- A GitHub account. The free tier is sufficient: GitHub-hosted `windows-latest` and
  `ubuntu-latest` runners are used. No personal hardware, no VPS, no self-hosted runner.
- Python 3.12+ only if you want to run the local tooling on your own machine.

## Step 1 — Create the repository (after approval, per PLAN.md §11)

1. Create a **private** repository on GitHub (e.g. `rs-windows-cloud-workspace`).
2. Push this source tree:

```bash
cd rs-windows-cloud-workspace
git init
git add .
git commit -m "RS Windows Cloud Workspace v1.0.0"
git remote add origin git@github.com:<you>/rs-windows-cloud-workspace.git
git branch -M main
git push -u origin main
```

(The source freeze in this workspace already performed `git init` + a local commit before
packaging — if you received the source archive, extract it and skip straight to `git remote
add` + `git push`.)

## Step 2 — Optional secret

Settings → Secrets and variables → Actions → New repository secret:

- Name: `PIXELDRAIN_API_KEY`
- Value: your pixeldrain API key (only needed if the X-Lite file ever requires authentication;
  current live checks show anonymous access works)

No other secrets are referenced anywhere in this repository.

## Step 3 — Run the workflows (Actions tab)

Every workflow also has `workflow_dispatch` (manual "Run workflow" button):

| Workflow | Suggested first run | What you get |
|---|---|---|
| `RS Test Suite` | automatic on push | pytest results on windows-latest AND ubuntu-latest, PowerShell AST syntax gate, shellcheck + actionlint |
| `RS Environment Audit` | manual | real Windows audit JSON (OS, CPU, RAM, disks, tools, network) |
| `RS Screenshot Capture` | manual | desktop PNG + visible window list |
| `RS GUI Automation` | manual | winget installs + GUI smoke tests + screenshots |
| `RS X-Lite Inspection` | manual, mode `probe` first, then `full` | availability probe / full download + SHA-256 + 7z listing + ISO detection report (analysis results only — the archive itself is never uploaded) |
| `RS Workspace Cleanup` | manual (weekly schedule built in) | cleanup reports |

## Step 4 — Release (optional)

```bash
git tag v1.0.0
git push origin v1.0.0
```

`build.yml` then runs full validation, builds the source archive and creates a GitHub Release
with the archive and its SHA-256 checksum attached.

## Local development

```bash
bash scripts/linux/bootstrap.sh     # pytest + PyYAML
bash scripts/linux/run_tests.sh     # everything: imports, configs, bash -n, PowerShell
                                    # static validation, workflow contracts, secret scan, pytest
```

Windows machines: `pwsh ./scripts/powershell/Invoke-WindowsTests.ps1` (installs requirements,
runs pytest with JUnit output). Cross-platform task runner:

```bash
python scripts/python/run_task.py --list
python scripts/python/run_task.py --run local-checks
python scripts/python/run_task.py --run gui-test    # BLOCKED (exit 2) on non-Windows — by design
```

## Cost control

- Windows minutes bill at **2x** on private repos. Public repos: Actions are free.
- All artifact uploads use short retention (3–14 days) and all jobs set `timeout-minutes`.
- `concurrency` groups cancel superseded runs of the same workflow.

## Where evidence lands

- Local runs: `reports/local-validation.json`, `reports/LOCAL-VALIDATION.md`
- CI runs: workflow artifacts (audit JSON, JUnit XML, screenshots, inspection reports)
