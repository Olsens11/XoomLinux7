#!/usr/bin/env python3
"""Create v034 exact userspace-only fix from committed v033 USB controller."""
from pathlib import Path
import hashlib
R=Path(__file__).resolve().parents[2]
p=R/'src/diag-init/phase1-v033/init.c'
source=p.read_text()
s=source
def once(a,b):
 global s
 assert s.count(a)==1,(a,s.count(a))
 s=s.replace(a,b,1)
once('long rc=iof(fd,up?HCIDEVUP:HCIDEVDOWN,&dev);',
'''/* HCI ioctl passes device index BY VALUE (hci_sock_ioctl(arg)).
    * Passing &dev used to return -ENODEV for an unrelated integer.
    */
 long rc=iof(fd,up?HCIDEVUP:HCIDEVDOWN,(void *)(uintptr_t)dev);''')
once('BT START PASS DRIVER REGISTERED; HCI POWER NOT REQUESTED',
     'BT START PASS DRIVER REGISTERED; AUTO HARDWARE INIT MAY HAVE OCCURRED')
once('BT_ON_FLAG ','BT_USB_ON_REQUESTED_FLAG ')
once('if(rc>=0 || rc==-114 || rc==-19){bt_on=0;usb_send("BT OFF COMPLETE OR ALREADY DOWN\\r\\n");}',
     'if(rc>=0){bt_on=0;usb_send("BT OFF HCI_DEV_DOWN COMPLETE\\r\\n");}')
once('else usb_send("BT OFF FAILED; STOP DENIED\\r\\n");',
     'else usb_send("BT OFF FAILED; HCI DEV_DOWN NOT CONFIRMED; INSPECT LOGS\\r\\n");')
once('BT_STATUS BT_START BT_ON BT_OFF BT_STOP\\r\\n',
     'BT_STATUS BT_START BT_ON BT_OFF BT_STOP V034_HCI_IOCTL_BY_VALUE\\r\\n')
out=R/'src/diag-init/phase1-v034'
out.mkdir(parents=True,exist_ok=True)
(out/'init.c').write_text(s)
print('V033_SOURCE_SHA256',hashlib.sha256(source.encode()).hexdigest())
print('V034_SOURCE_SHA256',hashlib.sha256(s.encode()).hexdigest())
print('V034_CHANGED_ONLY_HCI_IOCTL_ARGUMENT_AND_MESSAGING')
