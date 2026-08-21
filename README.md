# CopperBarsOS

CopperBarsOS is a 64-bit x86_64 Debian Live-based desktop operating system designed around a local-first AI assistant named **Copper**.

## Why CopperBarsOS is designed this way

Windows is widely attractive because of its broad PC software/hardware ecosystem and gaming support; Microsoft explicitly highlights Windows gaming features and maintains compatibility guidance for older applications. citeturn973639search10turn973639search3

macOS is attractive because Apple tightly integrates hardware and software and provides built-in continuity features such as Handoff, AirDrop, Universal Clipboard and Continuity Camera across Apple devices. Apple also layers App Store/Gatekeeper/Notarization/XProtect defenses into macOS. citeturn973639search0turn973639search9

CopperBarsOS aims to reproduce the useful ideas without copying either operating system: broad Linux hardware/software support, a simple app store, predictable system administration, strong defaults, and a local AI assistant that is part of the desktop rather than a separate website.

## What is included

- x86_64 hybrid BIOS/UEFI-friendly Live ISO workflow
- XFCE desktop with LightDM login
- NetworkManager, audio via PipeWire/WirePlumber, removable media support
- Firefox, Thunar, archive tools, terminal, hardware diagnostics and system utilities
- Calamares installer launcher for installing the live system to disk
- Copper AI daemon isolated in a dedicated `copper` service account
- Local AI HTTP gateway bound only to `127.0.0.1:8765`
- First-run Turkish AI model selector with Qwen3, Llama 3.2 and Gemma 3 choices
- Copper Store with curated application catalog, search, categories, install/remove actions and APT integration
- Copper Assistant: first-run Turkish-aware local AI chat window
- Copper Center: system, hardware, network and AI status dashboard
- GGUF model directory at `/opt/copperbars/models`
- Per-user first-start marker so each desktop user gets the onboarding once
- Automated Python/shell/JSON/policy validation in GitHub Actions

## Copper Store

Copper Store follows the useful ideas of Pardus Yazılım Merkezi: application categories, descriptions, installation/removal, and an approachable graphical interface. Pardus itself documents package installation/removal, application details, comments, statistics and application suggestions as core software-center features. citeturn578135search0turn578135search5

Copper Store currently uses a curated local catalog and invokes the Debian APT stack for installation. This keeps package handling inside the distribution's normal dependency and update system instead of creating a second package manager.

## AI onboarding

After the first desktop login, CopperBarsOS opens a setup window where the user can choose among several current lightweight local models:

- **Qwen3 1.7B** — about 1.4 GB in Ollama's current Q4_K_M build.
- **Llama 3.2 3B** — about 2.0 GB in Ollama's current Q4_K_M build.
- **Qwen3 4B** — about 2.5 GB in Ollama's current Q4_K_M build.
- **Gemma 3 4B** — about 3.3 GB in Ollama's current Q4_K_M build.

The setup detects system RAM and presents these as local choices. Model weights are not embedded in the ISO, so the image remains practical to distribute. Current model sizes and variants are taken from Ollama's published model pages. citeturn326893search1turn326893search3turn326893search0

The model picker saves the selection for the local Copper service. Actual model download is only attempted when an Ollama server is available; otherwise the choice is saved and the system continues to work without pretending that a model is installed.

## Architecture

```text
+------------------------- Copper Desktop -------------------------+
| XFCE | Copper Store | Copper Assistant | Copper Center | Thunar |
+--------------------------------+---------------------------------+
                                 |
                          127.0.0.1:8765
                                 |
                    +------------v-------------+
                    |       Copper AI API      |
                    |     sandboxed service    |
                    +------------+-------------+
                                 |
                  +--------------+---------------+
                  |                              |
           Local Ollama                    Local GGUF files
           127.0.0.1:11434                /opt/copperbars/models
```

Copper does not pretend a model exists when none is connected. The desktop stays usable without the model backend, and the AI panel reports the real backend/model state.

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

## Security model

The Copper service runs as the unprivileged `copper` user with systemd hardening (`NoNewPrivileges`, `PrivateTmp`, `ProtectSystem`, `ProtectHome`) and only the local model/state paths are writable. The AI API is intentionally bound to localhost rather than exposed to the LAN.

## Current scope

This repository contains the OS foundation, user-facing desktop tools, AI onboarding, software store and reproducible build definition. A release image still needs to be built and boot-tested on real x86_64 hardware/VMs because firmware, graphics, Wi-Fi, installer and hardware-specific acceleration cannot be verified from the source repository alone.
