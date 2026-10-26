/*
 * MZ600 temporary TWRP diagnostic: read only three eMMC LBAs with ARM EABI
 * syscalls and Linux _llseek (64-bit offset on 32-bit ARM).
 *
 * Never opens a device writable. No ioctl, mmap, mount, block or filesystem
 * mutation, radio action, reboot, or TWRP installer. Can be removed from /tmp.
 * Intended to verify whether BusyBox v1.21.1 dd's large skip gave a false read.
 *
 * Compile with ARM cross GNU GCC: -Os -ffreestanding -fno-stack-protector
 *   -nostdlib -static -Wl,-e,_start -Wl,--build-id=none -s -lgcc
 *
 * The expected eMMC device node must be separately verified on the target.
 */
/* libgcc integer division trap fallback; numeric formatting only divides by 10. */
int raise(int sig){(void)sig;return -1;}
typedef unsigned int u32;
typedef unsigned long long u64;
#define SYS_EXIT 1
#define SYS_READ 3
#define SYS_WRITE 4
#define SYS_OPEN 5
#define SYS_CLOSE 6
#define SYS_LLSEEK 140
#define STDOUT 1
#define O_RDONLY 0

static long call1(long n,long a){
 register long r0 asm("r0")=a;
 register long r7 asm("r7")=n;
 asm volatile("svc 0" : "+r"(r0) : "r"(r7) : "memory","cc");
 return r0;
}
static long call3(long n,long a,long b,long c){
 register long r0 asm("r0")=a;
 register long r1 asm("r1")=b;
 register long r2 asm("r2")=c;
 register long r7 asm("r7")=n;
 asm volatile("svc 0" : "+r"(r0) : "r"(r1),"r"(r2),"r"(r7) : "memory","cc");
 return r0;
}
static long call5(long n,long a,long b,long c,long d,long e){
 register long r0 asm("r0")=a;
 register long r1 asm("r1")=b;
 register long r2 asm("r2")=c;
 register long r3 asm("r3")=d;
 register long r4 asm("r4")=e;
 register long r7 asm("r7")=n;
 asm volatile("svc 0" : "+r"(r0) : "r"(r1),"r"(r2),"r"(r3),"r"(r4),"r"(r7) : "memory","cc");
 return r0;
}
static void put(const char *s){
 unsigned n=0;
 while(s[n]) n++;
 call3(SYS_WRITE,STDOUT,(long)s,n);
}
static void hex(unsigned char v){
 const char *digits="0123456789abcdef";
 char h[2]={digits[v>>4],digits[v&15]};
 call3(SYS_WRITE,STDOUT,(long)h,2);
}
static void number(u32 x){
 char tmp[12],out[12];unsigned n=0,i;
 if(!x){put("0");return;}
 while(x){tmp[n++]='0'+x%10;x/=10;}
 for(i=0;i<n;i++)out[i]=tmp[n-1-i];
 call3(SYS_WRITE,STDOUT,(long)out,n);
}
static const char dev[]="/dev/block/mmcblk0";
static unsigned char buf[512] __attribute__((aligned(16)));
static u64 newpos;
static void probe(long fd,u32 sector,const char *label){
 u64 offset=(u64)sector*512ULL;
 long rc;
 unsigned i,ff=0,zero=0;
 put(label);put(" LBA ");number(sector);put(" ");
 rc=call5(SYS_LLSEEK,fd,(long)(offset>>32),(long)(u32)offset,(long)&newpos,0);
 if(rc<0){put("LLSEEK_FAILED rc=");number((u32)(-rc));put("\n");return;}
 if(newpos!=offset){put("OFFSET_MISMATCH\n");return;}
 rc=call3(SYS_READ,fd,(long)buf,512);
 if(rc!=512){put("READ_FAILED bytes=");number((u32)rc);put("\n");return;}
 for(i=0;i<512;i++){if(buf[i]==255)ff++;if(buf[i]==0)zero++;}
 put("first32=");
 for(i=0;i<32;i++)hex(buf[i]);
 put(" ff=");number(ff);put(" zero=");number(zero);
 if(buf[0]=='E'&&buf[1]=='F'&&buf[2]=='I'&&buf[3]==' '&&
    buf[4]=='P'&&buf[5]=='A'&&buf[6]=='R'&&buf[7]=='T')
     put(" GPT_SIGNATURE_FOUND");
 put("\n");
}
void _start(void){
 long fd=call3(SYS_OPEN,(long)dev,O_RDONLY,0);
 if(fd<0){put("READONLY_OPEN_FAILED ");number((u32)(-fd));put("\n");call1(SYS_EXIT,2);for(;;){}}
 put("ARM32_LLSEEK_READONLY_BEGIN\n");
 probe(fd,62513151U,"OEM_BOOT_GPT_SECTOR");
 probe(fd,62521343U,"EMMC_LAST_SECTOR");
 probe(fd,118784U,"FACTORY_SYSTEM_FIRST_SECTOR");
 call1(SYS_CLOSE,fd);
 put("NO_BLOCK_DEVICE_WRITES_PERFORMED\n");
 call1(SYS_EXIT,0);
 for(;;){}
}
