# Motorola Xoom MZ600 — guarded provisional V31 persistence

**Status 2026-10-27:** The exact V31 lab module passed **two genuine consecutive multichannel scans** (17 and 23 BSS) using a temporary RAM firmware/WCC overlay, as documented in [V31 physical checkpoint](../../../docs/checkpoints/MZ600_V31_CONDITIONAL_WLC_UP_TWO_REAL_ESCANS_PHYSICAL_PASS_2026-10-27.md). **Persistent p8 installation has NOT yet run or been validated.** The separate [WIFI-4 review draft](../../../patches/upstream/review-drafts/WIFI-4-brcmfmac-bcm4329-resume-firmware-for-escan.patch) passes standalone ARM compilation; the [full WIFI1–4 integrated lab source](../../forensics/build_wifi4_with_legacy_scan_snapshot_once.py) passes offline compilation but still includes older experimental logging/knobs and is NOT an upstream-ready series.

## Objective and boundaries

The immediate requirement is to preserve BCM4329 V31 scan behavior over module reload and reboot, then test a real WPA connection. The target access-point name and any password are **private operational data**, not part of the public GitHub patches, handoff, or firmware. V31 preserves default MPC power-saving after scans and performs `WLC_UP` only when the firmware reports DOWN immediately before another scan. This deployment is temporary/provisional in **source quality** but persistent on the Linux p8 filesystem. It will eventually be superseded by the logically split, reviewed source patch series.

Only change these existing p8 files **after an exact SHA preflight and full backup**:

- `/lib/modules/7.0.0-next-20260422+/kernel/drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko`
- matching `.../brcmfmac/wcc/brcmfmac-wcc.ko`
- `/lib/firmware/brcm/brcmfmac4329-sdio.bin` — a user-owned Motorola 2012 candidate already tested in RAM (private)
- new `/etc/modprobe.d/xoom-bcm4329-v31-lab.conf` configuring the experiment's necessary Event69 owner and generation defaults

**Do not touch the kernel p7, root partitions/GPT, DTS, NVRAM `.txt`, MAC address, Bluetooth, country settings, or current Debian boot image.** No firmware files/identifiers are pushed to public GitHub.

## Inputs and immutable hashes

| Artifact | SHA256 | Bytes |
| --- | --- | ---: |
| Original installed `brcmfmac.ko` | `9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb` | Verified at runtime |
| Original installed WCC | `31475d34c94ee4b480fb295032dad84d86eeb81854cb2a140d1f39430f13ff80` | 5916 |
| Original installed firmware | `d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93` | Verified at runtime |
| Original device NVRAM | `a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb` | Never modified |
| Physically tested **V31** `brcmfmac.ko` | `c82bd4e25ba1d96a01136407b200fe8c5431c7c89856e420dac4a81580183dc8` | 354392 |
| Matching V31 WCC | `6d3ab647684e6e9fef37caa14ea539bc25f1458f4472d7d0e376a782b364115d` | 5892 |
| Private Motorola 2012 candidate firmware | `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834` | 264140 |

## 1. On Surface Book 2 — stage via proven COM9 protocol

Close the interactive terminal owning COM9. The Surface already contains the exactly verified V31 private artifacts under its `MZ600-V31-CONDITIONAL-UP-20261027` captures folder. No Desktop port43157 server is required.

Download the one-shot `prepare-v31-on-surface.ps1` from this directory using its pinned GitHub commit and run it locally. It downloads and independently SHA-verifies [installer](install-v31-provisional.sh), [recovery script](restore-before-v31.sh) and [COM9 staging helper](stage-v31-from-surface.py); then after typing **STAGE**, transfers the three files from the existing Surface captures to RAM over the **original V31 gzip/base64 ACK COM9 transport**. It also transfers both scripts, performs an on-device **read-only preflight** and leaves files under `/run/xoom-v31-install`. If it prints anything other than `V31_INSTALL_DRY_RUN_PASS`, stop and preserve the stage. **The one-shot does not install anything persistently or send a Wi-Fi scan.**

## 2. On the Xoom COM9 root terminal — install after successful dry-run

Reconnect the terminal, review the staged source and run the explicit install only when all SHA checks pass:

```bash
bash /run/xoom-v31-install/install-v31-provisional.sh --check
bash /run/xoom-v31-install/install-v31-provisional.sh --apply
```

The installer requires exact Linux ABI, `/dev/mmcblk0p8 ext4`, original module/firmware/NVRAM hashes, no bind mounts or active Wi-Fi carrier, non-active Bluetooth, and a matching set of RAM-staged artifacts. It creates `/var/lib/xoomlinux7/backup-v31-before-install` with four verified originals **before unloading** the Wi-Fi driver. It replaces the three payloads, writes the lab-specific `modprobe.d` options and runs `depmod`, then loads core and WCC and verifies generation/owner parameters. On failure after replacement starts, it attempts immediate file rollback and prints whether those files were restored; keep COM9 open and independently inspect the state. On any preflight failure, do not force or bypass the safety checks.

The exact new installation is **not** yet a physically verified integrated production build; it is the same original V31 experimental module that previously passed scanning. A later switch to the clean source series must repeat matching ABI/CRC, functional tests and snapshot rollback.

## 3. Postinstall tests (separate from installation)

After `V31_PROVISIONAL_P8_INSTALL_PASS`, verify module hashes and scan an appropriate normal regulatory-permitted 5 GHz band; do not override regulatory rules. Then use the existing private `wpa_supplicant`/COM9 session for association/authentication. `systemd-networkd` is available to provide DHCP but has not yet been configured or activated. Avoid printing private WPA credentials to logs or public repositories.

A reboot-persistence check and connection/traffic/BT coexistence testing are still open. Do not report them PASS until run.

## Rollback

After a successful install, the owner-run [restoration script](restore-before-v31.sh) is stored under `/var/lib/xoomlinux7/backup-v31-before-install/restore-v31.sh`. From COM9 with Wi-Fi disconnected:

```bash
bash /var/lib/xoomlinux7/backup-v31-before-install/restore-v31.sh
bash /var/lib/xoomlinux7/backup-v31-before-install/restore-v31.sh --restore
```

It checks original backup hashes and installed exact V31 hashes before unloading/replacing any file, restores the original firmware and matched modules, removes only its specific lab options file, reloads the original driver and verifies hashes. It deliberately preserves the backup directory. If the installed hashes no longer match the exact V31 revision, stop rather than rolling back over unrelated changes.

**Patch-series provenance:** [G01–G12 requirements](../../../patches/upstream/candidate/SUBMISSION_REQUIREMENTS.md). This deployment's shell scripts and binary outputs are **not** kernel submission patches; keep the clean WIFI-4 draft revised in place within the logical Wi-Fi series.
