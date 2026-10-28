# PENDING

## Awaiting owner approval (PLAN.md §11 — cannot proceed autonomously)
- [ ] Owner approval for GitHub deployment
- [ ] GitHub repository creation (private, least-privilege)
- [ ] First push (local commits d8876fb + 6e34d1c ready on local `main`)
- [ ] Optional: add `PIXELDRAIN_API_KEY` secret (currently not required — anonymous access works)

## Executes on GitHub runners after push (WG gates in docs/ACCEPTANCE-CRITERIA.md)
- [ ] test.yml: pytest matrix (windows-latest + ubuntu-latest) — real Windows Python execution
- [ ] test.yml: PowerShell AST syntax gate (Test-Syntax.ps1) + shellcheck + actionlint (lint-external)
- [ ] audit.yml: real Windows system audit JSON artifact
- [ ] gui.yml: winget installs + GUI smoke tests + screenshots
- [ ] screenshots.yml: desktop PNGs
- [ ] xlite-inspection.yml mode=probe, then mode=full (download + SHA-256 + 7z listing + ISO
      detection; after the first full run, pin the measured SHA-256 in config/xlite.json
      expected_sha256 for permanent integrity pinning)
- [ ] cleanup.yml: scheduled + manual cleanup
- [ ] build.yml: release archive artifact; GitHub Release on v* tag (optional)

## No other local work pending
All locally executable gates are green (217 PASS / 0 FAIL / 2 BLOCKED — the 2 BLOCKED gates
are the external linters, which execute in CI instead). Detailed evidence:
reports/local-validation.json + reports/LOCAL-VALIDATION.md + .rs-memory/TEST_RESULTS.md.
