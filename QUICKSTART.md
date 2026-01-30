"""
IPAnalyzer - Quick Start Guide
Author: MrAmirRezaie
"""

# ==============================================================================
# QUICK START - IPAnalyzer
# ==============================================================================

"""
IPAnalyzer is an advanced IP analysis tool that provides:
- WHOIS lookup for IP addresses
- Network device discovery
- IP range and CIDR analysis
- Port scanning
- Professional HTML reports

All functionality works OFFLINE with NO external dependencies!
"""

# ─────────────────────────────────────────────────────────────────────────────
# 1. INSTALLATION
# ─────────────────────────────────────────────────────────────────────────────

"""
Python 3.8+ required

Option A: Development Install
    pip install -e .

Option B: Run directly
    python ipanalyzer_cli.py --help
"""

# ─────────────────────────────────────────────────────────────────────────────
# 2. COMMAND LINE USAGE
# ─────────────────────────────────────────────────────────────────────────────

"""
WHOIS LOOKUP
────────────────────────────────────────────────────────────────────────────────
Get information about an IP address:

    python ipanalyzer_cli.py whois 8.8.8.8

Generate HTML report:

    python ipanalyzer_cli.py whois 8.8.8.8 -o reports/whois.html

JSON output:

    python ipanalyzer_cli.py whois 8.8.8.8 --json


NETWORK SCANNING
────────────────────────────────────────────────────────────────────────────────
Discover devices on your network:

    python ipanalyzer_cli.py scan

Scan specific network:

    python ipanalyzer_cli.py scan --range 192.168.1.0/24

Generate report:

    python ipanalyzer_cli.py scan -o reports/network.html


IP RANGE ANALYSIS
────────────────────────────────────────────────────────────────────────────────
Analyze CIDR blocks:

    python ipanalyzer_cli.py range 192.168.1.0/24

Divide into subnets:

    python ipanalyzer_cli.py range 192.168.1.0/24 --subnet 26

List all IPs:

    python ipanalyzer_cli.py range 192.168.1.0/24 --list-ips

Generate report:

    python ipanalyzer_cli.py range 192.168.1.0/24 -o reports/range.html


PORT SCANNING
────────────────────────────────────────────────────────────────────────────────
Scan ports on a host:

    python ipanalyzer_cli.py ports 192.168.1.100

Scan specific ports:

    python ipanalyzer_cli.py ports 192.168.1.100 --ports 22,80,443

Generate report:

    python ipanalyzer_cli.py ports 192.168.1.100 -o reports/ports.html


BATCH ANALYSIS
────────────────────────────────────────────────────────────────────────────────
Create a file with IPs/ranges (one per line):

    ips.txt:
    ────────────────────────────────────────────────────────────────────────────
    8.8.8.8
    1.1.1.1
    192.168.0.0/16
    # Comments supported
    10.0.0.0/8

Batch process:

    python ipanalyzer_cli.py batch ips.txt -o reports/batch.html

JSON output:

    python ipanalyzer_cli.py batch ips.txt --json > results.json
"""

# ─────────────────────────────────────────────────────────────────────────────
# 3. PYTHON API USAGE
# ─────────────────────────────────────────────────────────────────────────────

"""
Import modules:

    from ipanalyzer import (
        WHOISAnalyzer,
        NetworkScanner,
        IPRangeAnalyzer,
        ReportGenerator
    )


WHOIS ANALYSIS
────────────────────────────────────────────────────────────────────────────────

    analyzer = WHOISAnalyzer()
    result = analyzer.analyze_ip("8.8.8.8")
    
    print(result['classification'])      # 'Public'
    print(result['whois']['organization'])  # Organization name
    print(result['whois']['country'])    # Country code


NETWORK SCANNING
────────────────────────────────────────────────────────────────────────────────

    scanner = NetworkScanner()
    
    # Get network info
    net_info = scanner.get_network_info()
    # {'local_ip': '192.168.1.x', 'gateway': '192.168.1.1', ...}
    
    # Scan network
    devices = scanner.scan_network()
    # [{'ip': '192.168.1.x', 'mac': '...', 'hostname': '...', ...}, ...]
    
    # Scan ports
    ports = scanner.scan_ports("192.168.1.100")
    # [{'port': 22, 'service': 'SSH', 'status': 'open'}, ...]


IP RANGE ANALYSIS
────────────────────────────────────────────────────────────────────────────────

    analyzer = IPRangeAnalyzer()
    
    # Analyze CIDR
    analysis = analyzer.analyze_cidr("192.168.1.0/24")
    # {'cidr': '...', 'network_ip': '...', 'broadcast_ip': '...', ...}
    
    # Divide into subnets
    subnets = analyzer.subnet_division("192.168.1.0/24", 26)
    # ['192.168.1.0/26', '192.168.1.64/26', ...]
    
    # Check if IP in range
    in_range = analyzer.ip_in_range("192.168.1.50", "192.168.1.0/24")
    # True
    
    # Get usable IPs
    ips = analyzer.generate_ip_list("192.168.1.0/24")


REPORT GENERATION
────────────────────────────────────────────────────────────────────────────────

    generator = ReportGenerator()
    
    # Generate HTML report
    html = generator.generate_html_report(
        data={
            'ip': '8.8.8.8',
            'classification': 'Public',
            'whois': {...},
            'ranges': [{...}],
            'devices': [{...}]
        },
        output_file='report.html'
    )
"""

# ─────────────────────────────────────────────────────────────────────────────
# 4. UTILITY FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

"""
IP Utils module provides low-level utilities:

    from ipanalyzer.modules.ip_utils import (
        IPValidator,
        IPConverter,
        CIDRCalculator,
        IPClassifier
    )

IP VALIDATION
────────────────────────────────────────────────────────────────────────────────

    IPValidator.is_valid_ipv4("192.168.1.1")     # True
    IPValidator.is_valid_cidr("192.168.1.0/24")  # True


IP CONVERSION
────────────────────────────────────────────────────────────────────────────────

    ip_int = IPConverter.ip_to_int("192.168.1.1")      # 3232235777
    ip_str = IPConverter.int_to_ip(3232235777)        # "192.168.1.1"


CIDR CALCULATION
────────────────────────────────────────────────────────────────────────────────

    network, broadcast, mask, prefix = CIDRCalculator.parse_cidr("192.168.1.0/24")
    # ('192.168.1.0', '192.168.1.255', '255.255.255.0', 24)
    
    ips = CIDRCalculator.get_usable_ips("192.168.1.0/24")
    # ['192.168.1.1', '192.168.1.2', ..., '192.168.1.254']
    
    subnets = CIDRCalculator.subnets_from_cidr("192.168.1.0/24", 26)
    # ['192.168.1.0/26', '192.168.1.64/26', ...]


IP CLASSIFICATION
────────────────────────────────────────────────────────────────────────────────

    IPClassifier.classify("192.168.1.1")    # "Private"
    IPClassifier.classify("8.8.8.8")        # "Public"
    IPClassifier.classify("127.0.0.1")      # "Loopback"
    IPClassifier.is_private("192.168.1.1")  # True
    IPClassifier.is_loopback("127.0.0.1")   # True
"""

# ─────────────────────────────────────────────────────────────────────────────
# 5. REAL-WORLD EXAMPLES
# ─────────────────────────────────────────────────────────────────────────────

"""
EXAMPLE 1: Network Audit
────────────────────────────────────────────────────────────────────────────────

    from ipanalyzer import NetworkScanner, ReportGenerator
    
    scanner = NetworkScanner()
    generator = ReportGenerator()
    
    # Scan network
    devices = scanner.scan_network("192.168.1.0/24")
    
    # Get detailed info for each device
    for device in devices:
        ports = scanner.scan_ports(device['ip'])
        device['open_ports'] = ports
    
    # Generate report
    generator.generate_html_report(
        {'devices': devices},
        'network_audit.html'
    )


EXAMPLE 2: IP Research
────────────────────────────────────────────────────────────────────────────────

    from ipanalyzer import WHOISAnalyzer, IPRangeAnalyzer, ReportGenerator
    
    whois = WHOISAnalyzer()
    range_analyzer = IPRangeAnalyzer()
    generator = ReportGenerator()
    
    ip = "8.8.8.8"
    
    # Get IP info
    ip_data = whois.analyze_ip(ip)
    
    # Analyze entire network range
    cidr = f"{ip}/24"  # Simplified, should extract actual range
    range_data = range_analyzer.analyze_cidr(cidr)
    
    # Generate report
    generator.generate_html_report({
        'ip': ip_data,
        'ranges': [range_data]
    }, 'ip_research.html')


EXAMPLE 3: Subnet Planning
────────────────────────────────────────────────────────────────────────────────

    from ipanalyzer import IPRangeAnalyzer
    
    analyzer = IPRangeAnalyzer()
    
    # Plan subnets for large network
    org_network = "10.0.0.0/8"
    
    # Divide into /16 subnets
    subnets = analyzer.subnet_division(org_network, 16)
    
    # Analyze each
    for subnet in subnets:
        analysis = analyzer.analyze_cidr(subnet)
        print(f"{subnet}: {analysis['usable_hosts']} hosts")


EXAMPLE 4: Bulk IP Analysis
────────────────────────────────────────────────────────────────────────────────

    from ipanalyzer import WHOISAnalyzer
    
    analyzer = WHOISAnalyzer()
    
    ips = ['8.8.8.8', '1.1.1.1', '208.67.222.222']
    
    results = []
    for ip in ips:
        data = analyzer.analyze_ip(ip)
        results.append({
            'ip': ip,
            'organization': data['whois'].get('organization'),
            'country': data['whois'].get('country'),
            'is_private': data['is_private']
        })
    
    # Export as JSON
    import json
    with open('ips.json', 'w') as f:
        json.dump(results, f, indent=2)
"""

# ─────────────────────────────────────────────────────────────────────────────
# 6. COMMON TASKS
# ─────────────────────────────────────────────────────────────────────────────

"""
Find my network range:
    python ipanalyzer_cli.py scan  # Shows estimated range

Check if IP is private:
    python ipanalyzer_cli.py whois <IP>  # Look at 'Classification' field

Count usable IPs in subnet:
    python ipanalyzer_cli.py range <CIDR>  # Shows 'Usable Hosts'

Create smaller subnets:
    python ipanalyzer_cli.py range <CIDR> --subnet <PREFIX>

List all IPs in range:
    python ipanalyzer_cli.py range <CIDR> --list-ips

Find open ports on device:
    python ipanalyzer_cli.py ports <IP>

Analyze multiple IPs:
    python ipanalyzer_cli.py batch ips.txt

Get detailed report:
    python ipanalyzer_cli.py whois <IP> -o report.html
"""

# ─────────────────────────────────────────────────────────────────────────────
# 7. TROUBLESHOOTING
# ─────────────────────────────────────────────────────────────────────────────

"""
"No devices found" in network scan:
    - Specify network range: --range 192.168.1.0/24
    - Check firewall settings
    - Ensure you're on correct network

"WHOIS information unavailable":
    - IP may be private/new
    - Try with internet connection for public IPs

"Permission denied" on port scan:
    - May need admin/sudo privileges
    - Try specific ports: --ports 80,443

"Hostname resolution failed":
    - DNS may not be configured
    - IP may not have reverse DNS entry
"""

# ─────────────────────────────────────────────────────────────────────────────
# 8. HELP
# ─────────────────────────────────────────────────────────────────────────────

"""
Get help:
    python ipanalyzer_cli.py --help
    python ipanalyzer_cli.py whois --help
    python ipanalyzer_cli.py scan --help
    python ipanalyzer_cli.py range --help
    python ipanalyzer_cli.py ports --help
    python ipanalyzer_cli.py batch --help

View examples:
    python examples.py

Read documentation:
    See README.md
"""

# ─────────────────────────────────────────────────────────────────────────────
# 9. TIPS & TRICKS
# ─────────────────────────────────────────────────────────────────────────────

"""
Save all reports in one folder:
    python ipanalyzer_cli.py whois 8.8.8.8 -o reports/whois_8888.html

Batch process many IPs:
    Create ips.txt with one IP per line
    python ipanalyzer_cli.py batch ips.txt -o reports/all.html

Automate with cron/task scheduler:
    Add command to cron or Windows task scheduler

Use in scripts:
    #!/bin/bash
    for ip in 192.168.1.{1..255}; do
        python ipanalyzer_cli.py whois $ip --json >> results.json
    done

Parse JSON output:
    python ipanalyzer_cli.py whois 8.8.8.8 --json | python -m json.tool
"""

# ═══════════════════════════════════════════════════════════════════════════════
print("""

╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    IPAnalyzer - QUICK START GUIDE                           ║
║                                                                              ║
║  An advanced IP analysis tool with WHOIS lookup, network scanning,          ║
║  IP range analysis, and professional HTML reporting.                       ║
║                                                                              ║
║  Created by: MrAmirRezaie                                                   ║
║  Version: 1.0.0                                                             ║
║  License: MIT                                                               ║
║                                                                              ║
║  🔗 Start: python ipanalyzer_cli.py --help                                  ║
║  📚 Examples: python examples.py                                            ║
║  📖 Docs: README.md                                                         ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

Quick Commands:
  • Analyze IP:      python ipanalyzer_cli.py whois 8.8.8.8
  • Scan network:    python ipanalyzer_cli.py scan
  • Analyze range:   python ipanalyzer_cli.py range 192.168.1.0/24
  • Scan ports:      python ipanalyzer_cli.py ports 192.168.1.100
  • Batch process:   python ipanalyzer_cli.py batch ips.txt
  • Generate report: python ipanalyzer_cli.py whois 8.8.8.8 -o report.html

""")
