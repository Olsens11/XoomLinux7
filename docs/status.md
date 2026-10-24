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
- **v014 has not been established as physically booted or hardware-qualified.** Its hot-reload commands and module support must be verified experimentally before use.
- Built image, private binaries and exact device logs remain on development machines, not in public Git.

## Next gate
1. Confirm replacement DUT, USB/fastboot and adequate power.
2. Hash-check actual v014 candidate; temporary `fastboot boot` only.
3. Validate USB `PING` identifies V14, `WIFI_STATUS`, `WIFI_START`, `WIFI_STOP`, `WIFI_RETRY` and known rollback.
4. Verify module and firmware upload/checksum paths, then F2 instrumentation and hardware behavior.
5. Keep MAC identity and regulatory provenance gates before scanning/association.

See [Wi-Fi report](hardware/WIFI_BCM4329.md), [checkpoint log](checkpoints/README.md), [roadmap](roadmap.md).

## Repository workspace and import verification (2026-10-24)
- GitHub main commit `ea38127` imported 133 reviewed original source files. Desktop verification compared all 133 against `evidence/import-source-sha256.txt`: **133/133 SHA-256 match, 0 mismatches**.
- One historical note containing MAC-like material was excluded from public source pending review; private copy retained at source.
- Three development machines have cloned repositories and dedicated tracked Git worktrees. Desktop and Pi continuity checker: **0 errors**. Surface fresh checkout line-ending differences were resolved and both trees left clean.
- Separate SSH ed25519 keys and per-device host aliases were created. **GitHub write access is NOT yet enabled**: all new keys still need registration under repository Deploy Keys with Allow write access. No successful SSH auth or Git push is claimed.
- Surface v014 diagnostics client and safe USB probe scripts imported separately, without firmware or raw device-specific scripts.
