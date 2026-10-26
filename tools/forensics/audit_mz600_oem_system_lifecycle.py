#!/usr/bin/env python3
"""Version-pinned, offline Motorola MZ600 BCM4329 cross-layer source + ELF audit.

No device access, networking, firmware payload read, NVRAM, identity or RF writes.
The result is a set of source/ELF contracts, NOT proof of executed paths, physical
timing, electrical GPIO states, or Linux 7 functional equivalence.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

FILES = {
    "Makefile": (
        "drivers/net/wireless/bcm4329/Makefile",
        "57260ea887ef12166a87083046d0dc03a84ba4145935ca4ae592f63599dafec0"),
    "dhd_linux.c": (
        "drivers/net/wireless/bcm4329/dhd_linux.c",
        "d9eaaad014d25fbac09c46e92ff09c0c70aefa027f657d2979e088fc9d44ae92"),
    "dhd_custom_gpio.c": (
        "drivers/net/wireless/bcm4329/dhd_custom_gpio.c",
        "3be537d72d2426ac56f2c4b397272f07b6b1276865fb2be557121da81ac873e5"),
    "board-stingray-wifi.c": (
        "arch/arm/mach-tegra/board-stingray-wifi.c",
        "e8b92a268bca6bc1c7798159d731117022223c45e8926b7307987e9b74ccb494"),
    "board-stingray.c": (
        "arch/arm/mach-tegra/board-stingray.c",
        "916df985cbba4d5abc855772388042dd6d0f9f99418dcbd6e452fbb35d0b63e7"),
    "board-stingray-bluetooth.c": (
        "arch/arm/mach-tegra/board-stingray-bluetooth.c",
        "e2cf7582371d5a9a59ac6c237a8d7a6436410025009f57cce15dfecdc93f9fef"),
    "dhd_sdio.c": (
        "drivers/net/wireless/bcm4329/dhd_sdio.c",
        "e8ad9ef7bac25f6ba82140e1b44387ce537bd484bfbfe38289b923eadba2d016"),
    "siutils.c": (
        "drivers/net/wireless/bcm4329/siutils.c",
        "1d30a5c249c6a05c3fef59cedf4705a278c04c86dea3e334c48a1f70b3eeb092"),
}
ELF_SHA = "4bf267fb432deb068a38849d87c744a2397ef4a7c7fc79476e265f3571d4ab0f"
MODERN_SDIO_SHA = "cfc4635e4ae8c5690535b3933a4fd5387d3fbe6256f575c8794b074248fbf8f6"


def hashfile(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def extract(text, first, last):
    x = text.find(first)
    if x < 0:
        return ""
    y = text.find(last, x + len(first))
    if y < 0:
        return ""
    return text[x:y]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--oem-root", type=Path, required=True)
    parser.add_argument("--oem-module", type=Path, required=True)
    parser.add_argument("--linux-root", type=Path)
    parser.add_argument("--json", type=Path, help="Output sanitized boolean/report JSON")
    args = parser.parse_args()
    cases = []
    texts = {}

    def check(name, expr, level, comment=""):
        cases.append({"id": name, "passed": bool(expr), "evidence_level": level,
                      "note": comment})
        print(("PASS " if expr else "FAIL ") + name, flush=True)

    for name, (relative, expected) in FILES.items():
        target = args.oem_root / relative
        ok = target.is_file() and hashfile(target) == expected
        check("pinned_source_sha:" + name, ok, "file_sha")
        if ok:
            texts[name] = target.read_text(errors="replace")
    if len(texts) < len(FILES):
        return finish(args, cases)
    mk, gpio, dhd = (texts[k] for k in ("Makefile", "dhd_custom_gpio.c", "dhd_linux.c"))
    board = texts["board-stingray-wifi.c"]
    system = texts["board-stingray.c"]
    bt = texts["board-stingray-bluetooth.c"]
    sdio, si = texts["dhd_sdio.c"], texts["siutils.c"]
    symbols = set()
    elf_ok = args.oem_module.is_file() and hashfile(args.oem_module) == ELF_SHA
    check("original_hri39_oem_module_sha", elf_ok, "file_sha")
    if elf_ok:
        nm = subprocess.run(["nm", str(args.oem_module)], capture_output=True,
                            text=True, check=True).stdout
        symbols = {line.split()[-1] for line in nm.splitlines() if line.split()}
    check("makefile_enables_customer_hw2", "-DCUSTOMER_HW2" in mk, "source")
    check("makefile_enables_unique_mac_callback", "-DGET_CUSTOM_MAC_ENABLE" in mk, "source")
    check("makefile_enables_hw_oob_irq", "-DHW_OOB" in mk and "-DOOB_INTR_ONLY" in mk, "source")
    platform_guard = "#if defined(CUSTOMER_HW2) && defined(CONFIG_WIFI_CONTROL_FUNC)"
    check("platform_callbacks_under_both_compile_conditions",
          platform_guard in dhd and "static int wifi_probe(" in dhd
          and "static int wifi_remove(" in dhd, "source")
    check("shipping_elf_proves_platform_callbacks_compiled",
          {"wifi_probe", "wifi_remove", "wifi_set_carddetect", "wifi_set_power",
           "wifi_add_dev", "wifi_del_dev"} <= symbols, "elf_symbol",
          "With CUSTOMER_HW2 in the Makefile, ELF presence constrains CONFIG_WIFI_CONTROL_FUNC.")
    check("shipping_elf_proves_early_suspend_compiled",
          "dhd_set_suspend" in symbols and "#if defined(CONFIG_HAS_EARLYSUSPEND)" in dhd,
          "elf_symbol", "Platform wifi_suspend/resume are separate no-op callbacks.")
    probe = extract(dhd, "static int wifi_probe(", "static int wifi_remove(")
    remove = extract(dhd, "static int wifi_remove(", "static int wifi_suspend(")
    check("oem_probe_power_before_logical_carddetect",
          probe.find("wifi_set_power(1, 0)") >= 0
          and probe.find("wifi_set_carddetect(1)") > probe.find("wifi_set_power(1, 0)"), "source")
    check("oem_remove_power_off_before_carddetect_off",
          remove.find("wifi_set_power(0, 0)") >= 0
          and remove.find("wifi_set_carddetect(0)") > remove.find("wifi_set_power(0, 0)"), "source")
    check("platform_suspend_resume_callbacks_are_noop",
          "return 0;" in extract(dhd, "static int wifi_suspend(", "static int wifi_resume(")
          and "return 0;" in extract(dhd, "static int wifi_resume(", "static struct platform_driver wifi_device"),
          "source", "Does not imply whole driver PM is no-op; early-suspend modifies firmware.")
    wlan_power_on = extract(gpio, "case WLAN_POWER_ON:", "break;")
    wlan_power_off = extract(gpio, "case WLAN_POWER_OFF:", "break;")
    check("generic_power_on_does_not_double_vote_under_customer_hw2",
          "#ifdef CUSTOMER_HW" in wlan_power_on
          and "#ifdef CUSTOMER_HW2" not in wlan_power_on
          and "bcm_wlan_power_on(1)" in wlan_power_on
          and "#ifdef CUSTOMER_HW" in wlan_power_off
          and "#ifdef CUSTOMER_HW2" not in wlan_power_off, "source",
          "The separate RESET_ON/OFF cases do call wifi_set_power under CUSTOMER_HW2.")
    init = extract(dhd, "static int __init\ndhd_module_init(", "module_init(dhd_module_init)")
    check("startup_platform_probe_before_sdio_bus_registration",
          0 <= init.find("wifi_add_dev()") < init.find("dhd_bus_register()")
          and init.find("down_timeout(&wifi_control_sem") < init.find("dhd_bus_register()"),
          "source")
    check("startup_failure_unregisters_platform_and_runs_customer_power_off",
          "fail_2:" in init and "dhd_bus_unregister()" in init
          and "fail_1:" in init and "wifi_del_dev()" in init
          and "dhd_customer_gpio_wlan_ctrl(WLAN_POWER_OFF)" in init, "source")
    cleanup = extract(dhd, "static void __exit\ndhd_module_cleanup(", "static int __init\ndhd_module_init(")
    check("module_cleanup_sdio_before_platform_remove",
          cleanup.find("dhd_bus_unregister()") >= 0
          and cleanup.find("wifi_del_dev()") > cleanup.find("dhd_bus_unregister()"), "source")
    pwr = extract(board, "static int stingray_wifi_power(int on)", "static int stingray_wifi_reset_state;")
    check("staged_power_100ms_u4_100ms_u2_200ms",
          bool(re.search(r"mdelay\(100\).*change_power_brcm_4329\(on\).*mdelay\(100\).*gpio_set_value\(STINGRAY_WLAN_RST, on\).*mdelay\(200\)",
                         pwr, re.S)), "source")
    check("board_wlan_reset_initially_asserted",
          "gpio_direction_output(STINGRAY_WLAN_RST, 0)" in board, "source")
    check("oem_sdmmc2_tap_delay_six",
          'clk_get_sys("sdhci-tegra.1", NULL)' in system
          and "tegra_sdmmc_tap_delay(clk, 6)" in system, "source",
          "Board-specific trace-delay decision; not proof of the live v06.4 pad state.")
    embedded = extract(board, "static struct embedded_sdio_data stingray_wifi_emb_data", "static int stingray_wifi_cd")
    for key, val in (("sdio_vsn",2),("multi_block",1),("low_speed",0),
                     ("wide_bus",0),("high_power",1),("high_speed",1)):
        check("oem_sdio_override_" + key,
              bool(re.search(r"\." + key + r"\s*=\s*" + str(val) + r"\b", embedded)), "source")
    check("embedded_card_ocr_carddetect_registration",
          "MMC_VDD_165_195" in board and ".built_in" in board
          and ".register_status_notify" in board and ".embedded_sdio" in board, "source")
    shared = extract(system, "void change_power_brcm_4329(bool enable)", "static void __init tegra_stingray_init(")
    check("shared_u4_vote_spinlock_saturates_at_two",
          "spin_lock_irqsave" in shared and "TEGRA_GPIO_PU4" in shared
          and "brcm_4329_enable_count++" in shared
          and "brcm_4329_enable_count > 2" in shared, "source",
          "Untyped shared vote counter: per-consumer balance unknown.")
    check("shared_power_only_turns_u4_off_when_zero",
          "if (!brcm_4329_enable_count)" in shared
          and "gpio_set_value(TEGRA_GPIO_PU4, enable)" in shared, "source")
    check("oem_bluetooth_gpio_pins_i7_u0_u1_u6",
          all(k in bt for k in ("BT_SHUTDOWN_GPIO TEGRA_GPIO_PI7",
              "BT_RESET_GPIO TEGRA_GPIO_PU0",
              "BT_WAKE_GPIO TEGRA_GPIO_PU1",
              "BT_HOST_WAKE_GPIO TEGRA_GPIO_PU6")), "source")
    rfkill = extract(bt, "static int bcm4329_bt_rfkill_set_power(",
                     "static const struct rfkill_ops bcm4329_bt_rfkill_ops")
    on = extract(rfkill, "if (!blocked)", "} else {")
    off = extract(rfkill, "} else {", "return 0;")
    check("oem_bt_unblock_u4_vote_then_u0_reset_release_i7_low",
          on.find("change_power_brcm_4329(true)") >= 0
          and on.find("gpio_direction_output(BT_RESET_GPIO, 1)") > on.find("change_power_brcm_4329(true)")
          and on.find("gpio_direction_output(BT_SHUTDOWN_GPIO, 0)") > on.find("gpio_direction_output(BT_RESET_GPIO, 1)"),
          "source")
    check("oem_bt_block_releases_u4_before_i7_low_u0_reset",
          off.find("change_power_brcm_4329(false)") >= 0
          and off.find("gpio_direction_output(BT_SHUTDOWN_GPIO, 0)") > off.find("change_power_brcm_4329(false)")
          and off.find("gpio_direction_output(BT_RESET_GPIO, 0)") > off.find("gpio_direction_output(BT_SHUTDOWN_GPIO, 0)"),
          "source")
    btprobe = extract(bt, "static int bcm4329_bluetooth_probe(",
                      "static int bcm4329_bluetooth_remove(")
    check("oem_bt_probe_initial_block_before_rfkill_alloc",
          btprobe.find("bcm4329_bt_rfkill_set_power(NULL, true)") >= 0
          and btprobe.find("rfkill_alloc(") > btprobe.find("bcm4329_bt_rfkill_set_power(NULL, true)"),
          "source", "Possible cross-consumer decrement of untyped U4 counter; runtime ordering not established")
    check("oem_bt_probe_gpio_requests_reset_and_shutdown",
          "gpio_request(BT_RESET_GPIO" in btprobe
          and "gpio_request(BT_SHUTDOWN_GPIO" in btprobe, "source")
    check("oem_bt_lpm_gpio_irq_and_timer",
          "gpio_direction_output(BT_WAKE_GPIO, 0)" in bt
          and "gpio_direction_input(BT_HOST_WAKE_GPIO)" in bt
          and "request_irq(irq, host_wake_isr" in bt
          and "hrtimer_start(&bt_lpm.enter_lpm_timer" in bt, "source")
    btremove = extract(bt, "static int bcm4329_bluetooth_remove(",
                       "static struct platform_driver bcm4329_bluetooth_platform_driver")
    check("oem_bt_remove_has_no_explicit_shared_vote_release",
          "rfkill_unregister(bt_rfkill)" in btremove
          and "gpio_free(BT_RESET_GPIO)" in btremove
          and "gpio_free(BT_SHUTDOWN_GPIO)" in btremove
          and "change_power_brcm_4329" not in btremove, "source",
          "Absence of explicit call does not establish whether rfkill_unregister invokes a callback")
    check("board_registers_bt_platform_before_wlan_board_init",
          0 <= system.find("&bcm4329_bluetooth_device")
          and 0 <= system.find("platform_add_devices(stingray_devices, ARRAY_SIZE(stingray_devices))")
          < system.find("stingray_wlan_init();"), "source",
          "Platform-device registration order is not Bluetooth-driver probe time")
    check("firmware_arm_reset_and_nvram_download",
          "dhdsdio_download_firmware" in sdio
          and "dhdsdio_download_state" in sdio, "source")
    check("sdio_f2_ready_poll_and_mailbox",
          "SDIOD_CCCR_IOEN" in sdio and "SDIOD_CCCR_IORDY" in sdio
          and "tosbmailboxdata" in sdio, "source")
    check("oem_skips_host_pmu_initialization",
          "Skip PMU initialization from the Dongle Host" in si, "source")
    check("oem_clears_chipcommon_gpio_pulls",
          "W_REG(osh, &cc->gpiopullup, 0)" in si
          and "W_REG(osh, &cc->gpiopulldown, 0)" in si, "source")
    check("early_suspend_firmware_pm_packet_filter_roam",
          "bcn_li_dtim" in dhd and "roam_off" in dhd
          and "dhd_set_packet_filter(1, dhd)" in dhd
          and "WLC_SET_PM" in dhd, "source")
    check("oem_device_reset_is_more_than_module_unload",
          "dhd_bus_devreset(dhd_pub_t *dhdp, uint8 flag)" in sdio
          and "dhdsdio_release_dongle" in sdio
          and "bcmsdh_reset" in sdio
          and "dhdsdio_download_firmware" in sdio, "source")
    for name in ["dhd_bus_devreset", "dhd_custom_get_mac_address", "dhd_customer_oob_irq_map"]:
        check("shipping_elf_symbol_" + name, name in symbols, "elf_symbol")
    if args.linux_root:
        modern = args.linux_root / "drivers/mmc/core/sdio.c"
        valid = modern.is_file() and hashfile(modern) == MODERN_SDIO_SHA
        check("pinned_linux7_normal_mmc_core_sha", valid, "file_sha")
        if valid:
            check("modern_kernel_does_not_embed_v018_override",
                  "XOOM_OEM_CAPS_V018" not in modern.read_text(errors="replace"), "source",
                  "A clean MMC core does not prove all original OEM hardware behavior is absent.")
    return finish(args, cases)


def finish(args, cases):
    passed = sum(x["passed"] for x in cases)
    report = {
        "project": "MZ600 Motorola 2.6.36.3-g2a65edc exact-generation cross-layer audit",
        "source_generation": "Motorola Tegra 2a65edc",
        "actual_oem_driver_elf_sha256": ELF_SHA,
        "oem_firmware_binary_or_nvram_read": False,
        "physical_radiowaveforms_measured": False,
        "changes_to_device_or_kernel": False,
        "conditions_are_static_compiled_presence_not_runtime_call_traces": True,
        "checked": len(cases), "passed": passed, "failed": len(cases)-passed,
        "checks": cases
    }
    if args.json:
        if args.json.exists():
            raise RuntimeError("Refusing to overwrite existing audit report")
        args.json.write_text(json.dumps(report, indent=2) + "\n")
    print("SUMMARY: " + str(passed) + "/" + str(len(cases))
          + " source/ELF checks PASS; "
          + str(len(cases)-passed) + " FAIL", flush=True)
    return 0 if len(cases) == passed else 2


if __name__ == "__main__":
    sys.exit(main())
