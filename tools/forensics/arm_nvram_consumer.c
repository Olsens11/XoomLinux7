/* ARM user-mode independent BCM4329 NVRAM parser (simple non-multidevice path).
 * Mirrors the byte-oriented state machine in Linux 7 brcmfmac/firmware.c.
 * Test only: does NOT run the full kernel parser or request firmware.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <ctype.h>
static void fail(const char *s) {fprintf(stderr,"ARM_NVRAM_ERROR %s\n",s);exit(2);}
static int char_ok(unsigned char ch) {return ch>=0x20&&ch<0x7f&&ch!='#';}
static int ws(unsigned char ch) {return ch==' '||ch=='\r'||ch=='\n'||ch=='\t';}
int main(int argc,char **argv) {
 if(argc!=3)fail("usage: arm_nvram_consumer INPUT_TEXT OUTPUT_BINARY");
 FILE *f=fopen(argv[1],"rb");if(!f)fail("read input");
 if(fseek(f,0,SEEK_END))fail("seek");
 long size=ftell(f);if(size<1||size>64000)fail("input size");
 rewind(f);
 unsigned char *data=calloc((size_t)size+2,1),*out=calloc(65536,1);
 if(!data||!out)fail("alloc");
 if(fread(data,1,(size_t)size,f)!=(size_t)size)fail("read");
 fclose(f);
 size_t pos=0,entry=0,used=0;int state=0,boardrev=0,ignored=0;
 while(pos<(size_t)size) {
   unsigned char ch=data[pos];
   if(state==0) { /* IDLE */
     if(ch=='\n'){state=3;continue;}
     if(ws(ch)||ch=='\0'){pos++;continue;}
     if(ch=='#'){state=3;continue;}
     if(char_ok(ch)){entry=pos;state=1;continue;}
     pos++;continue;
   }
   if(state==1){ /* KEY */
     if(ch=='=') {
       if(!memcmp(data+entry,"RAW1",4)){state=3;ignored++;}
       else state=2;
       if(!memcmp(data+entry,"boardrev",8))boardrev=1;
     } else if(!char_ok(ch)||ch==' ') {state=3;continue;}
     pos++;continue;
   }
   if(state==2){ /* VALUE */
     if(!char_ok(ch)) {
       size_t n=pos-entry;
       if(used+n+1>=64000)fail("NVRAM oversized");
       memcpy(out+used,data+entry,n);used+=n;out[used++]=0;
       state=0;continue;
     }
     pos++;continue;
   }
   if(state==3){ /* COMMENT */
     while(pos<(size_t)size&&data[pos]!='\n'&&data[pos]!='\0')pos++;
     if(pos<(size_t)size)pos++;
     state=0;continue;
   }
 }
 if(used==0)fail("No entries");
 if(!boardrev){const char *def="boardrev=0xff";size_t n=strlen(def);memcpy(out+used,def,n);used+=n+1;}
 size_t aligned=(used+1+3)&~(size_t)3;
 if(aligned+4>65536)fail("NVRAM pad overflow");
 uint32_t count=(uint32_t)(aligned/4);
 uint32_t token=((~count&0xffff)<<16)|count;
 for(int i=0;i<4;i++)out[aligned+i]=(unsigned char)(token>>(8*i));
 FILE *g=fopen(argv[2],"wb");if(!g)fail("write output");
 if(fwrite(out,1,aligned+4,g)!=aligned+4)fail("write failed");
 fclose(g);
 printf("ARM_NVRAM_PACK_PASS source=%ld packed=%zu record_terminators=%d token_word_count=%u\n",
        size,aligned+4,(int)used, count);
 printf("ARM_NVRAM_RAW1_IGNORED=%d\n",ignored);
 free(data);free(out);
 return 0;
}
