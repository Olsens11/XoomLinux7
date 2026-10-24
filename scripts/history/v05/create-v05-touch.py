#!/usr/bin/env python3
"""Extend verified USB v04 with read-only 15s touchscreen sampling and optional guarded power controls."""
from pathlib import Path
base=Path('/home/xoomdev/xoom-linux-rom')
src=base/'phase1-v04/init.c'
dst=base/'phase1-v05'
dst.mkdir(exist_ok=True)
s=src.read_text()
def rep(old,new):
 global s
 assert s.count(old)==1,(s.count(old),old[:100])
 s=s.replace(old,new,1)
rep('/* Xoom MZ600 phase-1 v04 USB CDC-ACM diagnostic PID1, ARMv7 EABI, no libc or NEON.',
    '/* Xoom MZ600 phase-1 v05 USB touchscreen diagnostic, guarded power ops. No libc/NEON.')
rep('#define SYS_syslog 103',
'''#define SYS_syslog 103
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
#define ABS_MT_TRACKING_ID 57''')
rep('static void pause_seconds(long sec){struct ts t={sec,0};sc6(SYS_nanosleep,(long)&t,0,0,0,0,0);}',
'''static void pause_seconds(long sec){struct ts t={sec,0};sc6(SYS_nanosleep,(long)&t,0,0,0,0,0);}
static void pause_200ms(void){struct ts t={0,200000000};sc6(SYS_nanosleep,(long)&t,0,0,0,0,0);}''')
rep('static void usb_command(const char *cmd){',r'''
/* No event injection, grabs or writes; input events are observed read-only. */
struct input_event32 {int32_t sec;int32_t usec;uint16_t type;uint16_t code;int32_t value;};
_Static_assert(sizeof(struct input_event32)==16,"ARM input_event layout");
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
 touch_ticks_remaining=75;touch_ticks=0;touch_frames=0;touch_reports=0;
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
       if(touch_dirty&&(touch_tracking_changed||(int)touch_ticks-touch_last_sent_tick>=3)){
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
 pending_power=mode;pending_power_ticks=100;
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
 long r=sc6(SYS_reboot,RB_MAGIC1,RB_MAGIC2,mode==1?RB_AUTOBOOT:RB_POWER_OFF,0,0);
 if(r<0){usb_send("POWER SYSCALL FAILED errno=");send_int((int32_t)-r);usb_send("\r\n");}
}
static void usb_command(const char *cmd){''')
rep('usb_send("XOOM LINUX MZ600 V04 USB SERIAL\\r\\n");',
    'usb_send("XOOM LINUX MZ600 V05 USB TOUCH DIAGNOSTIC\\r\\n");')
rep('usb_send("HELP PING STATUS CPU MEM STORAGE INPUT THERMAL USB LOGS CMDLINE\\r\\n");',
    'usb_send("HELP PING STATUS CPU MEM STORAGE INPUT THERMAL USB LOGS CMDLINE TOUCH TOUCHSTOP REBOOT POWEROFF CANCEL\\r\\n");')
rep('usb_send("PONG XOOM-LINUX V04\\r\\n");','usb_send("PONG XOOM-LINUX V05\\r\\n");')
rep(' else usb_send("UNKNOWN COMMAND. SEND HELP\\r\\n");',
''' else if(equals(cmd,"TOUCH"))touch_start();
 else if(equals(cmd,"TOUCHSTOP"))touch_stop();
 else if(equals(cmd,"REBOOT"))power_arm(1);
 else if(equals(cmd,"POWEROFF"))power_arm(2);
 else if(equals(cmd,"CONFIRM REBOOT"))power_execute(1);
 else if(equals(cmd,"CONFIRM POWEROFF"))power_execute(2);
 else if(equals(cmd,"CANCEL")){pending_power=0;pending_power_ticks=0;usb_send("POWER ACTION CANCELLED\\r\\n");}
 else usb_send("UNKNOWN COMMAND. SEND HELP\\r\\n");''')
rep('   for(int i=0;i<5;i++){poll_usb_serial();pause_seconds(1);}',
    '''   for(int i=0;i<25;i++){
     poll_usb_serial();
     poll_touch();
     if(pending_power_ticks>0&&--pending_power_ticks==0){pending_power=0;usb_send("POWER CONFIRMATION EXPIRED\\r\\n");}
     pause_200ms();
   }''')
assert not any(x in s for x in ('SYS_write_block','/dev/mmcblk0p'))
(dst/'init.c').write_text(s)
print('V05 C SOURCE',dst/'init.c',len(s),'read-only touchscreen and guarded reboot/poweroff')
