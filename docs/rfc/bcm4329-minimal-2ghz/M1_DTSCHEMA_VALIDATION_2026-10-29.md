# M1 Device Tree schema environment and validation — 2026-10-29

**Milestone:** M1 board description, source proof only. **Result:** targeted binding validation and both Xoom compatible/DTB checks PASS; broader schema warnings remain inherited. **Not a boot or regulator/radio qualification.**

## Installed development environment

On authorized desktop `DESKTOP-R16QJD4`, WSL `Ubuntu-22.04`, installed scoped prerequisites `python3-venv`, `swig`, `python3-dev`, `libyaml-dev` using Ubuntu packages. Installed Python **`dtschema 2026.9`**, `yamllint 1.38.0` (and package dependencies including `pylibfdt 1.7.2.post2`) inside an isolated venv:

```
/home/xoomdev/xoom-linux-rom/.venvs/rfc-m1-dtschema-20261029
```

The earlier incomplete environment was preserved as `rfc-m1-dtschema-20261029-incomplete-bootstrap` rather than overwriting it. No Python packages were installed into the system Python interpreter. The installation follows the [Linux kernel Device Tree schema documentation](https://docs.kernel.org/devicetree/bindings/writing-schema.html).

## Reproducible source and commands

- Pinned upstream Linux 7: `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`.
- **Separate** local study worktree `/home/xoomdev/xoom-linux-rom/rfc-m1-dt-proof-20261029`, source tip `0d4d7d3161b6ed9595f2cf28200535d59dcb3e0f`, incorporating three independent unaccepted M1 proof commits.
- Build out-of-tree `/home/xoomdev/xoom-linux-rom/rfc-m1-dtb-prototype-build-20261029` using the same ARM config/toolchain as the original upstream DTB comparison.
- **Main clean RFC Linux source** `/home/xoomdev/xoom-linux-rom/rfc-bcm4329-minimal-2ghz-20261029` remains at original pinned upstream with **zero added source patches**.

Commands (run from WSL, substituting the paths above):

```bash
export PATH="/home/xoomdev/xoom-linux-rom/.venvs/rfc-m1-dtschema-20261029/bin:$PATH"
SRC=/home/xoomdev/xoom-linux-rom/rfc-m1-dt-proof-20261029
OUT=/home/xoomdev/xoom-linux-rom/rfc-m1-dtb-prototype-build-20261029
CROSS=/home/xoomdev/xoom-linux-rom/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-
SCHEMA=Documentation/devicetree/bindings/arm/tegra.yaml

dt-doc-validate "$SRC/$SCHEMA"
make -s -C "$SRC" O="$OUT" ARCH=arm CROSS_COMPILE="$CROSS" \
  DT_SCHEMA_FILES="$SCHEMA" dt_binding_check
make -s -C "$SRC" O="$OUT" ARCH=arm CROSS_COMPILE="$CROSS" -j 8 \
  DT_SCHEMA_FILES="$SCHEMA" dtbs_check

PREPARSED="$OUT/Documentation/devicetree/bindings/processed-schema.json"
for model in wingray stingray; do
  dt-validate -s "$PREPARSED" -l arm/tegra.yaml \
    "$OUT/arch/arm/boot/dts/nvidia/tegra20-motorola-$model.dtb"
done
```

## Exact observed results

| Test | Result | Qualification |
| --- | --- | --- |
| `dt-doc-validate` on study `arm/tegra.yaml` | **PASS, exit 0**, no diagnostics | YAML binding document validates |
| Kernel `dt_binding_check`, filtered to `arm/tegra.yaml` | **PASS, exit 0**, **0 output lines** | Schema package usable and targeted binding accepted |
| Kernel `dtbs_check` (same filtered schema) | **Exit 0**, **243 diagnostic lines** | Warnings/error text refers to **three OTHER boards**; not a warning-free whole-tree pass |
| `dt-validate -l arm/tegra.yaml` on prototype Wingray | **PASS, exit 0**, **0 output lines** | Exact Wingray root compatible matches targeted schema |
| `dt-validate -l arm/tegra.yaml` on prototype Stingray | **PASS, exit 0**, **0 output lines** | Exact Stingray root compatible matches targeted schema |
| Broader `dt-validate` on original and refactored Wingray | **66 diagnostic lines each**, identical multisets after normalizing DTB paths | Independent evidence the refactor introduced **zero new broad-schema diagnostics for Wingray**; broad schema has preexisting board-description inconsistencies |

Three unrelated device trees named in filtered `dtbs_check` output: `tegra20-lg-star.dtb`, `tegra30-microsoft-surface-rt-efi.dtb`, and `tegra30-microsoft-surface-rt.dtb`. Do not misattribute their `oneOf` root compatible messages to Motorola Xoom. In the **unfiltered** direct validation, inherited regulator, GPIO keys, panel and other issues also appear; these are not fixed by this M1 compatible/variant change. The full original and refactored Wingray schema-diagnostic line multisets matched exactly.

Local outputs (not containing private firmware or identities):

```
/home/xoomdev/xoom-linux-rom/inspection/rfc-m1-dtschema-20261029/binding.log
/home/xoomdev/xoom-linux-rom/inspection/rfc-m1-dtschema-20261029/dtbs.log
/home/xoomdev/xoom-linux-rom/inspection/rfc-m1-dtschema-20261029/wingray-tegra-only.log
/home/xoomdev/xoom-linux-rom/inspection/rfc-m1-dtschema-20261029/stingray-tegra-only.log
/home/xoomdev/xoom-linux-rom/inspection/rfc-m1-dtschema-20261029/untouched-wingray-all-schemas.log
```

## Milestone decision and rollback

**Check off the binding/tooling and Xoom-targeted schema subchecks** under M1c. Do **not** mark all of M1c/M1 complete: authoritative MZ600/MZ604 board differences, broader bindings, reviewer-friendly commit messages and MAINTAINERS checks, controlled MZ600 boot/SDIO/USB and MZ604 physical parity are still pending.

No Linux source patch was amended during the tooling installation; no new Git revision of the M1 proof source was needed. Prior r7, primary RFC zero-patch Linux source, original MZ600 p10 Linux installation and Wi-Fi remain unchanged. Rollback of installed tools is optional (remove project venv and apt prerequisites if desired); **no on-device rollback is required**. The M1 owning issue is [#17](https://github.com/Olsens11/XoomLinux7/issues/17).
