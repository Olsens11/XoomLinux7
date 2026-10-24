#!/usr/bin/env python3
"""Produce non-destructive MZ600 diagnostic v03 source from proven v02 PID1."""
from pathlib import Path
base=Path('/home/xoomdev/xoom-linux-rom')
orig=(base/'phase1/initramfs/init.c').read_text()
out=base/'phase1-v03'
out.mkdir(parents=True, exist_ok=True)
s=orig
def sub(old,new):
 global s
 if s.count(old)!=1:raise ValueError("Patch anchor count "+str(s.count(old))+" for "+repr(old[:80]))
 s=s.replace(old,new,1)
sub('/* Xoom MZ604 phase-1 freestanding PID1, ARMv7 EABI, NO libc, NO NEON.',
    '/* Xoom MZ600 phase-1 v03 display diagnostic PID1, ARMv7 EABI, NO libc, NO NEON.')
sub(' writef(1,p,len);\n long c=openf("/dev/console",O_WRONLY);\n if(c>=0){writef(c,p,len);closef(c);}\n long k=openf("/dev/kmsg",O_WRONLY);\n if(k>=0){writef(k,p,len);closef(k);}',
''' long k=openf("/dev/kmsg",O_WRONLY);
 if(k>=0){writef(k,p,len);closef(k);}
 else writef(1,p,len); /* early boot only, before devtmpfs */''')
# suppress framebuffer console draw after mapping, and produce full clean graphic
anchor='static void framebuffer(void){'
board='''static int present(const char *p){
 long fd=openf(p,O_RDONLY);
 if(fd<0)return 0;
 closef(fd);
 return 1;
}
/* Repaint entire screen, not just uptime, to recover from stray fbcon writes. */
static void dashboard(unsigned long seconds){
 if(!screen)return;
 uint32_t bg=rgb(9,18,32),cyan=rgb(30,174,167);
 uint32_t white=rgb(236,245,248),mint=rgb(125,234,176),amber=rgb(244,189,103);
 fill(0,0,(int)vi.xres,(int)vi.yres,bg);
 fill(0,0,(int)vi.xres,18,cyan);
 text(42,42,"XOOM LINUX",5,white);
 text(42,128,"KERNEL BOOTED",4,mint);
 text(42,218,"MZ600 STINGRAY",3,white);
 text(42,285,"RAM ONLY - NO DATA MOUNTS",2,amber);
 int y=347;int step=(vi.yres>700)?49:34;
 text(42,y,"DISPLAY",2,white);text(290,y,"READY",2,mint);y+=step;
 text(42,y,"MMC STORAGE",2,white);
 text(290,y,present("/sys/class/mmc_host/mmc0")?"DETECTED":"NOT DETECTED",2,mint);y+=step;
 text(42,y,"INPUT",2,white);
 text(290,y,present("/sys/class/input/event0")?"PRESENT":"NOT DETECTED",2,mint);y+=step;
 text(42,y,"WIFI",2,white);
 text(290,y,present("/sys/class/net/wlan0")?"DETECTED":"NOT FOUND",2,amber);y+=step;
 text(42,y,"BATTERY",2,white);
 text(290,y,present("/sys/class/power_supply/battery")?"DETECTED":"NOT FOUND",2,amber);y+=step;
 text(42,y,"THERMAL",2,white);
 text(290,y,present("/sys/class/thermal/thermal_zone0")?"DETECTED":"NOT FOUND",2,mint);
 int foot=(int)vi.yres-83;
 if(foot>y+28){
  fill(40,foot-12,(int)vi.xres-80,1,rgb(67,100,120));
  text(42,foot,"UPTIME",2,white);
  text(182,foot,utoa(seconds),3,mint);
  text(300,foot,"SECONDS",2,white);
  fill(42,foot+39,(int)((seconds%60)*8),8,cyan);
 }
}
'''
sub(anchor,board+anchor)
sub(' screen=(volatile uint8_t *)(uintptr_t)m;\n msg2("framebuffer available - ",utoa(vi.xres));echo("xoom-init: screen ready\\n");\n fill(0,0,vi.xres,vi.yres,rgb(9,18,32));\n fill(0,0,vi.xres,18,rgb(28,146,143));\n text(42,58,"XOOM LINUX",5,rgb(250,250,250));\n text(42,145,"KERNEL BOOTED",4,rgb(124,224,176));\n text(42,250,"PHASE 1 - DIAGNOSTIC",3,rgb(204,215,223));\n text(42,340,"NO DATA MOUNTED",3,rgb(245,194,118));\n text(42,430,"TWRP NOT MODIFIED",3,rgb(202,212,218));',
''' screen=(volatile uint8_t *)(uintptr_t)m;
 /* Linux framebuffer console is not our UI. Prevent it repainting over us. */
 long tty=openf("/dev/tty0",O_RDWR);
 if(tty>=0){iof(tty,0x4b3a,(void *)1);closef(tty);} /* KDSETMODE KD_GRAPHICS */
 msg2("framebuffer mapped: ",utoa(vi.xres));
 dashboard(0);''')
sub(' dump("/proc/cmdline");', ''' /* RAM-only console log level control; detailed diagnostics remain in kmsg. */
 long pk=openf("/proc/sys/kernel/printk",O_WRONLY);
 if(pk>=0){const char low[]="0 4 1 7\\n";writef(pk,low,sizeof(low)-1);closef(pk);}
 dump("/proc/cmdline");''')
sub(' unsigned long seconds=0;\n unsigned long last_report=0;\n unsigned phase=0;',
    ' unsigned long seconds=0;\n unsigned long last_report=0;')
sub('   if(screen){\n     uint32_t c=rgb(28,146,143);\n     fill(42,vi.yres-110,550,40,rgb(9,18,32));\n     text(42,vi.yres-110,"UPTIME",2,rgb(190,225,230));\n     text(180,vi.yres-110,utoa(seconds),2,rgb(190,225,230));\n     fill(42,vi.yres-65,(int)phase*6,9,c);\n   }',
    '   if(screen)dashboard(seconds);')
sub('   phase+=5;if(phase>=80)phase=0;','')
# Reinforce safety and selftest stable
assert 'of=/dev/block' not in s and 'MS_RDONLY' in s
assert 'xoom-init: selftest process (not PID1)' in s
(out/'init.c').write_text(s)
print('V03 SOURCE',out/'init.c',len(s))
print('UNCHANGED BASE',base/'phase1/initramfs/init.c')
