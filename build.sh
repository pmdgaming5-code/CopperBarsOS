#!/usr/bin/env bash
set -euo pipefail

# live-build needs root privileges for chroot, mount and filesystem operations.
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
  echo "live-build is required." >&2
  exit 1
}

# Debian Trixie's live-build is the supported builder. Fail early instead of
# accidentally using an older host distro implementation with different CLI semantics.
lb_version="$(lb --version 2>&1 | head -n1)"
case "$lb_version" in
  *3.0~a5*) ;;
  *)
    echo "Unsupported live-build: $lb_version" >&2
    echo "CopperBarsOS requires the Debian Trixie live-build package (1:20250505+deb13u1 or newer)." >&2
    exit 1
    ;;
esac

# Remove generated state while preserving the checked-in CopperBarsOS config tree.
rm -rf dist work cache .build chroot binary
rm -f config/binary config/bootstrap config/chroot config/common config/source
mkdir -p dist

export LB_AUTO_BUILD=1
export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-0}"

DEBIAN_MIRROR="https://deb.debian.org/debian"
DEBIAN_SECURITY_MIRROR="https://deb.debian.org/debian-security"

# Debian Trixie is the single source of truth for all live-build CLI options.
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
  --memtest none \
  --uefi-secure-boot auto

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
