/* SPDX-License-Identifier: GPL-2.0-only
 * ARM32/EABI raw reboot(2) probe for MZ600 Linux 7 recovery.
 *
 * Invoke only after proving actual replacement MZ600, root over USB,
 * SD root filesystem, and preserving fastboot recovery on Surface.
 * Linux kernel Tegra PMC reboot notifier interprets "bootloader" in
 * scratch register; this independently tests reboot to bootloader
 * without stock Android /system. No eMMC, GPT, filesystem, or radio I/O.
 * Binary has no password/host identifiers.
 */
typedef unsigned int u32;
#define NR_WRITE 4
#define NR_REBOOT 88
#define NR_EXIT 1
#define REBOOT_MAGIC1 0xfee1deadU
#define REBOOT_MAGIC2 0x28121969U
#define REBOOT_CMD_RESTART2 0xa1b2c3d4U
static const char mode[]="bootloader";
static const char msg[]="MZ600 LINUX7 REQUESTING BOOTLOADER VIA KERNEL RESTART2\n";
static long sys4(long n,long a,long b,long c,long d)
{
    register long r0 asm("r0")=a;
    register long r1 asm("r1")=b;
    register long r2 asm("r2")=c;
    register long r3 asm("r3")=d;
    register long r7 asm("r7")=n;
    asm volatile("svc 0":"+r"(r0):"r"(r1),"r"(r2),"r"(r3),"r"(r7):"memory","cc");
    return r0;
}
void _start(void)
{
    long result;
    sys4(NR_WRITE,1,(long)msg,sizeof(msg)-1,0);
    result=sys4(NR_REBOOT,REBOOT_MAGIC1,REBOOT_MAGIC2,
                REBOOT_CMD_RESTART2,(long)mode);
    /* Success does not return; nonzero means command was not executed. */
    sys4(NR_EXIT,result<0 ? 1 : 2,0,0,0);
    for(;;){}
}
