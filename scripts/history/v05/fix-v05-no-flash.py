from pathlib import Path
p=Path("/home/xoomdev/xoom-linux-rom/phase1-v05/init.c")
s=p.read_text()
old='static void framebuffer(void){'
new='''/* Update only the footer to avoid flashing the full LCD every five seconds.
 * The static dashboard is painted once by framebuffer(), then never repainted
 * unless framebuffer is remapped. Keep text and progress regions separate. */
static void dashboard_uptime(unsigned long seconds){
 if(!screen)return;
 int foot=(int)vi.yres-83;
 if(foot<=0)return;
 uint32_t bg=rgb(9,18,32),mint=rgb(125,234,176),cyan=rgb(30,174,167);
 /* Digit area x=180..294, 5x7 glyphs at scale 3 = 21px tall. */
 fill(180,foot,112,23,bg);
 text(182,foot,utoa(seconds),3,mint);
 /* The progress bar is independent of the separator and labels. */
 fill(42,foot+39,512,8,bg);
 fill(42,foot+39,(int)((seconds&63ul)*8),8,cyan);
}
static void framebuffer(void){'''
assert s.count(old)==1
s=s.replace(old,new,1)
old='   if(screen)dashboard(seconds);'
new='   if(screen)dashboard_uptime(seconds);'
assert s.count(old)==1
s=s.replace(old,new,1)
p.write_text(s)
print("v05 incremental framebuffer paint in place; source bytes",p.stat().st_size)
