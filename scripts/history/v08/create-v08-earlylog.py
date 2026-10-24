#!/usr/bin/env python3
"""v08 restore early-boot Broadcom / SDIO diagnostics, preserving v07 behavior."""
from pathlib import Path
base=Path('/home/xoomdev/xoom-linux-rom')
out=base/'phase1-v08';out.mkdir(exist_ok=True)
src=(base/'phase1-v07/init.c').read_text()
def replace(old,new):
 global src
 assert src.count(old)==1,('anchor',src.count(old),old[:100])
 src=src.replace(old,new,1)
replace('/* Xoom MZ600 phase-1 v07 native upstream BCM4329 driver diagnostics. No libc/NEON.',
        '/* Xoom MZ600 phase-1 v08 early SDIO/wifi kernel ring diagnostics. No libc/NEON.')
replace('usb_send("XOOM LINUX MZ600 V07 WIFI SDIO PROBE\\r\\n");',
        'usb_send("XOOM LINUX MZ600 V08 BOOT WIFI LOGS\\r\\n");')
replace('usb_send("PONG XOOM-LINUX V07\\r\\n");',
        'usb_send("PONG XOOM-LINUX V08\\r\\n");')
replace('usb_send("HELP PING STATUS CPU MEM STORAGE INPUT THERMAL USB LOGS CMDLINE GRID WIFI TOUCH TOUCHSTOP REBOOT POWEROFF CANCEL\\r\\n");',
        'usb_send("HELP PING STATUS CPU MEM STORAGE INPUT THERMAL USB LOGS CMDLINE GRID WIFI SDIO BOOTWIFI TOUCH TOUCHSTOP REBOOT POWEROFF CANCEL\\r\\n");')
anchor='/* No event injection, grabs or writes; input events are observed read-only. */'
new=r'''
static void usb_dir(const char *path){
 usb_send("=== DIR ");usb_send(path);usb_send(" ===\r\n");
 long f=openf(path,O_RDONLY);
 if(f<0){usb_send("UNAVAILABLE\r\n");return;}
 char buf[1024];int listed=0;
 for(int round=0;round<8&&listed<90;round++){
   long n=sc6(SYS_getdents64,f,(long)buf,sizeof(buf),0,0,0);
   if(n<=0)break;
   for(long off=0;off+19<=n && listed<90;){
     struct linux_dirent64 *e=(void *)(buf+off);
     if(e->d_reclen<19||off+e->d_reclen>n)break;
     if(e->d_name[0]!='.'){usb_send(e->d_name);usb_send("\r\n");listed++;}
     off+=e->d_reclen;
   }
 }
 closef(f);
 usb_send("ENTRIES ");usb_send(utoa((unsigned long)listed));usb_send("\r\n");
}
static int has_substring_ci(const char *hay,int len,const char *needle){
 for(int i=0;i<len;i++){
   int j=0;
   while(needle[j]&&i+j<len){
     char a=hay[i+j],b=needle[j];
     if(a>='A'&&a<='Z')a+=32;
     if(b>='A'&&b<='Z')b+=32;
     if(a!=b)break;
     j++;
   }
   if(!needle[j])return 1;
 }
 return 0;
}
static int is_wifi_bootline(const char *p,int n){
 const char *match[]={"brcm","mmc","sdhci","sdio","wlan","wifi","firmware","pwrseq",
                     "regulator-wifi","vdd_wifi","voltage","mmc@c8000200", "rfkill"};
 for(unsigned i=0;i<sizeof(match)/sizeof(match[0]);i++)
   if(has_substring_ci(p,n,match[i]))return 1;
 return 0;
}
static void usb_bootwifi(void){
 /* SYSLOG_ACTION_READ_ALL is non-destructive; capture retained ring from boot. */
 static char kernel_log[262144];
 long n=sc6(SYS_syslog,3,(long)kernel_log,sizeof(kernel_log)-1,0,0,0);
 if(n<0){usb_send("BOOTWIFI ERROR: kernel ring unavailable\r\n");return;}
 usb_send("=== BOOTWIFI FILTERED BOOT KMSG ===\r\n");
 usb_send("RETAINED_BYTES ");usb_send(utoa((unsigned long)n));usb_send("\r\n");
 long begin=0;int matches=0;int emitted=0;
 for(long j=0;j<=n;j++){
   if(j<n&&kernel_log[j]!='\n')continue;
   long size=j-begin;
   if(size>0&&size<1500 && is_wifi_bootline(kernel_log+begin,(int)size)){
     matches++;
     if(emitted<95){
       /* Bound individual print lines and total flow to protect CDC ACM. */
       char line[512];long lim=size<500?size:500;
       for(long i=0;i<lim;i++){char c=kernel_log[begin+i];line[i]=(c>=32&&c<=126)?c:' ';}
       line[lim]=0;usb_send(line);usb_send("\r\n");emitted++;
     }
   }
   begin=j+1;
 }
 usb_send("MATCHED_LINES ");usb_send(utoa((unsigned long)matches));
 usb_send(" EMITTED ");usb_send(utoa((unsigned long)emitted));usb_send("\r\n");
 usb_send("=== END BOOTWIFI ===\r\n");
}
static void usb_sdio(void){
 usb_send("=== SDIO ENUMERATION: READ-ONLY ===\r\n");
 usb_dir("/sys/class/mmc_host");
 usb_dir("/sys/class/mmc_host/mmc2");
 usb_dir("/sys/bus/sdio/devices");
 usb_dir("/sys/bus/mmc/devices");
 usb_dir("/sys/class/net");
 usb_file("/sys/class/mmc_host/mmc2/device/uevent",380);
 usb_send("NO SCAN / NO WPA / NO DHCP / NO TX INITIATED BY USERSPACE\r\n");
}
'''
replace(anchor,new+'\n'+anchor)
anchor=' else if(equals(cmd,"TOUCH"))touch_start();'
replace(anchor,' else if(equals(cmd,"BOOTWIFI"))usb_bootwifi();\n else if(equals(cmd,"SDIO"))usb_sdio();\n'+anchor)
(out/'init.c').write_text(src)
print('V08 SOURCE STAGED:',out/'init.c',len(src),'bytes; non-destructive syslog action 3 and read-only sysfs scans')
