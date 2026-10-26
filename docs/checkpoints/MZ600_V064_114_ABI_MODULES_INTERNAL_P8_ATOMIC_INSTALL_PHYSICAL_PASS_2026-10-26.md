# MZ600 Linux7 v06.4 — 114 ABI-exact modules installed on internal p8: PHYSICAL PASS

**Date:** 2026-10-26. **Target:** authorized experimental replacement Motorola Xoom MZ600, not the protected original. **Milestone:** 114 compatible modules installed under the current kernel's exact versioned Debian module tree. No boot-partition/GPT/recovery writes, no reboot and no live radio insertion during this milestone.

## Background and verified input

Previously proven persistent Linux `7.0.0-next-20260422+` Debian 12.15 from internal BigPart `/dev/mmcblk0p8 ext4`; byte-verified permanent boot p7 (see physical p7 checkpoint). Offline matched modules built/ELF vermagic+modversion QA passed for all 114. Initial tar.xz on Xoom had failed solely because `xz` was unavailable, leaving empty `/lib/modules/.stage-v064-YDDcoY1R`. A sanitized symlink-free gzip tar was subsequently transferred RAM-only with actual Xoom-side SHA256 PASS.

Owner reported COM9 open for unattended work. Surface independently confirmed serial exclusivity open PASS, root prompt, UID0, kernel exact ABI, internal p8 ext4 and the SHA of `/run/mz600-v064-stageD-matched-modules-gzip-safe.tar.gz`:

- Exact bytes **2,798,775**, SHA256 **`5e051de2a1cf9875414886966a1ff00cf3ec5ba038b0688e7f7750ea2594a409`**.
- Root filesystem `df -Pk` 495,712 KiB available before install.
- Preexisting legacy module directory `/lib/modules/7.0.0-next-20260422` remained present; target `/lib/modules/7.0.0-next-20260422+` absent.
- XZ orphan staging `/lib/modules/.stage-v064-YDDcoY1R` physically inspected: empty, 4KiB, untouched and retained.

## Guarded one-time script, host transport, and physical result

Canonical script `scripts/host/xoom/install-v064-stageD-matching-modules-once-20261026.sh` (source SHA256 `43df19ca162d13735841b860469def7d6cc1603b078a68f04aaf29aef5585dbb`) previously passed Desktop WSL `bash -n`. Exact source wrapped for safe TTY heredoc on Surface at `captures/MZ600-V064-SAFE-GZIP-114-Modules-OWNER-PASTE-ONCE-20261026.txt` SHA256 **`21b8599389e311607066fdb6602628db116c61361bddba9b5343817fbffe78ba`**; its decoded inner source SHA was independently checked equal to canonical.

A one-shot serial sender was created locally on Surface after the user authorized unattended execution. First invocation stopped BEFORE sending any installer lines because the parser matched the echoed text of the read-only preflight command rather than standalone preflight output markers. The parsing code was surgically corrected to require exact standalone terminal output lines; Python syntax passed. **No installer was sent and no module writes occurred on that first aborted invocation.** The second invocation successfully verified the physical UID0/ABI/internal-p8 read-only probe, sent the 95-line exact Bash heredoc once over COM9, and awaited installation output. Native Surface process **exit 0** (runtime 20.56s).

Xoom's actual privileged shell output:

```text
MZ600_V064_SAFE_GZIP_INSTALL_PREFLIGHT_BEGIN
/run/mz600-v064-stageD-matched-modules-gzip-safe.tar.gz: OK
KERNEL=7.0.0-next-20260422+ ROOT=/dev/mmcblk0p8 EXT4 FREE_KIB=495712 TAR_ENTRIES=189
INSPECT_PREVIOUS_XZ_FAILURE_STAGING_NO_DELETE:
/lib/modules/.stage-v064-YDDcoY1R
4.0K /lib/modules/.stage-v064-YDDcoY1R
EXISTING_MODULE_DIRECTORIES_NO_DELETE:
/lib/modules/.stage-v064-YDDcoY1R
/lib/modules/7.0.0-next-20260422
MZ600_V064_PREFLIGHT_PASS
NEW_STAGING_PATH=/lib/modules/.stage-v064-gzip.KGM8eFF5
MZ600_V064_STAGING_VERIFIED_MODULES=114 LINKS=0 SPECIAL=0
MZ600_V064_MATCHED_MODULES_ATOMIC_MOVE_PASS
MZ600_V064_DEPMOD_PASS
insmod /lib/modules/7.0.0-next-20260422+/kernel/drivers/net/wireless/broadcom/brcm80211/brcmutil/brcmutil.ko
insmod /lib/modules/7.0.0-next-20260422+/kernel/drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko
insmod /lib/modules/7.0.0-next-20260422+/kernel/drivers/net/wireless/broadcom/brcm80211/brcmutil/brcmutil.ko
insmod /lib/modules/7.0.0-next-20260422+/kernel/drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko
insmod /lib/modules/7.0.0-next-20260422+/kernel/drivers/net/wireless/broadcom/brcm80211/brcmfmac/wcc/brcmfmac-wcc.ko
MZ600_V064_MODULE_DRY_RUN_PASS_NO_RADIO_LOAD
MZ600_V064_MODULE_INSTALL_COMPLETE_ABI_114
```

The two `modprobe -n -v` checks are DRY-RUN plans; `insmod` lines are **printed**, NOT executed. Do not infer driver load or Wi-Fi availability from them.

**Dedicated private Surface receipts** (no public raw device secrets): `captures/MZ600-V064-MODULES-INSTALL-COM9-ONCE-20261026-output.txt` SHA256 `356caea568f6ad5a4b332cd038f9c34200809f2de2bcc4e95990f514b54d91f8`; success JSON `captures/MZ600-V064-MODULES-INSTALL-COM9-ONCE-20261026-result.json` SHA256 `2636ae8d52f0546c8980e796516ee368f73da01282f753418ba2c1ff35763295`, flags `installer_finished_success=true`, all six required checkpoint markers, canonical source SHA match.

## Independent on-Xoom read-only postinstall evidence

A fresh separate COM9 root read-only audit, after the installer had exited and closed its serial handle, returned:

```text
uname -r                             7.0.0-next-20260422+
findmnt -n -o SOURCE,FSTYPE /         /dev/mmcblk0p8 ext4
find /lib/modules/7.0.0-next-20260422+ -type f -name '*.ko' | wc -l    114
test -s /lib/modules/7.0.0-next-20260422+/modules.dep                  PASS
test -d /lib/modules/7.0.0-next-20260422                              PASS
ls /sys/class/net                    ip6tnl0 lo sit0
cat /proc/modules | grep brcm        no matches
```

So internal p8 now contains the correct 114 actual `.ko` files and depmod metadata; prior legacy tree survives; no live Broadcom modules were loaded and no `wlan0` exists yet. XZ residual empty stage was intentionally preserved without cleanup.

## Next actions: controlled tests, with separate checkpoint

- Inspect actual installed firmware, factory MAC source, regulatory state and live `/sys/bus/sdio/devices` read-only. `wlan0` is still not present because drivers are not loaded. Do not assert Wi-Fi scan/network success.
- Diagnose PID1/systemd and D-Bus separately with `ps -p 1`, `/proc/1/exe`, `/run/systemd`, `/run/dbus`, journals and service links; avoid auto-start or mass changes.
- Only after confirming correct radio/firmware provenance decide on bounded driver `modprobe` and controlled cleanup with WCC first. Do not RF-scan/associate without board regulatory qualification.
- Update latest handoff, runtime ledger, status and check repository; do not rebuild 114 modules or touch verified p7/GPT for these follow-ups.

**Accepted result:** MATCHED MODULES INSTALLED PHYSICALLY PASS. DEPENDENCIES DRY-RUN PASS. LIVE WIFI/BT NOT YET TESTED ON P8 DEBIAN.
