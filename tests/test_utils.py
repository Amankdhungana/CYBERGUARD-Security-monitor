import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ip_tracker import get_client_ip
from utils.logger import log_activity, log_security_event

class TestUtils(unittest.TestCase):
    """Test cases for utility functions - IP tracking and logging"""
    
    def test_get_client_ip(self):
        """Test getting client IP from request"""
        class MockRequest:
            def __init__(self):
                self.remote_addr = '192.168.1.100'
                self.headers = {}
        
        request = MockRequest()
        ip = get_client_ip(request)
        self.assertEqual(ip, '192.168.1.100')
    
    def test_get_client_ip_with_forwarded(self):
        """Test getting real IP when X-Forwarded-For header is present"""
        class MockRequest:
            def __init__(self):
                self.remote_addr = '192.168.1.100'
                self.headers = {
                    'X-Forwarded-For': '10.0.0.1, 192.168.1.100'
                }
        
        request = MockRequest()
        ip = get_client_ip(request)
        # Should get the first IP from X-Forwarded-For
        self.assertEqual(ip, '10.0.0.1')
    
    def test_log_activity(self):
        """Test that activity logging works"""
        # This is a smoke test - just check it doesn't crash
        result = log_activity(
            user='testuser',
            action='test_action',
            event_type='test',
            ip_address='192.168.1.100',
            endpoint='/test'
        )
        self.assertIsNone(result)
    
    def test_log_security_event(self):
        """Test that security event logging works"""
        result = log_security_event(
            event_type='test_event',
            source_ip='192.168.1.100',
            target_endpoint='/test',
            description='Test security event'
        )
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
    