# DECISIONS

| ID | Decision | Rationale | Date |
|----|----------|-----------|------|
| D-001 | Implement `.rs-memory/` local system instead of platform skill | Skill verified absent; PLAN.md §1 fallback clause | 2026-10-28 |
| D-002 | Python tooling is stdlib-first (urllib, not requests) | Zero external runtime deps; PyYAML only for lint tooling | 2026-10-28 |
| D-003 | Local X-Lite evidence = live metadata + 64 KB header probe; full download runs on Windows runner | Sandbox disk/bandwidth; inspection pipeline belongs where it executes | 2026-10-28 |
| D-004 | Pixeldrain client sends `Accept: application/json` and validates content-type on metadata calls | Live probe showed default curl Accept returns raw 7z bytes; JSON must be enforced and verified | 2026-10-28 |
| D-005 | GUI tests are best-effort per app; script exits non-zero only if ALL apps fail | Windows runner GUI availability varies; honest partial-credit reporting | 2026-10-28 |
| D-006 | App installs use winget (present on GitHub Windows runners), never choco dependency | Fewer deps; winget is preinstalled | 2026-10-28 |
| D-007 | Release archive produced via `git archive` (fallback python zipfile with exclusions) | Clean tracked-file source, respects .gitignore semantics | 2026-10-28 |
| D-008 | Local `git init` + commit allowed pre-approval; only push/publish is gated | GitHub-last constrains the remote, not local version control | 2026-10-28 |
| D-009 | Workflow `on:` key handled as YAML 1.1 boolean gotcha in linter | PyYAML parses bare `on` as True; linter normalizes | 2026-10-28 |
| D-010 | Secret patterns built via string concatenation inside scanner | Prevents the scanner source from self-matching | 2026-10-28 |
| D-011 | Only optional secret is PIXELDRAIN_API_KEY; never printed, redacted in reports | PLAN.md §6 no-hardcoded-secrets | 2026-10-28 |
| D-012 | Windows cost note documented (Windows minutes bill at 2x; public repos run free) | Free-tier engineering honesty | 2026-10-28 |
