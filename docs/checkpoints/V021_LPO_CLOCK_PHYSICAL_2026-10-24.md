# v021 LPO clock software-state observation — physical MZ600 — 2026-10-24

Result: the read-only v021 Broadcom diagnostic module ran on the real replacement MZ600 in the v022 temporary-boot RAM environment. **Linux reports its Wi-Fi pwrseq clock provider enabled at 32768 Hz; WLAN Function 2 still times out -62.**

## Exact module and method

- Device initial MMC2_STATUS: target valid, bound, BCM4329 verified, AUTO profile 0, Broadcom modules unloaded.
- ARM module brcmfmac-v021-lpo-readonly.ko: 462492 bytes, SHA256 13fb5af5cc637bf77d61fed8c7199dbaef2d979879e49669fe6c72387cb5007d, builder and Surface hashes matched.
- Existing USB BRCMFMAC upload succeeded: device responded UPLOAD DONE SIZE 462492 CRC32 0x1260F727; host verified transfer CRC.
- WIFI_START returned brcmutil rc 0 and brcmfmac rc 0 with debug 6.
- Source observer obtains the pwrseq clock via device tree then reads clk_get_rate and __clk_is_enabled, without altering clock, power, reset, firmware or MMC bus state.

## Actual kernel log

    XOOM_LPOV021 pwrseq rate=32768 enabled=1
    XOOM_F2V021 RAW cccr=11/0 caps=02/0 power=01/0 speed=01/0
    XOOM_F2V021 CARD sdio_vsn=1 multi=1 low=0 wide=0 highpower=1 highspeed=0
    XOOM_F2V021 HOST clock=25000000 timing=0 buswidth=2 signalvoltage=0 vdd=21
    XOOM_F2V021 before ioex=02/0 iorx=02/0 clkcsr=d2/0 clkstate=3
    XOOM_F2V021 after ioex=06/0 iorx=02/0 clkcsr=d2/0 result=-62

No wlan0. Standard firmware and OEM-matched generic NVRAM unchanged.

**Interpretation limit:** kernel software reports the clock requested/enabled at nominal 32768 Hz. This does not establish actual physical pin waveform, voltage, clock delivery, frequency stability or correct sequence relative to settled WLAN core supply. The normal driver message 'no LPO clock' means no directly assigned LPO clock to its device; a separate mmc-pwrseq clock may still be enabled.

## Final verified device state

WIFI_STOP: brcmfmac rc 0, brcmutil rc 0. MMC2_STATUS: target valid, bound, BCM4329 verified, modules unloaded, profile AUTO=0. USB responsive. Temporary RAM boot only; nothing flashed.

## Next discrimination

Audit OEM U4 (WLAN power) and U2 (reset) 100/100/200ms sequence against modern regulator/mmc-pwrseq and datasheet >=110ms after VDDC/VDDIO stable. Probe electrical signal at valid accessible board test pads with suitable scope if available; avoid inferring pin waveform from Linux software state. Separately instrument WLAN Cortex-M3 startup/SDPCM mailbox progress before F2 enable. Distinguish fresh MMC2 enumeration from actual chip power cycle.
