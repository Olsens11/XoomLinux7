# Ordered roadmap

## G0 — canonical reproducible source and continuity
- [x] Establish XoomLinux7 GitHub repo, strict state/evidence docs, upstream reference.
- [ ] Complete final source/builder parity and source license review.
- [x] Register each machine's distinct SSH public **deploy key** with Write access; real create/delete test branch push passed on Desktop, Pi and Surface.
- [x] Verify local worktrees, GitHub fetch, independent push/delete permissions, and sync all machine worktrees with main.
- [ ] Add deterministic checks and release manifests for every accepted kernel image.

## G1 — validate v014 LIVE-LAB, no flash
- [x] v014 temporary boot, USB protocol, and Broadcom start/stop passed; binary transfer failed and v015 corrective candidate built.
- [x] v015 RAM-only USB and module start/stop/retry transport qualified; F2 timeout persists and has an actionable live-lab reproduction path.
- [ ] Export dated, scrubbed evidence; keep exact raw serial/device information privately.

## G2 — solve BCM4329 SDIO F2
- [ ] Compare driver/firmware/clock and power state against Motorola OEM flow.
- [ ] Test small attributable changes one at a time; no general MMC core hacks without reproducer.
- [ ] Confirm `wlan0`; only then pursue regulatory/per-device MAC and network association.

## G3 — native platform
- [ ] Controlled USB peripheral/host/OTG investigation.
- [ ] Charging/battery power_supply with CPCAP ADC fixes.
- [ ] Bluetooth and audio after core boot stability.
- [ ] Writable root filesystem, boot/install design **after** explicit authorization.

## G4 — useful OS and Windows 95
- [ ] Debian armhf root filesystem and network services.
- [ ] QEMU/alternative x86 Windows 95 emulation feasibility and preservation.
- [ ] NEON Lite instruction pretranslation/caching research kept as separate experiment.

## F2 disciplined path (new 2026-10-24)
- [x] v016 live read-only F2 register instrumentation and physical evidence; F2 still fails.
- [x] Research Motorola complete six-field embedded SDIO setup and Broadcom firmware handshake; identify why v010-v013 do not fully reproduce OEM.
- [ ] Capture raw CCCR and final parsed card capabilities and host timing before any new SDIO capability patch.
- [ ] Compare valid same-device OEM firmware and NVRAM privately.
- [ ] Perform cold/warm baseline and one-change-at-a-time Motorola equivalent with observed effective fields.
- [ ] Qualify IORx bit 2, stable wlan0, regulatory/MAC identity, repeated network operation before declaring fixed.

- [x] Read-only v017 raw CCCR, effective mmc_cccr fields and host ios captured on real replacement MZ600.
- [ ] Produce complete Motorola six-capability equivalent in appropriately scoped modern SDIO initialization, with actual post-override field+timing measurements and no unrelated clock or calibration changes.
- [ ] Separate legacy clock-only control to test 46.15MHz versus conservative rate, if OEM-equivalent test alone cannot isolate failure.

- [x] Full Motorola six-field OEM-equivalent modern MMC override physically tested (v018): parsed fields and SD-HS mode actually corrected, F2 failed twice.
- [x] v019 controlled clock-only comparison: same OEM six-field patch, cap SDMMC2 at 25MHz, measure effective speed and F2 state.
- [ ] If still failing, prioritize firmware CPU/startup, 32k reference, and private same-device NVRAM/firmware provenance before more arbitrary quirk changes.

- [x] v019 controlled clock-only comparison physically tested; effective host clock 25,000,000Hz, F2 still timed out on two trials.
- [ ] Prioritize read-only BCM4329 firmware CPU/SDPCM startup checks and exact same-device OEM firmware + NVRAM provenance; no further MMC tweaks without specific evidence.

## On-demand SDIO test architecture
- [x] Identify actual Wi-Fi MMC2 platform device `c8000200.mmc` and Linux driver bind/unbind surfaces via existing read-only USB SDIO tool.
- [ ] Add board-scoped runtime capability profile and safe USB MMC2-only reinit controls, **requiring one further experimental temporary-boot diagnostic candidate**.
- [ ] Validate no-change controller rebind, clean removal/re-enumeration, effective capability changes, rollback and no impact to eMMC/USB; do not mark available until real hardware testing passes.
- [ ] Then vary capability, clock, reset, matched firmware/NVRAM one at a time without whole-kernel reboot, with cold-boot control runs.

## v020 on-demand controller integration
- [x] Implement and test root-only Stingray BCM4329 SDIO AUTO/MOTOROLA runtime profile.
- [x] Implement and test MMC2_STATUS, MMC2_PROFILE, MMC2_REINIT with USB command allowlists.
- [x] Demonstrate AUTO to MOTOROLA to AUTO card removal/re-enumeration, verified effective capabilities, with NO kernel reboot.
- [x] Refuse reinit when Broadcom drivers loaded; host waits for terminal response.
- [ ] Test recovery under deliberately failed bind/re-enumeration and compare card reinit to actual chip power cycle.
- [ ] Extend independent clock profile safely after no-change controls; continue firmware CPU/SDPCM and matched OEM calibration research.

- [ ] Investigate v020 post-test USB/Android/Linux mode transitions and fresh Linux uptime; establish whether the restart was kernel crash, power event, external tooling, or physical interaction. Preserve accurate logs and avoid causal guesses.
- [ ] Perform an independently monitored stability/soak and repeated on-demand MMC2 reinit test before promoting v020 as a long-duration stable environment.

## Evidence-based F2 isolation
- [x] Compare preserved OEM BCM4329 calibration and generic NVRAM values without exposing original MAC: all 53 shared values matched.
- [x] Test standard/old Motorola-era firmware under AUTO and Motorola profile with unchanged NVRAM: F2 still -62 in all three conditions.
- [x] Build exact SHA-verified read-only kernel clock-provider observer as replaceable v021 module; untouched kernel source restored after build.
- [ ] Test v021 observer through authorized RAM-only workflow (current remote upload blocked; not yet physically executed).
- [ ] Compare actual Tegra PMC 32.768kHz clock gating/clock-rate and OEM 100/100/200ms U4/U2 GPIO reset sequence using controlled MMC2 on-demand trials.
- [ ] Confirm firmware chip-CPU execution and true F2 readiness (not just firmware byte readback); restore original MAC provenance before RF activity.

## New datasheet-controlled F2 gate (Section 11, 2026-10-24)
- [x] Review entire BCM4329 Rev *F 149-page datasheet, SDIO Section 11 and reset/power/clock cross-references.
- [ ] Verify **AUTO/default timing=0 with actual SDIO data clock <=25MHz**, leaving firmware/NVRAM and reset profile unchanged. v019 at 25MHz high-speed does not satisfy this control.
- [ ] Check 110ms SDIO access delay measured from settled 1.25V VDDC and VDDIO, not only from software post-power-on delay; inspect 10-100k SDIO CMD/DAT pulls.
- [ ] Read Tegra PMC LPO clock enable/rate and check power regulator/reset sequence, preserving distinct software/physical observations.

- [x] Physically test SDIO Section 11 Table 3 AUTO/legacy at **measured 25 MHz**, unchanged firmware/NVRAM, three on-demand MMC2 trials: still F2 -62. Do not repeat this as an untested hypothesis.
- [ ] Diagnose WLAN Cortex-M3 firmware startup and measured LPO clock provider, chip core reset/power, GPIO U4/U2 control and settled VDDC min 110ms requirement. v021 LPO observer needs authorized hardware test.
- [ ] Verify performance and true cold boot after any verified functional fix; avoid declaring driver-loader success equal to Wi-Fi success.

- [x] Physically verify pwrseq clock software state using v021 RAM-loaded observer: rate=32768, enabled=1; F2 still -62.
- [ ] Confirm actual WLAN LPO electrical delivery, U4/U2 power/reset timing relative to settled VDDC/VDDIO and 110ms datasheet minimum.
- [ ] Instrument BCM4329 Cortex-M3 startup/SDPCM mailbox to isolate absent F2 readiness.

## Audit inherited Linux / Motorola assumptions
- [x] Physically prove MMC host default \`ios.power_delay_ms=10\`; separate \`wifi-pwrseq\` 300ms runs after reset release.
- [x] Build v025 by adding only MMC2 host pre-reset \`post-power-on-delay-ms=100\`; physical effective 100ms, three tests still F2 timeout -62.
- [x] Verify read-only U2/U4/U5 GPIO, MMC2 vmmc/vqmmc, pwrseq clock and host delay via dynamic v023/v024 modules. Checkpoint their software-not-electrical scope.
- [ ] Establish whether \`regulator-boot-on\` holds U4 on throughout host rebind; instrument driver sequencing/enable counts and GPIO latch transitions, staying read-only.
- [ ] Audit differences between original OEM 100/100/200ms power/reset sequence and mainline regulator/pwrseq ownership, especially initial boot order and real supply settling.
- [ ] Audit \`brcmf_chip_cm3_set_active\` and firmware startup/mailbox before F2 ready, refusing to treat release-from-reset as firmware-execution confirmation.
- [ ] Correct incorrect USB SDIO debug path (\`mmc-pwrseq-simple\` vs actual \`pwrseq_simple\`) in future diagnostic code only after documenting source/fix and tests.

## Virtual provenance lab
- [x] Independently inspect real compiled v025 DTB using Cortex-A9 QEMU ARM user-mode program.
- [x] Verify exact boot/CPIO image firmware, NVRAM and module entries and SHA256.
- [x] Compare Python and ARM model NVRAM transformations byte-for-byte: 672 bytes identical.
- [x] Pass seven deliberate fault-injection controls: wrong node, incorrect values, altered boot/NVRAM.
- [ ] Trace actual physical firmware request path, returned digest, NVRAM payload and platform MAC provenance without exposing identifiers.
- [ ] Timestamp actual MMC power sequencing, U4/U2 controls and clock voting to compare against source.
- [ ] Consider full Tegra20 and BCM4329 device modeling only where needed to answer questions userspace emulation cannot.

## Runtime provenance findings
- [x] Compile/rebuild v026 and physically verify actual requested firmware/NVRAM paths with monotonic kernel timestamps; first request board-specific then generic fallback.
- [x] Compare firmware 253748B, source NVRAM 1550B and packed NVRAM 672B CRC32 to virtual reference: all match.
- [x] Check platform-provided MAC callback without printing identifier: unavailable in current generic configuration; OTP/other sources and causality unresolved.
- [ ] Prove whether Tegra U4 WL power is actually cycled on MMC2 rebind and whether boot-on regulator or shared rail prevents it. Observe U2 reset command sequence with timestamped core traces, not just steady states.
- [ ] Trace internal Broadcom Cortex-M3/PMU execution, mailbox and real F2 response; do not conflate firmware RAM readback with execution.
- [ ] Find device-specific MAC provenance from correct replacement hardware without copying another Xoom MAC.

## BCM4329 full-datasheet compliance and power/clock audit
- [x] Make full 149-page linked datasheet index and 36-row source/hardware requirement audit with cross-subsystem fault tree.
- [x] Validate 31 static source + actual v025 DTB assertions: sole direct failure = source clock above 25MHz legacy limit; physical v025 unchanged/pass clock but F2 fails.
- [x] Run v027 RAM-loaded read-only dual WLAN/BT GPIO snapshot: U2/U4 high outputs; BT I7/U0/U1/U6 GPIO direction -22 (no trustworthy BT level), F2 still -62.
- [ ] Resolve U4/I7 physical logic using read-only Tegra pinmux and regulator owner APIs; inspect Bluetooth serdev binding and normal-ref vs LPO clock association.
- [ ] Verify complete internal PMU/resource/CLK_CSR/Cortex-M3 startup before F2, under genuine understood power-state transitions.
- [ ] Reconcile canonical DTS max-frequency and assigned-clock-rates with tested 25MHz legacy control, preserving rollback and no unqualified changes.
- [ ] Audit all-state SDIO CMD/DAT pullups, identification <=400kHz, reference oscillator, true VDDC settling, and full Motorola six-field SDIO override.
- [ ] Confirm electrical delivery and timing only if controller, pinmux, PMU, source and emulator checks cannot disambiguate.

## Whole BCM4329 physical-chip coordinator (following datasheet/OEM discovery)
- [x] Identify OEM shared U4 enable reference counting and BT I7-low rfkill policy, separate reset U0/U2.
- [x] Compare current Linux 7 fixed regulator + hci_bcm GPIO ownership and note generic pwrseq framework is compiled off and not integrated with consumers.
- [x] Create offline shared OR/power-refcount safety model; 20 unit tests passed, no hardware actions.
- [ ] Read-only determine actual BT serdev binding, I7/U0 pinmux, real resource state and U4 controller/clock votes.
- [ ] Build and compile a proper board-specific shared pwrseq provider and two consumer hooks *without duplicate GPIO ownership*; keep standard WLAN/BT protocol drivers.
- [ ] Validate temporary-boot callbacks, timing, on-chip PMU behavior and F2 after a controlled one-variable A/B against v025.
- [ ] Do not claim cold POR or a Wi-Fi fix until physical state and actual F2 readiness demonstrate it.

## Shared BCM4329 Linux provider implementation
- [x] Compile board-specific source prototype into 32-bit ARM object without direct GPIO ownership.
- [ ] Build a separate kernel configuration with CONFIG_POWER_SEQUENCING and link/test provider registration.
- [ ] Integrate both MMC and Bluetooth target consumers and board binding; reconcile existing GPIO and regulator votes without overlap.
- [ ] Validate I7/U0 pinmux ownership and a passive OEM-equivalent Bluetooth state, then time-stamp power sequencing.
- [ ] Keep temporary v025 boot and no partition flashing until full source/integration and physical testing qualifies a change.

## Next after v028/v029 shared-chip compile-only milestone
- [x] Direct read-only Tegra GPIO CNF/OE/OUT/IN test, no reset or GPIO writes; resolved direction=-22 root cause.
- [x] Linux 7 POWER_SEQUENCING core + Motorola shared-resource provider compile as ARM objects in isolated output.
- [x] Disabled DTS reference node compiles and resolves shared-supply and LPO clock; no active power change.
- [ ] Verify BT serdev driver binding and Tegra pinmux register selection independent of GPIO CNF.
- [ ] Design and compile a consumer integration that propagates power sequencing errors; migrate source ownership of U4/I7/U0/U2 without duplicate GPIO requests.
- [ ] Avoid experimental boot until a verified 25MHz legacy MMC profile, source/DTB match, known v025 rollback, and no conflicting clock/reset control.
- [ ] Establish actual internal PMU resource progress, Cortex-M3 execution, chip-derived ready response, and only then conclude root cause.

## v030 next gates after the compile-only Bluetooth shared U4 candidate
- [x] Board-gate a dedicated Bluetooth shared-U4 regulator vote; do not hijack the actual vbat/vddio supplies or request GPIO U4 twice.
- [x] Preserve OEM I7 passive LOW policy and assert active-low U0 from initial GPIO acquisition (avoid generic reset-release glitch).
- [x] Include monotonic command breadcrumbs; patch applies and ARM object compiles from exact SHA256-pinned Linux 7 source; disabled BT DT fixture and 21 static checks pass.
- [ ] Determine BT serdev driver binding, pinmux ownership and normal reference-clock versus LPO roles before allowing a powered Bluetooth test.
- [ ] Review devicetree binding/schema for new Motorola opt-in + shared-supply properties and prepare explicit 25 MHz legacy SDIO qualified boot variant/rollback.
- [ ] Test actual shared U4 regulator vote timestamps and chip PMU state via safe temporary boot only after independent source/DTB validation; do not infer full POR from software votes.
- [ ] Continue independent WLAN Cortex-M3 execution and SDIO Function 2 readiness diagnosis; a dormant BT consumer cannot alone fix F2 -62.

## Next gates from v031/v032 hardware evidence
- [x] Confirm live serdev child registration AND actual Bluetooth binding: child exists but \`DRIVER=NONE\` on v025.
- [x] Confirm actual live Bluetooth \`txco\` and Wi-Fi \`ext_clock\` use the same 32768Hz clock handle; mark old BT clock role misleading.
- [x] Build independent, disabled v032 preview with \`clock-names="lpo"\`, retaining shared U4 regulator ref and existing vbat/vddio; 12 checks pass.
- [ ] Inspect board-specific GPIO/pinmux wiring and reset startup behavior for I7 (GMI_WAIT) and U0/U1/U6 (GPIO-only) BEFORE enabling BT HCI driver.
- [ ] Verify actual normal 38.4MHz crystal/reference frequency from same Xoom OEM/PMU and ensure chip-side clock and VDDC POR timing.
- [ ] Implement controlled BT activation over existing USB in a **separate temporary RAM boot image**, with checked source/compiled DTB, qualified 25MHz MMC2, fail-closed regulator/reset state, and v025 rollback.
- [ ] Do not assume BT power coordination will resolve F2 while BT remains unbound; independently test Cortex-M3 firmware execution/PMU/F2 readiness.

## v033 controlled Bluetooth power experiment
- [x] Build and link patched Linux 7 Bluetooth HCI UART and ECC/ECDH/CMAC dependencies.
- [x] Preserve v025 kernel, 25MHz MMC2 and Wi-Fi binaries; add explicit USB BT status/load/power/down/unload commands with fail-closed guards.
- [x] Independent candidate and rollback image SHA checks on Surface and ARM no-NEON init selftest.
- [ ] Boot candidate with fastboot boot only, never flash.
- [ ] Verify UART binding and I7/U0 state on BT_START, then controlled BT_ON, BT_OFF, BT_STOP if safe.
- [ ] Separately diagnose Wi-Fi F2 -62 and chip-side PMU/Cortex-M3 startup.

## Physical v033 result and v034 corrective gate
- [x] Boot v033 on replacement Xoom with temporary fastboot boot and verified v025 fallback, no flash.
- [x] Demonstrate Bluetooth BCM4329B1 UART communication and Linux shared U4 regulator ON/OFF vote and reset sequence under module load/unload.
- [x] Discover that BT_START automatically initializes and powers Bluetooth; USB label claiming passive bind was incorrect.
- [x] Prove USB BT_OFF -19 is caused by HCI ioctl argument passed by pointer rather than device index value (Linux hci_sock_ioctl directly forwards arg to hci_dev_close).
- [x] Check after BT cleanup: Wi-Fi F2 still -62, no wlan0; final modules unloaded and MMC2 bound.
- [ ] Correct freestanding HCI ioctl argument semantics and BT_START startup messaging, package as v034 separate rollbackable candidate before relying on BT_OFF.
- [ ] Find correct Bluetooth BCM4329B1 .hcd firmware in private OEM reference if needed; never commit proprietary binaries or per-device secrets.
- [ ] Continue WLAN Cortex-M3 and chip PMU startup diagnosis; shared U4 vote is not proven internal POR.

## v034 physical result and next chip-side issues
- [x] Correct HCI up/down argument: Linux expects HCI device index by value, not a pointer to int.
- [x] Build and independently verify one-variable v034 temporary boot image, preserving v033 kernel and all modules/firmware/DTB.
- [x] Physically fastboot boot replacement Xoom, no flash. BT_START automatically initializes chip and reads BCM4329B1; corrected BT_OFF returns 0, vs v033 -19.
- [x] BT_STOP unloads six modules, logs reset assert and U4 vote off; MMC2 bound AUTO and USB responsive.
- [ ] Distinguish HCI device-down completion from regulator vote release on module unload: current timestamps do not prove U4 toggles at BT_OFF.
- [ ] Assess missing OEM Bluetooth HCD patch, preserve private proprietary binaries.
- [ ] Investigate WLAN Cortex-M3 execution, PMU clocks and F2 ready -62 independently.
