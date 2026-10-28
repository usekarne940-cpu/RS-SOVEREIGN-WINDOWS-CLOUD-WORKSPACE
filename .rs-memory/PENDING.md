# PENDING

## Awaiting owner approval (cannot proceed autonomously — PLAN.md §11)
- Owner approval for GitHub deployment
- GitHub repository creation (private, least-privilege) — after approval only
- First commit and push — after approval only
- Real Windows Actions execution (all 7 workflows) — after push
- Optional: add `PIXELDRAIN_API_KEY` secret to the repository

## Pending after push (executes on GitHub runners)
- [ ] test.yml: pytest on windows-latest + ubuntu-latest (real Windows Python execution)
- [ ] test.yml: PowerShell AST syntax gate on Windows (Test-Syntax.ps1)
- [ ] audit.yml: Windows system audit report artifact
- [ ] gui.yml: winget installs + GUI smoke tests + screenshot artifacts
- [ ] screenshots.yml: desktop screenshots
- [ ] xlite-inspection.yml mode=full: full download, SHA-256, 7z listing, ISO detection, image metadata
- [ ] cleanup.yml: scheduled cleanup run
- [ ] build.yml: release packaging (+ GitHub Release when a v* tag is pushed)

## Pending locally (tracked in current waves)
- [ ] External linters actionlint/shellcheck — fetch attempts; fallback validators if unreachable
- [ ] Full test suite green run recorded in reports/TEST-RESULTS.md
- [ ] Parallel review agents (security / test audit / docs audit)
- [ ] Source freeze + package + SHA-256 into /home/z/my-project/download/
