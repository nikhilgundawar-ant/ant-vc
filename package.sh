#!/usr/bin/env bash
# Build ant-vc.plugin: the installable plugin, without tests, golden data, build notes or git history.
set -euo pipefail
cd "$(dirname "$0")"
OUT="${1:-ant-vc.plugin}"
rm -f "$OUT"
zip -qr "$OUT" . -x ".git/*" ".gitignore" "evals/*" "*/__pycache__/*" "*.pyc" ".DS_Store" "*.plugin" "*.plugin.sha256" "package.sh" ".github/*" \
  "BUILD_LOG.md" "CLAUDE.md" "docs/*" "instinct-work/*" "home-db/*" "run/*" "setup-out/*"
SUM=$( (command -v sha256sum >/dev/null && sha256sum "$OUT" || shasum -a 256 "$OUT") | cut -d' ' -f1)
echo "$SUM  $(basename "$OUT")" > "$OUT.sha256"
echo "Built $OUT ($(du -h "$OUT" | cut -f1)), SHA-256 $SUM"
