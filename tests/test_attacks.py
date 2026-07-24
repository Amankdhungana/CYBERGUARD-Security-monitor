import unittest
import sys
import os
import tempfile

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from attacks.bruteforce import BruteForceAttack
from attacks.ddos import DDOSAttack
from attacks.request_flood import RequestFlood
from attacks.scanner import ScannerAttack

class TestBruteForce(unittest.TestCase):
    
    def setUp(self):
        self.attack = BruteForceAttack("http://192.168.101.12:5001")
    
    def test_attack_initialization(self):
        self.assertEqual(self.attack.target_url, "http://192.168.101.12:5001")
        self.assertEqual(self.attack.endpoint, "http://192.168.101.12:5001/auth/admin-login")
    
    def test_password_list_generation(self):
        passwords = self.attack.load_common_passwords()
        self.assertIsInstance(passwords, list)
        self.assertGreater(len(passwords), 0)
    
    def test_execute_returns_dict(self):
        # Test with very minimal parameters
        result = self.attack.execute(attempts=1, delay=0.001)
        self.assertIsInstance(result, dict)
        self.assertIn('successful', result)
        self.assertIn('attempts', result)
        self.assertIn('elapsed', result)
    
    def test_log_file_creation(self):
        self.assertIsNotNone(self.attack.log_file)
        self.assertTrue("bruteforce.log" in self.attack.log_file)

class TestDDoS(unittest.TestCase):
    
    def setUp(self):
        self.attack = DDOSAttack("http://192.168.101.12:5001")
    
    def test_attack_initialization(self):
        self.assertEqual(self.attack.target_url, "http://192.168.101.12:5001")
        self.assertIsNotNone(self.attack.endpoints)
        self.assertIsInstance(self.attack.endpoints, list)
    
    def test_fake_ips_generation(self):
        self.attack.fake_ips = []
        self.attack.generate_fake_ips(10)
        self.assertEqual(len(self.attack.fake_ips), 10)
    
    def test_execute_returns_dict(self):
        result = self.attack.execute(requests=2, threads=1, delay=0.001)
        self.assertIsInstance(result, dict)
        self.assertIn('successful', result)
        self.assertIn('failed', result)
        self.assertIn('elapsed', result)

class TestRequestFlood(unittest.TestCase):
    
    def setUp(self):
        self.attack = RequestFlood("http://192.168.101.12:5001")
    
    def test_attack_initialization(self):
        self.assertEqual(self.attack.target_url, "http://192.168.101.12:5001")
        self.assertIsNotNone(self.attack.endpoints)
    
    def test_execute_returns_dict(self):
        result = self.attack.execute(requests=2)
        self.assertIsInstance(result, dict)
        self.assertIn('successful', result)
        self.assertIn('failed', result)
        self.assertIn('elapsed', result)

class TestScanner(unittest.TestCase):
    
    def setUp(self):
        self.attack = ScannerAttack("http://192.168.101.12:5001")
    
    def test_attack_initialization(self):
        self.assertEqual(self.attack.target_url, "http://192.168.101.12:5001")
        self.assertIsNotNone(self.attack.directories)
        self.assertIsInstance(self.attack.directories, list)
    
    def test_user_agents_rotation(self):
        self.assertIsNotNone(self.attack.user_agents)
        self.assertGreater(len(self.attack.user_agents), 0)
    
    def test_execute_returns_dict(self):
        result = self.attack.execute(max_paths=2, delay=0.001)
        self.assertIsInstance(result, dict)
        self.assertIn('total_scanned', result)
        self.assertIn('found', result)
        self.assertIn('elapsed', result)

if __name__ == '__main__':
    unittest.main()
