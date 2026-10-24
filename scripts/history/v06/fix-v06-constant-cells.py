from pathlib import Path
p=Path("/home/xoomdev/xoom-linux-rom/phase1-v06/init.c")
s=p.read_text()
a="const int cw=(int)vi.xres/GRID_COLS;"
assert s.count(a)==1
s=s.replace(a,"const int cw=160;",1)
a="const int ch=(GRID_BOTTOM-GRID_TOP)/GRID_ROWS;"
assert s.count(a)==1
s=s.replace(a,"const int ch=120;",1)
a="int cw=(int)vi.xres/GRID_COLS,ch=(GRID_BOTTOM-GRID_TOP)/GRID_ROWS;"
assert s.count(a)==1
s=s.replace(a,"int cw=160,ch=120;",1)
p.write_text(s)
b=Path("/mnt/c/Users/olsen/XoomLinux/Phase1/build-v06-userland.sh")
t=b.read_text()
assert t.count('"$V/init.c" -lgcc')==1
b.write_text(t.replace('"$V/init.c" -lgcc','"$V/init.c"'))
print("v06 constant grid cells 160x120, removed libgcc, use pure no-libc ARM compiler output")
