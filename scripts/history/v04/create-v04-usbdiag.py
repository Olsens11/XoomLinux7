#!/usr/bin/env python3
from pathlib import Path
b=Path('/home/xoomdev/xoom-linux-rom')
v3=b/'phase1-v03/init.c'
d=b/'phase1-v04'
d.mkdir(exist_ok=True)
s=v3.read_text()
def edit(a,z):
 global s
 assert s.count(a)==1,(s.count(a),a[:80])
 s=s.replace(a,z,1)
edit('/* Xoom MZ600 phase-1 v03 display diagnostic PID1, ARMv7 EABI, NO libc, NO NEON.',
     '/* Xoom MZ600 phase-1 v04 USB CDC-ACM diagnostic PID1, ARMv7 EABI, no libc or NEON.')
edit('#define O_RDWR 2','#define O_RDWR 2\n#define O_NONBLOCK 0x800\n#define SYS_syslog 103')
mark='static void run_init(void){'
usb=r'''
/*
 * Minimal USB serial diagnostics:
 * CONFIG_USB_G_SERIAL=y presents one CDC ACM port, /dev/ttyGS0.
 * No /system,/data,/cache or external media reads/writes.
 * USB data interface requires physical cable. All commands are read-only.
 */
static long usbserial_fd=-1;
static unsigned long usb_poll_seconds;
static char usbline[160];
static int usbline_len;
static void usb_send(const char *s){
 if(usbserial_fd<0)return;
 long left=(long)slen(s);
 while(left>0){
   long n=writef(usbserial_fd,s,left);
   if(n<=0)break;
   s+=n;left-=n;
 }
}
static void usb_file(const char *path,int max_bytes){
 long f=openf(path,O_RDONLY);
 if(f<0){usb_send("UNAVAILABLE ");usb_send(path);usb_send("\r\n");return;}
 char buf[384];
 usb_send("=== ");usb_send(path);usb_send(" ===\r\n");
 int sent=0;
 for(;;){
   long r=readf(f,buf,(long)sizeof(buf)-1);
   if(r<=0)break;
   buf[r]=0;
   /* normalize CRLF for serial clients while preserving raw diagnostics */
   for(long i=0;i<r;i++)if(buf[i]=='\0')buf[i]=' ';
   if(sent+r>max_bytes)r=max_bytes-sent;
   if(r>0){
      buf[r]=0;
      usb_send(buf);
      sent+=(int)r;
   }
   if(sent>=max_bytes)break;
 }
 closef(f);
 usb_send("\r\n");
}
static void usb_logs(void){
 static char logbuf[8192]; /* kernel print ring, no block writes */
 long n=sc6(SYS_syslog,3,(long)logbuf,sizeof(logbuf)-1,0,0,0);
 if(n<0){usb_send("KERNEL LOG BUFFER UNAVAILABLE\r\n");return;}
 usb_send("=== KERNEL LOGS (LATEST 4KB) ===\r\n");
 long first=n>4096?n-4096:0;
 logbuf[n]=0;
 usb_send(logbuf+first);
 usb_send("\r\n=== END LOGS ===\r\n");
}
static void usb_command(const char *cmd){
 if(cmd[0]==0)return;
 if(cmd[0]=='H' && cmd[1]=='E' && cmd[2]=='L' && cmd[3]=='P' && cmd[4]==0){
   usb_send("XOOM LINUX MZ600 V04 USB SERIAL\r\n");
   usb_send("HELP PING STATUS CPU MEM STORAGE INPUT THERMAL USB LOGS CMDLINE\r\n");
 }else if(cmd[0]=='P' && cmd[1]=='I' && cmd[2]=='N' && cmd[3]=='G' && cmd[4]==0){
   usb_send("PONG XOOM-LINUX V04\r\n");
 }else if(cmd[0]=='S' && cmd[1]=='T' && cmd[2]=='A' && cmd[3]=='T' && cmd[4]=='U' && cmd[5]=='S' && cmd[6]==0){
   usb_send("SYSTEM XOOM LINUX MZ600\r\n");
   usb_file("/proc/uptime",150);
   usb_file("/proc/version",250);
   usb_file("/sys/class/udc",100);
   usb_send("MMC ");usb_send(present("/sys/class/mmc_host/mmc0")?"PRESENT":"MISSING");usb_send("\r\n");
   usb_send("FB ");usb_send(screen?"ACTIVE":"MISSING");usb_send("\r\n");
 }else if(cmd[0]=='C' && cmd[1]=='P' && cmd[2]=='U' && cmd[3]==0)usb_file("/proc/cpuinfo",1600);
 else if(cmd[0]=='M' && cmd[1]=='E' && cmd[2]=='M' && cmd[3]==0)usb_file("/proc/meminfo",1800);
 else if(cmd[0]=='S' && cmd[1]=='T' && cmd[2]=='O' && cmd[3]=='R' && cmd[4]=='A' && cmd[5]=='G' && cmd[6]=='E' && cmd[7]==0)usb_file("/proc/partitions",1400);
 else if(cmd[0]=='I' && cmd[1]=='N' && cmd[2]=='P' && cmd[3]=='U' && cmd[4]=='T' && cmd[5]==0)usb_file("/proc/bus/input/devices",2000);
 else if(cmd[0]=='T' && cmd[1]=='H' && cmd[2]=='E' && cmd[3]=='R' && cmd[4]=='M' && cmd[5]=='A' && cmd[6]=='L' && cmd[7]==0){
   usb_file("/sys/class/thermal/thermal_zone0/type",200);
   usb_file("/sys/class/thermal/thermal_zone0/temp",200);
   usb_file("/sys/class/thermal/thermal_zone1/type",200);
   usb_file("/sys/class/thermal/thermal_zone1/temp",200);
 }else if(cmd[0]=='U' && cmd[1]=='S' && cmd[2]=='B' && cmd[3]==0){
   usb_send("USB SERIAL ttyGS0 ACTIVE\r\n");
   usb_file("/sys/class/udc/ci_hdrc.0/state",250);
 }else if(cmd[0]=='L' && cmd[1]=='O' && cmd[2]=='G' && cmd[3]=='S' && cmd[4]==0)usb_logs();
 else if(cmd[0]=='C' && cmd[1]=='M' && cmd[2]=='D' && cmd[3]=='L' && cmd[4]=='I' && cmd[5]=='N' && cmd[6]=='E' && cmd[7]==0)usb_file("/proc/cmdline",1024);
 else usb_send("UNKNOWN COMMAND. SEND HELP\r\n");
}
static void poll_usb_serial(void){
 if(usbserial_fd<0){
   usbserial_fd=openf("/dev/ttyGS0",O_RDWR|O_NONBLOCK);
   if(usbserial_fd>=0)echo("xoom-init: USB ttyGS0 ready\n");
 }
 if(usbserial_fd<0)return;
 char b[128];
 long n=readf(usbserial_fd,b,sizeof(b));
 if(n<0)return; /* expected EAGAIN until host sends data */
 if(n==0)return;
 for(long i=0;i<n;i++){
   char c=b[i];
   if(c=='\r'||c=='\n'){
     usbline[usbline_len]=0;
     usb_command(usbline);
     usbline_len=0;
   }else if((unsigned char)c>=32 && (unsigned char)c<127){
     if(usbline_len<(int)sizeof(usbline)-2)usbline[usbline_len++]=c;
     else usbline_len=0;
   }
 }
 usb_poll_seconds++;
}
'''
# Important: string defined with raw backslash literals generated correctly? C \r\n literals from r-string should produce \r\n escapes
edit(mark,usb+'\n'+mark)
edit('   if(screen)dashboard(seconds);\n   pause_seconds(5);seconds+=5;',
     '   if(screen)dashboard(seconds);\n   for(int i=0;i<5;i++){poll_usb_serial();pause_seconds(1);}\n   seconds+=5;')
assert 'SYS_syslog 103' in s
(d/'init.c').write_text(s)
src=b/'linux-src/arch/arm/boot/dts/nvidia/tegra20-motorola-stingray.dts'
dst=b/'linux-src/arch/arm/boot/dts/nvidia/tegra20-motorola-stingray-usbdiag.dts'
dt=src.read_text()
old='usb@c5000000 {\n\t\tcompatible = "nvidia,tegra20-ehci"; \n\t\tstatus = "okay";\n\t\tdr_mode = "otg";'
new='usb@c5000000 {\n\t\tcompatible = "nvidia,tegra20-udc";\n\t\tstatus = "okay";\n\t\tdr_mode = "peripheral";'
assert dt.count(old)==1,('DTS USB compatible anchor',dt.count(old))
dt=dt.replace(old,new,1)
assert dt.count('usb-phy@c5000000 {')==1
dt=dt.replace('usb-phy@c5000000 {\n\t\tstatus = "okay";\n\t\tdr_mode = "otg";','usb-phy@c5000000 {\n\t\tstatus = "okay";\n\t\tdr_mode = "peripheral";',1)
intro='''// EXPERIMENTAL USB CDC-ACM diagnostic ONLY, no flash or battery enable
// USB0 gadget/peripheral mode override from Stingray v03; TWRP unchanged.
'''
if dst.exists(): assert dst.read_text()==intro+dt
else:dst.write_text(intro+dt)
mk=b/'linux-src/arch/arm/boot/dts/nvidia/Makefile'
s=mk.read_text()
old='\ttegra20-motorola-stingray.dtb \\\n'
new='\ttegra20-motorola-stingray.dtb \\\n\ttegra20-motorola-stingray-usbdiag.dtb \\\n'
assert s.count(old)==1
if new not in s: mk.write_text(s.replace(old,new,1))
print('V04 INIT SOURCE',d/'init.c',len((d/'init.c').read_bytes()))
print('V04 USB0 DTS',dst,len(dst.read_bytes()))
print('USB01 device tree change:',new.strip())

