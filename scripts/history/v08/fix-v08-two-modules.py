from pathlib import Path
p=Path('/mnt/c/Users/olsen/XoomLinux/Phase1/build-v08-wifi-module.sh')
s=p.read_text()
s=s.replace('--enable BRCMUTIL --module BRCMFMAC','--module BRCMUTIL --module BRCMFMAC')
s=s.replace("grep -Fx 'CONFIG_BRCMUTIL=y'","grep -Fx 'CONFIG_BRCMUTIL=m'")
s=s.replace('make -j2 O="$OUT" drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko >',
'''make -j2 O="$OUT" drivers/net/wireless/broadcom/brcm80211/brcmutil/brcmutil.ko drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko >''')
s=s.replace('echo "V08 DEFERRED MODULE VERIFIED;', '''UT="$OUT/drivers/net/wireless/broadcom/brcm80211/brcmutil/brcmutil.ko"
test -s "$UT"
sha256sum "$UT"
stat -c "BRCMUTIL_MODULE=%s bytes" "$UT"
echo "V08 DEFERRED MODULE VERIFIED;''')
p.write_text(s)
v=Path('/home/xoomdev/xoom-linux-rom/phase1-v08/init.c')
x=v.read_text()
find=''' long fd=openf("/wifi/brcmfmac.ko",O_RDONLY);
 if(fd<0){
   wifi_state=-1;wifi_errno=-fd;
   usb_send("WIFI_START ERROR OPEN MODULE errno=");send_int((int32_t)wifi_errno);usb_send("\\r\\n");return;
 }
 long rc=sc6(SYS_finit_module,fd,(long)"",0,0,0,0);'''
rep=''' long util=openf("/wifi/brcmutil.ko",O_RDONLY);
 if(util<0){wifi_state=-1;wifi_errno=-util;usb_send("WIFI_START ERROR OPEN BRCMUTIL errno=");send_int((int32_t)wifi_errno);usb_send("\\r\\n");return;}
 long utilrc=sc6(SYS_finit_module,util,(long)"",0,0,0,0);
 closef(util);
 usb_send("BRCMUTIL LOAD RESULT ");send_int((int32_t)utilrc);usb_send("\\r\\n");
 if(utilrc<0){wifi_state=-3;wifi_errno=-utilrc;return;}
 long fd=openf("/wifi/brcmfmac.ko",O_RDONLY);
 if(fd<0){
   wifi_state=-1;wifi_errno=-fd;
   usb_send("WIFI_START ERROR OPEN BRCMFMAC errno=");send_int((int32_t)wifi_errno);usb_send("\\r\\n");return;
 }
 long rc=sc6(SYS_finit_module,fd,(long)"",0,0,0,0);'''
assert x.count(find)==1
v.write_text(x.replace(find,rep))
print('Adjusted v08 2-stage deferred loading brcmutil -> brcmfmac')
