# CopperBarsOS

CopperBarsOS is a 64-bit x86_64 Debian Live-based desktop operating system designed around a local-first AI assistant named **Copper**.

## Included

- x86_64 hybrid BIOS/UEFI-friendly Live ISO workflow
- XFCE desktop with LightDM login
- NetworkManager, PipeWire/WirePlumber, removable media support
- Firefox, Thunar, archive tools, terminal, hardware diagnostics and system utilities
- Calamares installer launcher for installing the live system to disk
- Copper AI daemon isolated in a dedicated `copper` service account
- Local AI HTTP gateway bound only to `127.0.0.1:8765`
- Copper first-run model selector
- Copper Center system/AI/hardware/network dashboard
- Copper Store with curated APT applications
- Windows Compatibility Center
- Wine 64-bit + 32-bit multiarch support
- wine-binfmt for Windows executable integration
- Winetricks for compatibility components
- DXVK for Direct3D 8/9/10/11 through Vulkan
- vkd3d libraries for Direct3D 12 translation
- Per-application Wine prefixes
- One-click `.exe` launcher
- Automated Python, shell, JSON and policy validation

## Why Wine instead of a Microsoft Windows EXE runtime?

Microsoft provides WSL as a way to run Linux inside Windows, and WSL can invoke Windows `.exe` files because the Windows host is still present. That is the opposite of what CopperBarsOS needs. CopperBarsOS therefore uses Wine, the standard Windows API compatibility layer for Linux. Wine translates Windows API calls to POSIX/Linux equivalents instead of requiring a full Windows installation.

## Windows application compatibility

CopperBarsOS aims for the highest practical compatibility available without bundling Windows itself. Wine is not a drop-in Windows kernel and cannot guarantee every Windows application will work. Applications that require unsupported Windows kernel drivers, certain DRM systems, some anti-cheat components or very specific proprietary Windows internals may still fail. Applications with standard Win32 APIs, common runtimes and supported Direct3D paths have a much better chance of working.

Each application launched through Copper gets its own Wine prefix under:

```text
~/.local/share/copperbars/wine/<application>
```

This avoids a single broken Wine configuration affecting every Windows application.

## Building the ISO

Use an x86_64 Debian/Ubuntu builder with `live-build`:

```bash
sudo apt update
sudo apt install -y live-build debootstrap squashfs-tools xorriso grub-pc-bin grub-efi-amd64-bin mtools dosfstools
chmod +x build.sh
./build.sh
```

The final image is written to:

```text
dist/CopperBarsOS-x86_64.iso
dist/CopperBarsOS-x86_64.iso.sha256
```

## Local AI

The first desktop session opens a Copper setup screen where the user can select a local model profile. The selection is stored in `/var/lib/copperbars/model.conf` and Copper reads that setting at runtime.

Ollama is supported as an optional local backend. Copper never silently uses a remote model; the API is bound to localhost and reports when no local model is actually connected.

## Copper Store

Copper Store uses the system APT package manager for installation and removal. The catalog is curated in `config/includes.chroot/opt/copperbars/apps.json` and includes ordinary Linux software plus Windows compatibility components such as Wine, Winetricks and DXVK.

## Security model

The Copper service runs as the unprivileged `copper` user with systemd hardening (`NoNewPrivileges`, `PrivateTmp`, `ProtectSystem`, `ProtectHome`) and only the local model/state paths are writable.

## Validation

GitHub Actions validates:

- Python syntax for all Copper components
- Shell syntax for build and hook scripts
- Store catalog JSON
- Required OS/AI/Windows compatibility files
- Local-only AI API policy
- Presence of the Wine/DXVK compatibility stack

## Current release status

This repository contains the source foundation and reproducible build definition. A release image still needs to be built and boot-tested on real x86_64 hardware/VMs because graphics drivers, Wi-Fi firmware, audio devices, GPU acceleration, Windows application compatibility and installer behavior require real runtime testing.
