/* Xoom MZ600 phase-1 v03 display diagnostic PID1, ARMv7 EABI, NO libc, NO NEON.
 * Direct system calls; does NOT mount/write any block storage.
 * Kernel console and optional fb0 splash. Never flash without hardware preflight.
 */
#include <linux/fb.h>
#include <stdint.h>
#include <stddef.h>
#define SYS_exit 1
#define SYS_read 3
#define SYS_write 4
#define SYS_open 5
#define SYS_close 6
#define SYS_getpid 20
#define SYS_mount 21
#define SYS_ioctl 54
#define SYS_nanosleep 162
#define SYS_mmap2 192
#define SYS_getdents64 217
#define MS_RDONLY 1
#define MS_NOSUID 2
#define MS_NODEV 4
#define MS_NOEXEC 8
#define O_RDONLY 0
#define O_WRONLY 1
#define O_RDWR 2
static long sc6(long nr,long a,long b,long c,long d,long e,long f) {
 register long r0 asm("r0")=a, r1 asm("r1")=b, r2 asm("r2")=c;
 register long r3 asm("r3")=d, r4 asm("r4")=e, r5 asm("r5")=f;
 register long r7 asm("r7")=nr;
 asm volatile("svc 0" : "+r"(r0) : "r"(r1),"r"(r2),"r"(r3),"r"(r4),"r"(r5),"r"(r7) : "memory","cc");
 return r0;
}
static long openf(const char *n,long flags){return sc6(SYS_open,(long)n,flags,0,0,0,0);}
static void closef(long fd){sc6(SYS_close,fd,0,0,0,0,0);}
static long readf(long fd,void *p,long len){return sc6(SYS_read,fd,(long)p,len,0,0,0);}
static long writef(long fd,const void *p,long len){return sc6(SYS_write,fd,(long)p,len,0,0,0);}
static long iof(long fd,long req,void *p){return sc6(SYS_ioctl,fd,req,(long)p,0,0,0);}
static long mountf(const char *src,const char *where,const char *type,long flags){
 return sc6(SYS_mount,(long)src,(long)where,(long)type,flags,(long)"",0);
}
struct ts {long sec;long nano;};
static void pause_seconds(long sec){struct ts t={sec,0};sc6(SYS_nanosleep,(long)&t,0,0,0,0,0);}
static size_t slen(const char *s){size_t n=0;while(s[n])n++;return n;}
static void echo(const char *p){
 long len=(long)slen(p);
 long k=openf("/dev/kmsg",O_WRONLY);
 if(k>=0){writef(k,p,len);closef(k);}
 else writef(1,p,len); /* early boot only, before devtmpfs */
}
static char number[24];
static const char *utoa(unsigned long x){
 static const unsigned long units[]={1000000000ul,100000000ul,10000000ul,1000000ul,100000ul,10000ul,1000ul,100ul,10ul,1ul};
 int j=0,started=0;
 for(unsigned i=0;i<10;i++){
   unsigned char digit=0;
   while(x>=units[i]){x-=units[i];digit++;}
   if(digit||started||i==9){number[j++]=(char)('0'+digit);started=1;}
 }
 number[j]=0;
 return number;
}
static void msg2(const char *a,const char *b) {echo("xoom-init: ");echo(a);echo(b);echo("\n");}
static void dump(const char *p){
 long f=openf(p,O_RDONLY);
 if(f<0){msg2("unavailable: ",p);return;}
 char b[320];long n=readf(f,b,sizeof(b)-1);closef(f);
 if(n>0){b[n]=0;for(int i=0;i<n;i++)if(b[i]=='\n'||b[i]=='\r')b[i]=' ';
 msg2(p," ");echo(b);echo("\n");}
}
struct linux_dirent64 {
 uint64_t d_ino; int64_t d_off; unsigned short d_reclen; unsigned char d_type;char d_name[];
};
static void ls(const char *path){
 long fd=openf(path,O_RDONLY);
 if(fd<0){msg2("unavailable dir: ",path);return;}
 msg2("PROBING ",path);
 char b[1024];
 for(int rounds=0;rounds<2;rounds++){
 long n=sc6(SYS_getdents64,fd,(long)b,sizeof(b),0,0,0);
 if(n<=0)break;
 for(long off=0;off+19<n;){
   struct linux_dirent64 *e=(void*)(b+off);
   if(e->d_reclen<19||off+e->d_reclen>n)break;
   if(e->d_name[0]!='.')msg2("  ",e->d_name);
   off+=e->d_reclen;
 }
 }
 closef(fd);
}
static long fbfd=-1;
static volatile uint8_t *screen;
static size_t screen_bytes;
static struct fb_fix_screeninfo fi;
static struct fb_var_screeninfo vi;
static uint32_t rgb(uint8_t r,uint8_t g,uint8_t b){
 return ((((uint32_t)r*((1u<<vi.red.length)-1u))/255u)<<vi.red.offset)
       |((((uint32_t)g*((1u<<vi.green.length)-1u))/255u)<<vi.green.offset)
       |((((uint32_t)b*((1u<<vi.blue.length)-1u))/255u)<<vi.blue.offset);
}
static void px(int x,int y,uint32_t v){
 if(!screen||x<0||y<0||(uint32_t)x>=vi.xres||(uint32_t)y>=vi.yres)return;
 size_t nb=vi.bits_per_pixel/8;
 size_t at=(size_t)y*(size_t)fi.line_length+(size_t)x*nb;
 if(at+nb>screen_bytes)return;
 for(size_t j=0;j<nb;j++)screen[at+j]=(uint8_t)(v>>(j*8));
}
static void fill(int x,int y,int w,int h,uint32_t c){
 if(!screen||x<0||y<0)return;
 if((uint32_t)x>=vi.xres||(uint32_t)y>=vi.yres)return;
 if(x+w>(int)vi.xres)w=(int)vi.xres-x;
 if(y+h>(int)vi.yres)h=(int)vi.yres-y;
 for(int yy=y;yy<y+h;yy++)for(int xx=x;xx<x+w;xx++)px(xx,yy,c);
}
static const struct{char c;uint8_t a[5];} glyph[]={
{'A',{0x7e,0x11,0x11,0x11,0x7e}},{'B',{0x7f,0x49,0x49,0x49,0x36}},
{'C',{0x3e,0x41,0x41,0x41,0x22}},{'D',{0x7f,0x41,0x41,0x22,0x1c}},
{'E',{0x7f,0x49,0x49,0x49,0x41}},{'F',{0x7f,0x09,0x09,0x09,0x01}},
{'G',{0x3e,0x41,0x49,0x49,0x7a}},{'H',{0x7f,0x08,0x08,0x08,0x7f}},
{'I',{0x41,0x41,0x7f,0x41,0x41}},{'J',{0x20,0x40,0x41,0x3f,0x01}},
{'K',{0x7f,0x08,0x14,0x22,0x41}},{'L',{0x7f,0x40,0x40,0x40,0x40}},
{'M',{0x7f,0x02,0x0c,0x02,0x7f}},{'N',{0x7f,0x04,0x08,0x10,0x7f}},
{'O',{0x3e,0x41,0x41,0x41,0x3e}},{'P',{0x7f,0x09,0x09,0x09,0x06}},
{'Q',{0x3e,0x41,0x51,0x21,0x5e}},{'R',{0x7f,0x09,0x19,0x29,0x46}},
{'S',{0x46,0x49,0x49,0x49,0x31}},{'T',{0x01,0x01,0x7f,0x01,0x01}},
{'U',{0x3f,0x40,0x40,0x40,0x3f}},{'V',{0x1f,0x20,0x40,0x20,0x1f}},
{'W',{0x7f,0x20,0x18,0x20,0x7f}},{'X',{0x63,0x14,0x08,0x14,0x63}},
{'Y',{0x07,0x08,0x70,0x08,0x07}},{'Z',{0x61,0x51,0x49,0x45,0x43}},
{'0',{0x3e,0x45,0x49,0x51,0x3e}},{'1',{0,0x42,0x7f,0x40,0}},
{'2',{0x42,0x61,0x51,0x49,0x46}},{'3',{0x21,0x41,0x45,0x4b,0x31}},
{'4',{0x18,0x14,0x12,0x7f,0x10}},{'5',{0x27,0x45,0x45,0x45,0x39}},
{'6',{0x3c,0x4a,0x49,0x49,0x30}},{'7',{0x01,0x71,0x09,0x05,0x03}},
{'8',{0x36,0x49,0x49,0x49,0x36}},{'9',{0x06,0x49,0x49,0x29,0x1e}},
{' ',{0,0,0,0,0}},{'-',{0x08,0x08,0x08,0x08,0x08}},
{':',{0,0x36,0x36,0,0}},
};
static void text(int x,int y,const char *s,int scale,uint32_t col){
 for(;*s;s++,x+=6*scale){
   const uint8_t *g=0;
   for(size_t i=0;i<sizeof(glyph)/sizeof(glyph[0]);i++)
     if(glyph[i].c==*s){g=glyph[i].a;break;}
   if(!g)continue;
   for(int c=0;c<5;c++)for(int r=0;r<7;r++)
     if((g[c]>>r)&1u)fill(x+c*scale,y+r*scale,scale,scale,col);
 }
}
static int present(const char *p){
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
  fill(42,foot+39,(int)((seconds&63ul)*8),8,cyan);
 }
}
static void framebuffer(void){
 fbfd=openf("/dev/fb0",O_RDWR);if(fbfd<0)return;
 if(iof(fbfd,FBIOGET_FSCREENINFO,&fi)<0||iof(fbfd,FBIOGET_VSCREENINFO,&vi)<0)goto fail;
 if(vi.xres<320||vi.yres<240||vi.xres>4096||vi.yres>4096)goto fail;
 if(vi.bits_per_pixel!=16&&vi.bits_per_pixel!=32)goto fail;
 screen_bytes=fi.smem_len;
 if(screen_bytes<(size_t)fi.line_length*vi.yres||screen_bytes>64u*1024u*1024u)goto fail;
 long m=sc6(SYS_mmap2,0,screen_bytes,3,1,fbfd,0);
 if(m<0&&m>=-4095)goto fail;
 screen=(volatile uint8_t *)(uintptr_t)m;
 /* Linux framebuffer console is not our UI. Prevent it repainting over us. */
 long tty=openf("/dev/tty0",O_RDWR);
 if(tty>=0){iof(tty,0x4b3a,(void *)1);closef(tty);} /* KDSETMODE KD_GRAPHICS */
 msg2("framebuffer mapped: ",utoa(vi.xres));
 dashboard(0);
 return;
fail:
 closef(fbfd);fbfd=-1;
}
static void run_init(void){
 echo("xoom-init: Xoom Linux Phase1: freestanding no-NEON PID1\n");
 const char *src[]={"devtmpfs","proc","sysfs","tmpfs","tmpfs"};
 const char *target[]={"/dev","/proc","/sys","/run","/tmp"};
 const long flags[]={MS_NOSUID,MS_NOSUID|MS_NODEV|MS_NOEXEC,
 MS_NOSUID|MS_NODEV|MS_NOEXEC|MS_RDONLY,MS_NOSUID|MS_NODEV,MS_NOSUID|MS_NODEV};
 for(int i=0;i<5;i++){
   long r=mountf(src[i],target[i],src[i],flags[i]);
   msg2(r<0?"mount FAILED: ":"mount OK: ",target[i]);
 }
 /* RAM-only console log level control; detailed diagnostics remain in kmsg. */
 long pk=openf("/proc/sys/kernel/printk",O_WRONLY);
 if(pk>=0){const char low[]="0 4 1 7\n";writef(pk,low,sizeof(low)-1);closef(pk);}
 dump("/proc/cmdline");dump("/proc/cpuinfo");dump("/proc/meminfo");dump("/proc/partitions");
 ls("/sys/class/mmc_host");ls("/sys/class/drm");ls("/sys/class/input");
 ls("/sys/class/net");ls("/sys/class/power_supply");ls("/sys/class/thermal");
 echo("xoom-init: STAYING IN RAM - no system/userdata/cache mounts\n");
 unsigned long seconds=0;
 unsigned long last_report=0;
 for(;;) {
   if(fbfd<0)framebuffer();
   if(screen)dashboard(seconds);
   pause_seconds(5);seconds+=5;

   if(seconds-last_report>=60){last_report=seconds;msg2("heartbeat seconds: ",utoa(seconds));ls("/sys/class/mmc_host");ls("/sys/class/drm");}
 }
}
void _start(void) __attribute__((noreturn));
void _start(void) {
 if(sc6(SYS_getpid,0,0,0,0,0,0)!=1) {
   echo("xoom-init: selftest process (not PID1) - no mounts attempted\n");
   sc6(SYS_exit,0,0,0,0,0,0);
   for(;;){}
 }
 run_init();
 for(;;)pause_seconds(60);
}
