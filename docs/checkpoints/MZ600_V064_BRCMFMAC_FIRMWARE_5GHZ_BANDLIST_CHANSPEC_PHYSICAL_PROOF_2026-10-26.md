# MZ600 Linux 7 v06.4 — firmware bandlist and chanspec: physical root-cause boundary PROVED

**Physical date:** 2026-10-26. **Target:** experimental replacement Motorola Xoom MZ600, Debian 12.15 armhf on internal p8 ext4, Linux `7.0.0-next-20260422+`; Surface USB serial COM9 authenticated root. **Result:** The *firmware itself* advertises one 2.4 GHz band and exactly 11 2.4 GHz channel specifications. No 5 GHz band/chanspec is supplied to the generic Linux driver. This is a **software/firmware initialization boundary**, not yet a proven individual defective firmware/NVRAM parameter or a completed 5 GHz fix. Owner independently recalls Android negotiated **5 GHz Wi-Fi on the identical physical radio/board**.

## Previous evidence and goal

- Native Debian/p8 `brcmfmac` and WCC PHY `wlan0` physically scanned 19 BSS at 2.4 GHz and cleanly unloaded; known-good boot, TWRP and user data preserved.
- A separate 5 GHz PHY diagnostic discovered dynamic `phy2` but **zero** PHY channels between 5000–6000 MHz, so 5 GHz scan was intentionally skipped. Legacy fixed-name `phy0` bug was diagnosed in lab test harness and corrected.
- Existing private NVRAM has `aa2g=1`, `aa5g=1`, historical 5 GHz PA-related `pa1b0/1/2` calibration and `xtalfreq=38400`. These do not alone prove which band is enabled by *active* firmware.
- Pinned upstream kernel `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`: `brcmf_setup_wiphy()` in `brcmfmac/cfg80211.c` calls `BRCMF_C_GET_BANDLIST` and allocates a 5 GHz `wiphy` band **only if** the firmware reports `WLC_BAND_5G`. `brcmf_construct_chaninfo()` decodes `chanspecs` firmware iovar afterwards.
- User explicitly authorized a **read-only diagnostic patch and physical test**; avoid forced channels, MAC/regulatory overrides, network association and reboot.

## Count-only kernel lab patch and ABI-exact reproducible build

Canonical WIP GitHub branch `wip/clean-wifi-bt-usb-20261025` files:

1. [Lab diagnostic patch](../../patches/lab/0002-brcmfmac-log-firmware-bandlist-and-chanspec-band-counts.patch) SHA256 **`b70b1104f5fb1f32b780997e92507ffda644d483fa89c3336d7c910b5063c93a`**. A separate non-functional kernel patch on generic `brcmfmac/cfg80211.c`, not part of the proposed upstream/pwrseq patch series.
2. [One-shot builder](../../scripts/experiments/build-v064-bcm4329-5ghz-bandlist-diagnostic-20261026.py), source `v064-bigpart-linux`, ABI-matched module build `v064-bigpart-debian-sdroot-build`, ARM GNU 14.3 cross toolchain, `CONFIG_MODVERSIONS=y`, `CONFIG_BRCMFMAC=m`; `vermagic=7.0.0-next-20260422+ SMP mod_unload modversions ARMv7 p2v8`.
3. [Live bounded RAM-only test](../../scripts/host/xoom/test-v064-bcm4329-firmware-bandlist-diag-once-20261026.sh) SHA256 **`7668a065da00358303b84c192caa5e40e58c75db1973f5d66fce1ea3b1740f33`**; no persistent module install, scan, reboot or network config.

Patch `git apply --check` passes on the exact source tree. Instrumentation prints **firmware band count/enum** in `brcmf_setup_wiphy()`, firmware `chanspecs` total and decoded 2G/5G/other counts in `brcmf_construct_chaninfo()`, and allocated wiphy band booleans. No raw MAC, BSSID, SSID, network password, firmware payload, regulatory domain modification or RF settings in these messages.

First offline builder attempt correctly compiled but assumed the `M=` module artifact resided in the `O=` directory; actual kernel build emitted it in the **source-tree brcmfmac directory**. The builder rejected the unchanged original output despite build return code 0. The actual diagnostic source-tree `.ko` was recovered and SHA/ELF/markers validated separately; the known-good output tree module stayed unchanged.

**The builder was corrected and independently rerun** in a fresh `v064-5ghz-bandlist-diagnostic-v2-20261026` output area, which produced the **identical exact module SHA256** and restored both the source-tree `.ko` and the distinct original build-output `.ko` to their baseline SHA on exit. Physical boot image remained untouched throughout.

- Native original baseline module `brcmfmac.ko`: 341,676 bytes; SHA256 **`9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb`**.
- Read-only diagnostic `brcmfmac.ko`: 341,760 bytes; SHA256 **`1d38b1446a631c8d9ceaa82edb5b981b53288410a2d7bc88d0dc00f24c8e5444`**.
- The new diagnostic `.ko` was checked with `readelf -p .modinfo` for correct vermagic and three `MZ600_5G_DIAG_*` literal markers; module version checks verified.
- Build artifacts are private Desktop WSL files. Do NOT commit a binary artifact or Motorola proprietary firmware payload to public GitHub.

## Transport: existing permanent firewall setup rediscovered and temporary workaround closed

Owner reminded us that desktop-to-Surface firewall access was already solved permanently. Confirmed in live Windows firewall, **enabled inbound** rule **`Xoom image transfer - Surface only TCP 43157`** on Desktop `192.168.0.125`, **LocalPort TCP 43157, RemoteAddress `192.168.0.40`** (Surface); separate authenticated `devdesktop` SSH/SCP flow is also documented in prior handoffs. Future module transfers should **reuse existing validated port 43157 or SSH/SCP**, rather than creating ad hoc exceptions.

This run initially tried a one-time HTTP port 8877 on the Desktop; Surface timed out due to Public-profile inbound firewall. An **explicit temporary rule** restricted to `192.168.0.40` was used only to transfer this one SHA-pinned diagnostic module. Desktop-to-Surface file SHA validated byte-for-byte. **Temporary TCP 8877 firewall rule removed and its one-file Python HTTP server terminated**, both independently confirmed absent. Original permanent 43157 rule was not removed or changed.

This is a tooling-process finding; it did **not** affect the Xoom radio or kernel. Subsequent transfers should use the existing permanent solution.

## RAM-only transfer and physical Xoom run

Verified module transferred via COM9 as gzip+base64 framed 1024-character lines (185 frames) to **`/run/mz600-v064-bandlist-diag-once.ko`** with 16-line serial acknowledgments; size and **SHA256 verified independently on Xoom**. Sender exit 0. This **did not install** it to `/lib/modules`, and the original normal-driver module remained unchanged.

The exact SHA-pinned test wrapper was loaded into Xoom root terminal once, with UID0, exact kernel release and internal p8 read-only preflight PASS. The test then loaded regular `brcmutil`, `insmod` of the diagnostic `brcmfmac` from RAM, and the standard WCC module. It required the normal firmware+NVRAM image (generic `4.220.48` already 2.4 GHz PASS), detected `wlan0`, queried dynamic `phy3`, and did **not** start a scan or bring the link UP.

**Actual native kernel messages (the critical new evidence):**

```text
brcmfmac: brcmf_setup_wiphy: MZ600_5G_DIAG_BANDLIST count=1 first=2 second=0
brcmfmac: brcmf_setup_wiphy: MZ600_5G_DIAG_WIPHY has2g=1 has5g=0
brcmfmac: brcmf_construct_chaninfo: MZ600_5G_DIAG_CHANSPECS total=11 2g=11 5g=0 other=0
MZ600_5G_FW_DIAG_WLAN0_PRESENT
MZ600_5G_FW_DIAG_WIPHY_INDEX=3
MZ600_5G_FW_DIAG_ADVERTISED_5G_CHANNELS=0
```

`WLC_BAND_2G=2` in pinned kernel source. The **first band enum=2** means firmware explicitly reports 2 GHz band. Its **`count=1`** means exactly one band; `second=0` in our count-only diagnostic is the default printed for an absent second band, **not** a second returned enum. Channel list decodes 11 2 GHz specs and zero 5 GHz specs.

This is **stronger than the earlier regulatory/PHY symptom**: the firmware returned **no 5 GHz band or channel spec to the driver**. A patched kernel that simply allocates the 5 GHz band despite this would misrepresent what firmware allows and is **not a valid solution**. We have **not yet proven** why firmware does this: possible incompatible firmware image, 5 GHz front-end/board calibration, country/regrev/OTP or initial radio configuration. Android previously used 5 GHz on same board; compare known-good OEM stack carefully.

**Exit teardown and postconditions:**

```text
MZ600_5G_FW_DIAG_EXACT_RAM_MODULE_INSERT_RC0
MZ600_5G_FW_DIAG_WCC_MODULE_LOAD_RC0
MZ600_5G_FW_DIAG_LINK_DOWN_RC=0
MZ600_5G_FW_DIAG_UNLOAD_brcmfmac-wcc_RC=0
MZ600_5G_FW_DIAG_UNLOAD_brcmfmac_RC=0
MZ600_5G_FW_DIAG_UNLOAD_brcmutil_RC=0
MZ600_5G_FW_DIAG_DRIVER_TEARDOWN_VERIFIED
MZ600_5G_FW_DIAG_RESULTS_CAPTURED_AND_CLEANED
HOST_DIAG_RESULT=FULL_PHYSICAL_PASS
```

Separate **independent COM9 post-test read-only audit** (not just wrapper's declared cleanup) showed:
- Still authenticated UID0, Linux `7.0.0-next-20260422+`, root `/dev/mmcblk0p8 ext4`, COM9 responsive.
- `/sys/class/net`: `ip6tnl0 lo sit0`; `wlan0` absent, **no brcm modules in `/proc/modules`**.
- Original installed `brcmfmac.ko` SHA `9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb` unchanged.
- Full physical p7 `/dev/mmcblk0p7` SHA `901c79cfbeb646dad7f41d6de9d8605029d3fe082231ab7032cdba8cc7c0ff5c` unchanged; p8 UUID `c2fb0167-7143-4186-b284-c86d6c09ea64` unchanged.
- `dbus.socket` and `dbus.service` both **active**. No reboot or RF scan.

**Final outcome: physical 5 GHz firmware enumeration diagnostic SUCCESS; 5 GHz actual Wi-Fi still NOT FIXED.**

## Next minimum experiments — don't skip source verification

1. **OEM-vs-current private NVRAM and Wi-Fi firmware audit:** verified original Motorola HRI39 firmware `4.218.248.20` (261,317 bytes, SHA `7afdc1b85313bcc6054e01bd22aa4540a47cf6f42903b4f9728a1236b955251a`) vs currently working Debian generic `4.220.48` (253,748 bytes, SHA `d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93`). Diff `aa5g`, boardflags/boardtype/boardrev, band/power data and country/revision treatment **without publishing unique serials/MAC/OTP or proprietary binary**. Vendor firmware bundle may use different NVRAM encoding; verify exactly what device loads. Android 5 GHz experience is historical hardware evidence, not proof today's exact generic firmware is capable of 5 GHz.
2. Inspect firmware startup country/regrev path and board identity; test exact OEM candidate **only in isolated RAM/temporary context, one variable at a time**, with rollback, provenance/license awareness and comparison to proven 2.4 GHz baseline. Do not arbitrarily set regulatory country, force `aa5g`, inject blank calibration, or enable channels against the firmware answer.
3. If OEM firmware still reports a single 2 GHz band, add separate count-only diagnostics of **firmware NVRAM interpretation, OTP, variant board calibration, band selection and firmware regulatory iovars**, not shared power sequencing ungroundedly.
4. Keep the **whole-chip BCM4329 PMU/U4/I7/U0/U2/LPO provider** patch track separate and maintain the user's [multi-device qualification](../plans/MZ600_BCM4329_LINUX7_MULTIDEVICE_PATCH_SERIES_RELEASE_GATES_2026-10-26.md) before own-use rollout and later upstream submission. Do not claim success across MZ602/MZ604 or that vendor 5GHz hardware can be forced on other variants.
5. Document the firmware answer in the [whole-chip ledger](../research/MZ600_BCM4329_LINUX7_WHOLE_CHIP_PATCH_INTEGRATION_LEDGER_2026-10-26.md), handoff, status and runtime env; do **not** repeat the diagnostic unless comparing a specific changed condition.

**Status:** 5 GHz firmware missing band/chanspec **PHYSICAL PROOF**, preserved normal Debian 2.4 GHz and ABI; diagnostic lab patch and reproducible offline build ready for next A/B. No source/firmware/regulatory root-cause patch yet.
