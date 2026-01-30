#!/usr/bin/env python3
"""
Example Usage of IPAnalyzer
Author: MrAmirRezaie
"""

from ipanalyzer import WHOISAnalyzer, NetworkScanner, IPRangeAnalyzer, ReportGenerator
import json


def example_whois_analysis():
    """Example: WHOIS Analysis"""
    print("\n" + "="*60)
    print("Example 1: WHOIS Analysis")
    print("="*60 + "\n")
    
    analyzer = WHOISAnalyzer()
    
    # Analyze different IPs
    ips = ["8.8.8.8", "1.1.1.1", "192.168.1.1"]
    
    for ip in ips:
        result = analyzer.analyze_ip(ip)
        print(f"IP: {ip}")
        print(f"Classification: {result['classification']}")
        print(f"Private: {result['is_private']}")
        if result['whois']:
            print(f"Organization: {result['whois'].get('organization', 'N/A')}")
        print()


def example_ip_range_analysis():
    """Example: IP Range Analysis"""
    print("\n" + "="*60)
    print("Example 2: IP Range Analysis")
    print("="*60 + "\n")
    
    analyzer = IPRangeAnalyzer()
    
    # Analyze CIDR block
    cidr = "192.168.1.0/24"
    analysis = analyzer.analyze_cidr(cidr)
    
    print(f"CIDR: {analysis['cidr']}")
    print(f"Network: {analysis['network_ip']}")
    print(f"Broadcast: {analysis['broadcast_ip']}")
    print(f"Netmask: {analysis['netmask']}")
    print(f"Total Addresses: {analysis['total_addresses']}")
    print(f"Usable Hosts: {analysis['usable_hosts']}")
    print()
    
    # Divide into subnets
    print("Dividing into /26 subnets:")
    subnets = analyzer.subnet_division(cidr, 26)
    for subnet in subnets:
        sub_analysis = analyzer.analyze_cidr(subnet)
        print(f"  {subnet} - {sub_analysis['usable_hosts']} usable hosts")


def example_network_scanning():
    """Example: Network Scanning"""
    print("\n" + "="*60)
    print("Example 3: Network Scanning")
    print("="*60 + "\n")
    
    scanner = NetworkScanner()
    
    # Get network info
    net_info = scanner.get_network_info()
    print(f"Local IP: {net_info['local_ip']}")
    print(f"Gateway: {net_info['gateway']}")
    print(f"Estimated Range: {net_info['estimated_range']}\n")
    
    # Scan network
    print("Scanning network for devices...")
    devices = scanner.scan_network()
    
    print(f"Found {len(devices)} device(s):\n")
    for device in devices:
        print(f"  IP: {device.get('ip')}")
        print(f"  MAC: {device.get('mac')}")
        print(f"  Hostname: {device.get('hostname', 'N/A')}")
        print(f"  Vendor: {device.get('vendor', 'N/A')}")
        print()


def example_port_scanning():
    """Example: Port Scanning"""
    print("\n" + "="*60)
    print("Example 4: Port Scanning")
    print("="*60 + "\n")
    
    scanner = NetworkScanner()
    
    # Scan local host
    ip = "127.0.0.1"
    print(f"Scanning ports on {ip}...")
    
    ports = scanner.scan_ports(ip)
    print(f"Found {len(ports)} open port(s):\n")
    
    for port_info in ports:
        print(f"  Port: {port_info['port']} ({port_info['service']})")
        print(f"  Status: {port_info['status']}")


def example_html_report():
    """Example: Generate HTML Report"""
    print("\n" + "="*60)
    print("Example 5: Generate HTML Report")
    print("="*60 + "\n")
    
    whois = WHOISAnalyzer()
    analyzer = IPRangeAnalyzer()
    generator = ReportGenerator()
    
    # Gather data
    ip_analysis = whois.analyze_ip("8.8.8.8")
    range_analysis = analyzer.analyze_cidr("8.8.8.0/24")
    
    # Prepare report data
    report_data = {
        'ip': ip_analysis['ip'],
        'classification': ip_analysis['classification'],
        'is_private': ip_analysis['is_private'],
        'whois': ip_analysis['whois'],
        'ranges': [range_analysis]
    }
    
    # Generate HTML
    output_file = "examples/example_report.html"
    html = generator.generate_html_report(report_data, output_file)
    print(f"✅ Report generated: {output_file}\n")


def example_batch_analysis():
    """Example: Batch Analysis"""
    print("\n" + "="*60)
    print("Example 6: Batch Analysis")
    print("="*60 + "\n")
    
    whois = WHOISAnalyzer()
    analyzer = IPRangeAnalyzer()
    
    # List of IPs and ranges
    entries = [
        "8.8.8.8",
        "1.1.1.1",
        "192.168.0.0/16",
        "10.0.0.0/8",
    ]
    
    results = []
    for entry in entries:
        print(f"Analyzing: {entry}")
        if '/' in entry:
            result = analyzer.analyze_cidr(entry)
        else:
            result = whois.analyze_ip(entry)
        results.append(result)
    
    print(f"\n✅ Analyzed {len(results)} entries\n")
    
    # Save as JSON
    with open("examples/batch_analysis.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Saved to: examples/batch_analysis.json")


def example_utility_functions():
    """Example: Utility Functions"""
    print("\n" + "="*60)
    print("Example 7: Utility Functions")
    print("="*60 + "\n")
    
    from ipanalyzer.modules.ip_utils import (
        IPValidator, IPConverter, CIDRCalculator, IPClassifier
    )
    
    # Validation
    print("IP Validation:")
    print(f"  192.168.1.1 is valid: {IPValidator.is_valid_ipv4('192.168.1.1')}")
    print(f"  999.999.999.999 is valid: {IPValidator.is_valid_ipv4('999.999.999.999')}")
    print(f"  192.168.1.0/24 is valid CIDR: {IPValidator.is_valid_cidr('192.168.1.0/24')}\n")
    
    # Conversion
    print("IP Conversion:")
    ip = "192.168.1.1"
    ip_int = IPConverter.ip_to_int(ip)
    print(f"  {ip} = {ip_int}")
    print(f"  {ip_int} = {IPConverter.int_to_ip(ip_int)}\n")
    
    # CIDR Parsing
    print("CIDR Parsing:")
    network, broadcast, mask, prefix = CIDRCalculator.parse_cidr("192.168.1.0/24")
    print(f"  Network: {network}")
    print(f"  Broadcast: {broadcast}")
    print(f"  Netmask: {mask}")
    print(f"  Prefix: {prefix}\n")
    
    # Classification
    print("IP Classification:")
    test_ips = ["192.168.1.1", "8.8.8.8", "127.0.0.1", "169.254.1.1"]
    for ip in test_ips:
        classification = IPClassifier.classify(ip)
        print(f"  {ip}: {classification}")


def main():
    """Run all examples"""
    print("\n")
    print("█" * 60)
    print("█" + " " * 58 + "█")
    print("█  " + "IPAnalyzer - Usage Examples".center(54) + "  █")
    print("█  " + "Created by MrAmirRezaie".center(54) + "  █")
    print("█" + " " * 58 + "█")
    print("█" * 60)
    
    try:
        example_whois_analysis()
        example_ip_range_analysis()
        example_utility_functions()
        example_html_report()
        example_batch_analysis()
        
        print("\n" + "="*60)
        print("✅ All examples completed successfully!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
