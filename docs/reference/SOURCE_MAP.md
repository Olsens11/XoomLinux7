# Source, builder, machine and artifact map (2026-10-24 import)

| Location | What lives there | Authority |
| --- | --- | --- |
| `https://github.com/xoom-linux/linux` | Contributors' original kernel/DTS, pinned to `2404d273...` | Upstream historical baseline |
| `src/board/` | Our Stingray derived and USB-diagnostic DTS | Board-specific experiment source |
| src/diag-init/ | Freestanding PID1 source snapshots v03-v15 | v015 USB diagnostic verified; no native wireless functionality yet |
| `scripts/history/` | Build/packaging/setup/one-shot transfer recipes imported by version | Historical reproducibility, not all scripts current |
| `configs/` | Kernel config snapshot and MAC-free NVRAM text | Reproducibility inputs, never real calibration |
| `docs/checkpoints/` | Verifiable experiment chronology/status | Interpreted public summary |
| `evidence/` | Curated manifest and reviewed public outputs | Evidence only at recorded qualification level |
| Desktop WSL `/home/xoomdev/xoom-linux-rom/` | Actual extracted kernel build trees, toolchain, 12 versioned init files | Local build/reference files |
| Desktop Windows `C:\Users\olsen\XoomLinux\Phase1\` | 112 historical build/creation/package scripts, technical notes | Primary script archive |
| Surface `C:\Users\olsen\xoom-linux-rom\downloads\` | Original boot images, USB commands, one-shot test scripts | Private physical test staging |
| Pi `/home/ps2/xoom-phase1/` | Protected recovery project, OEM, TWRP reference | Not XoomLinux7 source; do not modify |
| `https://github.com/Olsens11/xoom-recovery` | Recovery tooling and Wi-Fi precedent | Separate project, read-only reference for this effort |
| `https://github.com/Olsens11/PS-to-VNC` | Development continuity and documentation patterns | Reference only |

Project Git is authoritative for *new changes*. Imported historical files are traceable but may not be byte-identical if line endings were normalized during migration; hashes of final published source establish fresh authority. Never treat an unversioned local `linux-src` extract as immutable upstream.

## Surface host command source
- Current host client: scripts/host/surface/Xoom-v15-LiveLab.ps1. The v014 client is retained as historical evidence of canonical TTY upload failure.
- `scripts/host/surface/Probe-MZ600-LinuxUSB.ps1` — USB gadget probing.
- `scripts/host/surface/history/Reboot-Verified-MZ600-Linux-V05.ps1` — historical v05 procedure, not an approved current action.
- The Surface's calibration scripts and Android Wi-Fi cycle helper include actual test-device serial identifiers, so they remain private and were **not** published.

## v015 diagnostic source
- src/diag-init/phase1-v15/init.c: raw TTY, bounded binary transfer, module lifecycle.
- scripts/build/v15-*: build and verification.
- scripts/host/surface/Xoom-v15-LiveLab.ps1: physically verified host client.
- releases/v015-manifest.txt: image identity and qualification.
- docs/checkpoints/V015_RAW_USB_LAB_2026-10-24.md: physical evidence.

## F2 v016 source
- \`scripts/experiments/v016-build-f2probe.py\` and \`patches/experiments/v016-brcmfmac-f2-cccr-readback.patch\` — RAM module build, read-only instrumentation, restored source verification.
- \`docs/research/\` and \`docs/checkpoints/V016_F2_IOEX_IORX_PHYSICAL_2026-10-24.md\` — comparison, plan and physical evidence. Binary v016 module stays private.

## v017 capability audit
- scripts/experiments/v017-build-capability-inventory.py; patches/experiments/v017-brcmfmac-f2-cccr-readback.patch; docs/checkpoints/V017_CCCR_CAPABILITIES_PHYSICAL_2026-10-24.md.

## v018 Motorola capability counterfactual
- \`scripts/experiments/v018-build-oem-caps.py\`: temporary source overlay/build and guaranteed restoration.
- \`patches/experiments/v018-motorola-six-field-sdio-capabilities.patch\`: exact board/chip-scoped modern equivalent.
- \`releases/v018-manifest.txt\`: image hash/physical negative test; image remains private.
- \`docs/checkpoints/V018_OEM_SIX_CAPABILITIES_PHYSICAL_2026-10-24.md\`: measured effective bus state and -62 timeout.

## v019 25MHz A/B
- scripts/experiments/v019-build-lowclock.py — source-scoped repeatable kernel rebuild with full source restoration.
- scripts/experiments/v019-package-tempboot.sh — v019 boot-image verifier; no flash.
- patches/experiments/v019-sdmmc2-maxclock-25mhz.patch — actual compiled -usbdiag.dts node, not ordinary unconsumed DTS.
- releases/v019-manifest.txt and docs/checkpoints/V019_SDMMC2_25MHZ_AB_2026-10-24.md — physical negative evidence.
