/* ARM QEMU-side FDT consumer. A separate implementation from host fdtget,
 * intended to independently decode real compiled DTB properties.
 * It does NOT execute a Tegra MMC controller or BCM4329.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <errno.h>

static uint32_t be32(const unsigned char *p) {
    return ((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];
}
static void die(const char *s) { fprintf(stderr,"FDT_CONSUMER_ERROR %s\n",s);exit(2); }
static int align4(int n) { return (n+3)&~3; }
typedef struct {const char *path;const char *name;uint32_t val;int found;} Target;
static Target targets[] = {
 {"/mmc@c8000200","post-power-on-delay-ms",0,0},
 {"/mmc@c8000200","max-frequency",0,0},
 {"/wifi-pwrseq","post-power-on-delay-ms",0,0},
 {"/wifi-pwrseq","power-off-delay-us",0,0},
 {"/regulator-wifi","regulator-boot-on",0,0},
 {"/mmc@c8000200","mmc-pwrseq",0,0},
 {"/mmc@c8000200","vmmc-supply",0,0},
 {"/mmc@c8000200","vqmmc-supply",0,0},
};
int main(int argc,char **argv) {
    if(argc!=5)die("syntax: arm_fdt_consumer DTB EXPECT_PRE EXPECT_POST EXPECT_SDIO_MAX");
    uint32_t expected_pre=(uint32_t)strtoul(argv[2],NULL,0);
    uint32_t expected_post=(uint32_t)strtoul(argv[3],NULL,0);
    uint32_t expected_clock=(uint32_t)strtoul(argv[4],NULL,0);
    FILE *fp=fopen(argv[1],"rb");
    if(!fp)die("cannot open DTB");
    if(fseek(fp,0,SEEK_END))die("seek");
    long length=ftell(fp);
    if(length<40 || length>2000000)die("DTB size invalid");
    rewind(fp);
    unsigned char *buf=malloc((size_t)length);
    if(!buf || fread(buf,1,(size_t)length,fp)!=(size_t)length)die("read failed");
    fclose(fp);
    if(be32(buf)!=0xd00dfeed)die("magic mismatch");
    uint32_t total=be32(buf+4),so=be32(buf+8),strings=be32(buf+12);
    uint32_t stringsize=be32(buf+32),structsize=be32(buf+36);
    if(total>(unsigned long)length || strings>total || so>total ||
       stringsize>total-strings || structsize>total-so)die("bad header offsets");
    unsigned char *sp=buf+so,*se=sp+structsize,*strings_start=buf+strings;
    char paths[64][512]={{0}};
    int depth=-1;
    while(sp+4<=se) {
        uint32_t tok=be32(sp);sp+=4;
        if(tok==1) { // BEGIN_NODE
            size_t available=(size_t)(se-sp);
            char *end=memchr(sp,0,available);
            if(!end || depth>=62)die("bad node name/depth");
            depth++;
            if(depth==0)paths[depth][0]='\0';
            else {
                char parent[512];
                memcpy(parent,paths[depth-1],sizeof(parent));
                int printed=snprintf(paths[depth],sizeof(paths[depth]),"%s/%s",
                    parent,(char*)sp);
                if(printed<0 || printed>=(int)sizeof(paths[depth]))die("path too long");
            }
            sp+=align4((int)(end-(char*)sp)+1);
        } else if(tok==2) {if(depth<0)die("unbalanced node");depth--;}
        else if(tok==3) {
            if(sp+8>se || depth<0)die("bad property header");
            uint32_t size=be32(sp),nameoff=be32(sp+4);sp+=8;
            if(size>(unsigned)(se-sp) || nameoff>=stringsize)die("bad property size/name");
            const char *name=(char*)strings_start+nameoff;
            if(!memchr(name,0,stringsize-nameoff))die("unclosed property name");
            for(unsigned i=0;i<sizeof(targets)/sizeof(targets[0]);i++) {
                Target *t=&targets[i];
                if(strcmp(paths[depth],t->path)==0 && strcmp(name,t->name)==0) {
                    if(t->found)die("duplicate target property");
                    if(size!=4 && strcmp(t->name,"regulator-boot-on")!=0)
                        die("expected single-cell 32-bit property");
                    if(strcmp(t->name,"regulator-boot-on")==0 && size!=0)
                        die("boolean property not empty");
                    t->val=size?be32(sp):1;
                    t->found=1;
                    printf("ARM_FDT_PROP path=%s prop=%s val=%u\n",
                         t->path,t->name,t->val);
                }
            }
            sp+=align4((int)size);
        } else if(tok==4){} // NOP
        else if(tok==9)break;
        else die("unknown FDT token");
    }
    for(unsigned i=0;i<sizeof(targets)/sizeof(targets[0]);i++)
        if(!targets[i].found)die("missing required property");
    if(targets[0].val!=expected_pre || targets[1].val!=expected_clock ||
       targets[2].val!=expected_post || targets[4].val!=1)
        die("expected consumer value mismatch");
    printf("ARM_QEMU_CONSUMER_PASS pre=%u post=%u clock=%u\n",
       targets[0].val,targets[2].val,targets[1].val);
    free(buf);
    return 0;
}
