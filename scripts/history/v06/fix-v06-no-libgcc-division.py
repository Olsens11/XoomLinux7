from pathlib import Path
p=Path("/home/xoomdev/xoom-linux-rom/phase1-v06/init.c")
s=p.read_text()
def one(a,b):
 global s
 assert s.count(a)==1,(a,s.count(a))
 s=s.replace(a,b,1)
one("static uint32_t grid_bg_for(int x,int y){","static uint32_t grid_div(uint32_t n,uint32_t d);\nstatic uint32_t grid_bg_for(int x,int y){")
one("int col=x/cw,row=(y-GRID_TOP)/ch;","int col=(int)grid_div((uint32_t)x,(uint32_t)cw),row=(int)grid_div((uint32_t)(y-GRID_TOP),(uint32_t)ch);")
one("if(x%cw==0||(y-GRID_TOP)%ch==0||x%cw==cw-1||(y-GRID_TOP)%ch==ch-1)",
"if(x-col*cw==0||(y-GRID_TOP)-row*ch==0||x-col*cw==cw-1||(y-GRID_TOP)-row*ch==ch-1)")
one("int col=cell%GRID_COLS,row=cell/GRID_COLS;","int col=cell&7,row=cell>>3;")
one("int cell=(sy>=GRID_TOP&&sy<GRID_BOTTOM)?((sy-GRID_TOP)/120)*GRID_COLS+sx/160:-1;",
"int cell=(sy>=GRID_TOP&&sy<GRID_BOTTOM)?(int)(grid_div((uint32_t)(sy-GRID_TOP),120u)*GRID_COLS+grid_div((uint32_t)sx,160u)):-1;")
one("if(n%(long)sizeof(a[0])!=0)return;","if((n&15L)!=0)return;")
one("for(int i=0;i<n/(long)sizeof(a[0]);i++){","for(int i=0;i<(n>>4);i++){")
p.write_text(s)
print("Replaced libgcc ARM integer division with v06 freestanding safe unsigned shift-subtract division")
