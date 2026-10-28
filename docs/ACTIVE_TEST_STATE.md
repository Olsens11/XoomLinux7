# XoomLinux7 — active physical test state

**Snapshot recorded: 2026-10-28, after the documented Bluetooth A/B testing and safe shutdown.** This is a **time-scoped, living index of verified observations**, not a claim about the device's state at an unspecified later time and not a substitute for immutable physical evidence. Every use of *current*, *latest* or *now* in a dated project document means **as of that document's stated observation or production time**. Earlier documents' current-state statements remain valid snapshots of their own dates; later findings add chronology, not retroactive corrections. To establish the presently running state in a future session, reread the newest checkpoint **and** independently inspect the live device. For new work also read the [evidence protocol](process/DOCUMENTATION_AUTHORITY.md).

## Device and safety boundary

**Current DUT:** replacement Motorola Xoom MZ600 CDMA, running the **nine-review Linux 7** kernel launched by temporary `fastboot boot`, with **Debian 12 Bookworm mounted read/write on internal BigPart p10**. USB g_serial COM9 remains functional from Surface Book 2. The **original Recovery Toolkit Xoom is a separate, protected device** and cannot share presumed Bluetooth identities/bonds or receive Linux DUT test images.

**Protected state:** previously verified V31 p7 kernel and p8 Debian fallback remain intact; BigPart TWRP 2.8.6.0 on p6 retained; cold p8 backup independently SHA-verified on rescue SD and Surface. No reboot, boot partition flash, GPT change, or Wi-Fi driver replacement in this Bluetooth series. The p10 filesystem is a 1GiB ext4 installation inside the larger BigPart p10 region, **not yet expanded**.

## Test acceptance ledger

| Subsystem / claim | Current verified level | Remaining gate |
| --- | --- | --- |
| Nine-review kernel + Debian | Actual root login over COM9; p10 root RW, BigPart partition starts/sizes checked | Persistent p7 migration **not approved**; p10 ext4 expansion open |
| 5GHz Wi-Fi and network | Real association with NetworkManager, IPv4/DHCP route, successful signed Debian HTTPS package fetch; association persisted throughout Bluetooth A/B trials | Repeatable full scan and sustained stress/coexistence acceptance |
| Native display | Actual 1280×800 tegradrmfb, fbcon bound; `busybox chvt 2` showed a login prompt; `/dev/tty2` clear/banner physically displayed | Local key input and touch-driven UI **not tested** |
| Touch hardware | Atmel maXTouch `/dev/input/event3`, active IRQ, evtest ABS MT axes and 16 slots | Actual finger/touch events and an on-screen keyboard **not tested** |
| Bluetooth basic stack | Linux `hci_uart_bcm` serdev, HCI0, BlueZ 5.66; generic HCD patch loads and HCI powers on; Wi-Fi stays associated | No discoverable peer, authenticated bond, HID, or data connection demonstrated |
| Generic BCM4329B1 HCD (A) | 17,332B, SHA256 `7fbab01012c909b9b2de0fda3a76c43fa1c5c150e08642d7d1dbaf4d5ebf887c`; loaded through `brcm/BCM4329B1.hcd`; controller registered after async delay | Bounded BR/EDR searches found no Surface in either direction; explain RF/config/clock/identity |
| Exact OEM MZ600 HCD (B) | 17,770B, SHA256 `2d68db625a3e4e32fcc30813746fb84ca37491e055ad5e5e5d43057e4f2c16ea`; matched HRI39/HRI66; loaded via device-specific filename | **Failed**: controller write-clock and reset timed out `-110`; no usable HCI index |
| End-of-test rollback | OEM B disabled to a SHA-verified `.trial-20261028` filename; generic A restored, HCI present; **radio powered OFF**, BlueZ service inactive, Windows discoverability restored OFF; Wi-Fi still connected, COM9 working | Verify baseline again before any new RF test |

## Bluetooth experiment timeline and interpretation

1. Installed official Debian BlueZ tools on p10 after confirming WLAN reachability and preserving COM9; the base image originally lacked them. BlueZ is distinct from the original Android/Recovery BlueZ 4.69 environment.
2. Verified Surface Marvell adapter and reviewed **Recovery project's real hardware** milestones V057 (Surface discovery + unpaired SDP), V062 (authenticated Just Works pairing using Windows Bluetooth callback) and OEM `init.stingray.rc` HCI setup. These are **historical evidence on a different Xoom**; they establish a useful implementation reference, not a current Linux 7 pass.
3. Corrected the Linux management inquiry from default LE+BR/EDR to BR/EDR-only. Confirmed discovery-start method success but no peer returned. Do not confuse a zero shell exit or inquiry started with discovery/connection success.
4. Transferred generic HCD A via bounded COM9 chunks, independently hashed on Xoom, reloaded Bluetooth-only `hci_uart`. A loaded and allowed HCI power, but both Surface→Xoom and Xoom→Surface inquiries remained negative.
5. Compared A with *exact original Motorola* HCD B from two OEM references; verified different file sizes and hashes, staged B as higher-priority device-specific firmware name. HCI driver loaded B, then failed on clock write and reset (`-110`). **This is negative evidence**, not Bluetooth success.
6. Removed B from active firmware lookup without deleting it; loaded A again, waited for asynchronous controller registration, verified BlueZ HCI powered and Wi-Fi association; then safely powered off BT and stopped bluetooth.service. The system is currently preserved at this state.

## Current hypotheses, ranked but NOT proven

**A. UART clock/baud sequencing and firmware compatibility:** Device-tree `max-speed=<3375000>`, while Motorola OEM Recovery startup explicitly used 3000000. `hci_bcm.c` sends Broadcom vendor `0xfc45` (48MHz clock request) at speeds above 3000000, exactly where OEM B timed out. **The difference is measured, the cause is a hypothesis.** Tegra20 `serial-tegra.c` uses integer divisors and a claimed PLLP-derived 216MHz clock; request 3000000 **may actually yield ~2700000** at divisor5. Measure actual clock before claiming equivalence.

**B. Address/probe ambiguity:** HCI identity observed changed across patch initializations. Do not reuse old Recovery bond entries, and do not attempt pairing on presumed identity. Keep real addresses out of Git and inspect after each firmware initialization.

**C. Shared-chip power/clock sequencing:** Wi-Fi remained associated through both HCD trials, but that proves only a basic coexistence observation; UART flow control and BT reset still need separate investigation. Avoid broad shared GPIO/regulator resets.

**Next safe engineering step:** source-only comparison of OEM HCI init vs Linux 7 Broadcom UART/clock handling; prepare one-variable diagnostics or a lab-only DTS/driver hypothesis with exact source delta and test gate. **No reboot or physical flash unattended.** After owner is physically available, run a guarded temporary-boot hardware experiment and record all success and failure conditions.

## Authoritative references and logging contract

- [Nine-review p10 first physical boot, display and network](checkpoints/MZ600_NINE_REVIEW_LINUX7_P10_BOOKWORM_FIRST_PHYSICAL_BOOT_PASS_2026-10-28.md)
- [Initial BlueZ 5.66 / Surface attempt and failure](checkpoints/MZ600_REVIEW9_P10_BLUEZ_BCM4329B1_SURFACE_BLUETOOTH_PAIR_ATTEMPT_2026-10-28.md)
- [OEM Recovery cross-reference + HCD A/B + rollback — latest physical Bluetooth checkpoint](checkpoints/MZ600_REVIEW9_P10_RECOVERY_SURFACE_OEM_BLUETOOTH_FIRMWARE_AB_2026-10-28.md)
- [Milestone recording and publication requirements](process/DOCUMENTATION_AUTHORITY.md) and [private evidence rules](process/EVIDENCE_AND_PRIVACY.md).

**On every physical test:** write a dated, append-only checkpoint with one tested hypothesis, exact inputs and commands/tool versions, observed pass/fail/unknown with timestamps, privacy-safe evidence pointers, unexpected effects, cleanup and the next discriminator. Update the new *as-of* snapshot or append a chronologically labeled entry here, `docs/status.md`, both machine-readable state files, and the appropriate index in the **same commit**. Do **not** change historical records merely because a later state differs; preserve their original timestamps and wording. Never quietly overwrite old results or assume the user's chat history exists.

**Private receipts on Surface:** under `C:\Users\olsen\xoom-linux-rom\captures\MZ600-Review9-P10-Debian-20261028-A\`; no vendor blobs, real addresses, raw identifying logs or passwords in Git.
