#!/usr/bin/env bash
# Full local validation run: pytest (non-network) + every static gate.
# Evidence: reports/local-validation.json + reports/LOCAL-VALIDATION.md
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

python3 -m pip install --quiet --disable-pip-version-warning \
    -r scripts/python/requirements.txt

RUN_ID="linux-run-$(date -u +%Y%m%dT%H%M%SZ)"
python3 scripts/python/run_all_checks.py --run-id "$RUN_ID"
