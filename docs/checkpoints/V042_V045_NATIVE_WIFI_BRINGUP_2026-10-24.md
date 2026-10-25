# v042–v045: BCM4329 firmware console, MAC-dependent F2, and first native wlan0 on Linux 7 — physical checkpoint

**Date:** October 24, 2026. **Device:** experimental replacement Motorola Xoom MZ600; preexisting v034 **temporary-boot** Linux 7 and USB COM9 diagnostic runtime, no reboot or flash. **Result:** F2 success **and** `wlan0 PRESENT` physically demonstrated on v045 in a controlled no-association experiment. **This is NOT production/qualified Wi-Fi**; per-device MAC/regulatory route and normal separate WCC module packaging remain outstanding. Following user instruction: **no additional hardware components, capacitor experiment or modifications**. Factory hardware works under OEM stack; focus on software integration.

## A. v042: exact Motorola-compatible SDPCM shared structure and console metadata

Source-only reversible observer [`v042-build-sdpcm-console-metadata.py`](../../scripts/experiments/v042-build-sdpcm-console-metadata.py); ARM module **465120 bytes**, SHA256 **`c08ab15289fda9a144cb38e5576d6e6eca2dd1f50bc999871830232bf2c480e6`**, USB RAM upload CRC32 **`777EBB9F`**. Source hashes restored. One physical F2 failing `-62` trial, with read-only, exact-bounds internal SDIO Function 1 backplane memory reads:

| Field | Physically observed |
| --- | --- |
| SOCRAM | `rambase=0`, `ramsize=294912` bytes (288 KiB) |
| SDPCM shared header pointer from final RAM word | **`0x0002B134`**, **above** the lower 128 KiB (~172.3 KiB offset) |
| First four header bytes (LE flags) | **`03 00 00 00`**, `flags=0x00000003` ⇒ shared version 3 |
| Firmware trap/assert flags | zero in snapshot |
| Console struct pointer at shared header +20 | **`0x00046A54`**, aligned and in RAM |
| Msgtrace pointer at shared header +24 | **`0x00000000`**, **ABSENT** |
| Console log circular buffer | **`0x0004664C`**, size **1024** bytes, write index **242** |
| First 128 bytes read | successful, **122 printable** ASCII and **3 newline** characters |

**Correction of v041 instrument bug:** `msgtrace_ptr=0` was mistakenly labeled `in_ram=1` because SOCRAM base is zero; zero is NULL, not a usable trace pointer. The master structure is Broadcom's `sdpcm_shared`, **not** a magic-`MSGB` or hypothetical `bcma sh_info` header. Motorola `dhdsdio_readshared` and pinned Linux 7 `brcmf_sdio_readshared` directly define the 28-byte flags/trap/assert/console/msgtrace layout. The observed pointer replacement establishes firmware execution progress but not a proof of every NVRAM field being accepted.

## B. v043: private bounded firmware console reveals root cause of F2 refusal

Source-only [`v043-build-private-console-sample.py`](../../scripts/experiments/v043-build-private-console-sample.py). ARM module **465456 bytes**, SHA256 **`37a2bc3e53384bb128c87c7e63fb03ce0504316d619f7a865c49a1963c9aab8b`**, RAM upload CRC32 **`67BA0C62`**. Retains v042 source instrumentation, reads just the first 256 bytes of the validated 1024-byte console ring (eight 32-byte private hex chunks); **no raw proprietary bytes in public repository**. Source restored. USB log was processed privately on Surface and sensitive identifiers masked.

Actual firmware text:

```text
RTE (SDIOCDCIR) 4.220.48 on BCM4329 r3 @ 38/80/80 MHz
sdpcmdcdc0: Broadcom SDPCMD CDC driver
reclaim section 0: Returned 35055 bytes to the heap
Failed to init wireless side, err: 21
reclaim section 1: Returned 22674 bytes to the heap
```

This explains why the Cortex-M3 published a valid shared pointer but F2 never became ready under the original **MAC-free** 1550-byte NVRAM.

**Source crosscheck:** same-generation open Broadcom `brcmsmac` `wlc_bmac_attach` has a numbered `err=21` path for missing `macaddr`, `err=22` for invalid address (see https://cos.googlesource.com/third_party/kernel/+/9f9d2760da8c7f94fae119fac3e13d5a1702f8f0/drivers/net/wireless/brcm80211/brcmsmac/main.c). It is analogous, not proof of closed 4.220 firmware's exact error code table. More persuasive, Motorola's actual [`dhd_common.c`](https://android.googlesource.com/kernel/tegra/+/2a65edc/drivers/net/wireless/bcm4329/dhd_common.c) states **default MAC must exist in OTP or NVRAM to bring firmware up, with unique per-board MAC set separately via customer code**. Actual Motorola [`board-stingray-wifi.c`](https://android.googlesource.com/kernel/tegra/+/2a65edc/arch/arm/mach-tegra/board-stingray-wifi.c) handles private `ATAG_STINGRAY_MAC=0x57464D41`, then `get_mac_addr` callback. Mainline Linux v026 physical provenance found platform MAC callback **unavailable**, and our deliberately privacy-stripped NVRAM had no `macaddr`.

## C. v044: controlled *one-field* stock-Motorola startup NVRAM experiment

Private actual stock calibration `bcm4329.cal` in **both original Motorola HRI39 and HRI66** system images: both contain exactly the same, valid, nonzero, unicast default `macaddr` field. This is **not proven to be replacement tablet's unique factory MAC**; it is an authentic generic *bootstrap* value. Value **not shown or committed**, and no RF activity performed.

- Exact original prepared Xoom NVRAM `brcmfmac4329-sdio.txt`, **1550 bytes**, SHA256 **`a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb`**, CRC32 **`FAFCC93A`**.
- Exactly one added 26-byte `macaddr` text line (no `ccode`/`regrev` changes): private trial NVRAM **1576 bytes**, SHA256 **`e53cd5312000a7a099e7d14930164eb0e9cf865fa1f8d786e6cbee959c430d94`**, CRC32 **`DFC494F0`**. Firmware `4.220.48`, v043 kernel module, board GPIO/regulator, clock, MMC2 profile and other 1550 NVRAM bytes unchanged.
- Existing *standard* Surface uploader correctly **rejected** a NVRAM with `macaddr`. A separate **temporary local one-off client**, derived from the untouched standard uploader, allowed *only the exact SHA256/size-pinned 1576-byte trial NVRAM*. It still rejected arbitrary identity and all `ccode`/`regrev` overrides; it did not patch the original launcher or Xoom. The special client was deleted after each test.
- USB uploaded only NVRAM to RAM with **`UPLOAD DONE SIZE 1576 CRC32 0xDFC494F0`**, then `WIFI_START` with v043.
- **Physical outcome:** `brcmf_sdio_firmware_callback enable F2: err=0` (previous consistent error **-62**). Firmware core initialized far enough to assert SDIO F2 ready. This single-variable result ties missing startup identity directly to failed F2 in this configuration.
- **Next observed failure:** `brcmf_fwvid_request_module: mod=wcc: failed -2`, `brcmf_attach: brcmf_fwvid_attach failed`. Vendor integration error `-ENOENT`, **not** an F2/firmware reset failure. v044 `WLAN0 ABSENT` despite F2 success.

## D. v045: first actual native `wlan0` with upstream WCC support

[`scripts/experiments/v045-build-inline-wcc-vops.py`](../../scripts/experiments/v045-build-inline-wcc-vops.py) builds a **RAM-only diagnostic module** against the exact pinned Linux 7 kernel. The following four kernel sources have SHA guards and restore byte-for-byte: `sdio.c` `74491e8f...`, `chip.c` `932e25c7...`, `fwvid.c` `0b495cc8...`, and `brcmfmac/Makefile` `fba4e66e...`.

This experimental driver compiles **unmodified upstream `wcc/core.c`** into `brcmfmac.ko` using temporary Kbuild linkage and teaches the WCC vendor selection to use `WCC_VOPS`/self-module rather than `request_module("brcmfmac-wcc")` in minimal initramfs. Other vendors still use normal loading. **This is a diagnostic packaging workaround, not the intended upstream production architecture**; final initramfs should supply and load the normal `brcmfmac-wcc.ko` alongside brcmfmac, or provide proper modprobe userspace.

- v045 ARM module **465724 bytes**, SHA256 **`c51a8d664e59ac13f223b7e11288da32fa2653f2df30506983aabc99b9c5b81b`**, ABI `7.0.0-next-20260422 SMP mod_unload modversions ARMv7 p2v8`.
- Surface-independent SHA256 and byte-length verification passed; USB RAM upload **`UPLOAD DONE SIZE 465724 CRC32 0x7710D266`**.
- Only previous 1576-byte private, exact-Motorola-bootstrap NVRAM one-field trial was loaded; no changes to firmware (253748 bytes, generic 4.220.48), kernel, DT, power, hardware, host MMC2 profile or radio permissions.
- The actual USB `Status` returned:

```text
brcmfmac [loaded]
brcmutil [loaded]
WLAN0 PRESENT
NO SCAN/ASSOCIATION/DHCP
```

- Independent live kernel log: `brcmf_net_attach wlan0: Broadcom Dongle Host Driver`, with per-device MAC masked. **No RF scans/association/DHCP were attempted**. This is first successful physical `wlan0` creation, not full identity-correct/radio-qualified Wi-Fi.

## E. Mandatory physical rollback / final state, actually verified

1. After each identity trial `WIFI_STOP brcmfmac_rc=0 brcmutil_rc=0`.
2. Original 1550-byte **MAC-free** NVRAM restored via untouched standard guarded uploader: **`UPLOAD DONE SIZE 1550 CRC32 0xFAFCC93A`**.
3. Temporary SHA256-whitelisted private upload client **deleted**; verified original uploader still rejects arbitrary `macaddr|ccode|regrev` overrides.
4. After v045, the **previous v043** 465456-byte RAM diagnostic module restored to `/run/brcmfmac.ko`, **`UPLOAD DONE SIZE 465456 CRC32 0x67BA0C62`**.
5. Final verified USB `MMC2_STATUS`: **TARGET VALID, BOUND YES, CARD BCM4329 VERIFIED, DRIVER MODULES UNLOADED, AUTO profile 0**, COM9 responsive; kernel remains original temporary v034, no flash/reboot or altered partition. Current *safe reverted state* has **no `wlan0`**, because the test module is unloaded and MAC-free NVRAM restored. v045 `wlan0` was *physically observed during its trial*, not permanently installed.

## F. Engineering path from demonstration to production

1. **Identity before normal RF:** faithfully recover bootloader/private `ATAG_STINGRAY_MAC` for the *actual replacement device* (or another independently proven same-device factory source), validate unicast, nonzero, nonplaceholder and regulatory provenance without public disclosure. The HRI39/HRI66 generic stock `macaddr` value alone is **not unique**. Motorola's OEM driver documents bootstrap default followed by `cur_etheraddr` override through `get_mac_addr`. Integrate this into an upstream-compatible initialization path; keep raw identity in private storage only.
2. **Upstream WCC distribution:** include the kernel-built `brcmfmac-wcc.ko` plugin (already exists in cross-build tree) in temporary initramfs and load it through the standard module dependency mechanism; do not ship v045's Kbuild monolithic workaround as the final architecture.
3. Repeat the host and physical acceptance chain with *verified unique MAC and regulatory settings*: new temporary boot, F2 ready, `wlan0`, no invalid/duplicate MAC, network link, DHCP only when permitted, repeat across cold/warm resets, power/BT coexistence, suspend/resume and recovery. Do not equate single `wlan0` appearance to fully qualified native Wi-Fi.
4. No new physical components/capacitors, PMIC voltage, GPIO, or board hardware changes are needed for this demonstrated software milestone. Respect user's explicit no-hardware instruction.

**Physical acceptance:** v042 header/console PASS; v043 firmware error-21 console PASS; v044 F2 PASS but vendor WCC missing; v045 WCC inline and **wlan0 PRESENT PASS**; rollback/USB/MMC2 PASS; unique identity, regulatory and connection tests **NOT YET QUALIFIED**.