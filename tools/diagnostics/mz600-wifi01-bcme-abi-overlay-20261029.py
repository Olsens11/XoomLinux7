#!/usr/bin/env python3
"""SOURCE ONLY: emit isolated BCM4329 read-only ABI/error lab overlay against r3.
Does not modify a kernel tree or contact a tablet. NOT an upstream patch.
"""
import argparse,difflib,pathlib,sys

CFG="drivers/net/wireless/broadcom/brcm80211/brcmfmac/cfg80211.c"
FWIL="drivers/net/wireless/broadcom/brcm80211/brcmfmac/fwil.c"
PROBE=r'''
/* MZ600_LAB_ONLY_20261029: six bounded read-only legacy ABI inputs.
 * Instrumented builds must NEVER be submitted as production patches.
 */
static void brcmf_bcm4329_lab_perchan_probe(struct brcmf_if *ifp)
{
	static const u16 args[] = { 0x200b, 0x280b, 0x2b0b,
				    0x1024, 0x1824, 0x1b24 };
	u32 io_type = 0;
	u32 result;
	int rc;
	int i;

	rc = brcmf_fil_cmd_int_get(ifp, BRCMF_C_GET_VERSION, &io_type);
	pr_info("MZ600_ABI_LAB get_version rc=%d io_type=%u\\n", rc,
		io_type);
	for (i = 0; i < ARRAY_SIZE(args); i++) {
		result = args[i];
		rc = brcmf_fil_bsscfg_int_query(ifp, "per_chan_info",
					       &result);
		if (rc)
			pr_info("MZ600_ABI_LAB query=%d arg=0x%04x rc=%d no_valid_result\\n",
				i, args[i], rc);
		else
			pr_info("MZ600_ABI_LAB query=%d arg=0x%04x rc=0 flags=0x%08x\\n",
				i, args[i], result);
	}
}

'''
DECL='''\ts32 err, fwerr;
\tbool mz600_lab_trace = false;
\tu32 mz600_lab_arg = 0;
\tstatic unsigned int mz600_lab_seen;
'''
BEFORE='''\tif (data != NULL)
\t\tlen = min_t(uint, len, BRCMF_DCMD_MAXLEN);
\tif (set)
'''
REPL=r'''	if (data != NULL)
		len = min_t(uint, len, BRCMF_DCMD_MAXLEN);
	/* MZ600_LAB_ONLY_20261029: observe raw firmware errno before
	 * ordinary fwil normalization; first six per_chan_info queries only.
	 */
	if (!set && cmd == BRCMF_C_GET_VAR && data &&
	    len >= sizeof("per_chan_info") + sizeof(__le32) &&
	    !memcmp(data, "per_chan_info", sizeof("per_chan_info"))) {
		__le32 le_arg;

		memcpy(&le_arg, (u8 *)data + sizeof("per_chan_info"),
		       sizeof(le_arg));
		mz600_lab_arg = le32_to_cpu(le_arg);
		mz600_lab_trace = true;
	}
	if (set)
'''
ANCHOR='''\tif (err) {
\t\tbrcmf_dbg(FIL, "Failed: error=%d\\n", err);
'''
LOG=r'''	if (mz600_lab_trace && mz600_lab_seen++ < 6) {
		if (err) {
			pr_info("MZ600_ABI_FW query=0x%04x transport=%d bcme=unavailable\\n",
				mz600_lab_arg, err);
		} else if (fwerr < 0) {
			pr_info("MZ600_ABI_FW query=0x%04x transport=0 bcme=%d no_valid_result\\n",
				mz600_lab_arg, fwerr);
		} else {
			__le32 le_result;

			memcpy(&le_result, data, sizeof(le_result));
			pr_info("MZ600_ABI_FW query=0x%04x transport=0 bcme=%d response=0x%08x\\n",
				mz600_lab_arg, fwerr,
				le32_to_cpu(le_result));
		}
	}
'''
def once(src,needle,replacement,label):
    num=src.count(needle)
    if num!=1:raise SystemExit(f"STOP: {label}: expected one anchor, found {num}")
    return src.replace(needle,replacement,1)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--kernel-root",required=True,type=pathlib.Path)
    p.add_argument("--out",required=True,type=pathlib.Path)
    args=p.parse_args()
    output=[]
    for rel in (CFG,FWIL):
        base=(args.kernel_root/rel).read_text(encoding="utf-8")
        if "MZ600_LAB_ONLY_20261029" in base:raise SystemExit("STOP: source already instrumented")
        if rel==CFG:
            if "per_chan_available = false" not in base or "brcmf_bcm4329_legacy_channels" not in base:
                raise SystemExit("STOP: not the intended r3 WIFI-01 source")
            updated=once(base,"static int brcmf_bcm4329_legacy_channels(",PROBE+"static int brcmf_bcm4329_legacy_channels(","r3 legacy function")
            updated=once(updated, "\tmax_count = (BRCMF_DCMD_MEDLEN - sizeof(list->count)) /",
                         "\tbrcmf_bcm4329_lab_perchan_probe(ifp);\n\tmax_count = (BRCMF_DCMD_MEDLEN - sizeof(list->count)) /",
                         "legacy fallback entry")
        else:
            updated=once(base,"\ts32 err, fwerr;\n",DECL,"fwil declarations")
            updated=once(updated,BEFORE,REPL,"fwil request args")
            updated=once(updated,ANCHOR,LOG+ANCHOR,"fwil response before normalization")
        diff="".join(difflib.unified_diff(base.splitlines(keepends=True),
                         updated.splitlines(keepends=True),
                         fromfile="a/"+rel,tofile="b/"+rel))
        if not diff:raise SystemExit("STOP: no changes for "+rel)
        output.append(diff.replace(chr(92)*2+"n", chr(92)+"n"))
    if args.out.exists():raise SystemExit("STOP: output already exists")
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text("".join(output),encoding="utf-8",newline="\n")
    print("SOURCE_OVERLAY_CREATED lab_only=1 no_tree_modified=1 target=r3")
    print("patch_bytes=",args.out.stat().st_size)
if __name__=="__main__":main()
