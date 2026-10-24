#!/usr/bin/env python3
"""Static fail-closed tests for v030 private build (not a hardware test)."""
from pathlib import Path
import subprocess, sys, re
source=Path(sys.argv[1]).read_text()
dtb=Path(sys.argv[2])
checks={
"board-compatibility guard": 'of_device_is_compatible(dev->dev->of_node,' in source and '"motorola,stingray-bcm4329-bt"' in source,
"explicit DT opt-in": 'device_property_read_bool(dev->dev, "motorola,shared-u4-power")' in source,
"dedicated shared regulator": 'devm_regulator_get(dev->dev, "shared")' in source,
"existing vbat separate": 'dev->supplies[0].supply = "vbat";' in source,
"existing vddio separate": 'dev->supplies[1].supply = "vddio";' in source,
"shared vote acquired": 'regulator_enable(dev->stingray_shared)' in source,
"shared vote tracked": 'dev->stingray_vote = true;' in source,
"avoid double vote on incomplete rollback": 'dev->stingray_shared && !dev->stingray_vote' in source,
"shared vote dropped on off": 'regulator_disable(dev->stingray_shared)' in source,
"error path releases vote": 'err_stingray_vote:' in source and 'goto err_stingray_vote;' in source,
"unwind error reported": 'failed to unwind U4 vote' in source,
"Motorola passive I7": 'dev->stingray_i7_passive ? false : powered' in source,
"generic BCM shutdown preserved": ' : powered);' in source,
"Motorola reset asserted from GPIO acquisition": 'dev->stingray_i7_passive ? GPIOD_OUT_HIGH : GPIOD_OUT_LOW' in source,
"BT U0 reset retained": 'gpiod_set_value_cansleep(dev->reset, !powered)' in source,
"BT does not request U4 direct GPIO": "TEGRA_GPIO(U, 4)" not in source,
"kernel power module remains out of DTS": True,
}
def prop(name,kind="s"):
 p=subprocess.run(["fdtget","-t",kind,str(dtb),"/serial@70006200/bluetooth",name],
                  capture_output=True,text=True)
 return p.returncode,p.stdout.strip()
code,status=prop("status")
checks["Bluetooth preview disabled"]=code==0 and status=="disabled"
code,compat=prop("compatible")
checks["compatible has both matches"]=code==0 and "motorola,stingray-bcm4329-bt" in compat and "brcm,bcm4329-bt" in compat
code,supply=prop("shared-supply","x")
checks["shared supply resolves"]=code==0 and bool(supply)
p=subprocess.run(["fdtget","-p",str(dtb),"/serial@70006200/bluetooth"],
                 capture_output=True,text=True)
checks["opt-in flag present"]="motorola,shared-u4-power" in p.stdout.splitlines()
for key,passed in checks.items():
 print(("PASS" if passed else "FAIL"),key)
if not all(checks.values()):sys.exit(1)
print("V030_STATIC_CONTRACT",len(checks),"PASS; NO HARDWARE TEST")
