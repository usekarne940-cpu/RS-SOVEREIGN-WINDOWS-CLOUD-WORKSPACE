# RS Windows Cloud Workspace

A complete Windows cloud development and automation workspace that runs entirely on **free
GitHub-hosted Windows runners** — no personal laptop, no desktop, no paid VPS, no self-hosted
runner. Built by **RAJSARASWATI JATAV (RS) — T3RMUXK1NG** (see `PLAN.md`, preserved verbatim).

Local development and validation were completed in the chat.z.ai Linux sandbox; every
Windows-side component is wired into GitHub Actions workflows that execute it **for real**
after you push. Nothing was faked: locally-unverifiable checks are recorded as `NOT_RUN`
(locally) and scheduled on the runners.

## What it does

| Workflow | File | What runs | Runners |
|---|---|---|---|
| Environment audit | `.github/workflows/audit.yml` | OS/hardware/tool/network audit (JSON reports) | windows-latest + ubuntu-latest |
| Test suite | `.github/workflows/test.yml` | pytest matrix + PowerShell AST syntax gate + shellcheck + actionlint | windows-latest + ubuntu-latest |
| Build & package | `.github/workflows/build.yml` | full validation + source archive (+ GitHub Release on `v*` tags) | ubuntu-latest |
| GUI automation | `.github/workflows/gui.yml` | winget app installs + GUI smoke tests (launch, SendKeys, verify, screenshot) | windows-latest |
| Screenshots | `.github/workflows/screenshots.yml` | desktop screenshot capture | windows-latest |
| X-Lite inspection | `.github/workflows/xlite-inspection.yml` | Windows X-Lite archive analysis: availability, SHA-256, safe 7z listing, ISO detection — **analysis only** | windows-latest |
| Cleanup | `.github/workflows/cleanup.yml` | guarded workspace cleanup (weekly schedule + manual) | both |

## Repository layout

```
.github/workflows/   7 GitHub Actions workflows (see table above)
.rs-memory/          project memory: state, waves, decisions, blockers, checkpoints
scripts/powershell/  Windows automation (Common.psm1 + 8 task scripts)
scripts/python/      cross-platform tooling (x-lite inspector, linters, scanners, orchestrator)
scripts/linux/       Linux automation (audit, bootstrap, tests, cleanup, packaging)
applications/        GUI test app specs (notepad, calculator, explorer)
automation/tasks/    10 JSON task definitions + run_task.py cross-OS dispatcher
tests/               unit / integration / workflow / security / gui contract suites (159 tests)
config/              applications (winget), settings, xlite source config
reports/             generated evidence (local-validation, xlite-probe, ...)
artifacts/           runtime outputs (screenshots, x-lite workdir, release archives)
docs/                plan analysis, requirements matrix, roadmap, acceptance criteria,
                    setup, testing, security, troubleshooting
```

## Quick start (after pushing to GitHub)

1. Push this repository to a **private** GitHub repository (see `docs/SETUP.md`).
2. Optional: add the `PIXELDRAIN_API_KEY` secret if the X-Lite file ever requires authentication.
3. Run workflows from the **Actions** tab (`workflow_dispatch`), or let `test.yml` run on push.
4. Download evidence artifacts (audit JSON, JUnit XML, screenshots, inspection reports).

Cost note (free tier): GitHub-hosted **Windows minutes bill at 2x**. A public repository gets
unlimited Actions minutes; a private repository uses your 2,000 min/month free quota
(Windows jobs consume it at double rate — the default suite here needs well under an hour).

## Local development (Linux or Windows)

```bash
bash scripts/linux/bootstrap.sh        # install pytest + PyYAML
bash scripts/linux/run_tests.sh        # full validation -> reports/LOCAL-VALIDATION.md
python scripts/python/run_task.py --list           # list automation tasks
python scripts/python/run_task.py --run xlite-probe --dry-run
```

## Security posture

- Least-privilege `permissions:` on every workflow (job-scoped `contents: write` only for releases)
- Single optional secret (`PIXELDRAIN_API_KEY`), never echoed, redacted in reports
- X-Lite pipeline is **inspection/analysis only** — the archive is never executed, never booted,
  and can never replace the runner OS; extraction is traversal-guarded
- **No RDP/remote-desktop/tunnel code** — Windows automation (tests, GUI, screenshots) is
  fundamentally different from interactive remote desktop access, which is an explicit non-goal
- No `pull_request_target`, no untrusted-context interpolation into shell blocks, pinned actions

Details: `docs/SECURITY.md`. Testing and evidence model: `docs/TESTING.md`.

## Verified status (local run)

- 159 pytest tests passed (locally), 2 network-marked tests deselected by default
- Orchestrator gate: 205 PASS / 0 FAIL / 2 BLOCKED (external linters — run in CI instead)
- Live X-Lite evidence: file available, 2,555,783,617 bytes, genuine 7z signature, HTTP 206
  range support (see `reports/xlite-probe.json`)
- Windows execution: scheduled on GitHub runners (recorded NOT_RUN locally, never faked)

## License

MIT — © 2026 RAJSARASWATI JATAV (RS). See `LICENSE`.
