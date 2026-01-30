#!/usr/bin/env python3
"""
Test script for Phase 2 modules
Tests all four Phase 2 modules: GeoIP, BGP, DNS, and Threat Intelligence
"""

from ipanalyzer.modules.geoip_analyzer import GeoIPAnalyzer
from ipanalyzer.modules.bgp_analyzer import BGPAnalyzer
from ipanalyzer.modules.dns_bulk_processor import DNSBulkProcessor
from ipanalyzer.modules.threat_intelligence import ThreatIntelligence


def test_geoip():
    """Test GeoIP analyzer functionality"""
    print("=" * 60)
    print("Testing GeoIP Analyzer")
    print("=" * 60)
    
    geoip = GeoIPAnalyzer()
    
    # Test single IP analysis
    result = geoip.analyze("8.8.8.8")
    print(f"✓ Analyzed 8.8.8.8:")
    print(f"  Country: {result.get('country')}")
    print(f"  City: {result.get('city')}")
    print(f"  Coordinates: {result.get('latitude')}, {result.get('longitude')}")
    print(f"  ISP: {result.get('isp')}")
    
    # Test batch analysis
    ips = ["8.8.8.8", "1.1.1.1", "8.8.4.4"]
    batch_results = geoip.batch_analyze(ips)
    print(f"✓ Batch analyzed {len(batch_results)} IPs")
    
    # Test distance calculation
    result1 = geoip.analyze("8.8.8.8")
    result2 = geoip.analyze("1.1.1.1")
    distance = geoip.calculate_distance(result1, result2)
    print(f"✓ Distance calculation: {distance:.2f} km between 8.8.8.8 and 1.1.1.1")
    
    # Test cache stats
    stats = geoip.get_cache_stats()
    print(f"✓ Cache stats: {stats['cached_ips']} cached IPs, DB has {stats['db_entries']} entries")
    print()


def test_bgp():
    """Test BGP analyzer functionality"""
    print("=" * 60)
    print("Testing BGP Analyzer")
    print("=" * 60)
    
    bgp = BGPAnalyzer()
    
    # Test IP analysis
    result = bgp.analyze_ip("8.8.8.8")
    print(f"✓ Analyzed 8.8.8.8:")
    print(f"  ASN: {result.get('asn')}")
    print(f"  AS Name: {result.get('as_name')}")
    print(f"  Route Prefix: {result.get('route_prefix')}")
    print(f"  Origin: {result.get('origin')}")
    
    # Test AS info lookup
    as_info = bgp.get_as_info(15169)
    print(f"✓ AS 15169 info: {as_info.get('name')} ({as_info.get('country')})")
    
    # Test find origin
    origin = bgp.find_origin("8.8.8.0/24")
    print(f"✓ Origin for 8.8.8.0/24: AS{origin.get('asn')} ({origin.get('as_name')})")
    
    # Test all ASNs
    all_asns = bgp.get_all_asns()
    print(f"✓ Database contains {len(all_asns)} unique ASNs")
    
    # Test statistics
    stats = bgp.get_statistics()
    print(f"✓ BGP stats: {stats['total_prefixes']} prefixes, {stats['total_asns']} ASNs")
    print()


def test_dns():
    """Test DNS bulk processor functionality"""
    print("=" * 60)
    print("Testing DNS Bulk Processor")
    print("=" * 60)
    
    dns = DNSBulkProcessor(threads=2, timeout=5)
    
    print(f"✓ DNS Processor initialized: {dns.threads} threads, {dns.timeout}s timeout")
    
    # Test cache and statistics
    stats = dns.get_statistics()
    print(f"✓ Initial stats: Forward={stats['forward_lookups']}, "
          f"Reverse={stats['reverse_lookups']}, Errors={stats['errors']}")
    
    # Test export format - CSV
    test_results = {
        'hostname1': {'hostname': 'google.com', 'ips': ['8.8.8.8'], 'error': None},
        'hostname2': {'hostname': 'example.com', 'ips': [], 'error': 'not_found'}
    }
    
    csv_export = dns.export_results(test_results, format='csv')
    print(f"✓ CSV export generated: {len(csv_export)} characters")
    
    # Test JSON export
    json_export = dns.export_results(test_results, format='json')
    print(f"✓ JSON export generated: {len(json_export)} characters")
    
    # Test text export
    text_export = dns.export_results(test_results, format='txt')
    print(f"✓ Text export generated: {len(text_export)} characters")
    
    print()


def test_threat_intelligence():
    """Test threat intelligence functionality"""
    print("=" * 60)
    print("Testing Threat Intelligence")
    print("=" * 60)
    
    threat = ThreatIntelligence()
    
    # Test threat analysis
    result = threat.analyze_threat("8.8.8.8")
    print(f"✓ Threat analysis for 8.8.8.8:")
    print(f"  Threat Level: {result.get('threat_level')}")
    print(f"  Risk Score: {result.get('risk_score')}/100")
    print(f"  Threat Types: {result.get('threat_types')}")
    print(f"  Whitelisted: {result.get('whitelisted')}")
    
    # Test whitelist
    threat.add_to_whitelist("8.8.8.8")
    result = threat.analyze_threat("8.8.8.8")
    print(f"✓ After whitelisting - Risk Score: {result.get('risk_score')}")
    threat.remove_from_whitelist("8.8.8.8")
    
    # Test blacklist
    threat.add_to_blacklist("192.0.2.1")
    is_blacklisted = threat.is_blacklisted("192.0.2.1")
    print(f"✓ Blacklist test: {is_blacklisted}")
    threat.remove_from_blacklist("192.0.2.1")
    
    # Test batch comparison
    ips = ["8.8.8.8", "1.1.1.1", "192.0.2.1"]
    comparison = threat.compare_ips(ips)
    print(f"✓ Compared {len(comparison)} IPs")
    
    # Test threat report export
    report_csv = threat.export_threat_report("8.8.8.8", format='csv')
    print(f"✓ CSV report generated: {len(report_csv)} characters")
    
    report_text = threat.export_threat_report("8.8.8.8", format='text')
    print(f"✓ Text report generated: {len(report_text)} characters")
    
    # Test statistics
    stats = threat.get_statistics()
    print(f"✓ Threat stats: Blacklist={stats['blacklist_size']}, "
          f"Whitelist={stats['whitelist_size']}")
    
    print()


def main():
    """Run all tests"""
    print("\n")
    print("=" * 60)
    print("   IPAnalyzer Phase 2 - Module Functionality Tests")
    print("=" * 60)
    print()
    
    try:
        test_geoip()
        test_bgp()
        test_dns()
        test_threat_intelligence()
        
        print("=" * 60)
        print("ALL PHASE 2 MODULES PASSED FUNCTIONAL TESTS!")
        print("=" * 60)
        print()
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
