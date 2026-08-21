# CopperBarsOS

CopperBarsOS is a 64-bit x86_64 Debian Live-based desktop operating system designed around a local-first AI assistant named **Copper**.

## What is included

- x86_64 hybrid BIOS/UEFI-friendly Live ISO workflow
- XFCE desktop with LightDM login
- NetworkManager, audio via PipeWire/WirePlumber, removable media support
- Firefox, Thunar, archive tools, terminal, hardware diagnostics and system utilities
- Calamares installer launcher for installing the live system to disk
- Copper AI daemon isolated in a dedicated `copper` service account
- Local AI HTTP gateway bound only to `127.0.0.1:8765`
- Ollama-compatible local backend configuration
- GGUF model directory at `/opt/copperbars/models`
- Copper Assistant: first-run Turkish-aware local AI chat window
- Copper Center: system, hardware, network and AI status dashboard
- Per-user first-start marker so Copper welcomes each desktop user once
- Automated Python/shell/policy validation in GitHub Actions

## Architecture

```text
+----------------------- Copper Desktop -----------------------+
|  XFCE  |  Copper Assistant  |  Copper Center  |  Thunar     |
+-------------------------------+------------------------------+
                                |
                         127.0.0.1:8765
                                |
                     +----------v----------+
                     |    Copper AI API    |
                     |  sandboxed service   |
                     +----------+----------+
                                |
                    +-----------+------------+
                    |                        |
             Local Ollama              Local model files
             127.0.0.1:11434           /opt/copperbars/models
```

Copper does not pretend a model exists when none is connected. The desktop stays usable without the model backend, and the AI panel shows its real state.

## Building the ISO

Use an x86_64 Debian/Ubuntu builder with live-build:

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

The preferred local backend is Ollama. Set the model for Copper with:

```bash
COPPER_OLLAMA_MODEL=<local-model-name>
COPPER_OLLAMA_URL=http://127.0.0.1:11434
```

GGUF files can be placed in `/opt/copperbars/models/`. Copper Center and the Model Setup utility show the currently detected models.

## Security model

The Copper service runs as the unprivileged `copper` user with systemd hardening (`NoNewPrivileges`, `PrivateTmp`, `ProtectSystem`, `ProtectHome`) and only the local model/state paths are writable.

## Current scope

This repository contains the OS foundation and reproducible build definition. A release image still needs to be built and boot-tested on real x86_64 hardware/VMs because hardware firmware, graphics, Wi-Fi and installer behavior cannot be verified from the source repository alone.
