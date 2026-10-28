#!/usr/bin/env bash
# Build the source release archive + SHA-256 checksum.
# Prefers `git archive` (tracked files only); falls back to a python zipfile
# walk with exclusion rules. Output: artifacts/release/<name>.zip + .sha256
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

VERSION="$(tr -d '[:space:]' < "$REPO_ROOT/VERSION")"
OUT_DIR="$REPO_ROOT/artifacts/release"
mkdir -p "$OUT_DIR"
BASE="rs-windows-cloud-workspace-v$VERSION"
ZIP="$OUT_DIR/$BASE.zip"
SHA_FILE="$ZIP.sha256"

if git -C "$REPO_ROOT" rev-parse HEAD >/dev/null 2>&1 \
    && git -C "$REPO_ROOT" archive --format=zip --prefix="$BASE/" -o "$ZIP" HEAD; then
    echo "archive built via git archive"
else
    python3 - "$ZIP" "$REPO_ROOT" "$BASE" <<'PYEOF'
import os
import sys
import zipfile

out, root, prefix = sys.argv[1], sys.argv[2], sys.argv[3]
EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache", "node_modules", ".venv"}
EXCLUDE_FILES = {".DS_Store", "Thumbs.db"}
count = 0
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for name in sorted(files):
            if name in EXCLUDE_FILES:
                continue
            full = os.path.join(base, name)
            rel = os.path.relpath(full, root)
            zf.write(full, os.path.join(prefix, rel))
            count += 1
print(f"packaged {count} files -> {out}")
PYEOF
fi

# checksum in `sha256sum -c` compatible format: "<hash>  <filename>"
(cd "$OUT_DIR" && sha256sum "$BASE.zip" > "$BASE.zip.sha256")
echo "archive: $ZIP"
echo "size: $(du -h "$ZIP" | awk '{print $1}')"
echo "sha256: $(awk '{print $1}' < "$SHA_FILE")"
echo "checksum file: $SHA_FILE"
echo "checksum verify:"
(cd "$OUT_DIR" && sha256sum -c "$BASE.zip.sha256")
