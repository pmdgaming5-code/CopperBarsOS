# CopperBarsOS

CopperBarsOS is a 64-bit x86_64 Debian 13 (Trixie) Live-based desktop operating system designed around a local-first AI assistant named **Copperium AI**.

## Included

- x86_64 hybrid BIOS/UEFI Live ISO workflow
- XFCE desktop with LightDM login
- NetworkManager, PipeWire/WirePlumber, removable media support
- Firefox ESR, Thunar, archive tools, terminal, hardware diagnostics and system utilities
- Calamares installer launcher
- Copperium AI local assistant and localhost-only AI gateway
- CopperBars Center system, AI, hardware and network dashboard
- CopperBars Store curated APT software center
- CopperBars Update with APT updates and signed-by-checksum GitHub Release updates
- CopperBars Diagnostics, Settings and Windows Compatibility tools
- Wine 64-bit plus 32-bit multiarch support
- wine-binfmt for Windows executable integration
- Winetricks for compatibility components
- DXVK for Direct3D 8/9/10/11 through Vulkan
- vkd3d libraries for Direct3D 12 translation
- Per-application Wine prefixes and one-click `.exe` launching
- Automated syntax, policy, artifact, checksum and QEMU smoke validation

## Base system

CopperBarsOS is built from Debian 13 (Trixie) packages with `live-build`. The build configuration is pinned to `trixie` rather than the moving `stable` alias so that the ISO base stays reproducible throughout the release cycle.

## Local AI

Copperium AI runs locally. The gateway binds only to `127.0.0.1:8765` and reports the real model/backend state. Ollama can be used as the local backend, and the first-run setup lets the user select a local model profile.

No model weights are stored in Git.

## Windows applications

CopperBarsOS uses Wine rather than bundling Windows. Wine provides the Windows API compatibility layer; 32-bit and 64-bit components are both installed. DXVK and vkd3d provide the supported Direct3D translation paths. Each application can have its own Wine prefix so a broken configuration does not affect unrelated applications.

Compatibility is not identical to a native Windows installation: software that depends on unsupported Windows kernel drivers, some DRM systems, certain anti-cheat components or Windows-only internals can still fail.

## CopperBars Update

CopperBars Update checks the latest public GitHub Release from this repository. An OS release is installable only when the release provides both:

- `CopperBarsOS-<version>-update.tar.gz`
- `CopperBarsOS-<version>-update.tar.gz.sha256`

The update package is downloaded, SHA-256 verified in the desktop application, verified again by the privileged updater, checked for unsafe archive paths, staged, backed up and then applied as a restricted overlay. A rollback backup is kept under `/var/backups/copperbars/`.

APT package updates and CopperBarsOS release updates are separate operations.

## Building

Use an x86_64 Debian/Ubuntu builder with live-build:

```bash
sudo apt update
sudo apt install -y live-build debootstrap squashfs-tools xorriso grub-pc-bin grub-efi-amd64-bin mtools dosfstools qemu-system-x86 qemu-utils ovmf shellcheck python3
./build.sh
```

Artifacts:

```text
dist/CopperBarsOS-x86_64.iso
dist/CopperBarsOS-x86_64.iso.sha256
```

The GitHub Actions ISO workflow performs the same validation, creates the update bundle and runs a BIOS/QEMU smoke test.

## Release model

The release workflow is tag-based. A tag such as `v0.9.0` must match the repository `VERSION` file exactly. The workflow builds the ISO, creates the update bundle, verifies all checksums, runs the QEMU smoke test and publishes the artifacts to the GitHub Release.

## Validation

CI validates:

- executable build/hook scripts
- Bash syntax and ShellCheck for build helpers
- Python syntax
- Store catalog JSON
- Copperium AI localhost policy
- Wine 32/64-bit compatibility stack
- ISO existence, checksum and xorriso readability
- update bundle checksum
- QEMU BIOS boot smoke test

A physical hardware validation pass is still required for GPU drivers, firmware, Wi-Fi, suspend/resume and application-specific Windows compatibility.
