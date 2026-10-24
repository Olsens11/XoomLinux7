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

## Pending BCM4329 qualification (2026-10-24, v016 on v015 environment)
A read-only hotloaded v016 Broadcom module physically recorded IOEx \`0x02→0x06\`, IORx \`0x02→0x02\`, clock CSR \`0xD2\`, \`-62\` timeout, still no wlan0. Source restored byte-identically. Previous v010/v011/v013 capability interventions are now considered **partial exploratory tests**, not OEM-equivalent accepted fixes. Next: read the RAW CCCR and EFFECTIVE parsed six card capabilities and host timing, then test a board-scoped complete Motorola equivalent with a valid control. [Evidence](checkpoints/V016_F2_IOEX_IORX_PHYSICAL_2026-10-24.md).

## v017 diagnostic evidence, no Wi-Fi promotion
v017 RAM-hotloaded read-only module verified actual raw CCCR and final card/host flags: raw CCCR 0x11, Linux version 1, high-speed 0 versus Motorola OEM version 2, high-speed 1. Host clock 46,153,846 Hz at legacy timing. F2 still -62, no wlan0. See [v017](checkpoints/V017_CCCR_CAPABILITIES_PHYSICAL_2026-10-24.md). This is **not a fixed Wi-Fi checkpoint**; v015 remains the proven diagnostic loader.

## v018 completed OEM capability counterfactual, 2026-10-24
The **complete board/chip-scoped Motorola six-field override** was applied after CCCR/CIS parsing and physically confirmed by the v017 read-only module. Final version=2 and highspeed=1, SDIO SPEED=03, host timing=2 (SD HS), clock remains 46,153,846Hz. With the same OEM firmware and generic NVRAM, two trials still had IOEx=06/IORx=02 and F2 timeout -62; no wlan0. **The full OEM card capability override alone does not solve Wi-Fi.** [Exact evidence](checkpoints/V018_OEM_SIX_CAPABILITIES_PHYSICAL_2026-10-24.md). v015 remains the stable diagnostic infrastructure.

## v019 25MHz physical A/B, 2026-10-24
A full Motorola six-field-override v018 kernel with the actual USB diagnostic DTS SDMMC2 max-frequency capped to 25MHz was rebuilt and temporary-booted as v019. DTB decompilation confirmed only one property difference; the first draft altering an unused source file was caught and NOT booted. Actual host clock **25,000,000Hz**, SDIO version 2/high-speed 1 and host timing 2. Same OEM firmware, generic NVRAM and v017 diagnostic module. Two attempts: IOEx=06/IORx=02, **F2 -62 and no wlan0**, unchanged. [v019 checkpoint](checkpoints/V019_SDMMC2_25MHZ_AB_2026-10-24.md). v015 remains accepted as diagnostic infrastructure; no Wi-Fi repair promoted.

## v018 supplementary recheck and on-demand design (2026-10-24)
Another physical v018 run (identical image SHA) confirmed six Motorola capabilities active, SDIO SPEED=03, host high-speed timing=2 and F2 -62 with IOEx=06, IORx=02. This instance measured **25 MHz actual MMC host clock**, whereas the earlier recorded v018 run measured 46.15 MHz despite v018 DTB max-frequency=46.15 MHz. The discrepancy needs a controlled investigation, not silent reconciliation. [Supplementary evidence](checkpoints/V018_RECHECK_2026-10-24.md). On-device read-only SDIO command shows the Wi-Fi platform device `c8000200.mmc` supports driver bind/unbind, which motivates a [guarded on-demand reinitialization design](architecture/MMC2_ON_DEMAND_DESIGN.md). **That capability has NOT been implemented, and F2 is not fixed.**

## v020 physically qualified on-demand MMC2 controls (2026-10-24)
**Latest accepted experimental diagnostic baseline v020**, with v015 retained as prior USB fallback. The replacement MZ600 successfully temporary-booted exact SHA256 b08863d6be4ae15f757eb9bfa8089d3a2d23859fc3ea63c4f119f4be9430ebf3. Without reboot, MMC2 reinitialized using unchanged AUTO, then MOTOROLA (all six effective fields changed), then AUTO again. A separate attempt with loaded Broadcom drivers was correctly denied; the Surface host client now waits for terminal PASS or error. Final state: AUTO, module list empty, card bound. **F2 still times out -62 and wlan0 remains absent.** Detailed [checkpoint](checkpoints/V020_MMC2_ON_DEMAND_PHYSICAL_2026-10-24.md). Rebind is not proven full electrical power cycle.

## v020 post-test stability caveat
After completing and documenting successful runtime MMC2 AUTO/MOTOROLA/AUTO tests, the Surface later observed a temporary loss of Linux USB CDC, followed by the replacement MZ600 appearing in Android ADB mode, then Linux v020 CDC again. Read-only Linux uptime at final recovery was only 83.96 seconds, whereas the prior session had passed 250 seconds. This confirms a **later session restart** but does not establish its cause. No deliberate reboot was issued by this workflow after initial v020 boot. v020 on-demand functionality physically passed; **long-running session stability is NOT yet qualified**. See v020 physical checkpoint.
