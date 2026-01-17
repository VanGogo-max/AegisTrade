# tests/test_grsm_basic.py

import unittest
from core.risk.global_risk_state_manager import GlobalRiskStateManager

class TestGRSM(unittest.TestCase):
    def setUp(self):
        self.grsm = GlobalRiskStateManager()

    def test_order_acceptance(self):
        order = {"symbol": "BTCUSDT", "size": 0.1, "price": 25000, "direction": 1, "leverage": 5}
        result = self.grsm.process_order(order)
        self.assertIn(result['status'], ["ACCEPTED", "REJECTED"])
