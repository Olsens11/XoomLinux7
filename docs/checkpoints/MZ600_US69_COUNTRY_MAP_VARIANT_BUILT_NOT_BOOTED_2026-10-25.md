# MZ600-US regulatory variant: offline build and one-click temporary boot preflight (2026-10-25)

**Status:** Separate DTB and Motorola-calibrated NVRAM candidates prepared. New temporary boot image transferred and SHA256 verified on Surface; user-facing boot launcher created and its **non-mutating preflight passed**. **The new candidate has NOT been booted yet.** Running Debian, current microSD root and Android/TWRP eMMC were not modified by this milestone; no wireless scan, association, interface UP or country-setting request issued.

## Why isolate the experiments

The existing physical Debian Bookworm image **PASS** boots with upstream Linux7, ext4 root, dynamic factory MAC handoff, USB ttyGS0 and BCM4329 `wlan0` (currently down). The official Debian signed `wireless-regdb 2026.05.30-1~deb12u1` was installed by the user through Surface's interactive COM9 console; `regulatory.db` and `.p7s` symlinks resolve to the upstream-signed pair. **Linux global regulatory country remains 00**, and Broadcom's custom PHY reports 99, by design. Two archived Motorola US MZ600 factory calibration files (HRI39/HRI66) agree on `ccode=US` and `regrev=69`; BCM4329 Linux driver does not offer generic ISO country-code fallback without an explicit board mapping.

The generic source `tegra20-motorola-stingray-usbdiag.dts` has `compatible = "motorola,stingray"` rather than a guaranteed US-MZ600-only ID. Therefore **do not hardcode US/69 into the shared source**. Build a board/jurisdiction-specific variant as a separate output, and always preserve the known-working generic image.

## Experiment A: MZ600-only country-map DTB, no firmware NVRAM replacement

Desktop WSL paths:
- Compiled baseline DTB: `/home/xoomdev/xoom-linux-rom/os-build/kernel/arch/arm/boot/dts/nvidia/tegra20-motorola-stingray-usbdiag.dtb`
- Output dir: `/home/xoomdev/xoom-linux-rom/os-build/variants-mz600-us-20261025/`
- Baseline copied DTB SHA256: `afae7fb328bc66c0ea186ef6c8e77164c41be8588bb5d14303374a3545499959`
- New `tegra20-mz600-us69.dtb` SHA256: `8ab57ae535b86d64aa3a42992d49deacbbef88b6986087b288b0d626ce613d4e`

Constructed by copying compiled DTB to a new path and applying **only**:

```bash
fdtput -t s tegra20-mz600-us69.dtb /mmc@c8000200/wifi@1 brcm,ccode-map US-US-69
```

Verified `fdtget` returns `US-US-69`, `wifi@1 compatible` remains `brcm,bcm4329-fmac`. Decompilation via `dtc -I dtb -O dts` and strict diff check demonstrated **exactly one added property and zero removed/modified properties**:

```diff
+ brcm,ccode-map = "US-US-69";
```

No other clock, regulator, GPIO, Wi-Fi MAC, factory identity, SDMMC, bootloader or firmware node changed. No hardcoded MAC present. The original DTB and code remain unchanged.

Boot image: concatenated exactly the existing (known-booting) Linux7 `zImage` + new variant DTB, and built an Android-format boot container with **the exact previously successful 754,277-byte non-empty gzip CPIO ramdisk that omits /init** and the correct private root `PARTUUID` + normal Debian `/sbin/init` boot arguments. Input known-good boot image was hash verified before build: `c84172c23e149bf8f215eb78284efeb46aa0a13090df4c159a7ab5d3c2a8cb8c`.

**New image**: `xoom-linux7-mz600-us69-TEMPBOOT.img`, **6,645,760 bytes**, SHA256 **`33dd667d97544c2343b7806fa53b19d5b6c94d3153cdcfd671852b6373bc28ae`**. The desktop build and Surface copy match this digest. Local Surface path: `C:\Users\olsen\xoom-linux-rom\downloads\xoom-linux7-mz600-us69-TEMPBOOT.img`. Root PARTUUID is not included in public documentation; it is preserved byte-for-byte from the proven physical Debian startup.

**Experiment A should happen before any calibration change**, so we can observe whether a userspace US country hint with proper country-code mapping can be translated into firmware's accepted country revision. The already-loaded Broadcom regulatory pseudo country 99 may remain separate from the global country—do not misinterpret that alone as failure.

## Experiment B: separately staged OEM-calibration NVRAM (NOT installed)

We generated a *separate* no-MAC candidate based on the exact 1550-byte generic Debian staging root file `lib/firmware/brcm/brcmfmac4329-sdio.txt`:
- Baseline no-ID text SHA256 `a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb`, 1550 bytes.
- Candidate filename `brcmfmac4329-sdio-mz600-us69-calibration-no-mac.txt`, **1569 bytes**, SHA256 **`bd76afc11469c4d2b377186f88ff23bba0180576867482b48f7d313bf9fd8610`**.

Exactly two OEM-validated fields were appended, leaving every previous byte unchanged:
```ini
ccode=US
regrev=69
```

Validation: neither generic nor variant NVRAM contains `macaddr=` or any statically copied device MAC. Dynamic MAC injection from the bootloader ATAG/FDT remains mandatory. The candidate is committed in GitHub at `configs/os/brcmfmac4329-sdio.mz600-us69-no-mac.txt` but **is NOT deployed to the running SD root**; no new WLAN firmware has been loaded. Only consider deploying it with a full backup and a separate test if Experiment A fails or after firmware-country acceptance readback establishes its need.

## Surface user-activated temporary boot procedure

Created:
- Launcher: `C:\Users\olsen\OneDrive\Desktop\Xoom - Boot MZ600 US69 Test.cmd`
- Script: `C:\Users\olsen\xoom-linux-rom\downloads\Start-Xoom-MZ600-US69-TempBoot.ps1`
- Desktop-side offline builder: `C:\Users\olsen\Downloads\build-xoom-mz600-us-variant-tempboot.sh`.

PowerShell parser and `-PreflightOnly` mode were tested **PASS**. The test reports image SHA and exact size accepted and live COM9 present, **without rebooting/activating image**.

The user closes their currently open `Xoom USB Console` window using Ctrl+], then runs the desktop launcher and presses any key. The launcher opens COM9, requires active authenticated `xoom` shell, verifies `wlan0` is DOWN, requests normal `sudo reboot`, and lets the human supply sudo password locally on Surface when prompted (not stored or retrieved by script). The tablet returns to original Android boot by default; script waits for correct Android ADB target `170061c243805617`, `ro.product.device=stingray`, `sys.boot_completed=1`. It commands `adb reboot bootloader`, verifies fastboot product `xoom-cdma`, bootloader `unlocked=yes` and matching image SHA256 before doing **only** `fastboot boot` (RAM, no flash). It then checks whether Linux COM9 returns.

All safeguards are fail-closed; if any prerequisite fails, do not force the boot action. **No test has run since image staging**. Do not claim kernel signature DB acceptance, country change, RF compliance, or firmware acceptance based only on the compilation.

### What to measure *after* Experiment A boot

1. Confirm booted kernel still mounts `/dev/mmcblkXp1 ext4 /` using private stable PARTUUID, Linux7, Debian12, USB ttyGS0 COM9 and old/new MAC remains identical (no device identity leak).
2. Read `/proc/device-tree/mmc@c8000200/wifi@1/brcm,ccode-map` to prove effective map is `US-US-69`.
3. Confirm signed regdb + detached .p7s targets still point to upstream-signed alternatives; kernel signature acceptance requires actual regulatory request test and dmesg.
4. Confirm `wlan0` is DOWN; then via *human-authorized privileged Surface serial console* request `iw reg set US` while down; inspect `iw reg get`, channel list, driver logs and any error indicating country iovar rejection. Neither a world-US display nor lack of log is conclusive **firmware country revision readback**.
5. If necessary, design a diagnostic for direct Broadcom `country` iovar readback. Do not raise TX power, unlock 5 GHz/ch12–14, scan or associate yet.
6. Keep known-good successful boot image on Surface for recovery. No eMMC image flash, no ext4 reformat.

**Overall state:** Experiment A candidate built and integrity-checked, not booted. Experiment B NVRAM built, not installed. Running generic Debian preserved.
