# [RFC PATCH 0/1] block: partitions: opt-in classic Xoom BigPart compatibility

Internal design note only. **NOT SENT; NO HUMAN SIGN-OFF.**

Classic Motorola Xoom BigPart is a long-standing downstream convention
that reinterprets the factory GPT's last three partition extents in
memory, retaining the on-disk GPT and first seven entries.

The pinned Linux7 Tegra MMC stack already supports NVIDIA's relocated
Android alternate GPT; the previous downstream sector override is
unnecessary. The only proposed change is the opt-in mapping, guarded by
target eMMC identification and exact CRC-validated factory geometry.

This RFC may not fit the generic GPT parser's upstream policy. Feedback
on whether and where such behavior belongs would eventually be needed,
but **no external review or submission is authorized** until the
complete BCM4329/board/Linux integration and human approval.

The older v06.4 hardware result is not a test of this new review source.
