"""
PHASE 2 QUICK REFERENCE GUIDE
==============================

Fast reference for using Phase 2 modules
"""

# GEOIP ANALYZER
# ==============

from ipanalyzer.modules.geoip_analyzer import GeoIPAnalyzer

# Create instance
geoip = GeoIPAnalyzer()

# Single IP analysis
result = geoip.analyze("8.8.8.8")
print(f"{result['country']} - {result['city']} ({result['latitude']}, {result['longitude']})")

# Batch analysis
results = geoip.batch_analyze(["8.8.8.8", "1.1.1.1", "8.8.4.4"])

# Calculate distance between IPs
geo1 = geoip.analyze("8.8.8.8")
geo2 = geoip.analyze("1.1.1.1")
distance = geoip.calculate_distance(geo1, geo2)
print(f"Distance: {distance:.2f} km")

# Country distribution
dist = geoip.get_countries_distribution(["8.8.8.8", "1.1.1.1"])

# Get IPs in country
us_ips = geoip.find_ips_in_country("US")

# Cache stats
stats = geoip.get_cache_stats()


# BGP ANALYZER
# ============

from ipanalyzer.modules.bgp_analyzer import BGPAnalyzer

# Create instance
bgp = BGPAnalyzer()

# Analyze IP
result = bgp.analyze_ip("8.8.8.8")
print(f"AS{result['asn']} ({result['as_name']}) - Route: {result['route_prefix']}")

# Get AS info
as_info = bgp.get_as_info(15169)
print(f"AS 15169: {as_info['name']} ({as_info['country']})")

# Find route origin
origin = bgp.find_origin("8.8.8.0/24")

# Get AS path
path = bgp.trace_as_path("8.8.8.8")

# Get all prefixes for AS
prefixes = bgp.get_prefixes_for_asn(15169)

# Get all ASNs in database
asns = bgp.get_all_asns()

# Statistics
stats = bgp.get_statistics()


# DNS BULK PROCESSOR
# ==================

from ipanalyzer.modules.dns_bulk_processor import DNSBulkProcessor

# Create instance (8 threads, 5s timeout)
dns = DNSBulkProcessor(threads=8, timeout=5)

# Forward lookup (hostname to IPs)
results = dns.forward_lookup_batch(['google.com', 'example.com'])

# Reverse lookup (IP to hostname)
results = dns.reverse_lookup_batch(['8.8.8.8', '1.1.1.1'])

# Batch from file
results = dns.batch_from_file('ips.txt', reverse=True)

# Export results
csv = dns.export_results(results, format='csv')
json = dns.export_results(results, format='json')
text = dns.export_results(results, format='txt')

# Bulk lookup with auto-batching
results = dns.bulk_lookup(['host1.com', 'host2.com'], max_batch=100)

# Statistics
stats = dns.get_statistics()

# Clear cache
dns.clear_cache()


# THREAT INTELLIGENCE
# ===================

from ipanalyzer.modules.threat_intelligence import ThreatIntelligence

# Create instance
threat = ThreatIntelligence()

# Analyze threat level
result = threat.analyze_threat("8.8.8.8")
print(f"Threat Level: {result['threat_level']} (Score: {result['risk_score']}/100)")

# Check blacklist/whitelist
is_blacklisted = threat.is_blacklisted("192.0.2.1")
is_whitelisted = threat.is_whitelisted("8.8.8.8")

# Manage lists
threat.add_to_blacklist("192.0.2.1")
threat.add_to_whitelist("8.8.8.8")
threat.remove_from_blacklist("192.0.2.1")

# Get history
history = threat.get_threat_history("8.8.8.8", days=30)

# Compare multiple IPs
comparison = threat.compare_ips(["8.8.8.8", "1.1.1.1", "192.0.2.1"])

# Get high-risk IPs
high_risk = threat.get_high_risk_ips(["8.8.8.8", "1.1.1.1"], threshold=70)

# Export report
csv_report = threat.export_threat_report("8.8.8.8", format='csv')
text_report = threat.export_threat_report("8.8.8.8", format='text')

# Statistics
stats = threat.get_statistics()

# Clear old history
removed = threat.clear_history(days_old=90)


# COMBINED USAGE EXAMPLE
# ======================

# Complete IP analysis with all Phase 2 features
def analyze_ip_complete(ip):
    from ipanalyzer.modules.geoip_analyzer import GeoIPAnalyzer
    from ipanalyzer.modules.bgp_analyzer import BGPAnalyzer
    from ipanalyzer.modules.threat_intelligence import ThreatIntelligence
    
    geoip = GeoIPAnalyzer()
    bgp = BGPAnalyzer()
    threat = ThreatIntelligence()
    
    result = {
        'ip': ip,
        'geoip': geoip.analyze(ip),
        'bgp': bgp.analyze_ip(ip),
        'threat': threat.analyze_threat(ip)
    }
    
    return result

# Usage
analysis = analyze_ip_complete("8.8.8.8")
print(f"IP: {analysis['ip']}")
print(f"  Location: {analysis['geoip']['country']} - {analysis['geoip']['city']}")
print(f"  ASN: {analysis['bgp']['asn']} ({analysis['bgp']['as_name']})")
print(f"  Threat: {analysis['threat']['threat_level']} ({analysis['threat']['risk_score']}/100)")


# ERROR HANDLING EXAMPLES
# =======================

# Handle invalid IP
try:
    result = geoip.analyze("invalid.ip.address")
except Exception as e:
    print(f"Error: {e}")

# Handle DNS timeout
dns = DNSBulkProcessor(threads=4, timeout=2)
results = dns.forward_lookup_batch(['slow-domain.example.com'])
if results['slow-domain.example.com']['error']:
    print(f"DNS Error: {results['slow-domain.example.com']['error']}")

# Handle missing IP in database
result = bgp.analyze_ip("127.0.0.1")
if result['asn'] is None:
    print("IP not found in BGP database")


# EXPORT AND REPORTING
# ====================

# Generate comprehensive report
def generate_report(ip_list, output_file):
    geoip = GeoIPAnalyzer()
    bgp = BGPAnalyzer()
    threat = ThreatIntelligence()
    dns = DNSBulkProcessor()
    
    with open(output_file, 'w') as f:
        f.write("IP Analysis Report\n")
        f.write("=" * 50 + "\n\n")
        
        for ip in ip_list:
            geo = geoip.analyze(ip)
            bgp_info = bgp.analyze_ip(ip)
            threat_info = threat.analyze_threat(ip)
            
            f.write(f"IP: {ip}\n")
            f.write(f"  Location: {geo['country']} - {geo['city']}\n")
            f.write(f"  ASN: AS{bgp_info['asn']} ({bgp_info['as_name']})\n")
            f.write(f"  Threat: {threat_info['threat_level']} ({threat_info['risk_score']}/100)\n")
            f.write("\n")

# Usage
generate_report(["8.8.8.8", "1.1.1.1"], "report.txt")


# PERFORMANCE TIPS
# ================

# 1. Use batch operations when possible
#    Good:   geoip.batch_analyze(100_ips)
#    Bad:    for ip in 100_ips: geoip.analyze(ip)

# 2. Configure DNS threads for your needs
#    Fast:   DNSBulkProcessor(threads=16)
#    Slow:   DNSBulkProcessor(threads=1)

# 3. Use caching to avoid duplicate lookups
#    Cache automatically enabled in all modules
#    Clear when needed: geoip.clear_cache()

# 4. Handle errors gracefully
#    Always check result['error'] in DNS module
#    Check 'found' key in BGP module
#    Check 'threat_level' in threat module

# 5. Export results efficiently
#    Use CSV for large datasets
#    Use JSON for programmatic parsing
#    Use TXT for human-readable reports


# INTEGRATION TIPS
# ================

# 1. Use with IPUtils
from ipanalyzer.modules.ip_utils import IPValidator, IPConverter

if IPValidator.is_valid_ipv4("8.8.8.8"):
    geoip_result = geoip.analyze("8.8.8.8")

# 2. Use with Range Analyzer
from ipanalyzer.modules.ip_range_analyzer import IPRangeAnalyzer

analyzer = IPRangeAnalyzer()
ips = analyzer.get_usable_ips("8.8.8.0/24")
threat_results = threat.compare_ips(ips)

# 3. Generate HTML reports
from ipanalyzer.modules.report_generator import ReportGenerator

report_gen = ReportGenerator()
# Add Phase 2 data to reports
geoip_data = geoip.analyze("8.8.8.8")
# Integrate with report generation


# NOTES
# =====

# All Phase 2 modules use only Python stdlib - no external dependencies
# All modules support batch operations for performance
# All modules include caching for frequently accessed data
# All modules have comprehensive error handling
# All modules include statistics and monitoring capabilities
# All modules are thread-safe for multi-threaded applications
# All modules can be used independently or together
# All modules are fully documented with docstrings
# All modules have been tested and verified to work correctly

"""
For more information, see:
- PHASE2_IMPLEMENTATION_REPORT.md
- PHASE2_COMPLETION.txt
- test_phase2_modules.py
"""
