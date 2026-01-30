"""
Test suite for IPAnalyzer
Author: MrAmirRezaie
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ipanalyzer.modules.ip_utils import (
    IPValidator, IPConverter, CIDRCalculator, IPClassifier
)
from ipanalyzer.modules.whois_analyzer import WHOISAnalyzer
from ipanalyzer.modules.ip_range_analyzer import IPRangeAnalyzer
from ipanalyzer.modules.network_scanner import NetworkScanner


class TestIPValidator(unittest.TestCase):
    """Test IP validation functions"""
    
    def test_valid_ipv4(self):
        """Test valid IPv4 addresses"""
        self.assertTrue(IPValidator.is_valid_ipv4("192.168.1.1"))
        self.assertTrue(IPValidator.is_valid_ipv4("8.8.8.8"))
        self.assertTrue(IPValidator.is_valid_ipv4("0.0.0.0"))
        self.assertTrue(IPValidator.is_valid_ipv4("255.255.255.255"))
    
    def test_invalid_ipv4(self):
        """Test invalid IPv4 addresses"""
        self.assertFalse(IPValidator.is_valid_ipv4("256.256.256.256"))
        self.assertFalse(IPValidator.is_valid_ipv4("192.168.1"))
        self.assertFalse(IPValidator.is_valid_ipv4("invalid"))
        self.assertFalse(IPValidator.is_valid_ipv4("192.168.1.1.1"))
    
    def test_valid_cidr(self):
        """Test valid CIDR notation"""
        self.assertTrue(IPValidator.is_valid_cidr("192.168.1.0/24"))
        self.assertTrue(IPValidator.is_valid_cidr("10.0.0.0/8"))
        self.assertTrue(IPValidator.is_valid_cidr("172.16.0.0/12"))
    
    def test_invalid_cidr(self):
        """Test invalid CIDR notation"""
        self.assertFalse(IPValidator.is_valid_cidr("192.168.1.0/33"))
        self.assertFalse(IPValidator.is_valid_cidr("192.168.1.0"))
        self.assertFalse(IPValidator.is_valid_cidr("invalid/24"))


class TestIPConverter(unittest.TestCase):
    """Test IP conversion functions"""
    
    def test_ip_to_int(self):
        """Test IP to integer conversion"""
        self.assertEqual(IPConverter.ip_to_int("0.0.0.0"), 0)
        self.assertEqual(IPConverter.ip_to_int("255.255.255.255"), 4294967295)
        self.assertEqual(IPConverter.ip_to_int("192.168.1.1"), 3232235777)
    
    def test_int_to_ip(self):
        """Test integer to IP conversion"""
        self.assertEqual(IPConverter.int_to_ip(0), "0.0.0.0")
        self.assertEqual(IPConverter.int_to_ip(4294967295), "255.255.255.255")
        self.assertEqual(IPConverter.int_to_ip(3232235777), "192.168.1.1")


class TestCIDRCalculator(unittest.TestCase):
    """Test CIDR calculation functions"""
    
    def test_parse_cidr(self):
        """Test CIDR parsing"""
        network, broadcast, mask, prefix = CIDRCalculator.parse_cidr("192.168.1.0/24")
        self.assertEqual(network, "192.168.1.0")
        self.assertEqual(broadcast, "192.168.1.255")
        self.assertEqual(mask, "255.255.255.0")
        self.assertEqual(prefix, 24)
    
    def test_get_usable_ips(self):
        """Test usable IP list generation"""
        ips = CIDRCalculator.get_usable_ips("192.168.1.0/24")
        self.assertEqual(len(ips), 254)
        self.assertEqual(ips[0], "192.168.1.1")
        self.assertEqual(ips[-1], "192.168.1.254")
    
    def test_subnets_from_cidr(self):
        """Test subnet division"""
        subnets = CIDRCalculator.subnets_from_cidr("192.168.1.0/24", 26)
        self.assertEqual(len(subnets), 4)
        self.assertIn("192.168.1.0/26", subnets)


class TestIPClassifier(unittest.TestCase):
    """Test IP classification functions"""
    
    def test_is_private(self):
        """Test private IP detection"""
        self.assertTrue(IPClassifier.is_private("192.168.1.1"))
        self.assertTrue(IPClassifier.is_private("10.0.0.1"))
        self.assertTrue(IPClassifier.is_private("172.16.0.1"))
        self.assertFalse(IPClassifier.is_private("8.8.8.8"))
    
    def test_is_loopback(self):
        """Test loopback IP detection"""
        self.assertTrue(IPClassifier.is_loopback("127.0.0.1"))
        self.assertTrue(IPClassifier.is_loopback("127.255.255.255"))
        self.assertFalse(IPClassifier.is_loopback("128.0.0.1"))
    
    def test_classify(self):
        """Test IP classification"""
        self.assertEqual(IPClassifier.classify("192.168.1.1"), "Private")
        self.assertEqual(IPClassifier.classify("8.8.8.8"), "Public")
        self.assertEqual(IPClassifier.classify("127.0.0.1"), "Loopback")


class TestWHOISAnalyzer(unittest.TestCase):
    """Test WHOIS analyzer functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = WHOISAnalyzer()
    
    def test_analyze_private_ip(self):
        """Test WHOIS analysis of private IP"""
        result = self.analyzer.analyze_ip("192.168.1.1")
        self.assertEqual(result['ip'], "192.168.1.1")
        self.assertTrue(result['is_private'])
        self.assertEqual(result['classification'], 'Private')
    
    def test_analyze_loopback_ip(self):
        """Test WHOIS analysis of loopback IP"""
        result = self.analyzer.analyze_ip("127.0.0.1")
        self.assertTrue(result['is_loopback'])


class TestIPRangeAnalyzer(unittest.TestCase):
    """Test IP range analyzer functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = IPRangeAnalyzer()
    
    def test_analyze_cidr(self):
        """Test CIDR analysis"""
        result = self.analyzer.analyze_cidr("192.168.1.0/24")
        self.assertEqual(result['cidr'], "192.168.1.0/24")
        self.assertEqual(result['network_ip'], "192.168.1.0")
        self.assertEqual(result['broadcast_ip'], "192.168.1.255")
        self.assertEqual(result['total_addresses'], 256)
        self.assertEqual(result['usable_hosts'], 254)
    
    def test_subnet_division(self):
        """Test subnet division"""
        subnets = self.analyzer.subnet_division("192.168.1.0/24", 26)
        self.assertEqual(len(subnets), 4)
    
    def test_ip_in_range(self):
        """Test IP range checking"""
        self.assertTrue(self.analyzer.ip_in_range("192.168.1.50", "192.168.1.0/24"))
        self.assertFalse(self.analyzer.ip_in_range("192.168.2.50", "192.168.1.0/24"))
    
    def test_find_overlaps(self):
        """Test overlap detection"""
        self.assertTrue(self.analyzer.find_overlaps("192.168.1.0/24", "192.168.1.0/25"))
        self.assertFalse(self.analyzer.find_overlaps("192.168.1.0/24", "192.168.2.0/24"))


class TestNetworkScanner(unittest.TestCase):
    """Test network scanner functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.scanner = NetworkScanner()
    
    def test_get_local_ip(self):
        """Test local IP detection"""
        local_ip = self.scanner.get_local_ip()
        self.assertIsNotNone(local_ip)
        self.assertTrue(IPValidator.is_valid_ipv4(local_ip))
    
    def test_get_network_info(self):
        """Test network info retrieval"""
        net_info = self.scanner.get_network_info()
        self.assertIn('local_ip', net_info)
        self.assertIn('gateway', net_info)
        self.assertIn('os', net_info)
    
    def test_ping_host(self):
        """Test ping functionality"""
        # Ping localhost - should always work
        result = self.scanner.ping_host("127.0.0.1")
        self.assertTrue(result)
    
    def test_get_service_name(self):
        """Test service name lookup"""
        self.assertEqual(NetworkScanner.get_service_name(22), "SSH")
        self.assertEqual(NetworkScanner.get_service_name(80), "HTTP")
        self.assertEqual(NetworkScanner.get_service_name(443), "HTTPS")
        self.assertEqual(NetworkScanner.get_service_name(65535), "Unknown")


def run_tests():
    """Run all tests"""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_tests()
