# MZ604 Wingray — first physical upstream fastboot RAM-only attempt (2026-10-29)

**Outcome: FASTBOOT DOWNLOAD PASS; temporary `boot` command FAIL on bootloader, native Linux kernel NOT entered.** No kernel regression, MMC, SDIO, firmware or Wi-Fi conclusion can be drawn from this test.

## Target and scope
- Selected test specimen: **Motorola Xoom MZ604 / Wingray Wi-Fi-only**, connected to **SURFACE-BOOK-2**. Private serial withheld from public record.
- Previously verified stock Android properties: `ro.product.device=wingray`, `ro.product.name=tervigon`, stock Android `4.1.2/JZO54K`, bootloader `1050`, full battery.
- User confirmed this newly purchased eBay tablet has no personal installation data worth preserving; they accepted factory data erasure during `fastboot oem unlock`. Prior to unlock, private copies of stock **1594-byte `bcm4329.cal`**, **259327-byte `fw_bcmdhd.bin`**, and **266967-byte `fw_bcmdhd_apsta.bin`** were captured and hashed on Surface. No proprietary binaries or device identity added to Git.
- Fastboot read-only checks **PASS**: `product=xoom-wifi`, `version-bootloader=1050`, and after user on-device unlock confirmation, `unlocked=yes`. No additional flashing or partition manipulation.
- Baseline kernel source: pinned upstream `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`, **zero patches**. Built `zImage`, original `tegra20-motorola-wingray.dtb`, and matching ARM modules; built distinct off-device RAM-only diagnostic image.
- Trial image: `MZ604-WINGRAY-UPSTREAM-RAMONLY-UNTESTED.img`, **5,892,096 bytes**, SHA256 `9be975cbe4ed6ee8ee3b362775b6d36159ea10b87ebf22cb07d2662eb5c9877c`. Android legacy boot image header with ARM zImage + appended original Wingray DTB, tiny diagnostic cpio initramfs, `rdinit=/init`; no write-capable persistent filesystem in the temporary image.

## Standard desktop → Surface transfer
- Followed canonical [transfer SOP](../process/DESKTOP_SURFACE_XOOM_ARTIFACT_TRANSFER.md): desktop WSL → Windows trial staging → temporary, pre-existing verified Python HTTP listener **192.168.0.125:43157** serving exact trial directory → Surface native PowerShell `Invoke-WebRequest` into a fresh private trial capture directory → independently verified **5,892,096 bytes and exact SHA-256 match**.
- The first transfer attempt was rejected by the Windows firewall; user allowed the rule. **Retry on same documented port succeeded.** An earlier unintended ad-hoc HTTP port 18881 was stopped. The established 43157 listener later disappeared/was closed; no old listener remained at last check. Avoid inventing alternate transfer methods.
- Preserve actual transfer receipt and original firmware only on the authorized computers, never in public Git.

## Physical fastboot observation
The single authorized, target-selected command was equivalent to:

```
fastboot -s <PRIVATE_SERIAL> boot <LOCAL_VERIFIED_RAMONLY_IMAGE>
Sending 'boot.img' (5754 KB)                       OKAY [  0.547s]
Booting                                            FAILED (remote: '(00000008)')
fastboot: error: Command failed
```

- **Download accepted; bootloader refused the `boot` operation.** No Linux dmesg, display, init, SDIO, `wlan0`, firmware or regulatory data were produced.
- Subsequent read-only queries: `fastboot devices` remains present and `unlocked=yes`. The bootloader's `max-download-size` and partition size getvars returned **blank values**, not validated sizes or evidence of support.
- An offline Android legacy header comparison with archived historically generated MZ600 Linux boot images shows **matching** `kernel_addr=0x10008000`, `ramdisk_addr=0x11000000`, `second_addr=0x10f00000`, `tags_addr=0x10000100`, `page_size=2048`, same general image type/format. This does **not prove** MZ604 bootloader acceptance or compatibility; original MZ604 stock boot image has not been acquired.
- Public Motorola Xoom documentation describes **flashing** verified images rather than guaranteeing `fastboot boot` on every device/bootloader revision. Neither unsupported temporary boot nor a particular validation fault can be asserted from this sole numeric error without source-backed meaning. [Google AOSP Xoom flashing notes](https://source.android.com/docs/setup/test/running); [TWRP original Xoom fastboot recovery instructions](https://twrp.me/motorola/motorolaxoom.html).
- No `fastboot flash`, `erase`, `format`, partition edits, radio transmission, or SD card writes were performed during the trial. The authorized bootloader unlock's OEM factory reset is distinct and was user-confirmed.

## Next engineering gate
1. **Do not retry blind variations of the same `fastboot boot` command.** Establish MZ604/bootloader1050 temporary-boot support (or absence) from original source/known-good model-specific precedents and inspect stock boot/recovery backup availability.
2. If temporary boot is genuinely unsupported, propose an **explicitly approved**, target-specific **reversible** alternative with validated image size and rollback/recovery path (likely a carefully selected recovery image or boot partition), rather than issuing `fastboot flash` without permission. The user should choose the persistent target before any flash.
3. Separately provision the verified Debian ARMHF root filesystem on **approved removable microSD**, and ensure fresh local credentials and private board-specific firmware/calibration prior to functional WLAN testing. No media write is currently approved or completed.
4. After any actual Linux boot, prove UART/console and kernel/DTB first, then SDIO + firmware and 2.4GHz regulatory-correct network functionality. No scan/association assertions yet.

**Milestone state:** W0 and offline W1 source/build/transfer PASS, MZ604 hardware identity/unlock confirmed, first temporary boot negative, Linux runtime W1 still OPEN. Older MZ600 patches and installed systems unchanged.
