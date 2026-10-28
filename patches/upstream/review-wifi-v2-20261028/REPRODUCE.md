# Reproduce the clean MZ600 Linux 7 ARM source build

**2026-10-28:** The first full clean build was initiated with the exactly pinned base `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3` in an isolated Linux worktree, with a **fresh output directory** containing only a copied existing kernel configuration, not prior object files. The build result is recorded in `clean-arm-build-result.json` once finished.

The final device source combines **two separately owned tracks**: (a) existing three platform integration snapshots and (b) three new unsigned wireless RFC commits. All patches are source-only and do not install to the device.

## Exact replay ordering

Starting from a pristine clone of `xoom-linux/linux`, with `P` pointing to the XoomLinux7 project workspace:

```sh
BASE=2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3
P=/path/to/XoomLinux7
git checkout --detach "$BASE"
git apply --check "$P/patches/upstream/candidate/0001-arm-dts-tegra20-motorola-stingray-board.patch"
git apply "$P/patches/upstream/candidate/0001-arm-dts-tegra20-motorola-stingray-board.patch"
git apply --check "$P/patches/upstream/candidate/0002-arm-tegra-stingray-wlan-mac-atag.patch"
git apply "$P/patches/upstream/candidate/0002-arm-tegra-stingray-wlan-mac-atag.patch"
git apply --check "$P/patches/upstream/candidate/0003-block-partitions-motorola-xoom-bigpart.patch"
git apply "$P/patches/upstream/candidate/0003-block-partitions-motorola-xoom-bigpart.patch"
```

For source application only, `git apply` is sufficient. For an inspectable `git am` development history, commit each platform snapshot separately with a clearly marked *temporary RFC author* and without any invented human DCO sign-off, before proceeding:

```sh
git am "$P/patches/upstream/review-wifi-v2-20261028"/0001-*.patch
git am "$P/patches/upstream/review-wifi-v2-20261028"/0002-*.patch
git am "$P/patches/upstream/review-wifi-v2-20261028"/0003-*.patch
git diff --check "$BASE"
```

The actual isolated replay used separately committed platform snapshots, and **all six members applied in order**. This does not establish individual platform patch upstream quality.

## Clean ARM build

In the tested development environment, the matched Cortex-A9 cross compiler prefix is:

```text
/home/xoomdev/xoom-linux-rom/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-
```

Use a **new/empty** build directory and the previously proven v06.4 Debian-p8 kernel `.config` as the configuration baseline:

```sh
cp /path/to/proven-v064-build/.config /path/to/empty-build/.config
make -C /path/to/replayed-linux O=/path/to/empty-build \
  ARCH=arm CROSS_COMPILE=/path/to/arm-none-linux-gnueabihf- olddefconfig
make -C /path/to/replayed-linux O=/path/to/empty-build \
  ARCH=arm CROSS_COMPILE=/path/to/arm-none-linux-gnueabihf- -j8 zImage dtbs modules
```

Check kernel release, hashes of `zImage`, the Stingray DTB, `brcmfmac.ko` and `brcmfmac-wcc.ko` and record errors/warnings. Matched modules must come from the *same* full-source build; do not use V31 core with mismatched WCC or symbols.

**Important distinction:** This reproduces the source/kernel build, **not the already installed Debian root filesystem, private original Motorola BCM4329 firmware/NVRAM, or bootloader kernel packaging**. The p7 boot image/p8 rootfs on the living MZ600 should not be overwritten merely because the build succeeds. For physical test use a reversible staging plan, verify hashes and maintain a rollback path first. The V31 on-device success is a benchmark, not proof that these exact cleaned modules work.

## Submission gates still open

Platform snapshots: DTS coding style and bindings, board/model variants, ATAG provenance/DCO, BigPart GPT generic safety, boot kernel command line. Wireless review: exact cleaned ARM build; individual-prefix buildability; cancellation/teardown/multiple interface/regulatory audit; exact physical scan/reassociation/DHCP/HTTPS on MZ600 and later MZ602/MZ604; root-causing slow 399s boot association separately. No upstream mail, recipient list or human signoff generated as a completed action.
