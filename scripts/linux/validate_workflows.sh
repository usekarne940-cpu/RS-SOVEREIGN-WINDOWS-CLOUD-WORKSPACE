#!/usr/bin/env bash
# Workflow contract validation gate.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

python3 scripts/python/workflow_lint.py --workflows-dir .github/workflows
