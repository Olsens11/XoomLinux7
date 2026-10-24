#!/usr/bin/env python3
"""Read-only BCM4329 datasheet contract source/artifact checker.
Does not contact the Xoom, modify device-tree files, or change kernel sources.
Separately reports actual generated-image and repository-source configurations.
"""
from pathlib import Path
import argparse, hashlib, json, re, subprocess, sys
def sha(b): return hashlib.sha256(b).hexdigest()
def text(p): return Path(p).read_text(encoding="utf8")
def prop(dtb,node,key):
 r=subprocess.run(["fdtget","-t","x",str(dtb),node,key],capture_output=True,text=True)
 if r.returncode: return None
 return [int(x,16) for x in r.stdout.strip().split()]
def exists(dtb,node,key):
 r=subprocess.run(["fdtget","-p",str(dtb),node],capture_output=True,text=True)
 if r.returncode: return False
 return key in r.stdout.splitlines()
def check(dtb,dts,kernel):
 base=Path(kernel)
 repo=text(dts)
 b=Path(dtb).read_bytes()
 assert b[:4]==b"\xd0\x0d\xfe\xed"
 data={"schema":1,"scope":"static, not electrical hardware proof",
       "source":str(dts),"compiled_dtb":str(dtb),"compiled_dtb_sha256":sha(b),
       "assertions":[],"observations":{}}
 def row(id, condition, evidence,meaning):
  data["assertions"].append({"id":id,"result":"PASS" if condition else "FAIL",
                             "evidence":evidence,"meaning":meaning})
 v=prop(dtb,"/mmc@c8000200","max-frequency")
 freq=v[0] if v else None
 data["observations"]["actual_dtb_max_frequency_hz"]=freq
 row("SDIO_DEFAULT_CLOCK",freq is not None and freq<=25000000,
     str(freq),"Compiled MMC2 limit must not exceed 25MHz when using legacy mode")
 source=re.search(r"sdmmc2:\s*mmc@c8000200\s*{.*?max-frequency\s*=\s*<(\d+)>",repo,re.S)
 sfreq=int(source.group(1)) if source else None
 data["observations"]["repository_source_max_frequency_hz"]=sfreq
 row("SOURCE_CLOCK_WITHIN_25MHZ",sfreq is not None and sfreq<=25000000,
     str(sfreq),"The canonical DTS and run-time DTB can disagree")
 for node,key,expected,ident in [
  ("/mmc@c8000200","post-power-on-delay-ms",100,"HOST_DELAY"),
  ("/wifi-pwrseq","post-power-on-delay-ms",300,"PWRSEQ_DELAY"),
  ("/mmc@c8000200","bus-width",4,"SDIO_BUS_4BIT"),
  ("/regulator-wifi","regulator-min-microvolt",3300000,"WIFI_REGULATOR_NOMINAL"),
  ("/regulator-wifi","regulator-max-microvolt",3300000,"WIFI_REGULATOR_MAX")
 ]:
  pv=prop(dtb,node,key)
  row(ident,pv is not None and pv[0]==expected,str(pv),f"expected {expected} at {node}/{key}")
 for node,key,ident in [
  ("/mmc@c8000200","mmc-pwrseq","MMC_HAS_PWRSEQ"),
  ("/mmc@c8000200","vmmc-supply","MMC_HAS_VMMC"),
  ("/mmc@c8000200","vqmmc-supply","MMC_HAS_VQMMC"),
  ("/regulator-wifi","regulator-boot-on","WIFI_REGULATOR_BOOT_ON"),
  ("/wifi-pwrseq","reset-gpios","WIFI_HAS_RESET_GPIO"),
  ("/serial@70006200/bluetooth","shutdown-gpios","BT_HAS_REG_ON_GPIO"),
  ("/serial@70006200/bluetooth","reset-gpios","BT_HAS_RESET_GPIO"),
  ("/serial@70006200/bluetooth","device-wakeup-gpios","BT_HAS_WAKE_GPIO"),
 ]:
  yes=exists(dtb,node,key)
  data["observations"][ident.lower()]=yes
  row(ident,yes, f"{node}/{key}={yes}", "presence check only; does not prove pin state")
 # source observations not presented as compliance assertions
 data["observations"]["wifi_u4_source"]="TEGRA_GPIO(U, 4)" in repo
 data["observations"]["wifi_u2_source"]="TEGRA_GPIO(U, 2)" in repo
 data["observations"]["bt_i7_source"]="TEGRA_GPIO(I, 7)" in repo
 data["observations"]["bt_u0_source"]="TEGRA_GPIO(U, 0)" in repo
 data["observations"]["bt_txco_assigned_pmc_blink"]=bool(re.search(
   r'bluetooth\s*{.*?clocks\s*=\s*<&tegra_pmc\s+TEGRA_PMC_CLK_BLINK>;\s*clock-names\s*=\s*"txco"',repo,re.S))
 data["observations"]["bt_lpo_explicit"]=bool(re.search(
   r'bluetooth\s*{.*?clock-names\s*=\s*"lpo"',repo,re.S))
 data["observations"]["wifi_pwrseq_blink"]=bool(re.search(
   r'wifi-pwrseq\s*{.*?clocks\s*=\s*<&tegra_pmc\s+TEGRA_PMC_CLK_BLINK>',repo,re.S))
 files={
  "mmc/core/core.c":["mmc_pwrseq_pre_power_on(host)","mmc_pwrseq_post_power_on(host)","mmc_delay(host->ios.power_delay_ms)"],
  "mmc/core/pwrseq_simple.c":["mmc_pwrseq_simple_pre_power_on","mmc_pwrseq_simple_post_power_on","mmc_pwrseq_simple_power_off"],
  "bluetooth/hci_bcm.c":["bcm_gpio_set_shutdown","bcm_get_txco","dev->shutdown","dev->reset","dev->txco_clk","dev->lpo_clk"],
  "mmc/core/sdio.c":["sdio_enable_hs(card)"],
  "net/wireless/broadcom/brcm80211/brcmfmac/chip.c":["brcmf_chip_cm3_set_active"],
  "net/wireless/broadcom/brcm80211/brcmfmac/sdio.c":["sdio_enable_func(sdiod->func2)","brcmf_sdio_download_firmware"]
 }
 for relative,syms in files.items():
  f=base/"drivers"/relative
  if not f.exists():raise FileNotFoundError(f)
  content=text(f)
  for sym in syms:
   row("CONSUMER_"+sym.split("(")[0],sym in content,f"{relative}: {sym}",
       "Code symbol present; cannot establish runtime invocation")
 return data
if __name__=="__main__":
 ap=argparse.ArgumentParser()
 ap.add_argument("--dtb",type=Path,required=True)
 ap.add_argument("--dts",type=Path,required=True)
 ap.add_argument("--kernel",type=Path,required=True)
 ap.add_argument("--out",type=Path,required=True)
 a=ap.parse_args()
 r=check(a.dtb,a.dts,a.kernel)
 a.out.parent.mkdir(parents=True,exist_ok=True)
 a.out.write_text(json.dumps(r,indent=2)+"\n")
 for entry in r["assertions"]:
  if entry["result"]=="FAIL":print("SOURCE_AUDIT_DISCREPANCY",entry["id"],entry["evidence"])
 print("ASSERTIONS",len(r["assertions"]),"FAILED",sum(x["result"]=="FAIL" for x in r["assertions"]))
 print("BOOT_DTB_SHA256",r["compiled_dtb_sha256"])
 print("BT_TXCO_PMC_BLINK",r["observations"]["bt_txco_assigned_pmc_blink"])
 print("READ_ONLY_NO_DEVICE_ACCESS")
