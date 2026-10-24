#!/usr/bin/env python3
from pathlib import Path
base=Path('/home/xoomdev/xoom-linux-rom')
dst=base/'phase1-v08';dst.mkdir(exist_ok=True)
s=(base/'phase1-v07/init.c').read_text()
def rep(a,b):
 global s
 assert s.count(a)==1,(s.count(a),a[:90])
 s=s.replace(a,b,1)
rep('/* Xoom MZ600 phase-1 v07 native upstream BCM4329 driver diagnostics. No libc/NEON.',
    '/* Xoom MZ600 phase-1 v08 early SDIO+brcmfmac diagnostic, no changes to driver. No libc/NEON.')
rep('XOOM LINUX MZ600 V07 WIFI SDIO PROBE','XOOM LINUX MZ600 V08 SDIO EARLY DIAGNOSTICS')
rep('PONG XOOM-LINUX V07','PONG XOOM-LINUX V08')
rep('USB LOGS CMDLINE GRID WIFI TOUCH','USB LOGS WIFILOG SDIO CMDLINE GRID WIFI TOUCH')
marker='/* No event injection, grabs or writes; input events are observed read-only. */'
inject=r'''
/* Read-only early boot driver and power status. Standard kernel printk ring.
 * Collects a large bounded snapshot to retain messages before PID1 initialization.
 * No arbitrary shell or network actions; only existing USB diagnostic output. */
static char wifi_kernel_log[131072];
static char lowascii(char c){return (c>='A'&&c<='Z')?(char)(c+32):c;}
static int has_ci(const char *hay,int n,const char *needle){
 for(int i=0;i<n;i++){
   int k=0;
   while(needle[k]&&i+k<n&&lowascii(hay[i+k])==lowascii(needle[k]))k++;
   if(!needle[k])return 1;
 }
 return 0;
}
static int wifi_log_match(const char *line,int n){
 const char *keys[]={"mmc","sdio","brcm","bcm43","wlan","firmware","regulator","cfg80211","vdd_wifi","pwrseq","gpio"};
 for(unsigned i=0;i<sizeof(keys)/sizeof(keys[0]);i++)
   if(has_ci(line,n,keys[i]))return 1;
 return 0;
}
static void usb_wifi_kernel_log(void){
 long n=sc6(SYS_syslog,3,(long)wifi_kernel_log,sizeof(wifi_kernel_log)-1,0,0,0);
 if(n<0){usb_send("WIFILOG ERROR: kernel syslog unavailable\r\n");return;}
 usb_send("=== V08 EARLY WIFI/SDIO PRINTK FILTER ===\r\n");
 int sent=0,matched=0;
 for(long start=0;start<n;){
    long end=start;
    while(end<n&&wifi_kernel_log[end]!='\n')end++;
    long len=end-start;
    if(len>0&&len<520&&wifi_log_match(wifi_kernel_log+start,(int)len)){
       matched++;
       if(sent<110){
          char save=wifi_kernel_log[end];
          wifi_kernel_log[end]=0;
          usb_send(wifi_kernel_log+start);
          usb_send("\r\n");
          wifi_kernel_log[end]=save;
          sent++;
       }
    }
    start=end+1;
 }
 usb_send("MATCHING_LINES ");usb_send(utoa((unsigned long)matched));
 usb_send(" SENT ");usb_send(utoa((unsigned long)sent));
 usb_send(" RING_BYTES ");usb_send(utoa((unsigned long)n));
 usb_send("\r\n=== END V08 WIFI LOG ===\r\n");
}
static void usb_wifi_list_dir(const char *path){
 long fd=openf(path,O_RDONLY);
 usb_send("DIR ");usb_send(path);usb_send(": ");
 if(fd<0){usb_send("UNAVAILABLE\r\n");return;}
 char b[1600];
 int count=0;
 for(int pass=0;pass<3;pass++){
  long n=sc6(SYS_getdents64,fd,(long)b,sizeof(b),0,0,0);
  if(n<=0)break;
  for(long off=0;off+19<n;){
   struct linux_dirent64 *entry=(void *)(b+off);
   if(entry->d_reclen<19||off+entry->d_reclen>n)break;
   if(entry->d_name[0]!='.'){
      if(count<25){usb_send(entry->d_name);usb_send(" ");}
      count++;
   }
   off+=entry->d_reclen;
  }
 }
 closef(fd);
 usb_send(" count=");usb_send(utoa((unsigned long)count));usb_send("\r\n");
}
static void usb_sdio_status(void){
 usb_send("=== V08 SDIO ENUMERATION (READ ONLY) ===\r\n");
 usb_wifi_list_dir("/sys/class/mmc_host");
 usb_wifi_list_dir("/sys/class/mmc_host/mmc2");
 usb_wifi_list_dir("/sys/bus/sdio/devices");
 usb_wifi_list_dir("/sys/bus/mmc/devices");
 usb_wifi_list_dir("/sys/class/net");
 usb_file("/sys/class/mmc_host/mmc2/device/uevent",300);
 usb_file("/sys/class/net/wlan0/operstate",120);
 usb_file("/sys/class/net/wlan0/addr_assign_type",120);
 usb_send("NO NETWORK JOIN OR RADIO COMMANDS\r\n");
}
'''
rep(marker,inject+marker)
rep(next(line for line in s.splitlines() if 'usb_file("/proc/cmdline",1024);' in line),
''' else if(equals(cmd,"WIFILOG"))usb_wifi_kernel_log();
 else if(equals(cmd,"SDIO"))usb_sdio_status();
 else if(cmd[0]=='C' && cmd[1]=='M' && cmd[2]=='D' && cmd[3]=='L' && cmd[4]=='I' && cmd[5]=='N' && cmd[6]=='E' && cmd[7]==0)usb_file("/proc/cmdline",1024);''')
assert 'WIFILOG' in s and 'SDIO' in s and 'grid_cross_paint' in s
(dst/'init.c').write_text(s)
print('V08 DIAGNOSTIC SOURCE:',dst/'init.c','bytes',len(s))
