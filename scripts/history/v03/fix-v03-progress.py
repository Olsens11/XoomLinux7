from pathlib import Path
p=Path('/home/xoomdev/xoom-linux-rom/phase1-v03/init.c')
s=p.read_text()
assert s.count('seconds%60')==1
p.write_text(s.replace('seconds%60','seconds&63ul'))
print('Fixed libc-free bitwise progress bar; source bytes',p.stat().st_size)
