#!/usr/bin/env python3
"""v06 grid: no-flash test UI, calibrated native touchscreen, crosshair, USB diagnostics."""
from pathlib import Path
b=Path("/home/xoomdev/xoom-linux-rom")
s=(b/"phase1-v05/init.c").read_text()
v=b/"phase1-v06"
v.mkdir(exist_ok=True)
def replace(a,z):
 global s
 assert s.count(a)==1,(s.count(a),a[:70])
 s=s.replace(a,z,1)
replace("/* Xoom MZ600 phase-1 v05 USB touchscreen diagnostic, guarded power ops. No libc/NEON.",
        "/* Xoom MZ600 phase-1 v06 touch grid and crosshair, USB diagnostics. No libc/NEON.")
start=s.index("/* Repaint entire screen, not just uptime")
end=s.index("static void framebuffer(void){",start)
grid=r'''
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
static uint32_t grid_bg_for(int x,int y){
 if(y<GRID_TOP||y>=GRID_BOTTOM)return rgb(9,18,32);
 const int cw=(int)vi.xres/GRID_COLS;
 const int ch=(GRID_BOTTOM-GRID_TOP)/GRID_ROWS;
 int col=x/cw,row=(y-GRID_TOP)/ch;
 if(col>=GRID_COLS)col=GRID_COLS-1;
 if(row>=GRID_ROWS)row=GRID_ROWS-1;
 if(x%cw==0||(y-GRID_TOP)%ch==0||x%cw==cw-1||(y-GRID_TOP)%ch==ch-1)
   return rgb(61,94,116); /* visible grid separators */
 if(row*GRID_COLS+col==grid_cell)return rgb(19,147,88);
 return ((col+row)&1)?rgb(22,37,56):rgb(15,29,45);
}
static void grid_repaint_cell(int cell){
 if(!screen||cell<0||cell>=GRID_COLS*GRID_ROWS)return;
 int cw=(int)vi.xres/GRID_COLS,ch=(GRID_BOTTOM-GRID_TOP)/GRID_ROWS;
 int col=cell%GRID_COLS,row=cell/GRID_COLS;
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
      if(dx>=-3&&dx<=3 || dy>=-3&&dy<=3 || (dx*dx+dy*dy>192&&dx*dx+dy*dy<255))
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
 int cell=(sy>=GRID_TOP&&sy<GRID_BOTTOM)?((sy-GRID_TOP)/120)*GRID_COLS+sx/160:-1;
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
'''
s=s[:start]+grid+s[end:]
replace(" dashboard(0);"," grid_scene();")
replace("   if(screen)dashboard_uptime(seconds);","   if(screen)grid_uptime(seconds);")
# add poll read loop after struct input_event32 declared, before touchfd
search="static long touchfd=-1;"
poll=r'''
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
 if(n%(long)sizeof(a[0])!=0)return;
 for(int i=0;i<n/(long)sizeof(a[0]);i++){
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
'''
replace(search,poll+"\n"+search)
replace("usb_send(\"XOOM LINUX MZ600 V05 USB TOUCH DIAGNOSTIC\\r\\n\");","usb_send(\"XOOM LINUX MZ600 V06 INTERACTIVE GRID TEST\\r\\n\");")
replace("usb_send(\"PONG XOOM-LINUX V05\\r\\n\");","usb_send(\"PONG XOOM-LINUX V06\\r\\n\");")
replace("usb_send(\"HELP PING STATUS CPU MEM STORAGE INPUT THERMAL USB LOGS CMDLINE TOUCH TOUCHSTOP REBOOT POWEROFF CANCEL\\r\\n\");",
        "usb_send(\"HELP PING STATUS CPU MEM STORAGE INPUT THERMAL USB LOGS CMDLINE GRID TOUCH TOUCHSTOP REBOOT POWEROFF CANCEL\\r\\n\");")
search=' else if(equals(cmd,"TOUCH"))touch_start();'
repl=r''' else if(equals(cmd,"GRID")){
   usb_send("GRID 8 COLS 5 ROWS, TOUCHSAFE, NO ACTIONS\r\n");
   usb_send("RAW X RANGE ");send_int(grid_minx);usb_send(" .. ");send_int(grid_maxx);
   usb_send(" Y RANGE ");send_int(grid_miny);usb_send(" .. ");send_int(grid_maxy);usb_send("\r\n");
   usb_send("LAST RAW X ");send_int(grid_rx);usb_send(" Y ");send_int(grid_ry);
   usb_send(" SCREEN X ");send_int(grid_sx);usb_send(" Y ");send_int(grid_sy);
   usb_send(" ACTIVE CELL ");send_int(grid_cell+1);usb_send("\r\n");
 }
 else if(equals(cmd,"TOUCH"))touch_start();'''
replace(search,repl)
replace('     poll_usb_serial();\n     poll_touch();',
        '     poll_usb_serial();\n     grid_poll_input();\n     poll_touch();')
# 50ms polls for responsive tracking, 100 cycles per 5s, 20sec safety still exact
replace('   for(int i=0;i<25;i++){','   for(int i=0;i<100;i++){')
replace('static void pause_200ms(void){struct ts t={0,200000000};','static void pause_200ms(void){struct ts t={0,50000000};')
replace('touch_ticks_remaining=75;', 'touch_ticks_remaining=300;')
replace('pending_power_ticks=100;', 'pending_power_ticks=400;')
# For 15 secs and 20s, power/harness moved to 50ms period. Touch report ticks gate was ~0.6s -> use 12 cycles.
replace('touch_ticks-touch_last_sent_tick>=3','touch_ticks-touch_last_sent_tick>=12')
# Important shift because v05 C uses 6th argument to reboot; no changes to destructive controls.
assert 'grid_scene();' in s and 'grid_poll_input();' in s
assert 'dashboard(' not in s and 'dashboard_uptime(' not in s
assert 'xoom-grid: event2 read-only auto UI' in s
(v/"init.c").write_text(s)
print("v06 source bytes",len(s))
print("Crosshair+grid+native ioctl calibration+USB GRID status ready")
