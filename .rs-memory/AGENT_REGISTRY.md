# AGENT_REGISTRY

Honest registry. Shell processes, subshells and pytest workers are NOT agents and are never
counted here. Platform agent capacity: Task tool with a small set of subagent types — the
requested 120-400 workers exceeded capacity (BLOCKERS B-02); the maximum safe concurrency was
used: 1 orchestrator + 3 parallel review agents, launched in a single batch.

| Agent ID | Type | Responsibility | Outcome | Status |
|----------|------|----------------|---------|--------|
| ORCH-MAIN | main orchestrator | All 30 engineering waves, integration coordination, memory, packaging | Complete source freeze + delivered archive (SHA-256 0b4bee82...c52e3) | COMPLETE |
| AGENT-01 | Task subagent (general-purpose) | Independent security review (READ-ONLY: full repo + live probes) | VERDICT: PASS (0 CRITICAL/HIGH); 4 MEDIUM + 9 LOW/INFO findings -> all actionable items fixed with regression tests by ORCH-MAIN | COMPLETE |
| AGENT-02 | Task subagent (general-purpose) | Independent test audit (READ-ONLY: run pytest, hunt fake tests, coverage honesty) | First launch FAILED (upstream API 400, recorded E-011); retry SUCCEEDED. VERDICT: PASS — no fake tests; 4 non-blocking recommendations implemented | COMPLETE (after retry) |
| AGENT-03 | Task subagent (general-purpose) | Documentation-reality audit (READ-ONLY: every claim vs actual tree) | VERDICT: FAIL at audit time — 17 findings; all integrated by ORCH-MAIN, including root-causing finding 2 as a display-layer false positive (byte-verified with od -c) | COMPLETE (findings integrated) |

Total genuine agents: **4** (1 orchestrator + 3 subagents; AGENT-02 required one retry).
Read-only review scopes prevented write conflicts; ORCH-MAIN integrated all findings centrally
(central integration coordinator per PLAN.md §3).
