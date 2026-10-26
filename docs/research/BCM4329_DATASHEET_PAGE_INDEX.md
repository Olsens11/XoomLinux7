# BCM4329 datasheet — full page-level navigation index

**Reference:** *BCM4329 Preliminary Data Sheet*, Broadcom 4329-DS105-R, December 3, 2010, included in Cypress document 002-14927 Rev. *F (September 19, 2016). **149 PDF pages.** Uploaded reference SHA256: `7c8ae70f36b1ce7e08d064d4965884eb9eb30e31d5df7e5434029fd3ad3bab24` (2,539,698 bytes). Printed page numbers match PDF page numbers in this edition.

This index covers **every page**, including front matter, non-WLAN subsystems and RF electrical tables, to help avoid blind spots. An **H** flag means high relevance to current F2 failure, **M** means a useful direct/cross-subsystem constraint or hardware reference, and **L** means indirect or post-start. A page rated L is **not** proof it is irrelevant to every future fault. The wording is a navigation summary, not a reproduction of the datasheet.

Original online reference: https://www.rxelectronics.jp/datasheet/ff/CYW4329HKUBGT.pdf (the uploaded 149-page copy was used for this index).

The exact uploaded datasheet remains the specification authority. Refer to figures/tables in the original PDF before interpreting timing, voltage, or pin polarity. Physical Xoom implementation is audited separately in [requirements and evidence](BCM4329_DATASHEET_REQUIREMENT_AUDIT.md).

| PDF page | Relevance | Subject, table or figure | Why it matters / follow-up |
|---:|:---:|---|---|
| 1 | L | Cypress continuity notice | Document provenance, no functional design guidance |
| 2 | M | BCM4329 overview and feature sheet | Supported SDIO v1.2, integrated WLAN/BT/FM and reference clocks |
| 3 | M | System block diagram, feature continuation | Shared resources, WL/BT host interfaces |
| 4 | L | Revision history, 2016/2010 | Trace which specification revision is used |
| 5 | M | Revision history, SDIO and reset changes | Historical edits to SDIO timing/boot sequence are relevant |
| 6 | M | Revision history, power and clock revisions | Caution comparing older Motorola implementation against revised datasheet |
| 7 | M | Revision history, reset sequencing introduced | Documents the reset/control-signal requirements provenance |
| 8 | L | Revision history, RF/regulator refinements | Revision provenance for electrical characterization |
| 9 | L | Legal notice | No technical requirements |
| 10 | L | Table of contents 1 | Navigation: WLAN/BT systems |
| 11 | L | Table of contents 2 | Navigation: WLAN interfaces and software |
| 12 | L | Table of contents 3 | Navigation: power, clocks, pinout |
| 13 | L | Table of contents 4 | Navigation: I/O/reset and electrical |
| 14 | L | Table of contents 5 | Navigation: control sequencing and packaging |
| 15 | L | List of figures | Quick jump to figures 1, 21–24, 30–33 |
| 16 | L | List of tables 1 | Quick jump to SDIO, clocks, pinout |
| 17 | L | List of tables 2 | Quick jump to regulator, power, timing |
| 18 | H | BCM4329 architecture block diagram | Shared WLAN/BT silicon backplane, PMU, LPO, WLAN Cortex-M3, OTP |
| 19 | M | Capability and host-interface features | SDIO v1.2 and integrated radios; avoid assuming other protocols |
| 20 | L | Standards compliance | MAC/PHY functions downstream of failed F2 |
| 21 | M | Bluetooth+FM integration | Power and reference resources may be shared |
| 22 | M | Bluetooth interfaces and low-power features | Separate UART, BT_WAKE, UART_WAKE, XTAL/clock request |
| 23 | M | Handset oscillator/usage model | TCXO and LPO host requirements |
| 24 | M | Mobile phone block diagram | Distinct WL_RESETx, BT_RESETx and UART/SDIO pins |
| 25 | L | Bluetooth transmit/receive internals | RF datapath not relevant until chip startup |
| 26 | L | Bluetooth RF calibration | Usually downstream of Wi-Fi F2 startup |
| 27 | L | Bluetooth baseband description | Peripheral functions, not Wi-Fi boot root path |
| 28 | L | Bluetooth baseband modes / RF PM | May indirectly retain shared resources |
| 29 | H | BT UART handshake; Table 1 CLK_REQ/BT_WAKE/UART_WAKE | Do not confuse CLK_REQ output with LPO input; pin mux/polarity |
| 30 | M | BBC and FM power management | Bluetooth low-power modes use LPO; FM may retain blocks |
| 31 | M | Bluetooth ARM7/ROM/reset | Separate BT firmware CPU and BT reset from WLAN Cortex-M3 |
| 32 | L | Bluetooth PCM peripheral | Low immediate WLAN-startup relevance |
| 33 | L | Bluetooth PCM slot mapping | No F2 readiness constraint |
| 34 | M | Bluetooth UART baudrate and I2S | Reference clock and BT serial clock dependencies |
| 35 | L | FM receiver/transmitter | Potential shared clock/PMU consumer |
| 36 | L | FM control and RDS | Only if FM enabled during Wi-Fi bring-up |
| 37 | L | WLAN protocol architecture | After F2 successfully starts |
| 38 | L | WLAN MAC feature set | Firmware feature compatibility eventually |
| 39 | M | WLAN MAC architecture; PSM | Power-saving microcode and silicon backplane |
| 40 | L | WLAN PSM details | Post-firmware-start behavior |
| 41 | L | MAC channel timers | Post-F2 communications |
| 42 | L | WLAN PHY functions | Not primary F2 initialization |
| 43 | M | PHY power-on calibration | Requires correct clocks and firmware execution |
| 44 | L | MIMO/STBC architecture | Post-start signal processing |
| 45 | L | WLAN RF receiver/transmitter | Shared supplies but RF not yet enabled |
| 46 | L | RF calibration and radio path | Not F2 root until core starts |
| 47 | H | WLAN Cortex-M3 CPU + on-chip RAM/ROM | Firmware download/readback != CPU execution; probe core release |
| 48 | H | WLAN PMU sequencer, LPO timers, active/doze/off | Internal regulator votes and transition timers can delay/retain supplies |
| 49 | H | SDIO v1.2, 110 ms VDDC delay, pullups, F0/F1/F2 | Direct initialization requirements; current F2 stalls |
| 50 | M | SDIO 1/4-bit wiring figures 9–11 | Four data and CMD/CLK mappings; pullup and pinmux |
| 51 | H | Default-mode SDIO timing, Table 3 | <=25 MHz transfer, <=400 kHz identification, timing/edge limits |
| 52 | H | High-speed SDIO timing, Table 4 | <=50 MHz ONLY when high-speed mode genuinely enabled |
| 53 | M | SPI interface electrical/functional | Alternative multiplexed interface, not present test transport |
| 54 | L | SPI timing, Figure 15/Table 5 | Do not apply SPI constraints to SDIO |
| 55 | L | SPI protocol transactions | Different packet semantics from SDIO |
| 56 | L | SPI command format | Not directly applicable to MMC2 SDIO |
| 57 | L | SPI status mechanism | Don't mistake SPI status for SDIO F2 readiness |
| 58 | L | SPI status timing and bits | Not applicable to current SDIO configuration |
| 59 | M | SPI wake/boot handshake, XTAL_PU and crystal programming | SPI-only sequence; suggests distinct clock/PMU mechanisms, not commands to replay over SDIO |
| 60 | L | SPI registers, Table 7 (part 1) | Not valid SDIO register map |
| 61 | L | SPI registers, Table 7 (part 2) | Avoid importing SPI wake-up semantics into SDIO |
| 62 | H | DHD host/device firmware architecture and remote downloader | Firmware must execute on WLAN Cortex-M3; framed control/data channels |
| 63 | M | Software architecture Figure 21 and control IOCTL | Separate host transport from target firmware readiness |
| 64 | H | Shared supply topology; WL/BT_REG_ON and reset interplay | Either subcore may hold regulators on; check actual board topology |
| 65 | H | Figure 22 internal rails + PMU resource sequencing | VDDC/CLDO/CBUCK, dependencies, LPO-timed resource transitions |
| 66 | H | PMU sequencing algorithm and low-power shutdown | OFF vs doze vs reset: warm rebind may not erase state |
| 67 | H | Normal TCXO/crystal vs LPO references; 38.4MHz default | Verify board reference and matching xtalfreq; not same as 32.768k |
| 68 | H | Table 8 oscillator specs and frequency autodetection footnotes | WLAN does NOT auto-detect reference frequency; external-LPO caveat |
| 69 | H | Table 9 LPO waveform specs and Figure 23 crystal | Software enabled!=physical waveform; required nominal 32.768k input |
| 70 | H | Clock selection and LPO stability during POR | BT/FM auto-frequency detect distinct from WLAN; reference during reset |
| 71 | M | 182-ball assignment map Table 10, start | Pin identification for external board validation |
| 72 | L | Ball assignments continued (part 2) | Hardware reference only |
| 73 | L | Ball assignments continued (part 3) | Hardware reference only |
| 74 | M | Ball assignments continued (part 4) | BT_GPIO and strap pin verification |
| 75 | M | Ball map Figure 24 | If eventual probing, board orientation; no opening planned |
| 76 | M | WLBGA signal descriptions Table 11 start | Signals/voltage domains and reset details |
| 77 | M | Power supply pins Table 11 | VBAT, internal PMU and IO supply semantics |
| 78 | L | JTAG and miscellaneous pins | Potential debug only; do not enable without board proof |
| 79 | L | RF/PA/control pads | Coexistence and RF switch later |
| 80 | M | Bluetooth UART signal definitions | Pins and HW flow control distinct from WLAN SDIO |
| 81 | H | BT_GPIO/REG_ON/RST_N and shared supplies | Internal 200k pulldowns; OR-regulator logic and pin thresholds |
| 82 | H | WLAN 1.25V rails and other supply pins | VDDC isn't same as host vmmc/vqmmc values |
| 83 | M | Remaining FM/RF/no-connect pins | Pinout caveats |
| 84 | H | WL_GPIO_8 boot strap SPI-versus-SDIO selection | WL_GPIO_8 low at WL_RST_N release selects SDIO; verify OEM board straps |
| 85 | M | I/O reset-state table legend | GPIO/pull assumptions before firmware runs |
| 86 | H | Table 13 during/after reset incl SDIO CMD/DAT pulls | Pull states may differ in power-down and reset; startup pinmux |
| 87 | H | Table 13 footnotes: reset-only/out-of-reset states | BT/WL reset combinations not equivalent to full regulator OFF |
| 88 | H | BT_GPIO mux matrix Table 14 | BT_WAKE, UART_WAKE, CLK_REQ alternate function; default mux not enough |
| 89 | M | Table 15 alternate GPIO/CLK_REQ mapping | CLK_REQ labeled BT debug on some mux options; don't assume active |
| 90 | M | Voltage absolute maxima, Tables 16/17 | Never force unsafe GPIO/rail levels in tests |
| 91 | M | Recommended supply conditions and ESD | VDDIO/host logic compatibility |
| 92 | M | Recommended input thresholds/voltage continued | GPIO polarity and voltage levels dependent on VDDO |
| 93 | L | Bluetooth receiver RF specs introduction | Irrelevant until firmware executes |
| 94 | L | BT receiver RF Table 20 | No F2 bring-up dependency |
| 95 | L | BT receiver blocker specs | Post-start RF only |
| 96 | L | BT transmitter RF Table 21 | Post-start RF only |
| 97 | L | BT LO characterization Table 22 | Check only if BT clock hypotheses need RF validation |
| 98 | L | FM transmitter specs introduction | Not directly WLAN startup |
| 99 | L | FM TX modulation parameters | Not relevant |
| 100 | L | FM TX noise dependent on LPO | Evidence shared LPO importance if FM active |
| 101 | L | FM receiver specs introduction | Not directly WLAN startup |
| 102 | L | FM Rx sensitivity/adjacency | Not relevant |
| 103 | L | FM Rx blocking | Not relevant |
| 104 | L | FM Rx distortion/decoder | Not relevant |
| 105 | L | FM RF filter scheme Figure 26 | Shared RF components, post-boot |
| 106 | L | WLAN RF transmitter/receiver overview | Power supplies only indirect bring-up relevance |
| 107 | L | 2.4 GHz WLAN RF specs Table 25/26 | Post-firmware capability checks |
| 108 | L | 2.4 GHz WLAN receiver sensitivity | After wlan0 |
| 109 | L | 2.4 GHz WLAN receiver rejection | After wlan0 |
| 110 | L | 5 GHz WLAN RF receiver specs | After wlan0 |
| 111 | L | 5 GHz WLAN RX blocking/rejection | After wlan0 |
| 112 | L | 2.4 GHz WLAN transmitter specs | After wlan0 |
| 113 | L | 2.4 GHz WLAN TX electrical | After wlan0 |
| 114 | L | 5 GHz WLAN transmitter specs | After wlan0 |
| 115 | L | WLAN spurious emissions | After wlan0 |
| 116 | M | CBUCK specs, Table 31 | CBUCK startup/timing supply characteristics; topology-dependent |
| 117 | M | PALDO/LDO2p5V specs, Tables 32–33 | Alternate internal regulators and startup time |
| 118 | H | CLDO supply specs, Table 34 | Internal 1.25V core supply settling depends on topology |
| 119 | M | LNLDO and PMU quiescent specs | Board topology and retained resource dependencies |
| 120 | L | WLAN power consumption Table 37 | Current draw could distinguish states only with electrical measurements |
| 121 | M | Bluetooth/FM current with WLAN held reset | Explicit example: Bluetooth can operate while WLAN in reset |
| 122 | L | Interface timing introduction | General electrical baselines |
| 123 | L | Bluetooth PCM timing start | No current SDIO boot effect |
| 124 | L | BT PCM master timings continued | No current SDIO boot effect |
| 125 | L | BT PCM slave timing | No current SDIO boot effect |
| 126 | L | BT PCM long-frame master | No current SDIO boot effect |
| 127 | L | BT PCM long-frame slave | No current SDIO boot effect |
| 128 | L | FM I2S timing figures 28/29 | Only if FM transport enabled |
| 129 | L | FM I2S timing table | Not current boot path |
| 130 | L | FM I2C timings Table 40 | Not current boot path |
| 131 | L | FM I2C timing continued | Not current boot path |
| 132 | H | Reset/REG_ON truth model + internal POR<=110ms | ORed regulator inputs, POR ORed with external resets; host access >=110ms |
| 133 | H | Control signals and figures 30–31 | Both on/off sequencing, WL_RST_N/BT_RST_N must be driven |
| 134 | H | Figures 32–33 WL-only/BT-only transitions | Essential to distinguishing shared powered reset vs true chip power-down |
| 135 | L | Thermal/environmental specs | Board reliability, not current F2 root |
| 136 | L | Package dimensions, Figure 34 | If hardware inspection someday |
| 137 | L | Ordering and package variations | Verify exact orderable chip/variant if known |
| 138 | L | Ordering continuation | No new startup requirement found |
| 139 | L | Ordering continuation | No new startup requirement found |
| 140 | L | Ordering continuation | No new startup requirement found |
| 141 | L | Ordering continuation | No new startup requirement found |
| 142 | L | Ordering continuation | No new startup requirement found |
| 143 | L | Ordering continuation | No new startup requirement found |
| 144 | L | Ordering continuation | No new startup requirement found |
| 145 | L | Ordering continuation | No new startup requirement found |
| 146 | L | Ordering continuation | No new startup requirement found |
| 147 | L | Ordering continuation | No new startup requirement found |
| 148 | L | Ordering continuation | No new startup requirement found |
| 149 | L | Manufacturer contact/back matter | No functional requirement |


### NEW 2026-10-26 navigation: verified hardware 5GHz, current Linux band-availability failure

Owner confirms Android negotiated 5GHz on this exact Motorola Xoom. Later Linux7 p8 Debian `brcmfmac`+BCM4329/3 generic firmware scanned 2.4GHz successfully but `iw phy` advertised **no 5GHz band or channels**. This is a *firmware/NVRAM/driver band-discovery software question*, not a failure of the chip to support 5GHz RF. Use **pp42–46 (WLAN PHY/RF/calibration), pp106–115 (RF electrical; p110–111 5GHz receiver, p114 5GHz transmitter), pp47 and 62–63 (on-chip WLAN firmware and host/DHD control), pp64–70 and 132–134 (shared supply/clock/reset if proven relevant), pp79–84 (RF/PA pads/board binding)**. Indexed original document 149 pages and requirements matrix are unchanged. Follow pinned kernel `brcmf_setup_wiphy()` firmware `BRCMF_C_GET_BANDLIST` and `brcmf_construct_chaninfo()` firmware `chanspecs`, as discovered in [2026-10-26 physical 5GHz regression checkpoint](../checkpoints/MZ600_V064_5GHZ_BAND_NOT_ADVERTISED_PASSIVE_SCAN_BLOCKED_PHYSICAL_2026-10-26.md). **Do not simply force channels into cfg80211 or change country/regrev, RF power or MAC to make a scan work.** This index is navigation, not a full radio qualification test.

## Fast reference by subsystem

### 2026-10-26 verified firmware-reporting boundary for Linux5GHz

The user's 149-page indexed Broadcom datasheet remains authoritative for physical RF: pp42–46 PHY/calibration, p110–111 5GHz receiver, p114 transmitter, pp47/62–63 chip FW/SDIO interface, pp64–70 power, pp132–134 shared reset. A minimal count-only kernel instrumentation has now confirmed actual Motorola MZ600 Debian firmware reports **only 2.4GHz via `BRCMF_C_GET_BANDLIST`** and 11 2GHz `chanspecs` (zero 5GHz) despite same unit's Android 5GHz success. [Actual firmware-enumeration checkpoint](../checkpoints/MZ600_V064_BRCMFMAC_FIRMWARE_5GHZ_BANDLIST_CHANSPEC_PHYSICAL_PROOF_2026-10-26.md). The physical specification confirms silicon capabilities, but **does not itself identify current firmware country/board-calibration cause**. Compare OEM vs generic firmware/NVRAM read-only before any experimental flash or forced RF setting.



- **Startup blocking path:** pp. **47–52**, **62–70**, **81–89**, **116–119**, **132–134**.
- **Shared Bluetooth/WLAN interactions:** pp. **18, 24, 29–31, 48, 64–66, 70, 81, 84–89, 121, 132–134**.
- **SDIO mode/clock/pin wiring:** pp. **49–52, 76–87**, plus SPI contrast **53–61**; *do not transfer SPI-only boot commands to SDIO*.
- **Firmware and host/device protocol:** pp. **47, 62–63**, with live checks from v026.
- **LPO, TCXO, PMU and internal 1.25V:** pp. **48, 64–70, 116–119, 132–134**.
- **Figures useful later:** Fig. 1 p.3, Fig. 2 p.18, Fig. 3 p.24, Fig. 22 p.65, Fig. 23 p.69, Fig. 24 p.75, Figs. 30–33 pp.133–134.

**Interpretation warning:** the 2016 Cypress cover is a continuation notice. Its visible body retains Broadcom’s 2010 revision and states the part is not recommended for new designs; our task is support for existing hardware, not a new hardware design.
