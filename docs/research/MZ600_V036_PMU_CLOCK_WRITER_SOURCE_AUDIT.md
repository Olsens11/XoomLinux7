# BCM4329 PMU/clock writer attribution and revision-safe v036 probe

**Date:** 2026-10-24. **Reference:** v035 3-trial physical checkpoint. **Status:** source-level host writer audit; no v036 physical conclusions.

## What v035 measured
- First trial PMUControl 0x01770180 (T3 just after CM3 release) → 0x012B03BC (T4 before F2), elapsed 31.920 ms; all reads successful.
- Two driver-only warm retries started and remained at 0x012B03BC and still failed F2 with IOEx 02→06 / IORx 02 (-62).
- Driver reload is not a proven BCM4329 power-on reset. F2 failed at both values, so this alone does not implicate retention as the cause.

## Host-side write search (pinned Linux 7)
A source-tree search of `drivers/net/wireless/broadcom/brcm80211/brcmfmac` at [pinned `2404d273`](https://github.com/xoom-linux/linux/tree/2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3) found one explicit `pmucontrol` write: [`sdio.c` ~4060–4069](https://github.com/xoom-linux/linux/blob/2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3/drivers/net/wireless/broadcom/brcm80211/brcmfmac/sdio.c), where the existing driver sets the `BCMA_CC_PMU_CTL_RES_RELOAD` request to reload POR values. That path precedes firmware download and CM3 release. No direct PMUControl write was identified in the later T3→T4 brcmfmac source window.

**Inference only:** onboard firmware/autonomous PMU activity is a stronger explanation for the later changed register, but a different host driver, indirect window writes, or changes in register semantics must still be excluded. This search does not instrument arbitrary backplane writes and is not a proof that firmware executed.

## PMU field interpretation caveat
The v035 first observed register change includes raw ILP_DIV 375→299; raw XTALFREQ code 0→15; NOILPONW 0→1; both HTREQEN and ALPREQEN remain 1. The MZ600 early and later original calibration each specify `xtalfreq=38400` kHz, and the BCM4329 datasheet [section 14](https://media.digikey.com/pdf/Data%20Sheets/Cypress%20PDFs/BCM4329_RevF_Sep19%2C2016.pdf) states default 38.4 MHz and automatic standard-frequency detection using an accurate externally stable 32.768-kHz LPO during POR.

**Do not equate XTALFREQ raw code 15 with 38.4 or 40 MHz yet.** [One later proprietary PMU table for another BCM family](https://android.googlesource.com/kernel/google-modules/wlan/bcmdhd/bcm4383/+/96454dff665397c5f08bbb83d1b54f9a027faf81/hndpmu_priv.h) maps code 15 to 38.4 MHz in a 960 MHz PLL family; [Linux SSB legacy PMU1 table](https://kernel.googlesource.com/pub/scm/linux/kernel/git/mda/linux/+/refs/tags/v6.17-rc7/drivers/ssb/driver_chipcommon_pmu.c) maps code 14 to 38.4 and 15 to 40 MHz. Neither table is proof of BCM4329B1 PMU's actual encoding. Determining actual PMU revision and clock resource state is the immediate evidence gate.

## v036 bounded measurement design
At existing v035 T0/T1/T2/T3/T4/T5 observation sites, add *only documented, non-destructive register reads*:
- ChipCommon revision, actual PMU revision, PMU status (`pmustatus`, 0x608);
- resource active (`res_state`, 0x60C), resource pending (`res_pending`, 0x610);
- ChipCommon `gpiopullup` and `gpiopulldown` (only if actual ChipCommon revision >=20);
- preserve v035 PMUControl, CHIPCLKCSR, IOEx and IORx timestamps and error codes.

Register offsets and names are defined in the pinned Linux 7 `drivers/net/wireless/broadcom/brcm80211/include/chipcommon.h` and `include/linux/bcma/bcma_driver_chipcommon.h`. Read-only access is not zero-effect (backplane transactions consume time); compare timestamps against v035 and keep the same firmware/NVRAM and MMC2 AUTO profile.

No new writes, changing PMU clock settings, pin/rail power toggles, firmware swaps, USB resets, reboot or flashing. Stop immediately on any abnormal resource-read or USB response; verify modules unload and MMC2 remains bound. Do not publish firmware, calibration, device MAC or unique identifiers.

**Not yet established:** actual BCM4329 code-15 clock mapping, CPU firmware execution, source of the T3→T4 write, definitive resource readiness, or Wi-Fi fix.
