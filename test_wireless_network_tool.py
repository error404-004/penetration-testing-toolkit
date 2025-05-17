
import unittest
from unittest.mock import patch, MagicMock
from wireless_network_tool import WirelessNetworkTool

class TestWirelessNetworkTool(unittest.TestCase):

    def setUp(self):
        self.tool = WirelessNetworkTool(interfaces=['test0'])

    @patch('wireless_network_tool.subprocess.check_output')
    def test_get_wireless_interfaces(self, mock_check_output):
        mock_check_output.return_value = "Interface test0\nInterface test1"
        interfaces = self.tool.get_wireless_interfaces()
        self.assertIn("test0", interfaces)
        self.assertIn("test1", interfaces)

    @patch('wireless_network_tool.subprocess.check_output')
    def test_scan_networks(self, mock_output):
        mock_output.return_value = """
            Cell 01 - Address: 00:11:22:33:44:55
                      ESSID:"TestNet"
                      Frequency:2.437 GHz
                      Channel:6
                      Quality=70/70  Signal level=-40 dBm
                      Encryption key:on
                      WPA2
        """
        results = self.tool.scan_networks("test0")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["ssid"], "TestNet")
        self.assertEqual(results[0]["bssid"], "00:11:22:33:44:55")
        self.assertEqual(results[0]["encryption"], "WPA2")

    @patch('wireless_network_tool.requests.get')
    def test_geolocate_network(self, mock_requests):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "result": [{"trilat": 12.34, "trilong": 56.78, "city": "TestCity"}]
        }
        mock_requests.return_value = mock_response
        self.tool.wigle_user = "user"
        self.tool.wigle_pass = "pass"
        result = self.tool.geolocate_network("00:11:22:33:44:55")
        self.assertEqual(result.get("latitude"), 12.34)

    def test_enrich_with_geolocation_empty(self):
        result = self.tool.enrich_with_geolocation({"test0": [{"bssid": "00:00:00:00:00:00"}]})
        self.assertIn("geolocation", result["test0"][0])

if __name__ == "__main__":
    unittest.main()