# MZ600 OEM May 2012 firmware country readback: US/US/rev0 with both WLAN bands — physical RAM-only PASS, independently restored (2026-10-29)

**Physical result:** Motorola OEM May25 2012 BCM4329 firmware `4.218.248.44` initialized with the Xoom's **unchanged, installed** 1550-byte generic NVRAM and directly returned firmware `country` **`err=0 abbrev=US ccode=US regrev=0`**. At the same time, a read-only `iw phy` listed both 2.4 GHz and 5 GHz channel templates, without any scan or regulatory write. Prior control [generic firmware 4.220.48 country readback](MZ600_COUNTRY_IOVAR_US_REV0_PHYSICAL_ROLLBACK_PASS_2026-10-29.md) with the **same NVRAM** also returned **US/US/rev0** but advertises only 2.4 GHz. This is a strong same-board, same-calibration **firmware-dependent band advertisement** result: US/69 is not necessary for OEM2012 to expose 5 GHz, and the generic missing band cannot simply be attributed to US/0.

**Scope:** One-use owner-approved COM9 trial, brief interruption of Wi-Fi with explicit automatic rollback and separate independent postflight. Original nine-review Linux kernel and modules unchanged on disk; no reboot/flash; no NVRAM, country, TX power or firmware settings written; no RF scan or association performed. This is NOT legal RF permission nor proof of production 5 GHz association/repeat-scan reliability, and WIFI-01 issue #4 remains OPEN.

## Control inputs and proof of identity

- Replacement Xoom **MZ600**, Surface Book 2 exclusive USB serial COM9, authenticated root. Running Linux `7.0.0-next-20260422+`, `/dev/mmcblk0p10 ext4`, original nine-review brcmfmac system; connected NetworkManager+wpa_supplicant, Bluetooth inactive/HCI DOWN.
- **Original generic firmware** installed SHA256 `d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93` (`4.220.48`), original installed NVRAM `a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb` (1550 bytes; `ccode`/`regrev` omitted), original installed `brcmfmac.ko` SHA `5e767d47017ff9028e6c364f8325420b0fc79efd1c1e07d36595fb4fd0540d26`, original WCC SHA `eb9aa7efc8d9e356088aa9693cf1937c8c7e1a65dcd0193618915521b7a048b9`.
- **Only test-variable firmware:** archived May 2012 Motorola `4.218.248.44`, private 264140-byte binary SHA256 **`5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834`**. Tested previously with real dual-band and 35 current valid channels, with the same installed NVRAM. Proprietary firmware retained privately; do not commit.
- **Read-only lab module:** previously validated exact original-nine `brcmfmac` country-iovar instrumentation, 342864-byte module SHA256 **`e542bdbd5bb25167a15138d977df2e68d93db9fb509c0f23526bfad19b368424`**, core imports 259/259 matching, WCC imports 7/7. The original WIFI-01 fallback in this build handles older `chanspecs` firmware; no new production patch. The diagnostic only calls `brcmf_fil_iovar_data_get(ifp,"country",...)` after bands are prepared.
- Fresh, unused one-shot test `E`; both host files hash verified on Surface. Serial transfer reused established tested COM9 gzip/base64 SHA ACK protocol; both independently verified on device at `/run/mz600-country-e-oem2012-fw.bin` and `/run/mz600-country-e-lab-core.ko`. Staging alone did not load or replace the Wi-Fi stack.
- Private receipts: Surface `C:\Users\olsen\xoom-linux-rom\captures\MZ600-COUNTRY-OEM2012-20261029-E\owner.py`, `owner-once.sh`, `country-E-private.txt`, `country-E-receipt.json`, `independent-postflight-private.txt`. No private MAC, SSID, device serial, full proprietary firmware or raw console logs published.

## Physical execution and actual results

The preflight used **short serial commands** (reliable after Oct29 long-command COM9 timeout), checking root, exact kernel/p10 ext4, original wlan0 `100 (connected)`, active WPA/NM, inactive Bluetooth/HCI, absence of firmware/module overlays, exact four original SHA values, both staged RAM SHA/size values, and unconsumed one-shot E marker. All PASS. Remote `bash -n` validated test script before arming.

One-use script stopped NM/WPA, brought wlan0 down, unloaded original WCC/core/util, **RAM bind-mounted only OEM2012 firmware over the installed .bin path** (hash checked) and left the installed NVRAM unmodified, then loaded the matched read-only core and WCC. `wlan0` appeared with this firmware; the script inserted a fresh kernel-log marker before driver init and looked only after that marker, excluding previous generic-country observations.

Actual private log summary, identity-safe:

```text
MZ600_COUNTRY_E_BASELINE_EXACT_HASH_PASS
MZ600_COUNTRY_E_OEM2012_FIRMWARE_OVERLAY_SHA_PASS_NVRAM_UNCHANGED
MZ600_COUNTRY_E_LAB_CORE_WLAN0_PRESENT_NO_SCAN
MZ600_COUNTRY_E_NEW_COUNTRY_LINES=1
MZ600_COUNTRY_E_COUNTRY_RESULT=err=0 abbrev=US ccode=US regrev=0
MZ600_COUNTRY_E_BAND24_CHANNEL_COUNT=14
MZ600_COUNTRY_E_BAND5_CHANNEL_COUNT=29
MZ600_COUNTRY_E_READ_ONLY_COUNTRY_CAPTURED_NO_RF_SCAN
```

The two count values are **counts of `iw phy`-listed channel templates**, including any disabled channels, **NOT a firmware `GET_VALID_CHANNELS` count** and not legal operating permissions. The original OEM2012 **35-current-valid-channel result** is from the earlier [native six-format metadata physical test](MZ600_WIFI01_BCME_SIXFORMAT_NATIVE_UNSUPPORTED_PHYSICAL_PASS_2026-10-29.md), not a new scan or per-channel permission measurement in trial E. In this trial we did **not** set country/rev, force DFS/passive flags, query/radiate on a 5GHz channel, scan, associate, or change any calibration.

## Automatic cleanup plus independent, separate postflight

The script exited `rc=0` and its EXIT cleanup successfully unloaded test modules, unmounted the OEM firmware RAM overlay (`OEM_FIRMWARE_UNMOUNT_RC=0`), verified all four unchanged installed file hashes, restarted `brcmutil/brcmfmac/brcmfmac-wcc/wpa_supplicant/NetworkManager` (every rc=0), observed wlan0 `100 (connected)`, removed **both** RAM-staged input files and printed `FINAL_ORIGINAL_RUNTIME_RESTORED initial_rc=0`.

A **separate Python process** independently reopened COM9 and verified root, p10 ext4, exact original firmware/NVRAM/core/WCC hashes, all three original Broadcom modules loaded, connected original WLAN and active NM/WPA, no firmware or module bind overlays, RAM staging removed, and one-use E marker consumed. **Independent postflight PASS, COM9 released.**

No persistent files, firmware, NVRAM, dtb, kernel boot image, p7, p8 or p10 boot configuration were modified.

## What this decides (and what it does NOT)

- **Supported finding:** under the same board and exact same installed NVRAM, two firmware images both report **US/US/rev0**, but only **OEM 4.218.248.44** exposes 5GHz. Thus `regrev=69` is **not a prerequisite for OEM firmware to enumerate 5GHz** under these test conditions; and `US/0` alone does **not** explain the generic one-band defect. Firmware compatibility is the strongest observed differentiator.
- **Previously established independent A/B:** the [Oct26 OEM-US69-only NVRAM overlay](MZ600_V064_OEM_US69_BOOTSTRAP_NVRAM_A_B_PHY5GHZ_UNCHANGED_OWNER_PHYSICAL_2026-10-26.md) while retaining generic `4.220.48` **still** had only the 2.4GHz band. Do **not** rerun that old experiment as if rev69 is untested.
- **Regulatory caveat:** 5GHz band templates/firmware channel-list membership do not establish DFS, per-channel passive/NO_IR or transmit rights. The OEM2012 firmware did not support any of six documented `per_chan_info` encodings (native `BCME_UNSUPPORTED=-23`) in prior physical trials. Linux signed regulatory rules, firmware restrictions, and hardware calibration must remain effective; no synthetic restrictions or permissive fake metadata.
- **Country-translation interface:** original Motorola dynamic region map and upstream `brcm,ccode-map` remain the proper mechanism if later needed for a verified board/SKU and legitimate country transitions. The immediate missing-Band-2 objective should **not** be approached by forcing US69, adding a global trivial-code fallback, or altering `brcmfmac` regulatory notifier without new causal evidence.
- **Engineering next gate:** focus on making the **OEM2012 firmware compatibility path** upstream-clean: refine the existing WIFI-01 legacy `GET_VALID_CHANNELS` fallback, handle native unsupported firmware metadata without treating all normalized `-EBADE` alike, and correctly intersect cfg80211/regdb country restrictions without prematurely freezing a country-dependent channel list or permanently applying experimental blanket 5GHz NO_IR. Keep WIFI-02/03/04 ESCAN completion/readiness work separate. Validate source and offline fixtures first; physical RF operations require the standard specifically authorized, bounded, rollback-protected gate.

**Canonical project state:** original installed exact-nine Linux7 2.4GHz Wi-Fi connected; all test overlays gone; module/firmware/calibration hashes pristine; one-use E consumed. WIFI-01 r3 still unsigned, unaccepted and not loaded permanently; no signoff or upstream submission.
