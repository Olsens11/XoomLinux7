#!/usr/bin/env python3
"""Pure offline model of BCM4329 shared regulator logic and sequencing guards.

Intent: prove Linux software coordination invariants BEFORE changing GPIO
ownership, device tree, MMC core or a real BCM4329. This DOES NOT represent
electrical measurements, internal PMU implementation or exact POR timing.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class Logic(Enum):
    LOW=0
    HIGH=1
    UNKNOWN=2

def or_regulator(wl: Logic, bt: Logic) -> Logic:
    """Broadcom 4329-DS105-R pp81/132: both LOW => off, either HIGH => on."""
    if wl is Logic.HIGH or bt is Logic.HIGH:
        return Logic.HIGH
    if wl is Logic.LOW and bt is Logic.LOW:
        return Logic.LOW
    return Logic.UNKNOWN

@dataclass(frozen=True)
class Observation:
    # Real chip levels, NOT an unloaded GPIO descriptor's raw latch!
    wl_reg_on: Logic
    bt_reg_on: Logic
    wl_rst_n: Logic
    bt_rst_n: Logic
    lpo_present: Optional[bool] = None
    normal_reference_present: Optional[bool] = None
    # The datasheet's VDDC/VDDIO condition is not satisfied by an MMC
    # host-side delay alone. Unmeasured chips should leave both unknown.
    vddc_and_vddio_stable_at_ms: Optional[float] = None
    first_sdio_command_at_ms: Optional[float] = None
    internal_regulators_confirmed_off: Optional[bool] = None

    @property
    def regulator_enable_demand(self) -> Logic:
        return or_regulator(self.wl_reg_on, self.bt_reg_on)

    @property
    def whole_chip_power_off_proven(self) -> bool:
        return (self.regulator_enable_demand is Logic.LOW and
                self.internal_regulators_confirmed_off is True)

    @property
    def wlan_reset_released(self) -> bool:
        return self.wl_rst_n is Logic.HIGH

    @property
    def bt_reset_held(self) -> bool:
        return self.bt_rst_n is Logic.LOW

    def sdio_access_qualified(self, minimum_margin_ms: float = 110.0) -> bool:
        """Conservative gates for host access; not a silicon POR model."""
        t0=self.vddc_and_vddio_stable_at_ms
        t1=self.first_sdio_command_at_ms
        return (self.wl_reg_on is Logic.HIGH and self.wlan_reset_released and
                self.lpo_present is True and
                self.normal_reference_present is True and
                t0 is not None and t1 is not None and
                t1-t0>=minimum_margin_ms)

@dataclass
class SharedVotes:
    """Abstract logical consumer requests; no hardware or GPIO side effects."""
    wlan_users: int = 0
    bt_users: int = 0

    def acquire(self, target: str) -> None:
        if target=="wlan": self.wlan_users+=1
        elif target=="bluetooth": self.bt_users+=1
        else: raise ValueError("unknown target: "+target)

    def release(self, target: str) -> None:
        if target=="wlan":
            if not self.wlan_users: raise ValueError("wlan release without vote")
            self.wlan_users-=1
        elif target=="bluetooth":
            if not self.bt_users: raise ValueError("bluetooth release without vote")
            self.bt_users-=1
        else: raise ValueError("unknown target: "+target)

    def requested_pins(self) -> tuple[Logic,Logic]:
        """Only requested logical outputs, NOT actual Tegra pin levels."""
        return (Logic.HIGH if self.wlan_users else Logic.LOW,
                Logic.HIGH if self.bt_users else Logic.LOW)

    def motorola_shared_u4_plan(self) -> tuple[Logic,Logic]:
        """OEM-inspired (U4, I7) output request model.

        From Motorola downstream: both WLAN and BT vote through U4, and
        the BT rfkill callback drives BT_SHUTDOWN/I7 low in both branches.
        This models that callback, NOT evidence that OEM pin I7 was always
        low throughout boot or that this plan has been qualified on Linux 7.
        """
        common = Logic.HIGH if (self.wlan_users or self.bt_users) else Logic.LOW
        return (common, Logic.LOW)

    def full_off_can_be_requested(self) -> bool:
        # A true chip reset is still conditional on physical regulators off.
        return self.wlan_users==0 and self.bt_users==0

    def full_off_is_proven(self, physical: Observation) -> bool:
        return self.full_off_can_be_requested() and physical.whole_chip_power_off_proven
