import unittest
import sys
import os
import tkinter as tk
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestUI(unittest.TestCase):
    """Test cases for UI components - verify they can be created"""
    
    def setUp(self):
        """Create a real tkinter root for UI tests"""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window
    
    def tearDown(self):
        """Clean up tkinter root"""
        self.root.destroy()
    
    @patch('ui.dashboard.get_attack_statistics')
    @patch('ui.dashboard.get_security_events')
    @patch('ui.dashboard.get_activity_logs')
    def test_dashboard_page_creation(self, mock_logs, mock_events, mock_stats):
        """Test that DashboardPage can be instantiated"""
        # Mock the data
        mock_stats.return_value = {
            'total_attacks': 0,
            'high_severity': 0,
            'unresolved': 0,
            'attack_types': [],
            'top_ips': []
        }
        mock_events.return_value = []
        mock_logs.return_value = []
        
        from monitoring_system.ui.dashboard import DashboardPage
        dashboard = DashboardPage(self.root)
        self.assertIsNotNone(dashboard)
        self.assertIsNotNone(dashboard.get_frame())
    
    @patch('ui.attacks.get_security_events')
    def test_attacks_page_creation(self, mock_events):
        """Test that AttacksPage can be instantiated"""
        mock_events.return_value = []
        
        from monitoring_system.ui.attacks import AttacksPage
        attacks = AttacksPage(self.root)
        self.assertIsNotNone(attacks)
        self.assertIsNotNone(attacks.get_frame())
    
    @patch('ui.logs.get_activity_logs')
    def test_logs_page_creation(self, mock_logs):
        """Test that LogsPage can be instantiated"""
        mock_logs.return_value = []
        
        from monitoring_system.ui.logs import LogsPage
        logs = LogsPage(self.root)
        self.assertIsNotNone(logs)
        self.assertIsNotNone(logs.get_frame())
    
    @patch('ui.alerts.get_security_events')
    def test_alerts_page_creation(self, mock_events):
        """Test that AlertsPage can be instantiated"""
        mock_events.return_value = []
        
        from monitoring_system.ui.alerts import AlertsPage
        alerts = AlertsPage(self.root)
        self.assertIsNotNone(alerts)
        self.assertIsNotNone(alerts.get_frame())
    
    def test_imports(self):
        """Test that all UI modules can be imported"""
        try:
            from monitoring_system.ui.dashboard import DashboardPage
            from monitoring_system.ui.attacks import AttacksPage
            from monitoring_system.ui.logs import LogsPage
            from monitoring_system.ui.alerts import AlertsPage
            from monitoring_system.ui.incident import IncidentPage
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"UI import failed: {e}")

if __name__ == '__main__':
    unittest.main()
