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

VERSION="$(tr -d '\r\n' < VERSION)"
if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Invalid VERSION: $VERSION" >&2
  exit 1
fi

rm -rf dist cache
rm -f live-image-amd64.hybrid.iso
mkdir -p dist

# Debian 13 (Trixie) is the stable base used by CopperBarsOS. Pinning the
# distribution avoids accidentally building from a moving testing/unstable
# target on a future builder.
lb config \
  --architecture amd64 \
  --distribution trixie \
  --archive-areas "main contrib non-free non-free-firmware" \
  --binary-images iso-hybrid \
  --bootappend-live "boot=live components locales=tr_TR.UTF-8 keyboard-layouts=tr timezone=Europe/Istanbul" \
  --debian-installer none \
  --apt-recommends true \
  --linux-flavours amd64 \
  --firmware-binary true \
  --firmware-chroot true \
  --iso-application "CopperBarsOS" \
  --iso-publisher "CopperBars Project" \
  --iso-volume "COPPERBARSOS" \
  --memtest none

lb build

ISO="live-image-amd64.hybrid.iso"
if [[ ! -s "$ISO" ]]; then
  echo "live-build completed but $ISO was not produced." >&2
  exit 2
fi

mv "$ISO" "dist/CopperBarsOS-x86_64.iso"
sha256sum "dist/CopperBarsOS-x86_64.iso" > "dist/CopperBarsOS-x86_64.iso.sha256"
printf '%s\n' "$VERSION" > "config/includes.chroot/opt/copperbars/version"

printf '\nCopperBarsOS ISO ready:\n  %s\n  %s\n' \
  "dist/CopperBarsOS-x86_64.iso" \
  "dist/CopperBarsOS-x86_64.iso.sha256"
