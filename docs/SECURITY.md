# SECURITY — RS Windows Cloud Workspace

## Scope and explicit non-goals

This workspace performs **Windows automation on ephemeral GitHub-hosted runners**: running
tests, installing development tools with winget, GUI smoke tests, screenshots, artifact
management, and static inspection of a user-provided archive. It is NOT, and does not
contain, any of the following (verified by contract tests in `tests/security/`):

- No persistent personal RDP hosting, no RustDesk/AnyDesk, no SSH/VNC servers, no tunnels
- No interactive remote desktop access of any kind — automation and remote desktop are
  fundamentally different activities (PLAN.md §5)
- No attempt to replace or modify the operating system of a GitHub-hosted runner
- No execution of anything extracted from the Windows X-Lite archive

## GitHub Actions hardening

- Least privilege: every workflow declares `permissions: contents: read`; the only elevation
  is a job-scoped `contents: write` on the tag-gated release job in `build.yml`
- No `pull_request_target` anywhere; no untrusted event context (`github.event.pull_request.*`,
  issue titles/comments) is interpolated into `run:` blocks
- All third-party actions are version-pinned to major tags
  (`actions/checkout@v4`, `actions/setup-python@v5`, `actions/upload-artifact@v4`,
  `actions/download-artifact@v4`, `softprops/action-gh-release@v2`); pinning to full commit
  SHAs is available as further optional hardening (documented decision — the linter's R7 rule
  enforces at least major-version tags and rejects floating refs like `@main`)
- The external actionlint binary is installed in CI via the official checksum-verifying
  installer, pinned to v1.7.12
- Every job sets `timeout-minutes` (≤ 120, well under the 360 limit)
- Every workflow uses a `concurrency` group; long-running inspections are never cancelled
  mid-flight (`cancel-in-progress: false` on cleanup/xlite only)
- All artifact uploads set short `retention-days` and run `if: always()` for evidence

## Secrets

- Exactly one secret is referenced in the entire repository: `PIXELDRAIN_API_KEY` (optional)
- It is passed to the inspection job via `env:` and read ONLY from the environment (the CLI
  never accepts it as a flag); no current code path logs or reports it — `xlite_inspector.redact`
  exists as defense-in-depth for any future error path that could embed authenticated URLs
- The secret scanner (`scripts/python/secret_scanner.py`) runs over the whole repository as a
  CI gate and must report zero ERROR findings; scanner rule patterns are constructed so the
  scanner source cannot self-match

## Windows X-Lite inspection safety (PLAN.md §6)

- The archive is inspected for analysis only: metadata, availability, SHA-256, safe listing,
  optional guarded extraction, ISO detection, image-marker reporting
- Extraction refuses archives whose listing contains traversal paths (`..`, absolute paths)
  and only ever extracts into a dedicated empty workdir
- Nothing extracted is ever executed: the inspector's only subprocess calls are `7z l` (list)
  and `7z x` (extract); `setup.exe` appears only inside the `WINDOWS_IMAGE_MARKERS`
  detection constant (pinned by `test_setup_exe_marker_is_detection_only`)
- The inspection report carries an explicit disclaimer that the image can never replace a
  GitHub-hosted runner's OS
- Licensing of the X-Lite image remains with Microsoft; you are responsible for having the
  rights to inspect the archive you pointed the tool at

## Local tooling safety

- `ps_validator` rejects `Invoke-Expression`/`iex` and execution-policy weakening in repo scripts
- Cleanup scripts delete only paths verified to be inside the repository root (guarded on
  both platforms)
- The task dispatcher (`run_task.py`) executes only command strings defined in the repository's
  own `automation/tasks/*.json` (trusted, version-controlled) and refuses OS-mismatched tasks
  with exit code 2 instead of silently skipping

## Verification

Security contract tests (`tests/security/test_security_contracts.py`) run in CI on every push
on both operating systems; a third-party security review pass (AGENT-01) was executed at code
freeze — see `.rs-memory/AGENT_REGISTRY.md`.
