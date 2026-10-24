# Verified project state — imported 2026-10-24

> **Verification labels are intentionally strict.** This is the working status as recovered from measured local outputs; it does not imply all parts were independently re-run at repository initialization.

## Source
- Upstream: `https://github.com/xoom-linux/linux.git`, pinned commit `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3` (Wingray DTS contribution, June 12, 2026).
- Kernel output reports `7.0.0-next-20260422`. ARMv7 Cortex-A9 Tegra2, no NEON.
- `tegra20-motorola-stingray.dts` is the upstream Wingray DTS with model/compatible strings changed; `-usbdiag` additionally changes USB0 to peripheral mode. Shared Wi-Fi nodes are unchanged.

## Hardware-qualified behavior (replacement MZ600)
- Temporary-boot Linux v013: serial USB diagnostics (`PONG XOOM-LINUX V13`), framebuffer/display, touch/grid, MMC/SDIO diagnostics.
- Touch v05 recorded 273 frames and 29 event reports; v06 touch crosshair confirmed physical mapping. Small transient lag at quick swipes, not considered worth special work on throwaway test UI.
- Wi-Fi: BCM4329 rev3 enumerated as `mmc2:0001` (three functions), correct F1 signature `0x9934329`, firmware transfer initiated. **No wlan0 and no working native wireless connection.**
- Blocker: `brcmf_sdio_firmware_callback enable F2: err=-62` (approx 3s ready timeout), including alternative OEM firmware, regulatory database integration, SDIO CCCR revision and high-speed host experiments.
- v012 instrumentation was built; separate conclusive physical v012 capture was not found.

## Latest build
- v014 RAM-only LIVE-LAB image staged and independently hashed on Surface: `MZ600-stingray-diagnostic-v14-LIVE-LAB-TEMPBOOT-ONLY.img`, 6,656,000 bytes; SHA256 `65846a0928feed535e81a0898bc186d48d12a96c40f36719d6b56a8a3589f670`.
- **v014 was physically temporary-booted 2026-10-24**: USB PING and STATUS PASS; Broadcom WIFI_START and WIFI_STOP PASS; BCM4329 F2 still times out -62; no wlan0. Binary firmware upload FAIL due to canonical TTY echo/buffering; session recovered without a reboot.
- **v015 was physically temporary-booted on 2026-10-24 and accepted for USB/live-lab use**. STATUS included USB RAW READY. Raw firmware uploads of 4,096 and 264,140 bytes returned matching CRC32; RAM module uploads of 17,828 and 460,140 bytes matched CRC32. Uploaded modules loaded, debug-level change was confirmed, WIFI_RETRY performed unload/load, and WIFI_STOP unloaded both. **WLAN0 remains absent; Wi-Fi F2 problem is not fixed.** See V015_RAW_USB_LAB_2026-10-24.md.
- Built image, private binaries and exact device logs remain on development machines, not in public Git.

## Next gate
1. Treat v015 as qualified RAM-only USB diagnostic baseline; no permanent flash.
2. Reproduce the BCM4329 F2 ready timeout using uploaded driver modules and controlled changes, comparing register/firmware/clock traces to OEM reference.
3. Before RF scans or associations, validate per-device MAC/calibration and regulatory provenance.
4. Do not confuse usable live-lab infrastructure with actual wlan0 or association success.

See [Wi-Fi report](hardware/WIFI_BCM4329.md), [checkpoint log](checkpoints/README.md), [roadmap](roadmap.md).

## Repository workspace and import verification (2026-10-24)
- GitHub main commit `ea38127` imported 133 reviewed original source files. Desktop verification compared all 133 against `evidence/import-source-sha256.txt`: **133/133 SHA-256 match, 0 mismatches**.
- One historical note containing MAC-like material was excluded from public source pending review; private copy retained at source.
- Three development machines have cloned repositories and dedicated tracked Git worktrees. Desktop and Pi continuity checker: **0 errors**. Surface fresh checkout line-ending differences were resolved and both trees left clean.
- Separate SSH ed25519 deploy keys are registered with write permissions. **Actual SSH auth, remote branch creation, and remote branch deletion passed from Desktop WSL, Raspberry Pi, and Surface**, with one independent branch per machine. Temporary access-test branches were removed afterward; see [dated access verification](checkpoints/GIT_ACCESS_2026-10-24.md).
- Surface v014 diagnostics client and safe USB probe scripts imported separately, without firmware or raw device-specific scripts.

## 2026-10-24 validated update
See [v014 physical testing](checkpoints/V014_USB_LAB_2026-10-24.md), and [v015 candidate manifest](../releases/v015-manifest.txt). v014 remains safely running, v015 pending physical qualification.
