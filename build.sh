#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if [[ "$(uname -m)" != "x86_64" ]]; then
  echo "CopperBarsOS requires an x86_64 build host or an x86_64 container." >&2
  exit 1
fi

command -v lb >/dev/null || {
  echo "live-build is required. Install it with: sudo apt install live-build" >&2
  exit 1
}

rm -rf dist work cache .build
mkdir -p dist

export LB_AUTO_BUILD=1

lb config \
  --architecture amd64 \
  --distribution stable \
  --archive-areas "main contrib non-free non-free-firmware" \
  --binary-images iso-hybrid \
  --bootappend-live "boot=live components quiet splash locales=tr_TR.UTF-8 keyboard-layouts=tr timezone=Europe/Istanbul" \
  --debian-installer none \
  --apt-recommends true \
  --linux-flavours amd64 \
  --firmware-binary true \
  --firmware-chroot true \
  --iso-application "CopperBarsOS" \
  --iso-publisher "CopperBarsOS Project" \
  --iso-volume "COPPERBARSOS" \
  --memtest none

lb build

ISO="live-image-amd64.hybrid.iso"
if [[ ! -f "$ISO" ]]; then
  echo "live-build completed but $ISO was not produced." >&2
  exit 2
fi

mv "$ISO" dist/CopperBarsOS-x86_64.iso
sha256sum dist/CopperBarsOS-x86_64.iso > dist/CopperBarsOS-x86_64.iso.sha256

printf '\nCopperBarsOS ISO ready:\n  %s\n  %s\n' \
  "dist/CopperBarsOS-x86_64.iso" \
  "dist/CopperBarsOS-x86_64.iso.sha256"
