# v020 additional image and repeated live MMC2 test — 2026-10-24

Status: MMC2 card re-enumeration and runtime OEM capability switching PASS physically; BCM4329 Wi-Fi F2 readiness FAIL (-62); long-running stability not qualified.

## Exact candidate
- Replacement MZ600 only, temporary fastboot boot; no partition flash.
- Candidate size: 6,662,144 bytes.
- Candidate SHA256: 96f01d72782cd3ab6574b806a0d84b1874ec0f98bbe865c74365623ba7148067.
- RAM initramfs SHA256: 060664a25adf9fa90136e0e10fd186f41fb397b920698c04d8e89b100a8fcb67.
- This is DISTINCT from earlier published v020 images with SHA256 b08863d6... and e23e3dea.... Differences are not yet accounted for. Do not treat the artifacts as interchangeable.
- v020 ARMv7/no-NEON selftest and Android boot header/kernel/DTB/initramfs validation PASS. Original mmc core source restored SHA256 cfc4635e4ae8c5690535b3933a4fd5387d3fbe6256f575c8794b074248fbf8f6, build config restored byte-identically.

## Actual repeated physical sequence
- USB host identified V20, MMC2 controller c8000200.mmc, and BCM4329 SDIO functions. Initial kernel profile AUTO=0.
- Loading Broadcom driver modules and sending MMC2_REINIT returned DENIED PREFLIGHT; controller remained bound. Both modules later unloaded cleanly.
- AUTO->AUTO MMC2_REINIT PASS: mmc2 card removed and re-enumerated. Effective card SDIO version 1, high-speed 0.
- AUTO->MOTOROLA: kernel profile changed to 1 PENDING, then MMC2_REINIT PASS. Kernel observed effective version 2, multi=1, low=0, wide=0, highpower=1, highspeed=1. New HIGH-SPEED SDIO card enumerated.
- With Motorola mode, v017 instrumented brcmfmac driver loaded, reported raw SPEED=0x03, actual host clock 46,153,846 Hz, timing=2, IOEx=0x06, IORx=0x02 and timeout -62; no wlan0.
- MOTOROLA->AUTO: MMC2_REINIT PASS. Kernel observed version 1, high-speed 0 and ordinary SDIO card enumeration.
- A second complete AUTO->MOTOROLA->AUTO cycle repeated both transitions and verified the effective kernel fields. Five MMC2 detach/rebind actions passed across the test sequence without another deliberate kernel reboot.
- Final MMC2_STATUS: target VALID, BOUND YES, BCM4329 VERIFIED, Broadcom modules UNLOADED, profile 0 AUTO; USB CDC command channel responsive.

## Strict limits
- The rebind is not proven to power cycle BCM4329's regulator, 32k oscillator or reset GPIO. It is full MMC2 card re-enumeration, not necessarily chip cold start.
- Different v020 images were observed; exact cause of hash differences remains unresolved, so no reproducible stable release is claimed.
- A separate earlier v020 session was observed to restart unexpectedly. No causal link to a particular reinit has been proven; long-duration stability is NOT accepted.
- Working Wi-Fi and MAC/regulatory identity were not demonstrated. Generic board NVRAM was used. No RF scan, association or DHCP performed.
- Private device IDs, firmware bytes and original recovery image were not published or modified.
