# Reused Xoom MZ600 touchscreen calibration — Linux next UI iteration

Source: Xoom TWRP R21/R22 hardware measurements and Surface tool `C:\Users\olsen\XoomDev\remote-tools\xoom-touch-calibrated-v3.py`, verified against replacement MZ600 Linux v05 (serial 170061C243805617) USB TOUCH capture. **No tablet writes.**

## Raw axis ranges, as measured in original TWRP recovery

- Original (different) MZ600 TWRP: qtouch-touchscreen `/dev/input/event6`; `ABS_MT_POSITION_X` 10..2569, `ABS_MT_POSITION_Y` 15..1614.
- Physical display: 1280x800 landscape. TWRP *theme* layout is 1920x1200; recovery's button index scaled theme x and y by 1280/1920 and 800/1200. Those existing recovery **UI control rectangles should not be imported** into the new custom Linux UI.
- Recovery host injector `xoom-touch-calibrated-v3.py` uses display -> raw: `X=10+round(screenX*(2569-10)/1279)`, `Y=15+round(screenY*(1614-15)/799)`.
- New replacement MZ600 Linux 7.0 ARMHF uses *different driver name and event node*: Atmel maXTouch touchscreen `/dev/input/event2`. Linux v05 read-only capture reported **29** updates, 28 valid XY: x=102..2461, y=113..1558; both within recovery reference ranges.
- Reverse mapping for custom Linux framebuffer UI (raw -> 1280x800): `x=clamp(round((raw_x - 10)*1279/2559),0,1279)`, `y=clamp(round((raw_y - 15)*799/1599),0,799)`.
- Integer-no-float implementation for ARM Cortex-A9: clamp raw coordinate to min/max, then `(uint32_t)(raw-min)*(extent-1)+range/2` divided by range; multiplication safely under 32 bits. Zero NEON/float required.
- Examples from v05 captures: raw (1631,751)->(810,368), (1967,622)->(978,303), (980,361)->(485,173), (2398,113)->(1194,49), (2441,1458)->(1215,721). All 28 valid samples mapped in-bounds.
- Touch state: Linux Atmel emits MT_TRACKING_ID=-1 upon finger release; this is normal **read-only real event data**. Past recovery bug was **synthetic injection of negative tracking ID into the old TWRP input driver**, which caused broken touch-release detection. Never transplant that injection behavior into Linux. Process real MT slot/tracking events per Linux semantics.
- Still required before clickable UI: verify orientation (x left/right, y top/bottom), raw ranges **on replacement actual Linux device** via `EVIOCGABS(ABS_MT_POSITION_X/Y)` to avoid assuming original MZ600 exact calibration applies, and confirm corner touches and rotation. UI should ignore invalid/uninitialized (-1,-1) startup sample and touch release, use `BTN_TOUCH`/MT tracking transitions with finger gesture debouncing.
- Screensaver/reboot/power-off areas should require explicit confirmation and never use a guess/inferred touch; don't activate destructive actions until input mapping is verified.

This is **a prospective calibration**, not yet integrated into currently running Linux v05. It provides a well-grounded baseline for the next userspace build.
