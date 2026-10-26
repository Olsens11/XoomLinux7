#!/usr/bin/env python3
"""Pure host-only BCM4329 shared-chip power model qualification."""
import unittest
from bcm4329_shared_chip_model import Logic, Observation, SharedVotes, or_regulator
L,H,U=Logic.LOW,Logic.HIGH,Logic.UNKNOWN
class GateTruthTable(unittest.TestCase):
 def test_4_defined_input_pairs(self):
  self.assertIs(or_regulator(L,L),L)
  self.assertIs(or_regulator(L,H),H)
  self.assertIs(or_regulator(H,L),H)
  self.assertIs(or_regulator(H,H),H)
 def test_unknown_not_assumed_off(self):
  self.assertIs(or_regulator(U,L),U)
  self.assertIs(or_regulator(L,U),U)
  self.assertIs(or_regulator(U,U),U)
  self.assertIs(or_regulator(H,U),H)
 def test_bt_high_blocks_chip_regulator_off(self):
  sample=Observation(L,H,L,L,internal_regulators_confirmed_off=False)
  self.assertFalse(sample.whole_chip_power_off_proven)
 def test_unmeasured_internal_power_cannot_claim_off(self):
  sample=Observation(L,L,L,L)
  self.assertIs(sample.regulator_enable_demand,L)
  self.assertFalse(sample.whole_chip_power_off_proven)
 def test_confirmed_both_low_and_internal_off(self):
  sample=Observation(L,L,L,L,internal_regulators_confirmed_off=True)
  self.assertTrue(sample.whole_chip_power_off_proven)
 def test_both_low_but_internal_still_on_not_off(self):
  sample=Observation(L,L,L,L,internal_regulators_confirmed_off=False)
  self.assertFalse(sample.whole_chip_power_off_proven)
 def test_bt_off_wlan_on_allowed(self):
  sample=Observation(H,L,H,L)
  self.assertIs(sample.regulator_enable_demand,H)
  self.assertTrue(sample.bt_reset_held)
  self.assertTrue(sample.wlan_reset_released)
 def test_bluetooth_on_wlan_off_allowed(self):
  sample=Observation(L,H,L,H)
  self.assertIs(sample.regulator_enable_demand,H)
  self.assertFalse(sample.wlan_reset_released)
 def test_sdio_access_after_true_supply_settle(self):
  sample=Observation(H,L,H,L,True,True,20.0,130.0)
  self.assertTrue(sample.sdio_access_qualified())
  self.assertFalse(sample.sdio_access_qualified(150.0))
 def test_109_ms_not_110_ms(self):
  sample=Observation(H,L,H,L,True,True,20.0,129.0)
  self.assertFalse(sample.sdio_access_qualified())
 def test_host_delay_without_supply_measurement_not_proof(self):
  sample=Observation(H,L,H,L,True,True,None,500.0)
  self.assertFalse(sample.sdio_access_qualified())
 def test_clock_mismatch_not_qualified(self):
  sample=Observation(H,L,H,L,True,False,0.0,200.0)
  self.assertFalse(sample.sdio_access_qualified())
 def test_wifi_reset_still_asserted_not_qualified(self):
  sample=Observation(H,L,L,L,True,True,0.0,200.0)
  self.assertFalse(sample.sdio_access_qualified())
 def test_reference_unknown_not_qualified(self):
  sample=Observation(H,L,H,L,True,None,0.0,200.0)
  self.assertFalse(sample.sdio_access_qualified())
 def test_vote_refcounts(self):
  v=SharedVotes()
  v.acquire("wlan");v.acquire("wlan");v.acquire("bluetooth")
  self.assertEqual(v.requested_pins(),(H,H))
  v.release("wlan");self.assertEqual(v.requested_pins(),(H,H))
  v.release("wlan");self.assertEqual(v.requested_pins(),(L,H))
  self.assertFalse(v.full_off_can_be_requested())
  v.release("bluetooth");self.assertTrue(v.full_off_can_be_requested())
  self.assertEqual(v.requested_pins(),(L,L))
 def test_oem_shared_u4_bluetooth_can_keep_chip_on(self):
  v=SharedVotes()
  self.assertEqual(v.motorola_shared_u4_plan(),(L,L))
  v.acquire("bluetooth")
  self.assertEqual(v.motorola_shared_u4_plan(),(H,L))
  v.acquire("wlan")
  v.release("bluetooth")
  self.assertEqual(v.motorola_shared_u4_plan(),(H,L))
  v.release("wlan")
  self.assertEqual(v.motorola_shared_u4_plan(),(L,L))
 def test_oem_bt_shutdown_low_is_not_power_off_when_u4_high(self):
  v=SharedVotes();v.acquire("bluetooth")
  u4,i7=v.motorola_shared_u4_plan()
  self.assertIs(or_regulator(u4,i7),H)
 def test_independent_current_dt_plan_differs_from_oem_bt_only(self):
  v=SharedVotes();v.acquire("bluetooth")
  self.assertEqual(v.requested_pins(),(L,H))
  self.assertEqual(v.motorola_shared_u4_plan(),(H,L))
 def test_vote_unbalanced_release_refused(self):
  v=SharedVotes()
  with self.assertRaises(ValueError):v.release("bluetooth")
  with self.assertRaises(ValueError):v.release("wlan")
  with self.assertRaises(ValueError):v.acquire("fm")
 def test_no_full_por_claim_without_real_feedback(self):
  v=SharedVotes()
  self.assertTrue(v.full_off_can_be_requested())
  self.assertFalse(v.full_off_is_proven(Observation(L,L,L,L)))
  self.assertFalse(v.full_off_is_proven(Observation(L,H,L,L,internal_regulators_confirmed_off=True)))
  self.assertTrue(v.full_off_is_proven(Observation(L,L,L,L,internal_regulators_confirmed_off=True)))
 def test_oem_bt_initial_block_can_release_wlan_shared_u4_vote(self):
  # Motorola 2a65edc board-stingray-bluetooth.c probes BT by blocking it;
  # board-stingray.c uses a shared, UNtyped U4 count. This is an offline
  # possible interleaving, never a claim it occurred on the original board.
  count=1 # only WLAN acquired shared physical U4 vote
  if count>0:count-=1 # OEM initial BT-block callback releases it
  self.assertEqual(count,0) # WLAN vote accidentally consumed in this order
  guarded=SharedVotes();guarded.acquire("wlan")
  with self.assertRaises(ValueError):guarded.release("bluetooth")
  self.assertEqual(guarded.motorola_shared_u4_plan(),(H,L))
  self.assertEqual((guarded.wlan_users,guarded.bt_users),(1,0))
if __name__=="__main__":unittest.main(verbosity=2)
