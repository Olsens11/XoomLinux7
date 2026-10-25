# v040/v041 physical BCM4329 Cortex-M3, NVRAM-token and SDPCM shared-memory handoff

**Date:** October 24, 2026. **Status:** two successful read-only diagnostic RAM-module tests; **native Wi-Fi still fails F2 readiness (-62)**. This disproves an *immediate and complete* WLAN firmware halt at reset release but does not establish ongoing CPU progress after timeout. No persistent hardware changes.

## Background and authoritative protocol

The original [Motorola `dhd_sdio.c` at Tegra kernel 2a65edc](https://android.googlesource.com/kernel/tegra/+/2a65edc/drivers/net/wireless/bcm4329/dhd_sdio.c) `dhdsdio_write_vars` writes the NVRAM size/complement token in the last four bytes of SOCRAM. The OEM `dhdsdio_readshared` routine, guarded by `DHD_DEBUG_TRAP`, *explicitly* reads that same word after firmware initialization as the pointer to its `sdpcm_shared` diagnostics structure, validates that the token was replaced, then reads header fields including flags, traps/asserts, console and message-trace pointers.

Pinned modern [Linux 7 `brcmfmac/sdio.c` at `2404d273`](https://github.com/xoom-linux/linux/blob/2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3/drivers/net/wireless/broadcom/brcm80211/brcmfmac/sdio.c) independently contains the same `sdpcm_shared_le` header structure and `brcmf_sdio_readshared` diagnostic function under DEBUG. `brcmf_chip_iscoreup` checks whether the WLAN Cortex-M3 core reset/clock wrapper is up; **this is a reset-state test, not instruction-pointer or running-status telemetry**.

## Artifact provenance and safety

- v040 builder: [`scripts/experiments/v040-build-cm3-nvram-shared-state.py`](../../scripts/experiments/v040-build-cm3-nvram-shared-state.py). ARMv7 module `brcmfmac-v040-pmu-cm3-readonly.ko` **463252 bytes**, SHA256 **`76bf426996f1ccab7835925eec3540aaa9b3e4ea325ef804bcdf58785e59c4c0`**, USB RAM upload **CRC32 `B33ECADA`**.
- v041 builder: [`scripts/experiments/v041-build-readonly-sdpcm-shared-header.py`](../../scripts/experiments/v041-build-readonly-sdpcm-shared-header.py). ARMv7 module `brcmfmac-v041-pmu-cm3-readonly.ko` **463856 bytes**, SHA256 **`8f245c13d4622bfb472882be3ea17154291561a5662fa27988ce4bc7e734c626`**, USB RAM upload **CRC32 `425063E6`**.
- Both used unchanged and source-hash-guarded pinned Linux kernel 7 modules, replaced `brcmfmac` only in RAM, restored temporary source changes after compilation, and kept original generic 253748-byte firmware, 1550-byte prepared Xoom NVRAM, MMC2 AUTO profile, shared PMIC/clock control and temporary boot v034 kernel fixed.
- No raw NVRAM bytes, per-device MAC, firmware content, console text or identifiers printed or committed. MCU RAM read is precisely 4 bytes at final RAM word and (v041 only) 28 bytes of the in-bounds shared header. No new GPIO/PMU/core-reset writes.
- Sanitized private log files on Surface: `v040-handoff-trial1-sanitized.log` and `v041-shared-header-sanitized.log`. Source of truth for *device* final status is COM9 `MMC2_STATUS`, not mere module-init return value.

## Actual v040 hardware result

| Phase | CM3 core up? | End-of-RAM behavior |
| --- | :---: | --- |
| Before CPU release | **No** (`arm_up=0`) | Read succeeded; `nvram_packed=672`, final 4 bytes match expected NVRAM length/complement token |
| Immediately after CPU release | **Yes** (`arm_up=1`) | No additional RAM read performed |
| Before Function 2 request | **Yes** | No additional RAM read performed |
| After 3-second F2 timeout (-62) | **Yes** | Read succeeded; last word no longer a length token; aligned, in-range pointer candidate |

- Chip reports SOCRAM `rambase=0`, `ramsize=294912` bytes (288 KiB).
- Read error codes for actual memory accesses = **0**.
- Even though PMU resources, SDPCM protocol-version mailbox and internal clocks proceed normally, `IOEx=0x06`, `IORx=0x02`, `sdio_enable_func(F2)` = **-62**.
- Because firmware overwrote the validated token **on that same attempt** with a plausible shared pointer, this is much stronger evidence of executed firmware instructions than the previous register-only measurements. An exception is still possible *later* in startup, not an immediate halt at reset release.

## v041 shared-header validation — decisive additional evidence

The v041 trial reproduced the same before/after RAM token behavior, then read just the standard 28-byte, 7-word SDPCM shared header at the published in-range pointer. The retrieved hardware event:

```text
XOOM_V041_SHARED read_rc=0 version=3 assert_flag=0 trap_flag=0
  trap_ptr_nonzero=0 assert_ptr_nonzero=0
  console_ptr_in_ram=1 msgtrace_ptr_in_ram=1 console_ptr_nonzero=1
XOOM_V041_HANDOFF phase=POST_F2_RESULT arm_up=1
  ram_base=00000000 ram_size=294912
  tail_read_rc=0 token_matches=0 tail_is_length=0
  tail_is_shared_ptr_candidate=1
brcmf_sdio_firmware_callback enable F2: err=-62
```

The protocol version **3** matches the current driver's SDPCM *shared structure* version and is distinct from the SDPCM *mailbox protocol* version **4**. Trap/assert flags were clear at the snapshot; this does **not** prove that errors are impossible or that no earlier reset occurred. Both console and message-trace pointers fall within chip RAM, giving a validated next diagnostic path.

**Interpretation:** Firmware did not simply sit in reset or die before doing any useful work. The shared-memory publication is a meaningful sign of actual firmware startup progress. The reason it has not set SDIO F2 IORx ready remains unknown. Failure could be a later protocol mismatch, firmware timing, radio/power fault, reset history or actual electrical droop; no oscilloscope or capacitor modification was part of these tests.

## Final state

After v040 and v041 each, `WIFI_STOP` returned `brcmfmac_rc=0 brcmutil_rc=0`. Final USB `MMC2_STATUS` showed **TARGET VALID, BOUND YES, CARD BCM4329 VERIFIED, DRIVER MODULES UNLOADED, AUTO profile 0, COM9 responsive**. No boot image flashed/reboot, Wi-Fi RF scan/association, BT changes or partition writes.

## Next discriminating step

Read-only validate the published console **ring metadata** (`struct rte_console.log_le`, pointer/size/index) with stringent bounds and no raw console dumping or GPIO writes. Only if metadata validates, retrieve a small bounded ring excerpt *privately* and sanitize MACs/identity before any reporting. Consider whether the firmware's `tohostmailboxdata` reports FWREADY or FWHALT before F2, using read-only access with non-destructive register semantics. Separately plan one additional verified-rail buffering capacitor experiment on the replacement Xoom if desired; no solder point or capacitor size is approved by these software observations alone.
