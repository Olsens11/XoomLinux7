# MZ604 persistent Linux 7 boot to Debian COM10 login — dated physical evidence, 2026-10-30

**Evidence classification:** actual physical boot and serial-console observations with explicitly limited claims, reported through connected Surface in the October 30 conversation. This record supersedes the older 2026-10-29 "**Linux has not booted**" as-of statement for the same MZ604, without altering that valid historical checkpoint. **NOT a Wi-Fi pass. NOT an authenticated Debian-shell pass.**

## Target / preserved storage

Dedicated unlocked Motorola Xoom MZ604 Wingray `xoom-wifi`, bootloader 1050; earlier two `fastboot boot` attempts returned `(00000008)` before kernel execution. Owner authorized subsequent persistent Linux installation. No EBB/BCT/p1/GPT modification. p6 TWRP 3.1.1-0, full backup SHA256 `a99ca1a761dbe2387f4a7e7a1ce8a19210489af6a2faeda6df6dc48c62fb3c3c`. p7 previously staged known-good Linux installation; p8 256MiB mini-Linux SHA256 `297eee632621b006b0e92eee4b37eb2e6bac8ba91aa2467b46a4d2f32384a03c`; p10 userdata retains `/data/xoomlinux7/rootfs.ext4` (~2GiB) SHA256 `8c3daf6b39ea8df166b243568336254d7d60c0819ee895ccaa68afd4cbaec4ed`.

Surface preflash private backups, original p7 SHA256 `c1df6dd7e810df45d6668e0458e4ffb365ef87a64b7599f14be0abd3194df66d`, original p8 SHA256 `71447f893d7df4ee91ffefd5966b52d05d13ef4868e150a99e0cc0fdd6a48b40`; exact paths in `C:\Users\olsen\xoom-linux-rom\inspection\MZ604-LINUX7-INTERNAL-PHYSICAL-CHECKPOINT-20261030.md`. OEM stock recovery-restoration script was renamed and preserved before replacement system became Linux p8; latest independent p6 readback before flashing was unchanged.

## Exact successful USB study

Separate diagnostic Wingray DTB changed controller compatible `nvidia,tegra20-ehci` → `nvidia,tegra20-udc`, controller and PHY `dr_mode` OTG → peripheral, using existing USB gadget serial config. Study DTB SHA256 `4a63058b61cb06307ed592290d7d025fcee2ee493a2ceb2ee33bb8ea65fae11d`. Owner-flashed p7 study image 7,104,512B SHA256 `56741fcc04f83dd7fb7a7e794e9c5ec21a8a21348401bb686a2d4abc4741c6a2`; early serial enumeration on Surface: **USB Serial Device (COM10)**, interactive `/ #` rescue shell. This is a diagnostic boot-harness DTB, **not a claim of bit-identical original Wingray DT physical qualification**.

Live serial stage evidence showed kernel initramfs `MZ604_INIT`, internal MMC, p8 startup and p10 Debian loop file mount. Initial stop was `missing Debian init`; stage2 `[ -x /newroot/sbin/init ]` followed an absolute symlink in the wrong root. Privileged rescue used BusyBox to back up p8 `/system/sbin/xoom-start.sh.pre-serial-fix`, replace the check with `[ -x /newroot/usr/lib/systemd/systemd ]`, remount p8 read-only, and create `getty.target.wants/serial-getty@ttyGS0.service` inside p10 Debian. A controlled reboot disconnected and later re-enumerated COM10; received **`xoom-wingray login:`**.

## Negative/unknown qualifications

- Fresh staged ARMhf Debian root and 114 matching Linux 7 modules were prepared offline, but there is **NO successful interactive Debian login**. Original source root template and packaged ext4 `/etc/shadow` both show `root:!*` and `xoom:!`: locked account authentication. This was explicitly documented by the prior `BASELINE_BUILD_AND_USERSPACE_2026-10-29.md`. This must be corrected only through verified privileged recovery, with selected private password/sudo policy; no guest account was provisioned.
- MZ604 `wlan0`, real original firmware request/return, per-device MAC provenance, SDIO F1/F2, channel inventory, 2.4GHz scan and WPA/DHCP all **NOT RUN** on this exact new runtime. Do not import MZ600 physical Wi-Fi results as MZ604 measurements.
- Physical recovery mode via Linux reboot request, p8 selector, kexec and unattended crash recovery all **NOT RUN**. Prior source config has `CONFIG_KEXEC=y` and watchdog/pstore capabilities only. Owner accepts physical restart, forbids bootloader modifications; no automated crash framework is required.

## Immediate next gate

With owner physically available, establish verified TWRP boot, offline backup and private login provisioning. Then exact COM10 authenticated shell and normal reboot PASS; only then guarded recovery reboot and minimal p8 root selector. All device tests require exact identity/image checks and evidence/rollback. See [infrastructure plan](../rfc/bcm4329-upstream-first/REMOTE_TEST_INFRASTRUCTURE_PLAN_2026-10-30.md) and [source reading map](../rfc/bcm4329-upstream-first/AGENT_READING_MAP.md).
