#!/usr/bin/env python3
from pathlib import Path
b=Path('/home/xoomdev/xoom-linux-rom')
v=b/'phase1-v08';v.mkdir(exist_ok=True)
s=(b/'phase1-v07/init.c').read_text()
def one(old,new):
 global s
 assert s.count(old)==1,(s.count(old),old[:75])
 s=s.replace(old,new,1)
one('/* Xoom MZ600 phase-1 v07 native upstream BCM4329 driver diagnostics. No libc/NEON.',
    '/* Xoom MZ600 phase-1 v08 kernel ring / MMC analysis, no driver changes. No libc/NEON.')
one('usb_send("XOOM LINUX MZ600 V07 WIFI SDIO PROBE\\r\\n");',
    'usb_send("XOOM LINUX MZ600 V08 EARLY WIFI DIAGNOSTICS\\r\\n");')
one('usb_send("PONG XOOM-LINUX V07\\r\\n");','usb_send("PONG XOOM-LINUX V08\\r\\n");')
one('usb_send("HELP PING STATUS CPU MEM STORAGE INPUT THERMAL USB LOGS CMDLINE GRID WIFI TOUCH TOUCHSTOP REBOOT POWEROFF CANCEL\\r\\n");',
    'usb_send("HELP PING STATUS CPU MEM STORAGE INPUT THERMAL USB LOGS CMDLINE GRID WIFI MMCINFO WIFILOG TOUCH TOUCHSTOP REBOOT POWEROFF CANCEL\\r\\n");')
anchor='/* No event injection, grabs or writes; input events are observed read-only. */'
new=r'''
/* Read *all retained* printk messages using SYSLOG_ACTION_READ_ALL, do not
 * clear or consume ring. Emit bounded matching lines only, retaining early
 * SDIO/firmware diagnostics lost by legacy USB LOGS latest-4K truncation.
 * All commands read-only. */
static char wifi_full_ring[131072];
static int wifi_log_line_match(const char *line,int n){
 static const char *keys[]={"mmc", "sdhci", "brcm", "firmware", "wifi", "wlan", "pwrseq", "regulator", "gpio", "voltage", "timeout", "cfg80211", "sdio", "clock"};
 for(unsigned ki=0;ki<sizeof(keys)/sizeof(keys[0]);ki++){
   const char *k=keys[ki];
   for(int i=0;i<n;i++){
     int j=0;
     while(k[j]&&i+j<n){
       char c=line[i+j];
       if(c>='A'&&c<='Z')c=(char)(c+('a'-'A'));
       if(c!=k[j])break;
       j++;
     }
     if(k[j]==0)return 1;
   }
 }
 return 0;
}
static void wifi_full_logs(void){
 long n=sc6(SYS_syslog,3,(long)wifi_full_ring,sizeof(wifi_full_ring)-1,0,0,0);
 if(n<=0){usb_send("WIFILOG ERR: SYSLOG_ACTION_READ_ALL unavailable\r\n");return;}
 wifi_full_ring[n]=0;
 usb_send("=== EARLY WIFI+SDIO+POWER KERNEL EVENTS (READ ONLY) ===\r\n");
 usb_send("RING_BYTES_READ=");usb_send(utoa((unsigned long)n));usb_send("\r\n");
 long lines=0,found=0,sent=0;
 for(long i=0;i<n;){
   long end=i;
   while(end<n&&wifi_full_ring[end]!='\n')end++;
   long ll=end-i;
   if(ll>0&&ll<390&&wifi_log_line_match(wifi_full_ring+i,(int)ll)){
      char line[400];
      for(int j=0;j<ll;j++)line[j]=wifi_full_ring[i+j];
      line[ll]=0;
      usb_send(line);usb_send("\r\n");
      found++;sent+=ll;
      if(found>=130||sent>15500){usb_send("WIFILOG MATCH OUTPUT CAPPED\r\n");break;}
   }
   lines++;
   i=end+1;
 }
 usb_send("MATCHED_LINES=");usb_send(utoa((unsigned long)found));
 usb_send(" SCANNED_LINES=");usb_send(utoa((unsigned long)lines));
 usb_send("\r\n=== END EARLY WIFI LOG ===\r\n");
}
static void wifi_usb_ls(const char *path){
 long fd=openf(path,O_RDONLY);
 usb_send("DIR ");usb_send(path);usb_send(": ");
 if(fd<0){usb_send("UNAVAILABLE\r\n");return;}
 char buf[1024];int printed=0;
 for(int t=0;t<3;t++){
   long n=sc6(SYS_getdents64,fd,(long)buf,sizeof(buf),0,0,0);
   if(n<=0)break;
   for(long o=0;o+19<n;){
     struct linux_dirent64 *e=(void *)(buf+o);
     if(e->d_reclen<19||o+e->d_reclen>n)break;
     if(e->d_name[0]!='.'){usb_send(e->d_name);usb_send(" ");printed++;}
     o+=e->d_reclen;
   }
 }
 closef(fd);
 if(!printed)usb_send("(empty)");
 usb_send("\r\n");
}
'''
assert s.count(anchor)==1
s=s.replace(anchor,new+anchor,1)
one(' else if(equals(cmd,"TOUCH"))touch_start();',r''' else if(equals(cmd,"WIFILOG"))wifi_full_logs();
 else if(equals(cmd,"MMCINFO")){
   wifi_usb_ls("/sys/bus/mmc/devices");
   wifi_usb_ls("/sys/class/mmc_host/mmc2");
   wifi_usb_ls("/sys/class/net");
   usb_file("/sys/bus/mmc/devices/mmc2:0001/uevent",500);
   usb_file("/sys/class/mmc_host/mmc2/device/uevent",500);
   usb_send("NO ASSOCIATION OR ACTIVE SCAN PERFORMED\r\n");
 }
 else if(equals(cmd,"TOUCH"))touch_start();''')
assert 'grid_touch_update' in s and 'SYS_reboot' in s
(v/'init.c').write_text(s)
print('V08 diagnostic-only userland, bytes=',len(s),'no kernel/dts change; no network operations')
