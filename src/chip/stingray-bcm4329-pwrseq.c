// SPDX-License-Identifier: GPL-2.0-only
/*
 * Motorola Stingray / Broadcom BCM4329 shared resource sequencer prototype.
 *
 * REVIEW-ONLY. Do not enable in a boot image until both WLAN and Bluetooth
 * consumer ownership have been migrated and the system-level DT validated.
 *
 * This driver deliberately does not request GPIO U4, I7, U2 or U0.
 * U4 already has a regulator-fixed owner, and the reset and BT control
 * GPIOs are currently owned by mmc-pwrseq-simple and hci_bcm.
 * Instead, a shared pwrseq unit holds a regulator vote through the
 * normal regulator framework. Each named target depends on that unit,
 * allowing WLAN and Bluetooth to retain common power without double
 * claiming GPIOs. This source is not a complete chip integration.
 */
#include <linux/clk.h>
#include <linux/device.h>
#include <linux/err.h>
#include <linux/module.h>
#include <linux/of.h>
#include <linux/platform_device.h>
#include <linux/pwrseq/provider.h>
#include <linux/regulator/consumer.h>

struct stingray_bcm4329 {
	struct device *dev;
	struct regulator *shared_supply;
	struct clk *lpo;
};

static int stingray_bcm4329_enable(struct pwrseq_device *seq)
{
	struct stingray_bcm4329 *ctx = pwrseq_device_get_drvdata(seq);
	int ret;

	/* Keep ordering explicit; whether this is correct for the actual
	 * chip's physical power-up remains subject to GPIO/PMU testing.
	 */
	ret = clk_prepare_enable(ctx->lpo);
	if (ret)
		return ret;

	ret = regulator_enable(ctx->shared_supply);
	if (ret) {
		clk_disable_unprepare(ctx->lpo);
		return ret;
	}
	dev_info(ctx->dev, "BCM4329 shared resource vote acquired\n");
	return 0;
}

static int stingray_bcm4329_disable(struct pwrseq_device *seq)
{
	struct stingray_bcm4329 *ctx = pwrseq_device_get_drvdata(seq);
	int ret;

	ret = regulator_disable(ctx->shared_supply);
	if (ret)
		return ret;

	clk_disable_unprepare(ctx->lpo);
	dev_info(ctx->dev, "BCM4329 shared resource vote released\n");
	return 0;
}

static const struct pwrseq_unit_data stingray_shared_unit = {
	.name = "shared-lpo-regulator",
	.enable = stingray_bcm4329_enable,
	.disable = stingray_bcm4329_disable,
};

static const struct pwrseq_unit_data *stingray_wlan_deps[] = {
	&stingray_shared_unit,
	NULL,
};
static const struct pwrseq_unit_data *stingray_bt_deps[] = {
	&stingray_shared_unit,
	NULL,
};

static const struct pwrseq_unit_data stingray_wlan_unit = {
	.name = "wlan-pass-through",
	.deps = stingray_wlan_deps,
};
static const struct pwrseq_unit_data stingray_bt_unit = {
	.name = "bluetooth-pass-through",
	.deps = stingray_bt_deps,
};

static const struct pwrseq_target_data stingray_wlan_target = {
	.name = "wlan",
	.unit = &stingray_wlan_unit,
};
static const struct pwrseq_target_data stingray_bt_target = {
	.name = "bluetooth",
	.unit = &stingray_bt_unit,
};
static const struct pwrseq_target_data *stingray_targets[] = {
	&stingray_wlan_target,
	&stingray_bt_target,
	NULL,
};

static int stingray_bcm4329_match(struct pwrseq_device *seq,
				 struct device *candidate)
{
	struct stingray_bcm4329 *ctx = pwrseq_device_get_drvdata(seq);
	struct device_node *chip;
	bool found;

	if (!candidate->of_node)
		return PWRSEQ_NO_MATCH;

	/* Explicit, review-only per-consumer reference; no heuristic that
	 * could steal a similarly named BCM device on a different board.
	 */
	chip = of_parse_phandle(candidate->of_node, "motorola,shared-chip", 0);
	if (!chip)
		return PWRSEQ_NO_MATCH;
	found = chip == ctx->dev->of_node;
	of_node_put(chip);
	return found ? PWRSEQ_MATCH_OK : PWRSEQ_NO_MATCH;
}

static int stingray_bcm4329_probe(struct platform_device *pdev)
{
	struct device *dev = &pdev->dev;
	struct stingray_bcm4329 *ctx;
	struct pwrseq_config cfg = {};
	struct pwrseq_device *seq;

	ctx = devm_kzalloc(dev, sizeof(*ctx), GFP_KERNEL);
	if (!ctx)
		return -ENOMEM;
	ctx->dev = dev;
	ctx->shared_supply = devm_regulator_get(dev, "shared");
	if (IS_ERR(ctx->shared_supply))
		return dev_err_probe(dev, PTR_ERR(ctx->shared_supply),
				     "shared regulator missing\n");
	ctx->lpo = devm_clk_get(dev, "lpo");
	if (IS_ERR(ctx->lpo))
		return dev_err_probe(dev, PTR_ERR(ctx->lpo),
				     "LPO clock missing\n");

	cfg.parent = dev;
	cfg.owner = THIS_MODULE;
	cfg.drvdata = ctx;
	cfg.match = stingray_bcm4329_match;
	cfg.targets = stingray_targets;
	seq = devm_pwrseq_device_register(dev, &cfg);
	return PTR_ERR_OR_ZERO(seq);
}

static const struct of_device_id stingray_bcm4329_ids[] = {
	{ .compatible = "motorola,stingray-bcm4329-shared-pwrseq" },
	{}
};
MODULE_DEVICE_TABLE(of, stingray_bcm4329_ids);

static struct platform_driver stingray_bcm4329_driver = {
	.probe = stingray_bcm4329_probe,
	.driver = {
		.name = "stingray-bcm4329-pwrseq",
		.of_match_table = stingray_bcm4329_ids,
	},
};
module_platform_driver(stingray_bcm4329_driver);

MODULE_DESCRIPTION("Prototype shared Broadcom BCM4329 resource owner for Motorola Stingray");
MODULE_LICENSE("GPL");
