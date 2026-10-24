#!/usr/bin/env python3
from pathlib import Path
b=Path('/home/xoomdev/xoom-linux-rom')
v=b/'phase1-v09'
v.mkdir(exist_ok=True)
s=(b/'phase1-v08/init.c').read_text()
def rep(a,z):
 global s
 assert s.count(a)==1,(a,s.count(a))
 s=s.replace(a,z,1)
rep('/* Xoom MZ600 phase-1 v08 extended SDIO telemetry, identical WLAN driver. No libc/NEON.',
    '/* Xoom MZ600 phase-1 v09 upstream tracefs BCM4329 firmware diagnostics. No libc/NEON.')
rep('usb_send("XOOM LINUX MZ600 V08 WIFI SDIO EARLY-BOOT DIAGNOSTIC\\r\\n");',
    'usb_send("XOOM LINUX MZ600 V09 STANDARD LINUX BCM4329 TRACE DIAGNOSTIC\\r\\n");')
rep('usb_send("PONG XOOM-LINUX V08\\r\\n");',
    'usb_send("PONG XOOM-LINUX V09\\r\\n");')
rep('usb_send("HELP PING STATUS CPU MEM STORAGE INPUT THERMAL USB LOGS CMDLINE GRID WIFI WIFILOG WIFIDIRS TOUCH TOUCHSTOP REBOOT POWEROFF CANCEL\\r\\n");',
    'usb_send("HELP PING STATUS CPU MEM STORAGE INPUT THERMAL USB LOGS CMDLINE GRID WIFI WIFILOG WIFIDIRS WIFITRACE TOUCH TOUCHSTOP REBOOT POWEROFF CANCEL\\r\\n");')
rep(' else if(equals(cmd,"TOUCH"))touch_start();',
''' else if(equals(cmd,"WIFITRACE")){
   usb_send("=== NATIVE LINUX BRCMFMAC BOOT TRACE (READ ONLY) ===\\r\\n");
   usb_file("/sys/kernel/tracing/trace",22000);
   usb_send("=== END BRCMFMAC BOOT TRACE ===\\r\\n");
 }
 else if(equals(cmd,"TOUCH"))touch_start();''')
rep(' /* RAM-only console log level control; detailed diagnostics remain in kmsg. */',
''' /* Mount upstream tracefs (kernel event tracing) to read early driver activity.
  * This is not a custom radio interface or hardware control. */
 long tr=mountf("tracefs","/sys/kernel/tracing","tracefs",MS_NOSUID|MS_NODEV|MS_NOEXEC);
 msg2(tr<0?"tracefs mount FAILED: ":"tracefs mount OK: ","/sys/kernel/tracing");
 /* RAM-only console log level control; detailed diagnostics remain in kmsg. */''')
(v/'init.c').write_text(s)
print('v09 tracefs diagnostic-only userspace created',len(s),'bytes, no custom driver patch')
