# PROJECT_CONTEXT — RS Windows Cloud Workspace

## Identity
- Project: RS Windows Cloud Workspace
- Founder & Developer: RAJSARASWATI JATAV (RS) — T3RMUXK1NG
- Plan version: V19 — RS Sovereign Autonomous Engineering System (preserved verbatim at repo root `PLAN.md`, SHA-256 `071d11a05996285ffb0cd30fba99f2a634967a94f568cfc096283ab9c7a0c987`)
- Development platform: chat.z.ai Linux sandbox (Debian 13, Python 3.12.16, 2 CPU, 4 GB RAM)
- Deployment platform: free GitHub-hosted Windows runners (GitHub Actions)

## Mission
Transform this repository into a complete, genuinely functional Windows cloud development and
automation system: real source code, real tests, real workflows, verifiable evidence — no mocks
substituted for deliverables, no invented results.

## Hard constraints (from PLAN.md §5)
- Free GitHub Actions infrastructure only; no personal hardware, no paid VPS, no self-hosted runners
- Real Windows execution happens on GitHub-hosted runners after owner approval and push
- NO persistent personal RDP hosting on GitHub-hosted runners; Windows automation is clearly
  distinguished from interactive remote desktop access (explicit non-goal)

## X-Lite integration scope (PLAN.md §6)
- Archive: `[Windows X-Lite] Optimum 11 26H1 Pro v2.7z` on pixeldrain (file id `ZdPxkVmH`)
- Inspection ONLY: metadata, availability, authenticated download (optional key), resume/retry,
  SHA-256, safe 7z listing/extraction, ISO detection, Windows image metadata, compatibility report
- Never execute anything from the archive; never claim X-Lite can replace the runner OS

## Engineering policy
- Zero-fake policy: every recorded test status is PASS/FAIL/BLOCKED/NOT_RUN backed by evidence
- GitHub-last: no repository creation, commit, push, or publish before explicit owner approval
- Skills: platform `rs-memory` skill DOES NOT EXIST in this environment (verified by listing the
  installed skills directory on 2026-10-28T18:40Z). Per PLAN.md §1 fallback clause, this
  `.rs-memory/` local system is the equivalent implementation. No false invocation is claimed.
- Agents: platform provides a Task tool with a small set of subagent types (not 120-400). Actual
  count used is recorded in AGENT_REGISTRY.md. Shell processes are never reported as agents.

## Memory maintenance protocol
Update CURRENT_STATE.md, WAVE_HISTORY.md, COMPLETED.md, PENDING.md, BLOCKERS.md,
ERROR_HISTORY.md and checkpoints/ after every meaningful wave group.
