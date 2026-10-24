from pathlib import Path
p=Path("/home/xoomdev/xoom-linux-rom/phase1-v06/init.c")
s=p.read_text()
mark="static long sc6(long nr,long a,long b,long c,long d,long e,long f) {"
assert s.count(mark)==1
mem='''/* Freestanding compiler helper; no libc. */
void *memset(void *dst,int value,size_t n){
 volatile unsigned char *b=(volatile unsigned char *)dst;
 for(size_t i=0;i<n;i++)b[i]=(unsigned char)value;
 return dst;
}
'''
p.write_text(s.replace(mark,mem+mark,1))
b=Path("/mnt/c/Users/olsen/XoomLinux/Phase1/build-v06-userland.sh")
t=b.read_text(encoding="utf-8-sig")
a='-s -o "$V/init" "$V/init.c"'
assert t.count(a)==1
b.write_text(t.replace(a,'-s -o "$V/init" "$V/init.c" -lgcc',1))
print("Added freestanding memset; GCC ARM EABI division helpers linked statically from libgcc")
