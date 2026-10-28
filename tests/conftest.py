"""Shared pytest fixtures and path setup for RS Windows Cloud Workspace tests."""
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_PY = REPO_ROOT / "scripts" / "python"
if str(SCRIPTS_PY) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_PY))


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT
