#!/usr/bin/env bash
# RS Linux environment audit — writes reports/linux-environment-audit.json
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
REPORT_DIR="$REPO_ROOT/reports"
mkdir -p "$REPORT_DIR"
LOG="$REPORT_DIR/linux-audit.log"

log() { printf '%s [%s] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$1" "$2" | tee -a "$LOG"; }

log INFO "Linux environment audit starting"

python3 - "$REPORT_DIR/linux-environment-audit.json" <<'PYEOF'
import datetime
import json
import os
import platform
import shutil
import sys

tools = ["git", "curl", "jq", "zip", "tar", "sha256sum", "unzip",
         "7z", "pwsh", "shellcheck", "actionlint"]
data = {
    "generated_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "platform": platform.platform(),
    "kernel": platform.release(),
    "python": sys.version.split()[0],
    "cpus": os.cpu_count(),
    "tools": {t: {"present": shutil.which(t) is not None} for t in tools},
}
try:
    target = "/home" if os.path.exists("/home") else "/"
    st = os.statvfs(target)
    data["disk_free_gb"] = round(st.f_bavail * st.f_frsize / 1024**3, 1)
except OSError:
    data["disk_free_gb"] = None

path = sys.argv[1]
with open(path, "w", encoding="utf-8") as handle:
    json.dump(data, handle, indent=2)
    handle.write("\n")
print("audit written:", path)
PYEOF

log INFO "Linux environment audit complete"
