#!/usr/bin/env python3
"""Minimal v07 Wi-Fi diagnostics, preserving verified v06 touch+USB work."""
from pathlib import Path
b=Path('/home/xoomdev/xoom-linux-rom')
dst=b/'phase1-v07'
dst.mkdir(exist_ok=True)
s=(b/'phase1-v06/init.c').read_text()
def rep(a,z):
 global s
 assert s.count(a)==1,(a,s.count(a))
 s=s.replace(a,z,1)
rep('/* Xoom MZ600 phase-1 v06 touch grid and crosshair, USB diagnostics. No libc/NEON.',
    '/* Xoom MZ600 phase-1 v07 native upstream BCM4329 driver diagnostics. No libc/NEON.')
rep('usb_send("XOOM LINUX MZ600 V06 INTERACTIVE GRID TEST\\r\\n");',
    'usb_send("XOOM LINUX MZ600 V07 WIFI SDIO PROBE\\r\\n");')
rep('usb_send("PONG XOOM-LINUX V06\\r\\n");',
    'usb_send("PONG XOOM-LINUX V07\\r\\n");')
rep('usb_send("HELP PING STATUS CPU MEM STORAGE INPUT THERMAL USB LOGS CMDLINE GRID TOUCH TOUCHSTOP REBOOT POWEROFF CANCEL\\r\\n");',
    'usb_send("HELP PING STATUS CPU MEM STORAGE INPUT THERMAL USB LOGS CMDLINE GRID WIFI TOUCH TOUCHSTOP REBOOT POWEROFF CANCEL\\r\\n");')
needle=' else if(equals(cmd,"TOUCH"))touch_start();'
code=r''' else if(equals(cmd,"WIFI")){
   usb_send("=== BCM4329 SDIO LINUX V07 PROBE (NO ASSOCIATION) ===\r\n");
   usb_send("WLAN0 ");
   usb_send(present("/sys/class/net/wlan0")?"PRESENT\r\n":"ABSENT\r\n");
   usb_file("/sys/class/net/wlan0/operstate",80);
   usb_file("/sys/class/net/wlan0/address",80);
   usb_file("/sys/class/net/wlan0/addr_assign_type",80);
   usb_file("/sys/class/net/wlan0/device/uevent",220);
   usb_file("/sys/class/net/wlan0/phy80211/name",80);
   usb_send("MMCHOST2 ");
   usb_send(present("/sys/class/mmc_host/mmc2")?"PRESENT\r\n":"ABSENT\r\n");
   usb_send("NO WPA, NO DHCP, NO SCAN, NO NETWORK CONNECTION\r\n");
 }
 else if(equals(cmd,"TOUCH"))touch_start();'''
rep(needle,code)
(dst/'init.c').write_text(s)
print('V07 MINIMAL USERLAND SOURCE',dst/'init.c','bytes',len(s))
assert '/dev/input/event2' in s and 'grid_cross_paint' in s
assert 'SYS_reboot' in s
