import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestUI(unittest.TestCase):
    """Test cases for UI components - verify they can be created"""
    
    def test_imports(self):
        """Test that all UI modules can be imported"""
        try:
            from ui.dashboard import DashboardPage
            from ui.attacks import AttacksPage
            from ui.logs import LogsPage
            from ui.alerts import AlertsPage
            from ui.incident import IncidentPage
            self.assertTrue(True)
        except ImportError:
            self.fail("UI import failed")
    
    def test_dashboard_page_creation(self):
        """Test that DashboardPage can be instantiated"""
        class MockParent:
            pass
        
        parent = MockParent()
        from ui.dashboard import DashboardPage
        dashboard = DashboardPage(parent)
        self.assertIsNotNone(dashboard)
        self.assertIsNotNone(dashboard.get_frame())
    
    def test_attacks_page_creation(self):
        """Test that AttacksPage can be instantiated"""
        class MockParent:
            pass
        
        parent = MockParent()
        from ui.attacks import AttacksPage
        attacks = AttacksPage(parent)
        self.assertIsNotNone(attacks)
        self.assertIsNotNone(attacks.get_frame())
    
    def test_logs_page_creation(self):
        """Test that LogsPage can be instantiated"""
        class MockParent:
            pass
        
        parent = MockParent()
        from ui.logs import LogsPage
        logs = LogsPage(parent)
        self.assertIsNotNone(logs)
        self.assertIsNotNone(logs.get_frame())
    
    def test_alerts_page_creation(self):
        """Test that AlertsPage can be instantiated"""
        class MockParent:
            pass
        
        parent = MockParent()
        from ui.alerts import AlertsPage
        alerts = AlertsPage(parent)
        self.assertIsNotNone(alerts)
        self.assertIsNotNone(alerts.get_frame())

if __name__ == '__main__':
    unittest.main()
    