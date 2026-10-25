# v038 physical — BCM4329 Cortex-M3 and NVRAM end-of-RAM handoff (October 24, 2026)

**Result:** PASS for read-only instrumentation, RAM module, physical CM3 core reset/clock-state transition, NVRAM length token verification, and known-safe unload. **Wi-Fi F2 remains FAIL -62**. Neither Xoom rebooted/flashed or had power/PMU sequencing changed; tests on replacement temporary-boot v034 only.

## Binary provenance and deployment

- Reversible source hash-guarded builder [`scripts/experiments/v038-build-cm3-nvram-handoff.py`](../../scripts/experiments/v038-build-cm3-nvram-handoff.py), derived from the v037 observer. Pinned Linux 7 original source restored after compilation.
- ARM ELF module `brcmfmac-v038-pmu-cm3-readonly.ko`: **463,028 bytes**, SHA256 **`22a7832015acd92f33aba03bd52fa569448f0afd130eb90b18c01785072044c2`**, vermagic `7.0.0-next-20260422 SMP mod_unload modversions ARMv7 p2v8`.
- Independently verified Surface transfer size+SHA256. Guarded COM9 USB upload to RAM returned **`UPLOAD DONE SIZE 463028 CRC32 0x9D0E923E`**. Existing firmware/NVRAM unchanged; no regulatory/RF activity or firmware swap. `BRCMUTIL rc 0`, `BRCMFMAC rc 0`.
- v038 adds `brcmf_chip_iscoreup` (read-only Sonics backplane TMSLOW status) before and after the existing CM3 release, and one 4-byte RAM read at `rambase+ramsize-4` to verify the NVRAM length/complement token; prints **only boolean match and lengths**, never token raw values, MAC, or NVRAM contents. The 4-byte extra read incurs a small timing change; no additional PMU/reset GPIO writes.

## Physical evidence

```text
PRE_CM3_RELEASE  arm_up=0 ram_base=00000000 ram_size=294912 nvram_packed=672 tail_read_rc=0 token_matches=1
POST_CM3_RELEASE arm_up=1 ram_base=00000000 ram_size=294912 nvram_packed=672 tail_read_rc=-95 [not requested]
PRE_F2_REQUEST  arm_up=1 ram_base=00000000 ram_size=294912 nvram_packed=0 [not applicable]
XOOM_V038_MAILBOX write_rc=0 sdpcm_protocol=4
PMUStatus 0xAE (ALP) → 0xBE (HT); resource mask 0x003FE63E; pending=0
F2 IOEx requested 0x06; IORx 0x02; enable F2: err=-62
```

**Important logging semantics:** `tail_read_rc=-95` after release is a **sentinel meaning 'read not requested'**, not a failed SDIO transaction. The only RAM-tail read (PRE release) returned rc0 and matched. `nvram_packed=0` at PRE_F2_REQUEST is a helper call with no applicable NVRAM length, not a signal that NVRAM disappeared.

`brcmf_chip_iscoreup` only shows the CM3 Sonics core clock set and reset/reject clear. It is **not proof that embedded firmware instructions actually execute**, nor an indication of a firmware-alive loop. The successful NVRAM token check proves the length token at the correct physical RAM address; **not** that the entire NVRAM parameters or firmware image are correct.

## Motorola original versus modern Linux NVRAM representation

The original [Motorola `dhd_sdio.c` at 2a65edc](https://android.googlesource.com/kernel/tegra/+/2a65edc/drivers/net/wireless/bcm4329/dhd_sdio.c) lines ~2364–2440 writes processed variables immediately below the final four bytes of original SOCRAM and then writes a complement/word-count token at the last four-byte word. The modern [Linux 7 `brcmfmac/firmware.c`](https://github.com/xoom-linux/linux/blob/2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3/drivers/net/wireless/broadcom/brcm80211/brcmfmac/firmware.c) ~393–448 produces the same token **inside a packed buffer** and `brcmfmac/sdio.c` ~3366–3380 writes it to the top of RAM. These layouts agree when original and configured sizes are equal. Physical v038 confirms the Linux buffer's last four bytes match its computed token.

Do not directly compare raw OEM `bcm4329.cal` file's 1595-byte text size with Linux's 672-byte *packed binary* result: comments, whitespace, separators and token packaging differ.

## Private value-by-value OEM calibration comparison — critical additional result

A private, tool-contained comparison inspected the Linux reference `firmware-reference-v07/brcm/brcmfmac4329-sdio.txt` and archived OEM HRI39 calibration without emitting any proprietary values/identifiers. Linux v07 reference and v08 private reference files are byte-identical: each **1550 bytes**, SHA256 `a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb`, with 97 text lines (many comments).

Parsing only valid non-comment `key=value` records, taking the final value for duplicate keys:
- Linux: **51 distinct keys**.
- OEM: **54 distinct keys**.
- All **51 shared keys have exactly identical values**.
- OEM-only keys: `macaddr`, `ccode`, `regrev`.
- No keys occur only in the Linux reference.

This is a strong *specific* equivalence of the textual references, subject to the usual distinction between checked reference files and the currently loaded chip's packed buffer. `macaddr` is a **unique identity input**, and `ccode`/`regrev` are **regulatory settings**; do not transplant original reference identifiers into a different physical Xoom. The OEM source `get_mac_addr` and regulatory callbacks must be traced to establish whether firmware may require these before F2 becomes ready, and how to source the actual replacement tablet's legitimate values.

## Conclusion and next discriminators

1. Neither a missing NVRAM length token nor CM3 remaining physically asserted in reset explains F2 -62 on this warm attempt. F2 still fails after successful mailbox write, ALP→HT and reported active PMU resources.
2. The original early-MZ600 firmware `fw_bcm4329.bin` version **4.218.248.20** (261317 bytes, private SHA256 `7afdc1b85313bcc6054e01bd22aa4540a47cf6f42903b4f9728a1236b955251a`) has **not** been tested under Linux 7; all physical observations here used the existing generic firmware. The image length fits 294912-byte RAM with room for 672-byte packed NVRAM; this size arithmetic alone is not a compatibility guarantee.
3. Audit MAC/regulatory provenance and embedded firmware startup expectations; then consider a **one-variable RAM-only original OEM firmware test** after preserving current firmware for rollback, with no association/scanning and no proprietary blobs in public Git.
4. Distinguish **CM3 core clocked and out of reset** from **CM3 executing firmware**; find a non-destructive firmware-alive indicator or precise ROM/firmware initialization status, not an inferred flag.
5. Preserve v034 temporary kernel and v025 rollback; do not change PMU/rails while firmware differences remain untested.

## End state

`WIFI_STOP brcmfmac_rc 0 brcmutil_rc 0`; final USB COM9 `MMC2_STATUS` target valid, card BCM4329 detected, MMC2 bound, AUTO profile 0, driver modules unloaded. No reboot, flash, nor any persistent device changes.

**Acceptance:** build PASS / SHA and USB upload CRC PASS / CM3 core-up transition PASS / NVRAM token PASS / modules cleanup PASS / WLAN F2 FAIL.
