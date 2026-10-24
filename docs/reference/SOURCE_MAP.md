# Source, builder, machine and artifact map (2026-10-24 import)

| Location | What lives there | Authority |
| --- | --- | --- |
| `https://github.com/xoom-linux/linux` | Contributors' original kernel/DTS, pinned to `2404d273...` | Upstream historical baseline |
| `src/board/` | Our Stingray derived and USB-diagnostic DTS | Board-specific experiment source |
| `src/diag-init/` | Freestanding PID1 source snapshots v03-v14 | Diagnostic experiments, v013 physically proven |
| `scripts/history/` | Build/packaging/setup/one-shot transfer recipes imported by version | Historical reproducibility, not all scripts current |
| `configs/` | Kernel config snapshot and MAC-free NVRAM text | Reproducibility inputs, never real calibration |
| `docs/checkpoints/` | Verifiable experiment chronology/status | Interpreted public summary |
| `evidence/` | Curated manifest and reviewed public outputs | Evidence only at recorded qualification level |
| Desktop WSL `/home/xoomdev/xoom-linux-rom/` | Actual extracted kernel build trees, toolchain, 12 versioned init files | Local build/reference files |
| Desktop Windows `C:\Users\olsen\XoomLinux\Phase1\` | 112 historical build/creation/package scripts, technical notes | Primary script archive |
| Surface `C:\Users\olsen\xoom-linux-rom\downloads\` | Original boot images, USB commands, one-shot test scripts | Private physical test staging |
| Pi `/home/ps2/xoom-phase1/` | Protected recovery project, OEM, TWRP reference | Not XoomLinux7 source; do not modify |
| `https://github.com/Olsens11/xoom-recovery` | Recovery tooling and Wi-Fi precedent | Separate project, read-only reference for this effort |
| `https://github.com/Olsens11/PS-to-VNC` | Development continuity and documentation patterns | Reference only |

Project Git is authoritative for *new changes*. Imported historical files are traceable but may not be byte-identical if line endings were normalized during migration; hashes of final published source establish fresh authority. Never treat an unversioned local `linux-src` extract as immutable upstream.

## Surface host command source
- `scripts/host/surface/Xoom-v14-LiveLab.ps1` — current v014 serial command/upload host-side client (source only; hardware v014 untested).
- `scripts/host/surface/Probe-MZ600-LinuxUSB.ps1` — USB gadget probing.
- `scripts/host/surface/history/Reboot-Verified-MZ600-Linux-V05.ps1` — historical v05 procedure, not an approved current action.
- The Surface's calibration scripts and Android Wi-Fi cycle helper include actual test-device serial identifiers, so they remain private and were **not** published.
