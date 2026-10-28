#!/usr/bin/env bash
# Install development requirements (pytest, PyYAML).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$REPO_ROOT"
python3 -m pip install --quiet --disable-pip-version-warning \
    -r scripts/python/requirements.txt
python3 -c "import yaml; print('pyyaml', yaml.__version__)"
python3 -c "import pytest; print('pytest', pytest.__version__)"
echo "bootstrap complete"
