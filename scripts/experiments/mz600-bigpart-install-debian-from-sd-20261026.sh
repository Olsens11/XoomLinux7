#!/bin/bash
# Motorola Xoom MZ600 BigPart p8 Debian installation from VERIFIED SD root.
# --preflight (default): READ ONLY. --install: explicit destructive p8 format.
# Never touches BCT/GPT, vendor p1..p5, TWRP p6, Android boot p7, p9 or p10.
# Normal ext4 + GNU tar; no custom raw-sector writes. No network required.
set -euo pipefail

TARGET=/dev/mmcblk0p8
ROOT=/dev/mmcblk1p1
MOUNT=/mnt/xoom-system-install
EXPECTED_KERN='7.0.0-next-20260422+'
MODE=${1:---preflight}
fail() { printf 'MZ600_INSTALL_REFUSED: %s\n' "$*" >&2; exit 1; }
part() { local num=$1 start=$2 count=$3 d=/sys/class/block/mmcblk0p${1}; 
    [[ $(cat "$d/start") == "$start" && $(cat "$d/size") == "$count" ]] ||
        fail "MZ600 partition p$num geometry is not expected";
}
case "$MODE" in --preflight|--install) ;; *) fail 'usage: --preflight or --install' ;; esac
[[ -b /dev/mmcblk0 && -b /dev/mmcblk1 && -b "$TARGET" && -b "$ROOT" ]] ||
    fail 'required eMMC/SD nodes absent'
[[ $(cat /sys/block/mmcblk0/size) == 62521344 ]] || fail 'wrong eMMC total sectors'
[[ $(cat /sys/block/mmcblk0/device/name) == MMC32G ]] || fail 'wrong internal eMMC name'
[[ $(cat /sys/block/mmcblk1/size) == 61067264 ]] || fail 'wrong SD card geometry'
[[ $(cat /sys/block/mmcblk1/device/name) == SD ]] || fail 'wrong removable SD card'
[[ $(findmnt -n -o SOURCE /) == "$ROOT" ]] || fail 'Linux / is not verified removable SD'
[[ $(findmnt -n -o FSTYPE /) == ext4 ]] || fail 'root not ext4'
[[ $(cat /etc/debian_version) == 12.15 ]] || fail 'not proven Debian 12.15'
[[ $(uname -r) == "$EXPECTED_KERN" ]] || fail 'not pinned Linux 7'
[[ $(cat /proc/1/comm) == systemd ]] || fail 'not normal systemd userspace'
[[ -e /sys/firmware/devicetree/base/mmc@c8000600/motorola,xoom-bigpart ]] ||
    fail 'BigPart internal MMC DT opt-in absent'
part 1 51200 6144
part 2 57344 4096
part 3 61440 4096
part 4 65536 8192
part 5 73728 4096
part 6 77824 24576
part 7 102400 16384
part 8 118784 2097152
part 9 2215936 1048576
part 10 3264512 59247616
[[ $(cat /sys/class/block/mmcblk0p8/dev) == 179:24 ]] ||
    fail 'internal system dev_t differs from tested kernel'
[[ $(cat /sys/class/block/mmcblk1p1/dev) == 179:1 ]] ||
    fail 'SD root dev_t differs from tested kernel'
! findmnt -rn -S "$TARGET" >/dev/null || fail 'system target already mounted'
! awk -v dev="$(cat /sys/class/block/mmcblk0p8/dev)" '$3 == dev {found=1} END {exit !found}' /proc/self/mountinfo ||
    fail 'internal p8 is mounted by its major:minor'
[[ -x /usr/sbin/mkfs.ext4 && -x /usr/sbin/e2fsck && -x /usr/sbin/blkid ]] ||
    fail 'standard Debian e2fsprogs not installed'
command -v tar >/dev/null || fail 'GNU tar missing'
tar --help | grep -q -- '--one-file-system' || fail 'GNU tar does not support FS boundaries'
tar --help | grep -q -- '--xattrs' || fail 'GNU tar does not preserve xattrs'
tar --help | grep -q -- '--acls' || fail 'GNU tar does not preserve ACLs'
grep -Eq '^[^#[:space:]][^[:space:]]*[[:space:]]+/[[:space:]]+ext4([[:space:]]|$)' /etc/fstab ||
    fail 'expected current /etc/fstab root entry missing'
P8_ID=$(sed -n 's/^PARTUUID=//p' /sys/class/block/mmcblk0p8/uevent)
[[ "$P8_ID" =~ ^[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}$ ]] ||
    fail 'BigPart system GPT PARTUUID missing/invalid'
# Kernel PARTUUID/partition name are authoritative for root=PARTUUID.
# Minimal Debian /dev may contain only the SD udev symlink; a missing
# by-partuuid symlink is not evidence the kernel lacks the GPT PARTUUID.
grep -Fxq 'PARTNAME=system' /sys/class/block/mmcblk0p8/uevent ||
    fail 'kernel does not label p8 as system'
if [[ -e /dev/disk/by-partuuid/"$P8_ID" ]]; then
    [[ $(readlink -f /dev/disk/by-partuuid/"$P8_ID") == "$TARGET" ]] ||
        fail 'existing p8 userspace symlink targets a different block device'
else
    printf 'INFO_P8_UDEV_SYMLINK_MISSING_KERNEL_GPT_UUID_VERIFIED\n'
fi
SRC_KIB=$(df -Pk / | awk 'NR==2 {print $3}') # avoid false failure on unprivileged dry-run
[[ "$SRC_KIB" =~ ^[0-9]+$ && "$SRC_KIB" -lt 800000 ]] ||
    fail 'SD OS footprint too large for safe 1GiB /system'
printf 'MZ600_BIGPART_PREFLIGHT_PASS\n'
printf 'ROOT=Debian-12.15-SD-ext4 KERNEL=Linux7\n'
printf 'TARGET=P8_BIGPART_1G P9_CACHE_512M P10_DATA_28929_5M\n'
printf 'PROTECTED_P1_TO_P7_PARTITION_GEOMETRY_PASS_NO_WRITES\n'
printf 'SD_ROOT_USED_KIB=%s TARGET_UNMOUNTED=PASS\n' "$SRC_KIB"
printf 'IDENTITY_AND_PARTUUID_VERIFIED=PASS\n'
if [[ "$MODE" == --preflight ]]; then
    printf 'READ_ONLY_NO_FORMAT_NO_MOUNT_NO_TRANSFER\n'
    exit 0
fi

# The user explicitly approved destruction of Android system/data and chose
# original Xoom BigPart. This flag is deliberately required per invocation.
[[ $(id -u) == 0 ]] || fail 'Must enter sudo password interactively via Surface USB console'
[[ ! -e "$MOUNT" ]] || fail 'Refusing to reuse any existing installer mount dir'
umask 022
printf 'DESTRUCTIVE_P8_SYSTEM_FORMAT_BEGIN\n'
/usr/sbin/mkfs.ext4 -F -m 1 -L xoom-system "$TARGET"
mkdir -p "$MOUNT"
mounted=0
cleanup() {
    if [[ $mounted == 1 ]]; then
        sync
        umount "$MOUNT" || true
    fi
}
trap cleanup EXIT
mount -t ext4 -o rw,noatime "$TARGET" "$MOUNT"
mounted=1
[[ $(findmnt -n -o SOURCE --target "$MOUNT") == "$TARGET" ]] ||
    fail 'mounted filesystem is not intended p8'
printf 'DEBIAN_SYSTEM_FILE_COPY_BEGIN\n'
# --one-file-system is NOT sufficient for volatile mountpoint metadata:
# physical first attempt failed because './sys' changed while read.
# Exclude all live kernel/virtual mount trees and create empty mountpoints on
# destination. Avoid transient logs and the destination nested under /mnt.
# Preserve owners/modes, hardlinks, symlinks, ACLs, xattrs for REAL files.
tar -C / --one-file-system --acls --xattrs --numeric-owner --sparse \
    --exclude='./dev' --exclude='./dev/*' \
    --exclude='./proc' --exclude='./proc/*' \
    --exclude='./sys' --exclude='./sys/*' \
    --exclude='./run' --exclude='./run/*' \
    --exclude='./tmp/*' \
    --exclude='./mnt/xoom-system-install' \
    --exclude='./mnt/xoom-system-install/*' \
    --exclude='./home/xoom/mz600-bigpart-p8-install-*.log' \
    -cpf - . |
    tar -C "$MOUNT" --acls --xattrs --numeric-owner -xpf -
mkdir -p "$MOUNT"/{dev,proc,sys,run,tmp,mnt,media}
chmod 1777 "$MOUNT/tmp"
[[ -x "$MOUNT/sbin/init" && -r "$MOUNT/etc/debian_version" ]] ||
    fail 'Installed Debian root missing essential systemd files'
cmp /etc/debian_version "$MOUNT/etc/debian_version" ||
    fail 'Installed Debian version mismatch'
cmp /sbin/init "$MOUNT/sbin/init" ||
    fail 'Installed systemd binary differs'
[[ -d "$MOUNT/lib/modules/$EXPECTED_KERN" ]] ||
    fail 'Installed Linux7 modules missing'
# Replace ONLY the copied root fstab selector; leave removable Debian unchanged.
cp -p "$MOUNT/etc/fstab" "$MOUNT/etc/fstab.original-sd"
awk -v uuid="$P8_ID" '
    $1 !~ /^#/ && $2 == "/" && $3 == "ext4" {
        if (++hits > 1) exit 2
        $1 = "PARTUUID=" uuid
    }
    {print}
    END {if (hits != 1) exit 3}
' "$MOUNT/etc/fstab.original-sd" > "$MOUNT/etc/fstab.new" ||
    fail 'Failed to update copied root fstab'
chmod 0644 "$MOUNT/etc/fstab.new"
mv "$MOUNT/etc/fstab.new" "$MOUNT/etc/fstab"
grep -Fq "PARTUUID=$P8_ID / ext4" "$MOUNT/etc/fstab" ||
    fail 'Internal root fstab update failed'
FREE_KIB=$(df -Pk "$MOUNT" | awk 'NR==2 {print $4}')
[[ "$FREE_KIB" =~ ^[0-9]+$ && "$FREE_KIB" -gt 140000 ]] ||
    fail 'Insufficient remaining target system space'
printf 'DEBIAN_FILE_COPY_AND_FSTAB_PASS FREE_KIB=%s\n' "$FREE_KIB"
sync
umount "$MOUNT"
mounted=0
trap - EXIT
# Read-only offline metadata check; physical root boot is still REQUIRED.
set +e
/usr/sbin/e2fsck -fn "$TARGET" >/tmp/xoom-system-fsck-output.txt 2>&1
code=$?
set -e
[[ $code == 0 ]] || fail "Post-copy read-only ext4 check reported status $code"
printf 'READ_ONLY_FSCK_PASS\n'
printf 'P8_SYSTEM_INSTALLATION_COMPLETE_NOT_BOOT_VERIFIED\n'
printf 'P7_BOOT_AND_P6_TWRP_STILL_UNCHANGED\n'
printf 'Use separately hashed Stage-C temporary boot to test internal root.\n'
