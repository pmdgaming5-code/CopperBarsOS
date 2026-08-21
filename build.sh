#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if [[ "$(uname -m)" != "x86_64" ]]; then
  echo "CopperBarsOS requires an x86_64 build host or an x86_64 container." >&2
  exit 1
fi

command -v lb >/dev/null || { echo "live-build is required." >&2; exit 1; }

rm -rf dist work cache
mkdir -p dist

lb config \
  --architecture amd64 \
  --distribution stable \
  --archive-areas "main contrib non-free non-free-firmware" \
  --binary-images iso-hybrid \
  --bootappend-live "boot=live components quiet splash" \
  --debian-installer none \
  --apt-recommends true \
  --linux-flavours amd64 \
  --iso-application "CopperBarsOS" \
  --iso-publisher "CopperBarsOS Project" \
  --iso-volume "COPPERBARSOS"

lb build
mv live-image-amd64.hybrid.iso dist/CopperBarsOS-x86_64.iso
sha256sum dist/CopperBarsOS-x86_64.iso > dist/CopperBarsOS-x86_64.iso.sha256

echo "Built: dist/CopperBarsOS-x86_64.iso"
