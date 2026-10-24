# Virtual Linux 7 forensic lab — verified phase 1 (2026-10-24)

**Result:** The existing Desktop runs a repeatable **offline** forensic test system against the exact tested v025 boot image. Two 32-bit ARM static programs execute under `qemu-arm -cpu cortex-a9`, while the host auditor independently parses Android boot headers, appended DTB, RAM initramfs, Broadcom file placement and Linux 7 source code. **All positive controls passed; seven deliberate negative tests were detected.** No physical Xoom changes, flashes or boot operations occurred.

## Exact reference image

- v025 image SHA256 `142daec30b6bf0ef52eaaf48456d313263197d9d224f1dfceb20972af48e39fb`
- Embedded compiled DTB SHA256 `517c631bf105db53f1b400c172a450727aed3e767780d493abdc21897d79086d`
- RAM initramfs SHA256 `060664a25adf9fa90136e0e10fd186f41fb397b920698c04d8e89b100a8fcb67`
- `brcmfmac4329-sdio.bin` at `/lib/firmware/brcm/`, 253,748 bytes, SHA256 `d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93`
- `brcmfmac4329-sdio.txt` at `/lib/firmware/brcm/`, 1,550 bytes, SHA256 `a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb`
- The initramfs also contains `/init`, `/wifi/brcmutil.ko`, `/wifi/brcmfmac.ko`, each with valid modes, sizes, SHA256. Raw binaries remain on the development machine outside Git.

## What was independently verified

| Topic | Observation | Limit |
| --- | --- | --- |
| MMC host pre-reset delay | Compiled `/mmc@c8000200/post-power-on-delay-ms = <100>`, ARM/QEMU consumer agrees | Boot-time parser input, not physical voltage timing |
| MMC pwrseq post-reset delay | Separate node `/wifi-pwrseq/post-power-on-delay-ms = <300>` | Not proof reset reached chip |
| Host clock cap | `25,000,000` Hz under the correct MMC node | Physical v025 did measure 25MHz/legacy but that remains separate evidence |
| U4 regulator | `/regulator-wifi` includes `regulator-boot-on`; MMC has `vmmc-supply` phandle | No proof of real off/on transitions |
| Reset/clock | MMC has `mmc-pwrseq`; pwrseq has reset GPIO and `ext_clock` | Not an oscilloscope trace |
| Firmware/name | `brcmfmac4329-sdio.bin` and `.txt` exist at normal Linux loader paths | Actual request path may be overridden by board-specific variant or firmware_path |
| Packed NVRAM | Two **independent** usermode implementations yield byte-identical 672-byte output, SHA256 `401b0b9a7b898519aa3c7403b53eff050ef1e8917fd90483145f59d675ad46ab`; `RAW1` excluded according to kernel firmware.c parser | Kernel's exact in-memory buffer and chip consumption remain unverified |
| Linux consumers | 12 distinct source parser/loader/pwrseq locations found and indexed | Source presence alone is not runtime execution proof |
| Driver sysfs path | `pwrseq_simple` is real name; old diagnostic had incorrectly queried `mmc-pwrseq-simple` | Confirmed diagnostic bug, not proven Wi-Fi root cause |

Negative cases: wrong DTB value, correct data on wrong node, MMC-host/pwrseq property conflation, corrupted boot payload, wrong NVRAM token/length, modified NVRAM contents, and supplied DTB not identical to appended boot-image DTB. Seven fault controls passed; baseline positive also passed. `qemu-arm -strace` independently shows the ARM program opening and reading the real compiled DTB and writing decoded values.

## New or refined conclusions

1. **The v025 files are not obviously misplaced:** the checked DTB fields are structurally valid and the expected firmware/NVRAM entries are physically embedded at their declared paths. Importantly, no new Wi-Fi root cause was discovered by phase 1.
2. Our own test instrumentation had an actual **wrong sysfs path**, validating the concern about inherited assumptions. See `src/diag-init/phase1-v20/init.c` and `drivers/mmc/core/pwrseq_simple.c` (actual registered name `pwrseq_simple`).
3. **The generic MAC-free NVRAM isn't yet fully cleared.** `firmware.c` only adds a platform-provided MAC when `eth_platform_get_mac_address()` succeeds. The original OEM NVRAM includes a per-device MAC; the generic test variant does not. The driver's fallback identity at runtime remains a candidate to verify, without publishing or hardcoding any MAC.
4. **Alternative firmware request path remains an unchecked runtime assumption.** In `brcmfmac/firmware.c` firmware requests can try board-qualified file names or a module-level firmware directory override. A correct initramfs file name does not alone prove the firmware loader selected that file. The same applies to USB RAM overrides.
5. **`regulator-boot-on` may prevent meaningful full power cycling.** The virtual lab confirms the property exists in the compiled DTB but cannot show whether power physically cycled during the real on-demand MMC2 rebind.
6. The virtual NVRAM simulator is separate test code derived from kernel source—not literally the Linux 7 firmware parser compiled into a VM kernel. Its byte-identical agreement with a Python model provides stronger format evidence, but we should not mislabel this as kernel execution.

## Implementation and operation

- Public sources in `tools/forensics/audit.py`, `arm_fdt_consumer.c`, `arm_nvram_consumer.c`, `test_lab.py`, `run_lab.sh`; developer usage in [forensic README](../../tools/forensics/README.md).
- Run once on Desktop: `bash /home/xoomdev/projects/XoomLinux7/tools/forensics/run_lab.sh`.
- A machine-local private file `/home/xoomdev/xoom-linux-rom/forensic-lab/config.env` identifies the v025 artifacts; it is not committed to Git. Results live under `/home/xoomdev/xoom-linux-rom/forensic-lab/output`.
- No private OEM firmware, MAC address, ARM executable or extracted raw payload is committed. The public repo includes code, sanitized findings and hashes only.
- Full-system `qemu-system-arm` is not installed and no accurate Tegra20/BCM4329 virtual machine exists yet. Running the v025 kernel under generic `virt` would not reproduce board-specific peripherals.

## Recommended phase 2: prove *runtime consumption*

The best next instrumented **physical** experiment is a RAM-loaded, read-only kernel trace of:
- selected `request_firmware` path and SHA-256 (or limited digests) of the exact returned payload, including board-specific fallback and custom `firmware_path`;
- actual packed NVRAM length/token/digest and MAC provenance, without printing the MAC;
- `mmc_power_up`, regulator U4 reference counts, U2 reset transitions, clock enable, first SDIO CMD52, ARM Cortex-M3 release and F2 ready polling, all with monotonic timestamps.
Then compare physical runtime observations with this virtual artifact baseline. Keep electrical arrival and internal VDDC settling explicitly **unverified** until measurable; no VM can infer those from Linux calls alone.

**Wi-Fi remains unresolved** on physical MZ600: SDIO F2 ready bit absent (IORx `02`), `-62` timeout and no `wlan0`. This lab is a testing capability, not a repair.
