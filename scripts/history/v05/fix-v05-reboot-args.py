from pathlib import Path
p=Path('/home/xoomdev/xoom-linux-rom/phase1-v05/init.c')
s=p.read_text()
a='sc6(SYS_reboot,RB_MAGIC1,RB_MAGIC2,mode==1?RB_AUTOBOOT:RB_POWER_OFF,0,0);'
b='sc6(SYS_reboot,RB_MAGIC1,RB_MAGIC2,mode==1?RB_AUTOBOOT:RB_POWER_OFF,0,0,0);'
assert s.count(a)==1
p.write_text(s.replace(a,b,1))
print('Reboot syscall wrapper argument count fixed')
