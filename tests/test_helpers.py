import unittest
import sys
import os
import sqlite3
import tempfile

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import (
    format_timestamp,
    get_severity_color,
    get_attack_statistics,
    get_security_events,
    get_activity_logs
)

class TestHelpers(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary test database
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()
        
        # Create test tables
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create security_events table
        cursor.execute('''
            CREATE TABLE security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                severity TEXT DEFAULT 'low',
                source_ip TEXT NOT NULL,
                target_endpoint TEXT,
                description TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                resolved BOOLEAN DEFAULT 0
            )
        ''')
        
        # Insert test data
        cursor.execute('''
            INSERT INTO security_events (event_type, severity, source_ip, target_endpoint, description)
            VALUES ('test_attack', 'high', '192.168.1.100', '/test', 'Test attack')
        ''')
        cursor.execute('''
            INSERT INTO security_events (event_type, severity, source_ip, target_endpoint, description)
            VALUES ('another_attack', 'low', '10.0.0.1', '/another', 'Another test')
        ''')
        cursor.execute('''
            INSERT INTO security_events (event_type, severity, source_ip, target_endpoint, description)
            VALUES ('bruteforce', 'medium', '192.168.1.200', '/login', 'Brute force attempt')
        ''')
        
        conn.commit()
        conn.close()
        
        # Monkey patch get_company_connection to use test DB
        import utils.helpers
        def mock_connection():
            return sqlite3.connect(self.db_path)
        utils.helpers.get_company_connection = mock_connection
    
    def tearDown(self):
        os.unlink(self.db_path)
    
    def test_format_timestamp(self):
        self.assertEqual(format_timestamp("2026-07-04 14:30:25.123456"), "2026-07-04 14:30")
        self.assertEqual(format_timestamp(""), "N/A")
        self.assertEqual(format_timestamp(None), "N/A")
    
    def test_get_severity_color(self):
        self.assertEqual(get_severity_color("high"), "#ff4757")
        self.assertEqual(get_severity_color("medium"), "#ffd93d")
        self.assertEqual(get_severity_color("low"), "#00d4aa")
        self.assertEqual(get_severity_color("unknown"), "#8892b0")
    
    def test_get_attack_statistics_returns_dict(self):
        stats = get_attack_statistics()
        self.assertIsInstance(stats, dict)
        self.assertIn('total_attacks', stats)
        self.assertIn('high_severity', stats)
        self.assertIn('unresolved', stats)
    
    def test_get_security_events_returns_list(self):
        events = get_security_events(5)
        self.assertIsInstance(events, list)
        self.assertGreaterEqual(len(events), 1)
    
    def test_get_security_events_with_severity_filter(self):
        events = get_security_events(5, "high")
        self.assertIsInstance(events, list)
        for event in events:
            self.assertEqual(event['severity'], 'high')

if __name__ == '__main__':
    unittest.main()
