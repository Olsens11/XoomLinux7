# XoomLinux7 Forensic Virtual Lab v1

**Scope:** offline analysis of the *actual* v025 temporary-boot Android image; runs on the existing Desktop WSL Ubuntu 22.04. This is not a working Xoom system VM, hardware simulator or Wi-Fi fix. **Never flashes or connects to the physical tablet.**

## One command

```bash
bash /home/xoomdev/projects/XoomLinux7/tools/forensics/run_lab.sh
```

The machine-local file `/home/xoomdev/xoom-linux-rom/forensic-lab/config.env` supplies XOOM_ART on the Desktop. It is private and outside Git. Override `XOOM_ART`, `XOOM_IMAGE`, `XOOM_DTB`, `XOOM_KERNEL`, `XOOM_BUILD`, `XOOM_CROSS`, or `XOOM_OUT` as required. The v1 default deliberately **fails closed** unless the selected boot image has SHA-256 `142daec30b6bf0ef52eaaf48456d313263197d9d224f1dfceb20972af48e39fb`. A new target needs an explicit audited expectation update, not a silent substitution.

Dependencies already on Desktop: Python 3, `dtc`/`fdtget`/`fdtput`, `qemu-arm`, `sha256sum`, Tegra2-compatible ARM cross compiler from `/home/xoomdev/xoom-linux-rom/toolchains`. No `qemu-system-arm` or BCM4329/Tegra hardware emulation required for this phase.

## Actual flow

1. Verify the exact legacy Android boot image SHA256, boot header SHA1, kernel and initramfs boundaries and appended FDT identity.
2. Cross-compile `arm_fdt_consumer.c` as **32-bit ARMv7 static ELF**; run under `qemu-arm -cpu cortex-a9`. Decode the real DTB with a separate ARM implementation (not the host's `fdtget`) and assert MMC host 100ms pre-reset delay, pwrseq 300ms post-reset delay, 25MHz SDIO maximum and regulator/pwrseq phandles.
3. Decompress/parse the **actual** embedded gzip/newc initramfs without extracting files into the repository. Check firmware, NVRAM, module and PID1 paths, file modes, sizes and SHA256; follow **12 kernel source consumer entry points** (property parsing, power sequence, Broadcom firmware allocation and NVRAM transformation).
4. Convert the embedded MAC-free, OEM-derived generic NVRAM text with independent Python and ARM/QEMU parsers into padded NUL-separated key/value data plus Broadcom length token. Compare the outputs **byte-for-byte**. In this v025 reference both produce 672 bytes and SHA256 `401b0b9a7b898519aa3c7403b53eff050ef1e8917fd90483145f59d675ad46ab`. Both intentionally exclude the `RAW1` record per the Linux driver's parser.
5. Run seven negative fault controls: wrong value, correct property on wrong node, conflated host/pwrseq delays, corrupted Android payload, NVRAM pack/token control, synthetic NVRAM mutation, compiled-DTB vs embedded-image mismatch.

Generated JSON and private raw derived data are stored **outside the Git repository** in `/home/xoomdev/xoom-linux-rom/forensic-lab/output`. Do **not** commit private firmware, live device MACs, other original OEM binaries, ARM build executables, or extracted blobs to this public source repo.

## Inspect ARM syscalls or debug virtually

```bash
source /home/xoomdev/xoom-linux-rom/forensic-lab/config.env
qemu-arm -cpu cortex-a9 -strace /home/xoomdev/xoom-linux-rom/forensic-lab/output/arm_fdt_consumer \
 "$XOOM_ART/tegra20-motorola-stingray-usbdiag.dtb" 100 300 25000000
```

The `-strace` output shows ARM guest `openat`, `read`, `close`, and `write` operations and can identify which file was consumed. QEMU `-g` can open a remote GDB stub if an ARM debugger is installed. These trace **the small ARM consumers**, not the complete v025 Linux kernel or BCM4329.

## Evidence boundaries and next phases

| Question | Current evidence |
| --- | --- |
| Was v025's compiled MMC host property placed and encoded correctly? | YES: host parser and separate ARM/QEMU parser agree |
| Was the pwrseq delay separately placed? | YES, 300ms on different node |
| Was the intended firmware bundled? | YES: `/lib/firmware/brcm/brcmfmac4329-sdio.bin`, size 253748; not proof of runtime selection |
| Was the NVRAM converted/aligned consistently? | YES in TWO INDEPENDENT MODELS; both match the 672-byte *size* observed on tablet |
| Does the running kernel actually load these bytes, possibly via board-specific fallback/override? | STILL NEEDS RUNTIME TRACE |
| Does Linux supply a correct per-device MAC when generic NVRAM omits macaddr? | STILL NEEDS RUNTIME TRACE; do not hardcode an identifier |
| Does `regulator-boot-on` prevent actual U4 power cycling? | NOT ESTABLISHED |
| Do electrical events reach BCM4329, and in order? | NOT ESTABLISHED BY A VM |
| Is F2 ready and wlan0 working? | NO: real hardware still -62/absent |

See [phase-1 findings](../../docs/research/VIRTUAL_FORENSIC_LAB_V1_2026-10-24.md), [Motorola source audit](../../docs/research/MOTOROLA_BCM4329_F2_SOURCE_AUDIT.md) and [v025 physical checkpoint](../../docs/checkpoints/V025_PRE_RESET_100MS_PHYSICAL_2026-10-24.md). The next phase should add narrow kernel live traces of the **actual firmware request path/returned data hash, NVRAM packed byte hash and MAC provenance**, plus timestamped MMC2/pwrseq/U4/U2 events. Comparisons against this virtual reference can then flag assumptions that looked right in source but differed on hardware.
