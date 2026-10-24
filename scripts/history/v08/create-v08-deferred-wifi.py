#!/usr/bin/env python3
"""v08: module-driven deferred Wi-Fi probe; unmodified v06 touchscreen infrastructure."""
from pathlib import Path
b=Path('/home/xoomdev/xoom-linux-rom')
s=(b/'phase1-v07/init.c').read_text()
dst=b/'phase1-v08';dst.mkdir(exist_ok=True)
def r(a,z):
 global s
 assert s.count(a)==1,(a,s.count(a),a[:80])
 s=s.replace(a,z,1)
r('/* Xoom MZ600 phase-1 v07 native upstream BCM4329 driver diagnostics. No libc/NEON.',
  '/* Xoom MZ600 phase-1 v08 deferred upstream BCM4329 driver with USB logging. No libc/NEON.')
r('#define SYS_syslog 103','#define SYS_syslog 103\n#define SYS_finit_module 379')
r('usb_send("XOOM LINUX MZ600 V07 WIFI SDIO PROBE\\r\\n");',
  'usb_send("XOOM LINUX MZ600 V08 WIFI ON-DEMAND PROBE\\r\\n");')
r('usb_send("PONG XOOM-LINUX V07\\r\\n");',
  'usb_send("PONG XOOM-LINUX V08\\r\\n");')
r('usb_send("HELP PING STATUS CPU MEM STORAGE INPUT THERMAL USB LOGS CMDLINE GRID WIFI TOUCH TOUCHSTOP REBOOT POWEROFF CANCEL\\r\\n");',
  'usb_send("HELP PING STATUS CPU MEM STORAGE INPUT THERMAL USB LOGS CMDLINE GRID WIFI WIFI_START WIFILOG TOUCH TOUCHSTOP REBOOT POWEROFF CANCEL\\r\\n");')
insert=r'''
/* Explicit user-triggered firmware probe. No association/scan/DHCP.
 * Kernel firmware and MAC-free NVRAM already embedded as CONFIG_EXTRA_FIRMWARE.
 * The SDIO module's init routine runs only when host sends WIFI_START. */
static int wifi_state=0;
static long wifi_errno=0;
static void wifi_start(void){
 if(wifi_state!=0){
   usb_send("WIFI_START ALREADY ATTEMPTED; STATE ");send_int(wifi_state);
   usb_send(" KERNEL_ERRNO ");send_int((int32_t)wifi_errno);usb_send("\r\n");return;
 }
 wifi_state=1;
 usb_send("WIFI_START EXECUTING: load upstream brcmfmac.ko only\r\n");
 echo("xoom-wifi: user requested deferred brcmfmac module load\n");
 long fd=openf("/wifi/brcmfmac.ko",O_RDONLY);
 if(fd<0){
   wifi_state=-1;wifi_errno=-fd;
   usb_send("WIFI_START ERROR OPEN MODULE errno=");send_int((int32_t)wifi_errno);usb_send("\r\n");return;
 }
 long rc=sc6(SYS_finit_module,fd,(long)"",0,0,0,0);
 closef(fd);
 wifi_errno=(rc<0)?-rc:0;
 wifi_state=(rc<0)?-2:2;
 usb_send("WIFI_START FINIT_MODULE RESULT ");send_int((int32_t)rc);
 usb_send(" (0=loaded; network interface may appear asynchronously)\r\n");
 echo("xoom-wifi: module load returned\n");
}
static int log_has(const char *line,int n,const char *needle){
 int m=(int)slen(needle);
 for(int i=0;i+m<=n;i++){
   int k=0;
   for(;k<m&&line[i+k]==needle[k];k++){}
   if(k==m)return 1;
 }
 return 0;
}
static void usb_wifi_log(void){
 static char all[65536];
 long n=sc6(SYS_syslog,3,(long)all,sizeof(all)-1,0,0,0);
 if(n<=0){usb_send("WIFILOG KERNEL RING UNAVAILABLE\r\n");return;}
 usb_send("=== FILTERED KERNEL LOG: BRCM, SDIO, FIRMWARE, I2C, TOUCH ===\r\n");
 int lines=0;
 for(long i=0;i<n;){
   long e=i;
   while(e<n&&all[e]!='\n')e++;
   long len=e-i;
   if(len>0&&len<250){
     const char *p=all+i;
     if(log_has(p,(int)len,"brcm")||log_has(p,(int)len,"mmc")||
        log_has(p,(int)len,"sdio")||log_has(p,(int)len,"firmware")||
        log_has(p,(int)len,"atmel")||log_has(p,(int)len,"maxtouch")||
        log_has(p,(int)len,"i2c")||log_has(p,(int)len,"xoom-wifi")){
       char line[256];
       for(int j=0;j<(int)len;j++)line[j]=p[j];
       line[len]=0;usb_send(line);usb_send("\r\n");lines++;
     }
   }
   i=e+1;
 }
 usb_send("=== FILTERED MATCHING LINES ");send_int(lines);usb_send(" ===\r\n");
}
'''
r('static void usb_command(const char *cmd){',insert+'\nstatic void usb_command(const char *cmd){')
r(' else if(equals(cmd,"WIFI")){',' else if(equals(cmd,"WIFI_START"))wifi_start();\n else if(equals(cmd,"WIFILOG"))usb_wifi_log();\n else if(equals(cmd,"WIFI")){')
r('   usb_send("=== BCM4329 SDIO LINUX V07 PROBE (NO ASSOCIATION) ===\\r\\n");',
  '   usb_send("=== BCM4329 SDIO LINUX V08 ON-DEMAND STATUS ===\\r\\n");\n   usb_send("WIFI_DRIVER_LOAD_STATE ");send_int(wifi_state);usb_send(" ERRNO ");send_int((int32_t)wifi_errno);usb_send("\\r\\n");\n   usb_send("TOUCHSCREEN ");usb_send(present("/sys/class/input/event3")?"EVENT3 PRESENT\\r\\n":"EVENT3 ABSENT\\r\\n");')
# Still reports event3 presence informational only: full input list must be inspected independently
(dst/'init.c').write_text(s)
assert 'SYS_finit_module 379' in s and 'poll_touch();' in s and 'grid_poll_input();' in s
print('V08 USERLAND',len(s),'bytes; unchanged touchscreen polling; deferred WIFI_START and WIFILOG added')
