# MZ600 v06.4 — actual firmware country-iovar control and OEM US/69 experiment: physical PASS, 5GHz STILL absent

**Date:** 2026-10-26. **Owner request:** continue after Motorola US/69 NVRAM file was proven insufficient; verify **on-chip effective country/revision**, not merely whether the configuration file contains those values. **Experimental board:** same MZ600 with Linux `7.0.0-next-20260422+`, internal Debian 12.15 p8 ext4. **Both live tests physically executed remotely on Xoom via Surface COM9.** No wireless scan, association, `iw reg set`, permanent kernel/module/firmware/NVRAM install, p7 modification or reboot.

## Read-only ABI-matched new kernel diagnostic

Built a distinct [read-only country iovar + existing band/chanspec diagnostic](../../scripts/experiments/build-v064-bcm4329-country-iovar-and-bandlist-diagnostic-20261026.py) against exact `v064-bigpart-linux`, `v064-bigpart-debian-sdroot-build`, `CONFIG_MODVERSIONS=y`, ARM GNU14.3. Original source and both original build outputs restored byte-for-byte. Resulting **342,136-byte** RAM-only `brcmfmac.ko` SHA256 **`fadd9d0242ddd693392a59c83725d184f2a325cdbe87d96b31a510776c6bb352`** and count-only patch SHA256 **`8fa5d1a3ac0ad80fe78f65eabd23e6964c4c07968363e632d54e44a97098639e`**. Exact `vermagic=7.0.0-next-20260422+ SMP mod_unload modversions ARMv7 p2v8`.

Instrumentation adds a single `brcmf_fil_iovar_data_get(ifp, "country", &diag_country, sizeof(diag_country))` after firmware band enumeration in `brcmf_setup_wiphy`. It logs return code, two bytes of country abbreviation and internal country code in hexadecimal and little-endian revision. **It never invokes firmware country-setting, regulatory overrides, power changes or RF scans**. Existing bandlist/chanspec logging retained.

File transferred from Desktop WSL through **existing authenticated Surface `devdesktop` SSH/SCP connection** with exactly matching SHA256 (no temporary firewall port or exception). The proven COM9 gzip/base64 transfer copied it **only into Xoom RAM** `/run/mz600-v064-countryread-diag-once.ko`, independent device SHA readback PASS. No permanent `/lib/modules` change.

## A. Normal calibration = firmware US revision 0

`NVRAM` exact 1550B SHA256 `a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb`; generic firmware 253748B SHA256 `d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93`.

[One-shot baseline test](../../scripts/host/xoom/test-v064-bcm4329-country-iovar-readonce-20261026.sh), SHA256 `14d28eb888cb410eeb5461501ca74c634aee61b31256e4801a85d9616d931676`, compiled/syntax verified, 99-line pinned wrapper over COM9:

```text
MZ600_COUNTRY_PREFLIGHT_PASS_IDENTICAL_BASELINE
MZ600_COUNTRY_WLAN0_PRESENT
MZ600_COUNTRY_DYNAMIC_PHY=5
MZ600_COUNTRY_PHY_5GHZ_FREQ_COUNT=0
MZ600_5G_DIAG_BANDLIST count=1 first=2 second=0
MZ600_5G_DIAG_WIPHY has2g=1 has5g=0
MZ600_5G_DIAG_COUNTRY_READ rc=0 abbrev=5553 ccode=5553 rev=0
MZ600_5G_DIAG_CHANSPECS total=11 2g=11 5g=0 other=0
MZ600_COUNTRY_UNLOAD_brcmfmac-wcc_RC=0
MZ600_COUNTRY_UNLOAD_brcmfmac_RC=0
MZ600_COUNTRY_UNLOAD_brcmutil_RC=0
MZ600_COUNTRY_ORIGINAL_FW_NVRAM_MODULES_AND_WLAN_RESTORED
MZ600_COUNTRY_READ_ONLY_DIAG_PASS_AND_CLEAN
HOST_DIAG_RESULT=FULL_PHYSICAL_PASS
```

Hex `5553` decodes ASCII **`US`**. Although NVRAM has no explicit `ccode` or `regrev`, the active generic firmware **already defaulted to US with revision 0**.

## B. Original OEM US/69 calibration-minus-bootstrap MAC = firmware US revision 69, **still no 5GHz**

[Second one-shot](../../scripts/host/xoom/test-v064-bcm4329-country-iovar-oem-us69-ram-20261026.sh), SHA256 `07aa4c2b609d2757f32a072fcb6252006ac0065f02dd59b40d79130363d72892`, 120-line pinned COM9 wrapper. Exact OEM original calibration without bootstrap MAC, 1569 B SHA256 `6de236d4d097f4996e1fef31d538757bfd9f4024cbcf2ade8bbaa97c040e53c4`, reconstructed from the **same 1550B base plus only `ccode=US` and `regrev=69`**. RAM **bind mounted before loading firmware**, with original current 4.220.48 `.bin`, factory-MAC handling, kernel, WCC, SDIO all unchanged. Actual results:

```text
MZ600_US69_EFFECT_BASELINE_SHA_PASS
MZ600_US69_EFFECT_CALIBRATION_RECONSTRUCTION_SHA_PASS
MZ600_US69_EFFECT_OEM_COUNTRY_REV_IN_RAM_AT_FW_BOOT
MZ600_US69_EFFECT_WLAN0_PRESENT
MZ600_US69_EFFECT_DYNAMIC_PHY=6
MZ600_US69_EFFECT_PHY_5GHZ_FREQ_COUNT=0
MZ600_5G_DIAG_BANDLIST count=1 first=2 second=0
MZ600_5G_DIAG_WIPHY has2g=1 has5g=0
MZ600_5G_DIAG_COUNTRY_READ rc=0 abbrev=5553 ccode=5553 rev=69
MZ600_5G_DIAG_CHANSPECS total=11 2g=11 5g=0 other=0
MZ600_US69_EFFECT_UNLOAD_brcmfmac-wcc_RC=0
MZ600_US69_EFFECT_UNLOAD_brcmfmac_RC=0
MZ600_US69_EFFECT_UNLOAD_brcmutil_RC=0
MZ600_US69_EFFECT_UNMOUNT_RC=0
MZ600_US69_EFFECT_ORIGINAL_FILES_AND_RADIO_RESTORED
MZ600_US69_EFFECT_READBACK_A_B_PHYSICAL_PASS_CLEAN
HOST_DIAG_RESULT=FULL_PHYSICAL_PASS
```

This test **now confirms the firmware effectively adopted Motorola's `US/69`** (versus `US/0` control), yet it still returned a single 2GHz band and eleven 2GHz chanspecs, **ZERO 5GHz**. This is stronger than [prior owner-pasted US69 experiment](MZ600_V064_OEM_US69_BOOTSTRAP_NVRAM_A_B_PHY5GHZ_UNCHANGED_OWNER_PHYSICAL_2026-10-26.md), whose country acceptance was unknown. **OEM country/regrev alone is definitively insufficient to restore 5GHz with currently running generic firmware/driver/board initialization.**

## C. Independent third read-only post-test state verification

A new COM9 root readback **after** both test scripts independently confirmed:
- Kernel `7.0.0-next-20260422+`, internal Debian `/dev/mmcblk0p8 ext4`, root terminal responsive.
- Network interfaces only `ip6tnl0`, `lo`, `sit0`; no `wlan0`; no Broadcom module loaded.
- Current NVRAM bind overlay **absent**, restored full 1550B original SHA `a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb`.
- Installed generic `.bin` SHA `d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93` and original installed `brcmfmac.ko` SHA `9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb`.
- `dbus.socket`, `dbus.service` both **active**. No reboot or permanent changes. Prior physical raw p7 SHA remains known; it was not independently re-hashed after these tests (there were no p7 writes).

## OEM cross-layer significance and next safe direction

Matching original Motorola 2a65edc DHD source has an **additional `WLC_SET_COUNTRY` execution path** in `dhd_common.c` when a host `dhd->country_code` has been set, alongside original firmware NVRAM `US/69`. Modern `brcmfmac` `cfg80211.c` country regulatory notifier uses `brcmf_fil_iovar_data_get/set(ifp,"country",...)`, but explicitly ignores an initial request for `00`. This proves at least two *distinct code paths* for country behavior; it **does not** justify forcing regulatory overrides. We have now proved **US/69 is actually honored by the current firmware on load but still exposes zero 5GHz channels**. Avoid repeat of the same country/rev-only experiment; OEM post-init `WLC_SET_COUNTRY` remains to be understood, but no evidence it is needed once effective iovar already US/69.

**Primary next discriminator:** original Motorola HRI39/HRI66 **4.218.248.20**, 261317 B SHA `7afdc1b85313bcc6054e01bd22aa4540a47cf6f42903b4f9728a1236b955251a`, versus generic **4.220.48** and their expected NVRAM, bootstrap factory identity, BCMDHD protocol and board initialization. Before a stock FW RAM A/B, privately inspect calibration/bootstrapping MAC behavior and current `brcmfmac-wcc` factory-MAC injection. **Never substitute stock MAC on multiple devices, enable synthetic PHY channels, or assume stock FW will work with upstream brcmfmac**. OEM shared U4/BT power, six-field SDIO quirk, PMU and ChipCommon source differences remain separate qualified investigation tracks; complete upstream patch series still unsubmitted with mandatory multi-device gates.

**Status:** exact firmware country acceptance confirmed for `US/0` vs `US/69`, successful safe teardown; 5GHz not yet fixed.
