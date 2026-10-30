> **2026-10-30 13:42 EDT INFRASTRUCTURE I0 HOST TOOLING PASS (NOT PHYSICAL):** Surface I0 safety inspection and full SHA-verified backup utility mock-tested; staged p10 root image install/promotion utility mocked for success, corrupt-image refusal and partial-rename rollback; COM10 privileged acceptance probe syntax checked only. [Exact execution instructions](I0_TWRP_EXECUTION_AND_RECOVERY_CHECKLIST_2026-10-30.md), [host-tool evidence](../../checkpoints/MZ604_I0_HOST_CONTROL_SCRIPTS_MOCK_PASS_2026-10-30.md). Tablet still Linux COM10 locked login, NOT in TWRP. W1 MZ604 firmware/SDIO/Wi-Fi physical remain NOT RUN, W0–W6 goal unchanged. Don't overdevelop reboot/watchdog infra.

> **2026-10-30 I0 OFFLINE PREPARATION PASS:** 10 SHA-verified files on Surface in `MZ604-READY-V2-20261030`, full ARM zImage/modules/DTBs build PASS, 114 modules archived, 3 ext4 raw images verified through gzip on Surface, five-pass fsck on modified Debian/p8 and optional p8 selector, QEMU ARM BusyBox applet test PASS. [Exact recovery entry/install gates](I0_TWRP_DEPLOYMENT_READY_2026-10-30.md); [immutable offline checkpoint](../../checkpoints/MZ604_I0_SURFACE_V2_DEPLOYMENT_OFFLINE_READY_2026-10-30.md). **I0 privileged COM10 still PHYSICAL NOT RUN; owner must enter TWRP first.** W1 actual MZ604 Wi-Fi unchanged NOT RUN. Do not conflate staged binaries with flash/boot/driver PASS.

> **2026-10-30 I0 REFINEMENT (NOT YET PHYSICALLY PASS):** The owner approved [passwordless-first Xoom lab access](../../process/DEVELOPMENT_AUTHENTICATION_POLICY_2026-10-30.md): COM10 `xoom` autologin + passwordless sudo; fallback account password `1234` if required. I0 still requires supervised TWRP backup/provisioning and independently verified privileged COM10. No account changes performed, and no other W0–W6 outcome is changed.

> **2026-10-30 STATUS AND PREREQUISITE:** W0 clean-source work complete. **W1 now has PHYSICAL Linux/USB COM10/PID1-to-Debian-login PASS through a separate USB-peripheral study DTB**, but **authenticated Debian login, actual stock-Wingray-DTB physical parity and all BCM4329 Wi-Fi measurements remain OPEN**. The Oct29 RAM-only bootloader rejection below is genuine historical evidence, superseded as the latest *bootability* state by [Oct30 checkpoint](../../checkpoints/MZ604_PERSISTENT_LINUX_COM10_PHYSICAL_2026-10-30.md). Before more Wi-Fi tests complete the bounded, separately tracked [I0–I5 practical remote boot/access gates](REMOTE_TEST_INFRASTRUCTURE_PLAN_2026-10-30.md), **without bootloader/BCT/EBB/GPT changes or elaborate automatic crash recovery**. Physical reboot may sometimes be necessary. Every future agent must read [required contextual records](AGENT_READING_MAP.md) and all [chronological logs](../../project-log/README.md); append short dated work log per substantive turn; detailed handoffs at milestones. **W2–W6 remain OPEN and Wi-Fi unchanged.**

# MZ604 Wingray — upstream-first BCM4329 2.4 GHz RFC milestones

**Active for branch `rfc/bcm4329-upstream-first-20261029`**; this replaces the MZ600-first M0–M7 checklist only for new work. The old checklist, M1 study commits, and nine-patch research stay unchanged as historical evidence. No MZ604 physical tests or new Linux source patches have been accepted.

## W0 — Select starting board and isolate source
- [x] Select Motorola Xoom **MZ604 (Wingray, Wi-Fi only)** to match the existing upstream DTS and avoid a first-series MZ600/Stingray variant refactor.
- [x] Create a new independent Linux source branch/worktree from pinned `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`; preserve old MZ600 branches/worktrees and installed systems.
- [x] Verify the new Linux checkout is clean, unchanged upstream `2404d273`, with an independent ARM build; original Wingray DTBs, zImage and complete modules build PASS, and offline Android-format RAM-only boot image header/embedded DTB verified. No MZ604 boot claim. [Baseline evidence](BASELINE_BUILD_AND_USERSPACE_2026-10-29.md).

## W1 — Prove baseline upstream support, before any patch
- [x] Source-level: upstream DTS and Makefile already contain Wingray; DTS contains BCM4329 SDIO, power, reset/clock, regulators and IRQ; `brcmfmac` already contains BCM4329 chip ID, standard STA/scan and firmware paths.
- [ ] Compare upstream DT declarations with actual OEM **MZ604** board and firmware provenance; identify true mismatches instead of assuming prior MZ600 differences apply.
- [ ] Verify OEM board and bootloader identity and which firmware/NVRAM/factory-MAC path MZ604 actually uses. **Physical `wingray` / `xoom-wifi` / bootloader1050 and stock firmware/calibration files are VERIFIED, but factory-MAC delivery to Linux remains OPEN.** Never publish private values.
- [x] Physically identify stock MZ604 (`wingray`/`xoom-wifi`), record its original firmware/calibration in private storage, and unlock dedicated eBay development hardware with owner authorization; confirmed `unlocked=yes`. **No flash.** [Actual checkpoint](../../checkpoints/MZ604_UPSTREAM_FIRST_FASTBOOT_BOOT_REJECTED_2026-10-29.md).
- [ ] **BLOCKED:** Guarded Linux temporary boot: the first two identical SHA-verified `fastboot boot` trials each transferred the image then returned Motorola `(00000008)`. Kernel execution **NOT OBSERVED**. Investigate exact bootloader behavior and reversible method; explicit owner consent required for any partition write. [Actual checkpoint](../../checkpoints/MZ604_UPSTREAM_FIRST_FASTBOOT_BOOT_REJECTED_2026-10-29.md). **2026-10-29 attempt:** exact upstream RAM-only image transferred+hashed; bootloader `boot` rejected with `(00000008)` after `Sending boot.img OKAY`. Linux never started. [Negative hardware checkpoint](MZ604_FASTBOOT_RAMONLY_FIRST_PHYSICAL_NEGATIVE_2026-10-29.md). No flash issued.
- [ ] Establish minimal normal boot, SDIO, firmware and `wlan0` baseline; if boot fails, isolate the earliest causal deviation.
- [x] **OFFLINE:** Stage **fresh Debian ARMHF network-capable root filesystem** before physical WLAN work: `NetworkManager`/`nmcli`, `wpa_supplicant`, `iw`, `ip`, `ping`, DHCP client, DNS tools, basic TLS/network diagnostics and kernel-matched `brcmfmac` modules; no recycled MZ600 identities or WPA credentials. Actual packages and kernel-matched module installation verified in the freshly bootstrapped ARM root; independent 2 GiB MBR/ext4 SD image and temporary SD-root boot image built and their on-disk structures and SHA-256 checked. **Physical MZ604 boot/root path is still OPEN.** This is separate from the minimal non-storage RAM-only diagnostic image; see [baseline build record](BASELINE_BUILD_AND_USERSPACE_2026-10-29.md).

## W2 — Decide the minimum BCM4329 firmware ABI compatibility
- [ ] Measure on **MZ604** whether `chanspecs` fails, which native BCME is returned, and whether `BRCMF_C_GET_VALID_CHANNELS` is available; distinguish old MZ600 evidence from new physical proof.
- [ ] If needed, introduce a small chipset/firmware-specific legacy inventory fallback in existing `brcmfmac` with bounded counts, native error discrimination and no changes to normal modern driver behavior.
- [ ] Source/negative/regression QA and then separate authorized exact-kernel hardware test.

## W3 — Effective 2.4 GHz regulatory safety
- [ ] Establish actual MZ604 firmware, board/calibration and Linux regulatory intersection; no forced US/69 or synthetic DFS metadata.
- [ ] Ensure unverified 5 GHz transmit-capable operation cannot occur; `NO_IR` alone is not enough.
- [ ] Review existing device-specific country mapping before adding a new DT property or policy.

## W4 — Repeatable ordinary scanning
- [ ] Three fresh completed 2.4 GHz scans through standard `iw`/cfg80211; verify event ingress vs delivered completion, timeout, cancellation and request lifetime.
- [ ] Add only **necessary proven** sync ID, invalid-index Event69 ownership and conditional firmware-UP fixes from preserved r7/V31 research, not the whole collection by default.

## W5 — Ordinary STA connectivity and reproducible build
- [ ] WPA2 connection, DHCP/DNS/data and normal NetworkManager or wpa_supplicant operation; disconnect/reconnect and repeated boots. **Install standard networking/testing utilities offline before the first WLAN physical trial**, not after the driver starts working.
- [ ] Full ARM zImage/DTB/modules and ABI, targeted DT schema, kernel style and static tests; exact source/build/firmware identities and physical receipts.
- [ ] No BigPart kernel GPT changes, proprietary firmware redistribution, CDMA/LTE work, Bluetooth/FM or unsupported 5 GHz claims.

## W6 — First upstream RFC review
- [ ] One logical issue per actual patch; original upstream code reused; meaningful commit body, no artificial patch count.
- [ ] Summarize demonstrated functions, exact tested **MZ604** hardware/firmware, known gaps, conservative radio behavior and precise maintainer questions.
- [ ] User reviews patch set and personally supplies applicable DCO; only then may it be submitted externally.
- [ ] Maintain MZ600 and other Xoom board variants as follow-on support, not blockers for this first RFC.

**Current completion:** W0 selected, clean pinned source verified, untouched Wingray DTB/zImage/modules built and RAM-only diagnostic packaged offline. W1 source baseline and **fresh full Debian ARMHF networking tools plus exact modules in verified off-device SD/root and boot image files PASS**. MZ604 physical identity and `unlocked=yes` **PASS**; original OEM firmware/calibration copies privately preserved; **fastboot temporary boot FAIL (00000008)**, therefore Linux runtime and real MAC provenance, WLAN operation and RF gates remain **OPEN**. No changed radio, device firmware, partitions or physical flash. Future changes require exact issue-linked evidence and safe rollback.
