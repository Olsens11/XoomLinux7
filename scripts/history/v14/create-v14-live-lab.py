#!/usr/bin/env python3
"""v14 live WiFi diagnostics, USB binary upload, module hotreload; no kernel flash."""
from pathlib import Path
B=Path('/home/xoomdev/xoom-linux-rom')
V=B/'phase1-v14'; V.mkdir(exist_ok=True)
s=(B/'phase1-v13/init.c').read_text()
def r(old,new):
 global s
 assert s.count(old)==1,(s.count(old),old[:65])
 s=s.replace(old,new,1)
r('/* Xoom MZ600 phase-1 v13 Tegra20 BCM4329 SDIO host init_card upstream workaround+F2 trace. No libc/NEON.',
  '/* Xoom MZ600 phase-1 v14 LIVE WiFi hot-reload/USB RAM transfer. No libc/NEON.')
r('#define SYS_syslog 103', '''#define SYS_syslog 103
#define SYS_finit_module 379
#define SYS_delete_module 129
#define SYS_unlink 10
#define SYS_mkdir 39
#define O_CREAT 0x40
#define O_TRUNC 0x200''')
r('\"pwrseq\",\"reset\",\"gpio\",\"firmware\",\"defer\",\"wifi\",\"-110\",\"timeout\"','\"pwrseq\",\"reset\",\"gpio\",\"firmware\",\"defer\",\"wifi\",\"-110\",\"timeout\",\"xoom-f2\",\"xoom-host\"')
r('usb_send(\"XOOM LINUX MZ600 V13 TEGRA HOST INIT QUIRK\\r\\n\");','usb_send(\"XOOM LINUX MZ600 V14 LIVE WIFI LAB\\r\\n\");')
r('usb_send(\"PONG XOOM-LINUX V13\\r\\n\");','usb_send(\"PONG XOOM-LINUX V14\\r\\n\");')
r('usb_send(\"HELP PING STATUS CPU MEM STORAGE INPUT THERMAL USB LOGS BOOTLOG SDIO CMDLINE GRID WIFI TOUCH TOUCHSTOP REBOOT POWEROFF CANCEL\\r\\n\");',
  'usb_send(\"HELP PING STATUS CPU MEM STORAGE INPUT THERMAL USB LOGS BOOTLOG SDIO CMDLINE GRID WIFI WIFI_START WIFI_STOP WIFI_RETRY WIFI_DEBUG N UPLOAD TYPE N TOUCH TOUCHSTOP REBOOT POWEROFF CANCEL\\r\\n\");')
pre=r'''
/* RAM-only USB transfer: fixed allowlist of firmware and modules.
 * No paths provided by host are used. CRC32 for transfer verification.
 * Uploaded modules are only loaded by explicit WIFI_START; no automatic execute.
 * Host must verify DONE checksum before starting a module.
 */
static long upl_fd=-1;
static uint32_t upl_crc=0xffffffffu;
static unsigned upl_total,upl_remaining;
static const char *upl_target;
static unsigned upl_idle;
static int wifi_debug=6;
static int wifi_on;
static void usb_hex32(uint32_t v){
 static const char hx[]="0123456789ABCDEF";
 char b[11]="0x00000000";
 for(int i=0;i<8;i++)b[2+i]=hx[(v>>(28-4*i))&15u];
 usb_send(b);
}
static void upload_stop(int done){
 if(upl_fd>=0){closef(upl_fd);upl_fd=-1;}
 if(done){
  usb_send("UPLOAD DONE SIZE ");usb_send(utoa(upl_total));
  usb_send(" CRC32 ");usb_hex32(upl_crc^0xffffffffu);usb_send("\r\n");
 }else if(upl_target){
  sc6(SYS_unlink,(long)upl_target,0,0,0,0,0);
  usb_send("UPLOAD ABORTED\r\n");
 }
 upl_remaining=0;upl_total=0;upl_crc=0xffffffffu;upl_idle=0;upl_target=0;
}
static int decparse(const char *s,unsigned *out){
 unsigned n=0;int count=0;
 if(!*s)return 0;
 for(;*s;s++,count++){
  if(*s<'0'||*s>'9'||count>9)return 0;
  unsigned d=(unsigned)(*s-'0');
  if(n>(0xffffffffu-d)/10u)return 0;
  n=n*10u+d;
 }
 *out=n;return 1;
}
static void usb_upload_begin(const char *command){
 if(upl_fd>=0){usb_send("UPLOAD BUSY\r\n");return;}
 if(wifi_on){usb_send("UPLOAD DENIED: WIFI_STOP first\r\n");return;}
 const char *p=command+7; /* 'UPLOAD ' */
 const char *type=0;unsigned size=0;
 if(p[0]=='B' && p[1]=='R' && p[2]=='C' && p[3]=='M' && p[4]=='F' &&
    p[5]=='M' && p[6]=='A' && p[7]=='C' && p[8]==' '){
  upl_target="/run/brcmfmac.ko";type=p+9;
 }else if(p[0]=='B' && p[1]=='R' && p[2]=='C' && p[3]=='M' && p[4]=='U' &&
          p[5]=='T' && p[6]=='I' && p[7]=='L' && p[8]==' '){
  upl_target="/run/brcmutil.ko";type=p+9;
 }else if(p[0]=='F' && p[1]=='I' && p[2]=='R' && p[3]=='M' &&
          p[4]=='W' && p[5]=='A' && p[6]=='R' && p[7]=='E' && p[8]==' '){
  upl_target="/lib/firmware/brcm/brcmfmac4329-sdio.bin";type=p+9;
 }else if(p[0]=='N' && p[1]=='V' && p[2]=='R' && p[3]=='A' && p[4]=='M' && p[5]==' '){
  upl_target="/lib/firmware/brcm/brcmfmac4329-sdio.txt";type=p+6;
 }else{upl_target=0;usb_send("UPLOAD BAD TYPE\r\n");return;}
 if(!decparse(type,&size)||size<16||size>1048576){
  upl_target=0;usb_send("UPLOAD INVALID LENGTH\r\n");return;
 }
 /* /run is an existing tmpfs. /lib/firmware/brcm exists in RAM initramfs. */
 long fd=sc6(SYS_open,(long)upl_target,O_WRONLY|O_CREAT|O_TRUNC,0600,0,0,0);
 if(fd<0){upl_target=0;usb_send("UPLOAD OPEN FAILED errno=");send_int((int32_t)-fd);usb_send("\r\n");return;}
 upl_fd=fd;upl_total=upl_remaining=size;upl_crc=0xffffffffu;upl_idle=0;
 usb_send("UPLOAD READY BYTES ");usb_send(utoa(size));usb_send("\r\n");
}
static void usb_upload_data(const char *b,long n){
 if(upl_fd<0||n<=0)return;
 if((unsigned long)n>upl_remaining)n=(long)upl_remaining;
 const char *p=b;
 long w=writef(upl_fd,p,n);
 if(w!=n){upload_stop(0);return;}
 for(long i=0;i<n;i++){
  uint32_t x=upl_crc^(uint8_t)p[i];
  for(int q=0;q<8;q++)x=(x>>1)^(0xedb88320u & (0u-(x&1u)));
  upl_crc=x;
 }
 upl_remaining-=(unsigned)n;upl_idle=0;
 if(!upl_remaining)upload_stop(1);
}
static long wifi_load_one(const char *preferred,const char *builtin,const char *args){
 long fd=openf(preferred,O_RDONLY);
 if(fd<0)fd=openf(builtin,O_RDONLY);
 if(fd<0)return fd;
 long rc=sc6(SYS_finit_module,fd,(long)args,0,0,0,0);
 closef(fd);return rc;
}
static void wifi_stop(void){
 if(upl_fd>=0){usb_send("STOP DENIED DURING UPLOAD\r\n");return;}
 long a=sc6(SYS_delete_module,(long)"brcmfmac",O_NONBLOCK,0,0,0,0);
 long b=sc6(SYS_delete_module,(long)"brcmutil",O_NONBLOCK,0,0,0,0);
 usb_send("WIFI_STOP brcmfmac_rc ");send_int((int32_t)a);
 usb_send(" brcmutil_rc ");send_int((int32_t)b);usb_send("\r\n");
 wifi_on=0;
}
static void wifi_start(void){
 if(upl_fd>=0){usb_send("START DENIED DURING UPLOAD\r\n");return;}
 if(wifi_on){usb_send("WIFI ALREADY STARTED - WIFI_STOP FIRST\r\n");return;}
 long r=wifi_load_one("/run/brcmutil.ko","/wifi/brcmutil.ko","");
 usb_send("BRCMUTIL rc ");send_int((int32_t)r);usb_send("\r\n");
 if(r<0 && r!=-17){usb_send("WIFI_START ABORTED\r\n");return;}
 char opts[]="debug=00000";
 unsigned v=(unsigned)wifi_debug;
 for(int i=10;i>=6;i--){opts[i]=(char)('0'+(v%10u));v/=10u;}
 r=wifi_load_one("/run/brcmfmac.ko","/wifi/brcmfmac.ko",opts);
 usb_send("BRCMFMAC rc ");send_int((int32_t)r);
 usb_send(" debug ");send_int(wifi_debug);usb_send("\r\n");
 if(r==0){wifi_on=1;usb_send("WIFI PROBE STARTED (NO ASSOCIATION)\r\n");}
}
static void wifi_status(void){
 usb_send("WIFI LIVE-LAB MODULE STATUS\r\n");
 usb_file("/proc/modules",1400);
 usb_file("/sys/module/brcmfmac/parameters/debug",80);
 usb_send("STAGED BRMF ");usb_send(present("/run/brcmfmac.ko")?"YES":"NO");
 usb_send(" BRCUTIL ");usb_send(present("/run/brcmutil.ko")?"YES":"NO");usb_send("\r\n");
 usb_send("WLAN0 ");usb_send(present("/sys/class/net/wlan0")?"PRESENT\r\n":"ABSENT\r\n");
 usb_send("NO SCAN/ASSOCIATION/DHCP\r\n");
}
'''
r('static void usb_command(const char *cmd){',pre+'\nstatic void usb_command(const char *cmd){')
r(' else if(equals(cmd,"BOOTLOG"))usb_bootlog();',
''' else if(equals(cmd,"WIFI_START"))wifi_start();
 else if(equals(cmd,"WIFI_STOP"))wifi_stop();
 else if(equals(cmd,"WIFI_RETRY")){wifi_stop();wifi_start();}
 else if(equals(cmd,"WIFI_STATUS"))wifi_status();
 else if(cmd[0]=='W'&&cmd[1]=='I'&&cmd[2]=='F'&&cmd[3]=='I'&&
         cmd[4]=='_'&&cmd[5]=='D'&&cmd[6]=='E'&&cmd[7]=='B'&&cmd[8]=='U'&&
         cmd[9]=='G'&&cmd[10]==' '){
   unsigned v=0;
   if(decparse(cmd+11,&v)&&v<=65535){wifi_debug=(int)v;usb_send("WIFI DEBUG SET ");send_int(wifi_debug);usb_send("\\r\\n");}
   else usb_send("WIFI DEBUG INVALID\\r\\n");
 }
 else if(cmd[0]=='U'&&cmd[1]=='P'&&cmd[2]=='L'&&cmd[3]=='O'&&cmd[4]=='A'&&cmd[5]=='D'&&cmd[6]==' ')
   usb_upload_begin(cmd);
 else if(equals(cmd,"BOOTLOG"))usb_bootlog();''')
r(' char b[128];\n long n=readf(usbserial_fd,b,sizeof(b));',
  ' char b[4096];\n long n=readf(usbserial_fd,b,sizeof(b));')
r(' for(long i=0;i<n;i++){\n   char c=b[i];\n   if(c==', ''' long i=0;
 if(upl_fd>=0){
   long take=(unsigned long)n>upl_remaining?(long)upl_remaining:n;
   usb_upload_data(b,take);
   i=take;
 }
 for(;i<n;i++){
   char c=b[i];
   if(c==''')
r('     pause_200ms();','     if(upl_fd>=0){struct ts t={0,3000000};sc6(SYS_nanosleep,(long)&t,0,0,0,0,0);}else pause_200ms();')
# debug module opts: "debug=00000" chars index 6..10 is correct.
assert '#define SYS_delete_module 129' in s
assert 'WIFI_START' in s and 'WIFI_STOP' in s and 'UPLOAD READY' in s
(V/'init.c').write_text(s)
host=Path('/mnt/c/Users/olsen/XoomLinux/Phase1')
t=(host/'build-v13-userland.sh').read_text()
(host/'build-v14-userland.sh').write_text(t.replace('phase1-v13','phase1-v14').replace('V13','V14'))
print("Created v14 live Wi-Fi module reload and binary USB upload PID1",len(s),"bytes")
