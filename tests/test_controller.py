import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from attack_controller import AttackController

class TestAttackController(unittest.TestCase):
    
    def setUp(self):
        self.controller = AttackController()
    
    def test_controller_initialization(self):
        self.assertEqual(self.controller.target_url, "http://192.168.101.12:5001")
    
    def test_banner_executes(self):
        # Just ensure it doesn't crash
        self.controller.banner()
        self.assertTrue(True)
    
    def test_run_attack_unknown_type(self):
        result = self.controller.run_attack("unknown_attack_type")
        self.assertFalse(result)
    
    def test_run_attack_bruteforce(self):
        # Test with minimal parameters
        result = self.controller.run_attack("bruteforce", username="test", attempts=1)
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()
