/* This test inserts the exact unmodified r7 regulatory notifier C function.
 * Firmware/cfg80211 interfaces are stubs; NEVER radio or kernel execution.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <errno.h>
#include <string.h>
typedef int32_t s32;
#define BRCM_CC_4329_CHIP_ID 4329
#define TRACE 0
#define brcmf_dbg(...) ((void)0)
#define bphy_err(...) (++errors)

struct brcmf_bus {int chip;};
struct brcmf_pub {struct brcmf_bus *bus_if;};
struct brcmf_if {struct brcmf_pub *drvr;int marker;};
struct brcmf_cfg80211_info {struct brcmf_pub *pub;};
struct wiphy {struct brcmf_cfg80211_info *cfg;};
struct regulatory_request {char alpha2[2];int initiator;};
struct brcmf_fil_country_le {char country_abbrev[4],ccode[4];s32 rev;};

static int get_err,translate_err,set_err,refresh_err;
static int get_calls,translate_calls,set_calls,refresh_calls,setup_calls,errors;
static struct brcmf_if the_if;
static struct brcmf_bus the_bus={BRCM_CC_4329_CHIP_ID};
static struct brcmf_pub the_pub={&the_bus};
static struct brcmf_cfg80211_info the_cfg={&the_pub};
static struct wiphy the_phy={&the_cfg};
static struct brcmf_cfg80211_info *wiphy_to_cfg(struct wiphy *w)
{return w->cfg;}
static struct brcmf_if *brcmf_get_ifp(struct brcmf_pub *p,int idx)
{(void)p;(void)idx;return &the_if;}
static int brcmf_fil_iovar_data_get(struct brcmf_if *p,const char *name,
 void *data,size_t len){
 (void)p;
 if(strcmp(name,"country")||len!=sizeof(struct brcmf_fil_country_le))abort();
 get_calls++;
 if(get_err)return get_err;
 memset(data,0,len);
 return 0;
}
static int brcmf_translate_country_code(struct brcmf_pub *p,
 const char *code,struct brcmf_fil_country_le *c){
 (void)p;(void)code;(void)c;translate_calls++;return translate_err;
}
static int brcmf_fil_iovar_data_set(struct brcmf_if *p,const char *name,
 void *data,size_t len){
 (void)p;(void)data;
 if(strcmp(name,"country")||len!=sizeof(struct brcmf_fil_country_le))abort();
 set_calls++;return set_err;
}
static int brcmf_bcm4329_refresh_legacy_channels(struct brcmf_cfg80211_info *c){
 (void)c;refresh_calls++;return refresh_err;
}
static int brcmf_setup_wiphybands(struct brcmf_cfg80211_info *c){
 (void)c;setup_calls++;return 0;
}

/* BEGIN_EXACT_R7_NOTIFIER_FUNCTION */
/* END_EXACT_R7_NOTIFIER_FUNCTION */

static void need(int cond,const char *name){
 if(!cond){fprintf(stderr,"FAIL %s\n",name);exit(3);}
}
static void reset(void){
 get_err=translate_err=set_err=refresh_err=0;
 get_calls=translate_calls=set_calls=refresh_calls=setup_calls=errors=0;
 the_bus.chip=BRCM_CC_4329_CHIP_ID;
}
static void go(char a,char b){
 struct regulatory_request r={{a,b},1};
 brcmf_cfg80211_reg_notifier(&the_phy,&r);
}
int main(void){
 the_if.drvr=&the_pub;
 reset();go('0','0');
 need(!get_calls&&!set_calls&&!refresh_calls,"world 00 ignored");
 puts("PASS world country ignored");

 reset();go('u','s');
 need(!get_calls&&!set_calls&&!refresh_calls,"invalid ISO ignored");
 puts("PASS invalid country ignored");

 reset();get_err=-EIO;go('U','S');
 need(get_calls==1&&!translate_calls&&!refresh_calls,"country GET failed");
 puts("PASS failed firmware country GET no requery");

 reset();translate_err=-EAGAIN;go('U','S');
 need(get_calls==1&&translate_calls==1&&refresh_calls==1&&!set_calls,
      "already-matching country refresh");
 puts("PASS EAGAIN reintersects current firmware");

 reset();translate_err=-EINVAL;go('U','S');
 need(get_calls==1&&refresh_calls==1&&!set_calls,"missing map requery");
 puts("PASS unavailable country translation reintersects");

 reset();set_err=-EIO;go('U','S');
 need(get_calls==1&&set_calls==1&&refresh_calls==1&&!setup_calls,
      "firmware country SET rejected requery");
 puts("PASS rejected firmware country SET reintersects");

 reset();go('U','S');
 need(get_calls==1&&set_calls==1&&setup_calls==1&&!refresh_calls,
      "successful country SET modern setup");
 puts("PASS successful SET uses ordinary band setup");

 reset();translate_err=-EINVAL;the_bus.chip=9999;go('U','S');
 need(get_calls==1&&!refresh_calls&&!set_calls,"modern chip no r7 fallback");
 puts("PASS other chip unchanged");

 reset();refresh_err=-EIO;translate_err=-EINVAL;go('U','S');
 need(refresh_calls==1&&errors>=1&&!set_calls,
      "requery failure logs but notifier cannot report failure");
 puts("PASS failed requery logs only; FAIL-SAFE RECOVERY STILL OPEN");

 puts("R7_EXACT_C_REGULATORY_NOTIFIER_9_CASES_PASS");
 return 0;
}
