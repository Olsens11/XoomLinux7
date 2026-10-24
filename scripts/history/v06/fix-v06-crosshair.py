from pathlib import Path
p=Path("/home/xoomdev/xoom-linux-rom/phase1-v06/init.c")
s=p.read_text()
a="dx>=-3&&dx<=3 || dy>=-3&&dy<=3 || (dx*dx+dy*dy>192&&dx*dx+dy*dy<255)"
b="(dx>=-3&&dx<=3) || (dy>=-3&&dy<=3) || (dx*dx+dy*dy>192&&dx*dx+dy*dy<255)"
assert s.count(a)==1
p.write_text(s.replace(a,b))
print("v06 crosshair clause parenthesized")
