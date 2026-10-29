/* Host-side test harness. A separate generator inserts the exact pinned
 * brcmf_bcm4329_legacy_channels() C implementation between markers.
 * No firmware, kernel driver or radio operations occur in this process.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <errno.h>

typedef uint32_t u32;
typedef uint8_t u8;
typedef int32_t s32;
#define GFP_KERNEL 0
#define BRCMF_DCMD_MEDLEN 1536
#define BRCMF_C_GET_VALID_CHANNELS 217
#define BRCMF_BCM4329_FW_UNSUPPORTED 23
#define NL80211_BAND_2GHZ 0
#define NL80211_BAND_5GHZ 1
#define NUM_NL80211_BANDS 2
#define BRCMU_CHAN_BAND_2G 1
#define BRCMU_CHAN_BAND_5G 2
#define BRCMU_CHAN_BW_20 20
#define BRCMU_CHAN_SB_NONE 0
#define IEEE80211_CHAN_DISABLED (1U << 0)
#define IEEE80211_CHAN_NO_IR (1U << 1)
#define IEEE80211_CHAN_RADAR (1U << 3)
#define IEEE80211_CHAN_NO_HT40 (1U << 4)
#define IEEE80211_CHAN_NO_80MHZ (1U << 7)
#define IEEE80211_CHAN_NO_160MHZ (1U << 8)
#define WL_CHAN_RADAR (1U << 0)
#define WL_CHAN_PASSIVE (1U << 1)
#define cpu_to_le32(v) (v)
#define le32_to_cpu(v) (v)

struct brcmf_chanspec_list {u32 count;u32 element[];};
struct ieee80211_channel {u32 hw_value;u32 flags;u32 orig_flags;};
struct ieee80211_supported_band {int band;size_t n_channels;struct ieee80211_channel *channels;};
struct wiphy {struct ieee80211_supported_band *bands[NUM_NL80211_BANDS];};
struct brcmf_pub {int marker;};
struct brcmf_if {int marker;};
struct brcmu_chan {u32 chnum,band,bw,sb,chspec;};
struct brcmu_d11inf {void (*encchspec)(struct brcmu_chan *);};
struct brcmf_cfg80211_info {struct brcmf_pub *pub;struct wiphy *wiphy;struct brcmu_d11inf d11inf;};

static struct brcmf_if mock_ifp;
static int list_err, metadata_err, fail_alloc, metadata_calls, list_calls;
static s32 metadata_fwerr;
static u32 metadata_value;
static u32 fw_channels[20];
static size_t fw_count;
static struct ieee80211_channel channels24[3],channels5[3];
static struct ieee80211_supported_band band24={NL80211_BAND_2GHZ,3,channels24};
static struct ieee80211_supported_band band5={NL80211_BAND_5GHZ,3,channels5};
static struct wiphy phy={{&band24,&band5}};
static struct brcmf_pub driver;
static struct brcmf_cfg80211_info cfg;

static struct brcmf_if *brcmf_get_ifp(struct brcmf_pub *p, int n)
{(void)p;(void)n;return &mock_ifp;}
static struct wiphy *cfg_to_wiphy(struct brcmf_cfg80211_info *c)
{return c->wiphy;}
static void *kcalloc(size_t n,size_t z,int flags)
{(void)flags;return fail_alloc ? NULL : calloc(n,z);}
static void kfree(void *p){free(p);}
static void encode(struct brcmu_chan *c){c->chspec=c->chnum;}

static int brcmf_fil_cmd_data_get(struct brcmf_if *ifp,u32 cmd,void *data,u32 len)
{
 (void)ifp;
 if(cmd!=BRCMF_C_GET_VALID_CHANNELS||len!=BRCMF_DCMD_MEDLEN) abort();
 list_calls++;
 if(list_err) return list_err;
 struct brcmf_chanspec_list *l=data;
 l->count=(u32)fw_count;
 for(size_t i=0;i<fw_count && i<20;i++)l->element[i]=fw_channels[i];
 return 0;
}
static int brcmf_fil_bsscfg_data_get_fwerr(struct brcmf_if *ifp,
 const char *name,void *data,u32 len,s32 *fwerr)
{
 (void)ifp;
 if(strcmp(name,"per_chan_info")||len!=4)abort();
 metadata_calls++;
 *fwerr=metadata_fwerr;
 if(metadata_err)return metadata_err;
 *(u32 *)data=metadata_value;
 return 0;
}

/* BEGIN_EXACT_R7_LEGACY_FUNCTION */
/* END_EXACT_R7_LEGACY_FUNCTION */

static void require(int ok,const char *name)
{if(!ok){fprintf(stderr,"FAIL %s\n",name);exit(2);}}
static void reset(void){
 static const u32 a[]={1,6,11},b[]={36,40,149};
 memset(channels24,0,sizeof(channels24));
 memset(channels5,0,sizeof(channels5));
 for(int i=0;i<3;i++){channels24[i].hw_value=a[i];channels5[i].hw_value=b[i];}
 fw_count=6; for(int i=0;i<3;i++){fw_channels[i]=a[i];fw_channels[3+i]=b[i];}
 list_err=metadata_err=fail_alloc=metadata_calls=list_calls=metadata_fwerr=0;
 metadata_value=0;
}
static int run(void){
 u8 data[BRCMF_DCMD_MEDLEN];
 memset(data,0x55,sizeof(data));
 return brcmf_bcm4329_legacy_channels(&cfg,data);
}
static void unchanged(const char *name){
 for(int i=0;i<3;i++)require(channels24[i].flags==0&&channels5[i].flags==0,name);
}
static void one(const char *name){puts(name);}

int main(void){
 cfg.pub=&driver;cfg.wiphy=&phy;cfg.d11inf.encchspec=encode;
 reset();list_err=-EIO;require(run()==-EIO,"GET_VALID_CHANNELS error propagated");
 unchanged("GET_VALID_CHANNELS error must leave all channels intact");one("PASS firmware query failure no mutation");

 reset();metadata_err=-EBADE;metadata_fwerr=-23;
 require(run()==0,"raw unsupported treated as optional metadata");
 require(metadata_calls==1,"unsupported is cached, no redundant queries");
 require((channels5[0].flags & IEEE80211_CHAN_NO_IR)!=0,"unknown 5GHz NO_IR");
 require(!(channels24[0].flags & IEEE80211_CHAN_NO_IR),"2GHz no extra NO_IR on valid FW list");
 one("PASS raw unsupported passive 5GHz and 2GHz service not blanket disabled");

 reset();metadata_err=-EBADE;metadata_fwerr=-4;
 require(run()==-EBADE,"NOTUP propagated");unchanged("NOTUP atomic");
 one("PASS firmware NOTUP leaves flags unchanged");

 reset();metadata_err=-EIO;
 require(run()==-EIO,"transport error propagated");unchanged("transport atomic");
 one("PASS transport failure leaves flags unchanged");

 reset();fail_alloc=1;require(run()==-ENOMEM,"alloc error");
 unchanged("allocation error atomic");one("PASS alloc error unchanged");

 reset();fw_count=1;fw_channels[0]=255;
 require(run()==-EINVAL,"invalid channel denied");unchanged("invalid channel atomic");
 one("PASS invalid channel denied");

 reset();fw_count=0;require(run()==-EINVAL,"empty list denied");unchanged("empty list atomic");
 one("PASS empty channel list denied");

 reset();fw_count=3;fw_channels[0]=1;fw_channels[1]=11;fw_channels[2]=36;
 metadata_err=-EBADE;metadata_fwerr=-23;
 require(run()==0,"reduced firmware list accepted");
 require(channels24[1].flags & IEEE80211_CHAN_DISABLED,"unlisted 2G disabled");
 require(channels5[1].flags & IEEE80211_CHAN_DISABLED,"unlisted 5G disabled");
 one("PASS unlisted 2.4/5GHz frequencies disabled");

 reset();channels24[0].flags=IEEE80211_CHAN_NO_IR;
 channels24[0].orig_flags=IEEE80211_CHAN_DISABLED;
 metadata_err=-EBADE;metadata_fwerr=-23;
 require(run()==0,"orig flags test");
 require(channels24[0].flags & IEEE80211_CHAN_NO_IR,"original flags not cleared");
 require(channels24[0].orig_flags & IEEE80211_CHAN_DISABLED,"hardware original not changed");
 one("PASS original hardware/regulator restrictions not relaxed");

 reset();metadata_value=WL_CHAN_RADAR|WL_CHAN_PASSIVE;
 require(run()==0,"per-channel metadata recognized");
 require((channels5[0].flags & (IEEE80211_CHAN_RADAR|IEEE80211_CHAN_NO_IR)) ==
 (IEEE80211_CHAN_RADAR|IEEE80211_CHAN_NO_IR),"radar must imply no IR");
 one("PASS real metadata radar/passive restrictions");

 puts("R7_EXACT_C_LEGACY_FAULT_INJECTION_10_CASES_PASS");
 return 0;
}
