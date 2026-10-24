# Original integration sources

- `board/`: Stingray DTS and USB-peripheral diagnostic derivative of the original Wingray DTS, preserving original GPL SPDX.
- `diag-init/`: v03-v14 freestanding PID1 diagnostic C source snapshots; individually versioned by test stage.
- Kernel source itself is external: `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`, fetched locally rather than committed wholesale.

Full source file placement is listed in [source map](../docs/reference/SOURCE_MAP.md). Keep generated binaries private or in explicitly reviewed releases.
