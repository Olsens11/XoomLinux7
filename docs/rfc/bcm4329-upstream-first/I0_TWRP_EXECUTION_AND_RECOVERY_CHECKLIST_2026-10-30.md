# MZ604 — exact TWRP recovery-to-development execution checklist

**As-of: Friday, 2026-10-30 13:42 EDT. This is a future-session procedure, NOT evidence of new device access.** Owner physically enters the **existing MZ604 TWRP** when home; an authorized agent then drives recovery ADB from the Surface. **Never modify bootloader, BCT, EBB, GPT, p1, p6 TWRP or stable p7. Do not change p8 during initial account recovery.** Physical reboot after kernel failure is acceptable; do not add speculative watchdog/crash recovery. Read the [comprehensive handoff](../../handoffs/MZ604_I0_SURFACE_RECOVERY_READY_COMPREHENSIVE_HANDOFF_2026-10-30.md) and [all chronological logs](../../project-log/README.md) first. Every claim is time-scoped.

## Who does what

The owner only boots the **MZ604** into original TWRP 3.1.1-0 and leaves it USB-connected to **SURFACE-BOOK-2**. The agent then verifies identity, mounts/inspects the correct userdata if needed, backs up live Debian, installs the prepared I0 image, verifies COM10 and privileged shell, and proceeds through clearly separate later tests. **No user-provided password is needed**: isolated USB serial should auto-login as `xoom`, sudo without password, local fallback `1234`.

The active tablet is *as of this record* running the earlier Linux p7→p8→p10 Debian **login prompt** on Surface COM10, **NOT authenticated**. It is **NOT in TWRP** and ADB is empty. The new images on Surface are not yet installed. An earlier Motorola `fastboot boot` rejection was genuine but superseded for normal boot by owner-flashed persistent p7. No Wi-Fi baseline has been taken from this MZ604 Linux runtime.

## Exact host/payload paths, separate evidence

- **Surface payload directory:** `C:\Users\olsen\xoom-linux-rom\staging\MZ604-READY-V2-20261030`. Manifest SHA256 `331f36e4340ba14f78c9217f8e66cd1175c907dfacddff202c33b3161848ddb6` (pinned). All **10** payload items separately length/SHA verified on Surface; three gzip ext4 files independently stream-decompressed and verified; 114 matched modules present. Detailed [payload manifest and raw/compressed hashes](I0_TWRP_DEPLOYMENT_READY_2026-10-30.md).
- **Live TWRP read-only safety/backup utility** on Surface: `C:\Users\olsen\xoom-linux-rom\MZ604-TWRP-I0-SAFE-GATE-20261030.py`, SHA256 `157693db5f691d559a2016ee8cfa3517942799cae1e2faaaae29399a3cf053f2`. Only `inspect` and `backup` phases, no partition write/flash/reboot.
- **Separate guarded installation utility** on Surface: `C:\Users\olsen\xoom-linux-rom\MZ604-TWRP-I0-STAGE-AND-PROMOTE-20261030.py`, SHA256 `895fc3eb0c39b94824237b85369739eb1ffc6434493f13ffe1dc39c7d5bf0482`. Explicit `check`, `stage`, `promote` phases. Only `stage` and `promote` can write within the verified p10 `/data/xoomlinux7` directory; no reboot/bootloader/p7/p8/p6 logic. Requires full independent Surface backup receipt and rereads actual TWRP identity/mount/live SHA before operations.
- **Read-only COM10 post-boot acceptance utility:** `C:\Users\olsen\xoom-linux-rom\MZ604-COM10-I0-ACCEPTANCE-20261030.py`, SHA256 `e0313525e2a8ec36dabd4b39f6e4dada2a2dac8c9736d1af3bf699ad80969a2b`. Syntax tested; **NOT executed on hardware**. Probes `id`, `sudo -n id`, `uname -r`, loop device and actual shell output; no privileged mutation. COM10 may be held exclusively by the older graphical `MZ604-COM-Console-20261030.py`; release that host-side handle if needed without logging out or rebooting the tablet.
- **Private host-only test scripts:** `MZ604-TWRP-I0-SAFE-GATE-MOCK-TEST-20261030.py` and `MZ604-TWRP-I0-STAGE-AND-PROMOTE-MOCK-TEST-20261030.py`, offline PASS; see [host-tool checkpoint](../../checkpoints/MZ604_I0_HOST_CONTROL_SCRIPTS_MOCK_PASS_2026-10-30.md). These paths and exact SHAs enable successor QA without publishing private device credentials/source images.
- **Protected original boot image** same as actual p7, SHA256 `56741fcc04f83dd7fb7a7e794e9c5ec21a8a21348401bb686a2d4abc4741c6a2`. **Do not reflash in I0.** Corrected p8 base and optional p8 selector V2 are **offline-only** and **not deployed as part of I0**. V1 selector is superseded/rejected.

## Gate 0 — owner returns, recovery actually appears

1. User places **MZ604** in TWRP recovery and tells agent; do not try `adb` writes or assume recovery merely because COM10 disconnects.
2. On Surface confirm `adb devices -l` shows the **specific known MZ604 recovery serial only** in `device` state, not MZ600 or another tablet. Verify TWRP `ro.twrp.version=3.1.1-0`, `ro.product.device=wingray`, physical storage map from `/proc/mounts` and partition inventory. If unknown, **STOP**; do not relax identity to make scripts pass.
3. If TWRP has not mounted `/data`, inspect the TWRP Mount UI and original device partition mapping; mount only the correct p10 with owner physically available. The host safety utility does not mount anything automatically.
4. Confirm Surface volume has enough space (~2.15GB for a full live-root backup, plus headroom); as of Oct30 Surface C had ~797GB free, but **recheck live**. 
5. Run from Surface, **READ-ONLY**:
   ```powershell
   python C:\Users\olsen\xoom-linux-rom\MZ604-TWRP-I0-SAFE-GATE-20261030.py inspect
   ```
   Must show exact MZ604 identity, expected `2146435072` byte current rootfs, SHA of **live** `/data/xoomlinux7/rootfs.ext4`, filesystem free space. Old staged image SHA may differ because original installed Debian was already modified to enable serial getty.

## Gate 1 — independent current-device backup; NO MUTATION

Run on Surface only after Gate 0:
```powershell
python C:\Users\olsen\xoom-linux-rom\MZ604-TWRP-I0-SAFE-GATE-20261030.py backup
```
This makes a **new, non-overwriting private Surface directory** `C:\Users\olsen\xoom-linux-rom\private-backups\MZ604-I0-LIVE-ROOT-<UTC>-<SHA>`, ADB-pulls the **actual mounted p10** original ext4 image, verifies full file size and exact live SHA **against the on-device pre-pull SHA**, and writes `BACKUP-RECEIPT.json`. STOP unless it reports `BACKUP_ON_SURFACE_VERIFIED`. Record that receipt's exact path. Never use an old MZ600/MZ604 reference image as a substitute for this live backup.

## Gate 2 — protected candidate stage (writes only *new* p10 files)

After verified backup and same TWRP identity, invoke three **separate** commands, reviewing each result before the next. Substitute the *actual* absolute backup receipt path printed by Gate 1 for the placeholder (use quotes):
```powershell
python C:\Users\olsen\xoom-linux-rom\MZ604-TWRP-I0-STAGE-AND-PROMOTE-20261030.py check --backup-receipt "C:\...\BACKUP-RECEIPT.json"
python C:\Users\olsen\xoom-linux-rom\MZ604-TWRP-I0-STAGE-AND-PROMOTE-20261030.py stage --backup-receipt "C:\...\BACKUP-RECEIPT.json"
```

**Do not run `stage` before `check` passes and the backup receipt is real.** Stage utility rehashes Surface payload, independently verifies full prior backup, re-runs safe TWRP identity and live-root hash, checks BusyBox applets and at least 2.8 million free 1K blocks, refuses existing stage/old-root filenames, ADB-pushes only compressed candidate under a new p10 stage name, verifies compressed SHA, decompresses with BusyBox gzip into a *different* no-clobber stage file, and verifies size/raw SHA. 
- Compressed candidate sha `0fcd28f6f2fd509c7c5af51ee1384c4acaad096209619e380762bbe626a13862`.
- Expected uncompressed `rootfs.i0-20261030.ext4.stage`: **2,146,435,072 bytes**, SHA256 `351ae328b62fce048ace29e5855425981e90f38534018c11c7cc03af6a66e0d1`.
- Original `rootfs.ext4` must retain the exact live SHA saved in `BACKUP-RECEIPT.json`.
- Stage may take minutes; commands are blocking, not background promises. If any command reports STOP, don't promote or delete partial files. Inspect actual state and reconcile names/hashes first.

## Gate 3 — same-partition promotion, with two independent rollback anchors

Only when `TWRP_I0_STAGE_VERIFIED` is observed and no other sessions have modified p10:
```powershell
python C:\Users\olsen\xoom-linux-rom\MZ604-TWRP-I0-STAGE-AND-PROMOTE-20261030.py promote --backup-receipt "C:\...\BACKUP-RECEIPT.json"
```
This verifies exact candidate/raw SHA and **unchanged original live-root SHA** again, refuses an already-occupied preserved-old filename, renames original `rootfs.ext4` to `rootfs.before-I0-20261030.ext4`, checks archived SHA, and renames staged candidate to canonical `rootfs.ext4`. It attempts the original-name restore if the second rename itself fails; stops without reboot on any post-check failure. New and old images both remain on p10, **plus** the independently SHA-verified Surface backup. **No p6/p7/p8/bootloader/GPT modification.** 
Require `TWRP_I0_ROOT_PROMOTED_AND_ROLLBACK_RETAINED` before leaving recovery.

## Gate 4 — normal boot and real, privileged Linux access

1. Only after promotion passed, reboot **normally to system** using the verified TWRP interface. The known-good p7 → p8 chain should pick up newly promoted Debian from p10. This is the **first physical boot test of this modified root**, not a proven result.
2. Surface should enumerate **COM10**. If a prior graphical serial-console program holds COM10, disconnect its Windows-side port without logging out of Linux; do not change tablet boot state.
3. Run prepared read-only acceptance probe (or equivalent interactive terminal):
   ```powershell
   python C:\Users\olsen\xoom-linux-rom\MZ604-COM10-I0-ACCEPTANCE-20261030.py
   ```
   Require actual `uid=1000(xoom)`, `uid=0(root)` from `sudo -n id`, kernel `7.0.0-next-20260422+`, and loop-backed Linux environment. A serial port, login prompt or echoed command alone is NOT privilege proof. If absent, stop; do not improvise an unattended reboot sequence.
4. With root privilege actually confirmed, capture `uname -a`, `/proc/mounts`, live `/lib/modules`, `journalctl -b`, `systemctl status serial-getty@ttyGS0` and physical console evidence (private logs, redacted source claims). Perform **one supervised normal Linux reboot**; prove a second full COM10 autologin + sudo reconnect. This completes I0 and the *normal reboot part* of I1, not recovery reboot.
5. If no authenticated Debian shell, owner can physically reenter existing TWRP. Independently verify the canonical new root SHA and preserved original SHA, safely move failed new canonical image to an unused name, restore `rootfs.before-I0-20261030.ext4` to `rootfs.ext4` without clobber, sync, and boot unchanged p7. If previous root is missing/changed, use independent Surface backup only after verified identity and SHA. Never delete the previous working image by assumption.

## Gates 5+ — separate tests, never combined into first I0

- **I1 Linux→TWRP reboot:** Only *after* authenticated Linux + normal reboot PASS and with owner physically near device. Investigate exact Tegra/Linux recovery-mode requests and then test the smallest supported command, verify TWRP ADB and return to normal Linux. If it fails, physical button reset is accepted. No bootloader/GPT writes, no watchdog automation.
- **I2 p8 one-shot root selector:** Optional V2 remains unbooted. Independently back up and hash actual live p8 before any modification. Compare exact current hotfix with candidate; test default path first under physical supervision, then one-shot alternate root/rescue and subsequent ordinary-boot fallback. Do not treat six static policy cases as execution of the ARM shell on hardware.
- **I4 alternative kernels:** kexec only optional after root/recovery switching is practical; validate same known-good kernel/DTB first and preserve persistent p7. Some failed kernels require physical restart. Do not replace bootloader or divert effort into automatic crash recovery.
- **W1–W6 upstream BCM4329:** Return to minimal **Wingray-first 2.4GHz** RFC. W1 actual upstream kernel/DTB + MZ604 SDIO F1/F2/firmware/MAC/regulatory baseline; W2 conditional legacy chanspec fallback only if physically measured; W3 real RF/regulatory restrictions; W4 three fresh ordinary scans; W5 WPA2/DHCP/DNS/data/reconnect/reboots; W6 smallest one-logical-defect-per-patch RFC under owner review/DCO. Historical MZ600 r7/V31 code is reference, not automatic transplant.

## Safety and documentation rules

A wrong model, unexpected partition, malformed getprop, missing /data, unusual rootfs SHA, insufficient headroom, failed host backup receipt, tool safety denial, existing stage/old-root file, bad gzip/raw SHA, unsupported BusyBox applet, failed verify, or missing COM10 privileged shell means **STOP, preserve evidence and report**. Every new agent must read ALL project logs chronologically and appreciate statements are true *as of their timestamp*. After every substantive turn append a short dated [project log](../../project-log/README.md) entry. After a physical I0/I1 milestone, also create a dated immutable checkpoint, update status/indexes and [MZ604 issue #18](https://github.com/Olsens11/XoomLinux7/issues/18), and prepare a comprehensive handoff. Never mark files staged as “installed” or lab mock as physical pass.
