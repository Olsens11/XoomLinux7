#!/usr/bin/env python3
"""Build an isolated, temporary-boot-only Linux 7 MZ600 Classic BigPart probe.

Based on Schischu's original BigPart in-memory GPT remap and 4.4 scoped port.
No device access, network, flash, file system format or block device writes.
No modifications to the already-qualified v06.3 build tree/artifacts.
Only use for READ-ONLY storage geometry testing after a separate host review.
"""
import hashlib, json, os, shutil, struct, subprocess
from pathlib import Path

ROOT=Path("/home/xoomdev/xoom-linux-rom")
W=ROOT/"clean-wifi-bt-usb-20261025"
PROJ=ROOT/"clean-upstream-usb-20261025/project"
OLD_SRC=W/"linux"
OLD_BUILD=W/"build"
NEW_SRC=W/"v064-bigpart-linux"
NEW_BUILD=W/"v064-bigpart-build"
OUT=W/"artifacts-embedded-v064-bigpart-stageA"
OLD_IMG=W/"artifacts-embedded-v063/MZ600-CLEAN-WIFI-BT-USB-v063-HCD-RAM-ONLY-UNTESTED.img"
CPIO=W/"artifacts-embedded-v063/v063-private-bcm4329b1-firmware.cpio.gz"
NEW_IMG=OUT/"MZ600-V064-BIGPART-GPT-READONLY-STAGE-A-TEMPBOOT.img"
PIN="2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3"
OLD_SHA="07950963496de68cf53b7d0218ed71450252450846768f065b0f36a37cb6743e"
CC=str(ROOT/"toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-")
def digest(x):return hashlib.sha256(x).hexdigest()
def run(*a,env=None):
 print("RUN"," ".join(map(str,a)),flush=True)
 return subprocess.run([str(x) for x in a],env=env,check=True)
def replace_once(path, old, new):
 text=path.read_text()
 if text.count(old)!=1:raise RuntimeError(f"anchor count {text.count(old)} on {path}: {old[:80]!r}")
 path.write_text(text.replace(old,new,1))
def require(x,msg):
 if not x:raise RuntimeError(msg)
def pfile(name):return NEW_SRC/name

require(os.geteuid()!=0,"Never run root")
require(OLD_IMG.is_file() and digest(OLD_IMG.read_bytes())==OLD_SHA,"v063 image hash mismatch")
require(CPIO.is_file() and (OLD_BUILD/".config").is_file(),"v063 CPIO/config missing")
require(subprocess.check_output(["git","-C",str(OLD_SRC),"rev-parse","HEAD"],text=True).strip()==PIN,"unexpected Linux source commit")
require(not NEW_SRC.exists() and not NEW_BUILD.exists() and not OUT.exists(),"Never overwrite prior staging; choose a unique output")
require(subprocess.check_output(["git","-C",str(PROJ),"status","--porcelain"],text=True).strip()=="","public project dirty; inspect first")

# Snapshot the already-known dirty but physically-qualified clean USB Stingray
# deltas, without resetting or editing their source worktree.
delta=subprocess.check_output(["git","-C",str(OLD_SRC),"diff","--binary","--",
 "arch/arm/boot/compressed/atags_to_fdt.c","arch/arm/boot/dts/nvidia/Makefile"])
require(b"atags_to_fdt.c" in delta and b"Makefile" in delta,"expected legacy baseline deltas missing")
dts=OLD_SRC/"arch/arm/boot/dts/nvidia/tegra20-motorola-stingray-clean-usb.dts"
require(dts.is_file(),"Stingray DTS missing")
run("git","-C",OLD_SRC,"worktree","add","--detach",NEW_SRC,PIN)
subprocess.run(["git","-C",str(NEW_SRC),"apply","--check","-"],input=delta,check=True)
subprocess.run(["git","-C",str(NEW_SRC),"apply","-"],input=delta,check=True)
dst=pfile("arch/arm/boot/dts/nvidia/tegra20-motorola-stingray-clean-usb.dts")
shutil.copy2(dts,dst)
replace_once(dst, """	sdmmc4: mmc@c8000600 {
		status = "okay";
		bus-width = <8>;
		non-removable;
""", """	sdmmc4: mmc@c8000600 {
		status = "okay";
		bus-width = <8>;
		non-removable;
		motorola,xoom-bigpart; /* OPT-IN: exact MZ600 virtual GPT map ONLY */
""")
kconf=pfile("block/partitions/Kconfig")
replace_once(kconf,"config SYSV68_PARTITION\n", """config MOTOROLA_XOOM_BIGPART
	bool "Motorola Stingray CDMA classic Xoom BigPart in-memory GPT view"
	depends on EFI_PARTITION && OF && ARCH_TEGRA
	help
	  Exact legacy Xoom BigPart geometry on opt-in Stingray internal eMMC.
	  Never writes GPT. Requires exact 10-entry factory geometry, OEM
	  relocated GPT sector and explicit eMMC DT opt-in; refuses otherwise.

config SYSV68_PARTITION
""")
efi=pfile("block/partitions/efi.c")
replace_once(efi,'#include <linux/slab.h>\n',"""#include <linux/slab.h>
#ifdef CONFIG_MOTOROLA_XOOM_BIGPART
#include <linux/of.h>
#include <linux/device.h>
#endif
""")
replace_once(efi,"static int force_gpt;\n", """static int force_gpt;
#ifdef CONFIG_MOTOROLA_XOOM_BIGPART
static u64 xoom_gpt_sector;
static bool xoom_bigpart_enabled(struct parsed_partitions *state);
static int __init xoom_gpt_sector_setup(char *s)
{
	if (kstrtoull(s, 0, &xoom_gpt_sector))
		xoom_gpt_sector = 0;
	return 1;
}
__setup("gpt_sector=", xoom_gpt_sector_setup);
#endif
""")
replace_once(efi,"\tforce_gpt = 1;\n\treturn 1;\n}\n__setup(\"gpt\", force_gpt_fn);", """#ifdef CONFIG_MOTOROLA_XOOM_BIGPART
	/* The legacy __setup() matcher uses prefixes: do not eat gpt_sector=. */
	if (*str)
		return 0;
#endif
	force_gpt = 1;
	return 1;
}
__setup("gpt", force_gpt_fn);""")
anchor="""	if (!good_agpt && force_gpt && fops->alternative_gpt_sector) {"""
fallback="""#ifdef CONFIG_MOTOROLA_XOOM_BIGPART
	/* Bootloader supplies this sector. Only on the exact opt-in eMMC. */
	if (!good_agpt && force_gpt && xoom_bigpart_enabled(state) &&
	    xoom_gpt_sector == 62513151ULL) {
		pr_info("MZ600 BigPart: probing relocated OEM GPT at sector %llu\\n",
			(unsigned long long)xoom_gpt_sector);
		good_agpt = is_gpt_valid(state, xoom_gpt_sector, &agpt, &aptes);
	}
#endif

"""
replace_once(efi,anchor,fallback+anchor)
# Source is validated GPT entries after is_gpt_valid() CRC checks; no GPT writes.
helper="""#ifdef CONFIG_MOTOROLA_XOOM_BIGPART
static bool xoom_bigpart_enabled(struct parsed_partitions *state)
{
	struct device *d;
	if (!of_machine_is_compatible("motorola,stingray") ||
	    get_capacity(state->disk) != 62521344ULL ||
	    queue_logical_block_size(state->disk->queue) != 512)
		return false;
	for (d = disk_to_dev(state->disk); d; d = d->parent)
		if (d->of_node &&
		    of_property_read_bool(d->of_node, "motorola,xoom-bigpart"))
			return true;
	return false;
}
/* Standard 2013 Schischu BigPart 1GiB system, 512MiB cache mapping.
 * We validate ALL ten original MZ600 GPT entry extents, not just the three
 * remapped starts, and reject extra valid entries to prevent overlaps.
 */
static int xoom_bigpart_prepare(struct parsed_partitions *state,
				gpt_header *gpt, gpt_entry *ptes)
{
	static const u64 starts[10] = {
		51200, 57344, 61440, 65536, 73728, 77824, 102400,
		118784, 643072, 989184
	};
	static const u64 sizes[10] = {
		6144, 4096, 4096, 8192, 4096, 24576, 16384,
		524288, 346112, 61522944
	};
	u32 i, n = le32_to_cpu(gpt->num_partition_entries);
	if (!xoom_bigpart_enabled(state))
		return 0;
	if (n < 10 || state->limit <= 10)
		return -EINVAL;
	for (i = 0; i < n; i++) {
		u64 start = le64_to_cpu(ptes[i].starting_lba);
		u64 end = le64_to_cpu(ptes[i].ending_lba);
		if (i >= 10) {
			if (is_pte_valid(&ptes[i], last_lba(state->disk)))
				return -EINVAL;
			continue;
		}
		if (!is_pte_valid(&ptes[i], last_lba(state->disk)) ||
		    start != starts[i] || end < start ||
		    end - start + 1 != sizes[i])
			return -EINVAL;
	}
	/* Factory p10 end and every protected p1..p7 extent are invariant. */
	if (starts[9] + sizes[9] != 62512128ULL)
		return -EINVAL;
	pr_info("MZ600 BigPart: validated exact factory 10-partition GPT; "
		"virtual system 1GiB, cache 512MiB, userdata 28929.5MiB\\n");
	return 1;
}
#endif

"""
replace_once(efi,"int efi_partition(struct parsed_partitions *state)\n",helper+"int efi_partition(struct parsed_partitions *state)\n")
replace_once(efi,"\tgpt_entry *ptes = NULL;\n", """	gpt_entry *ptes = NULL;
#ifdef CONFIG_MOTOROLA_XOOM_BIGPART
	int xoom_remap = 0;
#endif
""")
anchor="""	pr_debug("GUID Partition Table is valid!  Yea!\\n");"""
check="""#ifdef CONFIG_MOTOROLA_XOOM_BIGPART
	xoom_remap = xoom_bigpart_prepare(state, gpt, ptes);
	if (xoom_remap < 0) {
		pr_err("MZ600 BigPart: REFUSING unexpected partition layout\\n");
		kfree(gpt);
		kfree(ptes);
		return -1;
	}
#endif

"""
replace_once(efi,anchor,check+anchor)
anchor="""		put_partition(state, i+1, start * ssz, size * ssz);"""
remap="""#ifdef CONFIG_MOTOROLA_XOOM_BIGPART
		if (xoom_remap > 0) {
			if (i == 7) { start = 118784; size = 2097152; }
			if (i == 8) { start = 2215936; size = 1048576; }
			if (i == 9) { start = 3264512; size = 59247616; }
		}
#endif
"""
replace_once(efi,anchor,remap+anchor)
require("MZ600 BigPart: validated exact factory" in efi.read_text(),"kernel source integration failed")

OUT.mkdir()
shutil.copy2(OLD_BUILD/".config",OUT/"v063-build-config-before-v064.txt")
env={**os.environ,"ARCH":"arm","CROSS_COMPILE":CC}
run(NEW_SRC/"scripts/config","--file",OUT/"v063-build-config-before-v064.txt","--enable","MOTOROLA_XOOM_BIGPART")
# Use an independently isolated O= path; it must not write into OLD_BUILD.
NEW_BUILD.mkdir()
shutil.copy2(OUT/"v063-build-config-before-v064.txt",NEW_BUILD/".config")
run(NEW_SRC/"scripts/config","--file",NEW_BUILD/".config","--enable","MOTOROLA_XOOM_BIGPART")
run("make","-s","-C",NEW_SRC,f"O={NEW_BUILD}","olddefconfig",env=env)
cfg=(NEW_BUILD/".config").read_text()
require("CONFIG_MOTOROLA_XOOM_BIGPART=y" in cfg,"BigPart config disabled")
require(f'CONFIG_INITRAMFS_SOURCE="{CPIO}"' in cfg,"initramfs source changed")
log=OUT/"compile.log"
with log.open("w") as fh:
 result=subprocess.run(["make","-C",str(NEW_SRC),f"O={NEW_BUILD}","-j6","zImage","dtbs"],env=env,
                       stdout=fh,stderr=subprocess.STDOUT)
if result.returncode:
 print("BUILD_FAILED\n"+"\n".join(log.read_text().splitlines()[-60:]))
 raise RuntimeError("Kernel compile failed")
require((NEW_BUILD/"usr/initramfs_inc_data").read_bytes()==CPIO.read_bytes(),"CPIO embed mismatch")
z=(NEW_BUILD/"arch/arm/boot/zImage").read_bytes()
d=(NEW_BUILD/"arch/arm/boot/dts/nvidia/tegra20-motorola-stingray-clean-usb.dtb").read_bytes()
require(d[:4]==bytes.fromhex("d00dfeed"),"DTB magic")
old=OLD_IMG.read_bytes()
page=2048
kernel=z+d
header=bytearray(old[:page]);struct.pack_into("<I",header,8,len(kernel));struct.pack_into("<I",header,16,0)
idsha=hashlib.sha1()
for part in (kernel,b"",b"",b""):
 idsha.update(part);idsha.update(struct.pack("<I",len(part)))
header[576:596]=idsha.digest()
out=bytes(header)+kernel+b"\0"*(-len(kernel)%page)
require(len(out)<=8*1024*1024,"exceeds legacy boot envelope")
NEW_IMG.write_bytes(out)
diff=subprocess.check_output(["git","-C",str(NEW_SRC),"diff","--binary"])
(OUT/"linux-source-diff.patch").write_bytes(diff)
manifest={
 "classification":"OFFLINE GENERATED ONLY; READ-ONLY STORAGE TEST; NOT BOOTED/FLASHED",
 "base_v063_sha256":OLD_SHA,
 "upstream_commit":PIN,
 "classic_bigpart_commit_reference":"6b3d70fff905b7395fd15992c3779b27d1b6c101",
 "relocated_gpt_lba_physically_verified":62513151,
 "strict_all_10_partition_geometry":True,
 "efi_source_sha256":digest(efi.read_bytes()),
 "dts_sha256":digest(dst.read_bytes()),
 "kernel_image_bytes":len(kernel),
 "new_image_bytes":len(out),
 "new_image_sha256":digest(out),
 "new_dtb_sha256":digest(d),
 "build_config_sha256":digest(cfg.encode()),
 "source_diff_sha256":digest(diff),
 "firmware_private_inside_image":True,
 "original_v063_build_artifacts_unchanged":True,
 "no_device_access_no_flash":True,
}
(OUT/"MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n")
print("V064_BIGPART_STORAGE_STAGE_A_OFFLINE_BUILD_PASS",len(out),digest(out))
print("PRIVATE_FIRMWARE_IMAGE_DO_NOT_PUBLISH_OR_FLASH")
