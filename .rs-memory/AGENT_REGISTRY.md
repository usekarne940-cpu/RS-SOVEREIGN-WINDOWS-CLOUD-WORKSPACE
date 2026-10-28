# AGENT_REGISTRY

Honest registry. Shell processes, subshells and pytest workers are NOT agents and are never
counted here. Platform agent capacity: Task tool with a small set of subagent types — the
requested 120-400 workers exceed capacity (BLOCKERS.md B-02).

| Agent ID | Type | Responsibility | Isolated scope | Expected output | Status |
|----------|------|----------------|----------------|-----------------|--------|
| ORCH-MAIN | main orchestrator | All engineering waves, integration coordination, memory updates, packaging | Write access to entire repo | Complete verified source package | ACTIVE |
| AGENT-01 | Task subagent (general-purpose) | Independent security review (secrets, injection, least privilege, X-Lite safety) | READ-ONLY: full repo; may run read-only commands | Findings list with severity + file:line + fix recommendation | SCHEDULED (Wave 26-30) |
| AGENT-02 | Task subagent (general-purpose) | Independent test audit: run pytest, verify no fake/assert-true tests, coverage honesty, Windows-only tests correctly marked | READ-ONLY: tests/ + scripts/; may run pytest | Test audit verdict + gaps list | SCHEDULED (Wave 26-30) |
| AGENT-03 | Task subagent (general-purpose) | Documentation-reality audit: every doc claim traceable to a file/command; workflow steps match script paths | READ-ONLY: docs/ + .github/ + scripts/ | Doc accuracy findings | SCHEDULED (Wave 26-30) |

Parallelism policy: AGENT-01/02/03 launched concurrently in a single batch after local test
freeze; ORCH-MAIN integrates their findings (central integration coordinator per PLAN.md §3).
