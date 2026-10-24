# Iterative experimental protocol — BCM4329 Function 2

Each experiment gets a numbered vNN checkpoint, branch/worktree, a single falsifiable hypothesis, exact changed source/build SHA, matched DUT role, host/module/image hash, before/after readings, outcome, and rollback. The preferred v015 diagnostic system remains temporary-boot-only; never flash recovery/Android.

## Zero: evidence/measurement gates

- Verify target is the replacement MZ600; USB v015 STATUS/PING, image hash, `wlan0` absent and modules unloaded before loading a new module.
- Record 3 or more consecutive **baseline** v016 F2 attempts on the same firmware/NVRAM, including IOEx/IORx and clockcsr pre/post; note ambient conditions and uptime. Cold-boot repeats must be distinguished from module hot-retries because powering the chip may differ.
- Capture actual raw CCCR bytes: revision, CAPS, POWER, SPEED; final parsed six `mmc_cccr` fields; host `ios.clock`, `timing`, `bus_width`, `signal_voltage`; compare with Motorola values. **Next read-only instrumented module recommended before changing kernel**.
- Confirm firmware binary & generic NVRAM CRC, names and provenance. Keep per-device calibration private.

## One: OEM capability pathway — a real counterfactual

- Capture before/after parsed fields and show precisely which v010/v011/v013 overrides survived Linux's MMC initialization.
- Implement Motorola six-field equivalent at the **correct phase** of modern SDIO initialization, board/chip scoped, as a separate temporarily-bootable kernel variant. Do not replace unrelated MMC behavior.
- Run no-change control vs six-field candidate with otherwise identical firmware/NVRAM and host clocks; inspect F2 bit and driver outcomes. Verify all six effective values at runtime; a printed “quirk applied” is insufficient.
- If F2 ready passes, continue to firmware handshake and wlan0; otherwise preserve negative test and revert.

## Two: firmware-boot verification

- Read/check CPU core activation status, reset vector and SDPCM mailbox before/after firmware activation; use documented safe, read-only Broadcom backplane registers. Be cautious: arbitrary legacy register addresses may change behavior or trigger bus faults.
- Compare Linux 7 with historically working `dhd_sdio.c` sequence, correct firmware provenance, and corresponding private same-device NVRAM. Do not interpret a transfer CRC alone as firmware running.
- Use RAM-only module and firmware uploads to vary ONE condition at a time; record SHA+CRC per candidate.

## Three: power, 32k reference and MMC

- Compare OEM 100/100/200 ms power/reset flow with actual modern pwrseq/regulator/log/GPIO readings.
- Validate chip/host clock, reference input, voltage and SDMMC2 timing against proven recovery on the SAME physical Xoom where possible.
- Only test scoped timing variation with rollback; no permanent mmc-core workaround until evidence supports it.

## Stopping and promotion rules

- No universalizing from one warm reload. Stop if COM9 dies, kernel hangs, power is unsafe, error changes unexpectedly or fallback cannot be restored.
- Do not mark Wi-Fi “fixed” on `IORx==0x06` alone: demand F2 return 0 and stable wlan0, then correct per-device identity/regulation and safe connectivity.
- Record clean cold boot and at least three repeat successes of intended feature before stable acceptance.
- Every conclusion must distinguish measured facts, source-derived deductions and untested hypotheses.
