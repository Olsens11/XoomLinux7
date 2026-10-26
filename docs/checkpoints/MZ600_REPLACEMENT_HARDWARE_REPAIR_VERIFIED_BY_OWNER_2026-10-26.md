# Replacement MZ600 hardware correction — DC charging jack and volume button both repaired

**User confirmation: 2026-10-26 around 02:55 EDT.** Applies **only** to the experimental replacement Motorola Xoom MZ600 (not the protected original).

The owner explicitly corrected outdated project assumptions:

- **DC charging jack: PHYSICALLY REPAIRED, now works well**, according to owner. Do not describe it as still broken, or assume charging is dock-only. This is distinct from any older observations of charging issues.
- **Volume button: PHYSICALLY REPAIRED, now works well**, according to owner. Do not describe the button as defective or use a broken Volume Down button as a barrier to recovery.
- The owner says they have **successfully used the physical keys to enter fastboot and recovery themselves**. Manual entry is therefore a known working method and **does not rely on Android `/system`**.
- These are **owner-reported verified practical operations**, not new automated tests performed in this turn. The date and exact sequence of their last successful manual fastboot/recovery boot after the latest p7 Debian flash have not been independently captured in this turn. A final manual demonstration before p8 formatting can be useful, but the outdated claim that physical recovery is blocked by damaged buttons is **false**.

## Impact on Linux7 BigPart installation plan

Previous checkpoints and the original handoff contain historical mentions of defective Volume Down/charging jack; **retain as historical observations, but override them with this correction**. Earlier Linux7 `REBOOT_CMD_RESTART2("bootloader")` **did return to Android instead of fastboot**. That is a *software reboot-mode problem*, **not proof physical bootloader key entry is unavailable**. Do not conflate these two paths.

Latest actual software state, independently physically verified in preceding turn:
1. Replacement p7 persistent Stage-B Linux7/Debian 12 microSD boot: normal boot **PASS**.
2. Internal p7 first 6,645,760 bytes exact Stage-B SHA256 **`b9667187ffe0ff74a6d0f801f300a78012d8242c2e45e34bd35e39c59fc657ba`**, physical read-back **PASS**; full 8MiB p7 SHA `05e62cd6964659984e84ac36a316e6ed023e66b456bf9081e6395f13127276cf`.
3. BigPart p8 `/system` 1GiB remains unformatted; p6 original TWRP retained, **not BigPart aware**; on-device native installer **read-only preflight PASS**, destructive `--install` not run. Current SD installer SHA256 `d597e8b6c1cf7b83126d1db3bc82d726e26e8df61a12c87695da7b5d47a38e43`.
4. Original factory boot p7 backed up privately on Surface and verified; protected original Xoom not touched.

**Next safe procedure:** treat physical key access to fastboot/TWRP as available per owner, optionally physically demonstrate again now that p7 uses Debian; if using stock TWRP, do not format or write enlarged p8 since stock recovery sees old 256MiB GPT; use normal Debian SD-root installer under verified BigPart Linux kernel. Verify exact p8 and SD-root identity once more before any authorized destructive install. Retain all backup and key/USB rescue options. Never downgrade the repaired charging jack or volume button status unless newly observed.

