# v026 runtime firmware/NVRAM provenance — experimental branch

**Status: SOURCE CANDIDATE ONLY. Not built, uploaded, or run on the Xoom.**
The development machine's remote Linux execution was blocked in this session.
Do not flash this code or treat it as a working Wi-Fi fix.

Branch: `lab/runtime-provenance-v026`. Baseline: main at the end of the
v1 virtual provenance lab, commit `1e66ee6`.

## Goal and scope

Answer the specific runtime questions left open by
[virtual lab v1](../../docs/research/VIRTUAL_FORENSIC_LAB_V1_2026-10-24.md):

1. Which of the board-specific or generic `request_firmware` paths was
   actually attempted and returned content?
2. What were the length and CRC32 of firmware and NVRAM bytes returned
   by the firmware loader?
3. What length and CRC32 did the Linux 7 NVRAM parser actually produce
   immediately before passing it to the Broadcom driver?
4. Was a MAC address available through the platform callback? Log only
   **availability**, never the MAC address or NVRAM content.
5. What are the relative monotonic timestamps at F2 enable attempt
   and completion, alongside the existing read-only v024 GPIO/regulator
   and v021 clock diagnostics?

## Initial implementation

`scripts/experiments/v026-build-runtime-provenance.py` prepares a temporary
two-file patch to the *existing local kernel build tree*:
`brcmfmac/firmware.c` and `brcmfmac/sdio.c`, using the already physically
tested `v024-gpio-regulator-readonly.patch` as baseline.

The builder requires the exact original `sdio.c` SHA256, rejects dirty
kernel source, checks every expected source anchor, and restores both files
byte-for-byte in `finally`. The intended result is a module that can be
uploaded through the existing USB RAM transport. **Its build and runtime
behavior have not been verified.** A source review and compiler check are
required before any physical test; do not assume this prototype compiles.

Diagnostic lines use `XOOM_PROV026` and `ktime_get_ns()`. The included
CRC32 routine is intended to match the existing USB lab polynomial.
CRC32 is a **non-cryptographic fingerprint**, not a secure checksum.
The Python virtual lab's SHA256 applies to file artifacts, so compare
CRC-to-CRC on both sides or explicitly compute the CRC32 of the reference
source using the same convention—do not compare CRC32 with SHA256.

### Evidence boundaries

| Metric | Can v026 establish? |
| --- | --- |
| Synchronous firmware filename actually returned by loader | Intended: yes, if hook passes source audit |
| Asynchronous first-request file path attempted and content returned | Intended: yes, by tracking the request context |
| Kernel NVRAM packed data length and CRC32 | Intended: yes |
| Platform MAC availability | Intended: yes/no, no identifier |
| Cortex-M3 actually executed firmware | **No** |
| True Tegra U4 regulator transition during MMC2 rebind | **No**, module loads afterward |
| Actual arrival order of electrical signals at BCM4329 | **No** |

The pending **power-sequence event timeline** needs a separate
always-loaded kernel tracepoint or scoped instrumentation in MMC/pwrseq/
regulator drivers, because loading `brcmfmac.ko` *after* MMC2 enumeration
cannot record prior events. Do not overstate the reach of v026.

## Pending qualification checklist

- [ ] Run Python syntax and source-anchor verification with the **real**
  Linux 7 `firmware.c` and clean `sdio.c`.
- [ ] Compile ARMv7 kernel module, check exported symbols and no accidental
  unreferenced-function/format-string warnings.
- [ ] Confirm original kernel source SHA256 restored after build.
- [ ] SHA256-verify the candidate before moving it to Surface.
- [ ] Run one physical USB RAM upload only after all checks pass;
  `WIFI_START` should add `XOOM_PROV026` logs even if F2 still returns -62.
- [ ] Confirm firmware file path and CRC32 against exact real reference
  artifact, and NVRAM packed CRC32 against v1 virtual model.
- [ ] Stop/unload module and check MMC2 state. Never write partitions.
- [ ] Publish a physical checkpoint only for actually observed measurements.

**Current physical state (last verified):** v025 temporary RAM boot, MMC2
bound, profile AUTO, Broadcom modules unloaded, Function 2 unresolved.

No source or user private MAC, EEPROM, original OEM binary, or calibration
payload belongs in this public branch.
