# CopperBarsOS

**CopperBarsOS 0.9.0** is a 64-bit x86_64 Debian Live-based desktop operating system designed around a local-first AI experience.

## CopperBars experience

- **Copperium AI** — local AI assistant with Ollama-compatible backend
- **CopperBars Store** — curated Linux software center using APT
- **CopperBars Center** — system, hardware, network and AI dashboard
- **CopperBars Update** — APT updates plus GitHub Release-based CopperBarsOS updates
- **CopperBars Windows Center** — Wine/DXVK/vkd3d Windows application compatibility
- **CopperBars Diagnostics** — read-only hardware, graphics, audio, network, AI and Wine diagnostics
- **CopperBars Settings** and **CopperBars Files** launch points

## GitHub-based OS updates

CopperBars Update checks the public GitHub Releases API for `pmdgaming5-code/CopperBarsOS`.

A release can contain:

```text
CopperBarsOS-x86_64.iso
CopperBarsOS-x86_64.iso.sha256
CopperBarsOS-<version>-update.tar.gz
CopperBarsOS-<version>-update.tar.gz.sha256
```

The desktop updater downloads the update bundle, validates its SHA-256, validates archive paths, stages it in a temporary folder, requests administrator permission, creates a rollback backup under `/var/backups/copperbars/`, and then applies only the CopperBarsOS overlay. The privileged helper verifies the SHA-256 again before installation.

APT package updates and CopperBarsOS release updates are intentionally separate.

## Windows compatibility

CopperBarsOS uses Wine rather than a Microsoft Windows runtime. Wine is the Windows API compatibility layer for Linux; DXVK handles Direct3D 8/9/10/11 through Vulkan and vkd3d provides Direct3D 12 translation. Each application can use its own Wine prefix.

This aims for high practical compatibility, but it does not claim that every Windows application is identical to native Windows. Programs depending on unsupported Windows kernel drivers, certain DRM/anti-cheat mechanisms, or proprietary low-level Windows internals may still fail.

## Building

On an x86_64 Debian/Ubuntu builder:

```bash
sudo apt update
sudo apt install -y live-build debootstrap squashfs-tools xorriso grub-pc-bin grub-efi-amd64-bin mtools dosfstools
chmod +x build.sh tools/build-update-bundle.sh
./build.sh
./tools/build-update-bundle.sh
```

Output:

```text
dist/CopperBarsOS-x86_64.iso
dist/CopperBarsOS-x86_64.iso.sha256
dist/CopperBarsOS-0.9.0-update.tar.gz
dist/CopperBarsOS-0.9.0-update.tar.gz.sha256
```

## GitHub release automation

`.github/workflows/release.yml` builds the ISO, builds the verified update bundle, performs artifact checks, runs a QEMU BIOS smoke test and publishes the assets when a `vX.Y.Z` tag is pushed. The workflow is also manually runnable for CI artifact generation.

## Local AI

The first desktop session opens a CopperBars setup screen with several local model choices. The selected model is stored in `/var/lib/copperbars/model.conf` and Copperium AI reads it at runtime.

The AI gateway listens only on `127.0.0.1:8765` and reports its real local model state. No cloud account is required for the core assistant.

## Security

The Copperium AI service runs as an unprivileged `copper` account with systemd sandboxing. The release updater never executes arbitrary downloaded scripts; it accepts only the expected release bundle layout and verifies SHA-256 both before and after crossing the privilege boundary.

## Validation

GitHub Actions checks Python syntax, shell syntax, JSON, version consistency, CopperBars branding, Wine/DXVK support, release updater safety and the local-only AI policy. The build workflow additionally verifies the ISO checksum and boots it under QEMU for a short BIOS smoke test.

## Hardware testing note

A final desktop/driver/install experience still needs physical hardware testing because GPU drivers, Wi-Fi firmware, audio devices, suspend/resume, installer behavior and Windows application compatibility cannot be fully proven from source-only CI.
