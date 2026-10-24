# BCM4329 whole-chip resource ownership — Motorola OEM reconstruction

**Status (October 24, 2026):** Tested OFFLINE architectural model only. NOT activated as a Linux driver. No new kernel boot, GPIO output change, or flash. Physical v025 MZ600 remains unchanged with F2 timeout -62. See [149-page datasheet index](BCM4329_DATASHEET_PAGE_INDEX.md), [requirement audit](BCM4329_DATASHEET_REQUIREMENT_AUDIT.md), and [v027 GPIO record](../checkpoints/V027_BT_WLAN_GPIO_READONLY_PHYSICAL_2026-10-24.md).

## Evidence: the shared chip was already handled as shared in Motorola's OEM kernel

Historical Motorola Stingray kernel source: https://android.googlesource.com/kernel/tegra/+/eb4e253d7d76f6093ef50597e909157c21803842%5E2..eb4e253d7d76f6093ef50597e909157c21803842/

1. OEM change_power_brcm_4329(bool) uses a protected reference count so **both Wi-Fi and Bluetooth vote on the same Tegra U4 shared-power GPIO**. It drives U4 low only when the count falls to zero. It caps the count at two; modern software should use independent typed consumer vote accounting rather than copying its assumptions.
2. OEM stingray_wifi_power(on): delay 100 ms; call shared power function; delay 100 ms; set WLAN reset to on; delay 200 ms. These are source-level delays, **not physical VDDC timing measurements**.
3. OEM bcm4329_bt_rfkill_set_power() calls the same shared power function. It sets BT_SHUTDOWN_GPIO (I7) LOW in **both** enabled and blocked callbacks; it controls BT_RESET_GPIO U0 according to the request. It does not demonstrate what I7 was at every instant since boot.
4. The OEM code treats the BCM4329 as **one shared power object** while WLAN and Bluetooth retain separate functional interfaces. This is a concrete architecture not presently reproduced in our Linux 7 configuration.

## Datasheet grounding, with qualification

- BCM4329 datasheet pp.81 and 132: BT_REG_ON and WL_REG_ON are ORed inside the chip. **Both low** requests internal-regulator shutdown; either high can keep internal regulators on. Both inputs have **200k ohm internal pull-downs**: an undriven pin is not automatically high, though output ownership, external pulls and leakage still matter. Neither of these is a physical voltage measurement on our replacement Xoom.
- pp.132–134: WL_RST_N and BT_RST_N are separate active-low resets; the internal POR is a separate condition. Figure 32 shows that WLAN ON / Bluetooth OFF is possible, even if the shared internal regulators are still enabled. BT_REG_ON high does not by itself imply Bluetooth logic is running.
- pp.48, 64–70: shared PMU resources, clock/32.768-kHz LPO dependencies, and delayed transitions can outlast software GPIO calls. SDIO host must wait the mandated interval after **VDDC/VDDIO have actually become available**, not merely after an MMC delay started.

Important interpretation: if U4 WLAN enable is already high and the other input I7 is also high, this **does not directly prevent WLAN reset release**. Its consequence is that dropping U4 cannot force the chip's internal regulators off. An attempted complete power-cycle could actually be a WLAN-only warm reset. This is a plausible test-coverage gap, NOT yet a demonstrated cause of F2 -62.

## Current Linux 7 source and physical observations

| Resource | Source now | Motorola OEM | Status |
| --- | --- | --- | --- |
| U4 shared power | fixed regulator vdd_wifi, boot-on; MMC vmmc consumer | one U4 vote for WLAN and Bluetooth | architecture differs |
| I7 BT shutdown / regulator-enable | Broadcom UART hci_bcm shutdown-gpios, driven when BT loads | I7 low in both OEM BT rfkill branches | concrete source divergence; current physical I7 unknown |
| U2 WLAN reset | separate MMC simple pwrseq | OEM WLAN callback post-U4 vote | distinct ownership and sequencing |
| U0 BT reset | hci_bcm reset-gpios | OEM BT rfkill reset output | runtime ownership unknown |
| 32.768kHz LPO | WLAN pwrseq ext_clock and BT txco both same PMC blink phandle | shared hardware resource | configured roles require validation |
| Shared resource coordinator | CONFIG_POWER_SEQUENCING **not set**; no connected MMC/BT pwrseq consumer | protected shared power reference count | missing integration |
| BT driver | CONFIG_BT_HCIUART=m, Broadcom support y within HCI module | OEM board rfkill | compiled != loaded or bound |

Physical v027 read-only observations: U4 HIGH and U2 HIGH are valid configured output-latch readings. I7, U0, U1 and U6 direction returned -22; their raw-zero values **do not establish** their chip-level state. LPO software provider 32768Hz enabled, first actual F2 ready bit still absent. No reliable I7 measurement.

## Target system: whole-chip physical-resource coordinator, not a monolithic WLAN/BT/FM protocol driver

Desired logical model:

    Motorola BCM4329 physical-resource owner
      shared U4 power vote, shared regulator dependencies and LPO clock
      two named targets: WLAN and Bluetooth; optional FM depends on BT
      independent U2 WLAN reset and U0 BT reset, defined passive states
      monotonic power/clock/reset event trace and externally verified states
             /                                \
         MMC / SDIO                         UART / HCI
         brcmfmac                            hci_bcm

Use a modern Linux power-sequencing provider with target dependency units and reference counts: https://origin.kernel.org/doc/html/latest/driver-api/pwrseq.html. The source exists in Linux 7, but our build has CONFIG_POWER_SEQUENCING disabled, and **neither the current MMC nor hci_bcm implementation consumes that provider**. Merely adding a parent device-tree node does nothing; provider, matching, function-specific consumers and a migration of existing GPIO ownership are all required.

### Single ownership is mandatory

- **U4** is already owned by a fixed regulator. A new coordinator must acquire/vote on *that regulator*, or carefully remove the regulator GPIO ownership during migration; do not double-request U4.
- **I7** may be requested by hci_bcm when Bluetooth binds. Do not request/drive it independently until ownership is migrated or the driver is deliberately kept disabled, and verify original OEM pad wiring first.
- **U2** belongs to MMC simple pwrseq; **U0** to the UART Bluetooth driver. A replacement shared provider cannot request the same output pins at the same time.
- A documented Bluetooth-passive state is BT reset asserted, BT_WAKE deasserted, no active Bluetooth clock/resource request and no unintended BT_REG_ON vote, but the board-specific I7 low policy must be verified before hardware application.
- Ordinary WLAN and Bluetooth protocol drivers remain independent and portable; chip-specific shared resource handling remains board-aware and reusable.

### Staged implementation and safety

1. First **read-only**: determine if the HCI UART module is loaded/bound, check I7/U0 pinmux and actual controller ownership, and reconcile OEM U4/I7 policy. Do not infer line levels from v027 -22.
2. Offline model: tools/forensics/bcm4329_shared_chip_model.py and test_bcm4329_shared_chip_model.py cover the OR truth table including UNKNOWN states, independent and Motorola-shared-U4 plans, distinct WLAN/BT reset, conservative host-access gates and reference counts. **No hardware access in these tests.**
3. Compile-only kernel provider candidate with separate WLAN and BT targets, preserving Linux pwrseq API and existing standard SDIO/UART protocol drivers. Review all duplicated GPIO and clock consumer ownership; add DTS binding/schema before considering boot.
4. Temporary-boot **read-only** event trace of regulator votes, real GPIO/pinmux/controller reads, LPO/normal clock configuration and first SDIO access, all with common monotonic timestamps.
5. Only then test one-variable ownership differences (OEM shared U4 behavior versus current default), with v025 recovery image and USB control retained. Do not change oscillator, SDIO capability quirk and regulator policy in the same experiment.
6. Require F2 ready and stable WLAN interface plus correct unique same-device MAC, valid radio/regulatory data and repeated tests before qualifying a fix. Full chip POR is only "confirmed" if actual internal-regulator-off condition is observed, not merely because both software votes are released.

## Offline model and what it cannot prove

Run the software-only model unit tests:

    python3 /home/xoomdev/projects/XoomLinux7/tools/forensics/test_bcm4329_shared_chip_model.py

Tests deliberately cover an active BT vote preventing full power-off, shared OEM U4 kept high when WLAN releases its vote, zero-vote state without evidence of physical off, unknown pin states, and a minimum 110ms gate tied to a known supply-stable timestamp. It is **not an electrical model** and doesn't prove the source of F2 failure.

## Source references

- [Motorola historical Stingray code](https://android.googlesource.com/kernel/tegra/+/eb4e253d7d76f6093ef50597e909157c21803842%5E2..eb4e253d7d76f6093ef50597e909157c21803842/)
- [BCM4329 datasheet](https://media.digikey.com/pdf/Data%20Sheets/Cypress%20PDFs/BCM4329_RevF_Sep19%2C2016.pdf)
- [Linux power sequencing API](https://origin.kernel.org/doc/html/latest/driver-api/pwrseq.html)
- [Broadcom Bluetooth DT binding](https://linux.googlesource.com/linux/kernel/git/torvalds/linux/+/2a4d91142e538ff5580c6bf48b5e668d8131fd9a/Documentation/devicetree/bindings/net/bluetooth/brcm%2Cbluetooth.yaml)
