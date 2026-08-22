#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
VERSION="$(tr -d '\r\n' < VERSION)"
mkdir -p dist

case "$VERSION" in
  [0-9]*.[0-9]*.[0-9]*) ;;
  *) echo "Invalid VERSION: $VERSION" >&2; exit 2 ;;
esac

BUNDLE="dist/CopperBarsOS-${VERSION}-update.tar.gz"
rm -f "$BUNDLE" "$BUNDLE.sha256"

# Only ship the OS's own overlay. No arbitrary repository files are included.
# Keep this manifest aligned with the image's built-in CopperBars desktop.
tar -czf "$BUNDLE" \
  -C config/includes.chroot \
  opt/copperbars \
  etc/systemd/system/copper-ai.service \
  etc/systemd/system/copper-firstboot.service \
  etc/xdg/autostart/copperbars-desktop-setup.desktop \
  etc/skel/.config/gtk-3.0/gtk.css \
  usr/local/bin/copper-autostart \
  usr/local/bin/copper-firstboot \
  usr/local/bin/copper-model-setup \
  usr/local/bin/copper-exe-handler \
  usr/local/bin/copperbars-release-updater \
  usr/local/bin/copperbars-desktop-setup \
  usr/local/bin/copperium-spotlight \
  usr/share/copperbars/panel/config.txt \
  usr/share/applications/copper-assistant.desktop \
  usr/share/applications/copper-center.desktop \
  usr/share/applications/copper-store.desktop \
  usr/share/applications/copper-windows.desktop \
  usr/share/applications/copper-updates.desktop \
  usr/share/applications/copper-diagnostics.desktop \
  usr/share/applications/copper-settings.desktop \
  usr/share/applications/copper-files.desktop

sha256sum "$BUNDLE" > "$BUNDLE.sha256"
printf 'Update bundle: %s\nChecksum: %s\n' "$BUNDLE" "$BUNDLE.sha256"
