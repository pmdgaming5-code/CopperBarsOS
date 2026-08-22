#!/usr/bin/env bash
set -euo pipefail

# live-build needs root privileges for chroot, mount and filesystem operations.
# Re-exec with sudo when invoked by a normal user so local builds are less error-prone.
if [[ "$(id -u)" -ne 0 ]]; then
  exec sudo -E -- "$0" "$@"
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if [[ "$(uname -m)" != "x86_64" ]]; then
  echo "CopperBarsOS requires an x86_64 build host or runner." >&2
  exit 1
fi

command -v lb >/dev/null || {
  echo "live-build is required. Install it with: sudo apt install live-build" >&2
  exit 1
}

rm -rf dist work cache .build
mkdir -p dist

# Keep the OS base reproducible against Debian Trixie.
# Explicit Debian mirrors are important when building from an Ubuntu GitHub runner;
# otherwise live-build may inherit the host's Ubuntu mirror configuration.
export LB_AUTO_BUILD=1
export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-0}"

DEBIAN_MIRROR="https://deb.debian.org/debian"
DEBIAN_SECURITY_MIRROR="https://deb.debian.org/debian-security"

lb config \
  --mode debian \
  --architecture amd64 \
  --distribution trixie \
  --distribution-chroot trixie \
  --distribution-binary trixie \
  --archive-areas "main contrib non-free non-free-firmware" \
  --mirror-bootstrap "$DEBIAN_MIRROR" \
  --mirror-chroot "$DEBIAN_MIRROR" \
  --mirror-binary "$DEBIAN_MIRROR" \
  --mirror-chroot-security "$DEBIAN_SECURITY_MIRROR" \
  --mirror-binary-security "$DEBIAN_SECURITY_MIRROR" \
  --binary-images iso-hybrid \
  --bootappend-live "boot=live components quiet splash locales=tr_TR.UTF-8 keyboard-layouts=tr timezone=Europe/Istanbul" \
  --debian-installer none \
  --apt-recommends true \
  --apt-secure true \
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
