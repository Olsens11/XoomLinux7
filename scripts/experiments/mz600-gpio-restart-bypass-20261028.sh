#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
#
# Experimental replacement MZ600 only: bypass the higher-priority
# gpio-restart system-off handler for ONE bootloader-mode reboot by
# unbinding its platform driver at runtime. Restores binding if syscall
# returns or any pre-reboot check fails. No on-disk partition changes.
#
# Usage: bash scripts/experiments/mz600-gpio-restart-bypass-20261028.sh --preflight
#        MZ600_FASTBOOT_WATCHER_READY=YES_XOOM_CDMA_ONLY \
#          bash ... --execute
set -euo pipefail
export LC_ALL=C
MODE="${1:---preflight}"
case "$MODE" in --preflight|--execute) ;; *) echo 'Only --preflight or --execute is accepted' >&2; exit 2;; esac
fail() { printf 'MZ600_GPIO_RESET_BYPASS_STOP %s\n' "$*" >&2; exit 1; }
command -v readlink >/dev/null || fail 'readlink unavailable'
command -v findmnt >/dev/null || fail 'findmnt unavailable'
command -v sha256sum >/dev/null || fail 'sha256sum unavailable'
[[ -r /proc/device-tree/model ]] || fail 'no OF model'
model=$(tr -d '\000' </proc/device-tree/model)
[[ "$model" == 'Motorola Xoom (Stingray MZ600 minimal USB diagnostic)' ]] ||
  fail 'not the exact proven replacement Stingray diagnostic DT model'
[[ $(uname -r) == '7.0.0-next-20260422+' ]] || fail 'not verified installed kernel release'
[[ $(findmnt -n -o SOURCE /) == /dev/mmcblk0p8 ]] || fail 'unexpected root'
[[ $(cat /sys/class/block/mmcblk0/size) == 62521344 ]] || fail 'disk geometry'
[[ $(cat /sys/class/block/mmcblk0p8/start) == 118784 ]] || fail 'p8 start'
[[ $(cat /sys/class/block/mmcblk0p8/size) == 2097152 ]] || fail 'p8 size'
[[ -r /proc/device-tree/gpio-restart/priority ]] || fail 'missing GPIO restart DT priority'
[[ $(od -An -tu1 -N4 /proc/device-tree/gpio-restart/priority | xargs) == '0 0 0 200' ]] ||
  fail 'GPIO restart priority is not 200'
[[ -d /sys/bus/platform/drivers/restart-gpio ]] || fail 'gpio-restart driver unavailable'
[[ -d /sys/bus/platform/drivers/tegra-pmc ]] || fail 'Tegra PMC platform driver unavailable'
mapfile -t gpio_devices < <(
  find /sys/bus/platform/drivers/restart-gpio -mindepth 1 -maxdepth 1 -type l -printf '%f\n' |
  grep -v '^module$' || true
)
[[ ${#gpio_devices[@]} == 1 ]] || fail "expected one bound restart-gpio instance; got ${#gpio_devices[@]}"
dev="${gpio_devices[0]}"
[[ -e "/sys/bus/platform/drivers/restart-gpio/$dev" ]] || fail 'GPIO bind lost'
mapfile -t pmc_devices < <(
  find /sys/bus/platform/drivers/tegra-pmc -mindepth 1 -maxdepth 1 -type l -printf '%f\n' |
  grep -v '^module$' || true
)
[[ ${#pmc_devices[@]} == 1 ]] || fail "expected one bound Tegra PMC instance; got ${#pmc_devices[@]}"
[[ -d /sys/bus/platform/drivers/restart-gpio ]] || fail 'restart sysfs disappeared'
printf 'MZ600_GPIO_RESET_BYPASS_PREFLIGHT_PASS model_verified kernel_verified BigPart_p8_verified gpio_priority=200 PMC_bound=YES gpio_bound=%s\n' "$dev"
if [[ "$MODE" == --preflight ]]; then
  echo 'DRY_RUN_ONLY: no driver unbind, no reboot, no device storage writes'
  exit 0
fi
[[ $(id -u) == 0 ]] || fail 'execute requires authorized root'
[[ ${MZ600_FASTBOOT_WATCHER_READY:-} == YES_XOOM_CDMA_ONLY ]] ||
  fail 'explicit owner-host watcher handshake missing'
helper=/run/mz600-reboot-bootloader.elf
[[ -f "$helper" && -x "$helper" ]] || fail 'verified reboot helper not staged in tmpfs'
[[ $(stat -c%s "$helper") == 664 ]] || fail 'helper length mismatch'
[[ $(sha256sum "$helper" | cut -d' ' -f1) == 451847d8acda2526c93a7b02d4694f3e80fefacce6281417ce75ee4ee6a0bf14 ]] ||
  fail 'helper SHA mismatch'
[[ $(findmnt -n -o SOURCE /) == /dev/mmcblk0p8 ]] || fail 'root changed during arming'
if [[ -d /sys/bus/platform/drivers/restart-gpio && -w /sys/bus/platform/drivers/restart-gpio/unbind ]]; then :; else
  fail 'cannot unbind restart GPIO through sysfs'
fi
armed=1
restore() {
  if [[ $armed == 1 ]]; then
    printf 'MZ600_GPIO_RESET_REBIND_ATTEMPT %s\n' "$dev" >&2
    printf '%s' "$dev" > /sys/bus/platform/drivers/restart-gpio/bind ||
      echo 'MZ600_GPIO_RESET_REBIND_FAIL: manual service attention required' >&2
  fi
}
trap restore EXIT
echo 'MZ600_GPIO_RESET_EXPERIMENT_UNBINDING_RAM_DRIVER_ONLY'
printf '%s' "$dev" > /sys/bus/platform/drivers/restart-gpio/unbind
[[ ! -L /sys/bus/platform/drivers/restart-gpio/"$dev" ]] ||
  fail 'GPIO driver still bound after unbind'
[[ -d /sys/bus/platform/drivers/tegra-pmc ]] ||
  fail 'Tegra PMC platform driver disappeared after unbind'
echo 'MZ600_GPIO_RESET_UNBOUND_TEMPORARILY; request bootloader from PMC'
sync
# Does not return when kernel reboot succeeds; if it fails, EXIT trap
# immediately rebinds the GPIO reset driver on the running OS.
"$helper"
fail 'reboot helper returned without reboot'
