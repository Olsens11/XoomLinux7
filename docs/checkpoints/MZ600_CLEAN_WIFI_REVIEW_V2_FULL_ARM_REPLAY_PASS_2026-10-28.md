# MZ600 Linux 7 — clean BCM4329 review v2 and six-part full ARM source replay PASS

**UTC date:** 2026-10-28. **Base:** pinned `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`. **No Xoom boot, eMMC, private firmware, NVRAM or network services were changed.** All work below was performed on an isolated desktop WSL ARM cross-compile environment.

## Engineering decision

Preserve V31's independently proved physical network functionality (repeat real Event69 ESCAN, conditional WLC_UP after MPC idle-down, WPA2-PSK/CCMP, DHCP4, DNS, NTP and certificate-verified HTTPS) as the target benchmark, but **never equate the exact V31 laboratory module with the cleaned source review series**. Connection still took approximately 399 seconds after the successful first reboot, with eight WPA authentication timeouts and unusual Event0/Event16 invalid `bsscfg` indices. Connection-event parsing/quick reconnect is a **separate unresolved logical issue**, not a reason to contaminate the first three Wi-Fi patches.

The former `candidate/0004` patch contained ~680 lines of mixed fallback, scan owner routing, generation validation and instrumentation; kept frozen as a reproducibility snapshot and **NOT used as a review-series predecessor**.

## New logical patch series

Directory: [unsigned clean Wi-Fi RFC v2](../../patches/upstream/review-wifi-v2-20261028/README.md).

| Ordered member | Scope | Strict checkpatch |
| --- | --- | --- |
| `0001-wifi-brcmfmac-use-legacy-channel-list-on-BCM4329.patch` | BCM4329-only bounded `WLC_GET_VALID_CHANNELS` fallback when firmware lacks `chanspecs`; flags only narrowed | 0 errors / 0 warnings / 0 checks |
| `0002-wifi-brcmfmac-match-BCM4329-ESCAN-completion-to-acti.patch` | Active 16-bit generation + genuine 12-byte terminal Event69 owner attribution; keep as one lifetime change, never remap unrelated events | 0 / 0 / 0 |
| `0003-wifi-brcmfmac-restore-BCM4329-firmware-readiness-for.patch` | Scoped conditional `WLC_GET_UP`/`WLC_UP` before ESCAN after normal MPC0; preserve MPC1 | 0 / 0 / 0 |

No `MZ600_Vxx` lab instrumentation, module test switches, forced regulatory/channel settings or private identifiers in these source patches. Commit authorship is a clearly unauthenticated RFC placeholder (`rfc-draft@invalid.example`); includes `Assisted-by: ChatGPT:GPT-6 [Desktop Commander]`, **no AI-created Signed-off-by, no fabricated Reviewed-by or Tested-by**, no upstream posting. A human must review license/source attribution and certify DCO before submission.

## Exact clean replay and cross-build evidence

**Isolation:** local upstream source with uncommitted work left untouched; created new worktree `/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/v064-full-review-v2-20261028` at pinned upstream commit, then applied frozen `candidate/0001` Stingray DTS, `candidate/0002` Motorola MAC ATAG, `candidate/0003` BigPart snapshot, committed as separate explicit RFC integration revisions, followed by three **exact v2 Wi-Fi review patches via `git am`**. Each apply/prefix `git diff --check` passed; tip `93b926b26ec1f2cee9ab7050f21aada982f58eba`.

Fresh build output directory: `.../v064-full-review-v2-build-20261028`, seeded ONLY with known V064 matching `.config` then `make olddefconfig` and `make -j8 zImage dtbs modules` (ARM cross-toolchain `arm-gnu-toolchain-14.3.rel1`). No precompiled object files copied. **Exit code 0; wall time 542.25 seconds**. Kernel release `7.0.0-next-20260422+`. Five compiler warnings all from unmodified `drivers/gpu/drm/bridge/sii9234.c` (unused functions); no Broadcom build warnings.

| Build artifact | Size | SHA-256 |
| --- | ---: | --- |
| ARM `arch/arm/boot/zImage` | 5,826,832 | `5f42ae44441a051ff6811d5737fe6a86d2b8d2330a8278997b78c4571dd816ae` |
| `tegra20-motorola-stingray.dtb` | 61,110 | `1daba0e41071f373f0e0ac76a1e616c5b50354565afa0845efffedb9c8859f48` |
| `brcmfmac.ko` | 343,016 | `5e767d47017ff9028e6c364f8325420b0fc79efd1c1e07d36595fb4fd0540d26` |
| `brcmfmac-wcc.ko` | 5,916 | `eb9aa7efc8d9e356088aa9693cf1937c8c7e1a65dcd0193618915521b7a048b9` |
| `Module.symvers` | 844,612 | `6e3befe529cfa57cda6c788e1d9d387537ee8a246327dc09a6297e608fad5069` |

Both matched Broadcom modules have **identical `modinfo` vermagic** `7.0.0-next-20260422+ SMP mod_unload modversions ARMv7 p2v8`; core is ARM 32-bit little-endian ELF relocatable, EABI v5. Exact machine-readable results: [build report](../../patches/upstream/review-wifi-v2-20261028/clean-arm-build-result.json), [SHA and warnings](../../patches/upstream/review-wifi-v2-20261028/clean-build-verified-artifacts.json).

**This is exact clean-source offline compile + replay PASS, not a physical pass.** No flashed or loadable test on the Xoom was conducted for these new modules; the on-device persistent V31 remains original lab SHA `c82bd4e25ba1d96a01136407b200fe8c5431c7c89856e420dac4a81580183dc8`, so the binary identities differ by design. Do not mix core/WCC or assume their ABI interchangeability.

## Upstream acceptance ledger and independently blocked platform source

- G01 target and provenance: **PASS for pinned development base**, actual receiving maintainer tree still OPEN.
- G02 logical scope: **PASS initial Wi-Fi decomposition**, still requires human technical/race review.
- G03 application: **PASS for clean aggregate sequential six-part replay**; per-prefix independent compile/boot **OPEN**.
- G04 style: **PASS strict checkpatch on 3 Wi-Fi patches**, sparse/static analysis/lifetime tests **OPEN**.
- G05 build: **PASS fresh full ARM zImage, DTBs, modules**, other Kconfig/arch configs and bisect-prefix build **OPEN**.
- G06 lifetime/concurrency: **OPEN** for P2P/teardown/stale events/abort/scan ownership.
- G07 regulatory/hardware functional equivalence: **V31 lab PASS**, this exact clean source **OPEN**.
- G08 board DT bindings: **OPEN**, despite DTB compiler success.
- G09 multiple physical devices: **OPEN**.
- G10 maintainer mapping: pinned `get_maintainer.pl` **performed**, actual submission recipients/branches **OPEN**.
- G11 contributor DCO / licensing review: **OPEN, deliberately unsigned**.
- G12 private firmware/rootfs boundary: **PASS separation in source**, complete deployment/rollback design **OPEN**.

Strict platform snapshot checkpatch, see [exact audit JSON](../../patches/upstream/review-wifi-v2-20261028/platform-and-maintainers-audit.json): **DTS 353 errors/360 warnings**, **ARM ATAG 6 errors/16 warnings**, **BigPart 3 errors/4 warnings/2 checks**. These platform snapshots are **not upstream-ready**, must be separately cleaned as ARM/DT/Block patches; do not silently include them in the wireless submission. The DTS receives Tegra and Devicetree maintainers; ATAG goes through ARM; BigPart through block/GPT; Wi-Fi through wireless `brcm80211` maintainers.

## Next gates

1. Physically evaluate the **exact new zImage/DTB/matched module set** with a reversible no-flash or controlled backup/rollback plan, target same V31 functional result (two scans, association, DHCP, DNS, NTP, HTTPS), and compare real firmware logs. Do not displace currently working p7/p8 merely for an offline build.
2. Independently inspect Wi-Fi event owner races, cfg80211 scan lifecycle under cancellation, multi-interface, regulatory behavior, and check individual patch prefix builds.
3. Treat the 399-second boot WPA association problem (legacy v1/v2 firmware event format and/or firmware UP on connect path) as **pending separate, evidence-gated diagnostic issue**.
4. Rework platform and DT binding/BigPart correctness in their own logical series; preserve physical board baseline.
5. Obtain actual human DCO sign-off, accurate author/assist attribution and target maintainer review **only when user explicitly authorizes upstream mailing**.

No background job, automated source push upstream, eMMC flash or Xoom modification was made.
