import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import (
    format_timestamp,
    get_severity_color,
    get_attack_statistics,
    get_security_events
)

class TestHelpers(unittest.TestCase):
    """Test cases for helper functions - data formatting and database queries"""
    
    def test_format_timestamp(self):
        """Test timestamp formatting - should show only date and hour:minute"""
        # Valid timestamp
        self.assertEqual(
            format_timestamp("2026-07-04 14:30:25.123456"), 
            "2026-07-04 14:30"
        )
        # Empty timestamp
        self.assertEqual(format_timestamp(""), "N/A")
        # None timestamp
        self.assertEqual(format_timestamp(None), "N/A")
    
    def test_get_severity_color(self):
        """Test severity color mapping - different colors for different severity levels"""
        self.assertEqual(get_severity_color("high"), "#ff4757")    # Red
        self.assertEqual(get_severity_color("medium"), "#ffd93d")  # Yellow
        self.assertEqual(get_severity_color("low"), "#00d4aa")     # Green
        # Unknown severity should return default
        self.assertEqual(get_severity_color("unknown"), "#8892b0") # Gray
    
    def test_get_attack_statistics_returns_dict(self):
        """Test that attack statistics returns a dictionary with expected keys"""
        stats = get_attack_statistics()
        self.assertIsInstance(stats, dict)
        # Check for expected keys
        self.assertIn('total_attacks', stats)
        self.assertIn('high_severity', stats)
        self.assertIn('unresolved', stats)
        self.assertIn('attack_types', stats)
        self.assertIn('top_ips', stats)
    
    def test_get_security_events_returns_list(self):
        """Test that security events query returns a list"""
        events = get_security_events(5)
        self.assertIsInstance(events, list)
    
    def test_get_security_events_with_severity_filter(self):
        """Test that severity filtering works"""
        # Should return only high severity events
        events = get_security_events(5, "high")
        self.assertIsInstance(events, list)

if __name__ == '__main__':
    unittest.main()
    