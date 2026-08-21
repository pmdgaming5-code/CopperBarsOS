# CopperBarsOS

64-bit Linux desktop operating system with a local AI-first first-boot experience.

## Goals
- x86_64 bootable Linux ISO
- Lightweight graphical desktop
- First-boot local AI assistant named Copper
- No cloud account required for core assistant functions
- Offline-friendly system administration
- Reproducible ISO builds

## Architecture
CopperBarsOS is built as a Debian Live-based x86_64 image. The AI layer is isolated from the desktop and communicates through a local HTTP API. Model files are deliberately not committed to Git because they are large binaries.

## Build
On a Debian/Ubuntu x86_64 build host:

```bash
sudo apt update
sudo apt install -y live-build debootstrap squashfs-tools xorriso grub-pc-bin grub-efi-amd64-bin mtools dosfstools
./build.sh
```

The ISO is written to `dist/CopperBarsOS-x86_64.iso`.

## Local AI
The first boot starts `copper-ai.service`. If no model is installed, Copper opens a setup screen and explains how to place a compatible GGUF model in `/opt/copperbars/models/`. The system never pretends a model is available when it is not.

## Status
Initial OS foundation and build system. Hardware-specific GPU acceleration and model packaging remain configurable because they depend on the target machine.
