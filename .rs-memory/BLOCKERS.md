# BLOCKERS

## B-01 — Platform `rs-memory` skill does not exist (RESOLVED VIA FALLBACK)
Requested invocation `[$rs-memory]/skills/rs-memory` is not among installed skills (verified
2026-10-28T18:40Z by listing the skills directory). PLAN.md §1 explicitly authorizes a local
equivalent; implemented as this `.rs-memory/` system. No invocation was claimed.

## B-02 — Requested 120-400 parallel agents exceed platform capacity (MITIGATED)
The platform's Task tool supports a small number of genuine subagent invocations (issued from the
main orchestrator), not hundreds of independent workers. Actual agents used: 1 orchestrator +
3 parallel review subagents (see AGENT_REGISTRY.md). Shell processes are NOT counted as agents.

## B-03 — No Windows runtime in the development sandbox (BY DESIGN, DEFERRED)
All Windows-side code (PowerShell suite, workflows) is statically validated locally; real
execution requires push to GitHub and the windows-latest runners. Zero Windows results are
invented locally (PLAN.md §9). Status: NOT_RUN locally, scheduled on runners.

## B-04 — pwsh not installed in sandbox (MITIGATED)
PowerShell validation uses a static heuristic validator locally (scripts/python/ps_validator.py)
plus the real AST parser gate on Windows runners (Test-Syntax.ps1 inside test.yml).

## B-05 — shellcheck / actionlint not installable in the sandbox (RESOLVED VIA CI)
Fetch attempts 2026-10-28T19:15-19:17Z: GitHub release-asset downloads return a
9-byte "Not Found" body through the sandbox proxy (github.com HTML responds,
release binaries are stripped). Resolution: both linters are wired into
test.yml job `lint-external` (ubuntu-latest, shellcheck preinstalled,
actionlint pinned v1.7.12) and execute for real on GitHub runners. Local
status remains honestly BLOCKED; project-internal validators (workflow_lint,
bash -n) are the local gates.

## B-06 — Full multi-GB X-Lite download deferred to Windows runner (ENGINEERING DECISION D-03)
Sandbox has 9.3 GB free disk and shared bandwidth; the inspection pipeline is designed for the
GitHub Windows runner (xlite-inspection.yml mode=full). Local evidence covers live metadata +
7z header verification (64 KB range probe).

## B-07 — GitHub credentials not present in sandbox (BY DESIGN, GITHUB-LAST)
Repository creation and push are intentionally gated behind explicit owner approval (PLAN.md §11).
