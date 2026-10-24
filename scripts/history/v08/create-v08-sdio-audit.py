#!/usr/bin/env python3
"""Read-only v08 SDIO gate instrumentation. Preserves v07 driver/DTB/firmware."""
from pathlib import Path
b=Path('/home/xoomdev/xoom-linux-rom')
v=b/'phase1-v08'
v.mkdir(exist_ok=True)
s=(b/'phase1-v07/init.c').read_text()
def sub(a,z):
 global s
 assert s.count(a)==1,(a,s.count(a))
 s=s.replace(a,z,1)
sub('/* Xoom MZ600 phase-1 v07 native upstream BCM4329 driver diagnostics. No libc/NEON.',
    '/* Xoom MZ600 phase-1 v08 read-only SDIO enumeration and boot-log diagnostics. No libc/NEON.')
anchor='/* No event injection, grabs or writes; input events are observed read-only. */'
readers=r'''
/* Read-only SDIO gate probing: the host's sysfs existence alone does NOT
 * mean that an SDIO FUNCTION was enumerated. Never open block devices. */
static void usb_lsdir(const char *path){
 usb_send("DIR ");usb_send(path);usb_send("\r\n");
 long fd=openf(path,O_RDONLY);
 if(fd<0){usb_send("UNAVAILABLE\r\n");return;}
 char b[1024];
 int files=0;
 for(int rounds=0;rounds<5;rounds++){
   long n=sc6(SYS_getdents64,fd,(long)b,sizeof(b),0,0,0);
   if(n<=0)break;
   for(long off=0;off+19<n;){
     struct linux_dirent64 *e=(void*)(b+off);
     if(e->d_reclen<19||off+e->d_reclen>n)break;
     if(e->d_name[0]!='.'){
       usb_send("  ");usb_send(e->d_name);usb_send("\r\n");
       if(++files>=80){closef(fd);usb_send("  ...TRUNCATED\r\n");return;}
     }
     off+=e->d_reclen;
   }
 }
 closef(fd);
 usb_send("ENTRY COUNT ");usb_send(utoa((unsigned long)files));usb_send("\r\n");
}
static int contains_lower(const char *s,const char *key){
 for(const char *a=s;*a;a++){
   const char *p=a,*k=key;
   while(*p&&*k){
      char c=*p;
      if(c>='A'&&c<='Z')c=(char)(c+32);
      if(c!=*k)break;
      p++;k++;
   }
   if(!*k)return 1;
 }
 return 0;
}
static int kernel_line_interest(const char *s){
 static const char *words[]={"mmc","sdio","sdhci","brcm","bcm4329",
   "pwrseq","reset","gpio","firmware","defer","wifi","-110","timeout"};
 for(unsigned i=0;i<sizeof(words)/sizeof(words[0]);i++)
   if(contains_lower(s,words[i]))return 1;
 return 0;
}
static void usb_bootlog(void){
 /* SYSLOG_ACTION_READ_ALL=3 does not consume kernel logs.
  * Larger than previous 8KiB, so boot-time MMC errors are not lost. */
 static char history[131072];
 long n=sc6(SYS_syslog,3,(long)history,sizeof(history)-1,0,0,0);
 if(n<=0){usb_send("BOOTLOG UNAVAILABLE errno=");send_int((int)-n);usb_send("\r\n");return;}
 usb_send("=== KERNEL LOG MATCHES (READ-ONLY; EARLY+LATE) ===\r\n");
 usb_send("READ_BYTES ");usb_send(utoa((unsigned long)n));usb_send("\r\n");
 history[n]=0;
 int out=0,seen=0,lines=0;
 /* Split with bounded stack output. Matching lines only, ≤110 lines. */
 for(long i=0;i<n;){
   char line[390];
   int k=0;
   while(i<n&&history[i]!='\n'){
     char c=history[i++];
     if(k<(int)sizeof(line)-3 && c!='\0'&&c!='\r')line[k++]=c;
   }
   if(i<n)i++;
   line[k]=0;lines++;
   if(k>0 && kernel_line_interest(line)){
      seen++;
      if(out<110){usb_send(line);usb_send("\r\n");out++;}
   }
 }
 usb_send("MATCH_COUNT ");usb_send(utoa((unsigned long)seen));
 usb_send(" SENT ");usb_send(utoa((unsigned long)out));
 usb_send(" TOTAL_LINES ");usb_send(utoa((unsigned long)lines));usb_send("\r\n");
 usb_send("=== END BOOTLOG ===\r\n");
}
static void usb_sdio_gate(void){
 usb_send("=== READ-ONLY SDIO ENUMERATION GATE ===\r\n");
 usb_lsdir("/sys/bus/sdio/devices");
 usb_lsdir("/sys/bus/mmc/devices");
 usb_lsdir("/sys/class/mmc_host/mmc2");
 usb_lsdir("/sys/bus/platform/drivers/mmc-pwrseq-simple");
 usb_lsdir("/sys/bus/platform/drivers/sdhci-tegra");
 usb_file("/sys/bus/platform/devices/c8000200.mmc/uevent",400);
 usb_file("/sys/bus/sdio/devices/mmc2:0001:1/vendor",60);
 usb_file("/sys/bus/sdio/devices/mmc2:0001:1/device",60);
 usb_file("/sys/bus/sdio/devices/mmc2:0001:1/modalias",150);
 usb_file("/sys/bus/sdio/devices/mmc2:0001:2/vendor",60);
 usb_file("/sys/bus/sdio/devices/mmc2:0001:2/device",60);
 usb_send("=== END SDIO ENUMERATION ===\r\n");
}
'''
sub(anchor,readers+anchor)
sub('usb_send("XOOM LINUX MZ600 V07 WIFI SDIO PROBE\\r\\n");',
    'usb_send("XOOM LINUX MZ600 V08 SDIO ENUMERATION AUDIT\\r\\n");')
sub('usb_send("PONG XOOM-LINUX V07\\r\\n");',
    'usb_send("PONG XOOM-LINUX V08\\r\\n");')
sub('usb_send("HELP PING STATUS CPU MEM STORAGE INPUT THERMAL USB LOGS CMDLINE GRID WIFI TOUCH TOUCHSTOP REBOOT POWEROFF CANCEL\\r\\n");',
    'usb_send("HELP PING STATUS CPU MEM STORAGE INPUT THERMAL USB LOGS BOOTLOG SDIO CMDLINE GRID WIFI TOUCH TOUCHSTOP REBOOT POWEROFF CANCEL\\r\\n");')
a=' else if(equals(cmd,"WIFI")){'
sub(a,' else if(equals(cmd,"BOOTLOG"))usb_bootlog();\n else if(equals(cmd,"SDIO"))usb_sdio_gate();\n'+a)
assert 'kernel_line_interest' in s and 'usb_sdio_gate' in s
(v/'init.c').write_text(s)
print('V08 READ-ONLY DIAG SOURCE',v/'init.c',len(s),'bytes')
