from pathlib import Path
p=Path('/home/xoomdev/xoom-linux-rom/phase1-v08/init.c')
s=p.read_text()
a='usb_send("BOOTLOG UNAVAILABLE errno=");send_int((int)-n);usb_send("\\r\\n");'
b='usb_send("BOOTLOG UNAVAILABLE errno=");usb_send(utoa((unsigned long)(-n)));usb_send("\\r\\n");'
assert s.count(a)==1,(a,s.count(a))
p.write_text(s.replace(a,b,1))
print("V08 no forward declaration needed")
