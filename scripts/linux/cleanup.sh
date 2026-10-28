#!/usr/bin/env bash
# Workspace cleanup with guarded paths (Linux side).
# Every removed path is verified to be inside the repository root.
# Evidence: reports/cleanup-linux.json
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

log() { printf '%s [%s] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$1" "$2"; }

removed=0
remove_guarded() {
    local target="$1"
    local full
    full="$(readlink -f "$target" 2>/dev/null || echo "$target")"
    case "$full" in
        "$REPO_ROOT"/*)
            if [ -e "$full" ]; then
                rm -rf "$full"
                removed=$((removed + 1))
                log INFO "removed: $full"
            fi
            ;;
        *)
            log ERROR "refused (outside repo root): $full"
            exit 1
            ;;
    esac
}

remove_guarded "$REPO_ROOT/reports/tmp"
remove_guarded "$REPO_ROOT/artifacts/tmp"
remove_guarded "$REPO_ROOT/artifacts/xlite"
remove_guarded "$REPO_ROOT/.pytest_cache"

while IFS= read -r -d '' cache_dir; do
    remove_guarded "$cache_dir"
done < <(find "$REPO_ROOT" -type d -name '__pycache__' -print0 2>/dev/null)

python3 - "$removed" "$REPO_ROOT/reports/cleanup-linux.json" <<'PYEOF'
import datetime
import json
import sys

data = {
    "generated_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "removed_paths": int(sys.argv[1]),
}
with open(sys.argv[2], "w", encoding="utf-8") as handle:
    json.dump(data, handle, indent=2)
    handle.write("\n")
PYEOF

log INFO "cleanup complete ($removed paths removed)"
