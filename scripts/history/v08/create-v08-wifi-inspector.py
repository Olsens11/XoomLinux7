#!/usr/bin/env python3
from pathlib import Path
b=Path('/home/xoomdev/xoom-linux-rom')
v=b/'phase1-v08'
v.mkdir(exist_ok=True)
s=(b/'phase1-v07/init.c').read_text()
def rep(a,z):
 global s
 assert s.count(a)==1,(a,s.count(a))
 s=s.replace(a,z,1)
rep('/* Xoom MZ600 phase-1 v07 native upstream BCM4329 driver diagnostics. No libc/NEON.',
    '/* Xoom MZ600 phase-1 v08 extended SDIO telemetry, identical WLAN driver. No libc/NEON.')
rep('#define SYS_syslog 103','#define SYS_syslog 103\n#define SYS_getdents64 217')
addon=r'''
/* Read-only sysfs enumerator, ARM getdents64, no libc. */
static void usb_dir(const char *path){
 long fd=openf(path,O_RDONLY);
 usb_send("DIR ");usb_send(path);usb_send(": ");
 if(fd<0){usb_send("UNAVAILABLE\r\n");return;}
 char buf[2048];
 long n=sc6(SYS_getdents64,fd,(long)buf,sizeof(buf),0,0,0);
 if(n<0){usb_send("GETDENTS FAILED\r\n");closef(fd);return;}
 int count=0;
 for(long k=0;k+20<=n&&count<50;){
   unsigned short len=(unsigned short)((unsigned char)buf[k+16]|((unsigned char)buf[k+17]<<8));
   if(len<20||k+len>n)break;
   const char *name=buf+k+19;
   if(name[0]!='.'||name[1]!='\0'){
     usb_send(name);usb_send(" ");count++;
   }
   k+=len;
 }
 usb_send("\r\n");closef(fd);
}
/* All kernel early boot messages retained in syslog RAM. Only send lines
 * relevant to SD/MMC, Broadcom, power/clock, firmware and probe errors. */
static int contains(const char *s,const char *pattern){
 for(;*s;s++){
   const char *a=s,*b=pattern;
   while(*a&&*b){
     char c=*a; if(c>='A'&&c<='Z')c=(char)(c+32);
     if(c!=*b)break;
     a++;b++;
   }
   if(!*b)return 1;
 }
 return 0;
}
static void wifi_boot_log(void){
 static char log[65536];
 long n=sc6(SYS_syslog,3,(long)log,sizeof(log)-1,0,0,0);
 if(n<0){usb_send("EARLY BOOT SYSLOG FAILED\r\n");return;}
 if(n>(long)sizeof(log)-1)n=(long)sizeof(log)-1;
 log[n]=0;
 usb_send("=== EARLY BOOT WIFI / SDIO / FIRMWARE FILTER ===\r\n");
 int lines=0,bytes=0;
 for(long k=0;k<n&&lines<130&&bytes<16000;){
   long end=k;
   while(end<n&&log[end]!='\n')end++;
   char save=log[end];log[end]=0;
   const char *line=log+k;
   if(contains(line,"brcm")||contains(line,"sdhci")||
      contains(line,"mmc")||contains(line,"sdio")||
      contains(line,"wifi")||contains(line,"firmware")||
      contains(line,"regulator")||contains(line,"vdd")||
      contains(line,"gpio")||contains(line,"clk")){
       if(end-k<450){usb_send(line);usb_send("\r\n");bytes+=(int)(end-k)+2;lines++;}
   }
   log[end]=save;k=end+1;
 }
 usb_send("FILTERED_LINES ");usb_send(utoa((unsigned long)lines));
 usb_send(" BYTES ");usb_send(utoa((unsigned long)bytes));
 usb_send("\r\n=== END BOOT RADIO LOG ===\r\n");
}
'''
rep('/* No event injection, grabs or writes; input events are observed read-only. */',
    addon+'\n/* No event injection, grabs or writes; input events are observed read-only. */')
rep('usb_send("XOOM LINUX MZ600 V07 WIFI SDIO PROBE\\r\\n");',
    'usb_send("XOOM LINUX MZ600 V08 WIFI SDIO EARLY-BOOT DIAGNOSTIC\\r\\n");')
rep('usb_send("PONG XOOM-LINUX V07\\r\\n");',
    'usb_send("PONG XOOM-LINUX V08\\r\\n");')
rep('usb_send("HELP PING STATUS CPU MEM STORAGE INPUT THERMAL USB LOGS CMDLINE GRID WIFI TOUCH TOUCHSTOP REBOOT POWEROFF CANCEL\\r\\n");',
    'usb_send("HELP PING STATUS CPU MEM STORAGE INPUT THERMAL USB LOGS CMDLINE GRID WIFI WIFILOG WIFIDIRS TOUCH TOUCHSTOP REBOOT POWEROFF CANCEL\\r\\n");')
rep(' else if(equals(cmd,"TOUCH"))touch_start();',
''' else if(equals(cmd,"WIFILOG"))wifi_boot_log();
 else if(equals(cmd,"WIFIDIRS")){
   usb_dir("/sys/bus/sdio/devices");
   usb_dir("/sys/bus/mmc/devices");
   usb_dir("/sys/class/mmc_host/mmc2");
   usb_dir("/sys/class/net");
   usb_dir("/sys/class/regulator");
   usb_file("/sys/class/mmc_host/mmc2/device/uevent",320);
 }
 else if(equals(cmd,"TOUCH"))touch_start();''')
(v/'init.c').write_text(s)
print('V08 diagnostic userspace source',v/'init.c','bytes',len(s))
