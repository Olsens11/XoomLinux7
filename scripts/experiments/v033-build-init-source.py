#!/usr/bin/env python3
"""Generate v033 RAM-only /init from unchanged v020 source, with opt-in BT commands."""
from pathlib import Path
R=Path(__file__).resolve().parents[2]
B=Path('/home/xoomdev/xoom-linux-rom')
v=B/'phase1-v033'
v.mkdir(exist_ok=True)
p=R/'src/diag-init/phase1-v20/init.c'
s=p.read_text()
# Only v033 branch may modify this init source; original stays canonical.
a="#define SYS_finit_module 379\n"
assert s.count(a)==1
s=s.replace(a,a+"""#define SYS_socket 281
#define AF_BLUETOOTH 31
#define SOCK_RAW 3
#define BTPROTO_HCI 1
#define HCIDEVUP 0x400448c9UL
#define HCIDEVDOWN 0x400448caUL
""")
a="static int wifi_on;\n"
assert s.count(a)==1
s=s.replace(a,a+"static int bt_started, bt_on;\n")
a=' if(wifi_on){usb_send("UPLOAD DENIED: WIFI_STOP first\\r\\n");return;}\n'
assert s.count(a)==1
s=s.replace(a,a+' if(bt_started || present("/sys/module/hci_uart")){usb_send("UPLOAD DENIED: BT_STOP first\\r\\n");return;}\n')
a='static void wifi_start(void){\n if(upl_fd>=0){usb_send("START DENIED DURING UPLOAD\\r\\n");return;}'
assert s.count(a)==1
s=s.replace(a,a+'''
 if(bt_started || present("/sys/module/hci_uart")){
   usb_send("WIFI START DENIED: BT ACTIVE OR LOADED\\r\\n");return;
 }''')
a='static int mmc2_safe_to_change(void){\n    if(!usb_raw_ready || upl_fd>=0 || wifi_on) return 0;'
assert s.count(a)==1
s=s.replace(a,'''static int mmc2_safe_to_change(void){
    if(!usb_raw_ready || upl_fd>=0 || wifi_on || bt_started || bt_on ||
       present("/sys/module/hci_uart"))return 0;''')
# Functions inserted AFTER mmc2_card_valid and BEFORE mmc2_write_exact (safe ordered declarations).
anchor='static long mmc2_write_exact(const char *path,const char *val){'
assert s.count(anchor)==1
helpers=r'''
/* v033: Bluetooth load/bind and HCI power are all opt-in USB commands.
 * Never start BT automatically during boot, and never access block media.
 * BT_START binds HCI UART; BT_ON then uses HCI device up ioctl to request
 * actual power. BT_OFF must precede BT_STOP. Keep MMC2 operations isolated.
 */
static long bt_load_one(const char *name) {
 char path[96]="/bt/";
 int len=4;
 for(const char *x=name;*x&&len<84;x++)path[len++]=*x;
 if(len>=84)return -22;
 path[len++]='.';path[len++]='k';path[len++]='o';path[len]=0;
 long fd=openf(path,O_RDONLY);
 if(fd<0)return fd;
 long rc=sc6(SYS_finit_module,fd,(long)"",0,0,0,0);
 closef(fd);
 return rc;
}
static void bt_status(void) {
 usb_send("BT STATUS BEGIN\r\n");
 usb_send("BLUETOOTH HCI_UART ");
 usb_send(present("/sys/module/hci_uart")?"MODULE LOADED\r\n":"MODULE NOT LOADED\r\n");
 usb_send("HCI0 ");
 usb_send(present("/sys/class/bluetooth/hci0")?"PRESENT\r\n":"ABSENT\r\n");
 usb_send("BT_STARTED_FLAG ");usb_send(bt_started?"1\r\n":"0\r\n");
 usb_send("BT_ON_FLAG ");usb_send(bt_on?"1\r\n":"0\r\n");
 usb_lsdir("/sys/bus/serial/devices");
 usb_file("/proc/modules",2600);
 usb_send("BT STATUS END\r\n");
}
static void bt_stop(void);
static void bt_start(void) {
 if(!usb_raw_ready || upl_fd>=0 || wifi_on ||
    present("/sys/module/brcmfmac") || present("/sys/module/brcmutil") ||
    !mmc2_card_valid() || bt_started || present("/sys/module/hci_uart")) {
  usb_send("BT START DENIED PREFLIGHT (STOP WIFI FIRST)\r\n");return;
 }
 static const char *const order[]={
    "ecc","ecdh_generic","cmac","bluetooth","btbcm","hci_uart"
 };
 for(unsigned i=0;i<6;i++){
   long rc=bt_load_one(order[i]);
   usb_send("BT MODULE ");usb_send(order[i]);
   usb_send(" rc ");send_int((int32_t)rc);usb_send("\r\n");
   if(rc<0 && rc!=-17){
     usb_send("BT START FAILED; ATTEMPTING UNLOAD\r\n");
     bt_stop();
     return;
   }
 }
 bt_started=present("/sys/module/hci_uart");
 usb_send(bt_started?"BT START PASS DRIVER REGISTERED; HCI POWER NOT REQUESTED\r\n":
                     "BT START FAILED: HCI MODULE NOT PRESENT\r\n");
}
static long bt_hci_power(int up) {
 if(!present("/sys/class/bluetooth/hci0"))return -19;
 long fd=sc6(SYS_socket,AF_BLUETOOTH,SOCK_RAW,BTPROTO_HCI,0,0,0);
 if(fd<0)return fd;
 int dev=0; /* fail-closed: require hci0 sysfs path above */
 long rc=iof(fd,up?HCIDEVUP:HCIDEVDOWN,&dev);
 closef(fd);
 return rc;
}
static void bt_power_on(void) {
 if(!usb_raw_ready || upl_fd>=0 || wifi_on ||
    present("/sys/module/brcmfmac") || !bt_started || bt_on ||
    !present("/sys/module/hci_uart")) {
   usb_send("BT ON DENIED PREFLIGHT\r\n");return;
 }
 long rc=bt_hci_power(1);
 usb_send("BT ON HCI_DEV_UP rc ");send_int((int32_t)rc);usb_send("\r\n");
 if(rc>=0){bt_on=1;usb_send("BT ON REQUEST COMPLETE; READ LOGS AND STATUS\r\n");}
 else usb_send("BT ON FAILED; RUN BT_OFF THEN BT_STOP\r\n");
}
static void bt_power_off(void) {
 if(!bt_started && !present("/sys/module/hci_uart")){
    usb_send("BT OFF NOT LOADED\r\n");return;
 }
 long rc=bt_hci_power(0);
 usb_send("BT OFF HCI_DEV_DOWN rc ");send_int((int32_t)rc);
 usb_send("\r\n");
 if(rc>=0 || rc==-114 || rc==-19){bt_on=0;usb_send("BT OFF COMPLETE OR ALREADY DOWN\r\n");}
 else usb_send("BT OFF FAILED; STOP DENIED\r\n");
}
static void bt_stop(void){
 if(upl_fd>=0){usb_send("BT STOP DENIED DURING UPLOAD\r\n");return;}
 if(bt_on){usb_send("BT STOP DENIED: BT_OFF FIRST\r\n");return;}
 static const char *const order[]={
    "hci_uart","btbcm","bluetooth","cmac","ecdh_generic","ecc"
 };
 for(unsigned i=0;i<6;i++){
   long rc=sc6(SYS_delete_module,(long)order[i],O_NONBLOCK,0,0,0,0);
   usb_send("BT UNLOAD ");usb_send(order[i]);
   usb_send(" rc ");send_int((int32_t)rc);usb_send("\r\n");
 }
 bt_started=present("/sys/module/hci_uart");
 if(bt_started || present("/sys/module/btbcm") ||
    present("/sys/module/bluetooth") || present("/sys/module/ecdh_generic") ||
    present("/sys/module/ecc") || present("/sys/module/cmac"))
   usb_send("BT STOP INCOMPLETE MODULE REMAINS\r\n");
 else usb_send("BT STOP END MODULE UNLOADED\r\n");
}
'''
s=s.replace(anchor,helpers+"\n"+anchor,1)
a=' else if(equals(cmd,"WIFI_START"))wifi_start();'
assert s.count(a)==1
s=s.replace(a,''' else if(equals(cmd,"BT_STATUS"))bt_status();
 else if(equals(cmd,"BT_START"))bt_start();
 else if(equals(cmd,"BT_ON"))bt_power_on();
 else if(equals(cmd,"BT_OFF"))bt_power_off();
 else if(equals(cmd,"BT_STOP"))bt_stop();
'''+a,1)
a='HELP PING STATUS CPU MEM STORAGE INPUT THERMAL USB LOGS BOOTLOG SDIO CMDLINE GRID WIFI WIFI_START WIFI_STOP WIFI_RETRY WIFI_DEBUG N UPLOAD TYPE N MMC2_STATUS MMC2_PROFILE AUTO/MOTOROLA MMC2_REINIT MMC2_BIND TOUCH TOUCHSTOP REBOOT POWEROFF CANCEL'
assert s.count(a)==1
s=s.replace(a,a+' BT_STATUS BT_START BT_ON BT_OFF BT_STOP',1)
# keep PONG V20 to preserve verified transport/rollback client
assert 'PONG XOOM-LINUX V20' in s
dest=R/'src/diag-init/phase1-v033'
dest.mkdir(exist_ok=True)
(dest/'init.c').write_text(s)
print('V033_INIT_CREATED',len(s),'BT commands guarded, no automatic BT load')
