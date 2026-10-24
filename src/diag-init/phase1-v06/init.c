/* Xoom MZ600 phase-1 v06 touch grid and crosshair, USB diagnostics. No libc/NEON.
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
#define O_NONBLOCK 0x800
#define SYS_syslog 103
#define SYS_reboot 88
#define RB_MAGIC1 0xfee1deadUL
#define RB_MAGIC2 672274793UL
#define RB_AUTOBOOT 0x01234567UL
#define RB_POWER_OFF 0x4321fedcUL
#define EV_SYN 0
#define EV_KEY 1
#define EV_ABS 3
#define SYN_REPORT 0
#define BTN_TOUCH 330
#define ABS_MT_SLOT 47
#define ABS_MT_POSITION_X 53
#define ABS_MT_POSITION_Y 54
#define ABS_MT_TRACKING_ID 57
/* Freestanding compiler helper; no libc. */
void *memset(void *dst,int value,size_t n){
 volatile unsigned char *b=(volatile unsigned char *)dst;
 for(size_t i=0;i<n;i++)b[i]=(unsigned char)value;
 return dst;
}
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
static void pause_200ms(void){struct ts t={0,50000000};sc6(SYS_nanosleep,(long)&t,0,0,0,0,0);}
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

/* Xoom native 1280x800 framebuffer with eight-by-five safe touch targets.
 * No action is triggered by touching any cell: visual testing ONLY.
 * Header and footer deliberately separate from 40 target cells.
 * Event read is completely read-only. */
#define GRID_COLS 8
#define GRID_ROWS 5
#define GRID_TOP 104
#define GRID_BOTTOM 704
static int grid_minx=10,grid_maxx=2569,grid_miny=15,grid_maxy=1614;
static int grid_cell=-1,grid_finger=0,grid_rx=-1,grid_ry=-1;
static int grid_sx=-1,grid_sy=-1,grid_cross_x=-1,grid_cross_y=-1;
static int grid_framebuffer_ready=0;
static uint32_t grid_div(uint32_t n,uint32_t d);
static uint32_t grid_bg_for(int x,int y){
 if(y<GRID_TOP||y>=GRID_BOTTOM)return rgb(9,18,32);
 const int cw=160;
 const int ch=120;
 int col=(int)grid_div((uint32_t)x,(uint32_t)cw),row=(int)grid_div((uint32_t)(y-GRID_TOP),(uint32_t)ch);
 if(col>=GRID_COLS)col=GRID_COLS-1;
 if(row>=GRID_ROWS)row=GRID_ROWS-1;
 if(x-col*cw==0||(y-GRID_TOP)-row*ch==0||x-col*cw==cw-1||(y-GRID_TOP)-row*ch==ch-1)
   return rgb(61,94,116); /* visible grid separators */
 if(row*GRID_COLS+col==grid_cell)return rgb(19,147,88);
 return ((col+row)&1)?rgb(22,37,56):rgb(15,29,45);
}
static void grid_repaint_cell(int cell){
 if(!screen||cell<0||cell>=GRID_COLS*GRID_ROWS)return;
 int cw=160,ch=120;
 int col=cell&7,row=cell>>3;
 int x0=col*cw,y0=GRID_TOP+row*ch;
 /* repaint only changed cell. 160x120 px on 1280x800 display. */
 for(int y=y0;y<y0+ch;y++)for(int x=x0;x<x0+cw;x++)px(x,y,grid_bg_for(x,y));
}
static void grid_cross_restore(void){
 if(grid_cross_x<0||grid_cross_y<GRID_TOP||!screen)return;
 for(int dy=-22;dy<=22;dy++){
   int y=grid_cross_y+dy;
   if(y<GRID_TOP||y>=GRID_BOTTOM)continue;
   for(int dx=-22;dx<=22;dx++){
      int x=grid_cross_x+dx;
      if(x<0||x>=(int)vi.xres)continue;
      if((dx>=-3&&dx<=3) || (dy>=-3&&dy<=3) || (dx*dx+dy*dy>192&&dx*dx+dy*dy<255))
         px(x,y,grid_bg_for(x,y));
   }
 }
 grid_cross_x=-1;grid_cross_y=-1;
}
static void grid_cross_paint(int x,int y){
 if(!screen||x<0||x>=(int)vi.xres||y<GRID_TOP||y>=GRID_BOTTOM)return;
 uint32_t shade=rgb(0,0,0),white=rgb(255,255,255);
 /* black halo + white cross, limited to 45x45 pixels */
 for(int k=-19;k<=19;k++){
   if(k>=-6&&k<=6)continue;
   for(int o=-2;o<=2;o++){
      px(x+k,y+o,shade);px(x+o,y+k,shade);
   }
   px(x+k,y,white);px(x,y+k,white);
 }
 fill(x-3,y-3,7,7,white);
 fill(x-1,y-1,3,3,rgb(18,72,62));
 grid_cross_x=x;grid_cross_y=y;
}
static void grid_line_number(int x,int y,int n,int width){
 if(!screen)return;
 fill(x,y,width,29,rgb(9,18,32));
 if(n<0){text(x,y,"-",3,rgb(241,192,94));return;}
 text(x,y,utoa((unsigned long)n),3,rgb(139,243,188));
}
/* Fixed pixel ranges from original MZ600 recovery, revalidated at runtime
 * using read-only EVIOCGABS on the new Atmel input device. */
static uint32_t grid_div(uint32_t n,uint32_t d){
 if(!d)return 0;
 uint32_t q=0,r=0;
 for(int i=31;i>=0;i--){
   r=(r<<1)|((n>>i)&1u);
   if(r>=d){r-=d;q|=(1u<<i);}
 }
 return q;
}
static int grid_scale(int raw,int low,int high,int dim){
 if(dim<=1||high<=low)return 0;
 if(raw<=low)return 0;
 if(raw>=high)return dim-1;
 uint32_t n=(uint32_t)(raw-low)*(uint32_t)(dim-1)+(uint32_t)(high-low)/2u;
 return (int)grid_div(n,(uint32_t)(high-low));
}
static void grid_touch_update(int rawx,int rawy,int down){
 if(rawx<0||rawy<0||!screen)return;
 int sx=grid_scale(rawx,grid_minx,grid_maxx,(int)vi.xres);
 int sy=grid_scale(rawy,grid_miny,grid_maxy,(int)vi.yres);
 int cell=(sy>=GRID_TOP&&sy<GRID_BOTTOM)?(int)(grid_div((uint32_t)(sy-GRID_TOP),120u)*GRID_COLS+grid_div((uint32_t)sx,160u)):-1;
 if(cell>=40)cell=39;
 if(rawx==grid_rx&&rawy==grid_ry&&down==grid_finger&&cell==grid_cell)return;
 int old_cell=grid_cell,oldx=grid_cross_x,oldy=grid_cross_y;
 /* Unpaint crosshair before repainting any cell, then add it last. */
 grid_cross_restore();
 grid_rx=rawx;grid_ry=rawy;grid_sx=sx;grid_sy=sy;grid_finger=down;
 if(down&&cell>=0)grid_cell=cell; /* released cell stays green until next */
 if(grid_cell!=old_cell){grid_repaint_cell(old_cell);grid_repaint_cell(grid_cell);}
 /* Update just the six changed values, never the entire screen. */
 grid_line_number(178,56,grid_rx,110);
 grid_line_number(410,56,grid_ry,110);
 grid_line_number(681,56,grid_sx,110);
 grid_line_number(917,56,grid_sy,110);
 grid_line_number(1135,56,grid_cell>=0?grid_cell+1:0,65);
 /* show crosshair only while finger is pressed in grid area */
 if(down&&cell>=0)grid_cross_paint(sx,sy);
 (void)oldx;(void)oldy;
}
static void grid_scene(void){
 if(!screen)return;
 grid_cell=-1;grid_cross_x=-1;grid_cross_y=-1;
 fill(0,0,(int)vi.xres,(int)vi.yres,rgb(9,18,32));
 for(int cell=0;cell<40;cell++)grid_repaint_cell(cell);
 fill(0,0,(int)vi.xres,6,rgb(30,174,167));
 text(22,17,"XOOM LINUX V06 - TOUCH GRID",3,rgb(234,246,246));
 text(22,57,"RAW X",2,rgb(187,205,222));
 text(288,57,"RAW Y",2,rgb(187,205,222));
 text(535,57,"MAP X",2,rgb(187,205,222));
 text(775,57,"MAP Y",2,rgb(187,205,222));
 text(1030,57,"CELL",2,rgb(187,205,222));
 fill(0,GRID_BOTTOM,(int)vi.xres,2,rgb(30,174,167));
 text(22,724,"TOUCH OR DRAG TO HIGHLIGHT GRID CELLS",2,rgb(237,245,245));
 text(22,765,"LAST CELL STAYS GREEN - NO ACTIONS",2,rgb(147,197,210));
 text(925,765,"UPTIME",2,rgb(237,245,245));
 grid_line_number(178,56,-1,110);grid_line_number(410,56,-1,110);
 grid_line_number(681,56,-1,110);grid_line_number(917,56,-1,110);
 grid_line_number(1135,56,-1,65);
 grid_framebuffer_ready=1;
}
static void grid_uptime(unsigned long s){
 if(!screen)return;
 fill(1040,755,165,32,rgb(9,18,32));
 text(1045,760,utoa(s),2,rgb(139,243,188));
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
 grid_scene();
 return;
fail:
 closef(fbfd);fbfd=-1;
}

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

/* No event injection, grabs or writes; input events are observed read-only. */
struct input_event32 {int32_t sec;int32_t usec;uint16_t type;uint16_t code;int32_t value;};
_Static_assert(sizeof(struct input_event32)==16,"ARM input_event layout");

static long grid_eventfd=-1;
static int grid_slot=0,grid_touch_id=-1,grid_touch_down=0;
static int grid_rawx=-1,grid_rawy=-1;
struct absinfo_v06 {int32_t value,min,max,fuzz,flat,resolution;};
_Static_assert(sizeof(struct absinfo_v06)==24,"ABS ioctl layout");
static void grid_calibrate(long fd){
 struct absinfo_v06 x={0},y={0};
 /* EVIOCGABS(ABS_MT_POSITION_X/Y) = _IOR('E',0x40+code,struct input_absinfo) */
 long xret=iof(fd,0x80184575UL,&x),yret=iof(fd,0x80184576UL,&y);
 if(xret>=0&&yret>=0&&x.max>x.min&&y.max>y.min &&
    x.max-x.min>=100&&y.max-y.min>=100 &&
    x.max-x.min<100000&&y.max-y.min<100000){
    grid_minx=x.min;grid_maxx=x.max;grid_miny=y.min;grid_maxy=y.max;
    echo("xoom-grid: EVIOCGABS coordinate bounds read from live touchscreen\n");
 }else echo("xoom-grid: fallback to verified recovery calibration bounds\n");
}
static void grid_poll_input(void){
 if(grid_eventfd<0){
   grid_eventfd=openf("/dev/input/event2",O_RDONLY|O_NONBLOCK);
   if(grid_eventfd>=0){grid_calibrate(grid_eventfd);echo("xoom-grid: event2 read-only auto UI\n");}
 }
 if(grid_eventfd<0)return;
 struct input_event32 a[64];
 long n=readf(grid_eventfd,a,sizeof(a));
 if(n<=0)return;
 if((n&15L)!=0)return;
 for(int i=0;i<(n>>4);i++){
   struct input_event32 *e=&a[i];
   if(e->type==EV_ABS){
     if(e->code==ABS_MT_SLOT)grid_slot=e->value;
     else if(grid_slot==0&&e->code==ABS_MT_POSITION_X)grid_rawx=e->value;
     else if(grid_slot==0&&e->code==ABS_MT_POSITION_Y)grid_rawy=e->value;
     else if(grid_slot==0&&e->code==ABS_MT_TRACKING_ID){
       grid_touch_id=e->value;
       grid_touch_down=e->value>=0;
     }
   }else if(e->type==EV_KEY&&e->code==BTN_TOUCH){
       grid_touch_down=(e->value>0);
   }else if(e->type==EV_SYN&&e->code==SYN_REPORT){
     grid_touch_update(grid_rawx,grid_rawy,grid_touch_down);
   }
 }
}

static long touchfd=-1;
static int touch_ticks_remaining;
static unsigned touch_ticks, touch_frames, touch_reports;
static int32_t touch_x, touch_y, touch_id, touch_pressed;
static int touch_dirty, touch_tracking_changed, touch_last_sent_tick;

static void send_int(int32_t n){
 if(n<0){usb_send("-");usb_send(utoa((unsigned long)(-(int64_t)n)));}
 else usb_send(utoa((unsigned long)n));
}
static int equals(const char *a,const char *b){
 while(*a&&*b){if(*a!=*b)return 0;a++;b++;}
 return *a==0&&*b==0;
}
static void touch_report(void){
 if(touch_reports>=60)return;
 usb_send("TOUCH x=");send_int(touch_x);
 usb_send(" y=");send_int(touch_y);
 usb_send(" id=");send_int(touch_id);
 usb_send(" down=");send_int(touch_pressed);
 usb_send("\r\n");
 touch_reports++;
 touch_last_sent_tick=(int)touch_ticks;
}
static void touch_stop(void){
 if(touchfd>=0){closef(touchfd);touchfd=-1;}
 if(touch_ticks_remaining>0||touch_ticks>0){
   usb_send("TOUCH COMPLETE: frames=");usb_send(utoa(touch_frames));
   usb_send(" reports=");usb_send(utoa(touch_reports));usb_send("\r\n");
 }
 touch_ticks_remaining=0;touch_ticks=0;touch_dirty=0;
}
static void touch_start(void){
 if(touchfd>=0)touch_stop();
 touchfd=openf("/dev/input/event2",O_RDONLY|O_NONBLOCK);
 if(touchfd<0){usb_send("TOUCH ERROR: cannot open /dev/input/event2 (read-only)\r\n");return;}
 touch_ticks_remaining=300;touch_ticks=0;touch_frames=0;touch_reports=0;
 touch_x=-1;touch_y=-1;touch_id=-1;touch_pressed=0;
 touch_dirty=0;touch_tracking_changed=0;touch_last_sent_tick=-100;
 usb_send("TOUCH CAPTURE STARTED: touch and swipe display now for 15 seconds.\r\n");
 usb_send("Read-only events from Atmel maXTouch /dev/input/event2.\r\n");
}
static void poll_touch(void){
 if(touch_ticks_remaining<=0||touchfd<0)return;
 struct input_event32 events[64];
 long n=readf(touchfd,events,sizeof(events));
 if(n>0){
   if(n%(long)sizeof(events[0])!=0){
     usb_send("TOUCH ERROR: unexpected input_event alignment\r\n");
     touch_stop();return;
   }
   for(int i=0;i<n/(long)sizeof(events[0]);i++){
     const struct input_event32 *e=&events[i];
     if(e->type==EV_KEY&&e->code==BTN_TOUCH){touch_pressed=e->value;touch_dirty=1;touch_tracking_changed=1;}
     if(e->type==EV_ABS){
       if(e->code==ABS_MT_POSITION_X){touch_x=e->value;touch_dirty=1;}
       if(e->code==ABS_MT_POSITION_Y){touch_y=e->value;touch_dirty=1;}
       if(e->code==ABS_MT_TRACKING_ID){touch_id=e->value;touch_dirty=1;touch_tracking_changed=1;}
     }
     if(e->type==EV_SYN&&e->code==SYN_REPORT){
       touch_frames++;
       if(touch_dirty&&(touch_tracking_changed||(int)touch_ticks-touch_last_sent_tick>=12)){
         touch_report();touch_dirty=0;touch_tracking_changed=0;
       }
     }
   }
 }
 touch_ticks++;
 if(--touch_ticks_remaining==0)touch_stop();
}
/* In-memory guard, automatically disarms after 20 seconds. No button or touch triggers these. */
static int pending_power; /* 1=reboot; 2=poweroff */
static int pending_power_ticks;
static void power_arm(int mode){
 pending_power=mode;pending_power_ticks=400;
 usb_send(mode==1?"REBOOT ARMED: send CONFIRM REBOOT within 20 seconds.\r\n":"POWEROFF ARMED: send CONFIRM POWEROFF within 20 seconds.\r\n");
}
static void power_execute(int mode){
 if(pending_power!=mode||pending_power_ticks<=0){
   usb_send("POWER DENIED: expired or not armed. Send REBOOT or POWEROFF first.\r\n");return;
 }
 pending_power=0;pending_power_ticks=0;
 if(touchfd>=0){closef(touchfd);touchfd=-1;}
 usb_send(mode==1?"EXECUTING REBOOT NOW\r\n":"EXECUTING POWEROFF NOW\r\n");
 echo(mode==1?"xoom-init: requested USB-confirmed reboot\n":"xoom-init: requested USB-confirmed poweroff\n");
 long r=sc6(SYS_reboot,RB_MAGIC1,RB_MAGIC2,mode==1?RB_AUTOBOOT:RB_POWER_OFF,0,0,0);
 if(r<0){usb_send("POWER SYSCALL FAILED errno=");send_int((int32_t)-r);usb_send("\r\n");}
}
static void usb_command(const char *cmd){
 if(cmd[0]==0)return;
 if(cmd[0]=='H' && cmd[1]=='E' && cmd[2]=='L' && cmd[3]=='P' && cmd[4]==0){
   usb_send("XOOM LINUX MZ600 V06 INTERACTIVE GRID TEST\r\n");
   usb_send("HELP PING STATUS CPU MEM STORAGE INPUT THERMAL USB LOGS CMDLINE GRID TOUCH TOUCHSTOP REBOOT POWEROFF CANCEL\r\n");
 }else if(cmd[0]=='P' && cmd[1]=='I' && cmd[2]=='N' && cmd[3]=='G' && cmd[4]==0){
   usb_send("PONG XOOM-LINUX V06\r\n");
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
 else if(equals(cmd,"GRID")){
   usb_send("GRID 8 COLS 5 ROWS, TOUCHSAFE, NO ACTIONS\r\n");
   usb_send("RAW X RANGE ");send_int(grid_minx);usb_send(" .. ");send_int(grid_maxx);
   usb_send(" Y RANGE ");send_int(grid_miny);usb_send(" .. ");send_int(grid_maxy);usb_send("\r\n");
   usb_send("LAST RAW X ");send_int(grid_rx);usb_send(" Y ");send_int(grid_ry);
   usb_send(" SCREEN X ");send_int(grid_sx);usb_send(" Y ");send_int(grid_sy);
   usb_send(" ACTIVE CELL ");send_int(grid_cell+1);usb_send("\r\n");
 }
 else if(equals(cmd,"TOUCH"))touch_start();
 else if(equals(cmd,"TOUCHSTOP"))touch_stop();
 else if(equals(cmd,"REBOOT"))power_arm(1);
 else if(equals(cmd,"POWEROFF"))power_arm(2);
 else if(equals(cmd,"CONFIRM REBOOT"))power_execute(1);
 else if(equals(cmd,"CONFIRM POWEROFF"))power_execute(2);
 else if(equals(cmd,"CANCEL")){pending_power=0;pending_power_ticks=0;usb_send("POWER ACTION CANCELLED\r\n");}
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
   if(screen)grid_uptime(seconds);
   for(int i=0;i<100;i++){
     poll_usb_serial();
     grid_poll_input();
     poll_touch();
     if(pending_power_ticks>0&&--pending_power_ticks==0){pending_power=0;usb_send("POWER CONFIRMATION EXPIRED\r\n");}
     pause_200ms();
   }
   seconds+=5;

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
