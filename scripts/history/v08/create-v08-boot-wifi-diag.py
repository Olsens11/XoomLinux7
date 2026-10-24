#!/usr/bin/env python3
from pathlib import Path
B=Path('/home/xoomdev/xoom-linux-rom')
v=B/'phase1-v08'
v.mkdir(exist_ok=True)
s=(B/'phase1-v07/init.c').read_text()
def replace(a,b):
 global s
 assert s.count(a)==1,(s.count(a),a[:90])
 s=s.replace(a,b,1)
replace('/* Xoom MZ600 phase-1 v07 native upstream BCM4329 driver diagnostics. No libc/NEON.',
        '/* Xoom MZ600 phase-1 v08 BCM4329 SDIO full boot logs and regulator probe. No libc/NEON.')
needle='static void usb_logs(void){'
extra=r'''
/* Unlike LOGS (last 4 KiB only), scan up to 64 KiB of the kernel's
 * complete boot messages for Wi-Fi SDIO/power initialization.
 * Bounded output for nonblocking USB CDC ACM, purely read-only. */
static int wifi_keyword(const char *s,long n){
 static const char *terms[]={"mmc","sdio","brcm","bcm4329","dhd","wlan","wifi",
  "pwrseq","firmware","fw_","regulator","gpio","voltage","carddetect"};
 for(size_t t=0;t<sizeof(terms)/sizeof(terms[0]);t++){
  const char *word=terms[t];size_t wlen=slen(word);
  for(long i=0;i+(long)wlen<=n;i++){
    size_t j=0;
    while(j<wlen){
      char c=s[i+j];
      if(c>='A'&&c<='Z')c=(char)(c+32);
      if(c!=word[j])break;
      j++;
    }
    if(j==wlen)return 1;
  }
 }
 return 0;
}
static void usb_wifilog(void){
 static char logbuf[65536];
 long n=sc6(SYS_syslog,3,(long)logbuf,sizeof(logbuf)-1,0,0,0);
 if(n<=0){usb_send("WIFILOG KERNEL BUFFER UNAVAILABLE\r\n");return;}
 usb_send("=== FILTERED BOOT KERNEL LOG 64KiB WINDOW ===\r\n");
 usb_send("READ_BYTES=");usb_send(utoa((unsigned long)n));usb_send("\r\n");
 long i=0;unsigned shown=0;
 while(i<n){
  long start=i;
  while(i<n&&logbuf[i]!='\n')i++;
  long length=i-start;
  if(i<n)i++;
  if(!wifi_keyword(logbuf+start,length))continue;
  if(shown>=65){usb_send("WIFILOG TRUNCATED AFTER 65 MATCHES\r\n");break;}
  /* Strip overlong lines, do not send secrets or huge binary dumps. */
  char line[240];int len=(int)(length>225?225:length);
  for(int j=0;j<len;j++){
   char ch=logbuf[start+j];
   line[j]=(ch>=32&&ch<127)?ch:' ';
  }
  line[len]=0;usb_send(line);usb_send("\r\n");shown++;
 }
 usb_send("MATCHING_LINES=");usb_send(utoa(shown));usb_send("\r\n");
 usb_send("=== END WIFILOG ===\r\n");
}
static void usb_dir(const char *path){
 long fd=openf(path,O_RDONLY);
 usb_send("DIR ");usb_send(path);usb_send(" : ");
 if(fd<0){usb_send("NOT ACCESSIBLE\r\n");return;}
 usb_send("\r\n");unsigned emitted=0;
 char data[768];
 for(int rd=0;rd<2;rd++){
   long n=sc6(SYS_getdents64,fd,(long)data,sizeof(data),0,0,0);
   if(n<=0)break;
   for(long off=0;off+19<n;){
     struct linux_dirent64 *e=(void*)(data+off);
     if(e->d_reclen<19||off+e->d_reclen>n)break;
     if(e->d_name[0]!='.'&&emitted<45){
        usb_send("  ");usb_send(e->d_name);usb_send("\r\n");emitted++;
     }
     off+=e->d_reclen;
   }
 }
 closef(fd);
 usb_send("COUNT=");usb_send(utoa(emitted));usb_send("\r\n");
}
static void usb_sdio_state(void){
 usb_send("=== BCM4329 SDIO SYSTEM ENUMERATION ===\r\n");
 usb_dir("/sys/bus/sdio/devices");
 usb_dir("/sys/bus/mmc/devices");
 usb_dir("/sys/class/mmc_host");
 usb_dir("/sys/class/mmc_host/mmc2");
 usb_dir("/sys/class/net");
 usb_dir("/sys/class/regulator");
 usb_file("/sys/class/mmc_host/mmc2/device/uevent",256);
 usb_file("/sys/class/net/wlan0/address",80);
 usb_file("/sys/class/net/wlan0/addr_assign_type",80);
 usb_send("SAFE: NO SCAN, NO WPA, NO DHCP\r\n");
}
'''
replace(needle,extra+needle)
replace('usb_send("XOOM LINUX MZ600 V07 WIFI SDIO PROBE\\r\\n");',
        'usb_send("XOOM LINUX MZ600 V08 SDIO BOOT DIAGNOSTIC\\r\\n");')
replace('usb_send("PONG XOOM-LINUX V07\\r\\n");','usb_send("PONG XOOM-LINUX V08\\r\\n");')
replace('usb_send("HELP PING STATUS CPU MEM STORAGE INPUT THERMAL USB LOGS CMDLINE GRID WIFI TOUCH TOUCHSTOP REBOOT POWEROFF CANCEL\\r\\n");',
        'usb_send("HELP PING STATUS CPU MEM STORAGE INPUT THERMAL USB LOGS WIFILOG SDIO CMDLINE GRID WIFI TOUCH TOUCHSTOP REBOOT POWEROFF CANCEL\\r\\n");')
replace(' else if(cmd[0]==\'C\' && cmd[1]==\'M\' && cmd[2]==\'D\' && cmd[3]==\'L\' && cmd[4]==\'I\' && cmd[5]==\'N\' && cmd[6]==\'E\' && cmd[7]==0)usb_file("/proc/cmdline",1024);',
        ''' else if(equals(cmd,"WIFILOG"))usb_wifilog();
 else if(equals(cmd,"SDIO"))usb_sdio_state();
 else if(cmd[0]=='C' && cmd[1]=='M' && cmd[2]=='D' && cmd[3]=='L' && cmd[4]=='I' && cmd[5]=='N' && cmd[6]=='E' && cmd[7]==0)usb_file("/proc/cmdline",1024);''')
(v/'init.c').write_text(s)
print('V08 USERLAND',v/'init.c',len(s),'bytes, new WIFILOG/SDIO diagnostics')
